const std = @import("std");
const tensor = @import("../../tensor.zig");
const dtype_mod = @import("../../dtype.zig");
pub const simd = @import("../simd/root.zig");

// Use comptime-detected SIMD width for all vector operations
const VEC_LEN = simd.f32_vec_len;
const F32Vec = simd.F32Vec;
const fp16ToF32 = dtype_mod.fp16ToF32;

/// Comptime-derived math constants for exp approximation.
/// Using std.math ensures full precision and documents the derivation.
const exp_constants = struct {
    /// log2(e) = 1/ln(2)
    const log2e: f32 = 1.0 / std.math.ln2;
    /// ln(2) split into high and low parts for range reduction accuracy
    const ln2_hi: f32 = 0.693359375; // Exact in float
    const ln2_lo: f32 = -2.12194440e-4; // Correction term
    /// Overflow/underflow bounds: exp(88.72) ≈ FLT_MAX
    const exp_hi: f32 = 88.3762626647949;
    const exp_lo: f32 = -88.3762626647949;
    /// Polynomial coefficients for 2^x approximation on [-0.5, 0.5]
    /// These are minimax coefficients, not easily derived from std.math
    const p0: f32 = 1.9875691500e-4;
    const p1: f32 = 1.3981999507e-3;
    const p2: f32 = 8.3334519073e-3;
    const p3: f32 = 4.1665795894e-2;
    const p4: f32 = 1.6666665459e-1;
    const p5: f32 = 5.0000001201e-1;
};

/// Fast vectorized exp approximation using Schraudolph's method.
/// Accurate to ~1% for |x| < 10, good enough for neural networks (softmax, sigmoid).
/// Based on: exp(x) ≈ 2^(x/ln2) with polynomial approximation for fractional part.
/// Uses comptime-detected SIMD width for optimal performance on any architecture.
pub inline fn fastExp(x: F32Vec) F32Vec {
    const c = exp_constants;
    const I32Vec = @Vector(VEC_LEN, i32);

    // Clamp x to avoid overflow/underflow
    var xc = @max(@min(x, @as(F32Vec, @splat(c.exp_hi))), @as(F32Vec, @splat(c.exp_lo)));

    // Compute fx = floor(x * log2e + 0.5)
    const fx = @floor(xc * @as(F32Vec, @splat(c.log2e)) + @as(F32Vec, @splat(0.5)));
    const fxi: I32Vec = @intFromFloat(fx);

    // x = x - fx * ln2 (range reduction using hi/lo split)
    xc = xc - fx * @as(F32Vec, @splat(c.ln2_hi));
    xc = xc - fx * @as(F32Vec, @splat(c.ln2_lo));

    // Polynomial approximation of 2^frac using Horner's method
    var y: F32Vec = @splat(c.p0);
    y = y * xc + @as(F32Vec, @splat(c.p1));
    y = y * xc + @as(F32Vec, @splat(c.p2));
    y = y * xc + @as(F32Vec, @splat(c.p3));
    y = y * xc + @as(F32Vec, @splat(c.p4));
    y = y * xc + @as(F32Vec, @splat(c.p5));
    y = y * xc * xc + xc + @as(F32Vec, @splat(1.0));

    // Build 2^n by manipulating float exponent bits
    const emm0 = (fxi + @as(I32Vec, @splat(127))) << @as(@Vector(VEC_LEN, u5), @splat(23));
    const pow2n: F32Vec = @bitCast(emm0);

    return y * pow2n;
}

/// Scalar fast exp for remainder elements
pub inline fn fastExpScalar(x: f32) f32 {
    const c = exp_constants;

    var xc = @max(@min(x, c.exp_hi), c.exp_lo);
    const fx = @floor(xc * c.log2e + 0.5);
    const fxi: i32 = @intFromFloat(fx);
    xc = xc - fx * c.ln2_hi - fx * c.ln2_lo;

    var y = c.p0;
    y = y * xc + c.p1;
    y = y * xc + c.p2;
    y = y * xc + c.p3;
    y = y * xc + c.p4;
    y = y * xc + c.p5;
    y = y * xc * xc + xc + 1.0;

    const emm0: u32 = @bitCast((fxi + 127) << 23);
    const pow2n: f32 = @bitCast(emm0);
    return y * pow2n;
}

