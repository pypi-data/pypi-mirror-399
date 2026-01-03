//! Normalization operations with stride-aware implementations.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const tv = @import("tensor_view.zig");
const math = @import("math.zig");

const TensorView = tv.TensorView;
const DType = tv.DType;
const MAX_NDIM = tv.MAX_NDIM;
const TensorDType = tensor.DType;

// SIMD infrastructure
const simd = math.simd;
const VEC_LEN = simd.f32_vec_len;
const F32Vec = simd.F32Vec;

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

fn viewDTypeToTensor(dt: DType) TensorDType {
    return switch (dt) {
        .f32 => .f32,
        .f16 => .f16,
        .bf16 => .bf16,
        else => .f32,
    };
}

/// RMS Normalization: out = x * rsqrt(mean(x^2) + eps) * weight
pub fn rmsNorm(out: TensorView, input: TensorView, weight: TensorView, eps: f32) void {
    const weight_is_supported = weight.dtype == .f32 or weight.dtype == .f16 or weight.dtype == .bf16;
    if (input.dtype == .f32 and out.dtype == .f32 and input.isContiguous() and out.isContiguous() and weight.isContiguous() and weight_is_supported) {
        const hidden_size = input.shape[input.ndim - 1];
        const num_tokens = input.numel / hidden_size;
        const weight_f32 = if (weight.dtype == .f32) weight.asSlice(f32) else null;
        const weight_u16 = if (weight.dtype == .f16 or weight.dtype == .bf16) weight.asSlice(u16) else null;
        math.rmsnormContiguous(
            out.asSlice(f32),
            input.asSlice(f32),
            weight_f32,
            weight_u16,
            viewDTypeToTensor(weight.dtype),
            num_tokens,
            hidden_size,
            eps,
            0.0,
        );
        return;
    }

    switch (input.dtype) {
        .f32 => rmsNormTyped(f32, f32Identity, f32Identity, out, input, weight, eps),
        .f16 => rmsNormTyped(u16, fp16ToF32, f32ToFp16, out, input, weight, eps),
        .bf16 => rmsNormTyped(u16, bf16ToF32, f32ToBf16, out, input, weight, eps),
        else => unreachable,
    }
}

fn f32Identity(x: f32) f32 {
    return x;
}

fn rmsNormTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    input: TensorView,
    weight: TensorView,
    eps: f32,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
    const w_data = @as([*]const T, @ptrCast(@alignCast(weight.data)));

    std.debug.assert(input.ndim >= 1);
    const hidden_size = input.shape[input.ndim - 1];
    const num_tokens = input.numel / hidden_size;

    if (input.isContiguous() and out.isContiguous() and weight.isContiguous()) {
        // Fast path: all contiguous
        for (0..num_tokens) |t| {
            const offset = t * hidden_size;

            // Compute sum of squares
            var sum_sq: f32 = 0;
            for (0..hidden_size) |i| {
                const val = toF32(in_data[offset + i]);
                sum_sq += val * val;
            }

            // Compute inverse RMS
            const inv_rms = 1.0 / @sqrt(sum_sq / @as(f32, @floatFromInt(hidden_size)) + eps);

            // Apply normalization with weight
            for (0..hidden_size) |i| {
                const val = toF32(in_data[offset + i]);
                const w = toF32(w_data[i]);
                out_data[offset + i] = fromF32(val * inv_rms * w);
            }
        }
    } else {
        // Slow path: strided tensors
        var coords: [MAX_NDIM]usize = [_]usize{0} ** MAX_NDIM;

        for (0..num_tokens) |t| {
            // Compute outer coordinates (all dims except last)
            var remaining = t;
            var divisor: usize = num_tokens;
            for (0..input.ndim - 1) |d| {
                divisor /= input.shape[d];
                coords[d] = remaining / divisor;
                remaining %= divisor;
            }

            // Compute sum of squares along last dim
            var sum_sq: f32 = 0;
            for (0..hidden_size) |i| {
                coords[input.ndim - 1] = i;
                const in_offset = input.coordsToOffset(coords[0..input.ndim]);
                const val = toF32(in_data[in_offset]);
                sum_sq += val * val;
            }

            const inv_rms = 1.0 / @sqrt(sum_sq / @as(f32, @floatFromInt(hidden_size)) + eps);

            // Apply normalization
            for (0..hidden_size) |i| {
                coords[input.ndim - 1] = i;
                const in_offset = input.coordsToOffset(coords[0..input.ndim]);
                const out_offset = out.coordsToOffset(coords[0..out.ndim]);
                const w_coords = [_]usize{i};
                const w_offset = weight.coordsToOffset(w_coords[0..1]);

                const val = toF32(in_data[in_offset]);
                const w = toF32(w_data[w_offset]);
                out_data[out_offset] = fromF32(val * inv_rms * w);
            }
        }
    }
}

