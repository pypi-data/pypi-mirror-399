//! Model Conversion Utilities
//!
//! Shared infrastructure for model conversion. NOT a generic walker -
//! just utilities that both grouped-affine (MLX export) and native converters need.
//!
//! Design principle: Keep format-specific logic in grouped_affine.zig and native.zig.
//! This module only contains genuinely shared code.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const safetensors = @import("../safetensors/root.zig");
const dtype_mod = @import("../../dtype.zig");

pub const mapping = @import("mapping.zig");
pub const grouped_affine = @import("grouped_affine.zig");
pub const mlx = @import("mlx.zig");
pub const mlx_paths = @import("mlx_paths.zig");
pub const native = @import("native.zig");

// Re-export key types for convenience
pub const Role = mapping.Role;
pub const TensorInfo = mapping.TensorInfo;

// =============================================================================
// Progress Reporting
// =============================================================================

/// Callback for conversion progress reporting.
/// Both MLX and GGUF converters can use the same progress interface.
pub const ProgressCallback = *const fn (
    current: usize,
    total: usize,
    tensor_name: []const u8,
    user_data: ?*anyopaque,
) void;

/// Progress context that can be passed through conversion.
pub const ProgressContext = struct {
    callback: ?ProgressCallback = null,
    user_data: ?*anyopaque = null,

    /// Report progress if callback is set.
    pub fn report(self: ProgressContext, current: usize, total: usize, name: []const u8) void {
        if (self.callback) |cb| cb(current, total, name, self.user_data);
    }
};

// =============================================================================
// Tie Embeddings Logic
// =============================================================================

/// Check if model ties word embeddings (lm_head shares token_embed weights).
/// This is a model config decision, not a format decision.
/// When true, we should skip writing lm_head separately.
pub fn tiesWordEmbeddings(tie_word_embeddings: bool) bool {
    return tie_word_embeddings;
}

/// Check if a tensor should be skipped due to tied embeddings.
/// Convenience function combining role check and config check.
pub fn shouldSkipForTiedEmbeddings(info: mapping.TensorInfo, tie_word_embeddings: bool) bool {
    return tie_word_embeddings and mapping.isLmHead(info.role);
}

// =============================================================================
// Quantization Validation
// =============================================================================

/// Check if model contains already-quantized tensors.
/// We don't support re-quantizing quantized models.
pub fn isAlreadyQuantized(src: *safetensors.SafeTensors) bool {
    var it = src.entries.iterator();
    while (it.next()) |kv| {
        const entry = kv.value_ptr.*;
        switch (entry.dtype) {
            .grouped_affine_u4, .grouped_affine_u8, .q4_0, .q4_1, .q8_0, .q6_k => return true,
            else => {},
        }
    }
    return false;
}

/// Check if a tensor should be quantized based on its properties.
/// Combines role-based check with tensor shape/dtype validation.
pub fn shouldQuantizeTensor(info: mapping.TensorInfo, t: tensor.Tensor) bool {
    // Role-based check first
    if (!mapping.shouldQuantize(info.role)) return false;

    // Only quantize 2D weight matrices
    if (t.n_dims != 2) return false;

    // Only quantize float tensors
    switch (t.dtype) {
        .f32, .f16, .bf16 => {},
        else => return false,
    }

    // Skip small tensors (< 1024 elements)
    if (t.numel < 1024) return false;

    return true;
}

// =============================================================================
// Tensor Data Conversion
// =============================================================================

/// Result of tensorToF32 - tracks ownership for proper cleanup.
pub const F32Result = struct {
    data: []const u8,
    owned: ?[]f32, // Non-null if we allocated, null if borrowed

    pub fn deinit(self: F32Result, allocator: std.mem.Allocator) void {
        if (self.owned) |owned| allocator.free(owned);
    }

    pub fn asF32Slice(self: F32Result) []align(1) const f32 {
        return std.mem.bytesAsSlice(f32, @constCast(self.data));
    }
};

/// Convert tensor data to F32, tracking allocation ownership.
/// Returns borrowed slice for F32 tensors, owned allocation for others.
pub fn tensorToF32(allocator: std.mem.Allocator, t: tensor.Tensor) !F32Result {
    switch (t.dtype) {
        .f32 => return .{ .data = t.data()[0..t.data_size], .owned = null },
        .f16 => {
            const src = t.asSliceUnaligned(u16);
            const dst = try allocator.alloc(f32, src.len);
            for (src, dst) |s, *d| d.* = dtype_mod.fp16ToF32(s);
            return .{ .data = std.mem.sliceAsBytes(dst), .owned = dst };
        },
        .bf16 => {
            const src = t.asSliceUnaligned(u16);
            const dst = try allocator.alloc(f32, src.len);
            for (src, dst) |s, *d| d.* = dtype_mod.bf16ToF32(s);
            return .{ .data = std.mem.sliceAsBytes(dst), .owned = dst };
        },
        else => return error.UnsupportedDType,
    }
}