pub fn ropeFillCosSinCombinedStrided(
    data: [*]f32,
    stride0: usize,
    stride1: usize,
    seq_len: usize,
    dim: usize,
    theta: f32,
    offset: usize,
) void {
    const half_dim = dim / 2;
    for (0..seq_len) |pos| {
        const actual_pos = pos + offset;
        for (0..half_dim) |i| {
            const freq = 1.0 / std.math.pow(f32, theta, @as(f32, @floatFromInt(2 * i)) / @as(f32, @floatFromInt(dim)));
            const angle = @as(f32, @floatFromInt(actual_pos)) * freq;
            const base = pos * stride0;
            data[base + i * stride1] = @cos(angle);
            data[base + (i + half_dim) * stride1] = @sin(angle);
        }
    }
}

pub fn ropeFillCosSinFromInvFreq(
    cos: []f32,
    sin: []f32,
    inv_freq: []const f32,
    dim: usize,
    pos_start: usize,
    count: usize,
) void {
    const half_dim = dim / 2;
    for (0..count) |p| {
        const pos = pos_start + p;
        const base = p * dim;
        for (0..half_dim) |i| {
            const angle = @as(f32, @floatFromInt(pos)) * inv_freq[i];
            const c = @cos(angle);
            const s = @sin(angle);
            cos[base + i] = c;
            cos[base + i + half_dim] = c;
            sin[base + i] = s;
            sin[base + i + half_dim] = s;
        }
    }
}

pub fn siluContiguous(out: []f32, input: []const f32) void {
    @setFloatMode(.optimized);
    std.debug.assert(out.len == input.len);

    const one: F32Vec = @splat(1.0);
    var i: usize = 0;
    while (i + VEC_LEN - 1 < input.len) : (i += VEC_LEN) {
        const v: F32Vec = input[i..][0..VEC_LEN].*;
        const exp_neg = fastExp(-v);
        const sig = one / (one + exp_neg);
        out[i..][0..VEC_LEN].* = v * sig;
    }
    while (i < input.len) : (i += 1) {
        const v = input[i];
        const sig = 1.0 / (1.0 + fastExpScalar(-v));
        out[i] = v * sig;
    }
}

pub fn geluContiguous(out: []f32, input: []const f32) void {
    @setFloatMode(.optimized);
    std.debug.assert(out.len == input.len);

    const sqrt_2_over_pi: f32 = 0.7978845608028654;
    const coeff: f32 = 0.044715;

    for (input, 0..) |x, i| {
        const x3 = x * x * x;
        const inner = sqrt_2_over_pi * (x + coeff * x3);
        const tanh_val = std.math.tanh(inner);
        out[i] = 0.5 * x * (1.0 + tanh_val);
    }
}

pub fn reluContiguous(out: []f32, input: []const f32) void {
    std.debug.assert(out.len == input.len);
    for (input, 0..) |x, i| {
        out[i] = @max(0, x);
    }
}

pub fn sigmoidContiguous(out: []f32, input: []const f32) void {
    @setFloatMode(.optimized);
    std.debug.assert(out.len == input.len);

    const one: F32Vec = @splat(1.0);
    var i: usize = 0;
    while (i + VEC_LEN - 1 < input.len) : (i += VEC_LEN) {
        const v: F32Vec = input[i..][0..VEC_LEN].*;
        const exp_neg = fastExp(-v);
        out[i..][0..VEC_LEN].* = one / (one + exp_neg);
    }
    while (i < input.len) : (i += 1) {
        const v = input[i];
        out[i] = 1.0 / (1.0 + fastExpScalar(-v));
    }
}

pub fn tanhContiguous(out: []f32, input: []const f32) void {
    std.debug.assert(out.len == input.len);
    for (input, 0..) |x, i| {
        out[i] = std.math.tanh(x);
    }
}

