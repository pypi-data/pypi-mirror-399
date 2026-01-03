//! Mixture of Experts (MoE) FFN Layer
//!
//! Implements sparse MoE routing where each token selects top-k experts.
//! Used by GPT-OSS and similar architectures.

const std = @import("std");
const tensor = @import("../../../../tensor.zig");
const matmul = @import("../../../../compute/ops/matmul.zig");
const ops = @import("../../../../compute/ops/math.zig");
const dtype_mod = @import("../../../../dtype.zig");
const mxfp4 = @import("../../../../compute/ops/mxfp4.zig");

const Tensor = tensor.Tensor;
const MatmulFn = matmul.MatmulFn;

/// Scratch buffers for MoE computation
pub const MoEScratch = struct {
    router_logits: []f32 = &.{},
    expert_weights: []f32 = &.{}, // softmax weights for selected experts
    expert_indices: []u32 = &.{}, // indices of selected experts
    expert_outputs: []f32 = &.{}, // outputs from each expert
    gate_up: []f32 = &.{}, // intermediate for SwiGLU
    hidden: []f32 = &.{}, // intermediate hidden state

    pub fn deinit(self: *MoEScratch, allocator: std.mem.Allocator) void {
        if (self.router_logits.len > 0) allocator.free(self.router_logits);
        if (self.expert_weights.len > 0) allocator.free(self.expert_weights);
        if (self.expert_indices.len > 0) allocator.free(self.expert_indices);
        if (self.expert_outputs.len > 0) allocator.free(self.expert_outputs);
        if (self.gate_up.len > 0) allocator.free(self.gate_up);
        if (self.hidden.len > 0) allocator.free(self.hidden);
        self.* = .{};
    }
};

/// Expert weights for a single expert in MoE layer
pub const ExpertWeights = struct {
    /// Gate projection [d_model, d_ff] - for separate gate/up format
    gate_proj: ?Tensor = null,
    gate_scales: ?[]const u8 = null,
    gate_bias: ?[]const f32 = null,
    /// Up projection [d_model, d_ff] - for separate gate/up format
    up_proj: ?Tensor = null,
    up_scales: ?[]const u8 = null,
    up_bias: ?[]const f32 = null,
    /// Combined gate and up projection [d_model, 2*d_ff] - for fused format
    gate_up_proj: ?Tensor = null, // Can be MXFP4 quantized
    gate_up_scales: ?[]const u8 = null, // E8M0 scales for MXFP4
    gate_up_bias: ?[]const f32 = null,
    /// Down projection [d_ff, d_model]
    down_proj: Tensor,
    down_scales: ?[]const u8 = null,
    down_bias: ?[]const f32 = null,
};

