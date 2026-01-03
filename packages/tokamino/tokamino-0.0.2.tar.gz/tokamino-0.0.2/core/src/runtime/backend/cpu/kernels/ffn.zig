//! CPU Feed-Forward Network Kernel
//! SwiGLU (Swish-Gated Linear Unit) implementation
//!
//! This module provides the feed-forward network computation for CPU inference.
//! Uses SwiGLU activation: output = (SiLU(x @ W1) * (x @ W3)) @ W2

const std = @import("std");
const tensor = @import("../../../../tensor.zig");
const matmul = @import("../../../../compute/ops/matmul.zig");
const math_ops = @import("../../../../compute/ops/math.zig");
const ops = @import("../../../../compute/ops/root.zig");
const tv = ops.tensor_view;

// =============================================================================
// GPT-OSS SwiGLU Activation (architecture-agnostic compute primitive)
// =============================================================================

/// GPT-OSS custom SwiGLU variant:
/// `swiglu(x_glu, x_linear) = (clip(x_glu,[-7,7]) * sigmoid(1.702*clip(x_glu))) * (clip(x_linear) + 1)`
inline fn gptOssSwiGluScalar(x_glu: f32, x_linear: f32) f32 {
    const alpha: f32 = 1.702;
    const limit: f32 = 7.0;
    const glu_clipped = if (x_glu > limit) limit else if (x_glu < -limit) -limit else x_glu;
    const lin_clipped = std.math.clamp(x_linear, -limit, limit);
    const sig = 1.0 / (1.0 + @exp(-alpha * glu_clipped));
    return (glu_clipped * sig) * (lin_clipped + 1.0);
}

/// Apply GPT-OSS SwiGLU over interleaved `[glu0, lin0, glu1, lin1, ...]` buffer.
fn gptOssSwiGluFromInterleaved(gate_up_interleaved: []const f32, hidden_out: []f32) void {
    std.debug.assert(gate_up_interleaved.len == hidden_out.len * 2);
    for (0..hidden_out.len) |i| {
        const glu = gate_up_interleaved[i * 2];
        const lin = gate_up_interleaved[i * 2 + 1];
        hidden_out[i] = gptOssSwiGluScalar(glu, lin);
    }
}

/// Apply GPT-OSS SwiGLU over split gate/up buffers.
fn gptOssSwiGluFromSplit(gate: []const f32, up: []const f32, hidden_out: []f32) void {
    std.debug.assert(gate.len == up.len and gate.len == hidden_out.len);
    for (0..hidden_out.len) |i| hidden_out[i] = gptOssSwiGluScalar(gate[i], up[i]);
}

const Tensor = tensor.Tensor;
const MatmulFn = matmul.MatmulFn;

pub const GateUpLayout = enum {
    concat,
    interleaved,
};

/// Scratch buffers for FFN computation.
/// Pre-allocated to avoid allocation during inference.
pub const FfnScratch = struct {
    gate: []f32 = &.{},
    gate_act: []f32 = &.{},
    up: []f32 = &.{},
    hidden: []f32 = &.{},

    pub fn deinit(self: *FfnScratch, allocator: std.mem.Allocator) void {
        if (self.gate.len > 0) allocator.free(self.gate);
        if (self.gate_act.len > 0) allocator.free(self.gate_act);
        if (self.up.len > 0) allocator.free(self.up);
        if (self.hidden.len > 0) allocator.free(self.hidden);
        self.* = .{};
    }
};