pub fn softmaxContiguous(out: []f32, input: []const f32, rows: usize, cols: usize) void {
    @setFloatMode(.optimized);
    std.debug.assert(input.len == rows * cols);
    std.debug.assert(out.len == input.len);

    var r: usize = 0;
    while (r < rows) : (r += 1) {
        const in_row = input[r * cols ..][0..cols];
        const out_row = out[r * cols ..][0..cols];

        var max_vec: F32Vec = @splat(-std.math.inf(f32));
        var c: usize = 0;
        while (c + VEC_LEN - 1 < cols) : (c += VEC_LEN) {
            const v: F32Vec = in_row[c..][0..VEC_LEN].*;
            max_vec = @max(max_vec, v);
        }
        var maxv = @reduce(.Max, max_vec);
        while (c < cols) : (c += 1) {
            maxv = @max(maxv, in_row[c]);
        }

        const maxv_vec: F32Vec = @splat(maxv);
        var sum_vec: F32Vec = @splat(0);
        c = 0;
        while (c + VEC_LEN - 1 < cols) : (c += VEC_LEN) {
            const v: F32Vec = in_row[c..][0..VEC_LEN].*;
            const shifted = v - maxv_vec;
            const e = fastExp(shifted);
            out_row[c..][0..VEC_LEN].* = e;
            sum_vec += e;
        }
        var sum = @reduce(.Add, sum_vec);
        while (c < cols) : (c += 1) {
            const e = fastExpScalar(in_row[c] - maxv);
            out_row[c] = e;
            sum += e;
        }

        const inv_sum = 1.0 / sum;
        const inv_sum_vec: F32Vec = @splat(inv_sum);
        c = 0;
        while (c + VEC_LEN - 1 < cols) : (c += VEC_LEN) {
            const v: F32Vec = out_row[c..][0..VEC_LEN].*;
            out_row[c..][0..VEC_LEN].* = v * inv_sum_vec;
        }
        while (c < cols) : (c += 1) {
            out_row[c] *= inv_sum;
        }
    }
}

pub fn softmaxMaskedInPlaceWithMax(
    scores: []f32,
    active_start: usize,
    active_end: usize,
    sink_logit: ?f32,
    exact: bool,
    maxv: f32,
    mask_cutoff: ?f32,
) void {
    @setFloatMode(.optimized);
    std.debug.assert(active_start <= active_end and active_end <= scores.len);
    std.debug.assert(active_start < active_end);

    const cutoff = mask_cutoff;
    var sum: f32 = 0;
    if (exact) {
        if (sink_logit) |sl| {
            sum += @exp(sl - maxv);
        }
        for (0..active_start) |i| scores[i] = 0;
        for (active_start..active_end) |i| {
            const s = scores[i];
            if (cutoff != null and s <= cutoff.?) {
                scores[i] = 0;
                continue;
            }
            const e = @exp(s - maxv);
            scores[i] = e;
            sum += e;
        }
        for (active_end..scores.len) |i| scores[i] = 0;
    } else {
        const maxv_vec: F32Vec = @splat(maxv);
        var sum_vec: F32Vec = @splat(0);
        const sink_e: f32 = if (sink_logit) |sl| fastExpScalar(sl - maxv) else 0;
        for (0..active_start) |i| scores[i] = 0;

        var i: usize = active_start;
        if (cutoff == null) {
            while (i + VEC_LEN - 1 < active_end) : (i += VEC_LEN) {
                const v: F32Vec = scores[i..][0..VEC_LEN].*;
                const shifted = v - maxv_vec;
                const e = fastExp(shifted);
                scores[i..][0..VEC_LEN].* = e;
                sum_vec += e;
            }
        }
        sum = sink_e + @reduce(.Add, sum_vec);
        while (i < active_end) : (i += 1) {
            const s = scores[i];
            if (cutoff != null and s <= cutoff.?) {
                scores[i] = 0;
                continue;
            }
            const e = fastExpScalar(s - maxv);
            scores[i] = e;
            sum += e;
        }
        for (active_end..scores.len) |j| scores[j] = 0;
    }

    if (sum == 0) {
        @memset(scores, 0);
        return;
    }

    const inv_sum = 1.0 / sum;
    const inv_sum_vec: F32Vec = @splat(inv_sum);
    var i: usize = 0;
    while (i + VEC_LEN - 1 < scores.len) : (i += VEC_LEN) {
        const v: F32Vec = scores[i..][0..VEC_LEN].*;
        scores[i..][0..VEC_LEN].* = v * inv_sum_vec;
    }
    while (i < scores.len) : (i += 1) {
        scores[i] *= inv_sum;
    }
}

