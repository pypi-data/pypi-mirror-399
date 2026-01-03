//! CPU Normalization Kernels
//! RMS Normalization implementation
//!
//! This module provides normalization operations for CPU inference.

const std = @import("std");
const tensor = @import("../../../../tensor.zig");
const math = @import("../../../../compute/ops/math.zig");

const Tensor = tensor.Tensor;

/// RMS Normalization configuration.
pub const RMSNorm = struct {
    weight: *const Tensor,
    dim: usize,
    eps: f32,
    /// Offset added to weights before scaling (e.g., 1.0 for Gemma's (1+w) formulation)
    weight_offset: f32 = 0.0,
};

/// Apply RMS normalization: output = x * rsqrt(mean(x²) + eps) * weight
pub fn rmsnormForward(norm: *const RMSNorm, x: *const Tensor, out: *Tensor) void {
    // Internal invariants: tensor shapes must match model config
    std.debug.assert(x.dtype == .f32 and out.dtype == .f32);
    std.debug.assert(x.n_dims == 3 and out.n_dims == 3);
    std.debug.assert(x.shape[0] == out.shape[0] and x.shape[1] == out.shape[1] and x.shape[2] == out.shape[2]);
    std.debug.assert(x.shape[2] == norm.dim);

    const dim = norm.dim;
    const num_tokens: usize = @intCast(x.shape[0] * x.shape[1]);
    const w_dtype = norm.weight.dtype;
    const w_f32 = if (w_dtype == .f32) norm.weight.asSlice(f32) else null;
    const w_u16 = if (w_dtype == .bf16 or w_dtype == .f16) norm.weight.asSlice(u16) else null;

    math.rmsnormContiguous(
        out.asSlice(f32),
        x.asSlice(f32),
        w_f32,
        w_u16,
        w_dtype,
        num_tokens,
        dim,
        norm.eps,
        norm.weight_offset,
    );
}
