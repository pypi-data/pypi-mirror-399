//! Generic MoE Weight Loader
//!
//! Provides hooks for loading Mixture of Experts weights from SafeTensors.
//! Supports both separate gate/up projections and fused gate_up_proj formats.
//! Used by GPT-OSS and similar MoE architectures.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const dtype = @import("../../dtype.zig");
const block_kernels = @import("../../runtime/backend/cpu/block_kernels.zig");
const st_loader = @import("../safetensors/root.zig");
const weights = @import("weights.zig");
const moe = @import("../../runtime/backend/cpu/kernels/moe.zig");

// MoE weight naming patterns
const router_weight_fmt = "model.layers.{d}.mlp.router.weight";
const router_bias_fmt = "model.layers.{d}.mlp.router.bias";
const experts_gate_up_proj_blocks_fmt = "model.layers.{d}.mlp.experts.gate_up_proj_blocks";
const experts_gate_up_proj_scales_fmt = "model.layers.{d}.mlp.experts.gate_up_proj_scales";
const experts_gate_up_proj_bias_fmt = "model.layers.{d}.mlp.experts.gate_up_proj_bias";
const experts_down_proj_blocks_fmt = "model.layers.{d}.mlp.experts.down_proj_blocks";
const experts_down_proj_scales_fmt = "model.layers.{d}.mlp.experts.down_proj_scales";
const experts_down_proj_bias_fmt = "model.layers.{d}.mlp.experts.down_proj_bias";

// Separate gate/up format
const experts_gate_proj_weight_fmt = "model.layers.{d}.mlp.experts.gate_proj.weight";
const experts_gate_proj_scales_fmt = "model.layers.{d}.mlp.experts.gate_proj.scales";
const experts_gate_proj_bias_fmt = "model.layers.{d}.mlp.experts.gate_proj.bias";
const experts_up_proj_weight_fmt = "model.layers.{d}.mlp.experts.up_proj.weight";
const experts_up_proj_scales_fmt = "model.layers.{d}.mlp.experts.up_proj.scales";
const experts_up_proj_bias_fmt = "model.layers.{d}.mlp.experts.up_proj.bias";
const experts_down_proj_weight_fmt = "model.layers.{d}.mlp.experts.down_proj.weight";
const experts_down_proj_scales_separate_fmt = "model.layers.{d}.mlp.experts.down_proj.scales";
const experts_down_proj_bias_separate_fmt = "model.layers.{d}.mlp.experts.down_proj.bias";

/// Detect MoE settings from weights when config.json omits them.
pub fn inferMoEFromWeights(st: *st_loader.UnifiedSafeTensors, config: *tensor.ModelConfig) void {
    if (config.num_experts > 0) return;

    // Try fused format first
    var buf: [256]u8 = undefined;
    const gate_up_blocks_name = std.fmt.bufPrint(&buf, experts_gate_up_proj_blocks_fmt, .{0}) catch return;
    const t = st.getTensor(gate_up_blocks_name, null) catch {
        // Try separate format
        const gate_name = std.fmt.bufPrint(&buf, experts_gate_proj_weight_fmt, .{0}) catch return;
        const t2 = st.getTensor(gate_name, null) catch return;
        if (t2.n_dims <= 0) return;
        config.num_experts = @intCast(t2.shape[0]);
        if (config.experts_per_token <= 0) config.experts_per_token = 4;
        return;
    };

    if (t.n_dims <= 0) return;
    config.num_experts = @intCast(t.shape[0]);
    if (config.experts_per_token <= 0) config.experts_per_token = 4;

    if (std.posix.getenv("TOKAMINO_DEBUG_LOADER_MOE") != null) {
        std.debug.print(
            "Inferred MoE from weights: num_experts={} experts_per_token={}\n",
            .{ config.num_experts, config.experts_per_token },
        );
    }
}

/// Load MoE weights for a layer. Returns null if this isn't an MoE model.
pub fn maybeLoadMoEWeights(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    _: []u8, // Unused - we use our own larger buffer
    layer: usize,
    config: tensor.ModelConfig,
) !?*block_kernels.MoEWeights {
    if (config.num_experts <= 0) return null;
    // Use a larger local buffer for MoE weight names
    var local_buf: [512]u8 = undefined;
    return try loadMoEWeights(allocator, st, &local_buf, layer, config);
}