pub fn rmsnormContiguous(
    out: []f32,
    input: []const f32,
    weight_f32: ?[]const f32,
    weight_u16: ?[]const u16,
    weight_dtype: tensor.DType,
    num_tokens: usize,
    dim: usize,
    eps: f32,
    weight_offset: f32,
) void {
    @setFloatMode(.optimized);
    std.debug.assert(input.len == num_tokens * dim);
    std.debug.assert(out.len == input.len);

    const w_f32 = weight_f32 orelse &[_]f32{};
    const w_u16 = weight_u16 orelse &[_]u16{};
    std.debug.assert(weight_dtype == .f32 or weight_dtype == .f16 or weight_dtype == .bf16);
    if (weight_dtype == .f32) {
        std.debug.assert(weight_f32 != null);
    } else {
        std.debug.assert(weight_u16 != null);
    }

    const UNROLL = 4;
    const UNROLL_STRIDE = UNROLL * VEC_LEN;
    const has_offset = weight_offset != 0.0;
    const offset_vec: F32Vec = @splat(weight_offset);

    var t: usize = 0;
    while (t < num_tokens) : (t += 1) {
        const offset = t * dim;
        const x_row = input[offset..][0..dim];
        const out_row = out[offset..][0..dim];

        var sum_vecs: [UNROLL]F32Vec = .{@as(F32Vec, @splat(0))} ** UNROLL;
        var i: usize = 0;
        while (i + UNROLL_STRIDE - 1 < dim) : (i += UNROLL_STRIDE) {
            inline for (0..UNROLL) |k| {
                const v: F32Vec = x_row[i + k * VEC_LEN ..][0..VEC_LEN].*;
                sum_vecs[k] = @mulAdd(F32Vec, v, v, sum_vecs[k]);
            }
        }
        var sum_vec = sum_vecs[0] + sum_vecs[1] + sum_vecs[2] + sum_vecs[3];
        while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
            const v: F32Vec = x_row[i..][0..VEC_LEN].*;
            sum_vec = @mulAdd(F32Vec, v, v, sum_vec);
        }
        var sum = @reduce(.Add, sum_vec);
        while (i < dim) : (i += 1) {
            sum += x_row[i] * x_row[i];
        }

        const inv_rms = 1.0 / std.math.sqrt(sum / @as(f32, @floatFromInt(dim)) + eps);
        const inv_rms_vec: F32Vec = @splat(inv_rms);

        i = 0;
        switch (weight_dtype) {
            .f32 => {
                while (i + UNROLL_STRIDE - 1 < dim) : (i += UNROLL_STRIDE) {
                    inline for (0..UNROLL) |k| {
                        const off = i + k * VEC_LEN;
                        const v: F32Vec = x_row[off..][0..VEC_LEN].*;
                        var wv: F32Vec = w_f32[off..][0..VEC_LEN].*;
                        if (has_offset) wv += offset_vec;
                        out_row[off..][0..VEC_LEN].* = v * inv_rms_vec * wv;
                    }
                }
                while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
                    const v: F32Vec = x_row[i..][0..VEC_LEN].*;
                    var wv: F32Vec = w_f32[i..][0..VEC_LEN].*;
                    if (has_offset) wv += offset_vec;
                    out_row[i..][0..VEC_LEN].* = v * inv_rms_vec * wv;
                }
                while (i < dim) : (i += 1) {
                    var w = w_f32[i];
                    if (has_offset) w += weight_offset;
                    out_row[i] = x_row[i] * inv_rms * w;
                }
            },
            .bf16 => {
                while (i + UNROLL_STRIDE - 1 < dim) : (i += UNROLL_STRIDE) {
                    inline for (0..UNROLL) |k| {
                        const off = i + k * VEC_LEN;
                        const v: F32Vec = x_row[off..][0..VEC_LEN].*;
                        const w_raw: @Vector(VEC_LEN, u16) = w_u16[off..][0..VEC_LEN].*;
                        var wv: F32Vec = @bitCast(@as(@Vector(VEC_LEN, u32), w_raw) << @as(@Vector(VEC_LEN, u5), @splat(16)));
                        if (has_offset) wv += offset_vec;
                        out_row[off..][0..VEC_LEN].* = v * inv_rms_vec * wv;
                    }
                }
                while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
                    const v: F32Vec = x_row[i..][0..VEC_LEN].*;
                    const w_raw: @Vector(VEC_LEN, u16) = w_u16[i..][0..VEC_LEN].*;
                    var wv: F32Vec = @bitCast(@as(@Vector(VEC_LEN, u32), w_raw) << @as(@Vector(VEC_LEN, u5), @splat(16)));
                    if (has_offset) wv += offset_vec;
                    out_row[i..][0..VEC_LEN].* = v * inv_rms_vec * wv;
                }
                while (i < dim) : (i += 1) {
                    const w_bits: u32 = @as(u32, w_u16[i]) << 16;
                    var wf: f32 = @bitCast(w_bits);
                    if (has_offset) wf += weight_offset;
                    out_row[i] = x_row[i] * inv_rms * wf;
                }
            },
            .f16 => {
                while (i + UNROLL_STRIDE - 1 < dim) : (i += UNROLL_STRIDE) {
                    inline for (0..UNROLL) |k| {
                        const off = i + k * VEC_LEN;
                        const v: F32Vec = x_row[off..][0..VEC_LEN].*;
                        var wv: F32Vec = undefined;
                        inline for (0..VEC_LEN) |e| wv[e] = fp16ToF32(w_u16[off + e]);
                        if (has_offset) wv += offset_vec;
                        out_row[off..][0..VEC_LEN].* = v * inv_rms_vec * wv;
                    }
                }
                while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
                    const v: F32Vec = x_row[i..][0..VEC_LEN].*;
                    var wv: F32Vec = undefined;
                    inline for (0..VEC_LEN) |e| wv[e] = fp16ToF32(w_u16[i + e]);
                    if (has_offset) wv += offset_vec;
                    out_row[i..][0..VEC_LEN].* = v * inv_rms_vec * wv;
                }
                while (i < dim) : (i += 1) {
                    var w = fp16ToF32(w_u16[i]);
                    if (has_offset) w += weight_offset;
                    out_row[i] = x_row[i] * inv_rms * w;
                }
            },
            else => unreachable,
        }
    }
}

