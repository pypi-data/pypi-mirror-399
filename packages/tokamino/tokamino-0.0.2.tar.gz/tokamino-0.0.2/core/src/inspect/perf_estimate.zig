const std = @import("std");
const dtype_mod = @import("../dtype.zig");
const forward = @import("../runtime/backend/cpu/block_kernels.zig");

const DType = dtype_mod.DType;
const MultiHeadAttention = forward.MultiHeadAttention;
const FfnLayer = forward.FfnLayer;

pub const PerfEstimate = struct {
    prefill_flops: u64,
    per_token_flops: u64,
    prefill_mem_bytes: u64,
    per_token_mem_bytes: u64,
    seq_len: usize,
    weight_dtype: DType,

    pub fn format(self: PerfEstimate, writer: anytype) !void {
        try writer.print("Performance estimate (seq_len={}):\n", .{self.seq_len});

        try writer.writeAll("\n  FLOPs:\n");
        try writer.writeAll("    Prefill:   ");
        try formatFlops(writer, self.prefill_flops);
        try writer.writeAll("\n");
        try writer.writeAll("    Per-token: ");
        try formatFlops(writer, self.per_token_flops);
        try writer.writeAll("\n");

        try writer.writeAll("\n  Memory bandwidth:\n");
        try writer.writeAll("    Prefill:   ");
        try formatBytes(writer, self.prefill_mem_bytes);
        try writer.writeAll("\n");
        try writer.writeAll("    Per-token: ");
        try formatBytes(writer, self.per_token_mem_bytes);
        try writer.writeAll("\n");

        const prefill_ai = @as(f64, @floatFromInt(self.prefill_flops)) / @as(f64, @floatFromInt(self.prefill_mem_bytes));
        const decode_ai = @as(f64, @floatFromInt(self.per_token_flops)) / @as(f64, @floatFromInt(self.per_token_mem_bytes));
        try writer.writeAll("\n  Arithmetic intensity (FLOP/byte):\n");
        try writer.print("    Prefill:   {d:.1}\n", .{prefill_ai});
        try writer.print("    Per-token: {d:.1}\n", .{decode_ai});

        try writer.writeAll("\n  Theoretical decode tok/s:\n");
        const profiles = [_]struct { name: []const u8, tflops: f64, mem_gbps: f64 }{
            .{ .name = "CPU (AVX2)", .tflops = 0.5, .mem_gbps = 50 },
            .{ .name = "M1 Pro", .tflops = 5.2, .mem_gbps = 200 },
            .{ .name = "M2 Ultra", .tflops = 27.2, .mem_gbps = 800 },
            .{ .name = "RTX 4090", .tflops = 82.6, .mem_gbps = 1008 },
            .{ .name = "H100 SXM", .tflops = 989, .mem_gbps = 3350 },
        };

        for (profiles) |p| {
            const compute_limit = p.tflops * 1e12 / @as(f64, @floatFromInt(self.per_token_flops));
            const mem_limit = p.mem_gbps * 1e9 / @as(f64, @floatFromInt(self.per_token_mem_bytes));
            const actual = @min(compute_limit, mem_limit);
            const bottleneck: []const u8 = if (compute_limit < mem_limit) "compute" else "memory";
            try writer.print("    {s}: {d:.1} tok/s ({s}-bound)\n", .{ p.name, actual, bottleneck });
        }
    }
};

pub const EstimateArgs = struct {
    seq_len: usize,
    weight_dtype: DType,
    hidden_size: usize,
    vocab_size: usize,
    num_hidden_layers: usize,
    attn: *const MultiHeadAttention,
    ffn: *const FfnLayer,
};

pub const LayerGeom = struct {
    q_dim: usize,
    kv_dim: usize,
    qkv_proj_weights: usize,

    ffn_weights: usize,
    attn_bias_params: usize,
    router_weights: usize,
    expert_weights: usize,
    total_layer_params: usize,

    pub fn init(attn: *const MultiHeadAttention, ffn: *const FfnLayer) LayerGeom {
        const q_dim = attn.n_heads * attn.head_dim;
        const kv_dim = attn.n_kv_heads * attn.head_dim;

        const q_proj_weights = attn.d_model * q_dim;
        const k_proj_weights = attn.d_model * kv_dim;
        const v_proj_weights = attn.d_model * kv_dim;
        const o_proj_weights = q_dim * attn.d_model;
        const qkv_proj_weights = q_proj_weights + k_proj_weights + v_proj_weights + o_proj_weights;
        const attn_bias_params: usize =
            (if (attn.q_bias != null) q_dim else 0) +
            (if (attn.k_bias != null) kv_dim else 0) +
            (if (attn.v_bias != null) kv_dim else 0) +
            (if (attn.o_bias != null) attn.d_model else 0);

        var ffn_weights: usize = 0;
        var router_weights: usize = 0;
        var expert_weights: usize = 0;

        switch (ffn.*) {
            .swiglu => |mlp| {
                ffn_weights = mlp.d_model * mlp.d_ff * 3;
            },
            .moe_ffn => |moe| {
                router_weights = moe.d_model * moe.num_experts;
                expert_weights = moe.num_experts * moe.d_model * moe.d_ff * 3;
                ffn_weights = router_weights + expert_weights;
            },
        }

        return .{
            .q_dim = q_dim,
            .kv_dim = kv_dim,
            .qkv_proj_weights = qkv_proj_weights,
            .ffn_weights = ffn_weights,
            .attn_bias_params = attn_bias_params,
            .router_weights = router_weights,
            .expert_weights = expert_weights,
            .total_layer_params = qkv_proj_weights + attn_bias_params + ffn_weights,
        };
    }
};

