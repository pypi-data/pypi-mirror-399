const common = @import("common.zig");
const layers = @import("layers.zig");

const Tensor = common.Tensor;
const Attention = common.Attention;
const FFNLayer = common.FFNLayer;
const Op = common.Op;
const RMSNorm = common.RMSNorm;

const ffn_kernel = common.ffn_kernel;
const kernel_info = common.kernel_info;
const moe_kernel = common.moe_kernel;

const formatLinearLike = layers.formatLinearLike;
const formatRmsNormLike = layers.formatRmsNormLike;

fn formatSeqMatmulOp(
    writer: anytype,
    indent: usize,
    k: usize,
    n: usize,
    dtype: common.DType,
) !void {
    const op = Op{ .matmul = .{
        .m = .seq,
        .k = k,
        .n = n,
        .dtype = dtype,
        .kernel_name = kernel_info.matmulKernelName(dtype),
    } };
    try op.format(writer, indent);
}

fn describeLinearLine(
    writer: anytype,
    indent: usize,
    label: []const u8,
    weight: *const Tensor,
    bias: ?[]const f32,
    in_features: usize,
    out_features: usize,
) !void {
    try writer.writeByteNTimes(' ', indent);
    try writer.print("({s}): ", .{label});
    try formatLinearLike(writer, weight, bias, in_features, out_features);
    try writer.writeAll("\n");
}

fn describeRmsNormLine(
    writer: anytype,
    indent: usize,
    label: []const u8,
    dim: usize,
    eps: f32,
    weight_offset: f32,
) !void {
    try writer.writeByteNTimes(' ', indent);
    try writer.print("({s}): ", .{label});
    try formatRmsNormLike(writer, dim, eps, weight_offset);
    try writer.writeAll("\n");
}

// =============================================================================
// RMSNorm Layer
// =============================================================================

// `transformer.RMSNorm` is an alias to the CPU kernel type (see top of file).
// Introspection lives in helpers to avoid wrapper structs.

fn rmsNormFormatKernels(norm: *const RMSNorm, writer: anytype, indent: usize) !void {
    const rmsnorm_op = Op{ .rmsnorm = .{
        .dim = norm.dim,
        .eps = norm.eps,
    } };
    try rmsnorm_op.format(writer, indent);
}

pub fn rmsNormDescribe(norm: *const RMSNorm, writer: anytype, indent: usize, show_kernels: bool) !void {
    try writer.writeByteNTimes(' ', indent);
    try formatRmsNormLike(writer, norm.dim, norm.eps, norm.weight_offset);
    try writer.writeAll("\n");

    if (show_kernels) {
        try rmsNormFormatKernels(norm, writer, indent + 2);
    }
}

// =============================================================================
// Attention Module
// =============================================================================

// `transformer.Attention` is an alias to the CPU kernel type (see top of file).
// Introspection lives in helpers to avoid wrapper structs.

fn attentionFormatKernels(attn: *const Attention, writer: anytype, indent: usize) !void {
    const q_dim = attn.n_heads * attn.head_dim;
    const kv_dim = attn.n_kv_heads * attn.head_dim;

    // Q/K/V projections (may be fused for Phi-style models)
    if (attn.fused_qkv) |fq| {
        try formatSeqMatmulOp(writer, indent, attn.d_model, q_dim + 2 * kv_dim, fq.dtype);
    } else if (attn.q_proj != null and attn.k_proj != null and attn.v_proj != null) {
        try formatSeqMatmulOp(writer, indent, attn.d_model, q_dim, attn.q_proj.?.dtype);
        try formatSeqMatmulOp(writer, indent, attn.d_model, kv_dim, attn.k_proj.?.dtype);
        try formatSeqMatmulOp(writer, indent, attn.d_model, kv_dim, attn.v_proj.?.dtype);
    }

    // QK norm if present
    if (attn.q_norm != null) {
        const qk_norm_op = Op{ .rmsnorm = .{ .dim = attn.head_dim, .eps = attn.norm_eps } };
        try qk_norm_op.format(writer, indent);
    }

    // RoPE
    if (attn.rope) |r| {
        const rope_op = Op{ .rope = .{ .dim = attn.head_dim, .theta = r.theta } };
        try rope_op.format(writer, indent);
    }

    // SDPA
    const sdpa_op = Op{ .sdpa = .{
        .n_heads = attn.n_heads,
        .n_kv_heads = attn.n_kv_heads,
        .head_dim = attn.head_dim,
        .scale = attn.scale,
        .causal = true,
    } };
    try sdpa_op.format(writer, indent);

    // O projection
    try formatSeqMatmulOp(writer, indent, q_dim, attn.d_model, attn.o_proj.dtype);
}