/// Convert tensor data to F32 as owned allocation (always allocates).
pub fn tensorToF32Alloc(allocator: std.mem.Allocator, t: tensor.Tensor) ![]f32 {
    const n: usize = t.numel;
    const result = try allocator.alloc(f32, n);
    errdefer allocator.free(result);

    switch (t.dtype) {
        .f32 => {
            const src = @as([*]align(1) const f32, @ptrCast(t.data().ptr))[0..n];
            @memcpy(result, src);
        },
        .f16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0..n];
            for (src, result) |v, *dst| dst.* = dtype_mod.fp16ToF32(v);
        },
        .bf16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0..n];
            for (src, result) |v, *dst| dst.* = dtype_mod.bf16ToF32(v);
        },
        else => return error.UnsupportedDType,
    }

    return result;
}

// =============================================================================
// Float Conversion Utilities
// =============================================================================

/// Convert F32 to BF16 (truncate lower 16 bits).
pub fn f32ToBf16(value: f32) u16 {
    const bits: u32 = @bitCast(value);
    return @intCast(bits >> 16);
}

/// Convert F32 to F16 using IEEE 754 conversion.
pub fn f32ToF16(f: f32) u16 {
    const bits: u32 = @bitCast(f);
    const sign: u32 = (bits >> 31) & 1;
    var exp: i32 = @intCast((bits >> 23) & 0xFF);
    var mantissa: u32 = bits & 0x7FFFFF;

    if (exp == 0xFF) {
        // Inf/NaN
        return @intCast((sign << 15) | 0x7C00 | (if (mantissa != 0) @as(u32, 0x200) else 0));
    }

    exp -= 127; // Unbias f32 exponent

    if (exp > 15) {
        // Overflow to inf
        return @intCast((sign << 15) | 0x7C00);
    }

    if (exp < -14) {
        // Underflow to zero or denormal
        if (exp < -24) return @intCast(sign << 15);
        // Denormal
        mantissa |= 0x800000;
        const shift: u5 = @intCast(-exp - 14 + 13);
        mantissa >>= shift;
        return @intCast((sign << 15) | (mantissa & 0x3FF));
    }

    // Normal number
    const f16_exp: u32 = @intCast(exp + 15);
    return @intCast((sign << 15) | (f16_exp << 10) | (mantissa >> 13));
}

/// Convert F16 bits to F32.
pub fn f16ToF32(bits: u16) f32 {
    return @floatCast(@as(f16, @bitCast(bits)));
}

// =============================================================================
// Tensor Ordering
// =============================================================================

/// Compare tensor names for consistent ordering.
/// Order: token_embd, blk.0.*, blk.1.*, ..., output_norm, output
pub fn compareTensorNames(a: []const u8, b: []const u8) bool {
    const order_a = getTensorOrder(a);
    const order_b = getTensorOrder(b);
    if (order_a != order_b) return order_a < order_b;
    // Same category - sort alphabetically
    return std.mem.lessThan(u8, a, b);
}

fn getTensorOrder(name: []const u8) u32 {
    // token_embd first (order 0)
    if (std.mem.indexOf(u8, name, "embed_tokens") != null) return 0;

    // Block tensors (order 1000 + layer_num)
    const info = mapping.parseHfName(name);
    if (info.layer) |layer| {
        return 1000 + layer;
    }

    // output_norm near end (order 100000)
    if (std.mem.indexOf(u8, name, "norm") != null) return 100000;

    // output/lm_head last (order 100001)
    if (std.mem.indexOf(u8, name, "lm_head") != null) return 100001;

    // Unknown - put at end
    return 200000;
}

/// Sort tensor names for consistent output ordering.
pub fn sortTensorNames(names: [][]const u8) void {
    std.mem.sort([]const u8, names, {}, struct {
        fn lessThan(_: void, a: []const u8, b: []const u8) bool {
            return compareTensorNames(a, b);
        }
    }.lessThan);
}

// =============================================================================
// K-Quant Precision Selection (Q4_K_M strategy)
// =============================================================================

/// use_more_bits logic for Q4_K_M quantization (from llama.cpp).
/// Returns true for first/last 1/8 of layers, plus every 3rd layer in the middle.
pub fn useMoreBits(i_layer: usize, n_layers: usize) bool {
    if (n_layers == 0) return false;
    // First 1/8 of layers
    if (i_layer < n_layers / 8) return true;
    // Last 1/8 of layers
    if (i_layer >= 7 * n_layers / 8) return true;
    // Every 3rd layer in the middle section
    const middle_start = n_layers / 8;
    if ((i_layer - middle_start) % 3 == 2) return true;
    return false;
}

