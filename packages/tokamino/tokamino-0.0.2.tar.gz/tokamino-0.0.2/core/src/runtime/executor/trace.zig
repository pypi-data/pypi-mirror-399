//! Traced kernel execution wrappers.
//! Adds performance tracing around kernel calls.

const common = @import("common.zig");

const Tensor = common.Tensor;
const Attention = common.Attention;
const RMSNorm = common.RMSNorm;
const AttnCache = common.AttnCache;
const AttnTemp = common.AttnTemp;
const FFNLayer = common.FFNLayer;
const ScratchBuffer = common.ScratchBuffer;

const kernel_info = common.kernel_info;
const norm_kernel = common.norm_kernel;

pub fn rmsNormForwardTraced(norm: *const RMSNorm, x: *const Tensor, out: *Tensor) void {
    const t0 = kernel_info.traceTimestamp();
    if (kernel_info.isTraceEnabled()) {
        kernel_info.traceEnter("RMSNorm.forward", .{norm.dim});
    }

    norm_kernel.rmsnormForward(norm, x, out);

    if (kernel_info.isTraceEnabled()) {
        kernel_info.traceExit("RMSNorm.forward", t0);
    }
}

pub fn attentionForwardTraced(
    attn: *const Attention,
    x: *const Tensor,
    out: *Tensor,
    cache: *AttnCache,
    tmp: *AttnTemp,
    use_cache: bool,
) !void {
    const t0 = kernel_info.traceTimestamp();
    if (kernel_info.isTraceEnabled()) {
        kernel_info.traceEnter("Attention.forward", .{ attn.n_heads, attn.head_dim });
    }

    try attn.forward(x, out, cache, tmp, use_cache);

    if (kernel_info.isTraceEnabled()) {
        kernel_info.traceExit("Attention.forward", t0);
    }
}

pub fn ffnForwardTraced(ffn_layer: *const FFNLayer, x: *const Tensor, out: *Tensor, scratch: *ScratchBuffer) !void {
    const t0 = kernel_info.traceTimestamp();
    if (kernel_info.isTraceEnabled()) {
        switch (ffn_layer.*) {
            .swiglu => |s| kernel_info.traceEnter("MLP.forward", .{ s.d_model, s.d_ff }),
            .moe_ffn => |m| kernel_info.traceEnter("MoE.forward", .{ m.d_model, m.num_experts }),
        }
    }

    try ffn_layer.forward(x, out, scratch);

    if (kernel_info.isTraceEnabled()) {
        switch (ffn_layer.*) {
            .swiglu => kernel_info.traceExit("MLP.forward", t0),
            .moe_ffn => kernel_info.traceExit("MoE.forward", t0),
        }
    }
}
