//! CPU Block Kernel Containers + Scratch
//!
//! This file defines the CPU-side kernel structs and scratch buffers used by the
//! transformer engine (`src/model/*`).
//!
//! The *execution order* (the transformer “graph”) lives in `src/model/`;
//! this file provides the concrete CPU kernels (attention/ffn/norm) and the per-layer
//! containers (`TransformerBlock`) that the engine references.

const std = @import("std");
const tensor = @import("../../../tensor.zig");
const matmul = @import("../../../compute/ops/matmul.zig");
const ops = @import("../../../ops.zig");

pub const BufferId = ops.BufferId;

// Import CPU kernels
const attn = @import("kernels/attention.zig");
const ffn = @import("kernels/ffn.zig");
const moe = @import("kernels/moe.zig");
const norm = @import("kernels/norm.zig");
const rope = @import("kernels/rope.zig");
const embedding = @import("kernels/embedding.zig");
const simd = @import("../../../compute/simd/root.zig");

const Tensor = tensor.Tensor;
const ModelConfig = tensor.ModelConfig;

// Re-export kernel types for external use
pub const AttnTemp = attn.AttnTemp;
pub const AttnCache = attn.AttnCache;
pub const FfnScratch = ffn.FfnScratch;
pub const MultiHeadAttention = attn.MultiHeadAttention;
pub const SwiGLU = ffn.SwiGLU;
pub const GateUpLayout = ffn.GateUpLayout;
pub const RMSNorm = norm.RMSNorm;
pub const RoPE = rope.RoPE;
pub const rmsnormForward = norm.rmsnormForward;
pub const gatherEmbeddings = embedding.gatherEmbeddings;

/// Number of temporary buffers available.
/// Array index maps to BufferId enum values (except index 0):
/// - [0] = layer_tmp (internal use for Model.forward alternating buffer)
/// - [1] = norm_out (BufferId.norm_out = 1)
/// - [2] = branch_out (BufferId.branch_out = 2)
/// - [3..63] = tmp3..tmp63 (BufferId.tmp3 = 3, etc.)
/// Note: BufferId.residual (0) is NOT stored here - it uses the model output buffer.
pub const NUM_TMP_BUFFERS: usize = 64;

/// Scratch buffers shared across transformer forward pass.
/// Uses an array for tmp buffers to simplify allocation/deallocation.
pub const ScratchBuffer = struct {
    allocator: std.mem.Allocator,
    d_model: usize,
    d_ff: usize,

    /// Unified temporary buffer array. See NUM_TMP_BUFFERS doc for index mapping.
    /// Access via getTmp(BufferId, len) or getLayerTmp(len) for index 0.
    tmp: [NUM_TMP_BUFFERS][]f32 = [_][]f32{&.{}} ** NUM_TMP_BUFFERS,

    attn_caches: []attn.AttnCache = &.{},
    attn_tmp: attn.AttnTemp = .{},
    ffn_scratch: ffn.FfnScratch = .{},
    moe_scratch: moe.MoEScratch = .{}, // For MoE layers

    /// Get a temporary buffer by BufferId and length.
    /// This is the canonical way to access scratch buffers.
    /// Asserts that:
    /// - id is not .residual (which uses the model output buffer, not scratch)
    /// - the requested length fits within the allocated buffer
    pub fn getTmp(self: *ScratchBuffer, id: BufferId, len: usize) []f32 {
        const idx = @intFromEnum(id);
        std.debug.assert(id != .residual); // residual uses model output, not scratch
        std.debug.assert(idx < NUM_TMP_BUFFERS);
        const buf = self.tmp[idx];
        std.debug.assert(len <= buf.len); // buffer must be allocated via ensure()
        return buf[0..len];
    }

    /// Get layer_tmp buffer (internal use, index 0).
    /// This buffer is used by Model.forward for alternating input/output between layers.
    /// Asserts the requested length fits within the allocated buffer.
    pub fn getLayerTmp(self: *ScratchBuffer, len: usize) []f32 {
        const buf = self.tmp[0];
        std.debug.assert(len <= buf.len); // buffer must be allocated via ensure()
        return buf[0..len];
    }

    pub fn init(allocator: std.mem.Allocator, d_model: usize, d_ff: usize, n_layers: usize) ScratchBuffer {
        const attn_buf = allocator.alloc(attn.AttnCache, n_layers) catch unreachable;
        for (attn_buf) |*a| a.* = .{};
        return .{ .allocator = allocator, .d_model = d_model, .d_ff = d_ff, .attn_caches = attn_buf };
    }

    pub fn ensure(self: *ScratchBuffer, seq: usize) !void {
        // Account for fused projections which can be larger than d_model or d_ff alone:
        // - Fused QKV: ~1.5x d_model (Q + K + V)
        // - Fused gate_up: 2x d_ff (gate + up)
        // Use 2x d_ff as the max to handle all cases
        const max_dim = @max(self.d_model, self.d_ff * 2);
        const size = seq * max_dim;

        // Ensure all temporary buffers in a single loop
        for (&self.tmp) |*buf| {
            try ensureSlice(self.allocator, buf, size);
        }
    }

    pub fn deinit(self: *ScratchBuffer) void {
        // Free all temporary buffers in a single loop
        for (&self.tmp) |*buf| {
            if (buf.len > 0) {
                self.allocator.free(buf.*);
                buf.* = &.{};
            }
        }

        self.attn_tmp.deinit(self.allocator);
        for (self.attn_caches) |*a| a.deinit(self.allocator);
        if (self.attn_caches.len > 0) self.allocator.free(self.attn_caches);
        if (self.ffn_scratch.gate.len > 0) self.allocator.free(self.ffn_scratch.gate);
        if (self.ffn_scratch.gate_act.len > 0) self.allocator.free(self.ffn_scratch.gate_act);
        if (self.ffn_scratch.up.len > 0) self.allocator.free(self.ffn_scratch.up);
        if (self.ffn_scratch.hidden.len > 0) self.allocator.free(self.ffn_scratch.hidden);
        self.moe_scratch.deinit(self.allocator);
    }

    pub fn resetCaches(self: *ScratchBuffer) void {
        for (self.attn_caches) |*a| a.resetCache();
    }
};

