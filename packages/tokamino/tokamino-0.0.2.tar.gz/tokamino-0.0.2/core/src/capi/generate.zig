//! Generate C API
//!
//! C-callable functions for text generation, tokenization, and model management.

const std = @import("std");
const session_mod = @import("../runtime/session.zig");
const gen_config_mod = @import("../io/config/generation.zig");
const sampler = @import("../runtime/sampling.zig");
const io = @import("../io/root.zig");
const io_internal = @import("../io/internal.zig");
const storage = io.storage;
const tensor = @import("../tensor.zig");
const text_root = @import("../text/root.zig");
const tokenizer_api = @import("../text/api.zig");
const ct = tokenizer_api.c_types;
const tok_pipeline = tokenizer_api.pipeline;

// Native build uses C allocator
const allocator = std.heap.c_allocator;

/// Opaque session handle for C API
pub const SessionHandle = opaque {};

/// Opaque tokenizer handle for C API (lightweight, no model weights)
pub const TokenizerHandle = opaque {};

const Session = struct {
    session: session_mod.Session,
    model_dir: []u8,
    gen_config: gen_config_mod.GenerationConfig,
};

/// Lightweight tokenizer wrapper (no model weights loaded)
const TokenizerWrapper = struct {
    tok: tokenizer_api.Tokenizer,
    model_dir: []u8,
    gen_config: gen_config_mod.GenerationConfig,
};

/// Result structure returned from generate
pub const GenerateResult = extern struct {
    /// Pointer to generated token IDs (caller must free with tokamino_result_free)
    tokens: ?[*]u32,
    /// Number of tokens (prompt + generated)
    num_tokens: usize,
    /// Number of prompt tokens
    prompt_len: usize,
    /// Number of generated tokens
    generated_len: usize,
    /// Prefill time in nanoseconds
    prefill_ns: u64,
    /// Decode time in nanoseconds
    decode_ns: u64,
    /// Error message if failed (null on success)
    error_msg: ?[*:0]const u8,
};

/// Sampling configuration for C API
pub const SamplingParams = extern struct {
    /// Sampling strategy: 0=greedy, 1=top_k, 2=top_p
    strategy: u32 = 0,
    /// Temperature (default 1.0, 0 means use model default)
    temperature: f32 = 1.0,
    /// Top-k value (default 50)
    top_k: u32 = 50,
    /// Top-p value (default 0.9)
    top_p: f32 = 0.9,
};

/// Generation configuration for C API
pub const GenerateConfig = extern struct {
    /// Maximum tokens to generate
    max_tokens: u32 = 32,
    /// Sampling parameters
    sampling: SamplingParams = .{},
    /// Random seed (0 = use time-based seed)
    seed: u64 = 0,
};

/// Get BOS token ID from session, matching main.zig logic
fn getBosTokenId(wrapper: *const Session) ?u32 {
    if (wrapper.gen_config.bos_token_id) |id| {
        return if (wrapper.gen_config.add_bos_token) id else null;
    }
    if (wrapper.session.loaded.config.bos_token_id) |id| {
        if (id < 0) return null;
        return if (wrapper.gen_config.add_bos_token) @intCast(id) else null;
    }
    return null;
}

/// Create a session from a model path (handles both directory and GGUF)
fn createSessionFromPath(alloc: std.mem.Allocator, model_path: []const u8, seed: u64) !session_mod.Session {
    var bundle = try storage.resolve(alloc, model_path);
    defer bundle.deinit();

    return if (bundle.tokenizer_json()) |json|
        try session_mod.Session.initWithJson(alloc, bundle.config_path(), bundle.weights_path(), json, seed)
    else
        try session_mod.Session.init(alloc, bundle.config_path(), bundle.weights_path(), bundle.tokenizer_path(), seed);
}

// =============================================================================
// Session Management
// =============================================================================

/// Create a new generation session from a model directory.
/// The model_dir should contain config.json, model.safetensors, and tokenizer.json.
pub export fn tokamino_session_create(model_dir: [*:0]const u8) callconv(.c) ?*SessionHandle {
    return tokamino_session_create_with_seed(model_dir, 0);
}

/// Create a new generation session with a specific seed.
/// Accepts either a directory path (for SafeTensors) or a .gguf file path.
pub export fn tokamino_session_create_with_seed(model_path: [*:0]const u8, seed: u64) callconv(.c) ?*SessionHandle {
    const path = std.mem.span(model_path);
    const actual_seed = if (seed == 0) @as(u64, @intCast(std.time.timestamp())) else seed;

    const wrapper = allocator.create(Session) catch return null;
    errdefer allocator.destroy(wrapper);

    wrapper.model_dir = allocator.dupe(u8, path) catch return null;
    errdefer allocator.free(wrapper.model_dir);

    // Use shared generation config module (same as main.zig)
    wrapper.gen_config = gen_config_mod.loadGenerationConfig(allocator, path) catch .{};
    errdefer wrapper.gen_config.deinit(allocator);

    // Create session from path
    wrapper.session = createSessionFromPath(allocator, path, actual_seed) catch {
        wrapper.gen_config.deinit(allocator);
        allocator.free(wrapper.model_dir);
        return null;
    };

    // Add extra EOS tokens (same as main.zig lines 508-509)
    // This fixes Gemma-family models that emit "<end_of_turn>" as regular text
    addEosFromTokenizer(&wrapper.session.tok, &wrapper.gen_config, "<end_of_turn>");
    addEosFromTokenizer(&wrapper.session.tok, &wrapper.gen_config, "<eos>");

    return @ptrCast(wrapper);
}

fn addEosFromTokenizer(tok: *tokenizer_api.Tokenizer, cfg: *gen_config_mod.GenerationConfig, comptime token_str: []const u8) void {
    const ids = tok.encode(token_str) catch return;
    defer tok.allocator.free(ids);
    if (ids.len != 1) return;
    gen_config_mod.addEosTokenId(allocator, cfg, ids[0]) catch return;
}

