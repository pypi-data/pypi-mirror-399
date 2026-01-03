/// Backend abstraction for inference execution
/// Supports multiple backends: CPU (x86/ARM), Metal (macOS GPU)
///
/// This module provides a unified interface for running transformer inference
/// across different hardware backends. The backend selection is automatic based
/// on platform and model format.
const std = @import("std");
const builtin = @import("builtin");
const build_options = @import("build_options");

const io = @import("../../io/internal.zig");
const loader = io.model_loader;
const config_mod = io.config;
const ModelConfig = config_mod.ModelConfig;

pub const cpu = @import("cpu/root.zig");
const has_metal = build_options.enable_metal and builtin.os.tag == .macos;
pub const metal = if (has_metal) @import("metal/root.zig") else struct {
    pub const MetalBackend = void;
};

/// Backend type - tagged union of available backends
pub const Backend = union(enum) {
    cpu: cpu.CpuBackend,
    metal: if (has_metal) metal.MetalBackend else void,

    /// Initialize the appropriate backend based on platform and model format
    pub fn init(allocator: std.mem.Allocator, loaded: *loader.LoadedModel) !Backend {
        const debug_backend = std.posix.getenv("TOKAMINO_DEBUG_BACKEND") != null;

        // Check for BACKEND override
        if (std.posix.getenv("BACKEND")) |backend_env| {
            if (std.mem.eql(u8, backend_env, "cpu")) {
                std.log.info("BACKEND=cpu: forcing CPU backend", .{});
                if (debug_backend) std.log.info("Backend selected: cpu (forced)", .{});
                const cpu_backend = try cpu.CpuBackend.init(allocator, loaded);
                return .{ .cpu = cpu_backend };
            }
            if (std.mem.eql(u8, backend_env, "metal")) {
                if (!has_metal) {
                    std.log.err("BACKEND=metal requested but Metal backend is not enabled for this build/platform", .{});
                    return error.MetalNotEnabled;
                }
                std.log.info("BACKEND=metal: forcing Metal backend", .{});
                const metal_backend = try metal.MetalBackend.init(allocator, loaded);
                if (debug_backend) std.log.info("Backend selected: metal (forced)", .{});
                return .{ .metal = metal_backend };
            }
        }

        // Check if we should use Metal backend (macOS + quantized/bf16 model)
        if (has_metal) {
            const dtype = loaded.original_weight_dtype;
            const use_metal = dtype == .grouped_affine_u4 or dtype == .grouped_affine_u8 or dtype == .bf16;

            if (use_metal) {
                // Try Metal backend, but fall back to CPU if unsupported (e.g., MoE models)
                const metal_backend = metal.MetalBackend.init(allocator, loaded) catch |err| {
                    if (err == error.MoENotSupported or err == error.MLXNotAvailable) {
                        // Fall through to CPU backend
                        std.log.info("Metal backend unavailable ({s}), using CPU", .{@errorName(err)});
                        const cpu_backend = try cpu.CpuBackend.init(allocator, loaded);
                        if (debug_backend) std.log.info("Backend selected: cpu (metal unavailable: {s})", .{@errorName(err)});
                        return .{ .cpu = cpu_backend };
                    }
                    return err;
                };
                if (debug_backend) std.log.info("Backend selected: metal (auto)", .{});
                return .{ .metal = metal_backend };
            }
        }

        // Default to CPU backend
        const cpu_backend = try cpu.CpuBackend.init(allocator, loaded);
        if (debug_backend) std.log.info("Backend selected: cpu (default)", .{});
        return .{ .cpu = cpu_backend };
    }

    /// Clean up backend resources
    pub fn deinit(self: *Backend) void {
        switch (self.*) {
            .cpu => |*b| b.deinit(),
            .metal => |*b| if (has_metal) b.deinit() else unreachable,
        }
    }

    /// Prefill: process all prompt tokens, return logits for last position
    /// This resets the KV cache and processes the full prompt
    pub fn prefill(self: *Backend, tokens: []const u32, logits_out: []f32) !void {
        switch (self.*) {
            .cpu => |*b| try b.prefill(tokens, logits_out),
            .metal => |*b| if (has_metal) try b.prefill(tokens, logits_out) else unreachable,
        }
    }

    /// Decode: generate logits for a single token using KV cache
    /// Returns logits for the next token prediction
    pub fn decode(self: *Backend, token: u32, position: usize, logits_out: []f32) !void {
        switch (self.*) {
            .cpu => |*b| try b.decode(token, position, logits_out),
            .metal => |*b| if (has_metal) try b.decode(token, position, logits_out) else unreachable,
        }
    }

    /// Streaming token generation with callback support.
    ///
    /// Generates tokens autoregressively, invoking `callback` after each token.
    /// Some backends (Metal) can pipeline execution for better throughput.
    ///
    /// **Note:** Currently uses greedy (argmax) sampling. The configured sampling
    /// strategy is only applied to the first token (by session.generate()).
    /// See CpuBackend.decodeStreaming for details.
    pub fn decodeStreaming(
        self: *Backend,
        first_token: u32,
        start_position: usize,
        max_tokens: usize,
        eos_token_ids: []const u32,
        tokens_out: []u32,
        callback: ?*const fn (u32, ?*anyopaque) void,
        callback_data: ?*anyopaque,
    ) !usize {
        switch (self.*) {
            .cpu => |*b| return b.decodeStreaming(
                first_token,
                start_position,
                max_tokens,
                eos_token_ids,
                tokens_out,
                callback,
                callback_data,
            ),
            .metal => |*b| if (has_metal) {
                return b.decodeStreaming(
                    first_token,
                    start_position,
                    max_tokens,
                    eos_token_ids,
                    tokens_out,
                    callback,
                    callback_data,
                );
            } else unreachable,
        }
    }

    /// Get vocab size for this model
    pub fn vocabSize(self: *const Backend) usize {
        switch (self.*) {
            .cpu => |*b| return b.vocab_size,
            .metal => |*b| if (has_metal) return b.vocab_size else unreachable,
        }
    }

    /// Warmup: do a dummy forward pass to pull weights into CPU cache
    /// This eliminates cold-cache latency on first real inference
    pub fn warmup(self: *Backend) !void {
        switch (self.*) {
            .cpu => |*b| try b.warmup(),
            .metal => {}, // Metal doesn't need warmup (GPU has own memory)
        }
    }
};

test "backend selection" {
    // This test just verifies the module compiles correctly
    // Actual backend tests require model files
    const testing = std.testing;
    _ = testing;
}
