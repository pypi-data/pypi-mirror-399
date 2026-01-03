//! Tensor creation operations.

const std = @import("std");
const tv = @import("tensor_view.zig");
const tensor = @import("../../tensor.zig");
const matmul_ops = @import("matmul.zig");
const parallel = @import("../parallel.zig");
const simd = @import("math.zig").simd;

const TensorView = tv.TensorView;
const DType = tv.DType;

// SIMD configuration
const VEC_LEN = simd.f32_vec_len;
const F32Vec = simd.F32Vec;

/// Fill tensor with zeros
pub fn zeros(out: TensorView) void {
    switch (out.dtype) {
        .f32 => zerosTyped(f32, out),
        .f16, .bf16 => zerosTyped(u16, out),
        .i32 => zerosTyped(i32, out),
        .i64 => zerosTyped(i64, out),
    }
}

fn zerosTyped(comptime T: type, out: TensorView) void {
    const data = @as([*]T, @ptrCast(@alignCast(out.data)));
    @memset(data[0..out.numel], 0);
}

/// Fill tensor with ones
pub fn ones(out: TensorView) void {
    switch (out.dtype) {
        .f32 => onesTyped(f32, out),
        .f16, .bf16 => onesTyped(u16, out),
        .i32 => onesTyped(i32, out),
        .i64 => onesTyped(i64, out),
    }
}

fn onesTyped(comptime T: type, out: TensorView) void {
    const data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const one: T = if (T == f32) 1.0 else if (T == u16) 0x3C00 else 1; // 0x3C00 is fp16(1.0)
    @memset(data[0..out.numel], one);
}

/// Fill tensor with range [0, n)
pub fn arange(out: TensorView) void {
    switch (out.dtype) {
        .f32 => arangeTyped(f32, out),
        .i32 => arangeTyped(i32, out),
        .i64 => arangeTyped(i64, out),
        else => unreachable,
    }
}

fn arangeTyped(comptime T: type, out: TensorView) void {
    const data = @as([*]T, @ptrCast(@alignCast(out.data)));
    for (0..out.numel) |i| {
        data[i] = if (@typeInfo(T) == .float) @floatFromInt(i) else @intCast(i);
    }
}

/// Create causal attention mask
/// out: [seq_len, seq_len] with 0.0 for valid positions, -inf for masked
pub fn causalMask(out: TensorView) void {
    std.debug.assert(out.ndim == 2);
    std.debug.assert(out.shape[0] == out.shape[1]);

    switch (out.dtype) {
        .f32 => causalMaskTyped(f32, out),
        .f16, .bf16 => causalMaskTyped(u16, out),
        else => unreachable,
    }
}

fn causalMaskTyped(comptime T: type, out: TensorView) void {
    const data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const seq_len = out.shape[0];

    const zero: T = 0;
    const neg_inf: T = if (T == f32) -std.math.inf(f32) else 0xFC00; // 0xFC00 is fp16(-inf)

    for (0..seq_len) |row| {
        for (0..seq_len) |col| {
            const idx = row * @as(usize, @intCast(out.strides[0])) +
                col * @as(usize, @intCast(out.strides[1]));
            data[idx] = if (col <= row) zero else neg_inf;
        }
    }
}

/// Upper triangular matrix
/// Zeros out elements below the diagonal
/// diagonal: 0 = main diagonal, positive = above, negative = below
pub fn triu(out: TensorView, input: TensorView, diagonal: i32) void {
    switch (out.dtype) {
        .f32 => triuTyped(f32, out, input, diagonal),
        .f16, .bf16 => triuTyped(u16, out, input, diagonal),
        else => {},
    }
}

fn triuTyped(comptime T: type, out: TensorView, input: TensorView, diagonal: i32) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));

    std.debug.assert(input.ndim >= 2);
    const rows = input.shape[input.ndim - 2];
    const cols = input.shape[input.ndim - 1];
    const batch_size = input.numel / (rows * cols);

    const zero: T = 0;

    for (0..batch_size) |b| {
        const batch_offset = b * rows * cols;
        for (0..rows) |row| {
            for (0..cols) |col| {
                const idx = batch_offset + row * cols + col;
                const signed_col: i64 = @intCast(col);
                const signed_row: i64 = @intCast(row);
                if (signed_col >= signed_row + diagonal) {
                    out_data[idx] = in_data[idx];
                } else {
                    out_data[idx] = zero;
                }
            }
        }
    }
}

/// Embedding lookup
/// indices: [batch, seq] or [seq]
/// weight: [vocab_size, hidden_dim]
/// out: [batch, seq, hidden_dim] or [seq, hidden_dim]
pub fn embedding(out: TensorView, weight: TensorView, indices: TensorView) void {
    switch (out.dtype) {
        .f32 => embeddingTyped(f32, out, weight, indices),
        .f16, .bf16 => embeddingTyped(u16, out, weight, indices),
        else => unreachable,
    }
}

