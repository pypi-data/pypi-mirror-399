//! Attention operations with stride-aware implementations.
//!
//! Includes RoPE (rotary position embeddings) and SDPA (scaled dot-product attention).

const std = @import("std");
const tv = @import("tensor_view.zig");
const math = @import("math.zig");

const TensorView = tv.TensorView;
const DType = tv.DType;
const MAX_NDIM = tv.MAX_NDIM;

// SIMD and math infrastructure
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

/// Compute RoPE frequencies: 1 / (theta^(2i/d))
pub fn ropeFreqs(out: TensorView, theta: f32, offset: usize) void {
    std.debug.assert(out.dtype == .f32);
    std.debug.assert(out.ndim == 2); // [seq_len, dim]

    const out_data = @as([*]f32, @ptrCast(@alignCast(out.data)));
    const seq_len = out.shape[0];
    const dim = out.shape[1];
    const stride0 = out.strides[0];
    const stride1 = out.strides[1];
    math.ropeFillCosSinCombinedStrided(out_data, stride0, stride1, seq_len, dim, theta, offset);
}

/// Apply RoPE to query and key tensors in-place (PyTorch-compatible).
/// q, k: [batch, heads, seq, head_dim]
/// cos, sin: [batch, seq, head_dim/2] or [1, seq, head_dim/2] (broadcasts over batch/heads)
///           Also supports [seq, head_dim] format (used by C API rope_freqs).
pub fn applyRope(q: TensorView, k: TensorView, cos: TensorView, sin: TensorView) void {
    switch (q.dtype) {
        .f32 => applyRopeTyped(f32, f32Identity, f32Identity, q, k, cos, sin),
        .f16 => applyRopeTyped(u16, fp16ToF32, f32ToFp16, q, k, cos, sin),
        .bf16 => applyRopeTyped(u16, bf16ToF32, f32ToBf16, q, k, cos, sin),
        else => unreachable,
    }
}

fn f32Identity(x: f32) f32 {
    return x;
}

fn applyRopeTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    q: TensorView,
    k: TensorView,
    cos: TensorView,
    sin: TensorView,
) void {
    std.debug.assert(q.ndim == 4); // [batch, heads, seq, head_dim]

    const q_data = @as([*]T, @ptrCast(@alignCast(q.data)));
    const k_data = @as([*]T, @ptrCast(@alignCast(k.data)));

    // cos/sin can be f32, f16, or bf16 - read with same type as q/k
    const cos_data = @as([*]const T, @ptrCast(@alignCast(cos.data)));
    const sin_data = @as([*]const T, @ptrCast(@alignCast(sin.data)));

    const batch = q.shape[0];
    const q_heads = q.shape[1];
    const k_heads = k.shape[1];
    const seq_len = q.shape[2];
    const head_dim = q.shape[3];
    const half_dim = head_dim / 2;

    // Detect cos/sin format based on ndim
    // Runtime format: [batch, seq, half_dim] with ndim=3
    // C API format: [seq, head_dim] with ndim=2
    const is_pytorch_format = cos.ndim == 3;

    // Apply RoPE: x_rotated = x * cos - x_rotated_half * sin
    for (0..batch) |b| {
        for (0..seq_len) |s| {
            // Compute cos/sin offset based on format
            var freq_offset: usize = undefined;
            if (is_pytorch_format) {
                // Runtime: [batch, seq, half_dim] - broadcast batch dim if size 1
                const cos_batch = if (cos.shape[0] == 1) 0 else b;
                freq_offset = cos_batch * @as(usize, @intCast(cos.strides[0])) +
                    s * @as(usize, @intCast(cos.strides[1]));
            } else {
                // C API: [seq, head_dim] - cos in first half, sin in second half
                freq_offset = s * head_dim;
            }

            // Process query heads
            for (0..q_heads) |h| {
                const q_offset = b * q.strides[0] + h * q.strides[1] + s * q.strides[2];
                const q_ptr = q_data + q_offset;
                const q_stride = q.strides[3];
                const cos_ptr = cos_data + freq_offset;
                const sin_ptr = sin_data + freq_offset;
                const cos_stride = if (is_pytorch_format) cos.strides[2] else 1;
                const sin_stride = if (is_pytorch_format) sin.strides[2] else 1;

                math.applyRopeRotationStrided(
                    T,
                    toF32,
                    fromF32,
                    q_ptr,
                    q_stride,
                    cos_ptr,
                    cos_stride,
                    sin_ptr,
                    sin_stride,
                    half_dim,
                );
            }

            // Process key heads
            for (0..k_heads) |h| {
                const k_offset = b * k.strides[0] + h * k.strides[1] + s * k.strides[2];
                const k_ptr = k_data + k_offset;
                const k_stride = k.strides[3];
                const cos_ptr = cos_data + freq_offset;
                const sin_ptr = sin_data + freq_offset;
                const cos_stride = if (is_pytorch_format) cos.strides[2] else 1;
                const sin_stride = if (is_pytorch_format) sin.strides[2] else 1;

                math.applyRopeRotationStrided(
                    T,
                    toF32,
                    fromF32,
                    k_ptr,
                    k_stride,
                    cos_ptr,
                    cos_stride,
                    sin_ptr,
                    sin_stride,
                    half_dim,
                );
            }
        }
    }
}