pub fn layerNormContiguous(
    out: []f32,
    input: []const f32,
    weight: []const f32,
    bias: ?[]const f32,
    num_tokens: usize,
    dim: usize,
    eps: f32,
) void {
    @setFloatMode(.optimized);
    std.debug.assert(input.len == num_tokens * dim);
    std.debug.assert(out.len == input.len);
    std.debug.assert(weight.len >= dim);
    if (bias) |b| std.debug.assert(b.len >= dim);

    const dim_f: f32 = @floatFromInt(dim);

    var t: usize = 0;
    while (t < num_tokens) : (t += 1) {
        const offset = t * dim;
        const row = input[offset..][0..dim];
        const out_row = out[offset..][0..dim];

        var sum_vec: F32Vec = @splat(0);
        var sumsq_vec: F32Vec = @splat(0);
        var i: usize = 0;
        while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
            const v: F32Vec = row[i..][0..VEC_LEN].*;
            sum_vec += v;
            sumsq_vec = @mulAdd(F32Vec, v, v, sumsq_vec);
        }
        var sum = @reduce(.Add, sum_vec);
        var sumsq = @reduce(.Add, sumsq_vec);
        while (i < dim) : (i += 1) {
            const v = row[i];
            sum += v;
            sumsq += v * v;
        }

        const mean = sum / dim_f;
        const variance = @max(sumsq / dim_f - mean * mean, 0);
        const inv_std = 1.0 / @sqrt(variance + eps);
        const mean_vec: F32Vec = @splat(mean);
        const inv_std_vec: F32Vec = @splat(inv_std);

        i = 0;
        if (bias) |b| {
            while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
                const v: F32Vec = row[i..][0..VEC_LEN].*;
                const w: F32Vec = weight[i..][0..VEC_LEN].*;
                const bb: F32Vec = b[i..][0..VEC_LEN].*;
                out_row[i..][0..VEC_LEN].* = (v - mean_vec) * inv_std_vec * w + bb;
            }
            while (i < dim) : (i += 1) {
                out_row[i] = (row[i] - mean) * inv_std * weight[i] + b[i];
            }
        } else {
            while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
                const v: F32Vec = row[i..][0..VEC_LEN].*;
                const w: F32Vec = weight[i..][0..VEC_LEN].*;
                out_row[i..][0..VEC_LEN].* = (v - mean_vec) * inv_std_vec * w;
            }
            while (i < dim) : (i += 1) {
                out_row[i] = (row[i] - mean) * inv_std * weight[i];
            }
        }
    }
}