/// Layer Normalization: out = (x - mean) / sqrt(var + eps) * weight + bias
pub fn layerNorm(out: TensorView, input: TensorView, weight: TensorView, bias: ?TensorView, eps: f32) void {
    const bias_dtype_ok = if (bias) |b| b.dtype == .f32 else true;
    if (input.dtype == .f32 and out.dtype == .f32 and weight.dtype == .f32 and bias_dtype_ok and
        input.isContiguous() and out.isContiguous() and weight.isContiguous() and (bias == null or bias.?.isContiguous()))
    {
        const hidden_size = input.shape[input.ndim - 1];
        const num_tokens = input.numel / hidden_size;
        const bias_slice = if (bias) |b| b.asSlice(f32) else null;
        math.layerNormContiguous(out.asSlice(f32), input.asSlice(f32), weight.asSlice(f32), bias_slice, num_tokens, hidden_size, eps);
        return;
    }

    switch (input.dtype) {
        .f32 => layerNormTyped(f32, f32Identity, f32Identity, out, input, weight, bias, eps),
        .f16 => layerNormTyped(u16, fp16ToF32, f32ToFp16, out, input, weight, bias, eps),
        .bf16 => layerNormTyped(u16, bf16ToF32, f32ToBf16, out, input, weight, bias, eps),
        else => unreachable,
    }
}

fn layerNormTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    input: TensorView,
    weight: TensorView,
    bias: ?TensorView,
    eps: f32,
) void {
    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const in_data = @as([*]const T, @ptrCast(@alignCast(input.data)));
    const w_data = @as([*]const T, @ptrCast(@alignCast(weight.data)));
    const b_data: ?[*]const T = if (bias) |b| @as([*]const T, @ptrCast(@alignCast(b.data))) else null;

    std.debug.assert(input.ndim >= 1);
    const hidden_size = input.shape[input.ndim - 1];
    const num_tokens = input.numel / hidden_size;
    const hidden_f32 = @as(f32, @floatFromInt(hidden_size));

    if (input.isContiguous() and out.isContiguous() and weight.isContiguous()) {
        // Fast path: all contiguous
        for (0..num_tokens) |t| {
            const offset = t * hidden_size;

            // Compute mean
            var sum: f32 = 0;
            for (0..hidden_size) |i| {
                sum += toF32(in_data[offset + i]);
            }
            const mean = sum / hidden_f32;

            // Compute variance
            var var_sum: f32 = 0;
            for (0..hidden_size) |i| {
                const diff = toF32(in_data[offset + i]) - mean;
                var_sum += diff * diff;
            }
            const inv_std = 1.0 / @sqrt(var_sum / hidden_f32 + eps);

            // Apply normalization with weight and bias
            for (0..hidden_size) |i| {
                const val = (toF32(in_data[offset + i]) - mean) * inv_std;
                const w = toF32(w_data[i]);
                const b = if (b_data) |bd| toF32(bd[i]) else 0.0;
                out_data[offset + i] = fromF32(val * w + b);
            }
        }
    } else {
        // Slow path: strided tensors
        var coords: [MAX_NDIM]usize = [_]usize{0} ** MAX_NDIM;

        for (0..num_tokens) |t| {
            // Compute outer coordinates
            var remaining = t;
            var divisor: usize = num_tokens;
            for (0..input.ndim - 1) |d| {
                divisor /= input.shape[d];
                coords[d] = remaining / divisor;
                remaining %= divisor;
            }

            // Compute mean
            var sum: f32 = 0;
            for (0..hidden_size) |i| {
                coords[input.ndim - 1] = i;
                const in_offset = input.coordsToOffset(coords[0..input.ndim]);
                sum += toF32(in_data[in_offset]);
            }
            const mean = sum / hidden_f32;

            // Compute variance
            var var_sum: f32 = 0;
            for (0..hidden_size) |i| {
                coords[input.ndim - 1] = i;
                const in_offset = input.coordsToOffset(coords[0..input.ndim]);
                const diff = toF32(in_data[in_offset]) - mean;
                var_sum += diff * diff;
            }
            const inv_std = 1.0 / @sqrt(var_sum / hidden_f32 + eps);

            // Apply normalization
            for (0..hidden_size) |i| {
                coords[input.ndim - 1] = i;
                const in_offset = input.coordsToOffset(coords[0..input.ndim]);
                const out_offset = out.coordsToOffset(coords[0..out.ndim]);
                const w_coords = [_]usize{i};
                const w_offset = weight.coordsToOffset(w_coords[0..1]);

                const val = (toF32(in_data[in_offset]) - mean) * inv_std;
                const w = toF32(w_data[w_offset]);
                const b = if (b_data) |bd| blk: {
                    const b_offset = if (bias) |bv| bv.coordsToOffset(w_coords[0..1]) else 0;
                    break :blk toF32(bd[b_offset]);
                } else 0.0;
                out_data[out_offset] = fromF32(val * w + b);
            }
        }
    }
}

