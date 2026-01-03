//! Native Format Conversion (K-quants in SafeTensors)
//!
//! Converts HuggingFace models to tokamino's native quantized format.
//! Stores K-quant quantized weights in SafeTensors with metadata.
//!
//! This provides better quality than MLX grouped-affine quantization
//! while maintaining the simplicity of SafeTensors format.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const dtype_mod = @import("../../dtype.zig");
const safetensors = @import("../safetensors/root.zig");
const storage = @import("../storage/root.zig");
const config_loader = @import("../config/root.zig");
const convert = @import("root.zig");
const mapping = convert.mapping;

const Tensor = tensor.Tensor;
const DType = dtype_mod.DType;

/// Native quantization types (K-quants).
pub const NativeQuantType = enum {
    q4_0, // Basic 4-bit symmetric
    q4_k_m, // 4-bit K-quant with mixed precision (best 4-bit quality)
    q5_k, // 5-bit K-quant
    q6_k, // 6-bit K-quant (near 8-bit quality)
    q8_0, // 8-bit symmetric
    f16, // No quantization, keep as F16

    pub fn toString(self: NativeQuantType) []const u8 {
        return switch (self) {
            .q4_0 => "Q4_0",
            .q4_k_m => "Q4_K_M",
            .q5_k => "Q5_K",
            .q6_k => "Q6_K",
            .q8_0 => "Q8_0",
            .f16 => "F16",
        };
    }

    pub fn fromString(s: []const u8) ?NativeQuantType {
        if (std.ascii.eqlIgnoreCase(s, "q4_0")) return .q4_0;
        if (std.ascii.eqlIgnoreCase(s, "q4_k_m") or std.ascii.eqlIgnoreCase(s, "q4km")) return .q4_k_m;
        if (std.ascii.eqlIgnoreCase(s, "q5_k") or std.ascii.eqlIgnoreCase(s, "q5k")) return .q5_k;
        if (std.ascii.eqlIgnoreCase(s, "q6_k") or std.ascii.eqlIgnoreCase(s, "q6k")) return .q6_k;
        if (std.ascii.eqlIgnoreCase(s, "q8_0") or std.ascii.eqlIgnoreCase(s, "q8")) return .q8_0;
        if (std.ascii.eqlIgnoreCase(s, "f16") or std.ascii.eqlIgnoreCase(s, "16")) return .f16;
        return null;
    }

    /// Get the DType for this quantization type.
    pub fn toDType(self: NativeQuantType) DType {
        return switch (self) {
            .q4_0 => .q4_0,
            .q4_k_m => .q4_k,
            .q5_k => .q5_k,
            .q6_k => .q6_k,
            .q8_0 => .q8_0,
            .f16 => .f16,
        };
    }
};

/// Native format conversion options.
pub const ConvertNativeOptions = struct {
    quant: NativeQuantType = .q4_k_m,
    output_dir: []const u8 = "models",
    force: bool = false,
    progress: convert.ProgressContext = .{},
};

/// Convert a HuggingFace model to native quantized format.
/// Returns the output path (caller owns the memory).
pub fn convertToNative(
    allocator: std.mem.Allocator,
    input_path: []const u8,
    options: ConvertNativeOptions,
) ![]const u8 {
    // 1. Resolve input model files
    var bundle = try storage.resolve(allocator, input_path);
    defer bundle.deinit();

    // 2. Load model config
    const model_config = try config_loader.loadConfig(allocator, bundle.config_path());

    // 3. Load source weights
    var src_st = try safetensors.SafeTensors.load(allocator, bundle.weights_path());
    defer src_st.deinit();

    // 4. Check if model is already quantized
    if (convert.isAlreadyQuantized(&src_st)) {
        return error.AlreadyQuantized;
    }

    // 5. Generate output path
    const output_path = try generateNativeOutputPath(allocator, input_path, options.quant, options.output_dir);
    errdefer allocator.free(output_path);

    // 6. Check if output exists
    if (!options.force) {
        std.fs.cwd().access(output_path, .{}) catch |err| switch (err) {
            error.FileNotFound => {},
            else => return err,
        };
        if (std.fs.cwd().openDir(output_path, .{})) |_| {
            return error.OutputExists;
        } else |_| {}
    } else {
        std.fs.cwd().deleteTree(output_path) catch {};
    }

    // 7. Create output directory
    try std.fs.cwd().makePath(output_path);

    // 8. Build and write weights
    var builder = safetensors.Builder.init(allocator);
    defer builder.deinit();

    // Get and sort tensor names
    const names = try src_st.tensorNames(allocator);
    defer allocator.free(names);
    convert.sortTensorNames(names);

    // Convert tensors
    for (names, 0..) |name, idx| {
        options.progress.report(idx, names.len, name);

        const t = try src_st.getTensor(name, null);
        try convertTensor(allocator, &builder, name, t, options.quant, model_config.tie_word_embeddings, @intCast(model_config.n_layers));
    }

    // Write model.safetensors
    const weights_path = try std.fs.path.join(allocator, &.{ output_path, "model.safetensors" });
    defer allocator.free(weights_path);
    try builder.save(weights_path);

    // 9. Copy config.json from source (preserves architecture name)
    try convert.copyConfigFile(allocator, bundle.config_path(), output_path);

    // 10. Copy tokenizer files
    // Fall back to bundle.dir if tokenizer_path is empty (some models don't have tokenizer.json)
    const tok_path = bundle.tokenizer_path();
    const source_dir = if (tok_path.len > 0) std.fs.path.dirname(tok_path) orelse bundle.dir else bundle.dir;
    try convert.copyTokenizerFiles(allocator, source_dir, output_path);

    return output_path;
}