/// Free a generation session.
pub export fn tokamino_session_free(handle: ?*SessionHandle) callconv(.c) void {
    if (handle) |h| {
        const wrapper: *Session = @ptrCast(@alignCast(h));
        wrapper.session.deinit();
        wrapper.gen_config.deinit(allocator);
        allocator.free(wrapper.model_dir);
        allocator.destroy(wrapper);
    }
}

// =============================================================================
// Tokenizer-Only API (lightweight, no model weights)
// =============================================================================

/// Create a tokenizer-only handle from a model path.
/// This is much faster than tokamino_session_create() as it only loads
/// tokenizer.json, not model weights.
/// Accepts either a directory path or HuggingFace model ID.
pub export fn tokamino_tokenizer_create(model_path: [*:0]const u8) callconv(.c) ?*TokenizerHandle {
    const path = std.mem.span(model_path);

    const wrapper = allocator.create(TokenizerWrapper) catch return null;
    errdefer allocator.destroy(wrapper);

    wrapper.model_dir = allocator.dupe(u8, path) catch return null;
    errdefer allocator.free(wrapper.model_dir);

    // Load generation config (for EOS tokens)
    wrapper.gen_config = gen_config_mod.loadGenerationConfig(allocator, path) catch .{};
    errdefer wrapper.gen_config.deinit(allocator);

    // Resolve tokenizer path and load tokenizer only
    var bundle = storage.resolve(allocator, path) catch {
        wrapper.gen_config.deinit(allocator);
        allocator.free(wrapper.model_dir);
        return null;
    };
    defer bundle.deinit();

    // Load tokenizer (either from embedded JSON or file path)
    if (bundle.tokenizer_json()) |json| {
        wrapper.tok = tokenizer_api.Tokenizer.initFromJson(allocator, json) catch {
            wrapper.gen_config.deinit(allocator);
            allocator.free(wrapper.model_dir);
            return null;
        };
    } else {
        wrapper.tok = tokenizer_api.Tokenizer.initFromPath(allocator, bundle.tokenizer_path()) catch {
            wrapper.gen_config.deinit(allocator);
            allocator.free(wrapper.model_dir);
            return null;
        };
    }

    // Add extra EOS tokens (same as session creation)
    addEosFromTokenizer(&wrapper.tok, &wrapper.gen_config, "<end_of_turn>");
    addEosFromTokenizer(&wrapper.tok, &wrapper.gen_config, "<eos>");

    return @ptrCast(wrapper);
}

/// Free a tokenizer-only handle.
pub export fn tokamino_tokenizer_free(handle: ?*TokenizerHandle) callconv(.c) void {
    if (handle) |h| {
        const wrapper: *TokenizerWrapper = @ptrCast(@alignCast(h));
        wrapper.tok.deinit();
        wrapper.gen_config.deinit(allocator);
        allocator.free(wrapper.model_dir);
        allocator.destroy(wrapper);
    }
}

/// Encode text to token IDs using tokenizer-only handle.
/// Returns token array that must be freed with tokamino_tokens_free.
/// Takes explicit length to support text containing null bytes.
pub export fn tokamino_tokenizer_encode(
    handle: ?*TokenizerHandle,
    text: [*]const u8,
    text_len: usize,
) callconv(.c) EncodeResult {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return EncodeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "Invalid tokenizer handle",
        };

    const text_slice = text[0..text_len];
    const encoded = wrapper.tok.encodeSlice(text_slice) catch |err| {
        return EncodeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = @errorName(err),
        };
    };

    // Copy to C-allocated buffer (tokenizer uses its own allocator)
    const result = allocator.alloc(u32, encoded.len) catch {
        wrapper.tok.allocator.free(encoded);
        return EncodeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "OutOfMemory",
        };
    };
    @memcpy(result, encoded);
    wrapper.tok.allocator.free(encoded);

    return EncodeResult{
        .tokens = result.ptr,
        .num_tokens = result.len,
        .error_msg = null,
    };
}

/// Result struct for tokenize operation (returns token strings).
pub const TokenizeResult = extern struct {
    tokens: ?[*][*:0]u8, // Array of null-terminated token strings
    num_tokens: usize,
    error_msg: ?[*:0]const u8,
};

/// Tokenize text to token strings using tokenizer-only handle.
/// Returns array of token strings. Caller must free with tokamino_tokenize_result_free.
/// Takes explicit length to support text containing null bytes.
pub export fn tokamino_tokenizer_tokenize(
    handle: ?*TokenizerHandle,
    text: [*]const u8,
    text_len: usize,
) callconv(.c) TokenizeResult {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return TokenizeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "Invalid tokenizer handle",
        };

    const text_slice = text[0..text_len];

    // First call to get count
    var num_tokens: usize = 0;
    if (tok_pipeline.tokenizer_tokenize(wrapper.tok.handle, text_slice, null, &num_tokens) != 0) {
        return TokenizeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "Tokenization failed",
        };
    }

    if (num_tokens == 0) {
        return TokenizeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = null,
        };
    }

    // Allocate array for token pointers
    const tokens = allocator.alloc([*:0]u8, num_tokens) catch {
        return TokenizeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "OutOfMemory",
        };
    };

    // Second call to get tokens
    var actual_len = num_tokens;
    if (tok_pipeline.tokenizer_tokenize(wrapper.tok.handle, text_slice, tokens.ptr, &actual_len) != 0) {
        allocator.free(tokens);
        return TokenizeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "Tokenization failed",
        };
    }

    return TokenizeResult{
        .tokens = tokens.ptr,
        .num_tokens = actual_len,
        .error_msg = null,
    };
}

/// Free TokenizeResult returned by tokamino_tokenizer_tokenize.
pub export fn tokamino_tokenize_result_free(tokens: ?[*][*:0]u8, num_tokens: usize) callconv(.c) void {
    if (tokens) |tok_ptr| {
        // Free each token string
        for (0..num_tokens) |i| {
            tok_pipeline.tokenizer_string_free(tok_ptr[i]);
        }
        // Free the array itself
        allocator.free(tok_ptr[0..num_tokens]);
    }
}

