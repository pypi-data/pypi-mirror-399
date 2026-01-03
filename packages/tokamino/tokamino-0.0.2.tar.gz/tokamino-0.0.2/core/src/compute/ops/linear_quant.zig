//! Quantized linear operations for tokamino.ops
//!
//! These functions perform matrix multiplication with quantized weights.
//! Input activations are f32, weights are quantized (Q4_0 or Q8_0 format).

const std = @import("std");
const tensor = @import("../../tensor.zig");
const dtype = @import("../../dtype.zig");
const matmul = @import("matmul.zig");

const BlockQ4_0 = dtype.BlockQ4_0;
const BlockQ8_0 = dtype.BlockQ8_0;
const Tensor = tensor.Tensor;

/// Q4_0 linear layer: out = input @ weights^T + bias
/// input: [batch, in_features] as f32
/// weights: [out_features * n_blocks] as BlockQ4_0 (row-major, each row is out_features blocks)
/// bias: optional [out_features] as f32
/// output: [batch, out_features] as f32
pub fn linearQ4_0(
    input: []const f32,
    weights: []const BlockQ4_0,
    output: []f32,
    batch: usize,
    in_features: usize,
    out_features: usize,
    bias: ?[]const f32,
) void {
    const block_size = BlockQ4_0.block_size; // 32
    const n_blocks = in_features / block_size;
    std.debug.assert(in_features % block_size == 0);
    std.debug.assert(weights.len >= out_features * n_blocks);
    std.debug.assert(output.len >= batch * out_features);

    var a = Tensor.view(@ptrCast(@constCast(input.ptr)), &.{ batch, in_features }, .f32, null);
    const weights_bytes = std.mem.sliceAsBytes(weights);
    var b = Tensor.view(@ptrCast(@constCast(weights_bytes.ptr)), &.{ out_features, n_blocks }, .q4_0, weights_bytes.len);
    var out = Tensor.view(@ptrCast(output.ptr), &.{ batch, out_features }, .f32, null);

    matmul.matmulQ4_0(&a, &b, &out);

    if (bias) |b_ptr| {
        for (0..batch) |row| {
            const row_offset = row * out_features;
            for (0..out_features) |o| {
                output[row_offset + o] += b_ptr[o];
            }
        }
    }
}

/// Q8_0 linear layer: out = input @ weights^T + bias
/// input: [batch, in_features] as f32
/// weights: [out_features * n_blocks] as BlockQ8_0 (row-major)
/// bias: optional [out_features] as f32
/// output: [batch, out_features] as f32
pub fn linearQ8_0(
    input: []const f32,
    weights: []const BlockQ8_0,
    output: []f32,
    batch: usize,
    in_features: usize,
    out_features: usize,
    bias: ?[]const f32,
) void {
    const block_size = BlockQ8_0.block_size; // 32
    const n_blocks = in_features / block_size;
    std.debug.assert(in_features % block_size == 0);
    std.debug.assert(weights.len >= out_features * n_blocks);
    std.debug.assert(output.len >= batch * out_features);

    var a = Tensor.view(@ptrCast(@constCast(input.ptr)), &.{ batch, in_features }, .f32, null);
    const weights_bytes = std.mem.sliceAsBytes(weights);
    var b = Tensor.view(@ptrCast(@constCast(weights_bytes.ptr)), &.{ out_features, n_blocks }, .q8_0, weights_bytes.len);
    var out = Tensor.view(@ptrCast(output.ptr), &.{ batch, out_features }, .f32, null);

    matmul.matmulQ8_0(&a, &b, &out);

    if (bias) |b_ptr| {
        for (0..batch) |row| {
            const row_offset = row * out_features;
            for (0..out_features) |o| {
                output[row_offset + o] += b_ptr[o];
            }
        }
    }
}

test "linearQ4_0 basic" {
    const allocator = std.testing.allocator;

    const batch: usize = 1;
    const in_features: usize = 32;
    const out_features: usize = 2;
    const n_blocks = in_features / 32;

    // Input: all 1.0
    const input = try allocator.alloc(f32, batch * in_features);
    defer allocator.free(input);
    @memset(input, 1.0);

    // Weights: 2 rows of Q4_0 blocks
    var weights = try allocator.alloc(BlockQ4_0, out_features * n_blocks);
    defer allocator.free(weights);

    // First row: scale=1.0, all nibbles = 8 (which becomes 0 after -8 offset)
    weights[0] = BlockQ4_0{
        .d = 0x3C00, // 1.0 in fp16
        .qs = [_]u8{0x88} ** 16, // all 8s = 0 after offset
    };
    // Second row: scale=1.0, all nibbles = 9 (which becomes 1 after -8 offset)
    weights[1] = BlockQ4_0{
        .d = 0x3C00, // 1.0 in fp16
        .qs = [_]u8{0x99} ** 16, // all 9s = 1 after offset
    };

    const output = try allocator.alloc(f32, batch * out_features);
    defer allocator.free(output);

    linearQ4_0(input, weights, output, batch, in_features, out_features, null);

    // First output: 32 * 0 * 1.0 = 0
    try std.testing.expectApproxEqAbs(@as(f32, 0.0), output[0], 1e-4);
    // Second output: 32 * 1 * 1.0 = 32
    try std.testing.expectApproxEqAbs(@as(f32, 32.0), output[1], 1e-4);
}

test "linearQ8_0 basic" {
    const allocator = std.testing.allocator;

    const batch: usize = 1;
    const in_features: usize = 32;
    const out_features: usize = 2;
    const n_blocks = in_features / 32;

    // Input: all 1.0
    const input = try allocator.alloc(f32, batch * in_features);
    defer allocator.free(input);
    @memset(input, 1.0);

    // Weights: 2 rows of Q8_0 blocks
    var weights = try allocator.alloc(BlockQ8_0, out_features * n_blocks);
    defer allocator.free(weights);

    // First row: scale=1.0, all int8s = 0
    weights[0] = BlockQ8_0{
        .d = 0x3C00, // 1.0 in fp16
        .qs = [_]i8{0} ** 32,
    };
    // Second row: scale=1.0, all int8s = 1
    weights[1] = BlockQ8_0{
        .d = 0x3C00, // 1.0 in fp16
        .qs = [_]i8{1} ** 32,
    };

    const output = try allocator.alloc(f32, batch * out_features);
    defer allocator.free(output);

    linearQ8_0(input, weights, output, batch, in_features, out_features, null);

    // First output: 32 * 0 * 1.0 = 0
    try std.testing.expectApproxEqAbs(@as(f32, 0.0), output[0], 1e-4);
    // Second output: 32 * 1 * 1.0 = 32
    try std.testing.expectApproxEqAbs(@as(f32, 32.0), output[1], 1e-4);
}
