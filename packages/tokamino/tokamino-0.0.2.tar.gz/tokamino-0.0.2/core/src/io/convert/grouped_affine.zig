//! Grouped-affine Model Conversion (MLX-compatible export)
//!
//! Converts transformer models to grouped-affine quantization and exports
//! them in MLX-compatible SafeTensors layout.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const dtype_mod = @import("../../dtype.zig");
const safetensors = @import("../safetensors/root.zig");
const storage = @import("../storage/root.zig");
const mlx_paths = @import("mlx_paths.zig");
const config_loader = @import("../config/root.zig");
const parallel = @import("../../compute/parallel.zig");
const convert = @import("root.zig");
const mapping = convert.mapping;

const Tensor = tensor.Tensor;
const DType = dtype_mod.DType;

/// Quantization configuration
pub const QuantConfig = struct {
    bits: u8,
    group_size: u32,
};

/// Conversion options
pub const ConvertOptions = struct {
    quant: ?QuantConfig = null, // If null, preserve source precision
    output_dir: []const u8 = "models",
    force: bool = false,
    progress: convert.ProgressContext = .{},
};

/// Convert a transformer model to grouped-affine weights in MLX format (optionally quantized).
/// Returns the output path (caller owns the memory).
pub fn convertToGroupedAffine(
    allocator: std.mem.Allocator,
    input_path: []const u8,
    options: ConvertOptions,
) ![]const u8 {
    // 1. Resolve input model files
    var bundle = try storage.resolve(allocator, input_path);
    defer bundle.deinit();

    // 2. Load source model config
    const model_config = try config_loader.loadConfig(allocator, bundle.config_path());

    // 3. Generate output directory name
    const bits_for_name: u8 = if (options.quant) |q| q.bits else 16;
    const output_path = try mlx_paths.generateOutputName(
        allocator,
        input_path,
        bits_for_name,
        options.output_dir,
    );
    errdefer allocator.free(output_path);

    // 4. Check if output exists
    if (options.force) {
        std.fs.cwd().deleteTree(output_path) catch {};
    } else {
        std.fs.cwd().access(output_path, .{}) catch |err| switch (err) {
            error.FileNotFound => {},
            else => return err,
        };
        if (std.fs.cwd().openDir(output_path, .{})) |_| {
            return error.OutputExists;
        } else |_| {}
    }

    // 5. Load source weights and validate
    var src_st = try safetensors.SafeTensors.load(allocator, bundle.weights_path());
    defer src_st.deinit();

    // 6. Check if model is already quantized
    if (options.quant != null and convert.isAlreadyQuantized(&src_st)) {
        return error.AlreadyQuantized;
    }

    // 7. Validate quantization config
    if (options.quant) |q| {
        if (q.bits != 4 and q.bits != 8) {
            return error.UnsupportedBits;
        }
    }

    // 8. Create output directory structure
    var output_dir = try mlx_paths.MLXModelDir.init(allocator, output_path);
    defer output_dir.deinit();

    // 9. Process and write weights
    const weights_path = try output_dir.weightsPath();
    defer allocator.free(weights_path);

    if (options.quant) |quant_config| {
        try quantizeAndWrite(allocator, &src_st, weights_path, quant_config, model_config.tie_word_embeddings, options.progress);
    } else {
        try copyWeightsAsIs(allocator, &src_st, weights_path, model_config.tie_word_embeddings, options.progress);
    }

    // 10. Write MLX config
    const mlx_quant_config: ?mlx_paths.MLXConfig.QuantizationConfig = if (options.quant) |q| .{
        .group_size = @intCast(q.group_size),
        .bits = @intCast(q.bits),
    } else null;
    const mlx_config = mlx_paths.MLXConfig.fromModelConfig(model_config, mlx_quant_config);
    const config_path = try output_dir.configPath();
    defer allocator.free(config_path);
    try mlx_config.writeToFile(allocator, config_path);

    // 11. Copy tokenizer files
    const tok_path = bundle.tokenizer_path();
    const source_dir = if (tok_path.len > 0) std.fs.path.dirname(tok_path) orelse "." else bundle.dir;
    try output_dir.copyTokenizerFiles(source_dir);

    return output_path;
}