fn loadMoEWeights(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    buf: *[512]u8,
    layer: usize,
    config: tensor.ModelConfig,
) !*block_kernels.MoEWeights {
    const debug_shapes = std.posix.getenv("TOKAMINO_DEBUG_SHAPES") != null;
    if (debug_shapes) std.debug.print("  loadMoEWeights: layer={}, num_experts={}, experts_per_token={}, quant_method={}\n", .{
        layer, config.num_experts, config.experts_per_token, config.quant_method,
    });

    const num_experts: usize = @intCast(config.num_experts);
    const experts_per_token: usize = @intCast(config.experts_per_token);

    // Load router weights
    const router_name = try std.fmt.bufPrint(buf, router_weight_fmt, .{layer});
    if (debug_shapes) std.debug.print("    loading router: '{s}'\n", .{router_name});
    const router_weight_oriented = try weights.orientWeight(allocator, st, router_name, @intCast(config.d_model), config);

    // Router logits kernel expects [in, out] = [d_model, num_experts] in f32.
    const router_weight_f32_unoriented = try weights.ensureF32(allocator, router_weight_oriented);
    const router_weight = try weights.orientWeightF32(allocator, router_weight_f32_unoriented, @intCast(config.d_model));
    if (debug_shapes) std.debug.print("    router loaded: shape=[{},{}], dtype={}\n", .{ router_weight.shape[0], router_weight.shape[1], router_weight.dtype });

    // Load router bias (optional)
    const router_bias_name = try std.fmt.bufPrint(buf, router_bias_fmt, .{layer});
    const router_bias = tryLoadTensorF32(allocator, st, router_bias_name);

    const use_mxfp4 = config.quant_method == .mxfp4;
    const experts = if (use_mxfp4)
        try loadMxfp4Experts(allocator, st, buf, layer, config)
    else
        return error.NonMxfp4MoeNotSupported;

    const moe_weights = try allocator.create(block_kernels.MoEWeights);
    moe_weights.* = .{
        .router_weight = router_weight,
        .router_bias = router_bias,
        .experts = experts,
        .num_experts = num_experts,
        .experts_per_token = experts_per_token,
        .use_mxfp4 = use_mxfp4,
    };

    return moe_weights;
}

fn loadMxfp4Experts(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    buf: *[512]u8,
    layer: usize,
    config: tensor.ModelConfig,
) ![]moe.ExpertWeights {
    const num_experts: usize = @intCast(config.num_experts);
    if (num_experts == 0) return error.InvalidValue;

    var experts = try allocator.alloc(moe.ExpertWeights, num_experts);
    errdefer allocator.free(experts);

    const debug_shapes = std.posix.getenv("TOKAMINO_DEBUG_SHAPES") != null;

    // Try fused gate_up_proj blocks/scales format first
    const gate_up_blocks_name = try std.fmt.bufPrint(buf, experts_gate_up_proj_blocks_fmt, .{layer});
    const all_gate_up_blocks = st.getTensor(gate_up_blocks_name, null) catch {
        // Try separate gate/up format
        return try loadSeparateExperts(allocator, st, buf, layer, config, experts);
    };

    if (debug_shapes) std.debug.print("    loading MXFP4 fused format: '{s}'\n", .{gate_up_blocks_name});

    const gate_up_scales_name = try std.fmt.bufPrint(buf, experts_gate_up_proj_scales_fmt, .{layer});
    const all_gate_up_scales = try st.getTensor(gate_up_scales_name, null);

    const down_blocks_name = try std.fmt.bufPrint(buf, experts_down_proj_blocks_fmt, .{layer});
    const all_down_blocks = try st.getTensor(down_blocks_name, null);

    const down_scales_name = try std.fmt.bufPrint(buf, experts_down_proj_scales_fmt, .{layer});
    const all_down_scales = try st.getTensor(down_scales_name, null);

    const gate_up_bias_name = try std.fmt.bufPrint(buf, experts_gate_up_proj_bias_fmt, .{layer});
    const down_bias_name = try std.fmt.bufPrint(buf, experts_down_proj_bias_fmt, .{layer});

    const all_gate_up_bias = tryLoadTensorF32(allocator, st, gate_up_bias_name);
    const all_down_bias = tryLoadTensorF32(allocator, st, down_bias_name);

    const gate_up_expert_bytes = all_gate_up_blocks.data_size / num_experts;
    const down_expert_bytes = all_down_blocks.data_size / num_experts;
    const gate_up_scale_expert_size = all_gate_up_scales.data_size / num_experts;
    const down_scale_expert_size = all_down_scales.data_size / num_experts;
    const gate_up_bias_expert_size: usize = if (all_gate_up_bias) |b| b.len / num_experts else 0;
    const down_bias_expert_size: usize = if (all_down_bias) |b| b.len / num_experts else 0;

    for (0..num_experts) |e| {
        const gate_up_bytes_per_row: usize = gate_up_expert_bytes / @as(usize, @intCast(config.d_ff * 2));
        const down_bytes_per_row: usize = down_expert_bytes / @as(usize, @intCast(config.d_model));
        const gate_up_data = all_gate_up_blocks.data()[e * gate_up_expert_bytes ..][0..gate_up_expert_bytes];
        const down_data = all_down_blocks.data()[e * down_expert_bytes ..][0..down_expert_bytes];
        experts[e] = .{
            .gate_up_proj = tensor.Tensor.view(gate_up_data.ptr, &.{ @intCast(config.d_ff * 2), gate_up_bytes_per_row }, .mxfp4, gate_up_expert_bytes),
            .gate_up_scales = all_gate_up_scales.data()[e * gate_up_scale_expert_size ..][0..gate_up_scale_expert_size],
            .gate_up_bias = if (all_gate_up_bias) |b| b[e * gate_up_bias_expert_size ..][0..gate_up_bias_expert_size] else null,
            .down_proj = tensor.Tensor.view(down_data.ptr, &.{ @intCast(config.d_model), down_bytes_per_row }, .mxfp4, down_expert_bytes),
            .down_scales = all_down_scales.data()[e * down_scale_expert_size ..][0..down_scale_expert_size],
            .down_bias = if (all_down_bias) |b| b[e * down_bias_expert_size ..][0..down_bias_expert_size] else null,
        };
    }

    return experts;
}