/// Convert and add a tensor to the builder.
fn convertTensor(
    allocator: std.mem.Allocator,
    builder: *safetensors.Builder,
    name: []const u8,
    t: Tensor,
    quant: NativeQuantType,
    tie_word_embeddings: bool,
    _: usize, // n_layers - unused since Q4_K kernel not yet implemented
) !void {
    const info = mapping.parseHfName(name);

    // Skip lm_head when embeddings are tied
    if (convert.shouldSkipForTiedEmbeddings(info, tie_word_embeddings)) {
        return;
    }

    // F16 mode - never quantize
    if (quant == .f16) {
        const data = try convertToF16(allocator, t);
        defer allocator.free(data);
        const shape = t.shapeAsUsize();
        try builder.addTensor(name, .f16, shape[0..@intCast(t.n_dims)], data);
        return;
    }

    // Determine if this tensor should be quantized
    const do_quantize = convert.shouldQuantizeTensor(info, t);

    if (do_quantize) {
        const row_size: usize = @intCast(t.shape[@as(usize, @intCast(t.n_dims - 1))]);
        const shape = t.shapeAsUsize();
        const dims = shape[0..@intCast(t.n_dims)];

        // Block sizes for K-quant types
        const q6k_block_size: usize = 256;
        const q8_block_size: usize = 32;
        const q4_block_size: usize = 32;

        switch (quant) {
            .q4_0 => {
                const data = try quantizeQ4_0(allocator, t);
                defer allocator.free(data);
                // Q4_0 uses packed shape: [rows, cols/block_size]
                var packed_dims: [2]usize = .{ dims[0], dims[1] / q4_block_size };
                try builder.addTensor(name, .q4_0, &packed_dims, data);
            },
            .q4_k_m => {
                // Q4_K_M uses mixed precision based on layer position
                // Use Q6_K for all tensors since Q4_K matmul kernel is not yet implemented
                const q6k_compatible = (row_size % 256 == 0);

                if (q6k_compatible) {
                    const data = try quantizeQ6K(allocator, t);
                    defer allocator.free(data);
                    // Q6_K uses packed shape: [rows, cols/256]
                    var packed_dims: [2]usize = .{ dims[0], dims[1] / q6k_block_size };
                    try builder.addTensor(name, .q6_k, &packed_dims, data);
                } else {
                    const data = try quantizeQ8_0(allocator, t);
                    defer allocator.free(data);
                    var packed_dims: [2]usize = .{ dims[0], dims[1] / q8_block_size };
                    try builder.addTensor(name, .q8_0, &packed_dims, data);
                }
            },
            .q5_k => {
                // Use Q6_K since Q5_K matmul kernel is not yet implemented
                if (row_size % 256 == 0) {
                    const data = try quantizeQ6K(allocator, t);
                    defer allocator.free(data);
                    var packed_dims: [2]usize = .{ dims[0], dims[1] / q6k_block_size };
                    try builder.addTensor(name, .q6_k, &packed_dims, data);
                } else {
                    const data = try quantizeQ8_0(allocator, t);
                    defer allocator.free(data);
                    var packed_dims: [2]usize = .{ dims[0], dims[1] / q8_block_size };
                    try builder.addTensor(name, .q8_0, &packed_dims, data);
                }
            },
            .q6_k => {
                if (row_size % 256 == 0) {
                    const data = try quantizeQ6K(allocator, t);
                    defer allocator.free(data);
                    var packed_dims: [2]usize = .{ dims[0], dims[1] / q6k_block_size };
                    try builder.addTensor(name, .q6_k, &packed_dims, data);
                } else {
                    const data = try quantizeQ8_0(allocator, t);
                    defer allocator.free(data);
                    var packed_dims: [2]usize = .{ dims[0], dims[1] / q8_block_size };
                    try builder.addTensor(name, .q8_0, &packed_dims, data);
                }
            },
            .q8_0 => {
                const data = try quantizeQ8_0(allocator, t);
                defer allocator.free(data);
                var packed_dims: [2]usize = .{ dims[0], dims[1] / q8_block_size };
                try builder.addTensor(name, .q8_0, &packed_dims, data);
            },
            .f16 => unreachable, // Handled above
        }
    } else {
        // Don't quantize - keep as F16 for small tensors, F32 for 1D
        if (t.n_dims == 1) {
            const data = try convertToF32(allocator, t);
            defer allocator.free(data);
            const shape = t.shapeAsUsize();
            try builder.addTensor(name, .f32, shape[0..@intCast(t.n_dims)], data);
        } else {
            const data = try convertToF16(allocator, t);
            defer allocator.free(data);
            const shape = t.shapeAsUsize();
            try builder.addTensor(name, .f16, shape[0..@intCast(t.n_dims)], data);
        }
    }
}