/// SwiGLU Feed-Forward Network layer.
/// Computes: output = (SiLU(x @ W1) * (x @ W3)) @ W2
pub const SwiGLU = struct {
    d_model: usize,
    d_ff: usize,
    use_gelu: bool = false,
    use_gpt_oss_swiglu: bool = false,
    w1: ?*const Tensor = null,
    w2: *const Tensor,
    w3: ?*const Tensor = null,
    fused_gate_up: ?Tensor = null,
    fused_gate_up_layout: GateUpLayout = .concat,
    allocator: std.mem.Allocator,
    // Baked matmul kernels - resolved at load time, no runtime dispatch
    matmul_gate: MatmulFn, // for w1, w3
    matmul_gate_up: ?MatmulFn = null, // for fused gate+up
    matmul_down: MatmulFn, // for w2

    pub fn forward(self: *const SwiGLU, x: *const Tensor, out: *Tensor, scratch: *FfnScratch) !void {
        // Internal invariants: tensor shapes must match model config
        std.debug.assert(x.n_dims == 3 and out.n_dims == 3);
        std.debug.assert(x.shape[0] == 1 and out.shape[0] == 1); // Only batch=1 supported
        const seq: usize = @intCast(x.shape[1]);
        std.debug.assert(x.shape[2] == self.d_model and out.shape[2] == self.d_model);

        const use_fused = if (self.fused_gate_up) |fg| blk: {
            if (fg.n_dims != 2) break :blk false;
            const a = fg.shape[0] == self.d_model and fg.shape[1] == self.d_ff * 2;
            const b = fg.shape[0] == self.d_ff * 2 and fg.shape[1] == self.d_model;
            break :blk a or b;
        } else false;
        const gate_len = if (use_fused) seq * (2 * self.d_ff) else seq * self.d_ff;

        try ensureSlice(self.allocator, &scratch.gate, gate_len);
        if (!use_fused) {
            try ensureSlice(self.allocator, &scratch.gate_act, seq * self.d_ff);
            try ensureSlice(self.allocator, &scratch.hidden, seq * self.d_ff);
            try ensureSlice(self.allocator, &scratch.up, seq * self.d_ff);
        } else {
            // For the common decode case (seq=1) and concat layout, we can compute the
            // activation in-place into the gate half and avoid packing into `hidden`.
            if (!(seq == 1 and self.fused_gate_up_layout == .concat)) {
                try ensureSlice(self.allocator, &scratch.hidden, seq * self.d_ff);
            }
        }

        const x_view = Tensor.view2D(x.data(), seq, self.d_model);
        var gate_view: Tensor = undefined;
        var up_view: Tensor = undefined;
        if (use_fused) {
            const fused_weight = self.fused_gate_up.?;
            const fused_kernel = self.matmul_gate_up orelse self.matmul_gate;
            var gate_up = Tensor.view2DSlice(scratch.gate[0 .. seq * (2 * self.d_ff)], seq, 2 * self.d_ff);
            fused_kernel(&x_view, &fused_weight, &gate_up);
            gate_view = gate_up;
            up_view = gate_up;
        } else {
            const w1 = self.w1 orelse return error.MissingFFNWeights;
            const w3 = self.w3 orelse return error.MissingFFNWeights;
            var gate_tmp = Tensor.view2DSlice(scratch.gate[0 .. seq * self.d_ff], seq, self.d_ff);
            var up_tmp = Tensor.view2DSlice(scratch.up, seq, self.d_ff);
            self.matmul_gate(&x_view, w1, &gate_tmp);
            self.matmul_gate(&x_view, w3, &up_tmp);
            gate_view = gate_tmp;
            up_view = up_tmp;
        }

        // Apply activation and elementwise multiply.
        const n = seq * self.d_ff;
        const VEC = math_ops.simd.f32_vec_len;
        var hidden_view: Tensor = undefined;
        if (use_fused) {
            const gate_up = gate_view.asSlice(f32);
            if (self.fused_gate_up_layout == .interleaved) {
                const hidden = scratch.hidden[0..n];
                for (0..seq) |t| {
                    const row = gate_up[t * (2 * self.d_ff) ..][0 .. 2 * self.d_ff];
                    const out_row = hidden[t * self.d_ff ..][0..self.d_ff];
                    if (self.use_gpt_oss_swiglu) {
                        gptOssSwiGluFromInterleaved(row, out_row);
                    } else if (self.use_gelu) {
                        for (0..self.d_ff) |i| out_row[i] = geluApprox(row[i * 2]) * row[i * 2 + 1];
                    } else {
                        for (0..self.d_ff) |i| {
                            const g = row[i * 2];
                            const u = row[i * 2 + 1];
                            const sig = 1.0 / (1.0 + math_ops.fastExpScalar(-g));
                            out_row[i] = (g * sig) * u;
                        }
                    }
                }
                hidden_view = Tensor.view2DSlice(hidden, seq, self.d_ff);
            } else {
                // Concat layout: [gate..., up...] per token.
                // Fast path for decode (seq=1): compute in-place into the gate half to
                // avoid packing into a separate buffer.
                if (seq == 1) {
                    const row = gate_up[0 .. 2 * self.d_ff];
                    const gate_row = row[0..self.d_ff];
                    const up_row = row[self.d_ff .. 2 * self.d_ff];
                    if (self.use_gpt_oss_swiglu) {
                        gptOssSwiGluFromSplit(gate_row, up_row, gate_row);
                    } else if (self.use_gelu) {
                        for (0..self.d_ff) |i| gate_row[i] = geluApprox(gate_row[i]) * up_row[i];
                    } else {
                        const one: @Vector(VEC, f32) = @splat(1.0);
                        var i: usize = 0;
                        while (i + VEC - 1 < self.d_ff) : (i += VEC) {
                            const g: @Vector(VEC, f32) = gate_row[i..][0..VEC].*;
                            const u: @Vector(VEC, f32) = up_row[i..][0..VEC].*;
                            const exp_neg = math_ops.fastExp(-g);
                            const sig = one / (one + exp_neg);
                            gate_row[i..][0..VEC].* = (g * sig) * u;
                        }
                        while (i < self.d_ff) : (i += 1) {
                            const g = gate_row[i];
                            const sig = 1.0 / (1.0 + math_ops.fastExpScalar(-g));
                            gate_row[i] = (g * sig) * up_row[i];
                        }
                    }
                    hidden_view = Tensor.view2DSlice(gate_row, 1, self.d_ff);
                } else {
                    const hidden = scratch.hidden[0..n];
                    for (0..seq) |t| {
                        const row = gate_up[t * (2 * self.d_ff) ..][0 .. 2 * self.d_ff];
                        const gate_row = row[0..self.d_ff];
                        const up_row = row[self.d_ff .. 2 * self.d_ff];
                        const out_row = hidden[t * self.d_ff ..][0..self.d_ff];
                        if (self.use_gpt_oss_swiglu) {
                            gptOssSwiGluFromSplit(gate_row, up_row, out_row);
                        } else if (self.use_gelu) {
                            for (0..self.d_ff) |i| out_row[i] = geluApprox(gate_row[i]) * up_row[i];
                        } else {
                            const one: @Vector(VEC, f32) = @splat(1.0);
                            var i: usize = 0;
                            while (i + VEC - 1 < self.d_ff) : (i += VEC) {
                                const g: @Vector(VEC, f32) = gate_row[i..][0..VEC].*;
                                const u: @Vector(VEC, f32) = up_row[i..][0..VEC].*;
                                const exp_neg = math_ops.fastExp(-g);
                                const sig = one / (one + exp_neg);
                                out_row[i..][0..VEC].* = (g * sig) * u;
                            }
                            while (i < self.d_ff) : (i += 1) {
                                const g = gate_row[i];
                                const sig = 1.0 / (1.0 + math_ops.fastExpScalar(-g));
                                out_row[i] = (g * sig) * up_row[i];
                            }
                        }
                    }
                    hidden_view = Tensor.view2DSlice(hidden, seq, self.d_ff);
                }
            }
        } else {
            var gate_act_view = Tensor.view2DSlice(scratch.gate_act, seq, self.d_ff);
            if (self.use_gelu) {
                const gate = gate_view.asSlice(f32);
                const gate_act = gate_act_view.asSlice(f32);
                for (gate, gate_act) |g, *ga| ga.* = geluApprox(g);
            } else if (self.use_gpt_oss_swiglu) {
                const gate = gate_view.asSlice(f32)[0..n];
                const up = up_view.asSlice(f32)[0..n];
                gptOssSwiGluFromSplit(gate, up, scratch.hidden[0..n]);
                hidden_view = Tensor.view2DSlice(scratch.hidden[0..n], seq, self.d_ff);
                var out_view = Tensor.view2DSlice(out.asSlice(f32), seq, self.d_model);
                self.matmul_down(&hidden_view, self.w2, &out_view);
                return;
            } else {
                const gate_tv = tv.fromTensor(Tensor, &gate_view);
                const gate_act_tv = tv.fromTensor(Tensor, &gate_act_view);
                ops.activation.silu(gate_act_tv, gate_tv);
            }

            // hidden = gate_act * up (SIMD)
            const gate_act_data = gate_act_view.asSlice(f32);
            const up_data = up_view.asSlice(f32);
            const hidden_data = scratch.hidden;
            var i: usize = 0;
            while (i + VEC - 1 < n) : (i += VEC) {
                const g: @Vector(VEC, f32) = gate_act_data[i..][0..VEC].*;
                const u: @Vector(VEC, f32) = up_data[i..][0..VEC].*;
                hidden_data[i..][0..VEC].* = g * u;
            }
            while (i < n) : (i += 1) {
                hidden_data[i] = gate_act_data[i] * up_data[i];
            }
            hidden_view = Tensor.view2DSlice(hidden_data, seq, self.d_ff);
        }

        var out_view = Tensor.view2DSlice(out.asSlice(f32), seq, self.d_model);
        self.matmul_down(&hidden_view, self.w2, &out_view);
    }
};

fn geluApprox(x: f32) f32 {
    // GELU approximation: x * 0.5 * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
    const sqrt_2_over_pi: f32 = 0.7978845608;
    const x3 = x * x * x;
    const inner = sqrt_2_over_pi * (x + 0.044715 * x3);
    return x * 0.5 * (1.0 + std.math.tanh(inner));
}

fn ensureSlice(allocator: std.mem.Allocator, buf: *[]f32, needed: usize) !void {
    if (buf.*.len >= needed) return;
    if (buf.*.len > 0) allocator.free(buf.*);
    buf.* = try allocator.alloc(f32, needed);
}
