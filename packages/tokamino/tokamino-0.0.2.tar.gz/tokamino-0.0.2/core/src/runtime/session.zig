//! Inference Session
//!
//! Runtime state management for LLM inference. Ties together model loading,
//! tokenization, sampling, and backend execution.

const std = @import("std");
const sampler = @import("sampling.zig");
const tokenizer = @import("../text/api.zig");
const loader = @import("../io/internal.zig").model_loader;
const io = @import("../io/root.zig");
const Backend = @import("backend/root.zig").Backend;
const kernel_info = @import("../inspect/kernel_info.zig");
const debug = @import("debug.zig");

/// Callback function type for streaming token output.
/// Called with each newly generated token ID and optional user data.
pub const TokenCallback = *const fn (token_id: u32, user_data: ?*anyopaque) void;

pub const InferenceConfig = struct {
    max_new_tokens: usize = 32,
    sampling: sampler.SamplingConfig = .{},
    eos_token_ids: []const u32 = &.{},
    /// BOS token to prepend to input (from model config)
    bos_token_id: ?u32 = null,
    /// Optional callback for streaming output. Called after each token is sampled.
    token_callback: ?TokenCallback = null,
    /// User data passed to the token callback
    callback_data: ?*anyopaque = null,
};

pub const InferenceState = struct {
    tokens: []u32,
    final_logits: []f32,
    prompt_len: usize,
    generated_len: usize,
    prefill_ns: u64,
    decode_ns: u64,
};