pub fn attentionDescribe(attn: *const Attention, writer: anytype, indent: usize, show_kernels: bool) !void {
    const q_dim = attn.n_heads * attn.head_dim;
    const kv_dim = attn.n_kv_heads * attn.head_dim;

    try writer.writeByteNTimes(' ', indent);
    try writer.print("Attention(n_heads={}, n_kv_heads={}, head_dim={})\n", .{
        attn.n_heads,
        attn.n_kv_heads,
        attn.head_dim,
    });

    // Sub-modules (may be fused for Phi-style models)
    if (attn.fused_qkv) |fq| {
        try writer.writeByteNTimes(' ', indent + 2);
        try writer.print("(qkv_proj): Linear(in={}, out={}, dtype={s})\n", .{ attn.d_model, q_dim + 2 * kv_dim, @tagName(fq.dtype) });
    } else {
        if (attn.q_proj) |qp| try describeLinearLine(writer, indent + 2, "q_proj", qp, attn.q_bias, attn.d_model, q_dim);
        if (attn.k_proj) |kp| try describeLinearLine(writer, indent + 2, "k_proj", kp, attn.k_bias, attn.d_model, kv_dim);
        if (attn.v_proj) |vp| try describeLinearLine(writer, indent + 2, "v_proj", vp, attn.v_bias, attn.d_model, kv_dim);
    }
    try describeLinearLine(writer, indent + 2, "o_proj", attn.o_proj, attn.o_bias, q_dim, attn.d_model);

    if (attn.q_norm != null) {
        try describeRmsNormLine(writer, indent + 2, "q_norm", attn.head_dim, attn.norm_eps, attn.qk_norm_weight_offset);
    }
    if (attn.k_norm != null) {
        try describeRmsNormLine(writer, indent + 2, "k_norm", attn.head_dim, attn.norm_eps, attn.qk_norm_weight_offset);
    }

    if (show_kernels) {
        try writer.writeByteNTimes(' ', indent + 2);
        try writer.writeAll("Kernels:\n");
        try attentionFormatKernels(attn, writer, indent + 4);
    }
}

// =============================================================================
// MLP Module
// =============================================================================

// Dense FFN (SwiGLU/GELU) introspection helpers.

fn swigluFormatKernels(layer: *const ffn_kernel.SwiGLU, writer: anytype, indent: usize) !void {
    if (layer.fused_gate_up) |*fused| {
        try formatSeqMatmulOp(writer, indent, layer.d_model, layer.d_ff * 2, fused.dtype);
    } else {
        const w1 = layer.w1 orelse return;
        const w3 = layer.w3 orelse return;

        try formatSeqMatmulOp(writer, indent, layer.d_model, layer.d_ff, w1.dtype);
        try formatSeqMatmulOp(writer, indent, layer.d_model, layer.d_ff, w3.dtype);
    }

    // Activation
    if (layer.use_gelu) {
        const gelu_op = Op{ .gelu = .{} };
        try gelu_op.format(writer, indent);
    } else {
        const silu_op = Op{ .silu = .{} };
        try silu_op.format(writer, indent);
    }

    // Multiply gate * up
    const mul_op = Op{ .mul = .{} };
    try mul_op.format(writer, indent);

    // Down projection
    try formatSeqMatmulOp(writer, indent, layer.d_ff, layer.d_model, layer.w2.dtype);
}

