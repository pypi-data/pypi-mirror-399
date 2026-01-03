//! Tensor Role Mapping
//!
//! Maps HuggingFace tensor names to canonical roles.
//! Single source of truth for weight naming conventions.

const std = @import("std");

/// Canonical tensor roles in a transformer model.
pub const Role = enum {
    // Embeddings
    token_embed,

    // Attention (per-layer)
    attn_q,
    attn_k,
    attn_v,
    attn_o,
    attn_q_norm,
    attn_k_norm,

    // FFN (per-layer)
    ffn_gate,
    ffn_up,
    ffn_down,

    // Norms (per-layer)
    attn_norm,
    ffn_norm,
    post_attn_norm, // Gemma3: post_attention_layernorm
    post_ffn_norm, // Gemma3: post_feedforward_layernorm

    // Final
    final_norm,
    lm_head,

    // Unknown - passed through as-is
    unknown,
};

/// Parsed tensor information.
pub const TensorInfo = struct {
    role: Role,
    layer: ?u32, // null for non-layer tensors (embeddings, final norm, lm_head)
    original_name: []const u8, // Original HF name for error messages
};

/// Parse HuggingFace tensor name to canonical role.
/// Handles: Qwen, LLaMA, Mistral, Gemma naming conventions.
pub fn parseHfName(name: []const u8) TensorInfo {
    // Non-layer tensors
    if (std.mem.eql(u8, name, "model.embed_tokens.weight")) {
        return .{ .role = .token_embed, .layer = null, .original_name = name };
    }
    if (std.mem.eql(u8, name, "model.norm.weight")) {
        return .{ .role = .final_norm, .layer = null, .original_name = name };
    }
    if (std.mem.eql(u8, name, "lm_head.weight")) {
        return .{ .role = .lm_head, .layer = null, .original_name = name };
    }

    // Layer tensors: model.layers.N.component
    if (std.mem.startsWith(u8, name, "model.layers.")) {
        var it = std.mem.splitSequence(u8, name, ".");
        _ = it.next(); // "model"
        _ = it.next(); // "layers"
        const layer_str = it.next() orelse return unknown(name);
        const layer = std.fmt.parseInt(u32, layer_str, 10) catch return unknown(name);
        const component = it.rest();

        const role = parseLayerComponent(component);
        return .{ .role = role, .layer = layer, .original_name = name };
    }

    return unknown(name);
}

fn unknown(name: []const u8) TensorInfo {
    return .{ .role = .unknown, .layer = null, .original_name = name };
}

/// Parse the component part of a layer tensor name.
fn parseLayerComponent(component: []const u8) Role {
    // Attention projections
    if (std.mem.eql(u8, component, "self_attn.q_proj.weight")) return .attn_q;
    if (std.mem.eql(u8, component, "self_attn.k_proj.weight")) return .attn_k;
    if (std.mem.eql(u8, component, "self_attn.v_proj.weight")) return .attn_v;
    if (std.mem.eql(u8, component, "self_attn.o_proj.weight")) return .attn_o;

    // QK norms (Qwen3)
    if (std.mem.eql(u8, component, "self_attn.q_norm.weight")) return .attn_q_norm;
    if (std.mem.eql(u8, component, "self_attn.k_norm.weight")) return .attn_k_norm;

    // FFN projections (SwiGLU)
    if (std.mem.eql(u8, component, "mlp.gate_proj.weight")) return .ffn_gate;
    if (std.mem.eql(u8, component, "mlp.up_proj.weight")) return .ffn_up;
    if (std.mem.eql(u8, component, "mlp.down_proj.weight")) return .ffn_down;

    // Layer norms - standard (LLaMA/Qwen)
    if (std.mem.eql(u8, component, "input_layernorm.weight")) return .attn_norm;
    if (std.mem.eql(u8, component, "post_attention_layernorm.weight")) return .ffn_norm;

    // Gemma3 has 4 norms per layer
    if (std.mem.eql(u8, component, "pre_feedforward_layernorm.weight")) return .ffn_norm;
    if (std.mem.eql(u8, component, "post_feedforward_layernorm.weight")) return .post_ffn_norm;

    return .unknown;
}


/// Determine if a tensor should be quantized based on its role.
/// Layer norms and small tensors should NOT be quantized.
pub fn shouldQuantize(role: Role) bool {
    return switch (role) {
        // Quantize large weight matrices
        .token_embed, .lm_head => true,
        .attn_q, .attn_k, .attn_v, .attn_o => true,
        .ffn_gate, .ffn_up, .ffn_down => true,

        // Do NOT quantize norms (small, need precision)
        .attn_norm, .ffn_norm, .final_norm => false,
        .post_attn_norm, .post_ffn_norm => false,
        .attn_q_norm, .attn_k_norm => false,

        // Unknown - be conservative, don't quantize
        .unknown => false,
    };
}

/// Check if a tensor is the lm_head (output projection).
/// Used for tie_word_embeddings check.
pub fn isLmHead(role: Role) bool {
    return role == .lm_head;
}

// =============================================================================
// Tests
// =============================================================================

test "parseHfName - embeddings" {
    const info = parseHfName("model.embed_tokens.weight");
    try std.testing.expectEqual(Role.token_embed, info.role);
    try std.testing.expectEqual(@as(?u32, null), info.layer);
}

test "parseHfName - layer tensors" {
    {
        const info = parseHfName("model.layers.0.self_attn.q_proj.weight");
        try std.testing.expectEqual(Role.attn_q, info.role);
        try std.testing.expectEqual(@as(?u32, 0), info.layer);
    }
    {
        const info = parseHfName("model.layers.15.mlp.gate_proj.weight");
        try std.testing.expectEqual(Role.ffn_gate, info.role);
        try std.testing.expectEqual(@as(?u32, 15), info.layer);
    }
    {
        const info = parseHfName("model.layers.7.post_attention_layernorm.weight");
        try std.testing.expectEqual(Role.ffn_norm, info.role);
        try std.testing.expectEqual(@as(?u32, 7), info.layer);
    }
}

test "parseHfName - final norm and lm_head" {
    {
        const info = parseHfName("model.norm.weight");
        try std.testing.expectEqual(Role.final_norm, info.role);
        try std.testing.expectEqual(@as(?u32, null), info.layer);
    }
    {
        const info = parseHfName("lm_head.weight");
        try std.testing.expectEqual(Role.lm_head, info.role);
        try std.testing.expectEqual(@as(?u32, null), info.layer);
    }
}

test "shouldQuantize" {
    // Large weight matrices - yes
    try std.testing.expect(shouldQuantize(.attn_q));
    try std.testing.expect(shouldQuantize(.ffn_gate));
    try std.testing.expect(shouldQuantize(.token_embed));

    // Norms - no
    try std.testing.expect(!shouldQuantize(.attn_norm));
    try std.testing.expect(!shouldQuantize(.ffn_norm));
    try std.testing.expect(!shouldQuantize(.final_norm));
}

