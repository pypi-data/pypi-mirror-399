//! Activation functions with stride-aware, dtype-generic implementations.
//!
//! All ops work with TensorView and handle both contiguous and strided tensors.
//! Uses comptime generics to eliminate dtype dispatch repetition.

const std = @import("std");
const tv = @import("tensor_view.zig");
const math = @import("math.zig");

const TensorView = tv.TensorView;
const DType = tv.DType;

// Use existing SIMD infrastructure
const simd = math.simd;
const VEC_LEN = simd.f32_vec_len;
const F32Vec = simd.F32Vec;
const fastExp = math.fastExp;
const fastExpScalar = math.fastExpScalar;

/// Dtype conversion helpers - wrapped to remove inline calling convention
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

/// Generic element-wise unary op that handles strides and dtype conversion.
/// Computes: out[i] = op(input[i]) for all elements
fn unaryOpGeneric(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    input: TensorView,
    comptime op: fn (f32) f32,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));

    if (input.isContiguous() and out.isContiguous()) {
        // Fast path: contiguous tensors
        for (0..input.numel) |i| {
            out_data[i] = fromF32(op(toF32(in_data[i])));
        }
    } else {
        // Slow path: strided tensors - iterate by logical coordinates
        var coords: [tv.MAX_NDIM]usize = undefined;
        for (0..input.numel) |i| {
            input.indexToCoords(i, &coords);
            const in_offset = input.coordsToOffset(coords[0..input.ndim]);
            const out_offset = out.coordsToOffset(coords[0..out.ndim]);
            out_data[out_offset] = fromF32(op(toF32(in_data[in_offset])));
        }
    }
}

// Identity conversions for f32
fn f32Identity(x: f32) f32 {
    return x;
}

/// SiLU activation: x * sigmoid(x)
pub fn silu(out: TensorView, input: TensorView) void {
    if (input.dtype == .f32 and out.dtype == .f32 and input.isContiguous() and out.isContiguous()) {
        math.siluContiguous(out.asSlice(f32), input.asSlice(f32));
        return;
    }

    const siluFn = struct {
        fn f(x: f32) f32 {
            return x / (1.0 + fastExpScalar(-x));
        }
    }.f;

    switch (input.dtype) {
        .f32 => unaryOpGeneric(f32, f32Identity, f32Identity, out, input, siluFn),
        .f16 => unaryOpGeneric(u16, fp16ToF32, f32ToFp16, out, input, siluFn),
        .bf16 => unaryOpGeneric(u16, bf16ToF32, f32ToBf16, out, input, siluFn),
        else => unreachable,
    }
}

/// GELU activation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
pub fn gelu(out: TensorView, input: TensorView) void {
    if (input.dtype == .f32 and out.dtype == .f32 and input.isContiguous() and out.isContiguous()) {
        math.geluContiguous(out.asSlice(f32), input.asSlice(f32));
        return;
    }

    const geluFn = struct {
        fn f(x: f32) f32 {
            const sqrt_2_over_pi: f32 = 0.7978845608028654;
            const coeff: f32 = 0.044715;
            const x3 = x * x * x;
            const inner = sqrt_2_over_pi * (x + coeff * x3);
            return 0.5 * x * (1.0 + std.math.tanh(inner));
        }
    }.f;

    switch (input.dtype) {
        .f32 => unaryOpGeneric(f32, f32Identity, f32Identity, out, input, geluFn),
        .f16 => unaryOpGeneric(u16, fp16ToF32, f32ToFp16, out, input, geluFn),
        .bf16 => unaryOpGeneric(u16, bf16ToF32, f32ToBf16, out, input, geluFn),
        else => unreachable,
    }
}

