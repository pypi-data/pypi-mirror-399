//! CPU Backend for Transformer Inference
//!
//! This module provides the CPU backend implementation that orchestrates
//! transformer inference using the CPU kernel implementations.
//!
//! ## Architecture
//!
//! The backend uses a hybrid architecture optimized for both introspection and performance:
//!
//! ```
//! CpuBackend
//! ├── model: transformer.Model      # Unified transformer engine tree for introspection & forward pass
//! │   ├── embed_tokens: Embedding    # Token embedding lookup
//! │   ├── layers[]: Block            # Each block has attention + FFN modules
//! │   ├── norm: RMSNorm              # Final layer norm
//! │   └── lm_head: ?Linear           # Output projection (if not tied)
//! │
//! ├── blocks[]: cpu_blocks.TransformerBlock  # CPU kernel blocks (owned by LoadedModel after finalize)
//! ├── scratch: ScratchBuffer              # Shared runtime buffers/caches (tmp[], KV cache)
//! │
//! └── hidden/prefill_hidden/logits   # Activation buffers
//! ```
//!
//! The `transformer.Model` tree provides:
//! - Hierarchical introspection via `describe()` methods
//! - Weight/kernel inspection via `formatKernels()`
//! - Unified `forward()` interface that delegates to optimized kernels
//!
//! The `kernel_container` holds the actual kernel structs (attention, ffn, moe)
//! that modules reference via pointers. This separation allows:
//! - Zero-copy weight access via mmap
//! - Efficient kernel dispatch without virtual calls
//! - Clear ownership of scratch buffers

const std = @import("std");
const tensor = @import("../../../tensor.zig");
const Tensor = tensor.Tensor;
const OwnedTensor = tensor.OwnedTensor;
const matmul = @import("../../../compute/ops/matmul.zig");
const loader = @import("../../../io/internal.zig").model_loader;
const kernel_info = @import("../../../inspect/kernel_info.zig");
const executor = @import("../../executor/root.zig");
const graph = @import("../../model_build.zig");
const debug = @import("../../debug.zig");

// Alias for compatibility
const transformer = executor;

// Import CPU block kernels + scratch buffers (not transformer topology)
const cpu_blocks = @import("block_kernels.zig");

// Note: CPU kernel types are exported from `src/compute/backend/cpu/kernels/root.zig`.

