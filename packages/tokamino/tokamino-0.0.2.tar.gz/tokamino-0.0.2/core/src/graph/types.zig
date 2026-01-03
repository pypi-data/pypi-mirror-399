//! Graph Types
//!
//! Core types for representing compute graphs from Python model definitions.
//! These types bridge Python's traced operations to Zig's execution engine.

const std = @import("std");
const model_types = @import("../ops.zig");

/// Input to an operation - either a tensor reference or a scalar value.
pub const OpInput = union(enum) {
    tensor: []const u8, // Tensor name (e.g., "weight", "x")
    scalar: f32, // Scalar value (e.g., 1.0)
};

/// Operation types that can appear in a compute graph.
/// High-level ops (norm, multihead_attention, mlp) are preferred.
/// Low-level ops (linear, split, etc.) are used with TOKAMINO_PRIMITIVES_ONLY=1.
pub const OpType = enum {
    // High-level fused ops (preferred)
    norm,
    multihead_attention,
    mlp,
    moe,

    // Residual connection
    add,

    // Low-level primitive ops (for debugging/custom architectures)
    mul,
    mean,
    pow,
    rsqrt,
    matmul,
    split,
    transpose,
    reshape,
    softmax,
    silu,
    gelu,
    embedding,
    linear,
    rope,
    triu,
    scaled_dot_product_attention,
};

/// A single operation in the compute graph.
/// Parsed from JSON (_graphs/*.json) and compiled to LayerOp for execution.
pub const Op = struct {
    op_type: OpType,
    name: ?[]const u8 = null, // For norm: "input_layernorm", etc.
    inputs: []const OpInput = &.{}, // Inputs to the operation
    outputs: []const []const u8 = &.{}, // Output tensor names for dataflow tracking

    // Op-specific parameters
    weight_offset: f32 = 0.0, // For norm: add to weight before scaling (e.g., Gemma)
    qk_norm: bool = false, // For attention: apply QK normalization
    fused_qkv: bool = false, // For attention: weights are fused [Q,K,V] (Phi-style)
    fused_gate_up: bool = false, // For mlp: weights are fused [gate,up] (Phi-style)
    sliding_window: ?i32 = null, // For attention
    activation: ?[]const u8 = null, // For ffn: "silu", "gelu", "relu"
    num_experts: i32 = 0, // For moe
    experts_per_token: i32 = 0, // For moe
    scale: f32 = 1.0, // For residual_add
    num_outputs: i32 = 0, // For split: number of output tensors
    dim: i32 = -1, // For split/softmax: dimension to operate on
    dim0: i32 = -1, // For transpose: first dimension
    dim1: i32 = -1, // For transpose: second dimension
    keepdim: bool = false, // For mean
    exponent: f32 = 1.0, // For pow
    shape: []const i32 = &.{}, // For reshape
    split_sizes: []const i32 = &.{}, // For split: sizes of each output
};

/// A registered architecture definition.
/// Contains the compute graph and metadata derived from analyzing it.
pub const Architecture = struct {
    name: []const u8,
    model_types: []const []const u8,

    // Compute graph ops
    block_ops: []const Op,
    pre_block_ops: []const Op = &.{},
    post_block_ops: []const Op = &.{},

    // Weight name mapping (optional)
    weight_map: ?std.StringHashMapUnmanaged([]const u8) = null,

    // Flags derived from analyzing block_ops
    has_qk_norm: bool = false,
    has_moe: bool = false,
    has_fused_qkv: bool = false, // Phi-style fused QKV projection
    has_fused_gate_up: bool = false, // Phi-style fused gate_up projection
    num_norms_per_block: u8 = 2,
    use_gelu: bool = false,
    norm_weight_offset: f32 = 0.0,
    explicit_qk_norm_ops: bool = false,

    // Pre-block flags
    embedding_multiplier: f32 = 1.0, // Scaling factor after embedding (e.g., sqrt(hidden_size) for Gemma)

    /// Compiled LayerOp program (lazily created on first use)
    compiled_program: ?[]const model_types.LayerOp = null,
};
