//! Tokamino - High-performance Zig library for LLMs, Vector Search, and Tokenization
//!
//! This is the unified entry point that re-exports all public modules.

const std = @import("std");
const builtin = @import("builtin");

// =============================================================================
// Public API Exports
// =============================================================================

/// Core tensor operations and memory management
pub const core = struct {
    pub const tensor = @import("tensor.zig");
    pub const dtype = @import("dtype.zig");
    pub const device = @import("compute/device.zig");
    pub const parallel = @import("compute/parallel.zig");
    pub const ops = @import("compute/ops/root.zig");
    pub const simd = @import("compute/simd/root.zig");
};

/// Text processing and tokenization (from tokarai)
pub const text = @import("text/root.zig");

/// Neural network layers and model components
pub const nn = struct {
    pub const model = @import("runtime/backend/cpu/block_kernels.zig");
    pub const attention = @import("runtime/backend/cpu/kernels/attention.zig");
    pub const ffn = @import("runtime/backend/cpu/kernels/ffn.zig");
    pub const sampling = @import("runtime/sampling.zig");
};

/// I/O utilities for loading models and configs
pub const io = struct {
    pub const storage = @import("io/root.zig").storage;
    pub const internal = @import("io/internal.zig");
};

/// Model loading (via io subsystem)
pub const models = struct {
    pub const dispatcher = @import("io/loader/root.zig");
};

/// Compute graph parsing and compilation
pub const graph = @import("graph/root.zig");

/// Runtime - session management for inference
pub const runtime = @import("runtime/root.zig");
pub const session = runtime.session;

/// Generation configuration loading
pub const generation_config = @import("io/config/generation.zig");

/// Model conversion (native, MLX)
pub const convert = @import("io/internal.zig").convert;

/// CLI utilities
pub const cli = struct {
    pub const progress = @import("cli/progress.zig");
    pub const json_helpers = @import("cli/json_helpers.zig");
};

// =============================================================================
// CLI Application
// =============================================================================

const log = std.log.scoped(.tokamino);

/// Reserved subcommands that should not trigger implicit generate
const reserved_commands = [_][]const u8{
    "convert",
    "generate",
    "tokenize",
    "help",
    "--help",
    "-h",
};

fn isReservedCommand(arg: []const u8) bool {
    for (reserved_commands) |cmd| {
        if (std.mem.eql(u8, arg, cmd)) return true;
    }
    return false;
}

pub fn main() !void {
    if (std.posix.getenv("TOKAMINO_DEBUG_BUFFERS") != null) {
        std.debug.print("[main] start\n", .{});
    }
    // Use C allocator for release, GPA for debug (leak detection)
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = if (builtin.mode == .Debug) gpa.allocator() else std.heap.c_allocator;

    const stdout_file = std.fs.File.stdout();
    const stdin_file = std.fs.File.stdin();

    var args = try std.process.argsWithAllocator(allocator);
    defer args.deinit();
    _ = args.next(); // skip program name

    // Check if stdin is a pipe (not a TTY)
    const stdin_is_pipe = !stdin_file.isTty();

    const first_arg = args.next();

    // If stdin is piped and first arg is not a reserved command, implicitly run generate
    if (stdin_is_pipe) {
        if (first_arg) |arg| {
            if (!isReservedCommand(arg)) {
                // Not a reserved command - treat as generate flags/prompt
                // Create a new iterator that includes the first arg
                var args_with_first = try std.process.argsWithAllocator(allocator);
                defer args_with_first.deinit();
                _ = args_with_first.next(); // skip program name
                // Don't skip first arg - pass it to cmdGenerate
                try cmdGenerate(allocator, &args_with_first, stdout_file);
                return;
            }
        } else {
            // No args at all with piped input - run generate (will use MODEL_PATH or error)
            try cmdGenerate(allocator, &args, stdout_file);
            return;
        }
    }

    const command = first_arg orelse {
        try printUsage(stdout_file);
        return;
    };

    // Dispatch to subcommands
    if (std.mem.eql(u8, command, "generate")) {
        try cmdGenerate(allocator, &args, stdout_file);
    } else if (std.mem.eql(u8, command, "tokenize")) {
        try cmdTokenize(allocator, &args, stdout_file);
    } else if (std.mem.eql(u8, command, "convert")) {
        try cmdConvert(allocator, &args, stdout_file);
    } else if (std.mem.eql(u8, command, "help") or std.mem.eql(u8, command, "--help") or std.mem.eql(u8, command, "-h")) {
        try printUsage(stdout_file);
    } else {
        var buf: [256]u8 = undefined;
        const msg = std.fmt.bufPrint(&buf, "Unknown command: {s}\n\n", .{command}) catch return;
        try stdout_file.writeAll(msg);
        try printUsage(stdout_file);
    }
}