/// Pre-concatenated weights for fused kernels (optional per block).
pub const FusedBlockWeights = struct {
    qkv_proj: ?Tensor = null,
    gate_up: ?Tensor = null,
    gate_up_layout: ffn.GateUpLayout = .concat,
};

/// MoE (Mixture of Experts) weights for a layer
pub const MoEWeights = struct {
    router_weight: Tensor,
    router_bias: ?[]const f32 = null,
    experts: []moe.ExpertWeights,
    num_experts: usize,
    experts_per_token: usize,
    use_mxfp4: bool = false,
};

/// Weights for a single transformer block.
pub const BlockWeights = struct {
    ln1_weight: *const Tensor, // input_layernorm
    ln2_weight: *const Tensor, // post_attention_layernorm
    // Q/K/V projections - optional when using native fused QKV (Phi-style)
    q_proj: ?*const Tensor = null,
    k_proj: ?*const Tensor = null,
    v_proj: ?*const Tensor = null,
    o_proj: *const Tensor,
    // Dense FFN weights (null if MoE)
    w1: ?*const Tensor = null,
    w2: ?*const Tensor = null,
    w3: ?*const Tensor = null,
    rope: ?*rope.RoPE = null,
    /// Sliding window attention size for this layer (0 = disabled/global attention).
    /// For Gemma3, non-global layers use a window like 512/1024.
    sliding_window: usize = 0,
    fused: FusedBlockWeights = .{},
    // QKNorm weights (Qwen3/Gemma3 specific)
    q_norm: ?*const Tensor = null,
    k_norm: ?*const Tensor = null,
    // Gemma3-specific FFN norms (4 norms per block instead of 2)
    pre_ffn_norm: ?*const Tensor = null, // pre_feedforward_layernorm
    post_ffn_norm: ?*const Tensor = null, // post_feedforward_layernorm
    // Attention biases (GPT-OSS and similar)
    q_bias: ?[]const f32 = null,
    k_bias: ?[]const f32 = null,
    v_bias: ?[]const f32 = null,
    o_bias: ?[]const f32 = null,
    // MoE weights (null if dense FFN)
    moe_weights: ?*MoEWeights = null,
    // Attention sinks (GPT-OSS/MLX semantics) - per-head extra logit prepended to the score vector before softmax.
    sinks: ?[]const f32 = null,
};