fn swigluDescribe(layer: *const ffn_kernel.SwiGLU, writer: anytype, indent: usize, show_kernels: bool) !void {
    try writer.writeByteNTimes(' ', indent);

    const activation: []const u8 = if (layer.use_gelu) "GELU" else "SiLU";
    try writer.print("MLP(intermediate_size={}, activation={s})\n", .{ layer.d_ff, activation });

    if (layer.fused_gate_up) |*fused| {
        try describeLinearLine(writer, indent + 2, "gate_up_proj", fused, null, layer.d_model, layer.d_ff * 2);
    } else {
        const w1 = layer.w1 orelse @panic("MLP missing w1 weight");
        const w3 = layer.w3 orelse @panic("MLP missing w3 weight");

        try describeLinearLine(writer, indent + 2, "gate_proj", w1, null, layer.d_model, layer.d_ff);
        try describeLinearLine(writer, indent + 2, "up_proj", w3, null, layer.d_model, layer.d_ff);
    }

    try describeLinearLine(writer, indent + 2, "down_proj", layer.w2, null, layer.d_ff, layer.d_model);

    if (show_kernels) {
        try writer.writeByteNTimes(' ', indent + 2);
        try writer.writeAll("Kernels:\n");
        try swigluFormatKernels(layer, writer, indent + 4);
    }
}

// =============================================================================
// MoE Module (Mixture of Experts)
// =============================================================================

// MoE introspection helpers.

fn moeFormatKernels(layer: *const moe_kernel.MoEFFN, writer: anytype, indent: usize) !void {
    const route_op = Op{ .moe_route = .{
        .num_experts = layer.num_experts,
        .experts_per_token = layer.experts_per_token,
    } };
    try route_op.format(writer, indent);

    try writer.writeByteNTimes(' ', indent);
    try writer.print("└─ expert_gate(x[seq, {}]) → [seq, {}] (×{} experts)\n", .{
        layer.d_model,
        layer.d_ff,
        layer.experts_per_token,
    });

    try writer.writeByteNTimes(' ', indent);
    try writer.print("└─ expert_up(x[seq, {}]) → [seq, {}]\n", .{ layer.d_model, layer.d_ff });

    const silu_op = Op{ .silu = .{} };
    try silu_op.format(writer, indent);

    const mul_op = Op{ .mul = .{} };
    try mul_op.format(writer, indent);

    try writer.writeByteNTimes(' ', indent);
    try writer.print("└─ expert_down(x[seq, {}]) → [seq, {}]\n", .{ layer.d_ff, layer.d_model });

    try writer.writeByteNTimes(' ', indent);
    try writer.writeAll("└─ weighted_sum(expert_outputs, routing_weights)\n");
}

fn moeDescribe(layer: *const moe_kernel.MoEFFN, writer: anytype, indent: usize, show_kernels: bool) !void {
    try writer.writeByteNTimes(' ', indent);
    try writer.print("MoE(num_experts={}, experts_per_token={}, d_ff={})\n", .{
        layer.num_experts,
        layer.experts_per_token,
        layer.d_ff,
    });

    try writer.writeByteNTimes(' ', indent + 2);
    try writer.print("(router): Linear(in={}, out={})\n", .{ layer.d_model, layer.num_experts });

    try writer.writeByteNTimes(' ', indent + 2);
    try writer.print("(experts): {}× FFN(d_model={}, d_ff={})\n", .{
        layer.num_experts,
        layer.d_model,
        layer.d_ff,
    });

    if (show_kernels) {
        try writer.writeByteNTimes(' ', indent + 2);
        try writer.writeAll("Kernels:\n");
        try moeFormatKernels(layer, writer, indent + 4);
    }
}

pub fn ffnDescribe(layer: *const FFNLayer, writer: anytype, indent: usize, show_kernels: bool) !void {
    switch (layer.*) {
        .swiglu => |*m| try swigluDescribe(m, writer, indent, show_kernels),
        .moe_ffn => |*e| try moeDescribe(e, writer, indent, show_kernels),
    }
}