fn embeddingTyped(comptime T: type, out: TensorView, weight: TensorView, indices: TensorView) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const w_data = @as([*]const T, @ptrCast(@alignCast(weight.data)));

    const hidden_dim = weight.shape[1];
    const num_tokens = indices.numel;

    // Handle different index types
    const indices_i64 = @as([*]const i64, @ptrCast(@alignCast(indices.data)));
    const indices_i32 = @as([*]const i32, @ptrCast(@alignCast(indices.data)));

    for (0..num_tokens) |t| {
        const idx: usize = switch (indices.dtype) {
            .i64 => @intCast(indices_i64[t]),
            .i32 => @intCast(indices_i32[t]),
            else => unreachable,
        };

        const out_offset = t * hidden_dim;
        const w_offset = idx * hidden_dim;

        @memcpy(out_data[out_offset .. out_offset + hidden_dim], w_data[w_offset .. w_offset + hidden_dim]);
    }
}

/// Matrix multiplication for linear layers
/// out = input @ weight^T
/// input: [batch, seq, in_features]
/// weight: [out_features, in_features]
/// out: [batch, seq, out_features]
pub fn linear(out: TensorView, input: TensorView, weight: TensorView) void {
    switch (out.dtype) {
        .f32 => linearTyped(f32, f32Identity, f32Identity, out, input, weight),
        .f16 => linearTyped(u16, fp16ToF32, f32ToFp16, out, input, weight),
        .bf16 => linearTyped(u16, bf16ToF32, f32ToBf16, out, input, weight),
        else => unreachable,
    }
}

const dtype_mod = @import("../../dtype.zig");

fn fp16ToF32(x: u16) f32 {
    return dtype_mod.fp16ToF32(x);
}

fn f32ToFp16(x: f32) u16 {
    return dtype_mod.f32ToFp16(x);
}

fn bf16ToF32(x: u16) f32 {
    return dtype_mod.bf16ToF32(x);
}

fn f32ToBf16(x: f32) u16 {
    return dtype_mod.f32ToBf16(x);
}

fn f32Identity(x: f32) f32 {
    return x;
}

fn linearTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    input: TensorView,
    weight: TensorView,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
    const w_data = @as([*]const T, @ptrCast(@alignCast(weight.data)));

    const num_tokens = input.numel / input.shape[input.ndim - 1];
    const in_features = input.shape[input.ndim - 1];
    const out_features = weight.shape[0];

    // For f32, use SIMD + parallel. For other types, use parallel only.
    if (T == f32) {
        linearF32Parallel(out_data, in_data, w_data, num_tokens, in_features, out_features);
    } else {
        linearTypedParallel(T, toF32, fromF32, out_data, in_data, w_data, num_tokens, in_features, out_features);
    }
}

/// SIMD-optimized parallel linear for f32
fn linearF32Parallel(
    out_data: [*]f32,
    in_data: [*]const f32,
    w_data: [*]const f32,
    num_tokens: usize,
    in_features: usize,
    out_features: usize,
) void {
    const Ctx = struct {
        out_data: [*]f32,
        in_data: [*]const f32,
        w_data: [*]const f32,
        num_tokens: usize,
        in_features: usize,
        out_features: usize,

        fn run(start: usize, end: usize, ctx: *@This()) void {
            for (start..end) |idx| {
                const t = idx / ctx.out_features;
                const o = idx % ctx.out_features;

                const in_row = ctx.in_data[t * ctx.in_features ..][0..ctx.in_features];
                const w_row = ctx.w_data[o * ctx.in_features ..][0..ctx.in_features];

                // SIMD dot product
                var sum_vec: F32Vec = @splat(0);
                var i: usize = 0;

                // Main SIMD loop
                while (i + VEC_LEN <= ctx.in_features) : (i += VEC_LEN) {
                    const in_vec: F32Vec = in_row[i..][0..VEC_LEN].*;
                    const w_vec: F32Vec = w_row[i..][0..VEC_LEN].*;
                    sum_vec = @mulAdd(F32Vec, in_vec, w_vec, sum_vec);
                }

                // Reduce vector to scalar
                var sum: f32 = @reduce(.Add, sum_vec);

                // Scalar remainder
                while (i < ctx.in_features) : (i += 1) {
                    sum += in_row[i] * w_row[i];
                }

                ctx.out_data[t * ctx.out_features + o] = sum;
            }
        }
    };

    var ctx = Ctx{
        .out_data = out_data,
        .in_data = in_data,
        .w_data = w_data,
        .num_tokens = num_tokens,
        .in_features = in_features,
        .out_features = out_features,
    };

    parallel.global().parallelFor(num_tokens * out_features, Ctx.run, &ctx);
}

