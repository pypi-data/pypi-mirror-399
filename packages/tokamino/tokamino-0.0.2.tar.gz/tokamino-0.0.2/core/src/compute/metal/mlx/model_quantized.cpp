// MLX Bridge - Quantized (4-bit) Model
//
// Full transformer implementation using 4-bit quantized weights.
// Uses MLX's quantized_matmul for 8x memory bandwidth savings.

#include "common.h"

// ============================================================================
// Quantized Model Structure
// ============================================================================

struct FusedModelWeights {
    struct Layer {
        array ln1_w = array(0.0f, float32);  // attention norm
        array q_w = array(0.0f, float32), q_s = array(0.0f, float32), q_b = array(0.0f, float32);
        array k_w = array(0.0f, float32), k_s = array(0.0f, float32), k_b = array(0.0f, float32);
        array v_w = array(0.0f, float32), v_s = array(0.0f, float32), v_b = array(0.0f, float32);
        array o_w = array(0.0f, float32), o_s = array(0.0f, float32), o_b = array(0.0f, float32);
        array ln2_w = array(0.0f, float32);  // ffn norm (or post_attention_layernorm for Gemma3)
        array gate_w = array(0.0f, float32), gate_s = array(0.0f, float32), gate_b = array(0.0f, float32);
        array up_w = array(0.0f, float32), up_s = array(0.0f, float32), up_b = array(0.0f, float32);
        array down_w = array(0.0f, float32), down_s = array(0.0f, float32), down_b = array(0.0f, float32);
        std::optional<array> q_norm;
        std::optional<array> k_norm;
        // Gemma3-specific FFN norms (4 norms per block)
        std::optional<array> pre_ffn_norm;
        std::optional<array> post_ffn_norm;
        // Fused weights (created at model setup time for efficiency)
        // QKV fused: [hidden_dim, (n_heads + 2*n_kv_heads) * head_dim]
        std::optional<array> qkv_w, qkv_s, qkv_b;
        // Gate+Up fused: [hidden_dim, 2 * d_ff]
        std::optional<array> gate_up_w, gate_up_s, gate_up_b;
        bool use_fused_qkv = false;
        bool use_fused_gate_up = false;
    };
    std::vector<Layer> layers;

    array ln_final = array(0.0f, float32);
    array lm_head_w = array(0.0f, float32), lm_head_s = array(0.0f, float32), lm_head_b = array(0.0f, float32);
    array embed_w = array(0.0f, float32), embed_s = array(0.0f, float32), embed_b = array(0.0f, float32);

    int n_heads = 0;
    int n_kv_heads = 0;
    int head_dim = 0;
    int hidden_dim = 0;
    int group_size = 0;
    int bits = 4;
    float rope_theta = 0.0f;
    float rms_eps = 0.0f;

    // Custom RoPE frequencies for Llama3-style scaling
    std::optional<array> rope_freqs;

    // Gemma3-specific config
    bool is_gemma3 = false;
    bool use_gelu = false;  // GELU instead of SiLU
    float query_pre_attn_scalar = 0.0f;  // Custom attention scale

    // Granite-specific config (scaling multipliers)
    bool is_granite = false;
    float embedding_multiplier = 1.0f;  // Scales embedding output
    float attention_multiplier = 0.0f;  // Custom attention scale (0 = use 1/sqrt(head_dim))
    float residual_multiplier = 1.0f;   // Scales residual connections
    float logits_scaling = 1.0f;        // Scales output logits

    // Compiled forward function for decode (eliminates graph rebuild overhead)
    std::function<std::vector<array>(const std::vector<array>&)> compiled_decode;
    bool is_compiled = false;
};

static FusedModelWeights* g_fused_weights = nullptr;

// Pipeline state
static thread_local std::optional<array> g_current_token;
static thread_local std::optional<array> g_pending_token;

// ============================================================================
// Forward Pass Implementation
// ============================================================================