/// Scaled Dot-Product Attention
/// Q: [batch, heads, seq_q, head_dim]
/// K: [batch, heads, seq_k, head_dim]
/// V: [batch, heads, seq_k, head_dim]
/// mask: optional [1, 1, seq_q, seq_k] or compatible broadcast shape
/// out: [batch, heads, seq_q, head_dim]
pub fn sdpa(
    out: TensorView,
    q: TensorView,
    k: TensorView,
    v: TensorView,
    mask: ?TensorView,
    scale: f32,
) void {
    switch (out.dtype) {
        .f32 => sdpaTyped(f32, f32Identity, f32Identity, out, q, k, v, mask, scale),
        .f16 => sdpaTyped(u16, fp16ToF32, f32ToFp16, out, q, k, v, mask, scale),
        .bf16 => sdpaTyped(u16, bf16ToF32, f32ToBf16, out, q, k, v, mask, scale),
        else => unreachable,
    }
}

fn sdpaTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    q: TensorView,
    k: TensorView,
    v: TensorView,
    mask: ?TensorView,
    scale: f32,
) void {
    std.debug.assert(q.ndim == 4);

    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const q_data = @as([*]const T, @ptrCast(@alignCast(q.data)));
    const k_data = @as([*]const T, @ptrCast(@alignCast(k.data)));
    const v_data = @as([*]const T, @ptrCast(@alignCast(v.data)));

    const batch = q.shape[0];
    const num_heads = q.shape[1];
    const seq_q = q.shape[2];
    const head_dim = q.shape[3];
    const seq_k = k.shape[2];

    // For each batch and head
    for (0..batch) |b| {
        for (0..num_heads) |h| {
            // For each query position
            for (0..seq_q) |sq| {
                // Compute attention scores for this query
                var scores: [4096]f32 = undefined; // Stack allocation for scores
                std.debug.assert(seq_k <= 4096);

                // Q @ K^T
                for (0..seq_k) |sk| {
                    var dot: f32 = 0;
                    for (0..head_dim) |d| {
                        const q_idx = b * @as(usize, @intCast(q.strides[0])) +
                            h * @as(usize, @intCast(q.strides[1])) +
                            sq * @as(usize, @intCast(q.strides[2])) +
                            d * @as(usize, @intCast(q.strides[3]));
                        const k_idx = b * @as(usize, @intCast(k.strides[0])) +
                            h * @as(usize, @intCast(k.strides[1])) +
                            sk * @as(usize, @intCast(k.strides[2])) +
                            d * @as(usize, @intCast(k.strides[3]));
                        dot += toF32(q_data[q_idx]) * toF32(k_data[k_idx]);
                    }
                    scores[sk] = dot * scale;

                    // Apply mask if provided
                    if (mask) |m| {
                        const m_data = @as([*]const f32, @ptrCast(@alignCast(m.data)));
                        // Broadcast mask: handle different shapes
                        const m_idx = (sq % m.shape[m.ndim - 2]) * @as(usize, @intCast(m.strides[m.ndim - 2])) +
                            (sk % m.shape[m.ndim - 1]) * @as(usize, @intCast(m.strides[m.ndim - 1]));
                        scores[sk] += m_data[m_idx];
                    }
                }

                // Softmax
                var max_score: f32 = -std.math.inf(f32);
                for (scores[0..seq_k]) |s| max_score = @max(max_score, s);
                math.softmaxMaskedInPlaceWithMax(scores[0..seq_k], 0, seq_k, null, false, max_score, -std.math.inf(f32) + 1.0);

                // Weighted sum of values
                for (0..head_dim) |d| {
                    var acc: f32 = 0;
                    for (0..seq_k) |sk| {
                        const v_idx = b * @as(usize, @intCast(v.strides[0])) +
                            h * @as(usize, @intCast(v.strides[1])) +
                            sk * @as(usize, @intCast(v.strides[2])) +
                            d * @as(usize, @intCast(v.strides[3]));
                        acc += scores[sk] * toF32(v_data[v_idx]);
                    }
                    const out_idx = b * @as(usize, @intCast(out.strides[0])) +
                        h * @as(usize, @intCast(out.strides[1])) +
                        sq * @as(usize, @intCast(out.strides[2])) +
                        d * @as(usize, @intCast(out.strides[3]));
                    out_data[out_idx] = fromF32(acc);
                }
            }
        }
    }
}