/// Decode token IDs to text using tokenizer-only handle.
/// Returns a DecodeResult with text buffer (NOT null-terminated) and length.
/// Caller must free the result with tokamino_decode_result_free.
pub export fn tokamino_tokenizer_decode(
    handle: ?*TokenizerHandle,
    tokens: [*]const u32,
    num_tokens: usize,
) callconv(.c) DecodeResult {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = "Invalid handle",
        };

    if (num_tokens == 0) {
        return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = null,
        };
    }

    const text = wrapper.tok.decode(tokens[0..num_tokens]) catch return DecodeResult{
        .text = null,
        .text_len = 0,
        .error_msg = "Decode failed",
    };
    defer wrapper.tok.allocator.free(text);

    // Copy to C-allocated buffer (no null terminator needed)
    const result = allocator.alloc(u8, text.len) catch return DecodeResult{
        .text = null,
        .text_len = 0,
        .error_msg = "Allocation failed",
    };
    @memcpy(result, text);
    return DecodeResult{
        .text = result.ptr,
        .text_len = text.len,
        .error_msg = null,
    };
}

/// Get EOS tokens from a tokenizer-only handle.
pub export fn tokamino_tokenizer_get_eos_tokens(
    handle: ?*TokenizerHandle,
) callconv(.c) EosTokenResult {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };

    if (wrapper.gen_config.eos_token_ids.len == 0) {
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };
    }

    // Copy to owned array
    const ids = allocator.alloc(u32, wrapper.gen_config.eos_token_ids.len) catch {
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };
    };
    @memcpy(ids, wrapper.gen_config.eos_token_ids);

    return EosTokenResult{ .tokens = ids.ptr, .num_tokens = ids.len };
}

/// Get the model directory from a tokenizer-only handle.
/// Returns null-terminated string. Caller must free with tokamino_text_free.
pub export fn tokamino_tokenizer_get_model_dir(
    handle: ?*TokenizerHandle,
) callconv(.c) ?[*:0]u8 {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return null;

    const result = allocator.allocSentinel(u8, wrapper.model_dir.len, 0) catch return null;
    @memcpy(result, wrapper.model_dir);
    return result;
}

// =============================================================================
// Vocabulary Access API
// =============================================================================

/// Result struct for special tokens query.
pub const SpecialTokensResult = extern struct {
    bos_token_id: i32, // -1 if not set
    unk_token_id: i32, // -1 if not set
    pad_token_id: i32, // -1 if not set
};

/// Get the vocabulary size.
pub export fn tokamino_tokenizer_get_vocab_size(
    handle: ?*TokenizerHandle,
) callconv(.c) usize {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return 0;

    return ct.modelGetVocabSize(wrapper.tok.handle);
}

/// Get special token IDs (BOS, UNK, PAD).
/// Returns -1 for any token that is not set.
pub export fn tokamino_tokenizer_get_special_tokens(
    handle: ?*TokenizerHandle,
) callconv(.c) SpecialTokensResult {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return SpecialTokensResult{ .bos_token_id = -1, .unk_token_id = -1, .pad_token_id = -1 };

    return SpecialTokensResult{
        .bos_token_id = ct.modelGetBosId(wrapper.tok.handle),
        .unk_token_id = ct.modelGetUnkId(wrapper.tok.handle),
        .pad_token_id = wrapper.tok.handle.padding.pad_id,
    };
}

/// Convert a token ID to its string representation.
/// Returns null-terminated string. Caller must free with tokamino_text_free.
/// Returns null if ID is out of range.
pub export fn tokamino_tokenizer_id_to_token(
    handle: ?*TokenizerHandle,
    token_id: i32,
) callconv(.c) ?[*:0]u8 {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return null;

    const token = ct.modelIdToToken(wrapper.tok.handle, token_id) orelse return null;

    // Copy to owned null-terminated string
    const result = allocator.allocSentinel(u8, token.len, 0) catch return null;
    @memcpy(result, token);
    return result;
}

/// Convert a token string to its ID.
/// Returns -1 if token is not found in vocabulary.
pub export fn tokamino_tokenizer_token_to_id(
    handle: ?*TokenizerHandle,
    token: [*]const u8,
    token_len: usize,
) callconv(.c) i32 {
    const wrapper: *TokenizerWrapper = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return -1;

    const token_slice = token[0..token_len];
    return ct.modelTokenToId(wrapper.tok.handle, token_slice) orelse -1;
}

// =============================================================================
// Model Path Resolution (HuggingFace Hub)
// =============================================================================

/// Resolve a model path, downloading from HuggingFace Hub if needed.
/// If the path exists locally, returns a copy of the path.
/// If the path looks like a HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B"),
/// downloads the model and returns the local cache path.
/// Returns null on error. Caller must free with tokamino_text_free.
pub export fn tokamino_resolve_model_path(model_path: [*:0]const u8) callconv(.c) ?[*:0]u8 {
    const path = std.mem.span(model_path);

    // Check if it's an existing local path
    if (std.fs.cwd().access(path, .{})) |_| {
        // Path exists locally, return a copy
        const result = allocator.allocSentinel(u8, path.len, 0) catch return null;
        @memcpy(result, path);
        return result;
    } else |_| {
        // Path doesn't exist - check if it looks like a HuggingFace model ID
        if (!isHuggingFaceModelId(path)) {
            // Not a valid HF model ID and doesn't exist locally
            return null;
        }

        // Try to get from cache first
        if (storage.getCachedPath(allocator, path) catch null) |cached_path| {
            defer allocator.free(cached_path);
            const result = allocator.allocSentinel(u8, cached_path.len, 0) catch return null;
            @memcpy(result, cached_path);
            return result;
        }

        // Download from HuggingFace Hub
        storage.globalInit();
        defer storage.globalCleanup();

        const token = std.posix.getenv("HF_TOKEN");
        const downloaded_path = storage.downloadModel(allocator, path, .{
            .token = token,
        }) catch return null;
        defer allocator.free(downloaded_path);

        const result = allocator.allocSentinel(u8, downloaded_path.len, 0) catch return null;
        @memcpy(result, downloaded_path);
        return result;
    }
}