static array fused_forward_from_token(
    FusedModelWeights* m,
    MLXCache* cache,
    const array& token_idx,
    size_t pos_offset
) {
    const int gs = m->group_size;
    const int bits = m->bits;
    const int n_layers = static_cast<int>(m->layers.size());

    // Debug: print config on first call
    static bool printed_config = false;
    bool debug_fwd = (getenv("TOKATAMI_DEBUG_FWD") != nullptr);

    // Always print on first call to verify function is being called
    static bool first_call = true;
    if (first_call && debug_fwd) {
        fprintf(stderr, "[DEBUG] fused_forward_from_token called\n");
        first_call = false;
    }
    if (!printed_config && debug_fwd) {
        fprintf(stderr, "[DEBUG] C++ Forward Config:\n");
        fprintf(stderr, "  is_gemma3: %d\n", m->is_gemma3);
        fprintf(stderr, "  is_granite: %d\n", m->is_granite);
        fprintf(stderr, "  use_gelu: %d\n", m->use_gelu);
        fprintf(stderr, "  query_pre_attn_scalar: %.2f\n", m->query_pre_attn_scalar);
        fprintf(stderr, "  embedding_multiplier: %.4f\n", m->embedding_multiplier);
        fprintf(stderr, "  attention_multiplier: %.6f\n", m->attention_multiplier);
        fprintf(stderr, "  residual_multiplier: %.4f\n", m->residual_multiplier);
        fprintf(stderr, "  logits_scaling: %.4f\n", m->logits_scaling);
        fprintf(stderr, "  hidden_dim: %d\n", m->hidden_dim);
        fprintf(stderr, "  head_dim: %d\n", m->head_dim);
        fprintf(stderr, "  rope_theta: %.2f\n", m->rope_theta);
        fprintf(stderr, "  rms_eps: %.6f\n", m->rms_eps);
        fprintf(stderr, "  n_layers: %d\n", n_layers);
        fprintf(stderr, "  layer[0].pre_ffn_norm: %s\n", m->layers[0].pre_ffn_norm ? "yes" : "no");
        fprintf(stderr, "  layer[0].post_ffn_norm: %s\n", m->layers[0].post_ffn_norm ? "yes" : "no");
        fprintf(stderr, "  layer[0].q_norm: %s\n", m->layers[0].q_norm ? "yes" : "no");
        fprintf(stderr, "  layer[0].k_norm: %s\n", m->layers[0].k_norm ? "yes" : "no");
        printed_config = true;
    }

    // Attention scale:
    // - Granite: use attention_multiplier directly (0.015625 = 1/64)
    // - Gemma3: use 1/sqrt(query_pre_attn_scalar)
    // - Others: use 1/sqrt(head_dim)
    const float attn_scale = (m->attention_multiplier > 0.0f)
        ? m->attention_multiplier
        : (m->query_pre_attn_scalar > 0.0f)
            ? (1.0f / std::sqrt(m->query_pre_attn_scalar))
            : (1.0f / std::sqrt(static_cast<float>(m->head_dim)));
    const Shape q_shape = {1, 1, m->n_heads, m->head_dim};
    const Shape kv_shape = {1, 1, m->n_kv_heads, m->head_dim};
    const Shape attn_out_shape = {1, 1, m->n_heads * m->head_dim};

    // Embedding lookup (quantized)
    array idx = reshape(astype(token_idx, int32), {1, 1});
    array embed_rows = take(m->embed_w, idx, 0);
    array scale_rows = take(m->embed_s, idx, 0);
    array bias_rows = take(m->embed_b, idx, 0);
    array hidden = dequantize(embed_rows, scale_rows, bias_rows, gs, bits, "affine");

    // Debug: print embedding values (reset counter on each build)
    static int debug_step = 0;
    if (debug_fwd) {
        // Print the token ID being looked up
        eval(token_idx);
        int32_t tok_id = token_idx.item<int32_t>();
        fprintf(stderr, "[DEBUG step=%d] Token ID: %d\n", debug_step, tok_id);
    }
    if (debug_fwd && debug_step < 2) {

        eval(hidden);
        fprintf(stderr, "[DEBUG step=%d] After embedding dequantize, hidden shape=[%d,%d,%d]\n",
            debug_step, hidden.shape(0), hidden.shape(1), hidden.shape(2));
        // Print first few values
        auto h_f32 = astype(hidden, float32);
        eval(h_f32);
        auto* h_data = h_f32.data<float>();
        fprintf(stderr, "  hidden[0:4] = [%.4f, %.4f, %.4f, %.4f]\n", h_data[0], h_data[1], h_data[2], h_data[3]);
    }

    // Embedding scaling:
    // - Granite: scale by embedding_multiplier (e.g., 12.0)
    // - Gemma3: scale by sqrt(hidden_dim)
    if (m->embedding_multiplier != 1.0f) {
        hidden = hidden * m->embedding_multiplier;
        if (debug_fwd && debug_step < 2) {
            eval(hidden);
            auto h_f32 = astype(hidden, float32);
            eval(h_f32);
            auto* h_data = h_f32.data<float>();
            fprintf(stderr, "[DEBUG step=%d] After embedding scale (%.4f), hidden[0:4] = [%.4f, %.4f, %.4f, %.4f]\n",
                debug_step, m->embedding_multiplier,
                h_data[0], h_data[1], h_data[2], h_data[3]);
        }
    } else if (m->is_gemma3) {
        hidden = hidden * std::sqrt(static_cast<float>(m->hidden_dim));
        if (debug_fwd && debug_step < 2) {
            eval(hidden);
            auto h_f32 = astype(hidden, float32);
            eval(h_f32);
            auto* h_data = h_f32.data<float>();
            fprintf(stderr, "[DEBUG step=%d] After embedding scale (sqrt(%d)=%.4f), hidden[0:4] = [%.4f, %.4f, %.4f, %.4f]\n",
                debug_step, m->hidden_dim, std::sqrt(static_cast<float>(m->hidden_dim)),
                h_data[0], h_data[1], h_data[2], h_data[3]);
        }
    }

    for (int layer_idx = 0; layer_idx < n_layers; layer_idx++) {
        const auto& l = m->layers[layer_idx];
        auto& cl = cache->layers[layer_idx];

        array normed = fast::rms_norm(hidden, l.ln1_w, m->rms_eps);

        array q(0.0f), k(0.0f), v(0.0f);
        if (l.use_fused_qkv && l.qkv_w) {
            // Fused QKV: single matmul then split
            array qkv = quantized_matmul(normed, *l.qkv_w, *l.qkv_s, *l.qkv_b, true, gs, bits, "affine");
            // Split: q=[n_heads*head_dim], k=[n_kv_heads*head_dim], v=[n_kv_heads*head_dim]
            int q_dim = m->n_heads * m->head_dim;
            int kv_dim = m->n_kv_heads * m->head_dim;
            q = slice(qkv, {0, 0, 0}, {1, 1, q_dim});
            k = slice(qkv, {0, 0, q_dim}, {1, 1, q_dim + kv_dim});
            v = slice(qkv, {0, 0, q_dim + kv_dim}, {1, 1, q_dim + 2 * kv_dim});
        } else {
            q = quantized_matmul(normed, l.q_w, l.q_s, l.q_b, true, gs, bits, "affine");
            k = quantized_matmul(normed, l.k_w, l.k_s, l.k_b, true, gs, bits, "affine");
            v = quantized_matmul(normed, l.v_w, l.v_s, l.v_b, true, gs, bits, "affine");
        }

        q = reshape(q, q_shape);
        k = reshape(k, kv_shape);
        v = reshape(v, kv_shape);

        if (l.q_norm) q = fast::rms_norm(q, *l.q_norm, m->rms_eps);
        if (l.k_norm) k = fast::rms_norm(k, *l.k_norm, m->rms_eps);

        q = transpose(q, g_transpose_perm);
        k = transpose(k, g_transpose_perm);
        v = transpose(v, g_transpose_perm);

        // Apply RoPE with custom frequencies (Llama3) or standard base
        if (m->rope_freqs) {
            q = fast::rope(q, m->head_dim, false, std::nullopt, 1.0f, static_cast<int>(pos_offset), m->rope_freqs);
            k = fast::rope(k, m->head_dim, false, std::nullopt, 1.0f, static_cast<int>(pos_offset), m->rope_freqs);
        } else {
            q = fast::rope(q, m->head_dim, false, m->rope_theta, 1.0f, static_cast<int>(pos_offset));
            k = fast::rope(k, m->head_dim, false, m->rope_theta, 1.0f, static_cast<int>(pos_offset));
        }

        // Cache update
        size_t prev = cl.offset;
        int offset = static_cast<int>(prev + 1);

        if (cl.k_bfloat16 == nullptr || offset > cl.k_bfloat16->shape(2)) {
            int new_size = ((offset + cl.step - 1) / cl.step) * cl.step;
            Shape shape = {1, m->n_kv_heads, new_size, m->head_dim};
            if (cl.k_bfloat16) {
                array new_k = zeros(shape, bfloat16);
                array new_v = zeros(shape, bfloat16);
                Shape stop = {1, m->n_kv_heads, static_cast<int>(prev), m->head_dim};
                new_k = slice_update(new_k, slice(*cl.k_bfloat16, g_slice_start, stop), g_slice_start, stop);
                new_v = slice_update(new_v, slice(*cl.v_bfloat16, g_slice_start, stop), g_slice_start, stop);
                *cl.k_bfloat16 = new_k;
                *cl.v_bfloat16 = new_v;
            } else {
                cl.k_bfloat16 = new array(zeros(shape, bfloat16));
                cl.v_bfloat16 = new array(zeros(shape, bfloat16));
            }
        }

        Shape update_start = {0, 0, static_cast<int>(prev), 0};
        Shape update_stop = {1, m->n_kv_heads, offset, m->head_dim};
        *cl.k_bfloat16 = slice_update(*cl.k_bfloat16, k, update_start, update_stop);
        *cl.v_bfloat16 = slice_update(*cl.v_bfloat16, v, update_start, update_stop);
        cl.offset = offset;

        const Shape slice_stop = {1, m->n_kv_heads, offset, m->head_dim};
        array k_full = slice(*cl.k_bfloat16, g_slice_start, slice_stop);
        array v_full = slice(*cl.v_bfloat16, g_slice_start, slice_stop);

        array attn_out = fast::scaled_dot_product_attention(q, k_full, v_full, attn_scale, "");

        attn_out = transpose(attn_out, g_transpose_perm);
        attn_out = reshape(attn_out, attn_out_shape);

        array attn_proj = quantized_matmul(attn_out, l.o_w, l.o_s, l.o_b, true, gs, bits, "affine");

        // Gemma3: apply post_attention_layernorm to attn output before residual
        if (m->is_gemma3) {
            attn_proj = fast::rms_norm(attn_proj, l.ln2_w, m->rms_eps);
        }
        // Granite: scale layer output by residual_multiplier (NOT the residual input)
        array hidden_1 = (m->residual_multiplier != 1.0f)
            ? hidden + attn_proj * m->residual_multiplier
            : hidden + attn_proj;

        // FFN normalization: Gemma3 uses pre_ffn_norm, others use ln2
        array normed_2 = (m->is_gemma3 && l.pre_ffn_norm)
            ? fast::rms_norm(hidden_1, *l.pre_ffn_norm, m->rms_eps)
            : fast::rms_norm(hidden_1, l.ln2_w, m->rms_eps);

        array gate(0.0f), up(0.0f);
        if (l.use_fused_gate_up && l.gate_up_w) {
            // Fused gate/up: single matmul then split
            array gate_up = quantized_matmul(normed_2, *l.gate_up_w, *l.gate_up_s, *l.gate_up_b, true, gs, bits, "affine");
            int d_ff = l.gate_w.shape(0);  // FFN intermediate size
            gate = slice(gate_up, {0, 0, 0}, {1, 1, d_ff});
            up = slice(gate_up, {0, 0, d_ff}, {1, 1, 2 * d_ff});
        } else {
            gate = quantized_matmul(normed_2, l.gate_w, l.gate_s, l.gate_b, true, gs, bits, "affine");
            up = quantized_matmul(normed_2, l.up_w, l.up_s, l.up_b, true, gs, bits, "affine");
        }

        // Activation: Gemma3 uses GELU, others use SiLU
        array mid = [&]() -> array {
            if (m->use_gelu) {
                // GELU approximation: x * 0.5 * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
                const float sqrt_2_over_pi = 0.7978845608f;
                array x3 = gate * gate * gate;
                array inner = sqrt_2_over_pi * (gate + 0.044715f * x3);
                return gate * 0.5f * (1.0f + tanh(inner)) * up;
            } else {
                return (gate * sigmoid(gate)) * up;
            }
        }();
        array down = quantized_matmul(mid, l.down_w, l.down_s, l.down_b, true, gs, bits, "affine");

        // Gemma3: apply post_feedforward_layernorm to ffn output before residual
        if (m->is_gemma3 && l.post_ffn_norm) {
            down = fast::rms_norm(down, *l.post_ffn_norm, m->rms_eps);
        }

        // Granite: scale layer output by residual_multiplier (NOT the residual input)
        hidden = (m->residual_multiplier != 1.0f)
            ? hidden_1 + down * m->residual_multiplier
            : hidden_1 + down;

        // Debug: print after first layer
        if (debug_fwd && debug_step < 2 && layer_idx == 0) {
            eval(hidden);
            auto h_f32 = astype(hidden, float32);
            eval(h_f32);
            auto* h_data = h_f32.data<float>();
            fprintf(stderr, "[DEBUG step=%d] After layer 0, hidden[0:4] = [%.4f, %.4f, %.4f, %.4f]\n",
                debug_step, h_data[0], h_data[1], h_data[2], h_data[3]);
        }
    }

    // Debug: print before final norm
    if (debug_fwd && debug_step < 2) {
        eval(hidden);
        auto h_f32 = astype(hidden, float32);
        eval(h_f32);
        auto* h_data = h_f32.data<float>();
        fprintf(stderr, "[DEBUG step=%d] Before final norm, hidden[0:4] = [%.4f, %.4f, %.4f, %.4f]\n",
            debug_step, h_data[0], h_data[1], h_data[2], h_data[3]);
    }

    array final_normed = fast::rms_norm(hidden, m->ln_final, m->rms_eps);

    // Debug: print after final norm
    if (debug_fwd && debug_step < 2) {
        eval(final_normed);
        auto h_f32 = astype(final_normed, float32);
        eval(h_f32);
        auto* h_data = h_f32.data<float>();
        fprintf(stderr, "[DEBUG step=%d] After final norm, hidden[0:4] = [%.4f, %.4f, %.4f, %.4f]\n",
            debug_step, h_data[0], h_data[1], h_data[2], h_data[3]);
        debug_step++;
    }
    array logits = quantized_matmul(final_normed, m->lm_head_w, m->lm_head_s, m->lm_head_b, true, gs, bits, "affine");

    // Granite: scale logits by logits_scaling (divide, not multiply!)
    if (m->logits_scaling != 1.0f) {
        logits = logits / m->logits_scaling;
    }

    return argmax(reshape(logits, {-1}), 0);
}

