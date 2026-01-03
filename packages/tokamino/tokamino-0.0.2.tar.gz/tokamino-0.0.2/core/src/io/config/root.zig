const std = @import("std");
const tensor = @import("../../tensor.zig");
const graph = @import("../../graph/root.zig");

const ModelConfig = tensor.ModelConfig;

// =============================================================================
// Rope Scaling Parsing (shared helper for config.zig and gemma.zig)
// =============================================================================

/// Parse rope_scaling from a JSON object.
/// Used by both main config parsing and Gemma3 inference fallback.
pub fn parseRopeScalingFromObject(obj: std.json.ObjectMap) tensor.RopeScaling {
    var rope_type_val: @TypeOf((tensor.RopeScaling{}).rope_type) = .none;
    if (obj.get("rope_type")) |rtv| {
        if (rtv == .string) {
            if (std.mem.eql(u8, rtv.string, "llama3")) rope_type_val = .llama3;
            if (std.mem.eql(u8, rtv.string, "linear")) rope_type_val = .linear;
            if (std.mem.eql(u8, rtv.string, "yarn")) rope_type_val = .yarn;
        }
    }

    return .{
        .rope_type = rope_type_val,
        .factor = getFloatField(obj, "factor") orelse 1.0,
        .low_freq_factor = getFloatField(obj, "low_freq_factor") orelse
            getFloatField(obj, "beta_slow") orelse 1.0,
        .high_freq_factor = getFloatField(obj, "high_freq_factor") orelse
            getFloatField(obj, "beta_fast") orelse 4.0,
        .original_max_position_embeddings = if (obj.get("original_max_position_embeddings")) |v|
            (if (v == .integer) @as(i32, @intCast(v.integer)) else 8192)
        else
            8192,
    };
}

/// Helper to extract a float from a JSON value (handles both float and integer).
fn getFloatField(obj: std.json.ObjectMap, key: []const u8) ?f32 {
    const v = obj.get(key) orelse return null;
    return switch (v) {
        .float => @floatCast(v.float),
        .integer => @floatFromInt(v.integer),
        else => null,
    };
}

// =============================================================================
// Architecture Detection (centralized here for consistency)
// =============================================================================

/// Detect model architecture from model_type string in config.json.
/// This is the authoritative mapping used by all loaders.
pub fn detectFromModelType(model_type: []const u8) tensor.ModelArch {
    if (std.mem.eql(u8, model_type, "llama")) return .llama;
    if (std.mem.eql(u8, model_type, "mistral")) return .llama; // Mistral uses llama architecture
    if (std.mem.eql(u8, model_type, "qwen2") or std.mem.eql(u8, model_type, "qwen2_5")) return .qwen2;
    if (std.mem.eql(u8, model_type, "qwen3")) return .qwen3;
    if (std.mem.eql(u8, model_type, "gemma")) return .gemma;
    if (std.mem.eql(u8, model_type, "gemma2")) return .gemma2;
    if (std.mem.eql(u8, model_type, "gemma3") or std.mem.eql(u8, model_type, "gemma3_text")) return .gemma3;
    if (std.mem.eql(u8, model_type, "phi") or std.mem.eql(u8, model_type, "phi3") or std.mem.eql(u8, model_type, "phi4")) return .phi;
    if (std.mem.eql(u8, model_type, "granite")) return .granite;
    if (std.mem.eql(u8, model_type, "gpt_oss")) return .gpt_oss;
    return .llama;
}

/// Get the MLX model_type string for a given architecture.
pub fn getMLXModelType(arch: tensor.ModelArch) []const u8 {
    return switch (arch) {
        .llama => "llama",
        .qwen2 => "qwen2",
        .qwen3 => "qwen3",
        .gemma => "gemma",
        .gemma2 => "gemma2",
        .gemma3 => "gemma3",
        .phi => "phi",
        .granite => "granite",
        .gpt_oss => "gpt_oss",
        .custom => "llama",
    };
}