/// Mixture of Experts FFN Layer
/// Implements: output = sum(expert_weight[i] * expert[i](x)) for top-k experts
pub const MoEFFN = struct {
    allocator: std.mem.Allocator,
    d_model: usize,
    d_ff: usize,
    num_experts: usize,
    experts_per_token: usize, // top-k

    /// Router weights [d_model, num_experts]
    router_weight: Tensor,
    router_bias: ?[]const f32 = null,

    /// Expert weights - indexed by expert id
    experts: []ExpertWeights,

    /// Whether experts use MXFP4 quantization
    use_mxfp4: bool = false,
    /// GPT-OSS uses a custom SwiGLU variant inside MoE experts.
    use_gpt_oss_swiglu: bool = false,
    /// GPT-OSS stores MXFP4 weights transposed (input @ weight instead of weight @ input)
    use_transposed_weights: bool = false,

    pub fn forward(self: *const MoEFFN, x: *const Tensor, out: *Tensor, scratch: *MoEScratch) !void {
        std.debug.assert(x.n_dims == 3 and out.n_dims == 3);
        std.debug.assert(x.shape[0] == 1 and out.shape[0] == 1);
        const seq: usize = @intCast(x.shape[1]);
        std.debug.assert(x.shape[2] == self.d_model and out.shape[2] == self.d_model);
        std.debug.assert(self.router_weight.dtype == .f32);
        std.debug.assert(self.router_weight.n_dims == 2);
        std.debug.assert(self.router_weight.shape[0] == self.d_model);
        std.debug.assert(self.router_weight.shape[1] == self.num_experts);

        const debug_moe = std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_MOE") catch false;
        if (debug_moe) {
            std.debug.print("MoE router_weight shape=[{},{}]\n", .{ self.router_weight.shape[0], self.router_weight.shape[1] });
        }

        // Allocate scratch buffers
        try ensureSlice(self.allocator, &scratch.router_logits, seq * self.num_experts);
        try ensureSlice(self.allocator, &scratch.expert_weights, seq * self.experts_per_token);
        try ensureSliceU32(self.allocator, &scratch.expert_indices, seq * self.experts_per_token);
        try ensureSlice(self.allocator, &scratch.expert_outputs, seq * self.d_model * self.experts_per_token);
        try ensureSlice(self.allocator, &scratch.gate_up, seq * 2 * self.d_ff);
        try ensureSlice(self.allocator, &scratch.hidden, seq * self.d_ff);

        const x_data = x.asSlice(f32);
        const out_data = out.asSlice(f32);

        // Zero output
        @memset(out_data, 0.0);

        // Process each token
        for (0..seq) |token_idx| {
            const token_input = x_data[token_idx * self.d_model ..][0..self.d_model];
            const token_output = out_data[token_idx * self.d_model ..][0..self.d_model];

            // 1. Compute router logits: [num_experts]
            const router_logits = scratch.router_logits[0..self.num_experts];
            computeRouterLogits(token_input, &self.router_weight, self.router_bias, router_logits);

            if (debug_moe and token_idx == 0) {
                var min_logit: f32 = router_logits[0];
                var max_logit: f32 = router_logits[0];
                for (router_logits) |l| {
                    if (l < min_logit) min_logit = l;
                    if (l > max_logit) max_logit = l;
                }
                std.debug.print("MoE router logits range: [{d:.4}, {d:.4}]\n", .{ min_logit, max_logit });
                std.debug.print("MoE input sample: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ token_input[0], token_input[1], token_input[2], token_input[3] });
                // Also print input range
                var min_in: f32 = token_input[0];
                var max_in: f32 = token_input[0];
                for (token_input) |v| {
                    if (v < min_in) min_in = v;
                    if (v > max_in) max_in = v;
                }
                std.debug.print("MoE full input range: [{d:.4}, {d:.4}]\n", .{ min_in, max_in });
            }

            // 2. Select top-k experts
            const expert_indices = scratch.expert_indices[token_idx * self.experts_per_token ..][0..self.experts_per_token];
            const expert_weights = scratch.expert_weights[token_idx * self.experts_per_token ..][0..self.experts_per_token];
            selectTopKExperts(router_logits, self.experts_per_token, expert_indices, expert_weights);

            if (debug_moe and token_idx == 0) {
                std.debug.print("MoE selected experts: ", .{});
                for (expert_indices, expert_weights) |idx, w| {
                    std.debug.print("{}({d:.3}) ", .{ idx, w });
                }
                std.debug.print("\n", .{});
            }

            // 3. Run selected experts and combine outputs
            for (0..self.experts_per_token) |k| {
                const expert_idx = expert_indices[k];
                const weight = expert_weights[k];

                if (expert_idx >= self.num_experts) continue;

                const expert = &self.experts[expert_idx];

                // Run expert FFN (SwiGLU)
                const expert_out = scratch.expert_outputs[k * self.d_model ..][0..self.d_model];
                try self.runExpert(expert, token_input, expert_out, scratch);

                if (debug_moe and token_idx == 0 and k == 0) {
                    var min_val: f32 = expert_out[0];
                    var max_val: f32 = expert_out[0];
                    for (expert_out) |v| {
                        if (v < min_val) min_val = v;
                        if (v > max_val) max_val = v;
                        if (std.math.isNan(v)) {
                            std.debug.print("MoE expert {} output contains NaN!\n", .{expert_idx});
                            break;
                        }
                    }
                    std.debug.print("MoE expert {} output range: [{d:.4}, {d:.4}]\n", .{ expert_idx, min_val, max_val });
                }

                // Accumulate weighted output
                for (0..self.d_model) |i| {
                    token_output[i] += weight * expert_out[i];
                }
            }

            if (debug_moe and token_idx == 0) {
                var min_out: f32 = token_output[0];
                var max_out: f32 = token_output[0];
                for (token_output) |v| {
                    if (v < min_out) min_out = v;
                    if (v > max_out) max_out = v;
                }
                std.debug.print("MoE combined output range: [{d:.4}, {d:.4}]\n", .{ min_out, max_out });
            }
        }
    }

    fn runExpert(
        self: *const MoEFFN,
        expert: *const ExpertWeights,
        input: []const f32,
        output: []f32,
        scratch: *MoEScratch,
    ) !void {
        const gate_up = scratch.gate_up[0 .. 2 * self.d_ff];
        const hidden = scratch.hidden[0..self.d_ff];
        const gate = gate_up[0..self.d_ff];
        const up = gate_up[self.d_ff..][0..self.d_ff];

        // Check if using separate gate/up projections or fused
        const use_separate = expert.gate_proj != null and expert.up_proj != null;

        if (use_separate) {
            // Separate gate and up projections (gpt-oss format)
            const gate_proj = expert.gate_proj.?;
            const up_proj = expert.up_proj.?;

            if (self.use_mxfp4 and expert.gate_scales != null) {
                const debug_moe = std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_MOE") catch false;
                const debug_bytes = std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_BYTES") catch false;
                if (debug_moe) {
                    // Debug scale values
                    const scales = expert.gate_scales.?;
                    var min_scale: u8 = scales[0];
                    var max_scale: u8 = scales[0];
                    for (scales) |s| {
                        if (s < min_scale) min_scale = s;
                        if (s > max_scale) max_scale = s;
                    }
                    std.debug.print("  MXFP4 transposed={}, scales range: [{}, {}] (E8M0), scales_len={}, weight_len={}\n", .{ self.use_transposed_weights, min_scale, max_scale, scales.len, gate_proj.data_size });
                    // Print first 16 weight bytes
                    std.debug.print("  First 16 weight bytes: ", .{});
                    for (gate_proj.data()[0..@min(16, gate_proj.data_size)]) |b| {
                        std.debug.print("0x{x:0>2} ", .{b});
                    }
                    std.debug.print("\n  First 4 scales: ", .{});
                    for (scales[0..@min(4, scales.len)]) |s| {
                        std.debug.print("0x{x:0>2} ", .{s});
                    }
                    std.debug.print("\n", .{});
                }
                if (debug_bytes) {
                    std.debug.print("  Expert gate_proj first 16 bytes: ", .{});
                    for (gate_proj.data()[0..@min(16, gate_proj.data_size)]) |b| {
                        std.debug.print("0x{x:0>2} ", .{b});
                    }
                    std.debug.print("\n  Expert gate_scales first 4: ", .{});
                    const scales = expert.gate_scales.?;
                    for (scales[0..@min(4, scales.len)]) |s| {
                        std.debug.print("0x{x:0>2} ", .{s});
                    }
                    std.debug.print("\n", .{});
                }

                // MXFP4 dequantize and matmul for gate
                if (self.use_transposed_weights) {
                    // GPT-OSS: weights are [in, out], use input @ weight
                    mxfp4.matmulF32Transposed(
                        input,
                        gate_proj.data(),
                        expert.gate_scales.?,
                        gate,
                        self.d_model,
                        self.d_ff,
                        if (expert.gate_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                    );
                } else {
                    mxfp4.matmulF32(
                        input,
                        gate_proj.data(),
                        expert.gate_scales.?,
                        gate,
                        self.d_model,
                        self.d_ff,
                        if (expert.gate_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                    );
                }

                if (debug_moe) {
                    var min_gate: f32 = gate[0];
                    var max_gate: f32 = gate[0];
                    for (gate) |g| {
                        if (g < min_gate) min_gate = g;
                        if (g > max_gate) max_gate = g;
                    }
                    std.debug.print("  gate proj output range: [{d:.4}, {d:.4}]\n", .{ min_gate, max_gate });
                }

                // MXFP4 dequantize and matmul for up
                if (self.use_transposed_weights) {
                    mxfp4.matmulF32Transposed(
                        input,
                        up_proj.data(),
                        expert.up_scales.?,
                        up,
                        self.d_model,
                        self.d_ff,
                        if (expert.up_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                    );
                } else {
                    mxfp4.matmulF32(
                        input,
                        up_proj.data(),
                        expert.up_scales.?,
                        up,
                        self.d_model,
                        self.d_ff,
                        if (expert.up_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                    );
                }

                if (debug_moe) {
                    var min_up: f32 = up[0];
                    var max_up: f32 = up[0];
                    for (up) |u| {
                        if (u < min_up) min_up = u;
                        if (u > max_up) max_up = u;
                    }
                    std.debug.print("  up proj output range: [{d:.4}, {d:.4}]\n", .{ min_up, max_up });
                }
            } else {
                // Standard matmul for gate
                var in_view = Tensor.view2DSlice(@constCast(input), 1, self.d_model);
                var gate_out = Tensor.view2DSlice(gate, 1, self.d_ff);
                const gate_kernel = matmul.matmulKernel(gate_proj.dtype) catch matmul.matmulF32;
                gate_kernel(&in_view, &gate_proj, &gate_out);
                if (expert.gate_bias) |bias| {
                    for (0..self.d_ff) |i| gate[i] += bias[i];
                }

                // Standard matmul for up
                var up_out = Tensor.view2DSlice(up, 1, self.d_ff);
                const up_kernel = matmul.matmulKernel(up_proj.dtype) catch matmul.matmulF32;
                up_kernel(&in_view, &up_proj, &up_out);
                if (expert.up_bias) |bias| {
                    for (0..self.d_ff) |i| up[i] += bias[i];
                }
            }
        } else if (expert.gate_up_proj != null) {
            // Fused gate+up projection
            const gate_up_proj = expert.gate_up_proj.?;
            if (self.use_mxfp4 and expert.gate_up_scales != null) {
                // MXFP4 dequantize and matmul
                // GPT-OSS uses contiguous format: [gate[0:d_ff], up[0:d_ff]]
                // The output gate_up buffer is already laid out as [gate, up]
                // so no de-interleaving needed - gate and up slices point to the right places
                if (self.use_transposed_weights) {
                    mxfp4.matmulF32Transposed(
                        input,
                        gate_up_proj.data(),
                        expert.gate_up_scales.?,
                        gate_up,
                        self.d_model,
                        2 * self.d_ff,
                        if (expert.gate_up_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                    );
                } else {
                    mxfp4.matmulF32(
                        input,
                        gate_up_proj.data(),
                        expert.gate_up_scales.?,
                        gate_up,
                        self.d_model,
                        2 * self.d_ff,
                        if (expert.gate_up_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                    );
                }
                // gate and up already point to gate_up[0..d_ff] and gate_up[d_ff..2*d_ff]
                // so no additional work needed
            } else {
                // Standard F32/F16/BF16 matmul
                var in_view = Tensor.view2DSlice(@constCast(input), 1, self.d_model);
                var out_view = Tensor.view2DSlice(gate_up, 1, 2 * self.d_ff);
                const kernel = matmul.matmulKernel(gate_up_proj.dtype) catch matmul.matmulF32;
                kernel(&in_view, &gate_up_proj, &out_view);

                if (expert.gate_up_bias) |bias| {
                    for (0..2 * self.d_ff) |i| gate_up[i] += bias[i];
                }
            }
        } else {
            @panic("Expert must have either gate_up_proj or separate gate_proj+up_proj");
        }

        if (self.use_gpt_oss_swiglu) {
            // GPT-OSS custom SwiGLU:
            // swiglu(x_linear, x_glu) = (x_glu_clipped * sigmoid(1.702*x_glu_clipped)) * (clip(x_linear,[-7,7]) + 1)
            const alpha: f32 = 1.702;
            const limit: f32 = 7.0;
            const debug_moe = std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_MOE") catch false;
            if (debug_moe) std.debug.print("  using gpt_oss_swiglu activation\n", .{});
            for (0..self.d_ff) |i| {
                const x_glu = gate[i];
                const x_linear = up[i];

                const x_glu_clipped = std.math.clamp(x_glu, -limit, limit);
                const x_linear_clipped = std.math.clamp(x_linear, -limit, limit);

                const glu_scaled = alpha * x_glu_clipped;
                const sig = 1.0 / (1.0 + @exp(-glu_scaled));
                const out_glu = x_glu_clipped * sig;
                hidden[i] = out_glu * (x_linear_clipped + 1.0);
            }
        } else {
            // Standard SwiGLU: SiLU(gate) * up
            for (0..self.d_ff) |i| {
                const g = gate[i];
                const sig = 1.0 / (1.0 + @exp(-g));
                hidden[i] = (g * sig) * up[i];
            }
        }

        const debug_moe = std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_MOE") catch false;
        if (debug_moe) {
            var min_h: f32 = hidden[0];
            var max_h: f32 = hidden[0];
            for (hidden) |h| {
                if (h < min_h) min_h = h;
                if (h > max_h) max_h = h;
            }
            std.debug.print("  SwiGLU hidden range: [{d:.4}, {d:.4}]\n", .{ min_h, max_h });
        }

        // Down projection
        if (self.use_mxfp4 and expert.down_scales != null) {
            if (debug_moe) {
                const scales = expert.down_scales.?;
                var min_scale: u8 = scales[0];
                var max_scale: u8 = scales[0];
                for (scales) |s| {
                    if (s < min_scale) min_scale = s;
                    if (s > max_scale) max_scale = s;
                }
                std.debug.print("  down_proj scales range: [{}, {}] (E8M0)\n", .{ min_scale, max_scale });
            }

            if (self.use_transposed_weights) {
                mxfp4.matmulF32Transposed(
                    hidden,
                    expert.down_proj.data(),
                    expert.down_scales.?,
                    output,
                    self.d_ff,
                    self.d_model,
                    if (expert.down_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                );
            } else {
                mxfp4.matmulF32(
                    hidden,
                    expert.down_proj.data(),
                    expert.down_scales.?,
                    output,
                    self.d_ff,
                    self.d_model,
                    if (expert.down_bias) |b| std.mem.bytesAsSlice(f32, std.mem.sliceAsBytes(b)) else null,
                );
            }

            if (debug_moe) {
                var min_out: f32 = output[0];
                var max_out: f32 = output[0];
                for (output) |o| {
                    if (o < min_out) min_out = o;
                    if (o > max_out) max_out = o;
                }
                std.debug.print("  down_proj output range: [{d:.4}, {d:.4}]\n", .{ min_out, max_out });
            }
        } else {
            var in_view = Tensor.view2DSlice(hidden, 1, self.d_ff);
            var out_view = Tensor.view2DSlice(output, 1, self.d_model);
            const kernel = matmul.matmulKernel(expert.down_proj.dtype) catch matmul.matmulF32;
            kernel(&in_view, &expert.down_proj, &out_view);

            if (expert.down_bias) |bias| {
                for (0..self.d_model) |i| output[i] += bias[i];
            }
        }
    }
};

/// Compute router logits: input @ router_weight + router_bias
fn computeRouterLogits(
    input: []const f32,
    router_weight: *const Tensor,
    router_bias: ?[]const f32,
    output: []f32,
) void {
    const d_model = input.len;
    const num_experts = output.len;

    // Simple matmul: output[i] = sum(input[j] * weight[j, i])
    // Weight shape: [d_model, num_experts]
    const weight_data = router_weight.asSlice(f32);

    for (0..num_experts) |i| {
        var sum: f32 = 0.0;
        for (0..d_model) |j| {
            sum += input[j] * weight_data[j * num_experts + i];
        }
        if (router_bias) |bias| {
            sum += bias[i];
        }
        output[i] = sum;
    }
}

/// Select top-k experts using partial sort and compute softmax weights
fn selectTopKExperts(
    logits: []const f32,
    k: usize,
    indices: []u32,
    weights: []f32,
) void {
    const n = logits.len;
    if (k > n) return;

    // Simple selection: find top-k by iterating k times
    var used = std.StaticBitSet(256).initEmpty();

    for (0..k) |ki| {
        var best_idx: usize = 0;
        var best_val: f32 = -std.math.inf(f32);

        for (0..n) |i| {
            if (!used.isSet(i) and logits[i] > best_val) {
                best_val = logits[i];
                best_idx = i;
            }
        }

        indices[ki] = @intCast(best_idx);
        weights[ki] = best_val;
        used.set(best_idx);
    }

    // Softmax over selected logits
    var max_logit: f32 = weights[0];
    for (weights[1..k]) |w| {
        if (w > max_logit) max_logit = w;
    }

    var sum_exp: f32 = 0.0;
    for (0..k) |i| {
        weights[i] = @exp(weights[i] - max_logit);
        sum_exp += weights[i];
    }

    for (0..k) |i| {
        weights[i] /= sum_exp;
    }
}

fn ensureSlice(allocator: std.mem.Allocator, buf: *[]f32, needed: usize) !void {
    if (buf.*.len >= needed) return;
    if (buf.*.len > 0) allocator.free(buf.*);
    buf.* = try allocator.alloc(f32, needed);
}

fn ensureSliceU32(allocator: std.mem.Allocator, buf: *[]u32, needed: usize) !void {
    if (buf.*.len >= needed) return;
    if (buf.*.len > 0) allocator.free(buf.*);
    buf.* = try allocator.alloc(u32, needed);
}