/// Scaled Dot-Product Attention with causal mask (optimized path)
/// This version doesn't require an explicit mask tensor - causal masking is applied implicitly.
/// Q: [batch, heads, seq_q, head_dim]
/// K: [batch, heads, seq_k, head_dim]
/// V: [batch, heads, seq_k, head_dim]
/// out: [batch, heads, seq_q, head_dim]
/// kv_offset: offset for causal mask (e.g., cache length for decode step)
pub fn sdpaCausal(
    out: TensorView,
    q: TensorView,
    k: TensorView,
    v: TensorView,
    scale: f32,
    kv_offset: usize,
) void {
    switch (out.dtype) {
        .f32 => sdpaCausalTyped(f32, f32Identity, f32Identity, out, q, k, v, scale, kv_offset),
        .f16 => sdpaCausalTyped(u16, fp16ToF32, f32ToFp16, out, q, k, v, scale, kv_offset),
        .bf16 => sdpaCausalTyped(u16, bf16ToF32, f32ToBf16, out, q, k, v, scale, kv_offset),
        else => unreachable,
    }
}

fn sdpaCausalTyped(
    comptime T: type,
    comptime toF32: fn (T) f32,
    comptime fromF32: fn (f32) T,
    out: TensorView,
    q: TensorView,
    k: TensorView,
    v: TensorView,
    scale: f32,
    kv_offset: usize,
) void {
    std.debug.assert(q.ndim == 4);

    const out_data = @as([*]T, @ptrCast(@alignCast(out.data)));
    const q_data = @as([*]const T, @ptrCast(@alignCast(q.data)));
    const k_data = @as([*]const T, @ptrCast(@alignCast(k.data)));
    const v_data = @as([*]const T, @ptrCast(@alignCast(v.data)));

    const batch = q.shape[0];
    const num_heads = q.shape[1];
    const seq_q = q.shape[2];
    const head_dim = q.shape[3];
    const seq_k = k.shape[2];

    const neg_inf = -std.math.inf(f32);

    for (0..batch) |b| {
        for (0..num_heads) |h| {
            for (0..seq_q) |sq| {
                var scores: [8192]f32 = undefined;
                std.debug.assert(seq_k <= 8192);

                // The query position in the full sequence
                const q_pos = kv_offset + sq;

                // Q @ K^T with causal masking
                for (0..seq_k) |sk| {
                    // Causal: can only attend to positions <= current position
                    if (sk > q_pos) {
                        scores[sk] = neg_inf;
                        continue;
                    }

                    var dot: f32 = 0;
                    for (0..head_dim) |d| {
                        const q_idx = b * @as(usize, @intCast(q.strides[0])) +
                            h * @as(usize, @intCast(q.strides[1])) +
                            sq * @as(usize, @intCast(q.strides[2])) +
                            d * @as(usize, @intCast(q.strides[3]));
                        const k_idx = b * @as(usize, @intCast(k.strides[0])) +
                            h * @as(usize, @intCast(k.strides[1])) +
                            sk * @as(usize, @intCast(k.strides[2])) +
                            d * @as(usize, @intCast(k.strides[3]));
                        dot += toF32(q_data[q_idx]) * toF32(k_data[k_idx]);
                    }
                    scores[sk] = dot * scale;
                }

                // Softmax
                var max_score: f32 = neg_inf;
                for (scores[0..seq_k]) |s| max_score = @max(max_score, s);
                math.softmaxMaskedInPlaceWithMax(scores[0..seq_k], 0, seq_k, null, false, max_score, neg_inf + 1.0);

                // Weighted sum of values
                for (0..head_dim) |d| {
                    var acc: f32 = 0;
                    for (0..seq_k) |sk| {
                        const v_idx = b * @as(usize, @intCast(v.strides[0])) +
                            h * @as(usize, @intCast(v.strides[1])) +
                            sk * @as(usize, @intCast(v.strides[2])) +
                            d * @as(usize, @intCast(v.strides[3]));
                        acc += scores[sk] * toF32(v_data[v_idx]);
                    }
                    const out_idx = b * @as(usize, @intCast(out.strides[0])) +
                        h * @as(usize, @intCast(out.strides[1])) +
                        sq * @as(usize, @intCast(out.strides[2])) +
                        d * @as(usize, @intCast(out.strides[3]));
                    out_data[out_idx] = fromF32(acc);
                }
            }
        }
    }
}