/// Check if a string looks like a HuggingFace model ID (org/model format).
fn isHuggingFaceModelId(path: []const u8) bool {
    // HF model IDs contain exactly one slash and don't look like file paths
    var slash_count: usize = 0;
    var slash_pos: usize = 0;

    for (path, 0..) |char, i| {
        if (char == '/') {
            slash_count += 1;
            slash_pos = i;
        }
    }

    // Must have exactly one slash
    if (slash_count != 1) return false;

    // Slash can't be at the start or end
    if (slash_pos == 0 or slash_pos == path.len - 1) return false;

    // First character shouldn't indicate a path (., /, ~)
    if (path[0] == '.' or path[0] == '/' or path[0] == '~') return false;

    // Check for Windows absolute path (e.g., C:/)
    if (path.len > 1 and path[1] == ':') return false;

    return true;
}

/// Get EOS token IDs from model's generation_config.json.
/// Returns array of token IDs. Caller must free with tokamino_tokens_free.
pub const EosTokenResult = extern struct {
    tokens: ?[*]u32,
    num_tokens: usize,
};

pub export fn tokamino_get_eos_tokens(
    model_dir: [*:0]const u8,
) callconv(.c) EosTokenResult {
    const dir = std.mem.span(model_dir);

    // Use shared module (same as main.zig)
    var config = gen_config_mod.loadGenerationConfig(allocator, dir) catch return EosTokenResult{ .tokens = null, .num_tokens = 0 };

    if (config.eos_token_ids.len == 0) {
        config.deinit(allocator);
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };
    }

    // Copy to owned array (config.deinit would free the original)
    const ids = allocator.alloc(u32, config.eos_token_ids.len) catch {
        config.deinit(allocator);
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };
    };
    @memcpy(ids, config.eos_token_ids);
    config.deinit(allocator);

    return EosTokenResult{ .tokens = ids.ptr, .num_tokens = ids.len };
}

/// Get EOS tokens from a session (includes <end_of_turn> and <eos> tokens added during session creation).
/// This is preferred over tokamino_get_eos_tokens which only returns base EOS tokens from config.
pub export fn tokamino_session_get_eos_tokens(
    handle: ?*SessionHandle,
) callconv(.c) EosTokenResult {
    const wrapper: *Session = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };

    if (wrapper.gen_config.eos_token_ids.len == 0) {
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };
    }

    // Copy to owned array
    const ids = allocator.alloc(u32, wrapper.gen_config.eos_token_ids.len) catch {
        return EosTokenResult{ .tokens = null, .num_tokens = 0 };
    };
    @memcpy(ids, wrapper.gen_config.eos_token_ids);

    return EosTokenResult{ .tokens = ids.ptr, .num_tokens = ids.len };
}

/// Apply chat template with a JSON array of messages.
/// Supports multi-turn conversations, tool calls, and assistant prefill.
/// Returns null-terminated formatted prompt string. Caller must free with tokamino_text_free.
/// Returns null if chat template is not available or fails.
pub export fn tokamino_apply_chat_template(
    handle: ?*SessionHandle,
    model_path: [*:0]const u8,
    messages_json: [*:0]const u8,
    add_generation_prompt: c_int,
) callconv(.c) ?[*:0]u8 {
    _ = handle; // Session not needed, but kept for API consistency

    const path = std.mem.span(model_path);
    const messages = std.mem.span(messages_json);

    const result = gen_config_mod.applyChatTemplate(
        allocator,
        path,
        messages,
        add_generation_prompt != 0,
    ) catch return null;

    const c_result = allocator.allocSentinel(u8, result.len, 0) catch {
        allocator.free(result);
        return null;
    };
    @memcpy(c_result, result);
    allocator.free(result);
    return c_result;
}

// =============================================================================
// Text Generation
// =============================================================================

/// C callback type for streaming tokens
pub const TokenCallbackC = *const fn (token_id: u32, user_data: ?*anyopaque) callconv(.c) void;

/// Wrapper to convert C callback to Zig callback
fn wrapCallback(token_id: u32, user_data: ?*anyopaque) void {
    // user_data contains pointer to the C callback info
    const info: *const struct { cb: TokenCallbackC, data: ?*anyopaque } = @ptrCast(@alignCast(user_data.?));
    info.cb(token_id, info.data);
}

/// Generate text from a prompt (blocking, returns all tokens at once).
pub export fn tokamino_generate(
    handle: ?*SessionHandle,
    prompt: [*:0]const u8,
    config: *const GenerateConfig,
) callconv(.c) GenerateResult {
    return tokamino_generate_stream(handle, prompt, config, null, null);
}