pub fn estimatePerf(args: EstimateArgs) PerfEstimate {
    var prefill_flops: u64 = 0;
    var decode_flops: u64 = 0;
    var prefill_mem: u64 = 0;
    var decode_mem: u64 = 0;

    const weight_bytes_x2: u64 = switch (args.weight_dtype) {
        .grouped_affine_u4 => 1, // 0.5 bytes (4 bits per weight)
        .grouped_affine_u8 => 2, // 1 byte
        .f16, .bf16 => 4, // 2 bytes
        .f32 => 8, // 4 bytes
        else => 4, // Default to f16
    };

    prefill_mem += args.seq_len * args.hidden_size * weight_bytes_x2;
    decode_mem += args.hidden_size * weight_bytes_x2;

    const geom = LayerGeom.init(args.attn, args.ffn);
    const n_heads = args.attn.n_heads;
    const n_kv_heads = args.attn.n_kv_heads;
    const head_dim = args.attn.head_dim;

    var layer_prefill_flops: u64 = 0;
    var layer_decode_flops: u64 = 0;
    var layer_weight_bytes_x2: u64 = 0;

    // Weights (quantized; preserve prior behavior: biases are not included here)
    layer_weight_bytes_x2 += @as(u64, @intCast(geom.qkv_proj_weights + geom.ffn_weights)) * weight_bytes_x2;

    // Projections FLOPs: 2 * seq * (Q + K + V + O)
    layer_prefill_flops += 2 * args.seq_len * @as(u64, @intCast(geom.qkv_proj_weights));
    layer_decode_flops += 2 * @as(u64, @intCast(geom.qkv_proj_weights));

    // SDPA: Q @ K^T + scores @ V
    layer_prefill_flops += 2 * args.seq_len * args.seq_len * head_dim * n_heads;
    layer_decode_flops += 2 * args.seq_len * head_dim * n_heads;

    const kv_cache_per_layer = args.seq_len * n_kv_heads * head_dim * 4 * 2; // f32, K+V

    // FFN FLOPs
    switch (args.ffn.*) {
        .swiglu => |mlp| {
            layer_prefill_flops += 2 * args.seq_len * @as(u64, @intCast(geom.ffn_weights));
            layer_decode_flops += 2 * @as(u64, @intCast(geom.ffn_weights));
            _ = mlp;
        },
        .moe_ffn => |moe_layer| {
            // Only count active experts for compute.
            layer_prefill_flops += 2 * args.seq_len * @as(u64, @intCast(geom.router_weights));
            layer_prefill_flops += 2 * args.seq_len * moe_layer.d_model * moe_layer.d_ff * 3 * moe_layer.experts_per_token;

            layer_decode_flops += 2 * @as(u64, @intCast(geom.router_weights));
            layer_decode_flops += 2 * moe_layer.d_model * moe_layer.d_ff * 3 * moe_layer.experts_per_token;
        },
    }

    prefill_flops += layer_prefill_flops * args.num_hidden_layers;
    decode_flops += layer_decode_flops * args.num_hidden_layers;

    prefill_mem += layer_weight_bytes_x2 * args.num_hidden_layers;
    decode_mem += layer_weight_bytes_x2 * args.num_hidden_layers;
    decode_mem += kv_cache_per_layer * args.num_hidden_layers * 2; // Convert to x2 units

    // LM head
    const lm_head_size = args.hidden_size * args.vocab_size;
    const lm_head_bytes_x2 = lm_head_size * weight_bytes_x2;
    prefill_flops += 2 * lm_head_size;
    decode_flops += 2 * lm_head_size;
    prefill_mem += lm_head_bytes_x2;
    decode_mem += lm_head_bytes_x2;

    return .{
        .prefill_flops = prefill_flops,
        .per_token_flops = decode_flops,
        .prefill_mem_bytes = prefill_mem / 2,
        .per_token_mem_bytes = decode_mem / 2,
        .seq_len = args.seq_len,
        .weight_dtype = args.weight_dtype,
    };
}

pub fn formatFlops(writer: anytype, flops: u64) !void {
    const f = @as(f64, @floatFromInt(flops));
    if (f >= 1e15) {
        try writer.print("{d:.2} PFLOP", .{f / 1e15});
    } else if (f >= 1e12) {
        try writer.print("{d:.2} TFLOP", .{f / 1e12});
    } else if (f >= 1e9) {
        try writer.print("{d:.2} GFLOP", .{f / 1e9});
    } else if (f >= 1e6) {
        try writer.print("{d:.2} MFLOP", .{f / 1e6});
    } else {
        try writer.print("{} FLOP", .{flops});
    }
}

pub fn formatBytes(writer: anytype, bytes: u64) !void {
    const f = @as(f64, @floatFromInt(bytes));
    if (f >= 1e12) {
        try writer.print("{d:.2} TB", .{f / 1e12});
    } else if (f >= 1e9) {
        try writer.print("{d:.2} GB", .{f / 1e9});
    } else if (f >= 1e6) {
        try writer.print("{d:.2} MB", .{f / 1e6});
    } else if (f >= 1e3) {
        try writer.print("{d:.2} KB", .{f / 1e3});
    } else {
        try writer.print("{} B", .{bytes});
    }
}
