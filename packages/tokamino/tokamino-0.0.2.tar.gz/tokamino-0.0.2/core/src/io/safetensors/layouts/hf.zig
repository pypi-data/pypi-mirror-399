/// HuggingFace safetensors naming variants.
///
/// This module centralizes key-path variants (e.g. `model.layers.*` vs
/// `language_model.model.layers.*`) so loaders/backends can avoid embedding
/// model-packaging-specific strings.

pub const ln1_weight = [_][]const u8{
    "layers.{d}.ln1.weight",
    "model.layers.{d}.input_layernorm.weight",
    "language_model.model.layers.{d}.input_layernorm.weight",
};

pub const ln2_weight = [_][]const u8{
    "layers.{d}.ln2.weight",
    "model.layers.{d}.post_attention_layernorm.weight",
    "language_model.model.layers.{d}.post_attention_layernorm.weight",
};

pub const q_proj_weight = [_][]const u8{
    "layers.{d}.attn.q_proj.weight",
    "model.layers.{d}.self_attn.q_proj.weight",
    "language_model.model.layers.{d}.self_attn.q_proj.weight",
};

/// Phi-style fused QKV projection (Q, K, V concatenated into single weight)
pub const qkv_proj_weight = [_][]const u8{
    "model.layers.{d}.self_attn.qkv_proj.weight",
};

pub const k_proj_weight = [_][]const u8{
    "layers.{d}.attn.k_proj.weight",
    "model.layers.{d}.self_attn.k_proj.weight",
    "language_model.model.layers.{d}.self_attn.k_proj.weight",
};

pub const v_proj_weight = [_][]const u8{
    "layers.{d}.attn.v_proj.weight",
    "model.layers.{d}.self_attn.v_proj.weight",
    "language_model.model.layers.{d}.self_attn.v_proj.weight",
};

pub const o_proj_weight = [_][]const u8{
    "layers.{d}.attn.output_proj.weight",
    "model.layers.{d}.self_attn.o_proj.weight",
    "language_model.model.layers.{d}.self_attn.o_proj.weight",
};

pub const q_norm_weight = [_][]const u8{
    "layers.{d}.attn.q_norm.weight",
    "model.layers.{d}.self_attn.q_norm.weight",
    "language_model.model.layers.{d}.self_attn.q_norm.weight",
};

pub const k_norm_weight = [_][]const u8{
    "layers.{d}.attn.k_norm.weight",
    "model.layers.{d}.self_attn.k_norm.weight",
    "language_model.model.layers.{d}.self_attn.k_norm.weight",
};

pub const down_proj_weight = [_][]const u8{
    "layers.{d}.ffn.w2.weight",
    "model.layers.{d}.mlp.down_proj.weight",
    "language_model.model.layers.{d}.mlp.down_proj.weight",
};

pub const gate_proj_weight = [_][]const u8{
    "layers.{d}.ffn.w1.weight",
    "model.layers.{d}.mlp.gate_proj.weight",
    "language_model.model.layers.{d}.mlp.gate_proj.weight",
};

pub const up_proj_weight = [_][]const u8{
    "layers.{d}.ffn.w3.weight",
    "model.layers.{d}.mlp.up_proj.weight",
    "language_model.model.layers.{d}.mlp.up_proj.weight",
};

/// Phi-style fused gate+up projection (gate and up concatenated into single weight)
pub const gate_up_proj_weight = [_][]const u8{
    "model.layers.{d}.mlp.gate_up_proj.weight",
};

pub const pre_ffn_norm_weight = [_][]const u8{
    "model.layers.{d}.pre_feedforward_layernorm.weight",
    "language_model.model.layers.{d}.pre_feedforward_layernorm.weight",
};

pub const post_ffn_norm_weight = [_][]const u8{
    "model.layers.{d}.post_feedforward_layernorm.weight",
    "language_model.model.layers.{d}.post_feedforward_layernorm.weight",
};

pub const token_embeddings_weight = [_][]const u8{
    "token_embeddings.weight",
    "model.embed_tokens.weight",
    "language_model.model.embed_tokens.weight",
};

pub const ln_final_weight = [_][]const u8{
    "ln_final.weight",
    "model.norm.weight",
    "language_model.model.norm.weight",
};

pub const lm_head_weight = [_][]const u8{
    "lm_head.weight",
    "language_model.lm_head.weight",
};

// Attention biases (GPT-OSS and other models with attention biases)
pub const q_proj_bias = [_][]const u8{
    "model.layers.{d}.self_attn.q_proj.bias",
    "language_model.model.layers.{d}.self_attn.q_proj.bias",
};

pub const k_proj_bias = [_][]const u8{
    "model.layers.{d}.self_attn.k_proj.bias",
    "language_model.model.layers.{d}.self_attn.k_proj.bias",
};

pub const v_proj_bias = [_][]const u8{
    "model.layers.{d}.self_attn.v_proj.bias",
    "language_model.model.layers.{d}.self_attn.v_proj.bias",
};

pub const o_proj_bias = [_][]const u8{
    "model.layers.{d}.self_attn.o_proj.bias",
    "language_model.model.layers.{d}.self_attn.o_proj.bias",
};

// Attention sinks (GPT-OSS specific - extra logit per head prepended before softmax)
pub const attn_sinks = [_][]const u8{
    "model.layers.{d}.self_attn.sinks",
    "language_model.model.layers.{d}.self_attn.sinks",
};