// =============================================================================
// Quantization Functions
// =============================================================================

/// Quantize to Q8_0 format (32 elements per block, 8-bit symmetric)
fn quantizeQ8_0(allocator: std.mem.Allocator, t: Tensor) ![]u8 {
    const BlockQ8_0 = dtype_mod.BlockQ8_0;
    const block_size = BlockQ8_0.block_size; // 32

    // Get F32 data
    const f32_result = try convert.tensorToF32(allocator, t);
    defer f32_result.deinit(allocator);
    const src = f32_result.asF32Slice();

    // Calculate number of blocks
    const n_blocks = (src.len + block_size - 1) / block_size;
    const result = try allocator.alloc(BlockQ8_0, n_blocks);
    errdefer allocator.free(result);

    for (0..n_blocks) |i| {
        const start = i * block_size;
        const end = @min(start + block_size, src.len);
        const block_data = src[start..end];

        // Find max absolute value
        var amax: f32 = 0.0;
        for (block_data) |v| {
            const abs_v = @abs(v);
            if (abs_v > amax) amax = abs_v;
        }

        // Compute scale
        const d: f32 = if (amax > 0) amax / 127.0 else 1.0;
        const id: f32 = if (d > 0) 1.0 / d else 0.0;

        result[i].d = dtype_mod.f32ToFp16(d);

        // Quantize values
        for (0..block_size) |j| {
            const v = if (start + j < end) block_data[j] else 0.0;
            const scaled = v * id;
            const rounded = @round(scaled);
            const clamped = @max(-128.0, @min(127.0, rounded));
            result[i].qs[j] = @intFromFloat(clamped);
        }
    }

    return std.mem.sliceAsBytes(result);
}

