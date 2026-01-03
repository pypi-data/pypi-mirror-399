const std = @import("std");
const tensor = @import("../../tensor.zig");
const io = @import("../internal.zig");
const cfg = @import("root.zig");
const st_loader = io.safetensors.root;
const hf_layout = io.safetensors.layouts.hf;
const st_names = io.safetensors.names;

const ModelConfig = tensor.ModelConfig;

/// Multimodal Gemma3 conditional-generation configs often omit required top-level LM fields and
/// instead provide a nested `text_config` plus the full LM shapes in the safetensors weights.
/// Infer the missing values from a combination of the (partial) config JSON and weight shapes.
///
/// Returns `error.MissingField` when the file is not Gemma3 conditional-generation or cannot infer.
pub fn inferConfigFromWeights(
    allocator: std.mem.Allocator,
    config_path: []const u8,
    st: *st_loader.UnifiedSafeTensors,
) !ModelConfig {
    const data = std.fs.cwd().readFileAlloc(allocator, config_path, 256 * 1024) catch return error.InvalidJson;
    defer allocator.free(data);

    const parsed = std.json.parseFromSlice(std.json.Value, allocator, data, .{}) catch return error.InvalidJson;
    defer parsed.deinit();

    if (parsed.value != .object) return error.MissingField;
    const obj = parsed.value.object;

    const model_type = if (obj.get("model_type")) |v| switch (v) {
        .string => |s| s,
        else => null,
    } else null;

    const arch0 = if (obj.get("architectures")) |v| switch (v) {
        .array => |arr| if (arr.items.len > 0 and arr.items[0] == .string) arr.items[0].string else null,
        .string => |s| s,
        else => null,
    } else null;

    const is_gemma3_conditional = (model_type != null and std.mem.eql(u8, model_type.?, "gemma3")) and
        (arch0 != null and std.mem.eql(u8, arch0.?, "Gemma3ForConditionalGeneration"));
    if (!is_gemma3_conditional) return error.MissingField;

    // Pull a few hints from text_config when available.
    var n_layers: i32 = 0;
    var d_ff: i32 = 0;
    var sliding_window: i32 = 0;
    var sliding_window_pattern: i32 = 0;
    var rope_local_theta: f32 = 0;
    var query_pre_attn_scalar: f32 = 256;
    var rope_scaling: tensor.RopeScaling = .{};
    if (obj.get("text_config")) |tc_val| {
        if (tc_val == .object) {
            const tc = tc_val.object;
            if (tc.get("num_hidden_layers")) |v| {
                if (v == .integer) n_layers = @intCast(v.integer);
            }
            if (tc.get("intermediate_size")) |v| {
                if (v == .integer) d_ff = @intCast(v.integer);
            }
            if (tc.get("sliding_window")) |v| {
                if (v == .integer) sliding_window = @intCast(v.integer);
            }
            if (tc.get("sliding_window_pattern")) |v| {
                if (v == .integer) sliding_window_pattern = @intCast(v.integer);
            }
            if (tc.get("rope_local_base_freq")) |v| {
                rope_local_theta = switch (v) {
                    .float => @floatCast(v.float),
                    .integer => @as(f32, @floatFromInt(v.integer)),
                    else => 0,
                };
            }
            if (tc.get("query_pre_attn_scalar")) |v| {
                query_pre_attn_scalar = switch (v) {
                    .float => @floatCast(v.float),
                    .integer => @as(f32, @floatFromInt(v.integer)),
                    else => query_pre_attn_scalar,
                };
            }
            if (tc.get("rope_scaling")) |rs_val| {
                if (rs_val == .object) {
                    rope_scaling = cfg.parseRopeScalingFromObject(rs_val.object);
                }
            }
        }
    }
    // Some Gemma3 conditional-generation configs omit these fields but still rely on the defaults.
    if (sliding_window > 0 and sliding_window_pattern == 0) sliding_window_pattern = 6;
    if (sliding_window > 0 and rope_local_theta == 0) rope_local_theta = 10_000.0;

    // Infer vocab_size and d_model from embeddings.
    const embed_name = st_names.getNameAny(st, &hf_layout.token_embeddings_weight) catch return error.MissingField;

    const embed = try st.getTensor(embed_name, null);
    if (embed.n_dims != 2) return error.InvalidShape;
    const vocab_size: i32 = @intCast(embed.shape[0]);
    const d_model: i32 = @intCast(embed.shape[1]);

    if (n_layers <= 0) return error.MissingField;

    // Infer heads/head_dim from layer 0 shapes (Gemma3 uses Q/K norms of length head_dim).
    var name_buf: [128]u8 = undefined;
    const q_norm_name = st_names.selectNameLayer(st, name_buf[0..], 0, &hf_layout.q_norm_weight) catch return error.MissingField;
    const q_proj_name = st_names.selectNameLayer(st, name_buf[0..], 0, &hf_layout.q_proj_weight) catch return error.MissingField;
    const k_proj_name = st_names.selectNameLayer(st, name_buf[0..], 0, &hf_layout.k_proj_weight) catch return error.MissingField;

    const q_norm = try st.getTensor(q_norm_name, null);
    const q_proj = try st.getTensor(q_proj_name, null);
    const k_proj = try st.getTensor(k_proj_name, null);

    if (q_norm.n_dims != 1 or q_proj.n_dims != 2 or k_proj.n_dims != 2) return error.InvalidShape;
    const head_dim: i32 = @intCast(q_norm.shape[0]);
    const q_dim: i32 = @intCast(q_proj.shape[0]);
    const kv_dim: i32 = @intCast(k_proj.shape[0]);
    if (head_dim <= 0 or q_dim <= 0 or kv_dim <= 0) return error.InvalidValue;
    if (@mod(q_dim, head_dim) != 0 or @mod(kv_dim, head_dim) != 0) return error.InvalidValue;
    const n_heads: i32 = @divTrunc(q_dim, head_dim);
    const n_kv_heads: i32 = @divTrunc(kv_dim, head_dim);

    // Infer d_ff from weights if missing.
    if (d_ff <= 0) {
        const gate_name = st_names.selectNameLayer(st, name_buf[0..], 0, &hf_layout.gate_proj_weight) catch return error.MissingField;
        const gate = try st.getTensor(gate_name, null);
        if (gate.n_dims != 2) return error.InvalidShape;
        d_ff = @intCast(gate.shape[0]);
    }

    // Max sequence length is not always serialized in conditional-generation configs; pick a safe default.
    const max_seq_len: i32 = 32768;

    // Gemma3 defaults (matching gemma-3-1b-it config.json).
    const rope_theta: f32 = 1_000_000.0;
    const norm_eps: f32 = 1e-6;

    var bos_token_id: ?i32 = null;
    if (obj.get("bos_token_id")) |v| {
        if (v == .integer) bos_token_id = @intCast(v.integer);
    }

    return .{
        .vocab_size = vocab_size,
        .d_model = d_model,
        .n_layers = n_layers,
        .n_heads = n_heads,
        .n_kv_groups = n_kv_heads,
        .d_ff = d_ff,
        .max_seq_len = max_seq_len,
        .head_dim = head_dim,
        .rope_theta = rope_theta,
        .norm_eps = norm_eps,
        .gaffine_group_size = 64,
        .gaffine_bits = 4,
        .tie_word_embeddings = true,
        .num_experts = 0,
        .experts_per_token = 0,
        .attention_bias = false,
        .quant_method = .none,
        .rope_scaling = rope_scaling,
        .model_arch = .gemma3,
        .use_gelu = true,
        .use_qk_norm = true,
        .query_pre_attn_scalar = query_pre_attn_scalar,
        .rope_local_theta = rope_local_theta,
        .sliding_window = sliding_window,
        .sliding_window_pattern = sliding_window_pattern,
        .embedding_multiplier = 1.0,
        .attention_multiplier = 0,
        .residual_multiplier = 1.0,
        .logits_scaling = 1.0,
        .bos_token_id = bos_token_id,
    };
}