/// Quantize all tensors and write to SafeTensors file.
fn quantizeAndWrite(
    allocator: std.mem.Allocator,
    src: *safetensors.SafeTensors,
    output_path: []const u8,
    quant: QuantConfig,
    tie_word_embeddings: bool,
    progress: convert.ProgressContext,
) !void {
    var builder = safetensors.Builder.init(allocator);
    defer builder.deinit();

    const names = try src.tensorNames(allocator);
    defer allocator.free(names);

    for (names, 0..) |name, idx| {
        progress.report(idx, names.len, name);

        // Use shared mapping to check role
        const info = mapping.parseHfName(name);

        // Skip lm_head when embeddings are tied
        if (convert.shouldSkipForTiedEmbeddings(info, tie_word_embeddings)) {
            continue;
        }

        const t = try src.getTensor(name, null);

        // Use shared logic to determine if tensor should be quantized
        if (convert.shouldQuantizeTensor(info, t)) {
            try quantizeTensor(allocator, &builder, name, t, quant);
        } else {
            try copyTensor(allocator, &builder, name, t);
        }
    }

    try builder.save(output_path);
}

/// Copy all tensors without quantization (preserve original format).
fn copyWeightsAsIs(
    allocator: std.mem.Allocator,
    src: *safetensors.SafeTensors,
    output_path: []const u8,
    tie_word_embeddings: bool,
    progress: convert.ProgressContext,
) !void {
    var builder = safetensors.Builder.init(allocator);
    defer builder.deinit();

    const names = try src.tensorNames(allocator);
    defer allocator.free(names);

    for (names, 0..) |name, idx| {
        progress.report(idx, names.len, name);

        const info = mapping.parseHfName(name);

        // Skip lm_head when embeddings are tied
        if (convert.shouldSkipForTiedEmbeddings(info, tie_word_embeddings)) {
            continue;
        }

        const t = try src.getTensor(name, null);
        try copyTensor(allocator, &builder, name, t);
    }

    try builder.save(output_path);
}

/// Context for parallel quantization.
const QuantizeRowsCtx = struct {
    src_data: []align(1) const f32,
    packed_data: []u32,
    scales: []u16,
    biases: []u16,
    cols: usize,
    packed_cols: usize,
    num_groups: usize,
    group_size: usize,
    bits: u8,
};

/// Quantize a range of rows (called by each thread).
fn quantizeRows(start: usize, end: usize, ctx: *QuantizeRowsCtx) void {
    const cols = ctx.cols;
    const packed_cols = ctx.packed_cols;
    const num_groups = ctx.num_groups;
    const group_size = ctx.group_size;
    const bits = ctx.bits;

    const values_per_word: usize = if (bits == 4) 8 else 4;
    const max_quant: f32 = if (bits == 4) 15.0 else 255.0;

    for (start..end) |row| {
        const row_data = ctx.src_data[row * cols .. (row + 1) * cols];
        const row_packed = ctx.packed_data[row * packed_cols .. (row + 1) * packed_cols];
        const row_scales = ctx.scales[row * num_groups .. (row + 1) * num_groups];
        const row_biases = ctx.biases[row * num_groups .. (row + 1) * num_groups];

        for (0..num_groups) |g| {
            const group_start = g * group_size;
            const group_data = row_data[group_start .. group_start + group_size];

            var min_val: f32 = group_data[0];
            var max_val: f32 = group_data[0];
            for (group_data) |v| {
                if (v < min_val) min_val = v;
                if (v > max_val) max_val = v;
            }

            const range = max_val - min_val;
            const scale: f32 = if (range > 0) range / max_quant else 0;
            const bias: f32 = min_val;

            row_scales[g] = convert.f32ToBf16(scale);
            row_biases[g] = convert.f32ToBf16(bias);

            const words_per_group = group_size / values_per_word;
            for (0..words_per_group) |pack_idx| {
                const base = group_start + pack_idx * values_per_word;
                var packed_word: u32 = 0;

                for (0..values_per_word) |val_idx| {
                    const val = row_data[base + val_idx];
                    var quantized: u32 = 0;
                    if (scale > 0) {
                        const normalized = (val - bias) / scale;
                        quantized = @intFromFloat(@max(0, @min(max_quant, @round(normalized))));
                    }
                    packed_word |= quantized << @intCast(val_idx * bits);
                }

                row_packed[(group_start / values_per_word) + pack_idx] = packed_word;
            }
        }
    }
}