/// Generate text with streaming callback.
pub export fn tokamino_generate_stream(
    handle: ?*SessionHandle,
    prompt: [*:0]const u8,
    config: *const GenerateConfig,
    callback: ?TokenCallbackC,
    callback_data: ?*anyopaque,
) callconv(.c) GenerateResult {
    const wrapper: *Session = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return GenerateResult{
            .tokens = null,
            .num_tokens = 0,
            .prompt_len = 0,
            .generated_len = 0,
            .prefill_ns = 0,
            .decode_ns = 0,
            .error_msg = "Invalid session handle",
        };

    if (config.seed != 0) {
        wrapper.session.samp.prng = std.Random.DefaultPrng.init(config.seed);
    }

    // Convert sampling params
    const strategy: sampler.SamplingStrategy = switch (config.sampling.strategy) {
        0 => .greedy,
        1 => .top_k,
        2 => .top_p,
        else => .greedy,
    };

    // Setup callback wrapper if provided
    var callback_info: struct { cb: TokenCallbackC, data: ?*anyopaque } = undefined;
    const zig_callback: ?session_mod.TokenCallback = if (callback) |cb| blk: {
        callback_info = .{ .cb = cb, .data = callback_data };
        break :blk wrapCallback;
    } else null;

    const inference_config = session_mod.InferenceConfig{
        .max_new_tokens = @intCast(config.max_tokens),
        .sampling = .{
            .strategy = strategy,
            .temperature = config.sampling.temperature,
            .top_k = @intCast(config.sampling.top_k),
            .top_p = config.sampling.top_p,
        },
        .eos_token_ids = wrapper.gen_config.eos_token_ids,
        .bos_token_id = getBosTokenId(wrapper),
        .token_callback = zig_callback,
        .callback_data = if (callback != null) @ptrCast(&callback_info) else null,
    };

    const prompt_slice = std.mem.span(prompt);

    const state = wrapper.session.run(prompt_slice, inference_config) catch |err| {
        return GenerateResult{
            .tokens = null,
            .num_tokens = 0,
            .prompt_len = 0,
            .generated_len = 0,
            .prefill_ns = 0,
            .decode_ns = 0,
            .error_msg = @errorName(err),
        };
    };

    // Free logits (we don't expose them via C API for simplicity)
    allocator.free(state.final_logits);

    return GenerateResult{
        .tokens = state.tokens.ptr,
        .num_tokens = state.tokens.len,
        .prompt_len = state.prompt_len,
        .generated_len = state.generated_len,
        .prefill_ns = state.prefill_ns,
        .decode_ns = state.decode_ns,
        .error_msg = null,
    };
}

/// Free the result tokens.
pub export fn tokamino_result_free(result: *GenerateResult) callconv(.c) void {
    if (result.tokens) |tokens| {
        allocator.free(tokens[0..result.num_tokens]);
        result.tokens = null;
    }
}

// =============================================================================
// Encode / Decode API
// =============================================================================

/// Result structure for encode operation
pub const EncodeResult = extern struct {
    /// Pointer to token IDs (caller must free with tokamino_tokens_free)
    tokens: ?[*]u32,
    /// Number of tokens
    num_tokens: usize,
    /// Error message if failed (null on success)
    error_msg: ?[*:0]const u8,
};

/// Result structure for decode operation (supports null bytes in output)
pub const DecodeResult = extern struct {
    /// Pointer to decoded text (caller must free with tokamino_decode_result_free)
    text: ?[*]u8,
    /// Length of text in bytes (NOT null-terminated)
    text_len: usize,
    /// Error message if failed (null on success)
    error_msg: ?[*:0]const u8,
};

/// Encode text to token IDs.
/// Returns token array that must be freed with tokamino_tokens_free.
/// Takes explicit length to support text containing null bytes.
pub export fn tokamino_encode(
    handle: ?*SessionHandle,
    text: [*]const u8,
    text_len: usize,
) callconv(.c) EncodeResult {
    const wrapper: *Session = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return EncodeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "Invalid session handle",
        };

    const text_slice = text[0..text_len];
    const encoded = wrapper.session.tok.encodeSlice(text_slice) catch |err| {
        return EncodeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = @errorName(err),
        };
    };

    // Copy to C-allocated buffer (tokenizer uses its own allocator)
    const result = allocator.alloc(u32, encoded.len) catch {
        wrapper.session.tok.allocator.free(encoded);
        return EncodeResult{
            .tokens = null,
            .num_tokens = 0,
            .error_msg = "OutOfMemory",
        };
    };
    @memcpy(result, encoded);
    wrapper.session.tok.allocator.free(encoded);

    return EncodeResult{
        .tokens = result.ptr,
        .num_tokens = result.len,
        .error_msg = null,
    };
}

/// Free tokens returned by tokamino_encode.
pub export fn tokamino_tokens_free(tokens: ?[*]u32, num_tokens: usize) callconv(.c) void {
    if (tokens) |t| {
        allocator.free(t[0..num_tokens]);
    }
}

/// Decode token IDs to text. Returns DecodeResult with length (supports null bytes).
/// Caller must free with tokamino_decode_result_free.
pub export fn tokamino_decode(
    handle: ?*SessionHandle,
    tokens: [*]const u32,
    num_tokens: usize,
) callconv(.c) DecodeResult {
    const wrapper: *Session = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = "Invalid handle",
        };

    if (num_tokens == 0) {
        return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = null,
        };
    }

    const vocab_size = wrapper.session.backend.vocabSize();
    for (tokens[0..num_tokens]) |token| {
        // Sentinel used by generator APIs to signal end-of-stream / error.
        if (token == 0xFFFFFFFF) return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = "Invalid token (sentinel)",
        };
        // Tokenizer uses int32 IDs; avoid overflow / negative IDs reaching C code.
        if (token > std.math.maxInt(i32)) return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = "Token overflow",
        };
        // Defensive: prevent out-of-range vocab lookups in the tokenizer.
        if (@as(usize, token) >= vocab_size) return DecodeResult{
            .text = null,
            .text_len = 0,
            .error_msg = "Token out of vocab range",
        };
    }

    const text = wrapper.session.tok.decode(tokens[0..num_tokens]) catch return DecodeResult{
        .text = null,
        .text_len = 0,
        .error_msg = "Decode failed",
    };
    defer wrapper.session.tok.allocator.free(text);

    // Copy to C-allocated buffer (no null terminator needed)
    const result = allocator.alloc(u8, text.len) catch return DecodeResult{
        .text = null,
        .text_len = 0,
        .error_msg = "Allocation failed",
    };
    @memcpy(result, text);
    return DecodeResult{
        .text = result.ptr,
        .text_len = text.len,
        .error_msg = null,
    };
}