/// Determine if a tensor should use higher precision (Q6_K vs Q4_K).
/// Matches llama.cpp quantization strategy.
pub fn shouldUseHigherPrecision(name: []const u8, n_layers: usize) bool {
    // Token embeddings are always Q6_K
    if (std.mem.indexOf(u8, name, "token_embd") != null) return true;
    if (std.mem.indexOf(u8, name, "embed_tokens") != null) return true;

    // For layer tensors, use Q6_K only for certain layers based on use_more_bits
    if (mapping.parseLayerFromGguf(name)) |i_layer| {
        const use_q6k = useMoreBits(i_layer, n_layers);

        // Value projections - Q6_K only for use_more_bits layers
        if (std.mem.indexOf(u8, name, "attn_v") != null) return use_q6k;
        if (std.mem.indexOf(u8, name, "v_proj") != null) return use_q6k;

        // FFN down projections - Q6_K only for use_more_bits layers
        if (std.mem.indexOf(u8, name, "ffn_down") != null) return use_q6k;
        if (std.mem.indexOf(u8, name, "down_proj") != null) return use_q6k;
    }

    return false;
}

// =============================================================================
// Tests
// =============================================================================

test "f32ToBf16 round trip" {
    const values = [_]f32{ 0.0, 1.0, -1.0, 0.5, 2.0, 0.001, 100.0 };
    for (values) |v| {
        const bf16 = f32ToBf16(v);
        const back = dtype_mod.bf16ToF32(bf16);
        try std.testing.expectApproxEqAbs(v, back, 0.01);
    }
}

test "compareTensorNames ordering" {
    // Embeddings come first
    try std.testing.expect(compareTensorNames("model.embed_tokens.weight", "model.layers.0.attn.weight"));
    // Lower layers before higher layers
    try std.testing.expect(compareTensorNames("model.layers.0.attn.weight", "model.layers.1.attn.weight"));
    // Layers before final norm
    try std.testing.expect(compareTensorNames("model.layers.5.attn.weight", "model.norm.weight"));
    // Final norm before lm_head
    try std.testing.expect(compareTensorNames("model.norm.weight", "lm_head.weight"));
}

test "useMoreBits" {
    const n_layers: usize = 32;

    // First 1/8 (layers 0-3)
    try std.testing.expect(useMoreBits(0, n_layers));
    try std.testing.expect(useMoreBits(3, n_layers));

    // Middle section - every 3rd
    try std.testing.expect(!useMoreBits(4, n_layers)); // 4-4=0, 0%3=0
    try std.testing.expect(!useMoreBits(5, n_layers)); // 5-4=1, 1%3=1
    try std.testing.expect(useMoreBits(6, n_layers)); // 6-4=2, 2%3=2

    // Last 1/8 (layers 28-31)
    try std.testing.expect(useMoreBits(28, n_layers));
    try std.testing.expect(useMoreBits(31, n_layers));
}

// =============================================================================
// File Copy Utilities (shared by both converters)
// =============================================================================

/// Copy config.json from source to output directory.
pub fn copyConfigFile(allocator: std.mem.Allocator, source_config_path: []const u8, output_path: []const u8) !void {
    const dst_config = try std.fs.path.join(allocator, &.{ output_path, "config.json" });
    defer allocator.free(dst_config);

    std.fs.cwd().copyFile(source_config_path, std.fs.cwd(), dst_config, .{}) catch |err| {
        if (err != error.FileNotFound) return err;
    };
}

/// Copy tokenizer files from source directory to output directory.
/// Copies tokenizer.json and tokenizer_config.json if they exist.
///
/// Note: This copies fewer files than MLX conversion (mlx_paths.MLXModelDir.copyTokenizerFiles),
/// which also copies special_tokens_map.json, generation_config.json, merges.txt, vocab.json.
/// Native conversion intentionally copies only the minimal required files.
pub fn copyTokenizerFiles(allocator: std.mem.Allocator, source_dir: []const u8, output_path: []const u8) !void {
    const files = [_][]const u8{ "tokenizer.json", "tokenizer_config.json" };

    for (files) |filename| {
        const src_path = try std.fs.path.join(allocator, &.{ source_dir, filename });
        defer allocator.free(src_path);
        const dst_path = try std.fs.path.join(allocator, &.{ output_path, filename });
        defer allocator.free(dst_path);

        std.fs.cwd().copyFile(src_path, std.fs.cwd(), dst_path, .{}) catch |err| {
            if (err != error.FileNotFound) return err;
            // Silently skip missing files
        };
    }
}