fn loadSeparateExperts(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    buf: *[512]u8,
    layer: usize,
    config: tensor.ModelConfig,
    experts: []moe.ExpertWeights,
) ![]moe.ExpertWeights {
    const num_experts = experts.len;
    const debug_shapes = std.posix.getenv("TOKAMINO_DEBUG_SHAPES") != null;

    const gate_weight_name = try std.fmt.bufPrint(buf, experts_gate_proj_weight_fmt, .{layer});
    if (debug_shapes) std.debug.print("    loading MXFP4 separate format: '{s}'\n", .{gate_weight_name});

    const all_gate_weights = try st.getTensor(gate_weight_name, null);
    const gate_scales_name = try std.fmt.bufPrint(buf, experts_gate_proj_scales_fmt, .{layer});
    const all_gate_scales = try st.getTensor(gate_scales_name, null);

    const up_weight_name = try std.fmt.bufPrint(buf, experts_up_proj_weight_fmt, .{layer});
    const all_up_weights = try st.getTensor(up_weight_name, null);
    const up_scales_name = try std.fmt.bufPrint(buf, experts_up_proj_scales_fmt, .{layer});
    const all_up_scales = try st.getTensor(up_scales_name, null);

    const down_weight_name = try std.fmt.bufPrint(buf, experts_down_proj_weight_fmt, .{layer});
    const all_down_weights = try st.getTensor(down_weight_name, null);
    const down_scales_name = try std.fmt.bufPrint(buf, experts_down_proj_scales_separate_fmt, .{layer});
    const all_down_scales = try st.getTensor(down_scales_name, null);

    // Load biases (optional) - must load immediately after bufPrint since buf is reused
    const gate_bias_slice = try std.fmt.bufPrint(buf, experts_gate_proj_bias_fmt, .{layer});
    const all_gate_bias = tryLoadTensorF32(allocator, st, gate_bias_slice);

    const up_bias_slice = try std.fmt.bufPrint(buf, experts_up_proj_bias_fmt, .{layer});
    const all_up_bias = tryLoadTensorF32(allocator, st, up_bias_slice);

    const down_bias_slice = try std.fmt.bufPrint(buf, experts_down_proj_bias_separate_fmt, .{layer});
    const all_down_bias = tryLoadTensorF32(allocator, st, down_bias_slice);

    if (debug_shapes) {
        if (all_gate_bias) |b| {
            std.debug.print("    gate_bias loaded: len={}, first 4 values: {d:.6} {d:.6} {d:.6} {d:.6}\n", .{
                b.len, b[0], b[1], b[2], b[3],
            });
        }
    }

    const gate_expert_bytes = all_gate_weights.data_size / num_experts;
    const up_expert_bytes = all_up_weights.data_size / num_experts;
    const down_expert_bytes = all_down_weights.data_size / num_experts;

    const gate_scale_expert_size = all_gate_scales.data().len / num_experts;
    const up_scale_expert_size = all_up_scales.data().len / num_experts;
    const down_scale_expert_size = all_down_scales.data().len / num_experts;
    const gate_bias_expert_size: usize = if (all_gate_bias) |b| b.len / num_experts else 0;
    const up_bias_expert_size: usize = if (all_up_bias) |b| b.len / num_experts else 0;
    const down_bias_expert_size: usize = if (all_down_bias) |b| b.len / num_experts else 0;

    for (0..num_experts) |e| {
        const gate_bytes_per_row: usize = gate_expert_bytes / @as(usize, @intCast(config.d_ff));
        const up_bytes_per_row: usize = up_expert_bytes / @as(usize, @intCast(config.d_ff));
        const down_bytes_per_row: usize = down_expert_bytes / @as(usize, @intCast(config.d_model));
        const gate_slice = all_gate_weights.data()[e * gate_expert_bytes ..][0..gate_expert_bytes];
        const up_slice = all_up_weights.data()[e * up_expert_bytes ..][0..up_expert_bytes];
        const down_slice = all_down_weights.data()[e * down_expert_bytes ..][0..down_expert_bytes];
        experts[e] = .{
            .gate_proj = tensor.Tensor.view(gate_slice.ptr, &.{ @intCast(config.d_ff), gate_bytes_per_row }, .mxfp4, gate_expert_bytes),
            .gate_scales = all_gate_scales.data()[e * gate_scale_expert_size ..][0..gate_scale_expert_size],
            .gate_bias = if (all_gate_bias) |b| b[e * gate_bias_expert_size ..][0..gate_bias_expert_size] else null,
            .up_proj = tensor.Tensor.view(up_slice.ptr, &.{ @intCast(config.d_ff), up_bytes_per_row }, .mxfp4, up_expert_bytes),
            .up_scales = all_up_scales.data()[e * up_scale_expert_size ..][0..up_scale_expert_size],
            .up_bias = if (all_up_bias) |b| b[e * up_bias_expert_size ..][0..up_bias_expert_size] else null,
            .down_proj = tensor.Tensor.view(down_slice.ptr, &.{ @intCast(config.d_model), down_bytes_per_row }, .mxfp4, down_expert_bytes),
            .down_scales = all_down_scales.data()[e * down_scale_expert_size ..][0..down_scale_expert_size],
            .down_bias = if (all_down_bias) |b| b[e * down_bias_expert_size ..][0..down_bias_expert_size] else null,
        };
    }

    return experts;
}

