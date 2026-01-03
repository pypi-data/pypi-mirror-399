//! MLX model path utilities and config generation
//!
//! MLX (Apple's ML framework) uses a specific directory structure and config format
//! that differs from standard transformer configs.

const std = @import("std");
const tensor = @import("../../tensor.zig");
const io = @import("../root.zig");

const ModelConfig = tensor.ModelConfig;

/// MLX-specific configuration that differs from standard transformer format
pub const MLXConfig = struct {
    // Standard fields
    vocab_size: i32,
    hidden_size: i32,
    num_hidden_layers: i32,
    num_attention_heads: i32,
    num_key_value_heads: i32,
    intermediate_size: i32,
    max_position_embeddings: i32,
    head_dim: i32,
    rms_norm_eps: f32,
    rope_theta: f32,

    // MLX-specific quantization config
    quantization: ?QuantizationConfig = null,

    // Gemma3/model-specific fields
    model_type: ?[]const u8 = null,
    hidden_activation: ?[]const u8 = null, // "gelu_pytorch_tanh" for Gemma3
    query_pre_attn_scalar: ?i32 = null, // Gemma3: head_dim
    sliding_window: ?i32 = null,
    sliding_window_pattern: ?i32 = null,

    pub const QuantizationConfig = struct {
        group_size: i32 = 64,
        bits: i32 = 4,
    };

    /// Create MLX config from a standard ModelConfig
    pub fn fromModelConfig(cfg: ModelConfig, quant: ?QuantizationConfig) MLXConfig {
        return .{
            .vocab_size = cfg.vocab_size,
            .hidden_size = cfg.d_model,
            .num_hidden_layers = cfg.n_layers,
            .num_attention_heads = cfg.n_heads,
            .num_key_value_heads = cfg.n_kv_groups,
            .intermediate_size = cfg.d_ff,
            .max_position_embeddings = cfg.max_seq_len,
            .head_dim = cfg.head_dim,
            .rms_norm_eps = cfg.norm_eps,
            .rope_theta = cfg.rope_theta,
            .quantization = quant,
            // Gemma3-specific
            .hidden_activation = if (cfg.use_gelu) "gelu_pytorch_tanh" else null,
            .query_pre_attn_scalar = if (cfg.query_pre_attn_scalar > 0) @intFromFloat(cfg.query_pre_attn_scalar) else null,
            .sliding_window = if (cfg.sliding_window > 0) cfg.sliding_window else null,
            .sliding_window_pattern = if (cfg.sliding_window_pattern > 0) cfg.sliding_window_pattern else null,
            .model_type = io.getMLXModelType(cfg.model_arch),
        };
    }

    /// Write MLX config to a JSON file using std.json serialization
    pub fn writeToFile(self: *const MLXConfig, allocator: std.mem.Allocator, path: []const u8) !void {
        const json = try std.json.Stringify.valueAlloc(allocator, self, .{ .whitespace = .indent_2 });
        defer allocator.free(json);

        var file = try std.fs.cwd().createFile(path, .{});
        defer file.close();
        try file.writeAll(json);
    }

    /// Custom JSON serialization to omit null optional fields
    pub fn jsonStringify(self: *const MLXConfig, jws: anytype) !void {
        try jws.beginObject();

        // Required fields
        try jws.objectField("vocab_size");
        try jws.write(self.vocab_size);
        try jws.objectField("hidden_size");
        try jws.write(self.hidden_size);
        try jws.objectField("num_hidden_layers");
        try jws.write(self.num_hidden_layers);
        try jws.objectField("num_attention_heads");
        try jws.write(self.num_attention_heads);
        try jws.objectField("num_key_value_heads");
        try jws.write(self.num_key_value_heads);
        try jws.objectField("intermediate_size");
        try jws.write(self.intermediate_size);
        try jws.objectField("max_position_embeddings");
        try jws.write(self.max_position_embeddings);
        try jws.objectField("head_dim");
        try jws.write(self.head_dim);
        try jws.objectField("rms_norm_eps");
        try jws.write(self.rms_norm_eps);
        try jws.objectField("rope_theta");
        try jws.write(self.rope_theta);

        // Optional fields (only emit if non-null)
        if (self.model_type) |mt| {
            try jws.objectField("model_type");
            try jws.write(mt);
        }
        if (self.hidden_activation) |ha| {
            try jws.objectField("hidden_activation");
            try jws.write(ha);
        }
        if (self.query_pre_attn_scalar) |qpas| {
            try jws.objectField("query_pre_attn_scalar");
            try jws.write(qpas);
        }
        if (self.sliding_window) |sw| {
            try jws.objectField("sliding_window");
            try jws.write(sw);
        }
        if (self.sliding_window_pattern) |swp| {
            try jws.objectField("sliding_window_pattern");
            try jws.write(swp);
        }
        if (self.quantization) |q| {
            try jws.objectField("quantization");
            try jws.write(q);
        }

        try jws.endObject();
    }
};

