//! Fused attention helpers for CPU backend.
//! Provides utilities to project QKV with a single matmul and split views.

const std = @import("std");
const tensor = @import("../../../../tensor.zig");
const matmul = @import("../../../../compute/ops/matmul.zig");

const Tensor = tensor.Tensor;
const MatmulFn = matmul.MatmulFn;

/// Resulting views from a fused QKV projection.
pub const QkvViews = struct {
    q: Tensor,
    k: Tensor,
    v: Tensor,
};

/// Run one matmul against concatenated QKV weights and split into Q/K/V views.
/// After matmul, output is [seq, total_dim] where total_dim = q_dim + 2*kv_dim.
/// Each row contains [Q..., K..., V...] which we split along the feature dimension.
///
/// `qkv_buffer` must be at least 2 * seq * total_dim to allow for rearrangement.
/// Layout after this function:
///   [0 .. seq*q_dim]: Q (contiguous)
///   [seq*q_dim .. seq*(q_dim+kv_dim)]: K (contiguous)
///   [seq*(q_dim+kv_dim) .. seq*total_dim]: V (contiguous)
pub inline fn projectQkv(
    a: *const Tensor,
    fused_weight: *const Tensor,
    qkv_buffer: []f32,
    seq: usize,
    q_dim: usize,
    kv_dim: usize,
    kernel: MatmulFn,
) QkvViews {
    const total_dim = q_dim + 2 * kv_dim;
    const data_size = seq * total_dim;
    // We need space for matmul output + final rearranged output
    // Use second half of buffer for matmul, then copy to first half
    std.debug.assert(qkv_buffer.len >= 2 * data_size);

    // Matmul into second half of buffer
    const matmul_buf = qkv_buffer[data_size .. 2 * data_size];
    var fused_out = Tensor.view2DSlice(matmul_buf, seq, total_dim);
    kernel(a, fused_weight, &fused_out);

    // Rearrange: from [row0: Q0 K0 V0, row1: Q1 K1 V1, ...]
    //              to [Q0 Q1 ..., K0 K1 ..., V0 V1 ...]
    // Since we're copying from second half to first half, no overlap issues
    const out_buf = qkv_buffer[0..data_size];

    for (0..seq) |t| {
        const src_base = t * total_dim;

        // Copy Q
        const q_dst = t * q_dim;
        const q_src = src_base;
        @memcpy(out_buf[q_dst..][0..q_dim], matmul_buf[q_src..][0..q_dim]);

        // Copy K
        const k_dst = seq * q_dim + t * kv_dim;
        const k_src = src_base + q_dim;
        @memcpy(out_buf[k_dst..][0..kv_dim], matmul_buf[k_src..][0..kv_dim]);

        // Copy V
        const v_dst = seq * q_dim + seq * kv_dim + t * kv_dim;
        const v_src = src_base + q_dim + kv_dim;
        @memcpy(out_buf[v_dst..][0..kv_dim], matmul_buf[v_src..][0..kv_dim]);
    }

    return .{
        .q = Tensor.view2DSlice(out_buf[0 .. seq * q_dim], seq, q_dim),
        .k = Tensor.view2DSlice(out_buf[seq * q_dim .. seq * q_dim + seq * kv_dim], seq, kv_dim),
        .v = Tensor.view2DSlice(out_buf[seq * q_dim + seq * kv_dim .. seq * total_dim], seq, kv_dim),
    };
}