/// CPU Backend for transformer inference.
/// See module-level documentation for architecture overview.
pub const CpuBackend = struct {
    allocator: std.mem.Allocator,
    loaded: *loader.LoadedModel,

    /// Unified module model - the primary interface for forward pass and introspection
    model: transformer.Model,

    /// CPU kernel blocks (built once after model load/sanitize).
    blocks: []const cpu_blocks.TransformerBlock,

    /// Runtime scratch buffers and KV caches used during computation
    scratch: cpu_blocks.ScratchBuffer,

    // Buffers
    hidden: OwnedTensor,
    prefill_hidden: OwnedTensor,
    logits: OwnedTensor,

    // Model dimensions
    d_model: usize,
    vocab_size: usize,

    pub fn init(allocator: std.mem.Allocator, loaded: *loader.LoadedModel) !CpuBackend {
        const d_model: usize = @intCast(loaded.config.d_model);
        const vocab_size: usize = @intCast(loaded.config.vocab_size);
        if (loaded.config.num_experts > 0) {
            std.log.info(
                "MoE model detected - {d} experts, {d} active per token",
                .{ loaded.config.num_experts, loaded.config.experts_per_token },
            );
        }

        const blocks = try loaded.ensureCpuBlocks(allocator);

        var scratch = cpu_blocks.ScratchBuffer.init(
            allocator,
            d_model,
            @intCast(loaded.config.d_ff),
            @intCast(loaded.config.n_layers),
        );
        errdefer scratch.deinit();

        // Build unified transformer.Model for introspection and forward
        const model = try graph.buildModel(allocator, loaded, blocks);

        // Allocate buffers
        var hidden = try OwnedTensor.init(allocator, .f32, &.{ 1, 1, d_model });
        errdefer hidden.deinit();

        // Prefill buffer - will be resized as needed
        var prefill_hidden = try OwnedTensor.init(allocator, .f32, &.{ 1, 1, d_model });
        errdefer prefill_hidden.deinit();

        var logits = try OwnedTensor.init(allocator, .f32, &.{ 1, vocab_size });
        errdefer logits.deinit();

        return CpuBackend{
            .allocator = allocator,
            .loaded = loaded,
            .model = model,
            .blocks = blocks,
            .scratch = scratch,
            .hidden = hidden,
            .prefill_hidden = prefill_hidden,
            .logits = logits,
            .d_model = d_model,
            .vocab_size = vocab_size,
        };
    }

    pub fn deinit(self: *CpuBackend) void {
        self.allocator.free(self.model.layers); // Free model layers array
        self.logits.deinit();
        self.prefill_hidden.deinit();
        self.hidden.deinit();
        self.scratch.deinit();
        self.* = undefined;
    }

    /// Warmup: no-op, model pages loaded via MAP_POPULATE during init
    pub fn warmup(_: *CpuBackend) !void {}

    /// Prefill: process all prompt tokens, return logits for last position
    pub fn prefill(self: *CpuBackend, tokens: []const u32, logits_out: []f32) !void {
        const t0 = kernel_info.traceTimestamp();
        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceEnter("prefill", .{tokens.len});
        }

        const token_len = tokens.len;
        const flags = debug.getFlags();
        var t_start: u128 = 0;
        if (flags.timings) t_start = @intCast(std.time.nanoTimestamp());
        if (flags.shapes) {
            std.debug.print(
                "prefill token_len={} embed_shape=[{}, {}] embed_dtype={any}\n",
                .{
                    token_len,
                    self.loaded.token_embeddings.shape[0],
                    self.loaded.token_embeddings.shape[1],
                    self.loaded.token_embeddings.dtype,
                },
            );
        }

        // Resize prefill buffer if needed
        if (self.prefill_hidden.shape[1] != token_len) {
            self.prefill_hidden.deinit();
            self.prefill_hidden = try OwnedTensor.init(
                self.allocator,
                .f32,
                &.{ 1, token_len, self.d_model },
            );
        }

        var prefill_view = self.prefill_hidden.view();

        // 1. Gather embeddings for all prompt tokens (using unified module)
        try self.model.embed_tokens.forward(tokens, &prefill_view);
        applyEmbeddingScaling(&self.loaded.config, prefill_view.asSlice(f32));
        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            const delta = @as(u128, @intCast(now)) - t_start;
            std.debug.print("prefill gather_ns={d:.3}ms\n", .{@as(f64, @floatFromInt(delta)) / 1_000_000.0});
            t_start = @intCast(now);
        }

        // 2. Forward through transformer layers (using unified module)
        // Note: KV cache population for subsequent decode is handled inside the attention kernel
        // when `use_cache == false` (prefill path).
        try self.model.forward(&prefill_view, &prefill_view, &self.scratch, false);
        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            const delta = @as(u128, @intCast(now)) - t_start;
            std.debug.print("prefill transformer_ns={d:.3}ms\n", .{@as(f64, @floatFromInt(delta)) / 1_000_000.0});
            t_start = @intCast(now);
        }

        // 3. Apply final layer norm to the last position (using unified module)
        const last_pos_offset = (token_len - 1) * self.d_model * @sizeOf(f32);
        var last_hidden_view = Tensor.view3D(
            prefill_view.data()[last_pos_offset .. last_pos_offset + self.d_model * @sizeOf(f32)],
            1,
            self.d_model,
        );
        cpu_blocks.rmsnormForward(&self.model.norm, &last_hidden_view, &last_hidden_view);

        if (flags.block) {
            const h = last_hidden_view.asSlice(f32);
            std.debug.print("Prefill after ln_final: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ h[0], h[1], h[2], h[3] });
        }

        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            const delta = @as(u128, @intCast(now)) - t_start;
            std.debug.print("prefill ln_final_ns={d:.3}ms\n", .{@as(f64, @floatFromInt(delta)) / 1_000_000.0});
            t_start = @intCast(now);
        }

        // 4. Compute logits for the last position
        try computeLogits(&last_hidden_view, &self.loaded.lm_head, &self.logits, &self.loaded.config, self.d_model, self.vocab_size, logits_out);

        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            const delta = @as(u128, @intCast(now)) - t_start;
            std.debug.print("prefill logits_ns={d:.3}ms\n", .{@as(f64, @floatFromInt(delta)) / 1_000_000.0});
        }

        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceExit("prefill", t0);
        }
    }

    /// Decode: generate logits for a single token using KV cache
    pub fn decode(self: *CpuBackend, token: u32, position: usize, logits_out: []f32) !void {
        const t0 = kernel_info.traceTimestamp();
        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceEnter("decode", .{ token, position });
        }
        const flags = debug.getFlags();
        const token_slice = &[_]u32{token};

        // 1. Get embedding for the token (using unified module)
        var hidden_view = Tensor.view3D(
            self.hidden.data[0 .. self.d_model * @sizeOf(f32)],
            1,
            self.d_model,
        );
        try self.model.embed_tokens.forward(token_slice, &hidden_view);
        applyEmbeddingScaling(&self.loaded.config, hidden_view.asSlice(f32));

        // 2. Forward through transformer layers (using unified module, with cache enabled)
        try self.model.forward(&hidden_view, &hidden_view, &self.scratch, true);

        // 3. Apply final layer norm (using unified module)
        cpu_blocks.rmsnormForward(&self.model.norm, &hidden_view, &hidden_view);

        if (flags.block) {
            const h = hidden_view.asSlice(f32);
            std.debug.print("Decode after ln_final: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ h[0], h[1], h[2], h[3] });
        }

        // 4. Compute logits
        try computeLogits(&hidden_view, &self.loaded.lm_head, &self.logits, &self.loaded.config, self.d_model, self.vocab_size, logits_out);

        if (kernel_info.isTraceEnabled()) {
            kernel_info.traceExit("decode", t0);
        }
    }

    /// Streaming token generation with callback support.
    ///
    /// This function generates up to `max_tokens` tokens starting from `first_token`,
    /// invoking `callback` after each token for streaming output.
    ///
    /// **Important behavioral notes:**
    /// - Uses greedy (argmax) sampling internally. The first token (from prefill) is
    ///   sampled by session.generate() using the configured SamplingConfig, but all
    ///   subsequent tokens use greedy decoding.
    /// - The `first_token` parameter is the token to start decoding from (already
    ///   generated, not stored again). Decoded tokens are written to `tokens_out`.
    /// - `start_position` is the current KV cache position (prompt_len + 1 typically).
    /// - Returns the count of newly generated tokens (not including first_token).
    /// - Generation stops early if an EOS token is generated.
    ///
    /// TODO: To support non-greedy sampling, either:
    /// 1. Pass a Sampler to this function, or
    /// 2. Return logits and let the caller handle sampling
    pub fn decodeStreaming(
        self: *CpuBackend,
        first_token: u32,
        start_position: usize,
        max_tokens: usize,
        eos_token_ids: []const u32,
        tokens_out: []u32,
        callback: ?*const fn (u32, ?*anyopaque) void,
        callback_data: ?*anyopaque,
    ) !usize {
        var token = first_token;
        var position = start_position;
        var gen_count: usize = 0;

        // Allocate logits buffer for sampling
        var logits_buf = try self.allocator.alloc(f32, self.vocab_size);
        defer self.allocator.free(logits_buf);

        // Simple decode loop
        while (gen_count < max_tokens) : (gen_count += 1) {
            // Get logits for current token
            try self.decode(token, position, logits_buf);
            position += 1;

            // Greedy decode: find argmax token
            var max_idx: usize = 0;
            var max_val: f32 = logits_buf[0];
            for (logits_buf[1..], 1..) |val, idx| {
                if (val > max_val) {
                    max_val = val;
                    max_idx = idx;
                }
            }
            token = @intCast(max_idx);
            tokens_out[gen_count] = token;

            // Check for EOS
            var is_eos = false;
            for (eos_token_ids) |eos_id| {
                if (token == eos_id) {
                    is_eos = true;
                    break;
                }
            }

            // Invoke callback
            if (callback) |cb| {
                cb(token, callback_data);
            }

            if (is_eos) {
                gen_count += 1;
                break;
            }
        }

        return gen_count;
    }
};