// ============================================================================
// C API - Model Lifecycle
// ============================================================================

extern "C" {

void* mlx_fused_model_create(
    size_t n_layers,
    size_t n_heads, size_t n_kv_heads, size_t head_dim, size_t hidden_dim,
    size_t group_size, size_t bits, float rope_theta, float rms_eps
) {
    auto* w = new FusedModelWeights();
    w->layers.resize(n_layers);
    w->n_heads = static_cast<int>(n_heads);
    w->n_kv_heads = static_cast<int>(n_kv_heads);
    w->head_dim = static_cast<int>(head_dim);
    w->hidden_dim = static_cast<int>(hidden_dim);
    w->group_size = static_cast<int>(group_size);
    w->bits = static_cast<int>(bits);
    w->rope_theta = rope_theta;
    w->rms_eps = rms_eps;
    g_fused_weights = w;

    // Debug: print model config
    fprintf(stderr, "[MLX] FusedModel: layers=%zu heads=%zu kv_heads=%zu head_dim=%zu hidden=%zu group_size=%zu bits=%zu\n",
            n_layers, n_heads, n_kv_heads, head_dim, hidden_dim, group_size, bits);

    return w;
}

void mlx_fused_model_set_embeddings(void* model, const void* w, const void* s, const void* b) {
    auto* m = static_cast<FusedModelWeights*>(model);
    m->embed_w = *static_cast<const array*>(w);
    m->embed_s = *static_cast<const array*>(s);
    m->embed_b = *static_cast<const array*>(b);

    // Debug: print array properties
    if (getenv("TOKATAMI_DEBUG_ARRAYS") != nullptr) {
        const auto& ew = m->embed_w;
        const auto& es = m->embed_s;
        fprintf(stderr, "[MLX] embed_w: shape=[%d,%d] dtype=%s contiguous=%d row_contiguous=%d\n",
                ew.shape(0), ew.shape(1), ew.dtype() == uint32 ? "u32" : "other",
                ew.flags().contiguous ? 1 : 0,
                ew.flags().row_contiguous ? 1 : 0);
        fprintf(stderr, "[MLX] embed_s: shape=[%d,%d] dtype=%s contiguous=%d row_contiguous=%d\n",
                es.shape(0), es.shape(1), es.dtype() == bfloat16 ? "bf16" : "other",
                es.flags().contiguous ? 1 : 0,
                es.flags().row_contiguous ? 1 : 0);
    }
}

void mlx_fused_model_set_final(void* model, const void* ln_w, const void* lm_w, const void* lm_s, const void* lm_b) {
    auto* m = static_cast<FusedModelWeights*>(model);
    m->ln_final = *static_cast<const array*>(ln_w);
    m->lm_head_w = *static_cast<const array*>(lm_w);
    m->lm_head_s = *static_cast<const array*>(lm_s);
    m->lm_head_b = *static_cast<const array*>(lm_b);
}

void mlx_fused_model_set_rope_freqs(void* model, const void* freqs) {
    auto* m = static_cast<FusedModelWeights*>(model);
    m->rope_freqs = *static_cast<const array*>(freqs);
}

void mlx_fused_model_set_gemma3_config(void* model, bool is_gemma3, bool use_gelu, float query_pre_attn_scalar) {
    auto* m = static_cast<FusedModelWeights*>(model);
    m->is_gemma3 = is_gemma3;
    m->use_gelu = use_gelu;
    m->query_pre_attn_scalar = query_pre_attn_scalar;
}

void mlx_fused_model_set_granite_config(
    void* model,
    bool is_granite,
    float embedding_multiplier,
    float attention_multiplier,
    float residual_multiplier,
    float logits_scaling
) {
    auto* m = static_cast<FusedModelWeights*>(model);
    m->is_granite = is_granite;
    m->embedding_multiplier = embedding_multiplier;
    m->attention_multiplier = attention_multiplier;
    m->residual_multiplier = residual_multiplier;
    m->logits_scaling = logits_scaling;
}

void mlx_fused_model_set_layer(
    void* model, size_t layer_idx,
    const void* ln1_w,
    const void* q_w, const void* q_s, const void* q_b,
    const void* k_w, const void* k_s, const void* k_b,
    const void* v_w, const void* v_s, const void* v_b,
    const void* o_w, const void* o_s, const void* o_b,
    const void* ln2_w,
    const void* gate_w, const void* gate_s, const void* gate_b,
    const void* up_w, const void* up_s, const void* up_b,
    const void* down_w, const void* down_s, const void* down_b,
    const void* q_norm, const void* k_norm,
    const void* pre_ffn_norm, const void* post_ffn_norm
) {
    auto* m = static_cast<FusedModelWeights*>(model);
    auto& l = m->layers[layer_idx];

    l.ln1_w = *static_cast<const array*>(ln1_w);
    l.q_w = *static_cast<const array*>(q_w);
    l.q_s = *static_cast<const array*>(q_s);
    l.q_b = *static_cast<const array*>(q_b);
    l.k_w = *static_cast<const array*>(k_w);
    l.k_s = *static_cast<const array*>(k_s);
    l.k_b = *static_cast<const array*>(k_b);
    l.v_w = *static_cast<const array*>(v_w);
    l.v_s = *static_cast<const array*>(v_s);
    l.v_b = *static_cast<const array*>(v_b);
    l.o_w = *static_cast<const array*>(o_w);
    l.o_s = *static_cast<const array*>(o_s);
    l.o_b = *static_cast<const array*>(o_b);
    l.ln2_w = *static_cast<const array*>(ln2_w);
    l.gate_w = *static_cast<const array*>(gate_w);
    l.gate_s = *static_cast<const array*>(gate_s);
    l.gate_b = *static_cast<const array*>(gate_b);
    l.up_w = *static_cast<const array*>(up_w);
    l.up_s = *static_cast<const array*>(up_s);
    l.up_b = *static_cast<const array*>(up_b);
    l.down_w = *static_cast<const array*>(down_w);
    l.down_s = *static_cast<const array*>(down_s);
    l.down_b = *static_cast<const array*>(down_b);
    if (q_norm) l.q_norm = *static_cast<const array*>(q_norm);
    if (k_norm) l.k_norm = *static_cast<const array*>(k_norm);
    if (pre_ffn_norm) l.pre_ffn_norm = *static_cast<const array*>(pre_ffn_norm);
    if (post_ffn_norm) l.post_ffn_norm = *static_cast<const array*>(post_ffn_norm);

    // Debug: print layer 0 array properties
    if (layer_idx == 0 && getenv("TOKATAMI_DEBUG_ARRAYS") != nullptr) {
        fprintf(stderr, "[MLX] Layer 0 q_w: shape=[%d,%d] contiguous=%d strides=[%lld,%lld]\n",
                l.q_w.shape(0), l.q_w.shape(1),
                l.q_w.flags().contiguous ? 1 : 0,
                (long long)l.q_w.strides()[0], (long long)l.q_w.strides()[1]);
        fprintf(stderr, "[MLX] Layer 0 gate_w: shape=[%d,%d] contiguous=%d strides=[%lld,%lld]\n",
                l.gate_w.shape(0), l.gate_w.shape(1),
                l.gate_w.flags().contiguous ? 1 : 0,
                (long long)l.gate_w.strides()[0], (long long)l.gate_w.strides()[1]);
    }
}

void mlx_fused_model_free(void* model) {
    delete static_cast<FusedModelWeights*>(model);
    if (g_fused_weights == model) g_fused_weights = nullptr;
}

// Fuse weights for faster inference - call after all layers are set
// NOTE: Disabled - weight fusion slows down single-token decode
void mlx_fused_model_optimize(void* model) {
    auto* m = static_cast<FusedModelWeights*>(model);

    // Pre-evaluate all weights to ensure they're transferred to GPU
    // This eliminates lazy transfer overhead during first inference
    std::vector<array> to_eval;
    to_eval.push_back(m->embed_w);
    to_eval.push_back(m->embed_s);
    to_eval.push_back(m->embed_b);
    to_eval.push_back(m->ln_final);
    to_eval.push_back(m->lm_head_w);
    to_eval.push_back(m->lm_head_s);
    to_eval.push_back(m->lm_head_b);

    for (auto& l : m->layers) {
        to_eval.push_back(l.ln1_w);
        to_eval.push_back(l.q_w);
        to_eval.push_back(l.q_s);
        to_eval.push_back(l.q_b);
        to_eval.push_back(l.k_w);
        to_eval.push_back(l.k_s);
        to_eval.push_back(l.k_b);
        to_eval.push_back(l.v_w);
        to_eval.push_back(l.v_s);
        to_eval.push_back(l.v_b);
        to_eval.push_back(l.o_w);
        to_eval.push_back(l.o_s);
        to_eval.push_back(l.o_b);
        to_eval.push_back(l.ln2_w);
        to_eval.push_back(l.gate_w);
        to_eval.push_back(l.gate_s);
        to_eval.push_back(l.gate_b);
        to_eval.push_back(l.up_w);
        to_eval.push_back(l.up_s);
        to_eval.push_back(l.up_b);
        to_eval.push_back(l.down_w);
        to_eval.push_back(l.down_s);
        to_eval.push_back(l.down_b);
    }
    eval(to_eval);

    // Silence message unless debug mode
    if (getenv("TOKATAMI_DEBUG_ARRAYS") != nullptr) {
        fprintf(stderr, "[MLX] Pre-evaluated %zu weight arrays\n", to_eval.size());
    }
}

// Global compiled step function (set once, reused for all decode steps)
static std::function<std::vector<array>(const std::vector<array>&)> g_compiled_step;

// Compile the decode step for maximum performance
// This traces the forward pass once and reuses the compiled graph
void mlx_fused_model_compile(void* model) {
    auto* m = static_cast<FusedModelWeights*>(model);
    if (m->is_compiled) return;

    const int gs = m->group_size;
    const int bits = m->bits;
    const int n_layers = static_cast<int>(m->layers.size());

    // Create step function that takes: [hidden, k_caches..., v_caches..., pos]
    // Returns: [next_token, new_k_caches..., new_v_caches...]
    auto step_fn = [m, gs, bits, n_layers](const std::vector<array>& inputs) -> std::vector<array> {
        // inputs[0] = hidden state [1, 1, hidden_dim]
        // inputs[1..n_layers] = k_cache for each layer
        // inputs[n_layers+1..2*n_layers] = v_cache for each layer
        // inputs[2*n_layers+1] = position offset scalar

        array hidden = inputs[0];
        int pos_idx = static_cast<int>(inputs[2 * n_layers + 1].item<int32_t>());

        const float attn_scale = (m->attention_multiplier > 0.0f)
            ? m->attention_multiplier
            : (m->query_pre_attn_scalar > 0.0f)
                ? 1.0f / std::sqrt(m->query_pre_attn_scalar)
                : 1.0f / std::sqrt(static_cast<float>(m->head_dim));

        std::vector<array> new_k_caches, new_v_caches;

        for (int layer_idx = 0; layer_idx < n_layers; layer_idx++) {
            const auto& l = m->layers[layer_idx];
            array k_cache = inputs[1 + layer_idx];
            array v_cache = inputs[1 + n_layers + layer_idx];

            array normed = fast::rms_norm(hidden, l.ln1_w, m->rms_eps);

            array q = quantized_matmul(normed, l.q_w, l.q_s, l.q_b, true, gs, bits, "affine");
            array k = quantized_matmul(normed, l.k_w, l.k_s, l.k_b, true, gs, bits, "affine");
            array v = quantized_matmul(normed, l.v_w, l.v_s, l.v_b, true, gs, bits, "affine");

            // Reshape for attention
            q = reshape(q, {1, 1, m->n_heads, m->head_dim});
            k = reshape(k, {1, 1, m->n_kv_heads, m->head_dim});
            v = reshape(v, {1, 1, m->n_kv_heads, m->head_dim});

            if (l.q_norm) q = fast::rms_norm(q, *l.q_norm, m->rms_eps);
            if (l.k_norm) k = fast::rms_norm(k, *l.k_norm, m->rms_eps);

            q = transpose(q, {0, 2, 1, 3});
            k = transpose(k, {0, 2, 1, 3});
            v = transpose(v, {0, 2, 1, 3});

            // RoPE
            if (m->rope_freqs) {
                q = fast::rope(q, m->head_dim, false, std::nullopt, 1.0f, pos_idx, m->rope_freqs);
                k = fast::rope(k, m->head_dim, false, std::nullopt, 1.0f, pos_idx, m->rope_freqs);
            } else {
                q = fast::rope(q, m->head_dim, false, m->rope_theta, 1.0f, pos_idx);
                k = fast::rope(k, m->head_dim, false, m->rope_theta, 1.0f, pos_idx);
            }

            // Update cache (concatenate)
            array new_k = concatenate({k_cache, k}, 2);
            array new_v = concatenate({v_cache, v}, 2);
            new_k_caches.push_back(new_k);
            new_v_caches.push_back(new_v);

            // Attention
            array attn_out = fast::scaled_dot_product_attention(q, new_k, new_v, attn_scale, "");
            attn_out = transpose(attn_out, {0, 2, 1, 3});
            attn_out = reshape(attn_out, {1, 1, m->n_heads * m->head_dim});

            array attn_proj = quantized_matmul(attn_out, l.o_w, l.o_s, l.o_b, true, gs, bits, "affine");

            if (m->is_gemma3) {
                attn_proj = fast::rms_norm(attn_proj, l.ln2_w, m->rms_eps);
            }

            array hidden_1 = hidden + attn_proj;

            // FFN
            array normed_2 = (m->is_gemma3 && l.pre_ffn_norm)
                ? fast::rms_norm(hidden_1, *l.pre_ffn_norm, m->rms_eps)
                : fast::rms_norm(hidden_1, l.ln2_w, m->rms_eps);

            array gate = quantized_matmul(normed_2, l.gate_w, l.gate_s, l.gate_b, true, gs, bits, "affine");
            array up = quantized_matmul(normed_2, l.up_w, l.up_s, l.up_b, true, gs, bits, "affine");
            array mid = (gate * sigmoid(gate)) * up;
            array down = quantized_matmul(mid, l.down_w, l.down_s, l.down_b, true, gs, bits, "affine");

            hidden = hidden_1 + down;
        }

        // Final norm + LM head
        array final_normed = fast::rms_norm(hidden, m->ln_final, m->rms_eps);
        array logits = quantized_matmul(final_normed, m->lm_head_w, m->lm_head_s, m->lm_head_b, true, gs, bits, "affine");

        // Argmax
        array next_token = argmax(logits, -1);
        next_token = reshape(next_token, {1});

        // Build output: [next_token, k_caches..., v_caches...]
        std::vector<array> outputs;
        outputs.push_back(next_token);
        for (auto& k : new_k_caches) outputs.push_back(k);
        for (auto& v : new_v_caches) outputs.push_back(v);

        return outputs;
    };

    // Compile with shapeless=true to handle variable cache sizes
    g_compiled_step = compile(step_fn, /* shapeless= */ true);
    m->is_compiled = true;

    fprintf(stderr, "[MLX] Compiled decode step (group_size=%d, bits=%d, layers=%d)\n", gs, bits, n_layers);
}

// ============================================================================
// C API - Synchronous Decode
// ============================================================================

uint32_t mlx_fused_decode_step(void* model, void* cache_ptr, uint32_t token_id, size_t pos_offset) {
    auto* m = static_cast<FusedModelWeights*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    int32_t token_id_i32 = static_cast<int32_t>(token_id);
    array token = array(&token_id_i32, {1}, int32);

    array next = fused_forward_from_token(m, cache, token, pos_offset);
    eval(next);
    return static_cast<uint32_t>(next.item<int32_t>());
}

// ============================================================================
// C API - Pipelined Decode
// ============================================================================

// Timing accumulators for performance analysis
static thread_local uint64_t g_graph_build_ns = 0;
static thread_local uint64_t g_gpu_eval_ns = 0;
static thread_local int g_timing_count = 0;

void mlx_pipeline_prime(void* model, void* cache_ptr, uint32_t first_token_id, size_t pos_offset) {
    auto* m = static_cast<FusedModelWeights*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    int32_t token_id_i32 = static_cast<int32_t>(first_token_id);
    array first_token = array(&token_id_i32, {1}, int32);

    g_current_token = fused_forward_from_token(m, cache, first_token, pos_offset);
    async_eval(*g_current_token);
}

uint32_t mlx_pipeline_step(void* model, void* cache_ptr, size_t pos_offset) {
    if (!g_current_token) return 0;

    auto* m = static_cast<FusedModelWeights*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    bool debug_timing = (getenv("TOKATAMI_DEBUG_TIMINGS") != nullptr);
    auto t0 = std::chrono::high_resolution_clock::now();

    // Build next graph using current (lazy) token
    array& current = *g_current_token;
    array next = fused_forward_from_token(m, cache, current, pos_offset);

    auto t1 = std::chrono::high_resolution_clock::now();

    // Queue next
    async_eval(next);

    // Materialize current
    eval(current);

    auto t2 = std::chrono::high_resolution_clock::now();

    uint32_t result = static_cast<uint32_t>(*current.data<int32_t>());

    if (debug_timing) {
        g_graph_build_ns += std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count();
        g_gpu_eval_ns += std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        g_timing_count++;

        if (g_timing_count % 50 == 0) {
            double avg_graph_ms = (double)g_graph_build_ns / g_timing_count / 1e6;
            double avg_eval_ms = (double)g_gpu_eval_ns / g_timing_count / 1e6;
            fprintf(stderr, "[TIMING] Avg over %d steps: graph=%.2fms eval=%.2fms total=%.2fms (%.0f t/s)\n",
                    g_timing_count, avg_graph_ms, avg_eval_ms, avg_graph_ms + avg_eval_ms,
                    1000.0 / (avg_graph_ms + avg_eval_ms));
        }
    }

    // Rotate
    g_current_token = next;

    return result;
}

uint32_t mlx_pipeline_flush() {
    if (!g_current_token) return 0;
    uint32_t result = static_cast<uint32_t>(g_current_token->item<int32_t>());
    g_current_token.reset();
    return result;
}

// ============================================================================
// C API - Async Decode (legacy)
// ============================================================================

void* mlx_fused_decode_async_start(void* model, void* cache_ptr, uint32_t token_id, size_t pos_offset) {
    auto* m = static_cast<FusedModelWeights*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    int32_t token_id_i32 = static_cast<int32_t>(token_id);
    array token = array(&token_id_i32, {1}, int32);

    g_pending_token = fused_forward_from_token(m, cache, token, pos_offset);
    async_eval(*g_pending_token);

    return nullptr;
}

uint32_t mlx_fused_decode_async_get() {
    if (!g_pending_token) return 0;
    return static_cast<uint32_t>(g_pending_token->item<int32_t>());
}

// ============================================================================
// C API - Debug Timing
// ============================================================================

void mlx_print_decode_timing() {
    if (g_decode_count > 0) {
        fprintf(stderr, "\nC++ Decode Timing (avg over %d calls):\n", g_decode_count);
        fprintf(stderr, "  Graph build: %.2fms\n", (double)g_total_graph_ns / g_decode_count / 1e6);
        fprintf(stderr, "  GPU eval:    %.2fms\n", (double)g_total_eval_ns / g_decode_count / 1e6);
    }
    g_total_graph_ns = g_total_eval_ns = 0;
    g_decode_count = 0;
}

// ============================================================================
// C API - Compiled Layer (uses MLX compile() for fusion)
// ============================================================================
// These functions compile entire transformer layers for better GPU fusion.

struct CompiledLayer {
    std::function<std::vector<array>(const std::vector<array>&)> fn;
};
static std::vector<CompiledLayer*> g_compiled_layers;

void* mlx_compile_layer(
    const void* q_weight, const void* q_scales, const void* q_biases,
    const void* k_weight, const void* k_scales, const void* k_biases,
    const void* v_weight, const void* v_scales, const void* v_biases,
    const void* o_weight, const void* o_scales, const void* o_biases,
    const void* gate_weight, const void* gate_scales, const void* gate_biases,
    const void* up_weight, const void* up_scales, const void* up_biases,
    const void* down_weight, const void* down_scales, const void* down_biases,
    const void* attn_norm, const void* ffn_norm,
    const void* q_norm, const void* k_norm,
    size_t n_heads, size_t n_kv_heads, size_t head_dim, size_t hidden_dim,
    size_t group_size, size_t bits, float rope_theta, float rms_eps
) {
    // Capture weights by value
    const array w_q = *static_cast<const array*>(q_weight);
    const array s_q = *static_cast<const array*>(q_scales);
    const array b_q = *static_cast<const array*>(q_biases);
    const array w_k = *static_cast<const array*>(k_weight);
    const array s_k = *static_cast<const array*>(k_scales);
    const array b_k = *static_cast<const array*>(k_biases);
    const array w_v = *static_cast<const array*>(v_weight);
    const array s_v = *static_cast<const array*>(v_scales);
    const array b_v = *static_cast<const array*>(v_biases);
    const array w_o = *static_cast<const array*>(o_weight);
    const array s_o = *static_cast<const array*>(o_scales);
    const array b_o = *static_cast<const array*>(o_biases);
    const array w_gate = *static_cast<const array*>(gate_weight);
    const array s_gate = *static_cast<const array*>(gate_scales);
    const array b_gate = *static_cast<const array*>(gate_biases);
    const array w_up = *static_cast<const array*>(up_weight);
    const array s_up = *static_cast<const array*>(up_scales);
    const array b_up = *static_cast<const array*>(up_biases);
    const array w_down = *static_cast<const array*>(down_weight);
    const array s_down = *static_cast<const array*>(down_scales);
    const array b_down = *static_cast<const array*>(down_biases);
    const array norm_attn = *static_cast<const array*>(attn_norm);
    const array norm_ffn = *static_cast<const array*>(ffn_norm);
    const std::optional<array> q_norm_arr = q_norm ? std::optional<array>(*static_cast<const array*>(q_norm)) : std::nullopt;
    const std::optional<array> k_norm_arr = k_norm ? std::optional<array>(*static_cast<const array*>(k_norm)) : std::nullopt;

    auto layer_fn = [=](const std::vector<array>& inputs) -> std::vector<array> {
        const auto& hidden = inputs[0];
        const auto& k_cache_in = inputs[1];
        const auto& v_cache_in = inputs[2];
        int pos_offset = inputs[3].shape(0) - 1;

        int batch = hidden.shape(0);
        int seq_len = hidden.shape(1);
        int gs = static_cast<int>(group_size);
        int b = static_cast<int>(bits);

        auto normed = fast::rms_norm(hidden, norm_attn, rms_eps);

        auto q_proj = quantized_matmul(normed, w_q, s_q, b_q, true, gs, b, "affine");
        auto k_proj = quantized_matmul(normed, w_k, s_k, b_k, true, gs, b, "affine");
        auto v_proj = quantized_matmul(normed, w_v, s_v, b_v, true, gs, b, "affine");

        auto q = reshape(q_proj, {batch, seq_len, static_cast<int>(n_heads), static_cast<int>(head_dim)});
        auto k = reshape(k_proj, {batch, seq_len, static_cast<int>(n_kv_heads), static_cast<int>(head_dim)});
        auto v = reshape(v_proj, {batch, seq_len, static_cast<int>(n_kv_heads), static_cast<int>(head_dim)});

        if (q_norm_arr) q = fast::rms_norm(q, *q_norm_arr, rms_eps);
        if (k_norm_arr) k = fast::rms_norm(k, *k_norm_arr, rms_eps);

        q = transpose(q, {0, 2, 1, 3});
        k = transpose(k, {0, 2, 1, 3});
        v = transpose(v, {0, 2, 1, 3});

        q = fast::rope(q, static_cast<int>(head_dim), false, rope_theta, 1.0f, pos_offset);
        k = fast::rope(k, static_cast<int>(head_dim), false, rope_theta, 1.0f, pos_offset);

        bool is_prefill = (k_cache_in.ndim() == 0 || k_cache_in.size() == 0);
        array k_full = is_prefill ? k : concatenate({k_cache_in, k}, 2);
        array v_full = is_prefill ? v : concatenate({v_cache_in, v}, 2);

        float scale = 1.0f / std::sqrt(static_cast<float>(head_dim));
        auto attn_out = fast::scaled_dot_product_attention(q, k_full, v_full, scale, is_prefill ? "causal" : "");

        attn_out = transpose(attn_out, {0, 2, 1, 3});
        attn_out = reshape(attn_out, {batch, seq_len, static_cast<int>(n_heads * head_dim)});

        auto attn_proj = quantized_matmul(attn_out, w_o, s_o, b_o, true, gs, b, "affine");
        auto hidden_1 = hidden + attn_proj;

        auto normed_2 = fast::rms_norm(hidden_1, norm_ffn, rms_eps);
        auto gate = quantized_matmul(normed_2, w_gate, s_gate, b_gate, true, gs, b, "affine");
        auto up = quantized_matmul(normed_2, w_up, s_up, b_up, true, gs, b, "affine");
        auto ffn_hidden = (gate * sigmoid(gate)) * up;
        auto down = quantized_matmul(ffn_hidden, w_down, s_down, b_down, true, gs, b, "affine");

        auto output = hidden_1 + down;
        return {output, k, v};
    };

    auto* compiled = new CompiledLayer();
    compiled->fn = compile(layer_fn, /* shapeless= */ true);
    g_compiled_layers.push_back(compiled);
    return reinterpret_cast<void*>(g_compiled_layers.size() - 1);
}

void* mlx_layer_forward(
    void* compiled_handle,
    const void* hidden, void* cache_ptr, size_t layer_idx, size_t pos_offset
) {
    size_t compiled_idx = reinterpret_cast<size_t>(compiled_handle);
    auto& compiled_layer = g_compiled_layers[compiled_idx];
    const auto& h = *static_cast<const array*>(hidden);

    auto cache = static_cast<MLXCache*>(cache_ptr);
    auto& layer = cache->layers[layer_idx];

    size_t prev_offset = layer.offset;
    bool is_prefill = (prev_offset == 0);

    array kc = array(0.0f, float32);
    array vc = array(0.0f, float32);

    if (!is_prefill && layer.k_bfloat16) {
        const auto& k_full = *layer.k_bfloat16;
        const auto& v_full = *layer.v_bfloat16;
        Shape start = {0, 0, 0, 0};
        Shape stop = {k_full.shape(0), k_full.shape(1), static_cast<int>(prev_offset), k_full.shape(3)};
        kc = slice(k_full, start, stop);
        vc = slice(v_full, start, stop);
    }

    array pos_arr = zeros({static_cast<int>(pos_offset + 1)}, float32);
    auto results = compiled_layer->fn({h, kc, vc, pos_arr});

    const auto& hidden_out = results[0];
    const auto& k_new = results[1];
    const auto& v_new = results[2];

    const int B = k_new.shape(0);
    const int n_kv = k_new.shape(1);
    const int D = k_new.shape(3);
    const int num_steps = k_new.shape(2);
    const int new_offset = prev_offset + num_steps;

    const bool need_expand = !layer.k_bfloat16 ||
                             (prev_offset + num_steps) > static_cast<size_t>(layer.k_bfloat16->shape(2));

    if (need_expand) {
        const int step = 256;
        const int n_steps = ((prev_offset + num_steps + step - 1) / step) * step;
        Shape new_shape = {B, n_kv, n_steps, D};

        if (layer.k_bfloat16) {
            array new_k = zeros(new_shape, bfloat16);
            array new_v = zeros(new_shape, bfloat16);
            Shape copy_start = {0, 0, 0, 0};
            Shape copy_stop = {B, n_kv, static_cast<int>(prev_offset), D};
            array k_existing = slice(*layer.k_bfloat16, copy_start, copy_stop);
            array v_existing = slice(*layer.v_bfloat16, copy_start, copy_stop);
            new_k = slice_update(new_k, k_existing, copy_start, copy_stop);
            new_v = slice_update(new_v, v_existing, copy_start, copy_stop);
            *layer.k_bfloat16 = new_k;
            *layer.v_bfloat16 = new_v;
        } else {
            layer.k_bfloat16 = new array(zeros(new_shape, bfloat16));
            layer.v_bfloat16 = new array(zeros(new_shape, bfloat16));
        }
    }

    Shape start = {0, 0, static_cast<int>(prev_offset), 0};
    Shape stop = {B, n_kv, static_cast<int>(new_offset), D};
    array k_old = *layer.k_bfloat16;
    array v_old = *layer.v_bfloat16;
    *layer.k_bfloat16 = slice_update(k_old, k_new, start, stop);
    *layer.v_bfloat16 = slice_update(v_old, v_new, start, stop);
    layer.offset = new_offset;

    return pool_array(array(hidden_out));
}

// ============================================================================
// C API - Batch Decode (runs entire generation loop in C++)
// ============================================================================

uint32_t mlx_fused_decode_batch(
    void* model,
    void* cache_ptr,
    uint32_t first_token,
    size_t start_pos,
    uint32_t* out_tokens,
    size_t max_tokens,
    const uint32_t* eos_ids,
    size_t n_eos_ids
) {
    auto* m = static_cast<FusedModelWeights*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    auto is_eos = [&](uint32_t tok) {
        for (size_t i = 0; i < n_eos_ids; i++) {
            if (tok == eos_ids[i]) return true;
        }
        return false;
    };

    uint32_t current_token = first_token;
    size_t pos = start_pos;
    size_t gen_count = 0;

    while (gen_count < max_tokens) {
        int32_t token_id_i32 = static_cast<int32_t>(current_token);
        array token = array(&token_id_i32, {1}, int32);
        array next = fused_forward_from_token(m, cache, token, pos);
        eval(next);
        current_token = static_cast<uint32_t>(next.item<int32_t>());
        out_tokens[gen_count++] = current_token;
        pos++;
        if (is_eos(current_token)) break;
    }

    return gen_count;
}

} // extern "C"
