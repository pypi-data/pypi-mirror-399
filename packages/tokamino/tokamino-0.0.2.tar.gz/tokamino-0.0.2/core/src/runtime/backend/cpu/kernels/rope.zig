//! CPU Rotary Position Embedding (RoPE) Kernel
//!
//! Re-exports RoPE from compute/ops/math.zig for organization.
//! The actual implementation lives in ops/math.zig alongside other math operations.

const ops = @import("../../../../compute/ops/math.zig");

// Re-export RoPE from ops/math.zig
pub const RoPE = ops.RoPE;
