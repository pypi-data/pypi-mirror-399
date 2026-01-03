//! CPU kernel exports
//!
//! This is a convenience entrypoint for CPU-only kernel types and scratch buffers.
//! It is intentionally separate from `src/compute/backend/cpu/root.zig` (the backend
//! object) to keep the backend API focused.

const blocks = @import("../block_kernels.zig");
const moe = @import("moe.zig");

// Block containers + scratch
pub const TransformerBlock = blocks.TransformerBlock;
pub const ScratchBuffer = blocks.ScratchBuffer;

// Attention / FFN kernel structs and scratch
pub const AttnTemp = blocks.AttnTemp;
pub const AttnCache = blocks.AttnCache;
pub const FfnScratch = blocks.FfnScratch;
pub const MultiHeadAttention = blocks.MultiHeadAttention;
pub const SwiGLU = blocks.SwiGLU;
pub const GateUpLayout = blocks.GateUpLayout;
pub const RMSNorm = blocks.RMSNorm;
pub const RoPE = blocks.RoPE;

// Common CPU kernel entrypoints
pub const rmsnormForward = blocks.rmsnormForward;
pub const gatherEmbeddings = blocks.gatherEmbeddings;

// MoE kernel exports
pub const MoEFFN = moe.MoEFFN;
pub const MoEScratch = moe.MoEScratch;
pub const ExpertWeights = moe.ExpertWeights;