pub fn rmsnormInPlaceWeightTensor(vec: []f32, weight_tensor: *const tensor.Tensor, eps: f32, weight_offset: f32) void {
    const len = vec.len;
    const w_dtype = weight_tensor.dtype;
    const has_offset = weight_offset != 0.0;

    var sum_sq: f32 = 0;
    for (vec) |v| sum_sq += v * v;
    const inv_rms = 1.0 / @sqrt(sum_sq / @as(f32, @floatFromInt(len)) + eps);

    if (w_dtype == .bf16) {
        const w_u16 = weight_tensor.asSliceUnaligned(u16);
        for (0..len) |i| {
            var w = dtype_mod.bf16ToF32(w_u16[i]);
            if (has_offset) w += weight_offset;
            vec[i] = vec[i] * inv_rms * w;
        }
    } else if (w_dtype == .f16) {
        const w_u16 = weight_tensor.asSliceUnaligned(u16);
        for (0..len) |i| {
            var w = dtype_mod.fp16ToF32(w_u16[i]);
            if (has_offset) w += weight_offset;
            vec[i] = vec[i] * inv_rms * w;
        }
    } else {
        const w_f32 = weight_tensor.asSliceUnaligned(f32);
        for (0..len) |i| {
            const w = if (has_offset) weight_offset + w_f32[i] else w_f32[i];
            vec[i] = vec[i] * inv_rms * w;
        }
    }
}