/// Quantize to Q6_K format (256 elements per block, 6-bit with scales)
fn quantizeQ6K(allocator: std.mem.Allocator, t: Tensor) ![]u8 {
    const BlockQ6_K = dtype_mod.BlockQ6_K;
    const block_size = BlockQ6_K.block_size; // 256
    const sub_block_size: usize = 16;

    // Get F32 data
    const f32_result = try convert.tensorToF32(allocator, t);
    defer f32_result.deinit(allocator);
    const src = f32_result.asF32Slice();

    // Calculate number of blocks
    const n_blocks = (src.len + block_size - 1) / block_size;
    const result = try allocator.alloc(BlockQ6_K, n_blocks);
    errdefer allocator.free(result);

    for (0..n_blocks) |blk_idx| {
        const blk_start = blk_idx * block_size;
        const blk_end = @min(blk_start + block_size, src.len);
        const block_data = src[blk_start..blk_end];

        // Find global max for this block
        var amax: f32 = 0.0;
        for (block_data) |v| {
            const abs_v = @abs(v);
            if (abs_v > amax) amax = abs_v;
        }

        const d: f32 = if (amax > 0) amax / 31.0 else 1.0; // 6-bit range: -32 to 31
        result[blk_idx].d = dtype_mod.f32ToFp16(d);

        // Process 16 sub-blocks of 16 values each
        for (0..16) |sb| {
            const sb_start = sb * sub_block_size;
            const sb_end = @min(sb_start + sub_block_size, block_data.len);

            // Find sub-block max for scale
            var sb_max: f32 = 0.0;
            for (sb_start..sb_end) |i| {
                const abs_v = @abs(block_data[i]);
                if (abs_v > sb_max) sb_max = abs_v;
            }

            // Scale relative to global d
            const scale: i8 = if (d > 0 and sb_max > 0)
                @intFromFloat(@round(@min(127.0, @max(-128.0, sb_max / d * 4.0))))
            else
                0;
            result[blk_idx].scales[sb] = scale;
        }

        // Quantize values into ql (low 4 bits) and qh (high 2 bits)
        for (0..128) |i| {
            const idx0 = i;
            const idx1 = i + 128;

            const v0: f32 = if (idx0 < block_data.len) block_data[idx0] else 0.0;
            const v1: f32 = if (idx1 < block_data.len) block_data[idx1] else 0.0;

            const sb0 = idx0 / sub_block_size;
            const sb1 = idx1 / sub_block_size;

            const scale0: f32 = @floatFromInt(result[blk_idx].scales[sb0]);
            const scale1: f32 = @floatFromInt(result[blk_idx].scales[sb1]);

            const id0: f32 = if (scale0 != 0 and d > 0) 4.0 / (scale0 * d) else 0.0;
            const id1: f32 = if (scale1 != 0 and d > 0) 4.0 / (scale1 * d) else 0.0;

            const q0: i8 = @intFromFloat(@round(@max(-32.0, @min(31.0, v0 * id0))));
            const q1: i8 = @intFromFloat(@round(@max(-32.0, @min(31.0, v1 * id1))));

            // Store low 4 bits in ql, high 2 bits in qh
            const ql_val = (@as(u8, @bitCast(@as(i8, @truncate(q0 & 0xF)))) & 0xF) |
                ((@as(u8, @bitCast(@as(i8, @truncate(q1 & 0xF)))) & 0xF) << 4);
            result[blk_idx].ql[i] = ql_val;

            // Pack high bits (2 values per byte in qh)
            if (i % 2 == 0) {
                const qh_idx = i / 2;
                const h0: u8 = @as(u8, @bitCast(@as(i8, @truncate((q0 >> 4) & 0x3)))) & 0x3;
                const h1: u8 = @as(u8, @bitCast(@as(i8, @truncate((q1 >> 4) & 0x3)))) & 0x3;
                if (i + 1 < 128) {
                    const v0_next: f32 = if (idx0 + 1 < block_data.len) block_data[idx0 + 1] else 0.0;
                    const v1_next: f32 = if (idx1 + 1 < block_data.len) block_data[idx1 + 1] else 0.0;
                    const q0_next: i8 = @intFromFloat(@round(@max(-32.0, @min(31.0, v0_next * id0))));
                    const q1_next: i8 = @intFromFloat(@round(@max(-32.0, @min(31.0, v1_next * id1))));
                    const h0_next: u8 = @as(u8, @bitCast(@as(i8, @truncate((q0_next >> 4) & 0x3)))) & 0x3;
                    const h1_next: u8 = @as(u8, @bitCast(@as(i8, @truncate((q1_next >> 4) & 0x3)))) & 0x3;
                    result[blk_idx].qh[qh_idx] = h0 | (h0_next << 2) | (h1 << 4) | (h1_next << 6);
                } else {
                    result[blk_idx].qh[qh_idx] = h0 | (h1 << 4);
                }
            }
        }
    }

    return std.mem.sliceAsBytes(result);
}

/// Quantize to Q4_0 format (32 elements per block, 4-bit symmetric)
fn quantizeQ4_0(allocator: std.mem.Allocator, t: Tensor) ![]u8 {
    const BlockQ4_0 = dtype_mod.BlockQ4_0;
    const block_size = BlockQ4_0.block_size; // 32

    // Get F32 data
    const f32_result = try convert.tensorToF32(allocator, t);
    defer f32_result.deinit(allocator);
    const src = f32_result.asF32Slice();

    // Calculate number of blocks
    const n_blocks = (src.len + block_size - 1) / block_size;
    const result = try allocator.alloc(BlockQ4_0, n_blocks);
    errdefer allocator.free(result);

    for (0..n_blocks) |i| {
        const start = i * block_size;
        const end = @min(start + block_size, src.len);
        const block_data = src[start..end];

        // Find max absolute value
        var amax: f32 = 0.0;
        for (block_data) |v| {
            const abs_v = @abs(v);
            if (abs_v > amax) amax = abs_v;
        }

        // Compute scale (4-bit range: -8 to 7)
        const d: f32 = if (amax > 0) amax / 7.0 else 1.0;
        const id: f32 = if (d > 0) 1.0 / d else 0.0;

        result[i].d = dtype_mod.f32ToFp16(d);

        // Quantize values (pack 2 values per byte)
        for (0..16) |j| {
            const v0 = if (start + j < end) block_data[j] else 0.0;
            const v1 = if (start + j + 16 < end) block_data[j + 16] else 0.0;

            const q0: u8 = @intFromFloat(@max(0.0, @min(15.0, @round(v0 * id) + 8.0)));
            const q1: u8 = @intFromFloat(@max(0.0, @min(15.0, @round(v1 * id) + 8.0)));

            result[i].qs[j] = (q0 & 0xF) | ((q1 & 0xF) << 4);
        }
    }

    return std.mem.sliceAsBytes(result);
}

