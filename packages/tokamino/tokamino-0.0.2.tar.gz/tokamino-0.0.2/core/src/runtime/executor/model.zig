const std = @import("std");
const common = @import("common.zig");
const layers = @import("layers.zig");
const Block = @import("block.zig").Block;

const Tensor = common.Tensor;
const DType = common.DType;
const Attention = common.Attention;
const FFNLayer = common.FFNLayer;
const RMSNorm = common.RMSNorm;
const ScratchBuffer = common.ScratchBuffer;
const PerfEstimate = common.perf_estimate.PerfEstimate;

const kernel_info = common.kernel_info;
const perf_estimate = common.perf_estimate;
const cpu_forward = common.forward;

pub const Linear = layers.Linear;
pub const Embedding = layers.Embedding;

/// Complete transformer model
pub const Model = struct {
    model_type: []const u8,
    embed_tokens: Embedding,
    layers: []Block,
    norm: RMSNorm,
    lm_head: ?Linear = null,
    tie_word_embeddings: bool = true,

    // Dimensions
    hidden_size: usize,
    vocab_size: usize,
    num_hidden_layers: usize,

    // Original weight dtype for summary
    weight_dtype: DType,

    // File info for summary (from LoadedModel)
    file_size: usize = 0,
    tensor_count: usize = 0,

    /// Forward pass through transformer layers only (not embedding or final norm).
    /// This is the core transformer body: hidden_states -> layers -> hidden_states
    pub fn forward(
        self: *const Model,
        x: *const Tensor,
        out: *Tensor,
        scratch: *ScratchBuffer,
        use_cache: bool,
    ) !void {
        const t0 = kernel_info.traceTimestamp();
        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceEnter("Model.forward", .{self.num_hidden_layers});
        }

        if (!use_cache) scratch.resetCaches();
        const seq: usize = @intCast(x.shape[1]);
        try scratch.ensure(seq);

        // Use pre-allocated scratch buffer for alternating input/output
        var tmp_storage = Tensor.view3DSlice(scratch.tmp[0], seq, self.hidden_size);
        var current_in: *const Tensor = x;
        var use_tmp: bool = false;

        const debug_layers = std.posix.getenv("TOKAMINO_DEBUG_LAYERS") != null;
        for (self.layers, 0..) |*layer, idx| {
            const attn_cache = &scratch.attn_caches[idx];
            if (use_tmp) {
                try layer.forward(current_in, &tmp_storage, scratch, attn_cache, use_cache);
                current_in = &tmp_storage;
            } else {
                try layer.forward(current_in, out, scratch, attn_cache, use_cache);
                current_in = out;
            }
            use_tmp = !use_tmp;
            if (debug_layers) {
                const data = current_in.asSlice(f32);
                std.debug.print("Layer {d} output[0:4]: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ idx, data[0], data[1], data[2], data[3] });
            }
        }

        // Copy final result to out if needed
        if (current_in != out) {
            cpu_forward.copyTensor(current_in, out);
        }

        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceExit("Model.forward", t0);
        }
    }

    pub fn describe(self: *const Model, writer: anytype, show_kernels: bool) !void {
        try self.describeCondensed(writer, show_kernels, 3); // Show first 3, last 1
    }

    const DescribeMode = union(enum) {
        condensed: usize,
        all,
    };

    fn describeImpl(self: *const Model, writer: anytype, show_kernels: bool, mode: DescribeMode) !void {
        try writer.print("{s}(\n", .{self.model_type});

        try writer.writeAll("  (embed_tokens): ");
        try self.embed_tokens.formatTo(writer);
        try writer.writeAll("\n");

        if (show_kernels) {
            try self.embed_tokens.formatKernels(writer, 4);
        }

        try writer.writeAll("  (layers): [\n");

        const n_layers = self.layers.len;
        switch (mode) {
            .all => {
                for (self.layers) |*layer| {
                    try layer.describe(writer, 4, show_kernels);
                }
            },
            .condensed => |show_first| {
                if (n_layers <= show_first + 2) {
                    for (self.layers) |*layer| {
                        try layer.describe(writer, 4, show_kernels);
                    }
                } else {
                    for (self.layers[0..show_first]) |*layer| {
                        try layer.describe(writer, 4, show_kernels);
                    }
                    const hidden = n_layers - show_first - 1;
                    try writer.print("    ... {d} more identical layers ...\n", .{hidden});
                    try self.layers[n_layers - 1].describe(writer, 4, show_kernels);
                }
            },
        }
        try writer.writeAll("  ]\n");

        try writer.writeAll("  (norm): ");
        try layers.formatRmsNormLike(writer, self.norm.dim, self.norm.eps, self.norm.weight_offset);
        try writer.writeAll("\n");

        if (self.lm_head) |*head| {
            try writer.writeAll("  (lm_head): ");
            try head.formatTo(writer);
            try writer.writeAll("\n");
            if (show_kernels) {
                try head.formatKernels(writer, 4);
            }
        } else if (self.tie_word_embeddings) {
            try writer.writeAll("  (lm_head): [tied to embed_tokens]\n");
        }

        try writer.writeAll(")\n");
    }

    /// Describe model with condensed layer output.
    /// Shows first `show_first` layers, then "... N more layers ...", then last layer.
    pub fn describeCondensed(self: *const Model, writer: anytype, show_kernels: bool, show_first: usize) !void {
        try self.describeImpl(writer, show_kernels, .{ .condensed = show_first });
    }

    /// Describe model showing all layers (no condensing)
    pub fn describeAll(self: *const Model, writer: anytype, show_kernels: bool) !void {
        try self.describeImpl(writer, show_kernels, .all);
    }

    pub fn summary(self: *const Model, writer: anytype) !void {
        try self.summaryWithSeqLen(writer, 512); // Default seq_len for memory estimates
    }

    pub fn summaryWithSeqLen(self: *const Model, writer: anytype, seq_len: usize) !void {
        _ = seq_len; // Reserved for future use

        try writer.print("Model: {s}\n", .{self.model_type});

        // Estimate parameters
        var total_params: usize = 0;
        total_params += self.embed_tokens.vocab_size * self.embed_tokens.embed_dim;

        if (self.firstLayerGeom()) |geom| {
            var layer_params: usize = 0;
            layer_params += geom.total_layer_params;
            total_params += layer_params * self.num_hidden_layers;
        }

        if (self.lm_head) |head| {
            total_params += head.in_features * head.out_features;
        }

        // Parameters
        if (total_params >= 1_000_000_000) {
            const billions = @as(f64, @floatFromInt(total_params)) / 1_000_000_000.0;
            try writer.print("  Parameters: {d:.2}B\n", .{billions});
        } else if (total_params >= 1_000_000) {
            const millions = @as(f64, @floatFromInt(total_params)) / 1_000_000.0;
            try writer.print("  Parameters: {d:.2}M\n", .{millions});
        } else {
            try writer.print("  Parameters: {}\n", .{total_params});
        }

        // Quantization
        const quant_info: []const u8 = switch (self.weight_dtype) {
            .grouped_affine_u4 => "4-bit (grouped affine)",
            .grouped_affine_u8 => "8-bit (grouped affine)",
            .q5_0 => "Q5_0",
            .bf16 => "BF16",
            .f16 => "F16",
            .f32 => "F32",
            else => "unknown",
        };
        try writer.print("  Quantization: {s}\n", .{quant_info});

        // Weights (file size)
        if (self.file_size > 0) {
            try writer.writeAll("  Weights: ");
            try perf_estimate.formatBytes(writer, self.file_size);
            try writer.writeAll("\n");
        }

        // Architecture
        try writer.print("  Layers: {}\n", .{self.num_hidden_layers});
        try writer.print("  Hidden size: {}\n", .{self.hidden_size});
        try writer.print("  Vocab size: {}\n", .{self.vocab_size});

        // Help hint
        try writer.writeAll("\nUse -v for module graph, -vv for kernel operations\n");
    }

    /// Estimate weight memory in bytes (accounts for quantization)
    pub fn estimateWeightMemory(self: *const Model) u64 {
        var total_params: u64 = 0;

        // Embedding
        total_params += self.embed_tokens.vocab_size * self.embed_tokens.embed_dim;

        // Layers
        if (self.firstLayerGeom()) |geom| {
            var layer_params: u64 = 0;

            // Per-layer weights
            layer_params += @intCast(geom.total_layer_params);

            // Norms (always f32)
            const norm_params: u64 = self.hidden_size * 2; // input + post-attn norm

            total_params += layer_params * self.num_hidden_layers;
            // Norm params are always f32
            total_params += norm_params * self.num_hidden_layers * 4 / self.bytesPerParam();
        }

        // Final norm (f32)
        total_params += self.hidden_size * 4 / self.bytesPerParam();

        // LM head
        if (self.lm_head) |head| {
            total_params += head.in_features * head.out_features;
        }

        return total_params * self.bytesPerParam();
    }

    /// Estimate scratch buffer memory for given sequence length
    pub fn estimateScratchMemory(self: *const Model, seq_len: usize) u64 {
        var total: u64 = 0;

        // Activation buffers (f32): tmp[0..2] (layer_tmp, norm_out, branch_out)
        // Each is [seq_len, hidden_size]
        const activation_buf = seq_len * self.hidden_size * 4;
        total += activation_buf * 3;

        if (self.firstLayerKernels()) |layer| {
            const attn = layer.attn;
            const ffn = layer.ffn;

            const kv_per_layer = seq_len * attn.n_kv_heads * attn.head_dim * 4 * 2; // f32, K+V
            total += kv_per_layer * self.num_hidden_layers;

            // Scores: [n_heads, seq_len, seq_len] for prefill
            total += attn.n_heads * seq_len * seq_len * 4;

            const ffn_size = switch (ffn.*) {
                .swiglu => |mlp| seq_len * mlp.d_ff * 4,
                .moe_ffn => |moe| seq_len * moe.d_ff * moe.experts_per_token * 4,
            };
            total += ffn_size;
        }

        return total;
    }

    fn bytesPerParam(self: *const Model) u64 {
        return switch (self.weight_dtype) {
            .grouped_affine_u4 => 1, // ~0.5 bytes, round up to 1 for scale overhead
            .grouped_affine_u8 => 1,
            .f16, .bf16 => 2,
            .f32 => 4,
            else => 2,
        };
    }

    fn firstLayerKernels(self: *const Model) ?struct { attn: *const Attention, ffn: *const FFNLayer } {
        if (self.layers.len == 0) return null;
        const first = &self.layers[0];
        return .{
            .attn = first.getAttention(),
            .ffn = first.getFFN(),
        };
    }

    fn firstLayerGeom(self: *const Model) ?perf_estimate.LayerGeom {
        const layer = self.firstLayerKernels() orelse return null;
        return perf_estimate.LayerGeom.init(layer.attn, layer.ffn);
    }

    /// Estimate FLOPs for a forward pass with given sequence length.
    /// Returns struct with prefill and per-token decode FLOPs.
    pub fn estimateFlops(self: *const Model, seq_len: usize) PerfEstimate {
        return self.estimatePerf(seq_len);
    }

    /// Estimate performance characteristics (FLOPs and memory bandwidth) for inference.
    /// Returns struct with prefill and per-token decode estimates.
    pub fn estimatePerf(self: *const Model, seq_len: usize) PerfEstimate {
        const layer = self.firstLayerKernels() orelse return .{
            .prefill_flops = 0,
            .per_token_flops = 0,
            .prefill_mem_bytes = 0,
            .per_token_mem_bytes = 0,
            .seq_len = seq_len,
            .weight_dtype = self.weight_dtype,
        };
        return perf_estimate.estimatePerf(.{
            .seq_len = seq_len,
            .weight_dtype = self.weight_dtype,
            .hidden_size = self.hidden_size,
            .vocab_size = self.vocab_size,
            .num_hidden_layers = self.num_hidden_layers,
            .attn = layer.attn,
            .ffn = layer.ffn,
        });
    }
};