/// FFN layer type - either dense SwiGLU or Mixture of Experts
pub const FfnLayer = union(enum) {
    swiglu: ffn.SwiGLU,
    moe_ffn: moe.MoEFFN,

    pub fn forward(self: *const FfnLayer, x: *const Tensor, out: *Tensor, scratch: *ScratchBuffer) !void {
        switch (self.*) {
            .swiglu => |*s| try s.forward(x, out, &scratch.ffn_scratch),
            .moe_ffn => |*m| try m.forward(x, out, &scratch.moe_scratch),
        }
    }

    pub fn getDModel(self: *const FfnLayer) usize {
        return switch (self.*) {
            .swiglu => |s| s.d_model,
            .moe_ffn => |m| m.d_model,
        };
    }
};

/// Kernel container for a single transformer block.
/// Holds the kernel structs (attention, FFN) that the transformer engine references.
/// Note: The forward() logic is in `src/model/root.zig`, not here.
pub const TransformerBlock = struct {
    ln1: norm.RMSNorm,
    attention: attn.MultiHeadAttention,
    ln2: norm.RMSNorm,
    pre_ffn_norm: ?norm.RMSNorm = null,
    post_ffn_norm: ?norm.RMSNorm = null,
    ffn_layer: FfnLayer,
    residual_multiplier: f32 = 1.0,
    block_idx: usize = 0,

    /// Weight registry for primitive op execution.
    /// Maps weight names (e.g., "qkv_proj", "o_proj") to tensor pointers.
    /// Enables the `linear` primitive op to look up weights by name.
    weight_registry: std.StringHashMapUnmanaged(*const tensor.Tensor) = .{},

    /// Storage for fused weights (copied from BlockWeights to extend lifetime).
    /// These are referenced by weight_registry entries.
    fused_qkv_storage: ?tensor.Tensor = null,
    fused_gate_up_storage: ?tensor.Tensor = null,

    pub fn init(
        allocator: std.mem.Allocator,
        d_model: usize,
        d_ff: usize,
        n_heads: usize,
        n_kv_heads: usize,
        head_dim: usize,
        max_seq_len: usize,
        weights: BlockWeights,
        norm_eps: f32,
        runtime: tensor.ModelRuntime,
        residual_multiplier: f32,
        attention_scale: f32,
        use_gelu: bool,
        block_idx: usize,
    ) !TransformerBlock {
        // Resolve matmul kernels at load time based on weight dtypes
        // For native fused QKV (Phi-style), q/k/v_proj are null
        const has_separate_qkv = weights.q_proj != null and weights.k_proj != null and weights.v_proj != null;

        if (std.process.hasEnvVar(allocator, "TOKAMINO_DEBUG_SHAPES") catch false) {
            if (has_separate_qkv) {
                const q = weights.q_proj.?;
                const k = weights.k_proj.?;
                const v = weights.v_proj.?;
                if (weights.w1) |w1| {
                    std.debug.print("weight dtypes: q={any} k={any} v={any} o={any} w1={any} w2={any} w3={any}\n", .{
                        q.dtype,              k.dtype,  v.dtype,
                        weights.o_proj.dtype, w1.dtype, weights.w2.?.dtype,
                        weights.w3.?.dtype,
                    });
                } else {
                    std.debug.print("weight dtypes: q={any} k={any} v={any} o={any} (MoE layer)\n", .{
                        q.dtype,              k.dtype, v.dtype,
                        weights.o_proj.dtype,
                    });
                }
                std.debug.print("weight shapes: q=[{},{}] k=[{},{}] v=[{},{}]\n", .{
                    q.shape[0], q.shape[1],
                    k.shape[0], k.shape[1],
                    v.shape[0], v.shape[1],
                });
            } else if (weights.fused.qkv_proj) |fq| {
                std.debug.print("weight dtypes: fused_qkv={any} o={any}\n", .{ fq.dtype, weights.o_proj.dtype });
                std.debug.print("weight shapes: fused_qkv=[{},{}]\n", .{ fq.shape[0], fq.shape[1] });
            }
        }

        // Get attention matmul kernel dtype - use fused QKV if available, else separate Q
        const qkv_dtype = if (weights.fused.qkv_proj) |fq|
            fq.dtype
        else if (weights.q_proj) |q|
            q.dtype
        else
            return error.MissingAttentionWeights;

        const matmul_qkv = try matmul.matmulKernel(qkv_dtype);
        const matmul_o = try matmul.matmulKernel(weights.o_proj.dtype);

        // Check if K/V have different dtypes than Q (e.g., Q4_K_M models mix Q4_K and Q6_K)
        // Only relevant when using separate projections
        const matmul_k: ?matmul.MatmulFn = if (has_separate_qkv and weights.k_proj.?.dtype != weights.q_proj.?.dtype)
            try matmul.matmulKernel(weights.k_proj.?.dtype)
        else
            null;
        const matmul_v: ?matmul.MatmulFn = if (has_separate_qkv and weights.v_proj.?.dtype != weights.q_proj.?.dtype)
            try matmul.matmulKernel(weights.v_proj.?.dtype)
        else
            null;

        const matmul_qkv_fused: ?matmul.MatmulFn = if (weights.fused.qkv_proj) |fq|
            try matmul.matmulKernel(fq.dtype)
        else
            null;

        // Build FFN layer - either SwiGLU or MoE
        const ffn_layer: FfnLayer = if (weights.moe_weights) |moe_w| blk: {
            break :blk .{ .moe_ffn = .{
                .allocator = allocator,
                .d_model = d_model,
                .d_ff = d_ff,
                .num_experts = moe_w.num_experts,
                .experts_per_token = moe_w.experts_per_token,
                .router_weight = moe_w.router_weight,
                .router_bias = moe_w.router_bias,
                .experts = moe_w.experts,
                .use_mxfp4 = moe_w.use_mxfp4,
                .use_gpt_oss_swiglu = runtime.use_gpt_oss_swiglu,
                .use_transposed_weights = runtime.use_transposed_mxfp4,
            } };
        } else blk: {
            const w2 = weights.w2 orelse return error.MissingFFNWeights;
            const fused_gate_up = weights.fused.gate_up;
            const matmul_gate_dtype = if (weights.w1) |w1| w1.dtype else if (fused_gate_up) |fg| fg.dtype else return error.MissingFFNWeights;
            const matmul_gate = try matmul.matmulKernel(matmul_gate_dtype);
            const matmul_down = try matmul.matmulKernel(w2.dtype);
            const matmul_gate_up: ?matmul.MatmulFn = if (weights.fused.gate_up) |fg|
                try matmul.matmulKernel(fg.dtype)
            else
                null;
            break :blk .{ .swiglu = .{
                .d_model = d_model,
                .d_ff = d_ff,
                .use_gelu = use_gelu,
                .use_gpt_oss_swiglu = runtime.use_gpt_oss_swiglu,
                .w1 = weights.w1,
                .w2 = w2,
                .w3 = weights.w3,
                .fused_gate_up = weights.fused.gate_up,
                .fused_gate_up_layout = weights.fused.gate_up_layout,
                .allocator = allocator,
                .matmul_gate = matmul_gate,
                .matmul_gate_up = matmul_gate_up,
                .matmul_down = matmul_down,
            } };
        };

        const pre_ffn_norm: ?norm.RMSNorm = if (weights.pre_ffn_norm) |w|
            .{ .weight = w, .dim = d_model, .eps = norm_eps, .weight_offset = runtime.weight_offset }
        else
            null;
        const post_ffn_norm: ?norm.RMSNorm = if (weights.post_ffn_norm) |w|
            .{ .weight = w, .dim = d_model, .eps = norm_eps, .weight_offset = runtime.weight_offset }
        else
            null;

        // Build result struct with fused weight storage
        const result = TransformerBlock{
            .ln1 = .{ .weight = weights.ln1_weight, .dim = d_model, .eps = norm_eps, .weight_offset = runtime.weight_offset },
            .attention = .{
                .d_model = d_model,
                .n_heads = n_heads,
                .n_kv_heads = n_kv_heads,
                .head_dim = head_dim,
                .max_seq_len = max_seq_len,
                .scale = attention_scale,
                .qk_norm_weight_offset = runtime.qk_norm_weight_offset,
                .sliding_window = weights.sliding_window,
                .q_proj = weights.q_proj,
                .k_proj = weights.k_proj,
                .v_proj = weights.v_proj,
                .o_proj = weights.o_proj,
                .fused_qkv = weights.fused.qkv_proj,
                .rope = weights.rope,
                .q_norm = weights.q_norm,
                .k_norm = weights.k_norm,
                .norm_eps = norm_eps,
                .allocator = allocator,
                .matmul_qkv = matmul_qkv,
                .matmul_k = matmul_k,
                .matmul_v = matmul_v,
                .matmul_qkv_fused = matmul_qkv_fused,
                .matmul_o = matmul_o,
                .q_bias = weights.q_bias,
                .k_bias = weights.k_bias,
                .v_bias = weights.v_bias,
                .o_bias = weights.o_bias,
                .sinks = weights.sinks,
            },
            .ln2 = .{ .weight = weights.ln2_weight, .dim = d_model, .eps = norm_eps, .weight_offset = runtime.weight_offset },
            .pre_ffn_norm = pre_ffn_norm,
            .post_ffn_norm = post_ffn_norm,
            .ffn_layer = ffn_layer,
            .residual_multiplier = residual_multiplier,
            .block_idx = block_idx,
            // Copy fused weights to extend their lifetime
            .fused_qkv_storage = weights.fused.qkv_proj,
            .fused_gate_up_storage = weights.fused.gate_up,
        };

        // Weight registry is populated later via initWeightRegistry() after the struct
        // is stored at its final heap location. This is necessary because storing pointers
        // to struct fields during init() would create dangling pointers when the struct
        // is returned by value.

        return result;
    }

    /// Initialize the weight registry after the struct is at its final location.
    /// Must be called after TransformerBlock is stored in a stable heap location.
    pub fn initWeightRegistry(self: *TransformerBlock, allocator: std.mem.Allocator, weights: BlockWeights) !void {
        const putAlias = struct {
            fn add(map: *std.StringHashMapUnmanaged(*const tensor.Tensor), alloc: std.mem.Allocator, name: []const u8, weight: *const tensor.Tensor) !void {
                if (map.get(name) == null) {
                    try map.put(alloc, name, weight);
                }
            }
        }.add;

        // Now we can safely store pointers to self.fused_*_storage fields
        if (self.fused_qkv_storage) |*fq| {
            try self.weight_registry.put(allocator, "qkv_proj", fq);
            try self.weight_registry.put(allocator, "self_attn.qkv_proj", fq);
        } else {
            if (weights.q_proj) |qp| try self.weight_registry.put(allocator, "q_proj", qp);
            if (weights.k_proj) |kp| try self.weight_registry.put(allocator, "k_proj", kp);
            if (weights.v_proj) |vp| try self.weight_registry.put(allocator, "v_proj", vp);
            if (weights.q_proj) |qp| try self.weight_registry.put(allocator, "self_attn.q_proj", qp);
            if (weights.k_proj) |kp| try self.weight_registry.put(allocator, "self_attn.k_proj", kp);
            if (weights.v_proj) |vp| try self.weight_registry.put(allocator, "self_attn.v_proj", vp);
        }
        try self.weight_registry.put(allocator, "o_proj", weights.o_proj);
        try self.weight_registry.put(allocator, "self_attn.o_proj", weights.o_proj);

        if (self.fused_gate_up_storage) |*fg| {
            try self.weight_registry.put(allocator, "gate_up_proj", fg);
            try self.weight_registry.put(allocator, "mlp.gate_up_proj", fg);
        } else {
            if (weights.w1) |w1| try self.weight_registry.put(allocator, "gate_proj", w1);
            if (weights.w3) |w3| try self.weight_registry.put(allocator, "up_proj", w3);
            if (weights.w1) |w1| try self.weight_registry.put(allocator, "mlp.gate_proj", w1);
            if (weights.w3) |w3| try self.weight_registry.put(allocator, "mlp.up_proj", w3);
        }
        if (weights.w2) |w2| try self.weight_registry.put(allocator, "down_proj", w2);
        if (weights.w2) |w2| try self.weight_registry.put(allocator, "mlp.down_proj", w2);

        try putAlias(&self.weight_registry, allocator, "input_layernorm.weight", weights.ln1_weight);
        try putAlias(&self.weight_registry, allocator, "post_attention_layernorm.weight", weights.ln2_weight);
        try putAlias(&self.weight_registry, allocator, "ln1.weight", weights.ln1_weight);
        try putAlias(&self.weight_registry, allocator, "ln2.weight", weights.ln2_weight);

        if (weights.pre_ffn_norm) |pre| {
            try putAlias(&self.weight_registry, allocator, "pre_feedforward_layernorm.weight", pre);
            try putAlias(&self.weight_registry, allocator, "pre_ffn_norm.weight", pre);
        }
        if (weights.post_ffn_norm) |post| {
            try putAlias(&self.weight_registry, allocator, "post_feedforward_layernorm.weight", post);
            try putAlias(&self.weight_registry, allocator, "post_ffn_norm.weight", post);
        }
        if (weights.q_norm) |q_norm| {
            try putAlias(&self.weight_registry, allocator, "q_norm.weight", q_norm);
            try putAlias(&self.weight_registry, allocator, "self_attn.q_norm.weight", q_norm);
        }
        if (weights.k_norm) |k_norm| {
            try putAlias(&self.weight_registry, allocator, "k_norm.weight", k_norm);
            try putAlias(&self.weight_registry, allocator, "self_attn.k_norm.weight", k_norm);
        }
    }
};

