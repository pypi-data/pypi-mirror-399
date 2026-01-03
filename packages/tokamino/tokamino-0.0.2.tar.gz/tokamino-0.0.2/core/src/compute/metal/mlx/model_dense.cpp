// MLX Bridge - Dense (BFloat16) Model
//
// Full transformer implementation using BFloat16 weights.
// Optimizations:
//   - Pre-concatenated QKV and gate_up weights (single matmul instead of 3/2)
//   - Pre-transposed weights (avoid per-call transpose)
//   - Pipelined decode (async_eval overlaps with graph building)

#include "common.h"

// ============================================================================
// Dense Model Structure
// ============================================================================

struct FusedDenseModel {
    struct Layer {
        array ln1_w = array(0.0f, float32);      // attention norm
        array qkv_proj = array(0.0f, bfloat16);  // Pre-concatenated Q+K+V
        array o_proj = array(0.0f, bfloat16);
        array ln2_w = array(0.0f, float32);      // ffn norm
        array gate_up_proj = array(0.0f, bfloat16);  // Pre-concatenated gate+up
        array down_proj = array(0.0f, bfloat16);
        std::optional<array> q_norm;
        std::optional<array> k_norm;
        int q_size = 0;    // For splitting QKV result
        int kv_size = 0;
    };
    std::vector<Layer> layers;

    array ln_final = array(0.0f, float32);
    array lm_head = array(0.0f, bfloat16);  // Pre-transposed
    array embed_tokens = array(0.0f, bfloat16);

    int n_heads = 0;
    int n_kv_heads = 0;
    int head_dim = 0;
    int hidden_dim = 0;
    float rope_theta = 0.0f;
    float rms_eps = 0.0f;
};

// Global model pointer (for pipeline access)
static FusedDenseModel* g_fused_dense = nullptr;

// Pipeline state
static thread_local array* g_dense_current_token = nullptr;
static thread_local size_t g_dense_step_count = 0;

// Pre-computed shapes (avoid allocation per call)
static thread_local Shape g_dense_q_shape, g_dense_kv_shape, g_dense_attn_out_shape;
static thread_local Shape g_dense_token_shape = {1, 1};
static thread_local float g_dense_attn_scale = 0.0f;
static thread_local int g_dense_n_kv_heads = 0;
static thread_local int g_dense_head_dim = 0;

// ============================================================================
// Forward Pass Implementation
// ============================================================================

