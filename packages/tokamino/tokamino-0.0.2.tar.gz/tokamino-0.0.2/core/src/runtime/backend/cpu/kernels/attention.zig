//! CPU Attention Kernel
//! Multi-head attention with grouped query attention (GQA) support
//!
//! This module provides the core attention computation for CPU inference.
//! It supports both prefill (multiple tokens) and decode (single token with KV cache) modes.

const std = @import("std");
const tensor = @import("../../../../tensor.zig");
const matmul = @import("../../../../compute/ops/matmul.zig");
const ops = @import("../../../../compute/ops/math.zig");
const simd = @import("../../../../compute/simd/root.zig");
const rope_kernel = @import("rope.zig");
const fused_attn = @import("fused_attention.zig");

const Tensor = tensor.Tensor;
const MatmulFn = matmul.MatmulFn;
const RoPE = rope_kernel.RoPE;

// Use comptime-detected SIMD width for all vector operations
const VEC_LEN = simd.f32_vec_len;
const F32Vec = simd.F32Vec;

/// Temporary scratch buffers for attention computation.
/// These are safe to share across layers because they do not persist state.
pub const AttnTemp = struct {
    q: []f32 = &.{},
    k: []f32 = &.{},
    v: []f32 = &.{},
    qkv: []f32 = &.{},
    scores: []f32 = &.{},
    ctx: []f32 = &.{},

    pub fn deinit(self: *AttnTemp, allocator: std.mem.Allocator) void {
        if (self.q.len > 0) allocator.free(self.q);
        if (self.k.len > 0) allocator.free(self.k);
        if (self.v.len > 0) allocator.free(self.v);
        if (self.qkv.len > 0) allocator.free(self.qkv);
        if (self.scores.len > 0) allocator.free(self.scores);
        if (self.ctx.len > 0) allocator.free(self.ctx);
        self.* = .{};
    }
};

/// Per-layer KV cache (must persist across calls).
pub const AttnCache = struct {
    kv_k: []f32 = &.{},
    kv_v: []f32 = &.{},
    kv_capacity: usize = 0,
    cache_pos: usize = 0,

    pub fn deinit(self: *AttnCache, allocator: std.mem.Allocator) void {
        if (self.kv_k.len > 0) allocator.free(self.kv_k);
        if (self.kv_v.len > 0) allocator.free(self.kv_v);
        self.* = .{};
    }

    pub fn resetCache(self: *AttnCache) void {
        self.cache_pos = 0;
    }
};