/// Build CPU kernel blocks from loader-stage `BlockWeights`.
/// This preserves existing behavior from the prior `TransformerModel.init` path,
/// but returns the blocks directly so callers can store them in `LoadedModel`.
pub fn buildBlocks(
    allocator: std.mem.Allocator,
    config: ModelConfig,
    runtime: tensor.ModelRuntime,
    block_weights: []const BlockWeights,
) ![]TransformerBlock {
    if (block_weights.len != config.n_layers) return error.InvalidLayerCount;

    const blocks = try allocator.alloc(TransformerBlock, @intCast(config.n_layers));
    errdefer allocator.free(blocks);

    const default_attn_scale = 1.0 / @sqrt(@as(f32, @floatFromInt(config.head_dim)));
    const attention_scale: f32 = if (config.attention_multiplier > 0)
        config.attention_multiplier
    else if (config.query_pre_attn_scalar > 0)
        1.0 / @sqrt(config.query_pre_attn_scalar)
    else
        default_attn_scale;

    const use_gelu = config.use_gelu;
    for (blocks, block_weights, 0..) |*dst, bw, layer_idx| {
        dst.* = try TransformerBlock.init(
            allocator,
            @intCast(config.d_model),
            @intCast(config.d_ff),
            @intCast(config.n_heads),
            @intCast(config.n_kv_groups),
            @intCast(config.head_dim),
            @intCast(config.max_seq_len),
            bw,
            config.norm_eps,
            runtime,
            config.residual_multiplier,
            attention_scale,
            use_gelu,
            layer_idx,
        );
        // Initialize weight registry now that block is in its final heap location
        try dst.initWeightRegistry(allocator, bw);
    }

    return blocks;
}

