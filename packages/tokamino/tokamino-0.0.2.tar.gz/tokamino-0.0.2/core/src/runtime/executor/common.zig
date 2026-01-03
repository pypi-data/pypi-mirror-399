//! Executor common imports - kernel access for block execution.

const tensor_mod = @import("../../tensor.zig");
pub const matmul = @import("../../compute/ops/matmul.zig");
pub const dtype_mod = @import("../../dtype.zig");
pub const kernel_info = @import("../../inspect/kernel_info.zig");
pub const perf_estimate = @import("../../inspect/perf_estimate.zig");

// Backend kernels (CPU today)
pub const attn_kernel = @import("../backend/cpu/kernels/attention.zig");
pub const ffn_kernel = @import("../backend/cpu/kernels/ffn.zig");
pub const moe_kernel = @import("../backend/cpu/kernels/moe.zig");
pub const norm_kernel = @import("../backend/cpu/kernels/norm.zig");
pub const rope_kernel = @import("../backend/cpu/kernels/rope.zig");
pub const embedding_kernel = @import("../backend/cpu/kernels/embedding.zig");

pub const forward = @import("../backend/cpu/block_kernels.zig");
pub const block_kernels = forward; // Alias for clarity

// Common core types
pub const Tensor = tensor_mod.Tensor;
pub const OwnedTensor = tensor_mod.OwnedTensor;
pub const DType = dtype_mod.DType;
pub const MatmulFn = matmul.MatmulFn;
pub const Op = kernel_info.Op;

// Kernel struct types
pub const Attention = attn_kernel.MultiHeadAttention;
pub const RMSNorm = norm_kernel.RMSNorm;
pub const AttnTemp = attn_kernel.AttnTemp;
pub const AttnCache = attn_kernel.AttnCache;
pub const RoPE = rope_kernel.RoPE;
pub const FfnScratch = ffn_kernel.FfnScratch;
pub const MoeScratch = moe_kernel.MoEScratch;
pub const ScratchBuffer = forward.ScratchBuffer;
pub const FFNLayer = forward.FfnLayer;
pub const TransformerBlock = forward.TransformerBlock;

// Forward helpers
pub const addIntoScaled = forward.addIntoScaled;
pub const copyTensor = forward.copyTensor;