fn printUsage(file: std.fs.File) !void {
    try file.writeAll(
        \\Tokamino - High-performance LLM inference library
        \\
        \\Usage: tokamino <command> [options]
        \\       echo "prompt" | tokamino [options]
        \\
        \\Commands:
        \\  generate -m <model_dir> <prompt...>           Generate text from a local model
        \\  generate --hf <org/model> <prompt...>         Download from HuggingFace and generate
        \\  convert <model_dir> [options]                 Convert/quantize model
        \\  help                                          Show this help message
        \\
        \\Environment variables:
        \\  MODEL_PATH    Default model path or HuggingFace ID (e.g., Qwen/Qwen3-0.6B)
        \\  TOKENS=<n>    Max tokens to generate (default: 16)
        \\  TEMP=<f>      Sampling temperature (default: 1.0, 0=greedy)
        \\  TOP_K=<n>     Top-k sampling (default: 50)
        \\  HF_TOKEN      HuggingFace API token for private models
        \\
        \\Options for convert:
        \\  --format <native|mlx>  Output format (default: native)
        \\  --quant <type>         K-quant type: q4_0, q4_k_m, q5_k, q6_k, q8_0
        \\  --bits <4|8>           Shorthand for --quant (4=q4_k_m, 8=q8_0)
        \\  --group-size <n>       MLX format group size (default: 64)
        \\  --output <dir>         Output directory (default: models)
        \\  -f, --force            Overwrite existing output
        \\
        \\Examples:
        \\  tokamino generate -m ./models/Qwen3-0.6B "What is the capital of France?"
        \\  tokamino generate --hf Qwen/Qwen3-0.6B "What is the capital of France?"
        \\  MODEL_PATH=Qwen/Qwen3-0.6B tokamino generate "What is 2+2?"
        \\  echo "Tell me a joke" | tokamino -m ./models/Qwen3-0.6B
        \\  tokamino convert --hf Qwen/Qwen3-0.6B --bits 4
        \\  tokamino convert --hf Qwen/Qwen3-0.6B --format mlx --bits 4
        \\
    );
}

/// Resolve a model path, handling cache format (models--org--name/snapshots/).
fn resolveModelPath(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return io.storage.resolver.resolveSnapshot(allocator, path);
}

/// Check if a path looks like a HuggingFace model ID (e.g., "mlx-community/Phi-4-mini-instruct-4bit").
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

    // Check it doesn't start with . or / (relative/absolute paths)
    if (path[0] == '.' or path[0] == '/') return false;

    return true;
}

// Use shared generation config module
const gen_config_mod = generation_config;
const GenerationConfig = gen_config_mod.GenerationConfig;

fn addEosFromTokenizer(allocator: std.mem.Allocator, tok: *text.Tokenizer, cfg: *GenerationConfig, comptime token_str: []const u8) void {
    const ids = tok.encode(token_str) catch return;
    defer tok.allocator.free(ids);
    if (ids.len != 1) return;
    gen_config_mod.addEosTokenId(allocator, cfg, ids[0]) catch return;
}