pub const RoPE = struct {
    dim: usize,
    max_seq_len: usize,
    theta: f32,
    /// Precomputed inverse frequencies (dim/2 values)
    inv_freq: []f32,
    /// Cached cos/sin values (computed lazily up to cached_len)
    freqs_cos: []f32,
    freqs_sin: []f32,
    cached_len: usize,
    allocator: std.mem.Allocator,

    /// `inv_freq_scale` lets callers implement simple RoPE scaling variants by scaling the inverse
    /// frequencies (e.g. linear RoPE scaling uses `inv_freq_scale = 1 / factor`).
    pub fn init(allocator: std.mem.Allocator, dim: usize, max_seq_len: usize, theta: f32, inv_freq_scale: f32) !RoPE {
        // Precompute inverse frequencies (only dim/2 values)
        const half_dim = dim / 2;
        var inv_freq = try allocator.alloc(f32, half_dim);
        errdefer allocator.free(inv_freq);

        for (0..half_dim) |i| {
            const exponent = @as(f64, @floatFromInt(2 * i)) / @as(f64, @floatFromInt(dim));
            inv_freq[i] = @floatCast((1.0 / std.math.pow(f64, @as(f64, theta), exponent)) * @as(f64, inv_freq_scale));
        }

        // Start with small cache (256 positions typical for short prompts)
        const initial_cache = @min(256, max_seq_len);
        const cos = try allocator.alloc(f32, initial_cache * dim);
        errdefer allocator.free(cos);
        const sin = try allocator.alloc(f32, initial_cache * dim);
        errdefer allocator.free(sin);

        ropeFillCosSinFromInvFreq(cos, sin, inv_freq, dim, 0, initial_cache);

        return RoPE{
            .dim = dim,
            .max_seq_len = max_seq_len,
            .theta = theta,
            .inv_freq = inv_freq,
            .freqs_cos = cos,
            .freqs_sin = sin,
            .cached_len = initial_cache,
            .allocator = allocator,
        };
    }

    pub fn initWithRopeScaling(
        allocator: std.mem.Allocator,
        dim: usize,
        max_seq_len: usize,
        theta: f32,
        rope_scaling: tensor.RopeScaling,
    ) !RoPE {
        const inv_freq_scale: f32 = if (rope_scaling.rope_type == .linear and rope_scaling.factor > 0)
            1.0 / rope_scaling.factor
        else
            1.0;

        if (rope_scaling.rope_type != .llama3) {
            return RoPE.init(allocator, dim, max_seq_len, theta, inv_freq_scale);
        }

        // Llama3-style RoPE uses wavelength-dependent frequency scaling.
        // We implement the same formula as mlx_lm by modifying the *denominator* `freq = theta^(2i/dim)`
        // and then storing `inv_freq = 1 / freq`.
        const half_dim = dim / 2;
        var inv_freq = try allocator.alloc(f32, half_dim);
        errdefer allocator.free(inv_freq);

        const factor = rope_scaling.factor;
        const low_freq_factor = rope_scaling.low_freq_factor;
        const high_freq_factor = rope_scaling.high_freq_factor;
        const old_ctx: f32 = @floatFromInt(rope_scaling.original_max_position_embeddings);

        const low_freq_wavelen = old_ctx / low_freq_factor;
        const high_freq_wavelen = old_ctx / high_freq_factor;
        const dims_f: f32 = @floatFromInt(dim);

        const denom = high_freq_factor - low_freq_factor;
        const inv_denom: f32 = if (denom != 0) 1.0 / denom else 0;

        for (0..half_dim) |i| {
            const idx: f32 = @floatFromInt(i * 2);
            const exponent = idx / dims_f;
            const freq = std.math.pow(f32, theta, exponent);
            const wavelen = 2.0 * std.math.pi * freq;

            const freq_scaled: f32 = if (factor > 0 and wavelen > low_freq_wavelen) blk: {
                break :blk freq * factor;
            } else if (wavelen < high_freq_wavelen or factor <= 0 or inv_denom == 0) blk: {
                break :blk freq;
            } else blk: {
                // Medium wavelengths: smooth interpolation.
                // smooth_factor = (old_ctx / wavelen - low_freq_factor) / (high_freq_factor - low_freq_factor)
                const smooth_factor = (old_ctx / wavelen - low_freq_factor) * inv_denom;
                const t = @min(@max(smooth_factor, 0.0), 1.0);
                // freq / ((1 - t)/factor + t)
                break :blk freq / (((1.0 - t) / factor) + t);
            };

            inv_freq[i] = 1.0 / freq_scaled;
        }

        // Start with small cache (256 positions typical for short prompts)
        const initial_cache = @min(256, max_seq_len);
        const cos = try allocator.alloc(f32, initial_cache * dim);
        errdefer allocator.free(cos);
        const sin = try allocator.alloc(f32, initial_cache * dim);
        errdefer allocator.free(sin);

        ropeFillCosSinFromInvFreq(cos, sin, inv_freq, dim, 0, initial_cache);

        return RoPE{
            .dim = dim,
            .max_seq_len = max_seq_len,
            .theta = theta,
            .inv_freq = inv_freq,
            .freqs_cos = cos,
            .freqs_sin = sin,
            .cached_len = initial_cache,
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *RoPE, allocator: std.mem.Allocator) void {
        allocator.free(self.inv_freq);
        allocator.free(self.freqs_cos);
        allocator.free(self.freqs_sin);
        self.* = undefined;
    }

    /// Ensure cache covers at least `needed` positions.
    /// Grows cache exponentially (power of 2) up to max_seq_len.
    fn ensureCache(self: *RoPE, needed: usize) void {
        if (needed <= self.cached_len) return;

        // Grow cache to power of 2 for efficient reallocation
        var new_len = self.cached_len;
        while (new_len < needed) {
            // Saturating multiply to avoid overflow (though max_seq_len bound should prevent this)
            new_len = if (new_len > std.math.maxInt(usize) / 2) std.math.maxInt(usize) else new_len * 2;
        }
        new_len = @min(new_len, self.max_seq_len);

        // Realloc can fail if system is out of memory - log and continue with existing cache
        // The caller will see stale cache data which is incorrect but won't crash
        const new_cos = self.allocator.realloc(self.freqs_cos, new_len * self.dim) catch {
            std.debug.print("warning: RoPE cache realloc failed for {} positions\n", .{new_len});
            return;
        };
        const new_sin = self.allocator.realloc(self.freqs_sin, new_len * self.dim) catch {
            // Rollback cos realloc (we got new memory but sin failed)
            self.freqs_cos = self.allocator.realloc(new_cos, self.cached_len * self.dim) catch new_cos;
            std.debug.print("warning: RoPE cache realloc failed for {} positions\n", .{new_len});
            return;
        };
        self.freqs_cos = new_cos;
        self.freqs_sin = new_sin;

        const count = new_len - self.cached_len;
        const cos_slice = new_cos[self.cached_len * self.dim .. new_len * self.dim];
        const sin_slice = new_sin[self.cached_len * self.dim .. new_len * self.dim];
        ropeFillCosSinFromInvFreq(cos_slice, sin_slice, self.inv_freq, self.dim, self.cached_len, count);
        self.cached_len = new_len;
    }

    fn applyRotation(vec: []f32, cos: []const f32, sin: []const f32, half: usize) void {
        applyRopeRotationContiguous(vec, cos, sin, half);
    }

    pub fn applyInPlace(self: *RoPE, vec: []f32, pos: usize) void {
        // Ensure cache covers this position
        if (pos >= self.cached_len) self.ensureCache(pos + 1);

        const half = self.dim / 2;
        const base = pos * self.dim;
        const cos = self.freqs_cos[base..];
        const sin = self.freqs_sin[base..];

        applyRotation(vec, cos[0..half], sin[0..half], half);
    }
};

pub fn applyRopeRotationContiguous(vec: []f32, cos: []const f32, sin: []const f32, half: usize) void {
    @setFloatMode(.optimized);
    std.debug.assert(vec.len >= half * 2);
    std.debug.assert(cos.len >= half);
    std.debug.assert(sin.len >= half);

    var i: usize = 0;
    while (i + VEC_LEN - 1 < half) : (i += VEC_LEN) {
        const x1: F32Vec = vec[i..][0..VEC_LEN].*;
        const x2: F32Vec = vec[i + half ..][0..VEC_LEN].*;
        const c: F32Vec = cos[i..][0..VEC_LEN].*;
        const s: F32Vec = sin[i..][0..VEC_LEN].*;
        const r1 = @mulAdd(F32Vec, x1, c, -x2 * s);
        const r2 = @mulAdd(F32Vec, x2, c, x1 * s);
        vec[i..][0..VEC_LEN].* = r1;
        vec[i + half ..][0..VEC_LEN].* = r2;
    }
    while (i < half) : (i += 1) {
        const x1 = vec[i];
        const x2 = vec[i + half];
        const c = cos[i];
        const s = sin[i];
        vec[i] = x1 * c - x2 * s;
        vec[i + half] = x2 * c + x1 * s;
    }
}

pub fn applyRopeRotationStrided(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    data: [*]T,
    data_stride: usize,
    cos: [*]const T,
    cos_stride: usize,
    sin: [*]const T,
    sin_stride: usize,
    half: usize,
) void {
    if (T == f32 and data_stride == 1 and cos_stride == 1 and sin_stride == 1) {
        applyRopeRotationContiguous(data[0 .. half * 2], cos[0..half], sin[0..half], half);
        return;
    }

    for (0..half) |i| {
        const idx0 = i * data_stride;
        const idx1 = (i + half) * data_stride;
        const c = toF32(cos[i * cos_stride]);
        const s = toF32(sin[i * sin_stride]);
        const x0 = toF32(data[idx0]);
        const x1 = toF32(data[idx1]);
        data[idx0] = fromF32(x0 * c - x1 * s);
        data[idx1] = fromF32(x1 * c + x0 * s);
    }
}

test "llama3 rope scaling matches mlx formula" {
    const allocator = std.testing.allocator;

    const dim: usize = 128;
    const theta: f32 = 500_000.0;
    const scaling = tensor.RopeScaling{
        .rope_type = .llama3,
        .factor = 8.0,
        .low_freq_factor = 1.0,
        .high_freq_factor = 4.0,
        .original_max_position_embeddings = 8192,
    };

    var rope_inst = try RoPE.initWithRopeScaling(allocator, dim, 32, theta, scaling);
    defer rope_inst.deinit(allocator);

    // Recompute expected inv_freq in-place (mirrors metal computeLlama3RopeFreqs + inversion).
    const half = dim / 2;
    const old_ctx: f32 = @floatFromInt(scaling.original_max_position_embeddings);
    const low_freq_wavelen = old_ctx / scaling.low_freq_factor;
    const high_freq_wavelen = old_ctx / scaling.high_freq_factor;
    const dims_f: f32 = @floatFromInt(dim);
    const denom = scaling.high_freq_factor - scaling.low_freq_factor;
    const inv_denom: f32 = if (denom != 0) 1.0 / denom else 0;

    var i: usize = 0;
    while (i < half) : (i += 1) {
        const idx: f32 = @floatFromInt(i * 2);
        const freq = std.math.pow(f32, theta, idx / dims_f);
        const wavelen = 2.0 * std.math.pi * freq;
        const freq_scaled: f32 = if (wavelen > low_freq_wavelen) blk: {
            break :blk freq * scaling.factor;
        } else if (wavelen < high_freq_wavelen or inv_denom == 0) blk: {
            break :blk freq;
        } else blk: {
            const smooth_factor = (old_ctx / wavelen - scaling.low_freq_factor) * inv_denom;
            const t = @min(@max(smooth_factor, 0.0), 1.0);
            break :blk freq / (((1.0 - t) / scaling.factor) + t);
        };
        const expected_inv = 1.0 / freq_scaled;
        try std.testing.expectApproxEqRel(expected_inv, rope_inst.inv_freq[i], 1e-5);
    }
}