/// Quantization config - supports both MLX and MXFP4 formats
const QuantConfig = struct {
    group_size: ?i64 = null,
    bits: ?i64 = null,
    quant_method: ?[]const u8 = null, // "mxfp4", etc.
    mode: ?[]const u8 = null, // Alternative to quant_method used by some models
};

/// JSON config struct with all possible field name variants.
/// Different model formats use different names for the same fields.
const JsonConfig = struct {
    // Architecture identification
    model_type: ?[]const u8 = null,
    architectures: ?[]const []const u8 = null,

    vocab_size: ?i64 = null,
    // Model dimension
    d_model: ?i64 = null,
    hidden_size: ?i64 = null,
    // Layers
    n_layers: ?i64 = null,
    num_layers: ?i64 = null,
    num_hidden_layers: ?i64 = null,
    // Attention heads
    n_heads: ?i64 = null,
    num_heads: ?i64 = null,
    num_attention_heads: ?i64 = null,
    // KV heads
    n_kv_groups: ?i64 = null,
    num_key_value_heads: ?i64 = null,
    // FFN dimension
    d_ff: ?i64 = null,
    intermediate_size: ?i64 = null,
    // Max sequence length
    max_seq_len: ?i64 = null,
    context_length: ?i64 = null,
    max_position_embeddings: ?i64 = null,
    // Head dimension
    head_dim: ?i64 = null,
    // RoPE
    rope_base: ?f64 = null,
    rope_theta: ?f64 = null,
    // RoPE scaling (Llama3-style / YaRN-style)
    rope_scaling: ?struct {
        rope_type: ?[]const u8 = null,
        factor: ?f64 = null,
        low_freq_factor: ?f64 = null,
        high_freq_factor: ?f64 = null,
        // YaRN naming (maps to low/high frequency factors)
        beta_slow: ?f64 = null,
        beta_fast: ?f64 = null,
        truncate: ?bool = null,
        original_max_position_embeddings: ?i64 = null,
    } = null,
    // RoPE parameters (Mistral3/YARN-style)
    rope_parameters: ?struct {
        rope_theta: ?f64 = null,
        rope_type: ?[]const u8 = null,
        factor: ?f64 = null,
        original_max_position_embeddings: ?i64 = null,
    } = null,
    // Norm epsilon
    norm_eps: ?f64 = null,
    rms_norm_eps: ?f64 = null,
    // Quantization
    quantization: ?struct { group_size: ?i64 = null, bits: ?i64 = null, mode: ?[]const u8 = null } = null,
    quantization_config: ?QuantConfig = null,
    // Tied embeddings (lm_head shares weights with embed_tokens)
    tie_word_embeddings: ?bool = null,
    // MoE (Mixture of Experts) config
    num_local_experts: ?i64 = null,
    num_experts_per_tok: ?i64 = null,
    experts_per_token: ?i64 = null, // Alias used by some models
    // Attention bias
    attention_bias: ?bool = null,
    // Gemma3-specific fields
    hidden_activation: ?[]const u8 = null, // "silu" or "gelu_pytorch_tanh"
    query_pre_attn_scalar: ?f64 = null, // Attention scale factor (Gemma3: 256)
    use_qk_norm: ?bool = null, // Whether to use Q/K norms (Gemma3: true)
    sliding_window: ?i64 = null, // Sliding window size (Gemma3: 512)
    sliding_window_pattern: ?i64 = null, // Every Nth layer is global (Gemma3: 6)
    rope_local_base_freq: ?f64 = null, // Local RoPE theta for sliding layers
    // Special tokens
    bos_token_id: ?i64 = null, // Beginning of sequence token
    // Granite-specific fields (scaling multipliers)
    embedding_multiplier: ?f64 = null, // Scales embedding output
    attention_multiplier: ?f64 = null, // Custom attention scale (replaces 1/sqrt(head_dim))
    residual_multiplier: ?f64 = null, // Scales residual connections
    logits_scaling: ?f64 = null, // Scales output logits
    // Phi-specific fields
    partial_rotary_factor: ?f64 = null, // Fraction of head_dim to apply RoPE (Phi: 0.75)

    /// Get first non-null integer from a list of field names
    fn int(self: @This(), comptime fields: anytype) ?i32 {
        inline for (fields) |f| if (@field(self, f)) |v| return @intCast(v);
        return null;
    }

    /// Get first non-null float from a list of field names
    fn float(self: @This(), comptime fields: anytype) ?f32 {
        inline for (fields) |f| if (@field(self, f)) |v| return @floatCast(v);
        return null;
    }

    /// Get integer field with default
    fn intOr(self: @This(), comptime field: []const u8, default: i32) i32 {
        return if (@field(self, field)) |v| @intCast(v) else default;
    }

    /// Get float field with default
    fn floatOr(self: @This(), comptime field: []const u8, default: f32) f32 {
        return if (@field(self, field)) |v| @floatCast(v) else default;
    }

    /// Get grouped-affine group size from quantization config, defaulting to 64
    fn gaffineGroupSize(self: @This()) i32 {
        if (self.quantization) |q| return @intCast(q.group_size orelse 64);
        if (self.quantization_config) |q| return @intCast(q.group_size orelse 64);
        return 64;
    }

    /// Get grouped-affine quantization bits from quantization config, defaulting to 4
    fn gaffineBits(self: @This()) i32 {
        if (self.quantization) |q| return @intCast(q.bits orelse 4);
        if (self.quantization_config) |q| return @intCast(q.bits orelse 4);
        return 4;
    }
};