fn cmdGenerate(allocator: std.mem.Allocator, args: *std.process.ArgIterator, stdout: std.fs.File) !void {
    // Set up SIGINT handler for graceful Ctrl+C cancellation
    const sigaction_handler = struct {
        fn handler(_: c_int) callconv(.c) void {
            // Write newline to clear ^C visual artifact and exit cleanly
            const stdout_fd = std.fs.File.stdout();
            stdout_fd.writeAll("\n") catch {};
            std.process.exit(0);
        }
    };
    const sa = std.posix.Sigaction{
        .handler = .{ .handler = sigaction_handler.handler },
        .mask = std.posix.sigemptyset(),
        .flags = 0,
    };
    std.posix.sigaction(std.posix.SIG.INT, &sa, null);

    const usage =
        \\Usage: tokamino generate -m <model_dir> [options] <prompt...>
        \\       tokamino generate --hf <org/model> [options] <prompt...>
        \\       echo "prompt" | tokamino -m <model_dir>
        \\
        \\Generate text from a prompt using a language model.
        \\
        \\Model Source (one required):
        \\  -m, --model <dir>   Path to local model directory containing:
        \\                        - config.json
        \\                        - model.safetensors
        \\                        - tokenizer.json
        \\                      Supports cache format (models--org--name/snapshots/)
        \\  --hf <org/model>    Download model from HuggingFace Hub (e.g., Qwen/Qwen3-0.6B)
        \\
        \\Prompt Input:
        \\  <prompt...>         Text prompt as command line arguments
        \\  stdin               Piped input (combined with args if both provided)
        \\
        \\Options:
        \\  --no-chat         Skip chat template, use raw prompt directly
        \\  --no-stream       Disable streaming output (wait for full response)
        \\  -s, --system MSG  System message for chat mode (default: "You are a helpful assistant.")
        \\  -v, --verbose     Show full raw output including all markup
        \\
        \\Chat templates are automatically applied if tokenizer_config.json contains
        \\a chat_template field. Use --no-chat to disable this behavior.
        \\
        \\Environment Variables:
        \\  MODEL_PATH     Default model path or HuggingFace ID (e.g., Qwen/Qwen3-0.6B)
        \\  TOKENS=N       Max tokens to generate (default: 16)
        \\  TEMP=F         Sampling temperature (from generation_config.json, 0=greedy)
        \\  TOP_K=N        Top-k sampling (from generation_config.json)
        \\  TOP_P=F        Nucleus sampling threshold (from generation_config.json)
        \\  THREADS=N      Number of threads (default: CPU count)
        \\  HF_TOKEN       HuggingFace API token for private models
        \\
        \\Examples:
        \\  tokamino generate -m ./models/qwen "What is 2+2?"
        \\  tokamino generate --hf Qwen/Qwen3-0.6B "What is 2+2?"
        \\  MODEL_PATH=Qwen/Qwen3-0.6B tokamino generate "Tell me a story"
        \\  echo "Why is the sky blue?" | tokamino -m ./models/qwen
        \\  cat code.py | tokamino -m ./models/qwen "Fix this code:"
        \\
    ;

    // First pass: collect all arguments and identify flags
    var model_path_flag: ?[]const u8 = null; // From -m/--model
    var hf_model_id: ?[]const u8 = null; // From --hf
    var no_chat = false;
    var no_stream = false;
    var verbose = false;
    var system_msg: []const u8 = "You are a helpful assistant.";
    var system_msg_is_default = true;
    var prompt_buf = std.ArrayListUnmanaged(u8){};
    defer prompt_buf.deinit(allocator);

    // Parse all arguments
    while (args.next()) |arg| {
        if (std.mem.eql(u8, arg, "-m") or std.mem.eql(u8, arg, "--model")) {
            model_path_flag = args.next();
        } else if (std.mem.eql(u8, arg, "--hf") or std.mem.eql(u8, arg, "-hf")) {
            hf_model_id = args.next();
        } else if (std.mem.eql(u8, arg, "--no-chat")) {
            no_chat = true;
        } else if (std.mem.eql(u8, arg, "--no-stream")) {
            no_stream = true;
        } else if (std.mem.eql(u8, arg, "-v") or std.mem.eql(u8, arg, "--verbose")) {
            verbose = true;
        } else if (std.mem.eql(u8, arg, "--system") or std.mem.eql(u8, arg, "-s")) {
            system_msg = args.next() orelse {
                try stdout.writeAll("Error: --system/-s requires a message\n");
                return;
            };
            system_msg_is_default = false;
        } else if (std.mem.eql(u8, arg, "--help") or std.mem.eql(u8, arg, "-h")) {
            try stdout.writeAll(usage);
            return;
        } else {
            // Not a flag, add to prompt
            if (prompt_buf.items.len > 0) try prompt_buf.append(allocator, ' ');
            try prompt_buf.appendSlice(allocator, arg);
        }
    }

    // Read stdin if it's a pipe (not a TTY)
    var stdin_content: ?[]u8 = null;
    defer if (stdin_content) |sc| allocator.free(sc);

    const stdin_for_prompt = std.fs.File.stdin();
    if (!stdin_for_prompt.isTty()) {
        // Read all stdin content
        stdin_content = stdin_for_prompt.readToEndAlloc(allocator, 10 * 1024 * 1024) catch |err| {
            log.warn("Failed to read stdin: {s}", .{@errorName(err)});
            return;
        };

        if (stdin_content) |content| {
            // Trim trailing whitespace from stdin
            var trimmed = content;
            while (trimmed.len > 0 and (trimmed[trimmed.len - 1] == '\n' or trimmed[trimmed.len - 1] == '\r' or trimmed[trimmed.len - 1] == ' ')) {
                trimmed = trimmed[0 .. trimmed.len - 1];
            }

            if (trimmed.len > 0) {
                // Append stdin to prompt (with space separator if args were provided)
                if (prompt_buf.items.len > 0) try prompt_buf.append(allocator, ' ');
                try prompt_buf.appendSlice(allocator, trimmed);
            }
        }
    }

    // Determine model source: CLI flags take priority over MODEL_PATH env var
    var model_arg: []const u8 = undefined;
    var hf_model_path: ?[]const u8 = null;
    defer if (hf_model_path) |p| allocator.free(p);
    var use_hf = false;

    if (hf_model_id) |hf_id| {
        // --hf flag provided
        use_hf = true;
        model_arg = hf_id;
    } else if (model_path_flag) |path| {
        // -m/--model flag provided
        model_arg = path;
    } else if (std.posix.getenv("MODEL_PATH")) |env_path| {
        // Fall back to MODEL_PATH environment variable
        model_arg = env_path;
    } else {
        // No model specified at all
        if (prompt_buf.items.len == 0) {
            // No prompt either - show usage
            try stdout.writeAll(usage);
        } else {
            try stdout.writeAll("Error: No model specified. Use -m/--model, --hf, or set the MODEL_PATH environment variable.\n");
        }
        return;
    }

    // Download from HuggingFace if needed
    // Smart detection: if path doesn't exist locally and looks like a HF model ID, auto-download
    if (!use_hf) {
        // Check if path exists locally
        if (std.fs.cwd().access(model_arg, .{})) |_| {
            // Path exists, use as-is
        } else |_| {
            // Path doesn't exist - check if it looks like a HuggingFace model ID
            if (isHuggingFaceModelId(model_arg)) {
                // Check cache first
                if (io.storage.getCachedPath(allocator, model_arg) catch null) |cached_path| {
                    hf_model_path = cached_path;
                    model_arg = hf_model_path.?;
                } else {
                    // Not in cache, need to download
                    use_hf = true;
                }
            }
        }
    }

    if (use_hf) {
        io.storage.globalInit();
        defer io.storage.globalCleanup();

        const hf_token = std.posix.getenv("HF_TOKEN");
        var progress_state = cli.progress.DownloadProgress.init(stdout);

        try stdout.writeAll("Downloading model from HuggingFace Hub...\n");

        hf_model_path = io.storage.downloadModel(allocator, model_arg, .{
            .token = hf_token,
            .progress_callback = cli.progress.DownloadProgress.progressCallback,
            .progress_data = @ptrCast(&progress_state),
            .file_start_callback = cli.progress.DownloadProgress.fileStartCallback,
        }) catch |err| {
            try stdout.writeAll("\n");
            var buf: [256]u8 = undefined;
            const msg = std.fmt.bufPrint(&buf, "Failed to download model: {s}\n", .{@errorName(err)}) catch return;
            try stdout.writeAll(msg);
            if (err == error.Unauthorized) {
                try stdout.writeAll("Hint: Set HF_TOKEN environment variable for private models\n");
            } else if (err == error.ModelNotFound) {
                try stdout.writeAll("Hint: Check the model ID (format: org/model, e.g., Qwen/Qwen3-0.6B)\n");
            }
            return;
        };

        progress_state.printDone();
        model_arg = hf_model_path.?;
    }

    // Resolve cache path if needed (models--org--name/snapshots/)
    const model_dir = try resolveModelPath(allocator, model_arg);
    defer allocator.free(model_dir);

    // Load generation config from model directory (uses shared module)
    var gen_config = try gen_config_mod.loadGenerationConfig(allocator, model_dir);
    defer gen_config.deinit(allocator);

    // Parse environment variables (override generation_config.json if set)
    const max_tokens = if (std.posix.getenv("TOKENS")) |env|
        std.fmt.parseInt(usize, env, 10) catch 16
    else
        16;
    const temp: f32 = if (std.posix.getenv("TEMP")) |env|
        std.fmt.parseFloat(f32, env) catch gen_config.temperature
    else
        gen_config.temperature;
    const top_k = if (std.posix.getenv("TOP_K")) |env|
        std.fmt.parseInt(usize, env, 10) catch gen_config.top_k
    else
        gen_config.top_k;
    const top_p = if (std.posix.getenv("TOP_P")) |env|
        std.fmt.parseFloat(f32, env) catch gen_config.top_p
    else
        gen_config.top_p;

    var sampling = nn.sampling.SamplingConfig{ .strategy = .greedy };
    if (temp > 0 and gen_config.do_sample) {
        sampling = .{
            .strategy = .top_k,
            .temperature = temp,
            .top_k = top_k,
            .top_p = top_p,
        };
    }

    // Check that we have a prompt
    if (prompt_buf.items.len == 0) {
        try stdout.writeAll("Error: generate requires a prompt\n");
        return;
    }

    const user_prompt = prompt_buf.items;

    // Early check: discover model files before attempting chat template
    // This catches missing files early
    var bundle = io.storage.resolve(allocator, model_dir) catch |err| {
        log.err("Failed to find model files: {s}", .{@errorName(err)});
        var err_buf: [512]u8 = undefined;
        const err_msg = std.fmt.bufPrint(&err_buf, "Make sure {s} contains: config.json, *.safetensors, tokenizer.json\n", .{model_dir}) catch return;
        try stdout.writeAll(err_msg);
        return;
    };
    defer bundle.deinit();

    // Initialize graph registry and load architecture definitions from _graphs/
    graph.init(allocator);
    io.internal.loader.loadArchitectureDefinitions(allocator);

    // Early check: verify architecture is supported (now checks against runtime registry)
    const arch_check = io.internal.config.checkArchitecture(allocator, bundle.config_path()) catch io.internal.config.ArchitectureCheck{ .supported = true };
    if (!arch_check.supported) {
        if (arch_check.getArchitecture()) |arch| {
            log.err("Unsupported model architecture: {s}", .{arch});
            var err_buf: [256]u8 = undefined;
            const err_msg = std.fmt.bufPrint(&err_buf, "Error: Model architecture '{s}' is not supported.\n", .{arch}) catch return;
            try stdout.writeAll(err_msg);
        } else if (arch_check.getModelType()) |mt| {
            log.err("Unsupported model type: {s}", .{mt});
            var err_buf: [256]u8 = undefined;
            const err_msg = std.fmt.bufPrint(&err_buf, "Error: Model type '{s}' is not supported.\n", .{mt}) catch return;
            try stdout.writeAll(err_msg);
        }
        // List available architectures from the runtime registry
        try stdout.writeAll("Run 'make graphs' to generate architecture definitions.\n");
        return;
    }

    // Gemma3 instruction models tend to work best without any default system prompt.
    // Keep user-specified system messages unchanged.
    if (!no_chat and system_msg_is_default) {
        if (arch_check.getArchitecture()) |arch| {
            if (std.mem.startsWith(u8, arch, "Gemma3")) {
                system_msg = "";
            }
        }
    }

    // Apply chat template automatically if model has one (unless --raw)
    var formatted_prompt: []const u8 = user_prompt;
    var formatted_prompt_owned = false;
    defer if (formatted_prompt_owned) allocator.free(formatted_prompt);

    if (!no_chat) {
        // Build messages JSON from system_msg and user_prompt
        const messages_json = blk: {
            if (system_msg.len > 0) {
                break :blk std.fmt.allocPrint(allocator, "[{{\"role\":\"system\",\"content\":{f}}},{{\"role\":\"user\",\"content\":{f}}}]", .{
                    std.json.fmt(system_msg, .{}),
                    std.json.fmt(user_prompt, .{}),
                }) catch break :blk null;
            } else {
                break :blk std.fmt.allocPrint(allocator, "[{{\"role\":\"user\",\"content\":{f}}}]", .{
                    std.json.fmt(user_prompt, .{}),
                }) catch break :blk null;
            }
        };
        defer if (messages_json) |m| allocator.free(m);

        // Try to apply chat template
        if (messages_json) |mj| {
            if (gen_config_mod.applyChatTemplate(allocator, model_dir, mj, true)) |result| {
                formatted_prompt = result;
                formatted_prompt_owned = true;
                const show_len = @min(formatted_prompt.len, 500);
                log.debug("Rendered template ({} chars): {s}...", .{ formatted_prompt.len, formatted_prompt[0..show_len] });
            } else |err| {
                if (err != error.MissingChatTemplate and err != error.FileNotFound) {
                    log.warn("Chat template failed: {s}, using raw prompt", .{@errorName(err)});
                }
            }
        }
    }

    const prompt = formatted_prompt;

    var sess = blk: {
        // Use in-memory tokenizer JSON if available
        if (bundle.tokenizer_json()) |json| {
            break :blk session.Session.initWithJson(allocator, bundle.config_path(), bundle.weights_path(), json, 42) catch |err| {
                log.err("Failed to init session: {s}", .{@errorName(err)});
                var err_buf: [512]u8 = undefined;
                const err_msg = std.fmt.bufPrint(&err_buf, "Make sure {s} contains: config.json, model.safetensors, tokenizer.json\n", .{model_dir}) catch return;
                try stdout.writeAll(err_msg);
                return;
            };
        } else {
            break :blk session.Session.init(allocator, bundle.config_path(), bundle.weights_path(), bundle.tokenizer_path(), 42) catch |err| {
                log.err("Failed to init session: {s}", .{@errorName(err)});
                var err_buf: [512]u8 = undefined;
                const err_msg = std.fmt.bufPrint(&err_buf, "Make sure {s} contains: config.json, model.safetensors, tokenizer.json\n", .{model_dir}) catch return;
                try stdout.writeAll(err_msg);
                return;
            };
        }
    };
    defer sess.deinit();

    // Ensure we stop on the model's turn delimiter as well as <eos> when present.
    // This fixes Gemma-family models that emit "<end_of_turn>" as regular text when
    // generation_config/config.json are missing or incomplete.
    if (!no_chat) addEosFromTokenizer(allocator, &sess.tok, &gen_config, "<end_of_turn>");
    addEosFromTokenizer(allocator, &sess.tok, &gen_config, "<eos>");

    // Set up streaming if enabled
    const stream_enabled = !no_stream;

    // Streamer handles <think> tag dimming and chat marker stripping
    // In verbose mode, pass through raw output without processing
    const text_internal = @import("text/internal.zig");
    var streamer = text_internal.streaming.Streamer.initWithConfig(
        allocator,
        &sess.tok,
        stdout,
        .{ .strip_chat_markers = true, .raw_mode = verbose },
    );
    defer streamer.deinit();

    // Wrapper context for the callback
    const StreamCtx = struct {
        streamer: *text_internal.streaming.Streamer,
        eos_token_ids: []const u32,

        fn callback(token_id: u32, user_data: ?*anyopaque) void {
            if (user_data) |ptr| {
                const self: *@This() = @ptrCast(@alignCast(ptr));
                for (self.eos_token_ids) |eos_id| {
                    if (token_id == eos_id) return;
                }
                self.streamer.feed(token_id) catch {};
            }
        }
    };
    var stream_ctx = StreamCtx{ .streamer = &streamer, .eos_token_ids = gen_config.eos_token_ids };

    // Get BOS token ID from model config (prefer generation_config if set)
    // add_bos_token is loaded by the shared module
    const bos_id: ?u32 = if (gen_config.bos_token_id) |id|
        (if (gen_config.add_bos_token) id else null)
    else if (sess.loaded.config.bos_token_id) |id|
        (if (gen_config.add_bos_token) @intCast(id) else null)
    else
        null;

    // Run generation
    const state = sess.run(prompt, .{
        .max_new_tokens = max_tokens,
        .sampling = sampling,
        .eos_token_ids = gen_config.eos_token_ids,
        .bos_token_id = bos_id,
        .token_callback = if (stream_enabled) StreamCtx.callback else null,
        .callback_data = if (stream_enabled) @ptrCast(&stream_ctx) else null,
    }) catch |err| {
        log.err("Generate failed: {s}", .{@errorName(err)});
        return;
    };

    defer allocator.free(state.final_logits);
    defer sess.tok.allocator.free(state.tokens);

    // Calculate tokens per second for input (prefill) and output (decode)
    const prefill_s = @as(f64, @floatFromInt(state.prefill_ns)) / 1_000_000_000.0;
    const decode_s = @as(f64, @floatFromInt(state.decode_ns)) / 1_000_000_000.0;
    const input_tok_per_sec = if (prefill_s > 0) @as(f64, @floatFromInt(state.prompt_len)) / prefill_s else 0;
    const output_tok_per_sec = if (decode_s > 0 and state.generated_len > 1) @as(f64, @floatFromInt(state.generated_len - 1)) / decode_s else 0;

    if (stream_enabled) {
        // Streaming mode: flush any remaining bytes and add newline
        streamer.flush() catch {};
        try stdout.writeAll("\n");
    } else {
        // Non-streaming mode: decode all tokens and post-process
        var tokens_to_decode: []const u32 = state.tokens;
        if (tokens_to_decode.len > 0 and gen_config_mod.isEosToken(gen_config.eos_token_ids, tokens_to_decode[tokens_to_decode.len - 1])) {
            tokens_to_decode = tokens_to_decode[0 .. tokens_to_decode.len - 1];
        }
        const decoded = try sess.tok.decode(tokens_to_decode);
        defer sess.tok.allocator.free(decoded);

        // Extract clean response (assistant's reply only) unless verbose
        const display_text = if (verbose or no_chat)
            decoded
        else
            extractAssistantResponse(decoded);

        try stdout.writeAll(display_text);
        try stdout.writeAll("\n");
    }

    // Show stats on stderr so they don't mix with the response
    var stats_buf: [256]u8 = undefined;
    const stats = std.fmt.bufPrint(&stats_buf, "\n\x1b[36minput: {d} tok @ {d:.1} t/s | output: {d} tok @ {d:.1} t/s\x1b[0m\n", .{
        state.prompt_len,
        input_tok_per_sec,
        state.generated_len,
        output_tok_per_sec,
    }) catch return;
    const stderr = std.fs.File.stderr();
    stderr.writeAll(stats) catch {};
}