// =============================================================================
// Data Conversion
// =============================================================================

fn convertToF32(allocator: std.mem.Allocator, t: Tensor) ![]u8 {
    const n: usize = t.numel;
    const result = try allocator.alloc(u8, n * 4);
    errdefer allocator.free(result);

    const f32_slice = std.mem.bytesAsSlice(f32, result);

    switch (t.dtype) {
        .f32 => @memcpy(result, t.data()[0 .. n * 4]),
        .f16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0..n];
            for (src, f32_slice) |v, *dst| dst.* = dtype_mod.fp16ToF32(v);
        },
        .bf16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0..n];
            for (src, f32_slice) |v, *dst| dst.* = dtype_mod.bf16ToF32(v);
        },
        else => return error.UnsupportedDType,
    }

    return result;
}

fn convertToF16(allocator: std.mem.Allocator, t: Tensor) ![]u8 {
    const n: usize = t.numel;
    const result = try allocator.alloc(u8, n * 2);
    errdefer allocator.free(result);

    const f16_slice = std.mem.bytesAsSlice(u16, result);

    switch (t.dtype) {
        .f32 => {
            const src = @as([*]align(1) const f32, @ptrCast(t.data().ptr))[0..n];
            for (src, f16_slice) |v, *dst| dst.* = convert.f32ToF16(v);
        },
        .f16 => @memcpy(result, t.data()[0 .. n * 2]),
        .bf16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0..n];
            for (src, f16_slice) |v, *dst| {
                const f32_val = dtype_mod.bf16ToF32(v);
                dst.* = convert.f32ToF16(f32_val);
            }
        },
        else => return error.UnsupportedDType,
    }

    return result;
}

// =============================================================================
// Output Path Generation
// =============================================================================

fn generateNativeOutputPath(allocator: std.mem.Allocator, input_path: []const u8, quant: NativeQuantType, output_dir: []const u8) ![]const u8 {
    var model_name: ?[]const u8 = null;

    var current_path = input_path;
    while (current_path.len > 0) {
        const basename = std.fs.path.basename(current_path);
        if (std.mem.startsWith(u8, basename, "models--")) {
            model_name = basename;
            break;
        }
        const parent = std.fs.path.dirname(current_path);
        if (parent == null or std.mem.eql(u8, parent.?, current_path)) break;
        current_path = parent.?;
    }

    const name_to_use = model_name orelse std.fs.path.basename(input_path);

    var clean_name = name_to_use;
    // Remove existing suffix like -MLX-4bit
    if (std.mem.indexOf(u8, clean_name, "-MLX")) |idx| {
        clean_name = clean_name[0..idx];
    }

    var result = std.ArrayListUnmanaged(u8){};
    errdefer result.deinit(allocator);

    try result.writer(allocator).print("{s}/{s}-{s}", .{ output_dir, clean_name, quant.toString() });

    return try result.toOwnedSlice(allocator);
}

// =============================================================================
// Tests
// =============================================================================

test "NativeQuantType parsing" {
    try std.testing.expectEqual(NativeQuantType.q4_k_m, NativeQuantType.fromString("q4_k_m").?);
    try std.testing.expectEqual(NativeQuantType.q4_k_m, NativeQuantType.fromString("Q4_K_M").?);
    try std.testing.expectEqual(NativeQuantType.q4_k_m, NativeQuantType.fromString("q4km").?);
    try std.testing.expectEqual(NativeQuantType.q8_0, NativeQuantType.fromString("q8_0").?);
    try std.testing.expectEqual(NativeQuantType.q8_0, NativeQuantType.fromString("q8").?);
    try std.testing.expect(NativeQuantType.fromString("invalid") == null);
}