/// Result of checking model architecture support
pub const ArchitectureCheck = struct {
    supported: bool,
    model_type_buf: [64]u8 = undefined,
    model_type_len: usize = 0,
    architecture_buf: [64]u8 = undefined,
    architecture_len: usize = 0,

    pub fn getModelType(self: *const @This()) ?[]const u8 {
        if (self.model_type_len == 0) return null;
        return self.model_type_buf[0..self.model_type_len];
    }

    pub fn getArchitecture(self: *const @This()) ?[]const u8 {
        if (self.architecture_len == 0) return null;
        return self.architecture_buf[0..self.architecture_len];
    }
};

/// Check if a model's architecture is supported without fully loading.
/// Checks against the runtime registry (populated from _graphs/*.json).
pub fn checkArchitecture(allocator: std.mem.Allocator, path: []const u8) !ArchitectureCheck {
    var result = ArchitectureCheck{ .supported = false };

    const data = std.fs.cwd().readFileAlloc(allocator, path, 256 * 1024) catch {
        // Can't read config - assume supported (might be legacy format)
        result.supported = true;
        return result;
    };
    defer allocator.free(data);

    const parsed = std.json.parseFromSlice(JsonConfig, allocator, data, .{
        .ignore_unknown_fields = true,
        .allocate = .alloc_always,
    }) catch {
        // Can't parse - assume supported
        result.supported = true;
        return result;
    };
    defer parsed.deinit();

    const j = parsed.value;

    // Copy model_type if present
    if (j.model_type) |mt| {
        const len = @min(mt.len, result.model_type_buf.len);
        @memcpy(result.model_type_buf[0..len], mt[0..len]);
        result.model_type_len = len;
    }

    // Copy architecture name if present
    if (j.architectures) |archs| {
        if (archs.len > 0) {
            const arch = archs[0];
            const len = @min(arch.len, result.architecture_buf.len);
            @memcpy(result.architecture_buf[0..len], arch[0..len]);
            result.architecture_len = len;
        }
    }

    // Check model_type against the runtime registry
    // The registry is populated from bindings/python/tokamino/_graphs/*.json
    if (j.model_type) |mt| {
        if (graph.detectFromModelType(mt) != null) {
            result.supported = true;
            return result;
        }
        // model_type found but not in registry
        result.supported = false;
        return result;
    }

    // No model_type found - assume supported (legacy models)
    result.supported = true;
    return result;
}