/// Free text returned by tokamino_decode (old null-terminated version).
pub export fn tokamino_text_free(text: ?[*:0]u8) callconv(.c) void {
    if (text) |t| {
        // Find length by scanning for null
        var len: usize = 0;
        while (t[len] != 0) : (len += 1) {}
        allocator.free(t[0 .. len + 1]); // +1 for null terminator
    }
}

/// Free DecodeResult returned by tokamino_decode or tokamino_tokenizer_decode.
pub export fn tokamino_decode_result_free(text: ?[*]u8, text_len: usize) callconv(.c) void {
    if (text) |t| {
        if (text_len > 0) {
            allocator.free(t[0..text_len]);
        }
    }
}

// =============================================================================
// Generator API (resumable token generation for Python iterators)
// =============================================================================

/// Opaque generator handle for C API
pub const GeneratorHandle = opaque {};

/// Configuration for generator
pub const GeneratorConfig = extern struct {
    /// Maximum tokens to generate
    max_tokens: u32 = 32,
    /// Sampling parameters
    sampling: SamplingParams = .{},
    /// Flush interval in milliseconds for text mode (default 100ms)
    flush_interval_ms: u32 = 100,
    /// EOS token IDs (optional override). If non-null with num_eos_tokens > 0,
    /// these tokens are used exclusively for end-of-sequence detection.
    /// If null or num_eos_tokens == 0, uses model/session default EOS tokens.
    eos_tokens: ?[*]const u32 = null,
    /// Number of EOS tokens in eos_tokens array
    num_eos_tokens: usize = 0,
};

const GeneratorState = struct {
    alloc: std.mem.Allocator,
    session: *session_mod.Session,
    eos_tokens: []const u32,
    bos_token_id: ?u32,
    sampling: sampler.SamplingConfig,
    max_new_tokens: usize,

    // Token buffer (prompt + generated tokens)
    tokens: []u32,
    token_len: usize,
    prompt_len: usize,
    gen_count: usize,

    logits: []f32,

    prefill_ns: u64,
    finished: bool,

    fn currentToken(self: *const GeneratorState) u32 {
        if (self.token_len == 0) return 0;
        return self.tokens[self.token_len - 1];
    }

    fn isFinished(self: *const GeneratorState) bool {
        return self.finished;
    }

    fn deinit(self: *GeneratorState) void {
        self.alloc.free(self.logits);
        self.alloc.free(self.tokens);
        // Note: eos_tokens are owned by the session, not copied, so don't free them
        self.alloc.destroy(self);
    }

    fn isEos(self: *const GeneratorState, token: u32) bool {
        for (self.eos_tokens) |eos_id| {
            if (token == eos_id) return true;
        }
        return false;
    }

    fn step(self: *GeneratorState) !?u32 {
        if (self.finished) return null;
        if (self.gen_count >= self.max_new_tokens) {
            self.finished = true;
            return null;
        }
        const last_token = self.tokens[self.token_len - 1];
        try self.session.backend.decode(last_token, self.token_len - 1, self.logits);
        const sampled = try self.session.samp.sample(self.logits, self.sampling);
        const token: u32 = @intCast(sampled);

        self.tokens[self.token_len] = token;
        self.token_len += 1;
        self.gen_count += 1;

        if (self.isEos(token) or self.gen_count >= self.max_new_tokens) {
            self.finished = true;
        }
        return token;
    }
};

/// Start a new token generator. Returns handle or null on error.
/// The generator yields the first token immediately after prefill.
pub export fn tokamino_generator_start(
    handle: ?*SessionHandle,
    prompt: [*:0]const u8,
    config: *const GeneratorConfig,
) callconv(.c) ?*GeneratorHandle {
    const wrapper: *Session = if (handle) |h|
        @ptrCast(@alignCast(h))
    else
        return null;

    if (config.max_tokens == 0) return null;

    const prompt_slice = std.mem.span(prompt);

    const strategy: sampler.SamplingStrategy = switch (config.sampling.strategy) {
        0 => .greedy,
        1 => .top_k,
        2 => .top_p,
        else => .greedy,
    };

    const sampling_config = sampler.SamplingConfig{
        .strategy = strategy,
        .temperature = config.sampling.temperature,
        .top_k = @intCast(config.sampling.top_k),
        .top_p = config.sampling.top_p,
    };

    const state = allocator.create(GeneratorState) catch return null;
    errdefer allocator.destroy(state);

    // Use config EOS tokens if provided, otherwise fall back to session defaults
    const eos_tokens_owned: []const u32 = if (config.eos_tokens != null and config.num_eos_tokens > 0)
        config.eos_tokens.?[0..config.num_eos_tokens]
    else
        wrapper.gen_config.eos_token_ids;

    const logits = allocator.alloc(f32, wrapper.session.backend.vocabSize()) catch return null;
    errdefer allocator.free(logits);

    // Encode prompt and allocate token buffer (prompt + max generated tokens).
    const encoded = wrapper.session.tok.encode(prompt_slice) catch return null;
    defer wrapper.session.tok.allocator.free(encoded);

    const bos_id = getBosTokenId(wrapper);
    var has_bos = bos_id != null;
    if (has_bos and encoded.len > 0 and encoded[0] == bos_id.?) {
        has_bos = false;
    }
    const bos_offset: usize = if (has_bos) 1 else 0;
    const prompt_len: usize = encoded.len + bos_offset;

    // Need at least one token to prefill (either from prompt or BOS)
    if (prompt_len == 0) return null;

    const max_len: usize = prompt_len + @as(usize, @intCast(config.max_tokens));

    const tokens = allocator.alloc(u32, max_len) catch return null;
    errdefer allocator.free(tokens);
    if (has_bos) tokens[0] = bos_id.?;
    @memcpy(tokens[bos_offset..prompt_len], encoded);

    // Prefill
    var timer = std.time.Timer.start() catch return null;
    wrapper.session.backend.prefill(tokens[0..prompt_len], logits) catch return null;
    const prefill_ns = timer.read();

    // Sample first token
    const sampled = wrapper.session.samp.sample(logits, sampling_config) catch return null;
    const first_token: u32 = @intCast(sampled);

    tokens[prompt_len] = first_token;

    state.* = .{
        .alloc = allocator,
        .session = &wrapper.session,
        .eos_tokens = eos_tokens_owned,
        .bos_token_id = bos_id,
        .sampling = sampling_config,
        .max_new_tokens = @intCast(config.max_tokens),
        .tokens = tokens,
        .token_len = prompt_len + 1,
        .prompt_len = prompt_len,
        .gen_count = 1,
        .logits = logits,
        .prefill_ns = prefill_ns,
        .finished = (config.max_tokens <= 1) or (eos_tokens_owned.len > 0 and blk: {
            for (eos_tokens_owned) |eos_id| {
                if (eos_id == first_token) break :blk true;
            }
            break :blk false;
        }),
    };

    return @ptrCast(state);
}