/// Extract the assistant's response from chat-formatted output
/// Handles formats like: <|im_start|>assistant\n<think>...</think>\nResponse<|im_end|>
fn extractAssistantResponse(raw: []const u8) []const u8 {
    // Find the last assistant turn
    const assistant_marker = "<|im_start|>assistant";
    const end_marker = "<|im_end|>";

    // Find the last occurrence of assistant marker
    var last_assistant: ?usize = null;
    var search_pos: usize = 0;
    while (std.mem.indexOfPos(u8, raw, search_pos, assistant_marker)) |pos| {
        last_assistant = pos;
        search_pos = pos + assistant_marker.len;
    }

    if (last_assistant) |start| {
        // Skip past the marker and newline
        var content_start = start + assistant_marker.len;
        if (content_start < raw.len and raw[content_start] == '\n') {
            content_start += 1;
        }

        // Find the end marker
        const content_end = if (std.mem.indexOfPos(u8, raw, content_start, end_marker)) |end|
            end
        else
            raw.len;

        var response = raw[content_start..content_end];

        // Strip <think>...</think> block if present
        if (std.mem.startsWith(u8, response, "<think>")) {
            if (std.mem.indexOf(u8, response, "</think>")) |think_end| {
                var after_think = response[think_end + "</think>".len ..];
                // Skip leading newlines after </think>
                while (after_think.len > 0 and (after_think[0] == '\n' or after_think[0] == '\r')) {
                    after_think = after_think[1..];
                }
                response = after_think;
            }
        }

        // Trim trailing whitespace and replacement characters (U+FFFD = EF BF BD)
        while (response.len > 0) {
            const last = response[response.len - 1];
            if (last == '\n' or last == '\r' or last == ' ') {
                response = response[0 .. response.len - 1];
            } else if (response.len >= 3 and
                response[response.len - 3] == 0xEF and
                response[response.len - 2] == 0xBF and
                response[response.len - 1] == 0xBD)
            {
                // Remove trailing U+FFFD replacement character
                response = response[0 .. response.len - 3];
            } else {
                break;
            }
        }

        return response;
    }

    // No assistant marker found, return as-is
    return raw;
}