/// ReLU activation: max(0, x)
pub fn relu(out: TensorView, input: TensorView) void {
    if (input.dtype == .f32 and out.dtype == .f32 and input.isContiguous() and out.isContiguous()) {
        math.reluContiguous(out.asSlice(f32), input.asSlice(f32));
        return;
    }

    const reluFn = struct {
        fn f(x: f32) f32 {
            return @max(0, x);
        }
    }.f;

    switch (input.dtype) {
        .f32 => unaryOpGeneric(f32, f32Identity, f32Identity, out, input, reluFn),
        .f16 => unaryOpGeneric(u16, fp16ToF32, f32ToFp16, out, input, reluFn),
        .bf16 => unaryOpGeneric(u16, bf16ToF32, f32ToBf16, out, input, reluFn),
        else => unreachable,
    }
}

/// Sigmoid activation: 1 / (1 + exp(-x))
pub fn sigmoid(out: TensorView, input: TensorView) void {
    if (input.dtype == .f32 and out.dtype == .f32 and input.isContiguous() and out.isContiguous()) {
        math.sigmoidContiguous(out.asSlice(f32), input.asSlice(f32));
        return;
    }

    const sigmoidFn = struct {
        fn f(x: f32) f32 {
            return 1.0 / (1.0 + fastExpScalar(-x));
        }
    }.f;

    switch (input.dtype) {
        .f32 => unaryOpGeneric(f32, f32Identity, f32Identity, out, input, sigmoidFn),
        .f16 => unaryOpGeneric(u16, fp16ToF32, f32ToFp16, out, input, sigmoidFn),
        .bf16 => unaryOpGeneric(u16, bf16ToF32, f32ToBf16, out, input, sigmoidFn),
        else => unreachable,
    }
}

/// Tanh activation
pub fn tanh(out: TensorView, input: TensorView) void {
    if (input.dtype == .f32 and out.dtype == .f32 and input.isContiguous() and out.isContiguous()) {
        math.tanhContiguous(out.asSlice(f32), input.asSlice(f32));
        return;
    }

    const tanhFn = struct {
        fn f(x: f32) f32 {
            return std.math.tanh(x);
        }
    }.f;

    switch (input.dtype) {
        .f32 => unaryOpGeneric(f32, f32Identity, f32Identity, out, input, tanhFn),
        .f16 => unaryOpGeneric(u16, fp16ToF32, f32ToFp16, out, input, tanhFn),
        .bf16 => unaryOpGeneric(u16, bf16ToF32, f32ToBf16, out, input, tanhFn),
        else => unreachable,
    }
}

/// Softmax over specified dimension (PyTorch-compatible)
/// dim: dimension to apply softmax over (supports negative indexing)
pub fn softmaxDim(out: TensorView, input: TensorView, dim: i32) void {
    switch (input.dtype) {
        .f32 => softmaxDimTyped(f32, f32Identity, f32Identity, out, input, dim),
        .f16 => softmaxDimTyped(u16, fp16ToF32, f32ToFp16, out, input, dim),
        .bf16 => softmaxDimTyped(u16, bf16ToF32, f32ToBf16, out, input, dim),
        else => unreachable,
    }
}

/// Softmax over last dimension (convenience wrapper)
pub fn softmax(out: TensorView, input: TensorView) void {
    softmaxDim(out, input, -1);
}