/// Get the current (last generated) token.
/// Call this after start() to get the first token, then after each next() call.
pub export fn tokamino_generator_current(gen: ?*GeneratorHandle) callconv(.c) u32 {
    if (gen) |g| {
        const state: *GeneratorState = @ptrCast(@alignCast(g));
        return state.currentToken();
    }
    return 0;
}

/// Generate next token. Returns the token ID, or 0xFFFFFFFF when done.
pub export fn tokamino_generator_next(gen: ?*GeneratorHandle) callconv(.c) u32 {
    if (gen) |g| {
        const state: *GeneratorState = @ptrCast(@alignCast(g));
        const token = state.step() catch {
            state.finished = true;
            return 0xFFFFFFFF;
        };
        if (token == null) {
            state.finished = true;
            return 0xFFFFFFFF;
        }
        return token.?;
    }
    return 0xFFFFFFFF;
}

/// Check if generator is finished.
pub export fn tokamino_generator_finished(gen: ?*GeneratorHandle) callconv(.c) bool {
    if (gen) |g| {
        const state: *GeneratorState = @ptrCast(@alignCast(g));
        return state.isFinished();
    }
    return true;
}

/// Get count of tokens generated so far (excluding prompt).
pub export fn tokamino_generator_generated_count(gen: ?*GeneratorHandle) callconv(.c) usize {
    if (gen) |g| {
        const state: *GeneratorState = @ptrCast(@alignCast(g));
        return state.gen_count;
    }
    return 0;
}

/// Free the generator.
pub export fn tokamino_generator_free(gen: ?*GeneratorHandle) callconv(.c) void {
    if (gen) |g| {
        const state: *GeneratorState = @ptrCast(@alignCast(g));
        state.deinit();
    }
}

// =============================================================================
// Model Description API
// =============================================================================

/// Model information returned by describe
pub const ModelInfo = extern struct {
    // Core architecture
    vocab_size: i32,
    hidden_size: i32,
    num_layers: i32,
    num_heads: i32,
    num_kv_heads: i32,
    intermediate_size: i32,
    max_seq_len: i32,
    head_dim: i32,

    // RoPE parameters
    rope_theta: f32,
    norm_eps: f32,

    // Quantization
    quant_bits: i32, // 0 = no quantization, 4 = 4-bit, 8 = 8-bit, 16 = fp16
    quant_group_size: i32,

    // Architecture info (null-terminated strings, caller must free)
    model_type: ?[*:0]u8, // e.g., "qwen3", "llama"
    architecture: ?[*:0]u8, // e.g., "Qwen3ForCausalLM"

    // Flags
    tie_word_embeddings: bool,
    use_gelu: bool,

    // MoE
    num_experts: i32,
    experts_per_token: i32,

    // Error (null on success)
    error_msg: ?[*:0]const u8,
};

/// Get model information from a model directory.
/// Caller must free model_type and architecture strings with tokamino_text_free.
pub export fn tokamino_describe(model_path: [*:0]const u8) callconv(.c) ModelInfo {
    // Use the same resolution as tokamino_resolve_model_path (handles HF downloads)
    const resolved_ptr = tokamino_resolve_model_path(model_path);
    if (resolved_ptr == null) {
        return errorResult("Failed to resolve model path");
    }
    const resolved_path = std.mem.span(resolved_ptr.?);
    defer tokamino_text_free(resolved_ptr);

    // Build config.json path
    const config_path = std.fs.path.join(allocator, &.{ resolved_path, "config.json" }) catch {
        return errorResult("OutOfMemory");
    };
    defer allocator.free(config_path);

    // Check architecture first
    const arch_check = io.config.checkArchitecture(allocator, config_path) catch {
        return errorResult("Failed to read config.json");
    };

    // Load full config
    const config = io.config.loadConfig(allocator, config_path) catch |err| {
        return switch (err) {
            error.InvalidJson => errorResult("Invalid JSON in config.json"),
            error.MissingField => errorResult("Missing required field in config.json"),
            error.InvalidValue => errorResult("Invalid value in config.json"),
            else => errorResult("Failed to load config"),
        };
    };

    // Determine quantization bits from quant_method
    const quant_bits: i32 = switch (config.quant_method) {
        .none => 16, // FP16/BF16
        .gaffine => config.gaffine_bits,
        .mxfp4 => 4,
        .native => 4, // K-quant (mixed precision, report as 4-bit)
    };

    // Copy model_type string
    var model_type_str: ?[*:0]u8 = null;
    if (arch_check.getModelType()) |mt| {
        if (allocator.allocSentinel(u8, mt.len, 0)) |buf| {
            @memcpy(buf, mt);
            model_type_str = buf;
        } else |_| {}
    }

    // Copy architecture string
    var arch_str: ?[*:0]u8 = null;
    if (arch_check.getArchitecture()) |arch| {
        if (allocator.allocSentinel(u8, arch.len, 0)) |buf| {
            @memcpy(buf, arch);
            arch_str = buf;
        } else |_| {}
    }

    return ModelInfo{
        .vocab_size = config.vocab_size,
        .hidden_size = config.d_model,
        .num_layers = config.n_layers,
        .num_heads = config.n_heads,
        .num_kv_heads = config.n_kv_groups,
        .intermediate_size = config.d_ff,
        .max_seq_len = config.max_seq_len,
        .head_dim = config.head_dim,
        .rope_theta = config.rope_theta,
        .norm_eps = config.norm_eps,
        .quant_bits = quant_bits,
        .quant_group_size = config.gaffine_group_size,
        .model_type = model_type_str,
        .architecture = arch_str,
        .tie_word_embeddings = config.tie_word_embeddings,
        .use_gelu = config.use_gelu,
        .num_experts = config.num_experts,
        .experts_per_token = config.experts_per_token,
        .error_msg = null,
    };
}