fn cmdTokenize(allocator: std.mem.Allocator, args: *std.process.ArgIterator, stdout: std.fs.File) !void {
    // Parse args: tokenize -m <model_path> <text>
    var model_path: ?[]const u8 = null;
    var text_parts: std.ArrayListUnmanaged([]const u8) = .empty;
    defer text_parts.deinit(allocator);

    while (args.next()) |arg| {
        if (std.mem.eql(u8, arg, "-m") or std.mem.eql(u8, arg, "--model")) {
            model_path = args.next();
        } else if (!std.mem.startsWith(u8, arg, "-")) {
            // First positional arg is model path if not set, rest is text
            if (model_path == null) {
                model_path = arg;
            } else {
                try text_parts.append(allocator, arg);
            }
        }
    }

    const path = model_path orelse {
        try stdout.writeAll("Usage: tokamino tokenize <model_path> <text>\n");
        return;
    };

    if (text_parts.items.len == 0) {
        try stdout.writeAll("Usage: tokamino tokenize <model_path> <text>\n");
        return;
    }

    // Join text parts
    const input_text = try std.mem.join(allocator, " ", text_parts.items);
    defer allocator.free(input_text);

    // Load tokenizer
    const tokenizer_api = @import("text/api.zig");
    var tokenizer = tokenizer_api.Tokenizer.init(allocator, path) catch {
        try stdout.writeAll("error: Failed to load tokenizer\n");
        return;
    };
    defer tokenizer.deinit();

    // Encode
    const ids = tokenizer.encode(input_text) catch {
        try stdout.writeAll("error: Failed to encode text\n");
        return;
    };
    defer allocator.free(ids);

    // Output in expected format: "Tokens (N): [id1, id2, ...]"
    var buf: [32768]u8 = undefined;
    var stream = std.io.fixedBufferStream(&buf);
    const writer = stream.writer();

    try writer.print("Tokens ({d}): [", .{ids.len});
    for (ids, 0..) |id, i| {
        if (i > 0) try writer.writeAll(", ");
        try writer.print("{d}", .{id});
    }
    try writer.writeAll("]\n");

    try stdout.writeAll(stream.getWritten());
}