/// Shared helper to compute logits from hidden state.
/// Used by both prefill (last position) and decode (single token).
fn computeLogits(
    hidden_view: *const Tensor,
    lm_head: *const Tensor,
    logits_tensor: *OwnedTensor,
    config: *const tensor.ModelConfig,
    d_model: usize,
    vocab_size: usize,
    logits_out: []f32,
) !void {
    const flags = debug.getFlags();

    // hidden @ lm_head -> logits
    var hidden_flat = Tensor.view2D(hidden_view.data(), 1, d_model);
    var logits_view = Tensor.view2D(logits_tensor.data, 1, vocab_size);

    if (flags.block) {
        std.debug.print("lm_head dtype: {any}, shape: [{}, {}]\n", .{ lm_head.dtype, lm_head.shape[0], lm_head.shape[1] });
    }

    try matmul.matmulAuto(&hidden_flat, lm_head, &logits_view);

    if (flags.block) {
        const logits = logits_tensor.asSlice(f32);
        var max_logit: f32 = logits[0];
        var max_idx: usize = 0;
        for (logits, 0..) |l, i| {
            if (l > max_logit) {
                max_logit = l;
                max_idx = i;
            }
        }
        std.debug.print("Logits: max={d:.4} at idx={}, first 4: [{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ max_logit, max_idx, logits[0], logits[1], logits[2], logits[3] });
    }

    applyLogitsScaling(config, logits_tensor.asSlice(f32));
    @memcpy(logits_out, logits_tensor.asSlice(f32));
}

fn applyEmbeddingScaling(config: *const tensor.ModelConfig, hidden: []f32) void {
    if (config.embedding_multiplier == 1.0) return;
    const flags = debug.getFlags();
    if (flags.embed) {
        std.debug.print("applyEmbeddingScaling: multiplier={d:.4}, hidden[0:4] before=[{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ config.embedding_multiplier, hidden[0], hidden[1], hidden[2], hidden[3] });
    }
    for (hidden) |*v| v.* *= config.embedding_multiplier;
    if (flags.embed) {
        std.debug.print("applyEmbeddingScaling: hidden[0:4] after=[{d:.4}, {d:.4}, {d:.4}, {d:.4}]\n", .{ hidden[0], hidden[1], hidden[2], hidden[3] });
    }
}

fn applyLogitsScaling(config: *const tensor.ModelConfig, logits: []f32) void {
    if (config.logits_scaling == 1.0) return;
    for (logits) |*v| v.* /= config.logits_scaling;
}