/// Quantize a tensor to grouped-affine weights (4-bit or 8-bit).
fn quantizeTensor(
    allocator: std.mem.Allocator,
    builder: *safetensors.Builder,
    name: []const u8,
    t: Tensor,
    quant: QuantConfig,
) !void {
    const bits = quant.bits;
    if (bits != 4 and bits != 8) return error.UnsupportedBits;

    const rows: usize = @intCast(t.shape[0]);
    const cols: usize = @intCast(t.shape[1]);
    const group_size = quant.group_size;

    const values_per_word: usize = if (bits == 4) 8 else 4;

    // Ensure cols is divisible by group_size and values_per_word
    if (cols % group_size != 0 or cols % values_per_word != 0) {
        return copyTensor(allocator, builder, name, t);
    }

    // Convert source to F32
    const f32_result = try convert.tensorToF32(allocator, t);
    defer f32_result.deinit(allocator);

    const src_data = f32_result.asF32Slice();

    // Calculate output sizes
    const packed_cols = cols / values_per_word;
    const num_groups = cols / group_size;

    // Allocate output buffers
    const packed_data = try allocator.alloc(u32, rows * packed_cols);
    defer allocator.free(packed_data);

    const scales = try allocator.alloc(u16, rows * num_groups);
    defer allocator.free(scales);

    const biases = try allocator.alloc(u16, rows * num_groups);
    defer allocator.free(biases);

    // Quantize rows in parallel
    var ctx = QuantizeRowsCtx{
        .src_data = src_data,
        .packed_data = packed_data,
        .scales = scales,
        .biases = biases,
        .cols = cols,
        .packed_cols = packed_cols,
        .num_groups = num_groups,
        .group_size = group_size,
        .bits = bits,
    };

    const pool = parallel.global();
    pool.parallelFor(rows, quantizeRows, &ctx);

    // Add tensors to builder
    const weight_dtype: DType = if (bits == 4) .grouped_affine_u4 else .grouped_affine_u8;
    try builder.addTensor(
        name,
        weight_dtype,
        &[_]usize{ rows, packed_cols },
        std.mem.sliceAsBytes(packed_data),
    );

    // Scales and biases names
    var scales_name_buf: [256]u8 = undefined;
    const base_name = if (std.mem.endsWith(u8, name, ".weight"))
        name[0 .. name.len - ".weight".len]
    else
        name;
    const scales_name = try std.fmt.bufPrint(&scales_name_buf, "{s}.scales", .{base_name});
    try builder.addTensor(
        scales_name,
        .bf16,
        &[_]usize{ rows, num_groups },
        std.mem.sliceAsBytes(scales),
    );

    var biases_name_buf: [256]u8 = undefined;
    const biases_name = try std.fmt.bufPrint(&biases_name_buf, "{s}.biases", .{base_name});
    try builder.addTensor(
        biases_name,
        .bf16,
        &[_]usize{ rows, num_groups },
        std.mem.sliceAsBytes(biases),
    );
}

/// Copy a tensor without quantization - preserves original dtype.
fn copyTensor(
    allocator: std.mem.Allocator,
    builder: *safetensors.Builder,
    name: []const u8,
    t: Tensor,
) !void {
    _ = allocator;
    const shape_arr = t.shapeAsUsize();
    const shape = shape_arr[0..@intCast(t.n_dims)];
    try builder.addTensor(name, t.dtype, shape, t.data()[0..t.data_size]);
}

// =============================================================================
// Tests
// =============================================================================

test "QuantConfig defaults" {
    const config = QuantConfig{ .bits = 4, .group_size = 64 };
    try std.testing.expectEqual(@as(u8, 4), config.bits);
    try std.testing.expectEqual(@as(u32, 64), config.group_size);
}