fn cmdConvert(allocator: std.mem.Allocator, args: *std.process.ArgIterator, stdout: std.fs.File) !void {
    const first_arg = args.next() orelse {
        try stdout.writeAll(
            \\Usage: tokamino convert <model_dir> [options]
            \\       tokamino convert --hf <org/model> [options]
            \\
            \\Convert a transformer model to quantized format.
            \\
            \\Arguments:
            \\  <model_dir>       Path to source model directory containing:
            \\                      - config.json
            \\                      - model.safetensors (F32/F16/BF16)
            \\                      - tokenizer.json
            \\                    Supports cache format (models--org--name/snapshots/)
            \\  --hf <org/model>  Download model from HuggingFace Hub (e.g., Qwen/Qwen3-0.6B)
            \\
            \\Options:
            \\  --format FMT      Output format: native (default) or mlx
            \\  --quant TYPE      Quantization type for native: q4_0, q4_k_m, q5_k, q6_k, q8_0
            \\  --bits N          Quantization bits: 4 or 8 (default: 4 for native)
            \\                    For native: 4=Q4_K_M (best quality), 8=Q8_0
            \\                    For MLX: 4=grouped-affine-4bit, 8=grouped-affine-8bit
            \\  --group-size N    Group size for MLX format (default: 64, ignored for native)
            \\  --output DIR      Output directory (default: models)
            \\  -f, --force       Overwrite existing output
            \\
            \\Environment Variables:
            \\  THREADS=N         Number of threads for quantization (default: CPU count)
            \\  HF_TOKEN          HuggingFace API token for private models
            \\
            \\Output formats:
            \\  native - Tokamino native format with K-quants (best quality, default)
            \\  mlx    - MLX-compatible safetensors (for interoperability with MLX)
            \\
            \\Examples:
            \\  tokamino convert --hf Qwen/Qwen3-0.6B                     # Q4_K_M (default)
            \\  tokamino convert --hf Qwen/Qwen3-0.6B --quant q6_k        # Higher quality
            \\  tokamino convert --hf Qwen/Qwen3-0.6B --format mlx --bits 4
            \\  tokamino convert ./models/Qwen--Qwen3-0.6B --output /tmp -f
            \\
        );
        return;
    };

    // Check if using --hf flag for HuggingFace download
    var model_arg: []const u8 = undefined;
    var hf_model_path: ?[]const u8 = null;
    defer if (hf_model_path) |p| allocator.free(p);

    if (std.mem.eql(u8, first_arg, "--hf") or std.mem.eql(u8, first_arg, "-hf")) {
        const hf_model_id = args.next() orelse {
            try stdout.writeAll("Error: --hf requires a model ID (e.g., Qwen/Qwen3-0.6B)\n");
            return;
        };

        // Initialize curl globally
        io.storage.globalInit();
        defer io.storage.globalCleanup();

        const hf_token = std.posix.getenv("HF_TOKEN");
        var progress_state = cli.progress.DownloadProgress.init(stdout);

        try stdout.writeAll("Downloading model from HuggingFace Hub...\n");

        hf_model_path = io.storage.downloadModel(allocator, hf_model_id, .{
            .token = hf_token,
            .progress_callback = cli.progress.DownloadProgress.progressCallback,
            .progress_data = @ptrCast(&progress_state),
            .file_start_callback = cli.progress.DownloadProgress.fileStartCallback,
        }) catch |err| {
            try stdout.writeAll("\n"); // Newline after progress
            var buf: [256]u8 = undefined;
            const msg = std.fmt.bufPrint(&buf, "Failed to download model: {s}\n", .{@errorName(err)}) catch return;
            try stdout.writeAll(msg);
            if (err == error.Unauthorized) {
                try stdout.writeAll("Hint: Set HF_TOKEN environment variable for private models\n");
            } else if (err == error.ModelNotFound) {
                try stdout.writeAll("Hint: Check the model ID (format: org/model, e.g., Qwen/Qwen3-0.6B)\n");
            }
            return;
        };

        // Show "done" for last file
        progress_state.printDone();
        model_arg = hf_model_path.?;
    } else {
        model_arg = first_arg;
    }

    // Parse options
    var bits: ?u8 = null;
    var bits_str: ?[]const u8 = null; // For special values like "4k"
    var quant_str: ?[]const u8 = null; // For --quant option
    var group_size: ?u32 = null;
    var output_dir: []const u8 = "models";
    var force = false;
    var format: []const u8 = "native"; // Default to native format

    while (args.next()) |arg| {
        if (std.mem.eql(u8, arg, "--bits")) {
            if (args.next()) |val| {
                bits_str = val;
                // Parse "4@64" syntax: bits@group_size
                if (std.mem.indexOfScalar(u8, val, '@')) |at_pos| {
                    bits = std.fmt.parseInt(u8, val[0..at_pos], 10) catch null;
                    group_size = std.fmt.parseInt(u32, val[at_pos + 1 ..], 10) catch null;
                } else {
                    bits = std.fmt.parseInt(u8, val, 10) catch null;
                }
            }
        } else if (std.mem.eql(u8, arg, "--quant")) {
            if (args.next()) |val| {
                quant_str = val;
            }
        } else if (std.mem.eql(u8, arg, "--group-size")) {
            if (args.next()) |val| {
                group_size = std.fmt.parseInt(u32, val, 10) catch null;
            }
        } else if (std.mem.eql(u8, arg, "--output")) {
            if (args.next()) |val| {
                output_dir = val;
            }
        } else if (std.mem.eql(u8, arg, "--format")) {
            if (args.next()) |val| {
                format = val;
            }
        } else if (std.mem.eql(u8, arg, "-f") or std.mem.eql(u8, arg, "--force")) {
            force = true;
        }
    }

    var buf: [512]u8 = undefined;

    // Dispatch based on format
    if (std.mem.eql(u8, format, "native")) {
        // Native format with K-quants
        const native_quant: convert.native.NativeQuantType = if (quant_str) |qs|
            convert.native.NativeQuantType.fromString(qs) orelse {
                try stdout.writeAll("Error: Invalid quant type. Valid options: q4_0, q4_k_m, q5_k, q6_k, q8_0\n");
                return;
            }
        else if (bits) |b| switch (b) {
            4 => .q4_k_m,
            8 => .q8_0,
            16 => .f16,
            else => {
                try stdout.writeAll("Error: Native format only supports bits=4, 8, or 16\n");
                return;
            },
        } else .q4_k_m; // Default to Q4_K_M

        try stdout.writeAll("Converting model to native format...\n");
        var info_offset: usize = 0;
        info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Source: {s}\n", .{model_arg}) catch return).len;
        info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Format: Native {s}\n", .{native_quant.toString()}) catch return).len;
        info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Output dir: {s}\n", .{output_dir}) catch return).len;
        try stdout.writeAll(buf[0..info_offset]);

        const output_path = convert.native.convertToNative(allocator, model_arg, .{
            .quant = native_quant,
            .output_dir = output_dir,
            .force = force,
        }) catch |err| {
            log.err("Native conversion failed: {s}", .{@errorName(err)});
            if (err == error.OutputExists) {
                try stdout.writeAll("Error: Output directory already exists. Use -f to overwrite.\n");
            } else if (err == error.AlreadyQuantized) {
                try stdout.writeAll("Error: Model is already quantized. Re-quantizing is not supported.\n");
                try stdout.writeAll("       Please use an unquantized (F32/F16/BF16) source model.\n");
            }
            return;
        };
        defer allocator.free(output_path);

        const done_msg = std.fmt.bufPrint(&buf, "\nDone! Model saved to:\n  {s}\n", .{output_path}) catch return;
        try stdout.writeAll(done_msg);
    } else {
        // Default: MLX format
        const effective_bits = bits orelse 16; // Default to 16-bit (no quantization)
        try stdout.writeAll("Converting model to MLX...\n");
        var info_offset: usize = 0;
        info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Source: {s}\n", .{model_arg}) catch return).len;
        if (effective_bits == 16) {
            info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Format: MLX (original precision)\n", .{}) catch return).len;
        } else {
            info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Format: MLX {d}-bit\n", .{effective_bits}) catch return).len;
            info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Group size: {d}\n", .{group_size orelse 64}) catch return).len;
        }
        info_offset += (std.fmt.bufPrint(buf[info_offset..], "  Output dir: {s}\n", .{output_dir}) catch return).len;
        try stdout.writeAll(buf[0..info_offset]);

        // Build quant config - null means no quantization (preserve original)
        const quant_config: ?convert.grouped_affine.QuantConfig = if (effective_bits == 16)
            null
        else
            .{ .bits = effective_bits, .group_size = group_size orelse 64 };

        const output_path = convert.grouped_affine.convertToGroupedAffine(allocator, model_arg, .{
            .quant = quant_config,
            .output_dir = output_dir,
            .force = force,
        }) catch |err| {
            log.err("Conversion failed: {s}", .{@errorName(err)});
            if (err == error.OutputExists) {
                try stdout.writeAll("Error: Output directory already exists. Use -f to overwrite.\n");
            } else if (err == error.MissingQuantConfig) {
                try stdout.writeAll("Error: Model config missing quantization settings. Specify --bits and --group-size.\n");
            } else if (err == error.AlreadyQuantized) {
                try stdout.writeAll("Error: Model is already quantized. Re-quantizing is not supported.\n");
                try stdout.writeAll("       Please use an unquantized (F32/F16/BF16) source model.\n");
            } else if (err == error.UnsupportedBits) {
                try stdout.writeAll("Error: Only 4-bit, 8-bit, and 16-bit (no quant) are supported.\n");
            }
            return;
        };
        defer allocator.free(output_path);

        const done_msg = std.fmt.bufPrint(&buf, "\nDone! Model saved to:\n  {s}\n", .{output_path}) catch return;
        try stdout.writeAll(done_msg);
    }
}

// =============================================================================
// Tests
// =============================================================================

test "module imports" {
    // Verify all modules can be imported
    _ = core.tensor;
    _ = core.parallel;
    _ = core.ops.math;
    _ = text.api;
    _ = text.chat_template;
    _ = nn.model;
    _ = io.internal.config;
    _ = session;
}

test {
    std.testing.refAllDecls(@This());
}