/// SDPA with cached K/V and optional features.
/// Computes attention where K/V come from a pre-filled cache.
///
/// Parameters:
/// - out_data: output buffer [n_heads * seq_q * head_dim]
/// - out_strides: strides for output [batch, heads, seq, dim]
/// - q_data: query data [batch * n_heads * seq_q * head_dim]
/// - q_strides: strides for query
/// - k_cache: cached keys [max_seq * n_kv_heads * head_dim] for this layer
/// - v_cache: cached values [max_seq * n_kv_heads * head_dim] for this layer
/// - n_heads, n_kv_heads: number of query and kv heads
/// - seq_q: number of query positions
/// - cached_seq: number of valid positions in cache
/// - head_dim: dimension per head
/// - kv_offset: offset for causal masking (current position in full sequence)
/// - scale: attention scale (typically 1/sqrt(head_dim))
/// - sinks: optional per-head sink logits (null if not used)
/// - sliding_window: 0 = disabled, >0 = only attend to last N positions
pub fn sdpaCached(
    out_data: [*]f32,
    out_strides: [4]usize,
    q_data: [*]const f32,
    q_strides: [4]usize,
    k_cache: []const f32,
    v_cache: []const f32,
    n_heads: usize,
    n_kv_heads: usize,
    seq_q: usize,
    cached_seq: usize,
    head_dim: usize,
    kv_offset: usize,
    scale: f32,
    sinks: ?[]const f32,
    sliding_window: usize,
) void {
    const neg_inf = -std.math.inf(f32);
    const heads_per_kv = n_heads / n_kv_heads;
    const kv_size = n_kv_heads * head_dim;

    for (0..n_heads) |qh| {
        const kv_head = qh / heads_per_kv;
        const sink_logit: ?f32 = if (sinks) |s| s[qh] else null;

        for (0..seq_q) |sq| {
            var scores: [8192]f32 = undefined;
            std.debug.assert(cached_seq <= 8192);

            const q_pos = kv_offset + sq;

            // Determine attention window
            const window_start: usize = if (sliding_window > 0 and q_pos >= sliding_window)
                q_pos - sliding_window + 1
            else
                0;

            var max_score: f32 = neg_inf;

            // Q @ K^T with causal + sliding window masking
            for (0..cached_seq) |sk| {
                if (sk < window_start or sk > q_pos) {
                    scores[sk] = neg_inf;
                    continue;
                }

                const k_cache_idx = sk * kv_size + kv_head * head_dim;
                var dot: f32 = 0;
                for (0..head_dim) |d| {
                    const q_idx = qh * q_strides[1] + sq * q_strides[2] + d * q_strides[3];
                    dot += q_data[q_idx] * k_cache[k_cache_idx + d];
                }
                scores[sk] = dot * scale;
                max_score = @max(max_score, scores[sk]);
            }

            // Include sink in max calculation
            if (sink_logit) |sl| {
                max_score = @max(max_score, sl);
            }

            // Softmax with optional sink
            math.softmaxMaskedInPlaceWithMax(scores[0..cached_seq], 0, cached_seq, sink_logit, false, max_score, neg_inf + 1.0);

            // Weighted sum of values
            for (0..head_dim) |d| {
                var acc: f32 = 0;
                for (0..cached_seq) |sk| {
                    const v_cache_idx = sk * kv_size + kv_head * head_dim;
                    acc += scores[sk] * v_cache[v_cache_idx + d];
                }
                const out_idx = qh * out_strides[1] + sq * out_strides[2] + d * out_strides[3];
                out_data[out_idx] = acc;
            }
        }
    }
}

/// Update KV cache with new K/V values (stride-aware copy)
/// Used by attention_with_kv_cache to update the cache before computing attention.
pub fn updateKVCache(
    k_cache: []f32,
    v_cache: []f32,
    k_data: [*]const f32,
    v_data: [*]const f32,
    k_strides: [4]usize,
    layer_offset: usize,
    seq_pos: usize,
    max_seq_len: usize,
    seq_len: usize,
    n_kv_heads: usize,
    head_dim: usize,
) void {
    const kv_size = n_kv_heads * head_dim;

    for (0..seq_len) |s| {
        const cache_pos = (seq_pos + s) % max_seq_len;
        const cache_idx = layer_offset + cache_pos * kv_size;

        for (0..n_kv_heads) |h| {
            for (0..head_dim) |d| {
                const in_idx = h * k_strides[1] + s * k_strides[2] + d * k_strides[3];
                k_cache[cache_idx + h * head_dim + d] = k_data[in_idx];
                v_cache[cache_idx + h * head_dim + d] = v_data[in_idx];
            }
        }
    }
}

test "ropeFreqs basic" {
    var data = [_]f32{0} ** 8;
    const out = TensorView.initContiguous(@ptrCast(&data), &.{ 2, 4 }, .f32);

    ropeFreqs(out, 10000.0, 0);

    // First position should have cos(0)=1, sin(0)=0 for first freq
    try std.testing.expectApproxEqAbs(@as(f32, 1.0), data[0], 1e-5); // cos at pos 0, freq 0
    try std.testing.expectApproxEqAbs(@as(f32, 0.0), data[2], 1e-5); // sin at pos 0, freq 0
}