pub const Session = struct {
    allocator: std.mem.Allocator,
    loaded: *loader.LoadedModel,
    tok: tokenizer.Tokenizer,
    samp: sampler.Sampler,
    backend: Backend,

    /// Build session from already-loaded components.
    /// This is the single point of truth for session assembly, avoiding duplication
    /// between threaded and synchronous initialization paths.
    /// Includes debug timing/shape output when flags are enabled.
    fn buildFromComponents(
        allocator: std.mem.Allocator,
        loaded_ptr: *loader.LoadedModel,
        tok: tokenizer.Tokenizer,
        seed: u64,
    ) !Session {
        const flags = debug.getFlags();
        var t_start: i128 = if (flags.timings) std.time.nanoTimestamp() else 0;

        var samp = try sampler.Sampler.init(allocator, seed, @intCast(loaded_ptr.config.vocab_size));
        errdefer samp.deinit();
        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("[init] sampler: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
            t_start = now;
        }
        if (flags.shapes) {
            std.debug.print("after sampler: embed_shape=[{}, {}]\n", .{
                loaded_ptr.token_embeddings.shape[0],
                loaded_ptr.token_embeddings.shape[1],
            });
        }

        var session = Session{
            .allocator = allocator,
            .loaded = loaded_ptr,
            .tok = tok,
            .samp = samp,
            .backend = undefined,
        };

        var backend = try Backend.init(allocator, session.loaded);
        errdefer backend.deinit();
        session.backend = backend;
        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("[init] backend: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
            t_start = now;
        }
        if (flags.shapes) {
            std.debug.print("after backend init: embed_shape=[{}, {}]\n", .{
                session.loaded.token_embeddings.shape[0],
                session.loaded.token_embeddings.shape[1],
            });
        }

        try session.backend.warmup();
        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("[init] warmup: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        }

        return session;
    }

    /// Initialize session with explicit tokenizer path
    pub fn init(
        allocator: std.mem.Allocator,
        config_path: []const u8,
        weights_path: []const u8,
        tokenizer_path: []const u8,
        seed: u64,
    ) !Session {
        return initWithTokenizer(allocator, config_path, weights_path, tokenizer_path, null, seed);
    }

    /// Initialize session with in-memory tokenizer JSON (for GGUF models)
    pub fn initWithJson(
        allocator: std.mem.Allocator,
        config_path: []const u8,
        weights_path: []const u8,
        tokenizer_json: []const u8,
        seed: u64,
    ) !Session {
        return initWithTokenizer(allocator, config_path, weights_path, "", tokenizer_json, seed);
    }

    /// Internal init with optional tokenizer JSON
    fn initWithTokenizer(
        allocator: std.mem.Allocator,
        config_path: []const u8,
        weights_path: []const u8,
        tokenizer_path: []const u8,
        tokenizer_json: ?[]const u8,
        seed: u64,
    ) !Session {
        // Initialize kernel tracing if TOKAMINO_TRACE is set
        kernel_info.initTracing();

        const flags = debug.getFlags();
        var t_start: i128 = if (flags.timings) std.time.nanoTimestamp() else 0;

        // Fail early with a clear error when required files are missing.
        // This keeps behavior stable across backends and tokenizers.
        std.fs.cwd().access(config_path, .{}) catch |err| switch (err) {
            error.FileNotFound => return error.FileNotFound,
            else => return err,
        };
        std.fs.cwd().access(weights_path, .{}) catch |err| switch (err) {
            error.FileNotFound => return error.FileNotFound,
            else => return err,
        };
        // Skip tokenizer path check if we have JSON in memory
        if (tokenizer_json == null) {
            std.fs.cwd().access(tokenizer_path, .{}) catch |err| switch (err) {
                error.FileNotFound => return error.FileNotFound,
                else => return err,
            };
        }

        // Start model loading in background thread
        const LoaderThread = struct {
            alloc: std.mem.Allocator,
            cfg_path: []const u8,
            wts_path: []const u8,
            result: ?loader.LoadedModel = null,
            err: ?anyerror = null,

            fn run(self: *@This()) void {
                self.result = io.loadModel(self.alloc, self.cfg_path, self.wts_path) catch |e| {
                    self.err = e;
                    return;
                };
            }
        };

        var loader_ctx = LoaderThread{
            .alloc = allocator,
            .cfg_path = config_path,
            .wts_path = weights_path,
        };

        const loader_thread = std.Thread.spawn(.{}, LoaderThread.run, .{&loader_ctx}) catch {
            // Thread spawn failed - load synchronously instead
            const loaded_ptr = try allocator.create(loader.LoadedModel);
            errdefer allocator.destroy(loaded_ptr);
            loaded_ptr.* = try io.loadModel(allocator, config_path, weights_path);
            errdefer loaded_ptr.deinit();

            var tok = if (tokenizer_json) |json|
                try tokenizer.Tokenizer.initFromJson(allocator, json)
            else
                try tokenizer.Tokenizer.initFromPath(allocator, tokenizer_path);
            errdefer tok.deinit();

            return buildFromComponents(allocator, loaded_ptr, tok, seed);
        };

        // Load tokenizer while model loads in background (~60ms of parallel work)
        var tok = if (tokenizer_json) |json|
            try tokenizer.Tokenizer.initFromJson(allocator, json)
        else
            try tokenizer.Tokenizer.initFromPath(allocator, tokenizer_path);
        errdefer tok.deinit();
        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("[init] tokenizer: {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
            t_start = now;
        }

        // Wait for model to finish loading
        loader_thread.join();

        if (loader_ctx.err) |e| return e;
        const loaded_ptr = try allocator.create(loader.LoadedModel);
        errdefer allocator.destroy(loaded_ptr);
        loaded_ptr.* = loader_ctx.result.?;
        errdefer loaded_ptr.deinit();

        if (flags.timings) {
            const now = std.time.nanoTimestamp();
            std.debug.print("[init] load_model (parallel): {d:.1}ms\n", .{@as(f64, @floatFromInt(now - t_start)) / 1_000_000.0});
        }
        if (flags.shapes) {
            std.debug.print(
                "after load: embed_shape=[{}, {}] dtype={any}\n",
                .{ loaded_ptr.token_embeddings.shape[0], loaded_ptr.token_embeddings.shape[1], loaded_ptr.token_embeddings.dtype },
            );
        }

        // Build session (includes granular timing for sampler/backend/warmup)
        return buildFromComponents(allocator, loaded_ptr, tok, seed);
    }

    pub fn deinit(self: *Session) void {
        // Finalize tracing (writes JSON if TOKAMINO_TRACE_JSON was set)
        kernel_info.finalizeTracing();

        self.backend.deinit();
        self.samp.deinit();
        self.loaded.deinit();
        self.allocator.destroy(self.loaded);
        self.tok.deinit();
        self.* = undefined;
    }

    pub fn run(self: *Session, prompt: []const u8, cfg: InferenceConfig) !InferenceState {
        return generate(self.allocator, &self.tok, &self.samp, &self.backend, prompt, cfg);
    }
};

pub fn generate(
    allocator: std.mem.Allocator,
    tok: *tokenizer.Tokenizer,
    samp: *sampler.Sampler,
    backend: *Backend,
    prompt: []const u8,
    cfg: InferenceConfig,
) !InferenceState {
    const flags = debug.getFlags();
    const vocab_size = backend.vocabSize();

    // Encode prompt
    var encode_timer = try std.time.Timer.start();
    const encoded = try tok.encode(prompt);
    const encode_ns = encode_timer.read();
    if (flags.timings) {
        std.debug.print("[encode] prompt: {d:.3}ms ({} tokens)\n", .{ @as(f64, @floatFromInt(encode_ns)) / 1_000_000.0, encoded.len });
    }

    // Prepend BOS token if configured (required by some models like Gemma),
    // but avoid double-prepending when the prompt already starts with BOS.
    var has_bos = cfg.bos_token_id != null;
    if (has_bos and encoded.len > 0 and encoded[0] == cfg.bos_token_id.?) {
        has_bos = false;
    }
    const bos_offset: usize = if (has_bos) 1 else 0;
    const prompt_len = encoded.len + bos_offset;
    const max_len = prompt_len + cfg.max_new_tokens;

    var tokens = try allocator.alloc(u32, max_len);
    errdefer allocator.free(tokens);
    if (has_bos) {
        tokens[0] = cfg.bos_token_id.?;
    }
    @memcpy(tokens[bos_offset..prompt_len], encoded);
    tok.allocator.free(encoded);

    // Allocate logits buffer
    const logits = try allocator.alloc(f32, vocab_size);
    defer allocator.free(logits);

    // Start timing prefill
    var timer = try std.time.Timer.start();

    // === PREFILL PHASE ===
    try backend.prefill(tokens[0..prompt_len], logits);

    // Capture prefill time (ONLY the forward pass, like llama.cpp)
    const prefill_ns = timer.read();

    // Sample first token (not included in prefill timing)
    var final_logits = try allocator.dupe(f32, logits);
    const sampled = try samp.sample(final_logits, cfg.sampling);
    tokens[prompt_len] = @intCast(sampled);
    var token_len = prompt_len + 1;

    // Debug: print first sampled token
    if (flags.tokens) {
        std.debug.print("prefill_sampled = {} (prompt_len={})\n", .{ sampled, prompt_len });
    }

    // Invoke callback for first token
    if (cfg.token_callback) |callback| {
        callback(@intCast(sampled), cfg.callback_data);
    }
    if (flags.timings) {
        std.debug.print("prefill_ns={d:.3}ms\n", .{@as(f64, @floatFromInt(prefill_ns)) / 1_000_000.0});
    }
    timer.reset();

    // Check if first token is EOS
    for (cfg.eos_token_ids) |eos_id| {
        if (sampled == eos_id) {
            const result = try allocator.realloc(tokens, token_len);
            return InferenceState{
                .tokens = result,
                .final_logits = final_logits,
                .prompt_len = prompt_len,
                .generated_len = 1,
                .prefill_ns = prefill_ns,
                .decode_ns = 0,
            };
        }
    }

    // === DECODE PHASE ===
    var gen_count: usize = 1;

    // Use streaming decode for remaining tokens
    const remaining = cfg.max_new_tokens - 1;
    if (remaining > 0) {
        const generated = try backend.decodeStreaming(
            @intCast(sampled),
            token_len,
            remaining,
            cfg.eos_token_ids,
            tokens[token_len..],
            cfg.token_callback,
            cfg.callback_data,
        );
        gen_count += generated;
        token_len += generated;
    }

    // Capture decode time
    const decode_ns = timer.read();
    if (flags.timings) {
        std.debug.print("decode_ns={d:.3}ms\n", .{@as(f64, @floatFromInt(decode_ns)) / 1_000_000.0});
    }

    // Get final logits from last decode
    if (gen_count > 1) {
        try backend.decode(tokens[token_len - 1], token_len - 1, logits);
        allocator.free(final_logits);
        final_logits = try allocator.dupe(f32, logits);
    }

    // Shrink to actual size
    const result = try allocator.realloc(tokens, token_len);
    return InferenceState{
        .tokens = result,
        .final_logits = final_logits,
        .prompt_len = prompt_len,
        .generated_len = gen_count,
        .prefill_ns = prefill_ns,
        .decode_ns = decode_ns,
    };
}

test "session init fails cleanly for missing files" {
    const res = Session.init(
        std.testing.allocator,
        "/no/such/config.json",
        "/no/such/model.safetensors",
        "/no/such/tokenizer",
        1,
    );
    try std.testing.expectError(error.FileNotFound, res);
}