/// Generate output directory name for MLX model
/// Input: "models--Qwen--Qwen3-0.6B" or "/path/to/models--Qwen--Qwen3-0.6B"
///        or HF cache path like "~/.cache/.../models--Qwen--Qwen3-0.6B/snapshots/abc123"
/// Output: "models--aprxi--Qwen--Qwen3-0.6B-MLX-4bit" (quantized)
///         "models--aprxi--Qwen--Qwen3-0.6B-MLX" (16-bit, no quantization)
pub fn generateOutputName(allocator: std.mem.Allocator, input_path: []const u8, bits: u8, output_dir: []const u8) ![]const u8 {
    // Find the "models--org--name" component in the path
    // It could be the basename or a parent directory (for HF cache paths)
    var model_name: ?[]const u8 = null;

    // Walk up the path looking for a "models--" component
    var current_path = input_path;
    while (current_path.len > 0) {
        const basename = std.fs.path.basename(current_path);
        if (std.mem.startsWith(u8, basename, "models--")) {
            model_name = basename;
            break;
        }
        const parent = std.fs.path.dirname(current_path);
        if (parent == null or std.mem.eql(u8, parent.?, current_path)) break;
        current_path = parent.?;
    }

    // If no "models--" found, use the original basename
    const name_to_use = model_name orelse std.fs.path.basename(input_path);

    // Remove "models--" prefix if present
    var clean_name = name_to_use;
    if (std.mem.startsWith(u8, name_to_use, "models--")) {
        clean_name = name_to_use["models--".len..];
    }

    // Construct final folder name (keep "--" separators for HF compatibility)
    var result = std.ArrayListUnmanaged(u8){};
    errdefer result.deinit(allocator);

    if (bits == 16) {
        // No quantization - just "-MLX" suffix
        try result.writer(allocator).print("{s}/models--aprxi--{s}-MLX", .{
            output_dir,
            clean_name,
        });
    } else {
        // Quantized - include bit depth
        try result.writer(allocator).print("{s}/models--aprxi--{s}-MLX-{d}bit", .{
            output_dir,
            clean_name,
            bits,
        });
    }

    return try result.toOwnedSlice(allocator);
}

/// MLX model directory structure
pub const MLXModelDir = struct {
    allocator: std.mem.Allocator,
    path: []const u8,

    pub fn init(allocator: std.mem.Allocator, path: []const u8) !MLXModelDir {
        // Create directory if it doesn't exist
        std.fs.cwd().makePath(path) catch |err| switch (err) {
            error.PathAlreadyExists => {},
            else => return err,
        };

        return .{
            .allocator = allocator,
            .path = try allocator.dupe(u8, path),
        };
    }

    pub fn deinit(self: *MLXModelDir) void {
        self.allocator.free(self.path);
        self.* = undefined;
    }

    /// Get path for config.json
    pub fn configPath(self: *const MLXModelDir) ![]const u8 {
        return try std.fs.path.join(self.allocator, &.{ self.path, "config.json" });
    }

    /// Get path for model.safetensors
    pub fn weightsPath(self: *const MLXModelDir) ![]const u8 {
        return try std.fs.path.join(self.allocator, &.{ self.path, "model.safetensors" });
    }

    /// Get path for tokenizer.json
    pub fn tokenizerPath(self: *const MLXModelDir) ![]const u8 {
        return try std.fs.path.join(self.allocator, &.{ self.path, "tokenizer.json" });
    }

    /// Copy tokenizer and config files from source directory
    pub fn copyTokenizerFiles(self: *const MLXModelDir, source_dir: []const u8) !void {
        const files_to_copy = [_][]const u8{
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "generation_config.json",
            "merges.txt",
            "vocab.json",
        };

        for (files_to_copy) |filename| {
            const src_path = try std.fs.path.join(self.allocator, &.{ source_dir, filename });
            defer self.allocator.free(src_path);

            const dst_path = try std.fs.path.join(self.allocator, &.{ self.path, filename });
            defer self.allocator.free(dst_path);

            std.fs.cwd().copyFile(src_path, std.fs.cwd(), dst_path, .{}) catch |err| switch (err) {
                error.FileNotFound => continue, // Optional files
                else => return err,
            };
        }
    }
};

test "generateOutputName" {
    const allocator = std.testing.allocator;

    // Direct path - 4-bit quantization
    {
        const result = try generateOutputName(allocator, "models--Qwen--Qwen3-0.6B", 4, "models");
        defer allocator.free(result);
        try std.testing.expectEqualStrings("models/models--aprxi--Qwen--Qwen3-0.6B-MLX-4bit", result);
    }

    // HF cache path with snapshots - 4-bit
    {
        const result = try generateOutputName(allocator, "/home/user/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/abc123def", 4, "models");
        defer allocator.free(result);
        try std.testing.expectEqualStrings("models/models--aprxi--Qwen--Qwen3-0.6B-MLX-4bit", result);
    }

    // 16-bit (no quantization)
    {
        const result = try generateOutputName(allocator, "models--Qwen--Qwen3-0.6B", 16, "models");
        defer allocator.free(result);
        try std.testing.expectEqualStrings("models/models--aprxi--Qwen--Qwen3-0.6B-MLX", result);
    }
}

test "MLXConfig from ModelConfig" {
    const cfg = ModelConfig{
        .vocab_size = 151936,
        .d_model = 1024,
        .n_layers = 28,
        .n_heads = 16,
        .n_kv_groups = 8,
        .d_ff = 3072,
        .max_seq_len = 32768,
        .head_dim = 128,
        .rope_theta = 1000000.0,
        .norm_eps = 1e-6,
        .gaffine_group_size = 64,
    };

    const mlx_cfg = MLXConfig.fromModelConfig(cfg, .{ .group_size = 64, .bits = 4 });

    try std.testing.expectEqual(@as(i32, 151936), mlx_cfg.vocab_size);
    try std.testing.expectEqual(@as(i32, 1024), mlx_cfg.hidden_size);
    try std.testing.expectEqual(@as(i32, 64), mlx_cfg.quantization.?.group_size);
}