fn softmaxDimTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    input: TensorView,
    dim_arg: i32,
) void {
    std.debug.assert(input.ndim >= 1);
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));

    // Handle negative dimension (PyTorch convention)
    const ndim_i32: i32 = @intCast(input.ndim);
    const dim: usize = @intCast(if (dim_arg < 0) dim_arg + ndim_i32 else dim_arg);
    std.debug.assert(dim < input.ndim);

    const dim_size = input.shape[dim];

    // Fast path: if dim is last dimension and contiguous
    if (dim == input.ndim - 1 and input.isContiguous() and out.isContiguous()) {
        const outer_size = input.numel / dim_size;
        if (input.dtype == .f32 and out.dtype == .f32) {
            math.softmaxContiguous(out.asSlice(f32), input.asSlice(f32), outer_size, dim_size);
            return;
        }

        for (0..outer_size) |outer| {
            const offset = outer * dim_size;

            // Find max
            var max_val: f32 = -std.math.inf(f32);
            for (0..dim_size) |i| {
                max_val = @max(max_val, toF32(in_data[offset + i]));
            }

            // Exp and sum
            var sum: f32 = 0;
            for (0..dim_size) |i| {
                const exp_val = fastExpScalar(toF32(in_data[offset + i]) - max_val);
                out_data[offset + i] = fromF32(exp_val);
                sum += exp_val;
            }

            // Normalize
            const inv_sum = 1.0 / sum;
            for (0..dim_size) |i| {
                out_data[offset + i] = fromF32(toF32(out_data[offset + i]) * inv_sum);
            }
        }
    } else {
        // General path: strided access for any dimension
        // Compute outer_size = product of all dims except dim
        var outer_size: usize = 1;
        for (0..input.ndim) |d| {
            if (d != dim) outer_size *= input.shape[d];
        }

        var coords: [tv.MAX_NDIM]usize = [_]usize{0} ** tv.MAX_NDIM;
        for (0..outer_size) |outer| {
            // Convert outer index to coords, skipping the softmax dimension
            var remaining = outer;
            var d_idx: usize = input.ndim - 1;
            while (true) {
                if (d_idx != dim) {
                    coords[d_idx] = remaining % input.shape[d_idx];
                    remaining /= input.shape[d_idx];
                }
                if (d_idx == 0) break;
                d_idx -= 1;
            }

            // Find max along dim
            var max_val: f32 = -std.math.inf(f32);
            for (0..dim_size) |i| {
                coords[dim] = i;
                const in_off = input.coordsToOffset(coords[0..input.ndim]);
                max_val = @max(max_val, toF32(in_data[in_off]));
            }

            // Exp, sum, and store
            var sum: f32 = 0;
            for (0..dim_size) |i| {
                coords[dim] = i;
                const in_off = input.coordsToOffset(coords[0..input.ndim]);
                const out_off = out.coordsToOffset(coords[0..out.ndim]);
                const exp_val = fastExpScalar(toF32(in_data[in_off]) - max_val);
                out_data[out_off] = fromF32(exp_val);
                sum += exp_val;
            }

            // Normalize
            const inv_sum = 1.0 / sum;
            for (0..dim_size) |i| {
                coords[dim] = i;
                const out_off = out.coordsToOffset(coords[0..out.ndim]);
                out_data[out_off] = fromF32(toF32(out_data[out_off]) * inv_sum);
            }
        }
    }
}

/// Reciprocal square root: 1 / sqrt(x)
pub fn rsqrt(out: TensorView, input: TensorView) void {
    const rsqrtFn = struct {
        fn f(x: f32) f32 {
            return 1.0 / @sqrt(x);
        }
    }.f;

    switch (input.dtype) {
        .f32 => unaryOpGeneric(f32, f32Identity, f32Identity, out, input, rsqrtFn),
        .f16 => unaryOpGeneric(u16, fp16ToF32, f32ToFp16, out, input, rsqrtFn),
        .bf16 => unaryOpGeneric(u16, bf16ToF32, f32ToBf16, out, input, rsqrtFn),
        else => {},
    }
}

test "silu contiguous" {
    var in_data = [_]f32{ 0, 1, -1, 2 };
    var out_data = [_]f32{ 0, 0, 0, 0 };

    const input = TensorView.initContiguous(@ptrCast(&in_data), &.{4}, .f32);
    const out = TensorView.initContiguous(@ptrCast(&out_data), &.{4}, .f32);

    silu(out, input);

    // silu(0) = 0
    try std.testing.expectApproxEqAbs(@as(f32, 0), out_data[0], 1e-5);
    // silu(1) ≈ 0.731
    try std.testing.expectApproxEqAbs(@as(f32, 0.731), out_data[1], 1e-2);
}