test "rmsNorm simple" {
    var in_data = [_]f32{ 1, 2, 3, 4 };
    var out_data = [_]f32{ 0, 0, 0, 0 };
    var w_data = [_]f32{ 1, 1, 1, 1 };

    const input = TensorView.initContiguous(@ptrCast(&in_data), &.{ 1, 4 }, .f32);
    const out = TensorView.initContiguous(@ptrCast(&out_data), &.{ 1, 4 }, .f32);
    const weight = TensorView.initContiguous(@ptrCast(&w_data), &.{4}, .f32);

    rmsNorm(out, input, weight, 1e-6);

    // Verify output is normalized
    var sum_sq: f32 = 0;
    for (out_data) |v| sum_sq += v * v;
    const rms = @sqrt(sum_sq / 4.0);

    // RMS of normalized output should be close to 1 (within tolerance)
    try std.testing.expectApproxEqAbs(@as(f32, 1.0), rms, 0.01);
}

test "layerNorm simple" {
    var in_data = [_]f32{ 1, 2, 3, 4 };
    var out_data = [_]f32{ 0, 0, 0, 0 };
    var w_data = [_]f32{ 1, 1, 1, 1 };
    var b_data = [_]f32{ 0, 0, 0, 0 };

    const input = TensorView.initContiguous(@ptrCast(&in_data), &.{ 1, 4 }, .f32);
    const out = TensorView.initContiguous(@ptrCast(&out_data), &.{ 1, 4 }, .f32);
    const weight = TensorView.initContiguous(@ptrCast(&w_data), &.{4}, .f32);
    const bias = TensorView.initContiguous(@ptrCast(&b_data), &.{4}, .f32);

    layerNorm(out, input, weight, bias, 1e-6);

    // Verify mean is ~0 and std is ~1
    var sum: f32 = 0;
    for (out_data) |v| sum += v;
    const mean = sum / 4.0;

    var var_sum: f32 = 0;
    for (out_data) |v| {
        const diff = v - mean;
        var_sum += diff * diff;
    }
    const std_val = @sqrt(var_sum / 4.0);

    try std.testing.expectApproxEqAbs(@as(f32, 0.0), mean, 0.01);
    try std.testing.expectApproxEqAbs(@as(f32, 1.0), std_val, 0.01);
}