/// Multi-head attention layer with grouped query attention support.
pub const MultiHeadAttention = struct {
    d_model: usize,
    n_heads: usize,
    n_kv_heads: usize,
    head_dim: usize,
    max_seq_len: usize,
    /// Attention softmax temperature (typically 1/sqrt(head_dim), but some models override)
    scale: f32,
    /// Offset added to QK norm weights (e.g., 1.0 for Gemma's (1+w) formulation)
    qk_norm_weight_offset: f32 = 0.0,
    /// Sliding window attention (0 = disabled). When enabled, each query only attends
    /// to the most recent `sliding_window` keys (still causal).
    sliding_window: usize = 0,
    // Q/K/V projections - optional when using native fused QKV (Phi-style)
    q_proj: ?*const Tensor = null,
    k_proj: ?*const Tensor = null,
    v_proj: ?*const Tensor = null,
    o_proj: *const Tensor,
    fused_qkv: ?Tensor = null,
    rope: ?*RoPE = null,
    // QKNorm (Qwen3 specific) - applied after Q/K projection, before RoPE
    q_norm: ?*const Tensor = null,
    k_norm: ?*const Tensor = null,
    norm_eps: f32 = 1e-6,
    allocator: std.mem.Allocator,
    // Baked matmul kernels - resolved at load time, no runtime dispatch
    matmul_qkv: MatmulFn, // Default for Q, also used for K/V if they match Q's dtype
    matmul_k: ?MatmulFn = null, // Override for K if different dtype
    matmul_v: ?MatmulFn = null, // Override for V if different dtype
    matmul_qkv_fused: ?MatmulFn = null,
    matmul_o: MatmulFn,
    // Attention biases (GPT-OSS and similar architectures)
    q_bias: ?[]const f32 = null,
    k_bias: ?[]const f32 = null,
    v_bias: ?[]const f32 = null,
    o_bias: ?[]const f32 = null,
    // Attention sinks (GPT-OSS/MLX semantics) - per-head extra logit prepended to the score vector before softmax.
    sinks: ?[]const f32 = null,

    pub fn forward(
        self: *const MultiHeadAttention,
        x: *const Tensor, // [1, seq, d_model]
        out: *Tensor, // [1, seq, d_model]
        cache: *AttnCache,
        tmp: *AttnTemp,
        use_cache: bool,
    ) !void {
        const exact_softmax = std.process.hasEnvVar(self.allocator, "TOKAMINO_CPU_EXACT_SOFTMAX") catch false;
        // Internal invariants: model config must be valid after loading
        std.debug.assert(self.n_heads > 0 and self.n_kv_heads > 0);
        std.debug.assert(self.n_heads % self.n_kv_heads == 0);
        const q_dim = self.n_heads * self.head_dim;
        const kv_dim = self.n_kv_heads * self.head_dim;
        std.debug.assert(x.n_dims == 3 and out.n_dims == 3);
        std.debug.assert(x.shape[0] == 1 and out.shape[0] == 1); // Only batch=1 supported
        const seq: usize = @intCast(x.shape[1]);
        std.debug.assert(x.shape[2] == self.d_model and out.shape[2] == self.d_model);
        // Use fused QKV when available (required for Phi-style native fused, optional optimization for others)
        // Weight layout is [out_features, in_features] where out = q_dim + 2*kv_dim
        // For quantized weights, shape[1] is packed so we only check output dimension
        const use_fused_qkv = if (self.fused_qkv) |fq| blk: {
            if (fq.dtype == .f32 and fq.shape[1] == q_dim + 2 * kv_dim) break :blk true;
            break :blk fq.shape[0] == q_dim + 2 * kv_dim;
        } else false;
        try self.ensureTemp(tmp, seq, use_cache, q_dim, kv_dim, use_fused_qkv);

        // Flatten batch dimension for matmul
        const a_view = Tensor.view2D(x.data(), seq, self.d_model);
        var q_view: Tensor = undefined;
        var k_view: Tensor = undefined;
        var v_view: Tensor = undefined;
        const debug_qkv = std.posix.getenv("TOKAMINO_DEBUG_QKV") != null;
        if (use_fused_qkv) {
            const fused_qkv = self.fused_qkv.?;
            const fused_kernel = self.matmul_qkv_fused orelse self.matmul_qkv;
            const views = fused_attn.projectQkv(&a_view, &fused_qkv, tmp.qkv, seq, q_dim, kv_dim, fused_kernel);
            q_view = views.q;
            k_view = views.k;
            v_view = views.v;

            if (debug_qkv) {
                const q_data = q_view.asSlice(f32);
                const k_data = k_view.asSlice(f32);
                const v_data = v_view.asSlice(f32);
                std.debug.print("fused QKV split: Q[0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{ q_data[0], q_data[1], q_data[2], q_data[3] });
                std.debug.print("                 K[0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{ k_data[0], k_data[1], k_data[2], k_data[3] });
                std.debug.print("                 V[0:4]=[{d:.4},{d:.4},{d:.4},{d:.4}]\n", .{ v_data[0], v_data[1], v_data[2], v_data[3] });
            }
        } else {
            // Separate Q/K/V projections - must have all three
            const q_proj = self.q_proj orelse return error.MissingAttentionWeights;
            const k_proj = self.k_proj orelse return error.MissingAttentionWeights;
            const v_proj = self.v_proj orelse return error.MissingAttentionWeights;

            var q_tmp = Tensor.view2DSlice(tmp.q[0 .. seq * q_dim], seq, q_dim);
            var k_tmp = Tensor.view2DSlice(tmp.k[0 .. seq * kv_dim], seq, kv_dim);
            var v_tmp = Tensor.view2DSlice(tmp.v[0 .. seq * kv_dim], seq, kv_dim);
            const debug_matmul = std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_MATMUL") catch false;
            const t0 = if (debug_matmul) std.time.nanoTimestamp() else 0;
            self.matmul_qkv(&a_view, q_proj, &q_tmp);
            const t1 = if (debug_matmul) std.time.nanoTimestamp() else 0;
            // Use separate matmul for K/V if they have different dtype than Q
            const matmul_k_fn = self.matmul_k orelse self.matmul_qkv;
            const matmul_v_fn = self.matmul_v orelse self.matmul_qkv;
            matmul_k_fn(&a_view, k_proj, &k_tmp);
            const t2 = if (debug_matmul) std.time.nanoTimestamp() else 0;
            matmul_v_fn(&a_view, v_proj, &v_tmp);
            const t3 = if (debug_matmul) std.time.nanoTimestamp() else 0;
            if (debug_matmul) {
                std.debug.print("QKV matmul: Q={d:.3}ms K={d:.3}ms V={d:.3}ms (m={} k={} n_q={} n_kv={})\n", .{
                    @as(f64, @floatFromInt(t1 - t0)) / 1e6,
                    @as(f64, @floatFromInt(t2 - t1)) / 1e6,
                    @as(f64, @floatFromInt(t3 - t2)) / 1e6,
                    seq,
                    self.d_model,
                    q_dim,
                    kv_dim,
                });
            }
            q_view = q_tmp;
            k_view = k_tmp;
            v_view = v_tmp;
        }

        if (debug_qkv) {
            const q_data = q_view.asSlice(f32);
            const k_data = k_view.asSlice(f32);
            const v_data = v_view.asSlice(f32);
            std.debug.print("Q proj first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ q_data[0], q_data[1], q_data[2], q_data[3] });
            std.debug.print("K proj first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ k_data[0], k_data[1], k_data[2], k_data[3] });
            std.debug.print("V proj first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ v_data[0], v_data[1], v_data[2], v_data[3] });
        }

        // Apply attention biases if present (GPT-OSS and similar)
        if (self.q_bias) |bias| {
            addBias(q_view.asSlice(f32), bias, seq, q_dim);
        }
        if (self.k_bias) |bias| {
            addBias(k_view.asSlice(f32), bias, seq, kv_dim);
        }
        if (self.v_bias) |bias| {
            addBias(v_view.asSlice(f32), bias, seq, kv_dim);
        }

        if (debug_qkv) {
            const q_data = q_view.asSlice(f32);
            const k_data = k_view.asSlice(f32);
            const v_data = v_view.asSlice(f32);
            std.debug.print("Q after bias first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ q_data[0], q_data[1], q_data[2], q_data[3] });
            std.debug.print("K after bias first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ k_data[0], k_data[1], k_data[2], k_data[3] });
            std.debug.print("V after bias first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ v_data[0], v_data[1], v_data[2], v_data[3] });
        }

        // Apply QKNorm if present (Qwen3 specific)
        // Normalize each head's Q/K vectors independently
        // Note: weight tensors may be stored as BF16/F16 and may not be aligned
        if (self.q_norm) |qn| {
            const q_slice = q_view.asSlice(f32);
            var t: usize = 0;
            while (t < seq) : (t += 1) {
                var h: usize = 0;
                while (h < self.n_heads) : (h += 1) {
                    const base = t * q_dim + h * self.head_dim;
                    applyQKNormInPlace(q_slice[base .. base + self.head_dim], qn, self.norm_eps, self.qk_norm_weight_offset);
                }
            }
        }
        if (self.k_norm) |kn| {
            const k_slice = k_view.asSlice(f32);
            var t: usize = 0;
            while (t < seq) : (t += 1) {
                var h: usize = 0;
                while (h < self.n_kv_heads) : (h += 1) {
                    const base = t * kv_dim + h * self.head_dim;
                    applyQKNormInPlace(k_slice[base .. base + self.head_dim], kn, self.norm_eps, self.qk_norm_weight_offset);
                }
            }
        }

        // Apply RoPE to Q/K per position/head
        // pos_offset is the position in the sequence (accounting for cached tokens)
        // Note: For partial rotary (e.g., Phi), rope.dim < head_dim. We only apply RoPE
        // to the first rope.dim dimensions, leaving the rest unchanged.
        const pos_offset = if (use_cache) cache.cache_pos else 0;
        if (self.rope) |rope| {
            const rope_dim = rope.dim;
            var t: usize = 0;
            while (t < seq) : (t += 1) {
                const pos = pos_offset + t;
                var h: usize = 0;
                while (h < self.n_heads) : (h += 1) {
                    const base = t * q_dim + h * self.head_dim;
                    rope.applyInPlace(q_view.asSlice(f32)[base .. base + rope_dim], pos);
                }
                h = 0;
                while (h < self.n_kv_heads) : (h += 1) {
                    const base = t * kv_dim + h * self.head_dim;
                    rope.applyInPlace(k_view.asSlice(f32)[base .. base + rope_dim], pos);
                }
            }
        }

        // Populate KV cache during prefill so subsequent decode steps can attend to the prompt.
        // Cache layout matches the decode path: [kv_head, seq_pos, head_dim].
        if (!use_cache) {
            const k_data_prefill = k_view.asSlice(f32);
            const v_data_prefill = v_view.asSlice(f32);
            try self.ensureKvCapacity(cache, seq, kv_dim);
            const head_dim = self.head_dim;
            const n_kv_heads = self.n_kv_heads;
            const kv_stride = cache.kv_capacity;

            for (0..n_kv_heads) |kv_h| {
                var pos: usize = 0;
                while (pos < seq) : (pos += 1) {
                    const src_k = k_data_prefill[pos * kv_dim + kv_h * head_dim ..][0..head_dim];
                    const src_v = v_data_prefill[pos * kv_dim + kv_h * head_dim ..][0..head_dim];
                    const dst_k = cache.kv_k[kv_h * kv_stride * head_dim + pos * head_dim ..][0..head_dim];
                    const dst_v = cache.kv_v[kv_h * kv_stride * head_dim + pos * head_dim ..][0..head_dim];
                    @memcpy(dst_k, src_k);
                    @memcpy(dst_v, src_v);
                }
            }
            cache.cache_pos = seq;
        }

        // Attention scores and context
        const scores = tmp.scores;
        const ctx = tmp.ctx;
        const q_data = q_view.asSlice(f32);
        const k_data = k_view.asSlice(f32);
        const v_data = v_view.asSlice(f32);
        const scale = self.scale;
        const heads_per_kv = self.n_heads / self.n_kv_heads;

        if (use_cache) {
            std.debug.assert(seq == 1); // Cache mode only processes one token at a time
            if (cache.cache_pos >= self.max_seq_len) return error.CacheOverflow;

            const kv_seq_len = cache.cache_pos + seq;
            if (kv_seq_len > self.max_seq_len) return error.CacheOverflow;
            const start_k: usize = if (self.sliding_window > 0 and kv_seq_len > self.sliding_window)
                kv_seq_len - self.sliding_window
            else
                0;
            // Grow cache buffers as needed (layout: [kv_head, seq_pos, head_dim])
            try self.ensureKvCapacity(cache, kv_seq_len, kv_dim);

            // Append current K/V to cache with transposed layout [kv_head, seq_pos, head_dim]
            const head_dim = self.head_dim;
            const n_kv_heads = self.n_kv_heads;
            const kv_stride = cache.kv_capacity;
            const cache_pos = cache.cache_pos;
            const score_stride = self.max_seq_len;

            // Copy K/V for each kv_head to its contiguous region
            for (0..n_kv_heads) |kv_h| {
                const src_k = k_data[kv_h * head_dim ..][0..head_dim];
                const src_v = v_data[kv_h * head_dim ..][0..head_dim];
                // Cache layout: kv_head * (kv_stride * head_dim) + seq_pos * head_dim
                const dst_k = cache.kv_k[kv_h * kv_stride * head_dim + cache_pos * head_dim ..][0..head_dim];
                const dst_v = cache.kv_v[kv_h * kv_stride * head_dim + cache_pos * head_dim ..][0..head_dim];
                @memcpy(dst_k, src_k);
                @memcpy(dst_v, src_v);
            }

            // Iterate by kv_head first to maximize K/V cache reuse
            // All Q heads sharing the same KV head process together
            var kv_h: usize = 0;
            while (kv_h < n_kv_heads) : (kv_h += 1) {
                // K/V cache for this kv_head - read once, reuse for all Q heads
                const k_cache_base = cache.kv_k[kv_h * kv_stride * head_dim ..];
                const v_cache_base = cache.kv_v[kv_h * kv_stride * head_dim ..];

                // Process all Q heads that share this KV head
                const h_start = kv_h * heads_per_kv;
                const h_end = h_start + heads_per_kv;

                var h: usize = h_start;
                while (h < h_end) : (h += 1) {
                    const q_head = q_data[h * head_dim ..][0..head_dim];
                    const scores_head = scores[h * score_stride ..][0..kv_seq_len];

                    // Q·K dot products with inline SIMD
                    var maxv: f32 = -std.math.inf(f32);
                    var kpos: usize = 0;
                    while (kpos < start_k) : (kpos += 1) {
                        scores_head[kpos] = -std.math.inf(f32);
                    }
                    while (kpos < kv_seq_len) : (kpos += 1) {
                        const k_row = k_cache_base[kpos * head_dim ..][0..head_dim];

                        // Inline SIMD dot product
                        var sum0: F32Vec = @splat(0);
                        var sum1: F32Vec = @splat(0);
                        var d: usize = 0;
                        while (d + 2 * VEC_LEN - 1 < head_dim) : (d += 2 * VEC_LEN) {
                            const vq0: F32Vec = q_head[d..][0..VEC_LEN].*;
                            const vk0: F32Vec = k_row[d..][0..VEC_LEN].*;
                            const vq1: F32Vec = q_head[d + VEC_LEN ..][0..VEC_LEN].*;
                            const vk1: F32Vec = k_row[d + VEC_LEN ..][0..VEC_LEN].*;
                            sum0 = @mulAdd(F32Vec, vq0, vk0, sum0);
                            sum1 = @mulAdd(F32Vec, vq1, vk1, sum1);
                        }
                        while (d + VEC_LEN - 1 < head_dim) : (d += VEC_LEN) {
                            const vq: F32Vec = q_head[d..][0..VEC_LEN].*;
                            const vk: F32Vec = k_row[d..][0..VEC_LEN].*;
                            sum0 = @mulAdd(F32Vec, vq, vk, sum0);
                        }
                        var dot = @reduce(.Add, sum0 + sum1);
                        while (d < head_dim) : (d += 1) {
                            dot += q_head[d] * k_row[d];
                        }
                        dot *= scale;
                        scores_head[kpos] = dot;
                        if (dot > maxv) maxv = dot;
                    }

                    // Attention sinks (MLX semantics): add an extra "sink" logit before softmax,
                    // then discard its probability mass (do not renormalize).
                    // This effectively dampens attention outputs by (1 - p_sink).
                    const sink_logit: ?f32 = if (self.sinks) |s| s[h] else null;
                    if (sink_logit) |sl| {
                        if (sl > maxv) maxv = sl;
                    }

                    ops.softmaxMaskedInPlaceWithMax(
                        scores_head,
                        start_k,
                        kv_seq_len,
                        sink_logit,
                        exact_softmax,
                        maxv,
                        null,
                    );

                    // Initialize context output for this head to zero
                    const ctx_head = ctx[h * head_dim ..][0..head_dim];
                    @memset(ctx_head, 0);

                    // Context accumulation
                    var j: usize = 0;
                    while (j < kv_seq_len) : (j += 1) {
                        const attn_weight = scores_head[j];
                        const v_row = v_cache_base[j * head_dim ..][0..head_dim];

                        // SIMD accumulation with FMA
                        const weight_vec: F32Vec = @splat(attn_weight);
                        var d: usize = 0;
                        while (d + VEC_LEN - 1 < head_dim) : (d += VEC_LEN) {
                            const v_vec: F32Vec = v_row[d..][0..VEC_LEN].*;
                            const out_slice = ctx_head[d..][0..VEC_LEN];
                            out_slice.* = @mulAdd(F32Vec, weight_vec, v_vec, out_slice.*);
                        }
                        while (d < head_dim) : (d += 1) {
                            ctx_head[d] += attn_weight * v_row[d];
                        }
                    }
                }
            }

            // Apply output projection directly from ctx buffer (already laid out as [seq, q_dim])
            const attn_view = Tensor.view2DSlice(ctx[0 .. seq * q_dim], seq, q_dim);
            var out_view = Tensor.view2DSlice(out.asSlice(f32), seq, self.d_model);
            self.matmul_o(&attn_view, self.o_proj, &out_view);
            // Apply output bias if present
            if (self.o_bias) |bias| {
                addBias(out.asSlice(f32), bias, seq, self.d_model);
            }
            cache.cache_pos = kv_seq_len;
            return;
        }

        // SIMD-optimized prefill attention
        const head_dim = self.head_dim;
        var h: usize = 0;
        while (h < self.n_heads) : (h += 1) {
            const kv_head = h / heads_per_kv;
            var qpos: usize = 0;
            while (qpos < seq) : (qpos += 1) {
                const start_k: usize = if (self.sliding_window > 0 and (qpos + 1) > self.sliding_window)
                    (qpos + 1) - self.sliding_window
                else
                    0;
                var maxv: f32 = -std.math.inf(f32);
                const q_head = q_data[qpos * q_dim + h * head_dim ..][0..head_dim];
                const scores_row = scores[h * seq ..][0..seq];
                const ctx_head = ctx[(qpos * self.n_heads + h) * head_dim ..][0..head_dim];

                var kpos: usize = 0;
                while (kpos < start_k) : (kpos += 1) {
                    scores_row[kpos] = -std.math.inf(f32);
                }
                while (kpos <= qpos) : (kpos += 1) {
                    const k_head = k_data[kpos * kv_dim + kv_head * head_dim ..][0..head_dim];

                    // SIMD dot product
                    var sum0: F32Vec = @splat(0);
                    var sum1: F32Vec = @splat(0);
                    var d: usize = 0;
                    while (d + 2 * VEC_LEN - 1 < head_dim) : (d += 2 * VEC_LEN) {
                        const vq0: F32Vec = q_head[d..][0..VEC_LEN].*;
                        const vk0: F32Vec = k_head[d..][0..VEC_LEN].*;
                        const vq1: F32Vec = q_head[d + VEC_LEN ..][0..VEC_LEN].*;
                        const vk1: F32Vec = k_head[d + VEC_LEN ..][0..VEC_LEN].*;
                        sum0 = @mulAdd(F32Vec, vq0, vk0, sum0);
                        sum1 = @mulAdd(F32Vec, vq1, vk1, sum1);
                    }
                    while (d + VEC_LEN - 1 < head_dim) : (d += VEC_LEN) {
                        const vq: F32Vec = q_head[d..][0..VEC_LEN].*;
                        const vk: F32Vec = k_head[d..][0..VEC_LEN].*;
                        sum0 = @mulAdd(F32Vec, vq, vk, sum0);
                    }
                    var dot = @reduce(.Add, sum0 + sum1);
                    while (d < head_dim) : (d += 1) {
                        dot += q_head[d] * k_head[d];
                    }
                    dot *= scale;
                    scores_row[kpos] = dot;
                    if (dot > maxv) maxv = dot;
                }
                // Fill causal mask (only needed for exp/normalize loops; we keep it zeroed after softmax)
                while (kpos < seq) : (kpos += 1) scores_row[kpos] = -std.math.inf(f32);

                // Attention sinks (MLX semantics): add an extra "sink" logit before softmax,
                // then discard its probability mass (do not renormalize).
                const sink_logit: ?f32 = if (self.sinks) |s| s[h] else null;
                if (sink_logit) |sl| {
                    if (sl > maxv) maxv = sl;
                }

                const attn_len = qpos + 1;
                ops.softmaxMaskedInPlaceWithMax(
                    scores_row,
                    start_k,
                    attn_len,
                    sink_logit,
                    exact_softmax,
                    maxv,
                    null,
                );

                // Context accumulation directly into output buffer (avoid storing full scores matrix)
                @memset(ctx_head, 0);
                var kpos2: usize = start_k;
                while (kpos2 <= qpos) : (kpos2 += 1) {
                    const attn_weight = scores_row[kpos2];
                    if (attn_weight == 0) continue;
                    const v_head = v_data[kpos2 * kv_dim + kv_head * head_dim ..][0..head_dim];
                    const weight_vec: F32Vec = @splat(attn_weight);

                    var d: usize = 0;
                    while (d + VEC_LEN - 1 < head_dim) : (d += VEC_LEN) {
                        const v_vec: F32Vec = v_head[d..][0..VEC_LEN].*;
                        const out_slice = ctx_head[d..][0..VEC_LEN];
                        out_slice.* = @mulAdd(F32Vec, weight_vec, v_vec, out_slice.*);
                    }
                    while (d < head_dim) : (d += 1) {
                        ctx_head[d] += attn_weight * v_head[d];
                    }
                }
            }
        }

        // Apply output projection directly from ctx buffer (layout: [seq, heads, head_dim])
        if (debug_qkv) {
            std.debug.print("ctx before o_proj first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ ctx[0], ctx[1], ctx[2], ctx[3] });
        }
        var attn_view = Tensor.view2DSlice(ctx[0 .. seq * q_dim], seq, q_dim);
        var out_view = Tensor.view2DSlice(out.asSlice(f32), seq, self.d_model);
        self.matmul_o(&attn_view, self.o_proj, &out_view);
        // Apply output bias if present
        if (self.o_bias) |bias| {
            addBias(out.asSlice(f32), bias, seq, self.d_model);
        }

        if (debug_qkv) {
            const out_data = out.asSlice(f32);
            std.debug.print("attn output first 4: [{d:.6}, {d:.6}, {d:.6}, {d:.6}]\n", .{ out_data[0], out_data[1], out_data[2], out_data[3] });
        }
    }

    pub fn ensureTemp(self: *const MultiHeadAttention, tmp: *AttnTemp, seq: usize, use_cache: bool, q_dim: usize, kv_dim: usize, use_fused_qkv: bool) !void {
        // Always allocate separate Q, K, V buffers
        try ensureSlice(self.allocator, &tmp.q, seq * q_dim);
        try ensureSlice(self.allocator, &tmp.k, seq * kv_dim);
        try ensureSlice(self.allocator, &tmp.v, seq * kv_dim);
        if (use_fused_qkv) {
            // Need buffer for fused matmul output + rearranged result (2x size)
            // First half: final rearranged Q/K/V
            // Second half: temporary matmul output before rearrangement
            try ensureSlice(self.allocator, &tmp.qkv, 2 * seq * (q_dim + 2 * kv_dim));
        }
        // Decode uses scores[head, max_seq_len] for current token; prefill reuses scores[head, seq] per query.
        const scores_needed = if (use_cache) self.n_heads * self.max_seq_len else self.n_heads * seq;
        try ensureSlice(self.allocator, &tmp.scores, scores_needed);
        try ensureSlice(self.allocator, &tmp.ctx, seq * self.n_heads * self.head_dim);
    }

    pub fn ensureKvCapacity(self: *const MultiHeadAttention, cache: *AttnCache, needed_seq: usize, kv_dim: usize) !void {
        if (needed_seq <= cache.kv_capacity and cache.kv_k.len > 0 and cache.kv_v.len > 0) return;

        const current = cache.kv_capacity;
        const grow_to = if (current == 0) needed_seq else @max(needed_seq, current * 2);
        const target_seq = @min(self.max_seq_len, grow_to);
        const total = target_seq * kv_dim;
        const new_k = try self.allocator.alloc(f32, total);
        errdefer self.allocator.free(new_k);
        const new_v = try self.allocator.alloc(f32, total);
        errdefer self.allocator.free(new_v);

        if (cache.kv_capacity > 0) {
            const old_stride = cache.kv_capacity;
            const head_dim = self.head_dim;
            for (0..self.n_kv_heads) |kv_h| {
                for (0..cache.cache_pos) |pos| {
                    const src_k = cache.kv_k[kv_h * old_stride * head_dim + pos * head_dim ..][0..head_dim];
                    const src_v = cache.kv_v[kv_h * old_stride * head_dim + pos * head_dim ..][0..head_dim];
                    const dst_k = new_k[kv_h * target_seq * head_dim + pos * head_dim ..][0..head_dim];
                    const dst_v = new_v[kv_h * target_seq * head_dim + pos * head_dim ..][0..head_dim];
                    @memcpy(dst_k, src_k);
                    @memcpy(dst_v, src_v);
                }
            }
            self.allocator.free(cache.kv_k);
            self.allocator.free(cache.kv_v);
        }

        cache.kv_k = new_k;
        cache.kv_v = new_v;
        cache.kv_capacity = target_seq;
    }
};

/// Apply QKNorm (RMS normalization) in-place with support for BF16/F16/F32 weight tensors.
/// This handles the weight tensor dtype conversion for QKNorm weights which may be stored
/// in various formats in safetensors files.
pub fn applyQKNormInPlace(vec: []f32, weight_tensor: *const Tensor, eps: f32, weight_offset: f32) void {
    ops.rmsnormInPlaceWeightTensor(vec, weight_tensor, eps, weight_offset);
}

fn ensureSlice(allocator: std.mem.Allocator, buf: *[]f32, needed: usize) !void {
    if (buf.*.len >= needed) return;
    if (buf.*.len > 0) allocator.free(buf.*);
    buf.* = try allocator.alloc(f32, needed);
}

/// Add bias to output tensor (for attention with bias)
/// data: [seq, dim], bias: [dim]
fn addBias(data: []f32, bias: []const f32, seq: usize, dim: usize) void {
    for (0..seq) |t| {
        const row = data[t * dim ..][0..dim];
        var i: usize = 0;
        while (i + VEC_LEN - 1 < dim) : (i += VEC_LEN) {
            const d: F32Vec = row[i..][0..VEC_LEN].*;
            const b: F32Vec = bias[i..][0..VEC_LEN].*;
            row[i..][0..VEC_LEN].* = d + b;
        }
        while (i < dim) : (i += 1) {
            row[i] += bias[i];
        }
    }
}