pub fn loadConfig(allocator: std.mem.Allocator, path: []const u8) !ModelConfig {
    const data = try std.fs.cwd().readFileAlloc(allocator, path, 256 * 1024);
    defer allocator.free(data);

    // Parse once as generic JSON value, then extract what we need
    const raw_parsed = std.json.parseFromSlice(std.json.Value, allocator, data, .{}) catch return error.InvalidJson;
    defer raw_parsed.deinit();

    // Determine which value to parse as JsonConfig:
    // - If multimodal model with text_config, use that subobject
    // - Otherwise use the root object
    const config_value: std.json.Value = if (raw_parsed.value == .object) blk: {
        if (raw_parsed.value.object.get("text_config")) |text_config| {
            break :blk text_config;
        }
        break :blk raw_parsed.value;
    } else raw_parsed.value;

    // Parse the selected value into JsonConfig (no re-parsing of the file)
    const parsed = std.json.parseFromValue(JsonConfig, allocator, config_value, .{
        .ignore_unknown_fields = true,
    }) catch return error.InvalidJson;
    defer parsed.deinit();
    const j = parsed.value;

    const vocab_size = j.int(.{"vocab_size"}) orelse return error.MissingField;
    const d_model = j.int(.{ "d_model", "hidden_size" }) orelse return error.MissingField;
    const n_layers = j.int(.{ "n_layers", "num_layers", "num_hidden_layers" }) orelse return error.MissingField;
    const n_heads = j.int(.{ "n_heads", "num_heads", "num_attention_heads" }) orelse return error.MissingField;
    const d_ff = j.int(.{ "d_ff", "intermediate_size" }) orelse return error.MissingField;
    const max_seq_len = j.int(.{ "max_seq_len", "context_length", "max_position_embeddings" }) orelse return error.MissingField;

    if (vocab_size <= 0 or d_model <= 0 or n_layers <= 0 or n_heads <= 0 or d_ff <= 0 or max_seq_len <= 0) {
        return error.InvalidValue;
    }

    // Determine quantization method
    const quant_method: tensor.QuantMethod = blk: {
        // Check quantization_config first (both quant_method and mode fields)
        if (j.quantization_config) |qc| {
            if (qc.quant_method) |method| {
                if (std.mem.eql(u8, method, "mxfp4")) break :blk .mxfp4;
                if (std.mem.eql(u8, method, "tokamino")) break :blk .native;
            }
            if (qc.mode) |mode| {
                if (std.mem.eql(u8, mode, "mxfp4")) break :blk .mxfp4;
            }
        }
        // Check quantization.mode field (used by some models like gpt-oss)
        if (j.quantization) |q| {
            if (q.mode) |mode| {
                if (std.mem.eql(u8, mode, "mxfp4")) break :blk .mxfp4;
            }
        }
        // Check if grouped-affine quantization (has group_size or bits)
        if (j.quantization != null or (j.quantization_config != null and
            (j.quantization_config.?.group_size != null or j.quantization_config.?.bits != null)))
        {
            break :blk .gaffine;
        }
        break :blk .none;
    };

    // Parse rope_scaling if present.
    // Note: some models (e.g. GPT-OSS) use `rope_type="yarn"` with `beta_fast/beta_slow`.
    const rope_scaling: tensor.RopeScaling = if (j.rope_scaling) |rs| blk: {
        // Determine rope_type enum value
        var rope_type_val: @TypeOf((tensor.RopeScaling{}).rope_type) = .none;
        if (rs.rope_type) |rt| {
            if (std.mem.eql(u8, rt, "llama3")) rope_type_val = .llama3;
            if (std.mem.eql(u8, rt, "linear")) rope_type_val = .linear;
            // YaRN is its own scaling scheme; CPU currently treats it as "no scaling" to match Metal path.
            if (std.mem.eql(u8, rt, "yarn")) rope_type_val = .yarn;
        }
        const beta_slow = if (rs.beta_slow) |f| @as(f32, @floatCast(f)) else 1.0;
        const beta_fast = if (rs.beta_fast) |f| @as(f32, @floatCast(f)) else 4.0;
        break :blk .{
            .rope_type = rope_type_val,
            .factor = if (rs.factor) |f| @floatCast(f) else 1.0,
            .low_freq_factor = if (rs.low_freq_factor) |f| @floatCast(f) else beta_slow,
            .high_freq_factor = if (rs.high_freq_factor) |f| @floatCast(f) else beta_fast,
            .original_max_position_embeddings = if (rs.original_max_position_embeddings) |v| @intCast(v) else 8192,
        };
    } else .{};

    // Detect GELU activation from hidden_activation field
    const use_gelu = if (j.hidden_activation) |act|
        std.mem.eql(u8, act, "gelu_pytorch_tanh") or std.mem.eql(u8, act, "gelu")
    else
        false;

    // Detect model architecture from model_type field using centralized mapping
    const model_arch: tensor.ModelArch = if (j.model_type) |mt|
        detectFromModelType(mt)
    else
        .llama;

    // Calculate rope_dim from head_dim and partial_rotary_factor
    // For most models, rope_dim == head_dim. For Phi, it's head_dim * 0.75
    const head_dim = j.int(.{"head_dim"}) orelse @divTrunc(d_model, n_heads);
    const rope_dim: i32 = if (j.partial_rotary_factor) |prf|
        @intFromFloat(@as(f32, @floatFromInt(head_dim)) * @as(f32, @floatCast(prf)))
    else
        0; // 0 means use head_dim

    return .{
        .vocab_size = vocab_size,
        .d_model = d_model,
        .n_layers = n_layers,
        .n_heads = n_heads,
        .n_kv_groups = j.int(.{ "n_kv_groups", "num_key_value_heads" }) orelse n_heads,
        .d_ff = d_ff,
        .max_seq_len = max_seq_len,
        .head_dim = head_dim,
        .rope_dim = rope_dim,
        .rope_theta = j.float(.{ "rope_base", "rope_theta" }) orelse
            (if (j.rope_parameters) |rp| if (rp.rope_theta) |t| @as(f32, @floatCast(t)) else null else null) orelse 10000.0,
        .norm_eps = j.float(.{ "norm_eps", "rms_norm_eps" }) orelse 1e-5,
        .gaffine_group_size = j.gaffineGroupSize(),
        .gaffine_bits = j.gaffineBits(),
        .tie_word_embeddings = j.tie_word_embeddings orelse true, // Default true for most models
        .num_experts = j.int(.{"num_local_experts"}) orelse 0,
        .experts_per_token = j.int(.{ "num_experts_per_tok", "experts_per_token" }) orelse 0,
        .attention_bias = j.attention_bias orelse false,
        .quant_method = quant_method,
        .rope_scaling = rope_scaling,
        // Model arch detected from model_type field above; dispatcher may override for weights-based detection.
        .model_arch = model_arch,
        .use_gelu = use_gelu,
        .use_qk_norm = j.use_qk_norm orelse false,
        .query_pre_attn_scalar = j.floatOr("query_pre_attn_scalar", 0),
        .rope_local_theta = j.floatOr("rope_local_base_freq", 0),
        .sliding_window = j.intOr("sliding_window", 0),
        .sliding_window_pattern = j.intOr("sliding_window_pattern", 0),
        // Granite-specific config
        .embedding_multiplier = j.floatOr("embedding_multiplier", 1.0),
        .attention_multiplier = j.floatOr("attention_multiplier", 0),
        .residual_multiplier = j.floatOr("residual_multiplier", 1.0),
        .logits_scaling = j.floatOr("logits_scaling", 1.0),
        .bos_token_id = if (j.bos_token_id) |id| @intCast(id) else null,
    };
}