fn tryLoadTensorF32(
    allocator: std.mem.Allocator,
    st: *st_loader.UnifiedSafeTensors,
    name: []const u8,
) ?[]const f32 {
    const debug_shapes = std.posix.getenv("TOKAMINO_DEBUG_SHAPES") != null;
    if (debug_shapes) {
        std.debug.print("    tryLoadTensorF32: attempting '{s}'\n", .{name});
    }
    const t = st.getTensor(name, null) catch {
        if (debug_shapes) std.debug.print("    tryLoadTensorF32: getTensor FAILED for '{s}'\n", .{name});
        return null;
    };
    if (t.n_dims < 1) {
        if (debug_shapes) std.debug.print("    tryLoadTensorF32: n_dims < 1 for '{s}'\n", .{name});
        return null;
    }

    if (debug_shapes) {
        std.debug.print("    tryLoadTensorF32: '{s}' dtype={}, n_dims={}, shape=[{},{}], data.len={}\n", .{
            name, t.dtype, t.n_dims, t.shape[0], t.shape[1], t.data_size,
        });
    }

    // Calculate number of elements from shape
    var n: usize = 1;
    for (0..@intCast(t.n_dims)) |i| {
        n *= @intCast(t.shape[i]);
    }
    const out = allocator.alloc(f32, n) catch return null;

    switch (t.dtype) {
        .f32 => {
            const src = @as([*]align(1) const f32, @ptrCast(t.data().ptr))[0 .. t.data_size / @sizeOf(f32)];
            @memcpy(out, src[0..n]);
        },
        .bf16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0 .. t.data_size / @sizeOf(u16)];
            for (0..n) |i| out[i] = dtype.bf16ToF32(src[i]);
        },
        .f16 => {
            const src = @as([*]align(1) const u16, @ptrCast(t.data().ptr))[0 .. t.data_size / @sizeOf(u16)];
            for (0..n) |i| out[i] = dtype.fp16ToF32(src[i]);
        },
        else => {
            allocator.free(out);
            return null;
        },
    }
    return out;
}