fn errorResult(msg: [*:0]const u8) ModelInfo {
    return ModelInfo{
        .vocab_size = 0,
        .hidden_size = 0,
        .num_layers = 0,
        .num_heads = 0,
        .num_kv_heads = 0,
        .intermediate_size = 0,
        .max_seq_len = 0,
        .head_dim = 0,
        .rope_theta = 0,
        .norm_eps = 0,
        .quant_bits = 0,
        .quant_group_size = 0,
        .model_type = null,
        .architecture = null,
        .tie_word_embeddings = false,
        .use_gelu = false,
        .num_experts = 0,
        .experts_per_token = 0,
        .error_msg = msg,
    };
}

/// Free model info strings (model_type and architecture).
pub export fn tokamino_model_info_free(info: *ModelInfo) callconv(.c) void {
    if (info.model_type) |mt| {
        var len: usize = 0;
        while (mt[len] != 0) : (len += 1) {}
        allocator.free(mt[0 .. len + 1]);
        info.model_type = null;
    }
    if (info.architecture) |arch| {
        var len: usize = 0;
        while (arch[len] != 0) : (len += 1) {}
        allocator.free(arch[0 .. len + 1]);
        info.architecture = null;
    }
}

// =============================================================================
// Template Rendering
// =============================================================================

const template_engine = text_root.template_engine;

/// Thread-local error message for template operations
threadlocal var template_error_msg: ?[]const u8 = null;

/// Convert std.json.Value to template.Value recursively
fn jsonToTemplateValue(json_val: std.json.Value) template_engine.Value {
    return switch (json_val) {
        .null => .none,
        .bool => |b| .{ .boolean = b },
        .integer => |i| .{ .integer = i },
        .float => |f| .{ .float = f },
        .string => |s| .{ .string = s },
        .array => |arr| {
            const items = allocator.alloc(template_engine.Value, arr.items.len) catch return .none;
            for (arr.items, 0..) |item, i| {
                items[i] = jsonToTemplateValue(item);
            }
            return .{ .array = items };
        },
        .object => |obj| {
            var map = std.StringHashMapUnmanaged(template_engine.Value){};
            var iter = obj.iterator();
            while (iter.next()) |entry| {
                map.put(allocator, entry.key_ptr.*, jsonToTemplateValue(entry.value_ptr.*)) catch continue;
            }
            return .{ .map = map };
        },
        .number_string => |s| {
            // Try to parse as integer first, then float
            if (std.fmt.parseInt(i64, s, 10)) |i| {
                return .{ .integer = i };
            } else |_| {
                if (std.fmt.parseFloat(f64, s)) |f| {
                    return .{ .float = f };
                } else |_| {
                    return .{ .string = s };
                }
            }
        },
    };
}

/// Render a Jinja2 template with JSON variables.
/// Returns null-terminated rendered string. Caller must free with tokamino_text_free.
/// On error, returns null and error can be retrieved with tokamino_template_error.
pub export fn tokamino_template_render(
    template_str: [*:0]const u8,
    json_vars: [*:0]const u8,
) callconv(.c) ?[*:0]u8 {
    // Clear previous error
    if (template_error_msg) |msg| {
        allocator.free(msg);
        template_error_msg = null;
    }

    const template = std.mem.span(template_str);
    const json_str = std.mem.span(json_vars);

    // Parse JSON variables
    const parsed = std.json.parseFromSlice(std.json.Value, allocator, json_str, .{}) catch |err| {
        setTemplateError("JSON parse error: {s}", .{@errorName(err)});
        return null;
    };
    defer parsed.deinit();

    // Build template context from JSON object
    var ctx = template_engine.Context.init(allocator);
    defer ctx.deinit();

    if (parsed.value == .object) {
        var iter = parsed.value.object.iterator();
        while (iter.next()) |entry| {
            const val = jsonToTemplateValue(entry.value_ptr.*);
            ctx.set(entry.key_ptr.*, val) catch continue;
        }
    }

    // Render template
    const result = template_engine.render(allocator, template, &ctx) catch |err| {
        setTemplateError("Template error: {s}", .{@errorName(err)});
        return null;
    };

    // Copy to null-terminated C string
    const c_result = allocator.allocSentinel(u8, result.len, 0) catch {
        allocator.free(result);
        return null;
    };
    @memcpy(c_result, result);
    allocator.free(result);

    return c_result;
}

fn setTemplateError(comptime fmt: []const u8, args: anytype) void {
    const msg = std.fmt.allocPrint(allocator, fmt, args) catch return;
    // Allocate with null terminator
    const msg_z = allocator.allocSentinel(u8, msg.len, 0) catch {
        allocator.free(msg);
        return;
    };
    @memcpy(msg_z, msg);
    allocator.free(msg);
    template_error_msg = msg_z;
}

/// Get the last template error message.
/// Returns null if no error occurred.
pub export fn tokamino_template_error() callconv(.c) ?[*:0]const u8 {
    if (template_error_msg) |msg| {
        // Return as null-terminated (allocPrintZ already adds null)
        return @ptrCast(msg.ptr);
    }
    return null;
}