fn ensureSlice(allocator: std.mem.Allocator, buf: *[]f32, needed: usize) !void {
    if (buf.*.len >= needed) return;
    if (buf.*.len > 0) allocator.free(buf.*);
    buf.* = try allocator.alloc(f32, needed);
}
fn addInto(a: *const Tensor, b: *const Tensor, out: *Tensor) void {
    // Internal invariants: tensors must be f32 with matching sizes
    std.debug.assert(a.dtype == .f32 and b.dtype == .f32 and out.dtype == .f32);
    std.debug.assert(a.numel == b.numel and a.numel == out.numel);
    const a_data = a.asSlice(f32);
    const b_data = b.asSlice(f32);
    const o_data = out.asSlice(f32);
    const n = a.numel;

    // SIMD add
    const VEC = simd.f32_vec_len;
    var i: usize = 0;
    while (i + VEC - 1 < n) : (i += VEC) {
        const va: @Vector(VEC, f32) = a_data[i..][0..VEC].*;
        const vb: @Vector(VEC, f32) = b_data[i..][0..VEC].*;
        o_data[i..][0..VEC].* = va + vb;
    }
    // Scalar remainder
    while (i < n) : (i += 1) {
        o_data[i] = a_data[i] + b_data[i];
    }
}

pub fn addIntoScaled(a: *const Tensor, b: *const Tensor, out: *Tensor, scale: f32) void {
    if (scale == 1.0) return addInto(a, b, out);

    std.debug.assert(a.dtype == .f32 and b.dtype == .f32 and out.dtype == .f32);
    std.debug.assert(a.numel == b.numel and a.numel == out.numel);
    const a_data = a.asSlice(f32);
    const b_data = b.asSlice(f32);
    const o_data = out.asSlice(f32);
    const n = a.numel;

    const VEC = simd.f32_vec_len;
    const vscale: @Vector(VEC, f32) = @splat(scale);
    var i: usize = 0;
    while (i + VEC - 1 < n) : (i += VEC) {
        const va: @Vector(VEC, f32) = a_data[i..][0..VEC].*;
        const vb: @Vector(VEC, f32) = b_data[i..][0..VEC].*;
        o_data[i..][0..VEC].* = va + vb * vscale;
    }
    while (i < n) : (i += 1) {
        o_data[i] = a_data[i] + b_data[i] * scale;
    }
}

pub fn copyTensor(src: *const Tensor, dst: *Tensor) void {
    // Internal invariant: tensors must have matching data size
    std.debug.assert(src.data_size == dst.data_size);
    std.mem.copyForwards(u8, dst.data(), src.data());
}