static array dense_forward_from_token(
    FusedDenseModel* m,
    MLXCache* cache,
    const array& token_idx,
    size_t pos_offset
) {
    const int n_layers = static_cast<int>(m->layers.size());

    // Lazy init cached shapes
    if (g_dense_attn_scale == 0.0f) {
        g_dense_attn_scale = 1.0f / std::sqrt(static_cast<float>(m->head_dim));
        g_dense_q_shape = {1, 1, m->n_heads, m->head_dim};
        g_dense_kv_shape = {1, 1, m->n_kv_heads, m->head_dim};
        g_dense_attn_out_shape = {1, 1, m->n_heads * m->head_dim};
        g_dense_n_kv_heads = m->n_kv_heads;
        g_dense_head_dim = m->head_dim;
    }

    // Embedding lookup
    array hidden = take(m->embed_tokens, reshape(token_idx, g_dense_token_shape), 0);

    for (int layer_idx = 0; layer_idx < n_layers; layer_idx++) {
        const auto& l = m->layers[layer_idx];
        auto& cl = cache->layers[layer_idx];

        // RMS norm
        array normed = fast::rms_norm(hidden, l.ln1_w, m->rms_eps);

        // Single matmul for Q+K+V (weights pre-concatenated)
        array qkv = matmul(normed, l.qkv_proj);
        auto qkv_parts = split(qkv, {l.q_size, l.q_size + l.kv_size}, -1);
        array q = reshape(qkv_parts[0], g_dense_q_shape);
        array k = reshape(qkv_parts[1], g_dense_kv_shape);
        array v = reshape(qkv_parts[2], g_dense_kv_shape);

        if (l.q_norm) q = fast::rms_norm(q, *l.q_norm, m->rms_eps);
        if (l.k_norm) k = fast::rms_norm(k, *l.k_norm, m->rms_eps);

        q = transpose(q, g_transpose_perm);
        k = transpose(k, g_transpose_perm);
        v = transpose(v, g_transpose_perm);

        q = fast::rope(q, m->head_dim, false, m->rope_theta, 1.0f, static_cast<int>(pos_offset));
        k = fast::rope(k, m->head_dim, false, m->rope_theta, 1.0f, static_cast<int>(pos_offset));

        // Cache update
        size_t prev = cl.offset;
        int offset = static_cast<int>(prev + 1);

        if (cl.k_bfloat16 == nullptr || offset > cl.k_bfloat16->shape(2)) {
            int new_size = ((offset + cl.step - 1) / cl.step) * cl.step;
            Shape shape = {1, g_dense_n_kv_heads, new_size, g_dense_head_dim};
            if (cl.k_bfloat16) {
                array new_k = zeros(shape, bfloat16);
                array new_v = zeros(shape, bfloat16);
                Shape stop = {1, g_dense_n_kv_heads, static_cast<int>(prev), g_dense_head_dim};
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
        Shape update_stop = {1, g_dense_n_kv_heads, offset, g_dense_head_dim};
        *cl.k_bfloat16 = slice_update(*cl.k_bfloat16, k, update_start, update_stop);
        *cl.v_bfloat16 = slice_update(*cl.v_bfloat16, v, update_start, update_stop);
        cl.offset = offset;

        const Shape slice_stop = {1, g_dense_n_kv_heads, offset, g_dense_head_dim};
        array k_full = slice(*cl.k_bfloat16, g_slice_start, slice_stop);
        array v_full = slice(*cl.v_bfloat16, g_slice_start, slice_stop);

        array attn_out = fast::scaled_dot_product_attention(q, k_full, v_full, g_dense_attn_scale, "");

        attn_out = transpose(attn_out, g_transpose_perm);
        attn_out = reshape(attn_out, g_dense_attn_out_shape);

        array attn_proj = matmul(attn_out, l.o_proj);
        array hidden_1 = hidden + attn_proj;

        // FFN - single matmul for gate+up (weights pre-concatenated)
        array normed_2 = fast::rms_norm(hidden_1, l.ln2_w, m->rms_eps);
        array gate_up = matmul(normed_2, l.gate_up_proj);
        auto parts = split(gate_up, 2, -1);
        array& gate = parts[0];
        array& up = parts[1];
        array down = matmul(gate * sigmoid(gate) * up, l.down_proj);

        hidden = hidden_1 + down;
    }

    // Final norm + LM head + argmax
    array final_normed = fast::rms_norm(hidden, m->ln_final, m->rms_eps);
    array logits = matmul(final_normed, m->lm_head);
    return reshape(argmax(logits, -1), {});
}

// ============================================================================
// C API - Model Lifecycle
// ============================================================================

extern "C" {

void* mlx_dense_model_create(
    size_t n_layers,
    size_t n_heads, size_t n_kv_heads, size_t head_dim, size_t hidden_dim,
    float rope_theta, float rms_eps
) {
    auto* m = new FusedDenseModel();
    m->layers.resize(n_layers);
    m->n_heads = static_cast<int>(n_heads);
    m->n_kv_heads = static_cast<int>(n_kv_heads);
    m->head_dim = static_cast<int>(head_dim);
    m->hidden_dim = static_cast<int>(hidden_dim);
    m->rope_theta = rope_theta;
    m->rms_eps = rms_eps;
    g_fused_dense = m;
    return m;
}

void mlx_dense_model_set_embeddings(void* model, const void* embed) {
    auto* m = static_cast<FusedDenseModel*>(model);
    m->embed_tokens = *static_cast<const array*>(embed);
}

void mlx_dense_model_set_final(void* model, const void* ln_w, const void* lm_head) {
    auto* m = static_cast<FusedDenseModel*>(model);
    m->ln_final = *static_cast<const array*>(ln_w);
    // Pre-transpose lm_head for optimal memory access
    m->lm_head = transpose(*static_cast<const array*>(lm_head));
    eval(m->lm_head);
}

void mlx_dense_model_set_layer(
    void* model, size_t layer_idx,
    const void* ln1_w,
    const void* q_proj, const void* k_proj, const void* v_proj, const void* o_proj,
    const void* ln2_w,
    const void* gate_proj, const void* up_proj, const void* down_proj,
    const void* q_norm, const void* k_norm
) {
    auto* m = static_cast<FusedDenseModel*>(model);
    auto& l = m->layers[layer_idx];

    l.ln1_w = *static_cast<const array*>(ln1_w);

    // Pre-transpose all weights: [out, in] -> [in, out]
    auto q_t = transpose(*static_cast<const array*>(q_proj));
    auto k_t = transpose(*static_cast<const array*>(k_proj));
    auto v_t = transpose(*static_cast<const array*>(v_proj));
    l.o_proj = transpose(*static_cast<const array*>(o_proj));

    // Pre-concatenate QKV for single matmul
    l.qkv_proj = concatenate({q_t, k_t, v_t}, 1);
    l.q_size = q_t.shape(1);
    l.kv_size = k_t.shape(1);

    l.ln2_w = *static_cast<const array*>(ln2_w);

    auto gate_t = transpose(*static_cast<const array*>(gate_proj));
    auto up_t = transpose(*static_cast<const array*>(up_proj));
    l.down_proj = transpose(*static_cast<const array*>(down_proj));

    // Pre-concatenate gate+up for single matmul
    l.gate_up_proj = concatenate({gate_t, up_t}, 1);

    if (q_norm) l.q_norm = *static_cast<const array*>(q_norm);
    if (k_norm) l.k_norm = *static_cast<const array*>(k_norm);

    // Evaluate all to materialize
    std::vector<array> to_eval = {l.qkv_proj, l.o_proj, l.gate_up_proj, l.down_proj};
    eval(to_eval);
}

void mlx_dense_model_free(void* model) {
    delete static_cast<FusedDenseModel*>(model);
    if (g_fused_dense == model) g_fused_dense = nullptr;
}

// ============================================================================
// C API - Pipelined Decode
// ============================================================================
// Implements async pipelining: while GPU runs token N, CPU builds graph for N+1

void mlx_dense_pipeline_prime(void* model, void* cache_ptr, uint32_t first_token_id, size_t pos_offset) {
    auto* m = static_cast<FusedDenseModel*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    int32_t token_id_i32 = static_cast<int32_t>(first_token_id);
    array first_token = array(&token_id_i32, {1}, int32);

    array result = dense_forward_from_token(m, cache, first_token, pos_offset);
    if (!g_dense_current_token) {
        g_dense_current_token = new array(std::move(result));
    } else {
        *g_dense_current_token = std::move(result);
    }
    async_eval(*g_dense_current_token);
}

uint32_t mlx_dense_pipeline_step(void* model, void* cache_ptr, size_t pos_offset) {
    if (!g_dense_current_token) return 0;

    auto* m = static_cast<FusedDenseModel*>(model);
    auto* cache = static_cast<MLXCache*>(cache_ptr);

    // Build graph for NEXT token using current (lazy) token
    array& current = *g_dense_current_token;
    array next = dense_forward_from_token(m, cache, current, pos_offset);

    // Queue next token computation
    async_eval(next);

    // NOW materialize current token
    eval(current);
    uint32_t result = static_cast<uint32_t>(*current.data<int32_t>());

    // Rotate buffers
    *g_dense_current_token = std::move(next);

    // Clear memory cache periodically (like Python mlx-lm)
    if (++g_dense_step_count % 256 == 0) {
        clear_cache();
    }

    return result;
}

uint32_t mlx_dense_pipeline_flush() {
    if (!g_dense_current_token) return 0;
    eval(*g_dense_current_token);
    uint32_t result = static_cast<uint32_t>(*g_dense_current_token->data<int32_t>());
    return result;
}

} // extern "C"
