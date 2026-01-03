//! Executor - transformer model execution.
//!
//! This module contains the execution logic that runs transformer models
//! using the compute kernels. It bridges model types (from model/) with
//! kernel implementations (from compute/backend/).
//!
//! Main types:
//! - Block: Transformer block with forward() execution
//! - Model: Complete transformer model

pub const common = @import("common.zig");
pub const trace = @import("trace.zig");

pub const Block = @import("block.zig").Block;
pub const Model = @import("model.zig").Model;

// Re-export model types for convenience
const model_types = @import("../../ops.zig");
pub const LayerOp = model_types.LayerOp;
pub const BufferId = model_types.BufferId;

// Re-export kernel types needed by callers
pub const Attention = common.Attention;
pub const RMSNorm = common.RMSNorm;
pub const FFNLayer = common.FFNLayer;
pub const AttnTemp = common.AttnTemp;
pub const AttnCache = common.AttnCache;
pub const ScratchBuffer = common.ScratchBuffer;
pub const TransformerBlock = common.TransformerBlock;

// Re-export layer types
const layers = @import("layers.zig");
pub const Linear = layers.Linear;
pub const Embedding = layers.Embedding;