/// Parallel linear for non-f32 types (bf16, f16)
fn linearTypedParallel(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out_data: [*]T,
    in_data: [*]const T,
    w_data: [*]const T,
    num_tokens: usize,
    in_features: usize,
    out_features: usize,
) void {
    const Ctx = struct {
        out_data: [*]T,
        in_data: [*]const T,
        w_data: [*]const T,
        num_tokens: usize,
        in_features: usize,
        out_features: usize,

        fn run(start: usize, end: usize, ctx: *@This()) void {
            for (start..end) |idx| {
                const t = idx / ctx.out_features;
                const o = idx % ctx.out_features;

                const in_offset = t * ctx.in_features;
                const w_offset = o * ctx.in_features;

                var sum: f32 = 0;
                for (0..ctx.in_features) |i| {
                    sum += toF32(ctx.in_data[in_offset + i]) * toF32(ctx.w_data[w_offset + i]);
                }

                ctx.out_data[t * ctx.out_features + o] = fromF32(sum);
            }
        }
    };

    var ctx = Ctx{
        .out_data = out_data,
        .in_data = in_data,
        .w_data = w_data,
        .num_tokens = num_tokens,
        .in_features = in_features,
        .out_features = out_features,
    };

    parallel.global().parallelFor(num_tokens * out_features, Ctx.run, &ctx);
}

/// General matrix multiplication
/// out = a @ b
/// a: [..., M, K]
/// b: [..., K, N]
/// out: [..., M, N]
pub fn matmul(out: TensorView, a: TensorView, b: TensorView) void {
    if (out.dtype == .f32 and a.dtype == .f32 and b.dtype == .f32 and a.ndim == 2 and b.ndim == 2 and out.ndim == 2 and
        a.isContiguous() and b.isContiguous() and out.isContiguous())
    {
        var a_tensor = tensor.Tensor.view(a.data, &.{ a.shape[0], a.shape[1] }, .f32, null);
        var b_tensor = tensor.Tensor.view(b.data, &.{ b.shape[0], b.shape[1] }, .f32, null);
        var out_tensor = tensor.Tensor.view(out.data, &.{ out.shape[0], out.shape[1] }, .f32, null);
        matmul_ops.matmulF32(&a_tensor, &b_tensor, &out_tensor);
        return;
    }

    switch (out.dtype) {
        .f32 => matmulTyped(f32, f32Identity, f32Identity, out, a, b),
        .f16 => matmulTyped(u16, fp16ToF32, f32ToFp16, out, a, b),
        .bf16 => matmulTyped(u16, bf16ToF32, f32ToBf16, out, a, b),
        else => unreachable,
    }
}

fn matmulTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    a: TensorView,
    b: TensorView,
) void {
    std.debug.assert(a.ndim >= 2 and b.ndim >= 2);

    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const a_data = @as([*]const T, @ptrCast(@alignCast(a.data)));
    const b_data = @as([*]const T, @ptrCast(@alignCast(b.data)));

    const M = a.shape[a.ndim - 2];
    const K = a.shape[a.ndim - 1];
    const N = b.shape[b.ndim - 1];
    const batch = a.numel / (M * K);

    // Simple batched matmul (can be optimized with SIMD/tiling later)
    for (0..batch) |bat| {
        const a_batch_off = bat * M * K;
        const b_batch_off = bat * K * N;
        const out_batch_off = bat * M * N;

        for (0..M) |m| {
            for (0..N) |n| {
                var sum: f32 = 0;
                for (0..K) |k| {
                    sum += toF32(a_data[a_batch_off + m * K + k]) *
                        toF32(b_data[b_batch_off + k * N + n]);
                }
                out_data[out_batch_off + m * N + n] = fromF32(sum);
            }
        }
    }
}

test "zeros fills with zeros" {
    var data = [_]f32{ 1, 2, 3, 4 };
    const out = TensorView.initContiguous(@ptrCast(&data), &.{4}, .f32);
    zeros(out);
    for (data) |v| try std.testing.expectEqual(@as(f32, 0), v);
}

test "causalMask correct shape" {
    var data = [_]f32{0} ** 9;
    const out = TensorView.initContiguous(@ptrCast(&data), &.{ 3, 3 }, .f32);
    causalMask(out);

    // Lower triangle should be 0, upper should be -inf
    try std.testing.expectEqual(@as(f32, 0), data[0]); // [0,0]
    try std.testing.expect(data[1] < -1e30); // [0,1] = -inf
    try std.testing.expectEqual(@as(f32, 0), data[4]); // [1,1]
}
