/// Metal Backend for transformer inference (macOS GPU via MLX)
/// This is the main entry point for the Metal backend.
const std = @import("std");
const loader = @import("../../../io/internal.zig").model_loader;
const tensor = @import("../../../tensor.zig");
const ModelConfig = tensor.ModelConfig;

// Import compute primitives from compute/metal/
const metal_compute = @import("../../../compute/metal/root.zig");
const graph = metal_compute.graph;

// Internal orchestration modules
const mlx_forward = @import("mlx_forward.zig");

// Re-exports for direct access if needed
pub const device = metal_compute.device;
pub const matmul = metal_compute.matmul;
pub const Graph = graph;
pub const Forward = mlx_forward;

pub const Device = metal_compute.Device;
pub const Buffer = metal_compute.Buffer;
pub const isAvailable = metal_compute.isAvailable;
pub const Cache = metal_compute.Cache;
pub const WeightHandles = mlx_forward.WeightHandles;

/// Metal backend for GPU-accelerated transformer inference
pub const MetalBackend = struct {
    allocator: std.mem.Allocator,
    config: ModelConfig,
    weights: *mlx_forward.WeightHandles,
    cache: graph.Cache,
    vocab_size: usize,

    // Track position for decode
    current_position: usize,

    // Fused model handles (quantized or dense)
    fused_model: ?*anyopaque,
    dense_model: ?*anyopaque,

    pub fn init(allocator: std.mem.Allocator, loaded: *loader.LoadedModel) !MetalBackend {
        // Load weights to GPU
        const weights = try mlx_forward.loadWeightsToGPU(allocator, loaded);
        errdefer mlx_forward.freeWeights(allocator, weights);

        // Create fused model for decode optimization
        mlx_forward.createFusedModel(allocator, weights, loaded.config) catch |err| {
            std.debug.print("Warning: Failed to create fused model: {}\n", .{err});
            // Continue without fused model - will fall back to per-layer calls
        };

        // Initialize KV cache (bfloat16)
        const cache = graph.Cache.init(@intCast(loaded.config.n_layers), true);

        return MetalBackend{
            .allocator = allocator,
            .config = loaded.config,
            .weights = weights,
            .cache = cache,
            .vocab_size = @intCast(loaded.config.vocab_size),
            .current_position = 0,
            .fused_model = weights.fused_model,
            .dense_model = weights.dense_model,
        };
    }

    pub fn deinit(self: *MetalBackend) void {
        self.cache.deinit();
        mlx_forward.freeWeights(self.allocator, self.weights);
        self.* = undefined;
    }

    /// Prefill: process all prompt tokens, return logits for last position
    pub fn prefill(self: *MetalBackend, tokens: []const u32, logits_out: []f32) !void {
        const token_len = tokens.len;

        // Reset cache for new sequence
        self.cache.deinit();
        self.cache = graph.Cache.init(@intCast(self.config.n_layers), true);

        // Build lazy computation graph
        const logits_handle = try mlx_forward.transformerForwardLazy(
            self.allocator,
            self.weights,
            tokens,
            self.config,
            self.cache,
            0, // pos_offset
            false, // use_compiled (prefill must use manual path)
        );

        // Execute graph on GPU
        graph.eval(&[_]graph.ArrayHandle{logits_handle});

        // Get shape to verify
        var shape_buf: [8]usize = undefined;
        const ndim = graph.getShape(logits_handle, &shape_buf);
        std.debug.assert(ndim == 3);
        std.debug.assert(shape_buf[0] == 1);
        std.debug.assert(shape_buf[1] == token_len);
        std.debug.assert(shape_buf[2] == self.vocab_size);

        // Copy full logits from GPU
        const full_logits = try self.allocator.alloc(f32, token_len * self.vocab_size);
        defer self.allocator.free(full_logits);
        graph.copyToHost(logits_handle, full_logits);

        // Extract last position
        const last_offset = (token_len - 1) * self.vocab_size;
        @memcpy(logits_out, full_logits[last_offset .. last_offset + self.vocab_size]);

        // Free handle
        graph.freeArray(logits_handle);

        // Update position
        self.current_position = token_len;
    }

    /// Decode: generate logits for a single token using KV cache
    pub fn decode(self: *MetalBackend, token: u32, position: usize, logits_out: []f32) !void {
        const token_slice = &[_]u32{token};

        // Build lazy computation graph for single token
        const logits_handle = try mlx_forward.transformerForwardLazy(
            self.allocator,
            self.weights,
            token_slice,
            self.config,
            self.cache,
            position,
            false,
        );

        // Execute graph
        graph.eval(&[_]graph.ArrayHandle{logits_handle});

        // Copy logits from GPU
        graph.copyToHost(logits_handle, logits_out);

        // Free handle
        graph.freeArray(logits_handle);

        self.current_position = position + 1;
    }

    /// Decode with streaming - Metal uses pipelined execution for better throughput
    pub fn decodeStreaming(
        self: *MetalBackend,
        first_token: u32,
        start_position: usize,
        max_tokens: usize,
        eos_token_ids: []const u32,
        tokens_out: []u32,
        callback: ?*const fn (u32, ?*anyopaque) void,
        callback_data: ?*anyopaque,
    ) !usize {
        // Allow forcing non-fused path for debugging
        const force_non_fused = std.process.hasEnvVar(self.allocator, "TOKAMINO_NO_FUSED") catch false;
        const use_batch = std.process.hasEnvVar(self.allocator, "TOKAMINO_BATCH_DECODE") catch false;
        const use_fused = !force_non_fused and (self.fused_model != null or self.dense_model != null);

        // Batch decode: run entire loop in C++ to eliminate FFI overhead
        // Note: callbacks are called AFTER batch completes (not during)
        if (use_batch and self.fused_model != null) {
            const gen_count = graph.mlx_fused_decode_batch(
                self.fused_model.?,
                self.cache.handle,
                first_token,
                start_position,
                tokens_out.ptr,
                max_tokens,
                eos_token_ids.ptr,
                eos_token_ids.len,
            );

            // Call callbacks after batch (for streaming output)
            if (callback) |cb| {
                for (0..gen_count) |i| {
                    cb(tokens_out[i], callback_data);
                }
            }

            self.current_position = start_position + gen_count;
            return gen_count;
        }

        if (use_fused) {
            return self.decodeStreamingFused(
                first_token,
                start_position,
                max_tokens,
                eos_token_ids,
                tokens_out,
                callback,
                callback_data,
            );
        } else {
            return self.decodeStreamingNonFused(
                first_token,
                start_position,
                max_tokens,
                eos_token_ids,
                tokens_out,
                callback,
                callback_data,
            );
        }
    }

    /// Fused decode path - uses pipelined C++ execution
    fn decodeStreamingFused(
        self: *MetalBackend,
        first_token: u32,
        start_position: usize,
        max_tokens: usize,
        eos_token_ids: []const u32,
        tokens_out: []u32,
        callback: ?*const fn (u32, ?*anyopaque) void,
        callback_data: ?*anyopaque,
    ) !usize {
        var gen_count: usize = 0;
        var position = start_position;

        // Prime the pipeline
        if (self.fused_model) |fused| {
            graph.mlx_pipeline_prime(
                fused,
                self.cache.handle,
                first_token,
                position,
            );
        } else if (self.dense_model) |dense| {
            graph.mlx_dense_pipeline_prime(
                dense,
                self.cache.handle,
                first_token,
                position,
            );
        }
        position += 1;

        while (gen_count < max_tokens) : (gen_count += 1) {
            var sampled: u32 = undefined;

            if (gen_count + 1 < max_tokens) {
                // Normal step: returns current, queues next
                if (self.fused_model) |fused| {
                    sampled = graph.mlx_pipeline_step(
                        fused,
                        self.cache.handle,
                        position,
                    );
                } else if (self.dense_model) |dense| {
                    sampled = graph.mlx_dense_pipeline_step(
                        dense,
                        self.cache.handle,
                        position,
                    );
                }
            } else {
                // Last iteration: flush
                if (self.fused_model != null) {
                    sampled = graph.mlx_pipeline_flush();
                } else {
                    sampled = graph.mlx_dense_pipeline_flush();
                }
            }
            position += 1;

            // Store token
            tokens_out[gen_count] = sampled;

            // Debug: print generated token IDs
            if (std.process.hasEnvVar(self.allocator, "TOKAMINO_DEBUG_TOKENS") catch false) {
                std.debug.print("gen[{}] = {} (pos={})\n", .{ gen_count, sampled, position - 1 });
            }

            // Check for EOS
            var is_eos = false;
            for (eos_token_ids) |eos_id| {
                if (sampled == eos_id) {
                    is_eos = true;
                    break;
                }
            }

            // Invoke callback
            if (callback) |cb| {
                cb(sampled, callback_data);
            }

            if (is_eos) {
                gen_count += 1;
                break;
            }
        }

        self.current_position = position;
        return gen_count;
    }

    /// Non-fused decode path - uses lazy graph API with pipelining
    fn decodeStreamingNonFused(
        self: *MetalBackend,
        first_token: u32,
        start_position: usize,
        max_tokens: usize,
        eos_token_ids: []const u32,
        tokens_out: []u32,
        callback: ?*const fn (u32, ?*anyopaque) void,
        callback_data: ?*anyopaque,
    ) !usize {
        var gen_count: usize = 0;
        var position = start_position;

        // Prime: Build first token graph
        const first_token_slice = &[_]u32{first_token};
        var current_logits = try mlx_forward.transformerForwardLazy(
            self.allocator,
            self.weights,
            first_token_slice,
            self.config,
            self.cache,
            position,
            false,
        );
        var current_last_logits = graph.mlx_lazy_slice_last(current_logits);
        var current_token = graph.mlx_lazy_argmax(current_last_logits, -1);
        graph.asyncEval(&[_]graph.ArrayHandle{current_token});
        position += 1;

        while (gen_count < max_tokens) : (gen_count += 1) {
            var sampled: u32 = undefined;

            if (gen_count + 1 < max_tokens) {
                // Build graph for NEXT token using current (lazy) token
                const next_logits = try mlx_forward.transformerForwardFromGPUToken(
                    self.allocator,
                    self.weights,
                    current_token,
                    self.config,
                    self.cache,
                    position,
                );
                const next_last_logits = graph.mlx_lazy_slice_last(next_logits);
                const next_token = graph.mlx_lazy_argmax(next_last_logits, -1);

                // Queue next token computation
                graph.asyncEval(&[_]graph.ArrayHandle{next_token});

                // Materialize current token
                sampled = graph.mlx_array_item_u32(current_token);

                // Free old handles
                graph.freeArray(current_logits);

                // Rotate
                current_logits = next_logits;
                current_last_logits = next_last_logits;
                current_token = next_token;
            } else {
                // Last iteration - just materialize current
                sampled = graph.mlx_array_item_u32(current_token);
                graph.freeArray(current_logits);
            }
            position += 1;

            // Reset pool periodically
            if (gen_count % 64 == 0) {
                graph.mlx_pool_reset();
            }

            // Store token
            tokens_out[gen_count] = sampled;

            // Check for EOS
            var is_eos = false;
            for (eos_token_ids) |eos_id| {
                if (sampled == eos_id) {
                    is_eos = true;
                    break;
                }
            }

            // Invoke callback
            if (callback) |cb| {
                cb(sampled, callback_data);
            }

            // Clear memory cache periodically
            if (gen_count % 256 == 0) {
                graph.mlx_clear_memory_cache();
            }

            if (is_eos) {
                gen_count += 1;
                break;
            }
        }

        self.current_position = position;
        return gen_count;
    }
};

test {
    @import("std").testing.refAllDecls(@This());
    _ = @import("test.zig");
}
