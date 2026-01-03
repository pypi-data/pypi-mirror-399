//! Core ops entrypoint
//!
//! This file is the "table of contents" for `src/compute/ops/`.
//! Keep it small and ordered so readers can discover where functionality lives.

// === Stride-aware ops for C API (TensorView-based) ===
pub const tensor_view = @import("tensor_view.zig");
pub const activation = @import("activation.zig");
pub const norm = @import("norm.zig");
pub const shape = @import("shape.zig");
pub const attention = @import("attention.zig");
pub const creation = @import("creation.zig");

// === Quantized ops ===
pub const mxfp4 = @import("mxfp4.zig");
pub const linear_quant = @import("linear_quant.zig");
pub const quant_rows = @import("quant_rows.zig");
pub const grouped_affine_quant = @import("grouped_affine_quant.zig");

// === Legacy internal ops (Tensor-based, for graph executor) ===
pub const matmul = @import("matmul.zig");
pub const matmul_prefill = @import("matmul_prefill.zig");

pub const math = @import("math.zig");
