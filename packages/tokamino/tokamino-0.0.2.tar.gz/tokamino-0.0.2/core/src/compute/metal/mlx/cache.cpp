// MLX Bridge - KV Cache Management
//
// Implements KV cache for transformer inference, matching Python mlx-lm behavior.
// Uses pre-allocated buffers with slice_update for efficiency.

#include "common.h"

extern "C" {

// ============================================================================
// Cache Lifecycle
// ============================================================================

void* mlx_cache_create(size_t n_layers) {
    auto cache = new MLXCache();
    cache->layers.resize(n_layers);
    return cache;
}

void* mlx_cache_create_bfloat16(size_t n_layers) {
    // Same as mlx_cache_create - cache type determined by usage
    return mlx_cache_create(n_layers);
}

void mlx_cache_free(void* cache_ptr) {
    auto cache = static_cast<MLXCache*>(cache_ptr);
    for (auto& layer : cache->layers) {
        delete layer.k_bfloat16;
        delete layer.v_bfloat16;
        delete layer.k_view;
        delete layer.v_view;
    }
    delete cache;
}

// ============================================================================
// BFloat16 Cache Operations
// ============================================================================
// Matches Python's mlx_lm KVCache pattern:
//   1. Pre-allocate 256-token buffers
//   2. Use slice_update for in-place writes
//   3. Return slice [0:offset]

void mlx_cache_update_and_fetch_bfloat16(
    void* cache_ptr, size_t layer_idx,
    const void* k_new, const void* v_new,
    void** k_out, void** v_out, bool* is_prefill_out
) {
    auto cache = static_cast<MLXCache*>(cache_ptr);
    auto& layer = cache->layers[layer_idx];

    const auto& k_new_arr = *static_cast<const array*>(k_new);
    const auto& v_new_arr = *static_cast<const array*>(v_new);

    int B = k_new_arr.shape(0);
    int n_kv_heads = k_new_arr.shape(1);
    int num_steps = k_new_arr.shape(2);
    int k_head_dim = k_new_arr.shape(3);
    int v_head_dim = v_new_arr.shape(3);

    size_t prev = layer.offset;
    *is_prefill_out = (prev == 0);

    // Expand buffer if needed
    if (layer.k_bfloat16 == nullptr ||
        (prev + num_steps) > static_cast<size_t>(layer.k_bfloat16->shape(2))) {

        int n_steps = (layer.step + num_steps - 1) / layer.step;
        Shape k_shape = {B, n_kv_heads, n_steps * layer.step, k_head_dim};
        Shape v_shape = {B, n_kv_heads, n_steps * layer.step, v_head_dim};
        auto new_k = zeros(k_shape, k_new_arr.dtype());
        auto new_v = zeros(v_shape, v_new_arr.dtype());

        if (layer.k_bfloat16 != nullptr) {
            // Trim if not aligned to step boundary
            if (prev % layer.step != 0) {
                Shape start = {0, 0, 0, 0};
                Shape stop_k = {B, n_kv_heads, static_cast<int>(prev), k_head_dim};
                Shape stop_v = {B, n_kv_heads, static_cast<int>(prev), v_head_dim};
                *layer.k_bfloat16 = slice(*layer.k_bfloat16, start, stop_k);
                *layer.v_bfloat16 = slice(*layer.v_bfloat16, start, stop_v);
            }
            *layer.k_bfloat16 = concatenate({*layer.k_bfloat16, new_k}, 2);
            *layer.v_bfloat16 = concatenate({*layer.v_bfloat16, new_v}, 2);
        } else {
            layer.k_bfloat16 = new array(new_k);
            layer.v_bfloat16 = new array(new_v);
        }
    }

    // Slice update: cache[..., prev:offset, :] = new_data
    size_t offset = prev + num_steps;
    Shape start = {0, 0, static_cast<int>(prev), 0};
    Shape stop_k = {B, n_kv_heads, static_cast<int>(offset), k_head_dim};
    Shape stop_v = {B, n_kv_heads, static_cast<int>(offset), v_head_dim};
    *layer.k_bfloat16 = slice_update(*layer.k_bfloat16, k_new_arr, start, stop_k);
    *layer.v_bfloat16 = slice_update(*layer.v_bfloat16, v_new_arr, start, stop_v);

    layer.offset = offset;

    // Return slice [0:offset]
    Shape view_start = {0, 0, 0, 0};
    Shape view_stop_k = {B, n_kv_heads, static_cast<int>(offset), k_head_dim};
    Shape view_stop_v = {B, n_kv_heads, static_cast<int>(offset), v_head_dim};

    // Reuse view arrays to avoid allocation
    if (layer.k_view == nullptr) {
        layer.k_view = new array(slice(*layer.k_bfloat16, view_start, view_stop_k));
        layer.v_view = new array(slice(*layer.v_bfloat16, view_start, view_stop_v));
    } else {
        *layer.k_view = slice(*layer.k_bfloat16, view_start, view_stop_k);
        *layer.v_view = slice(*layer.v_bfloat16, view_start, view_stop_v);
    }

    *k_out = layer.k_view;
    *v_out = layer.v_view;
}

void mlx_cache_get_bfloat16(
    void* cache_ptr, size_t layer_idx,
    void** k_out, void** v_out
) {
    auto cache = static_cast<MLXCache*>(cache_ptr);
    auto& layer = cache->layers[layer_idx];
    *k_out = layer.k_bfloat16;
    *v_out = layer.v_bfloat16;
}

void mlx_cache_set_full_bfloat16(
    void* cache_ptr, size_t layer_idx,
    const void* k_full, const void* v_full
) {
    auto cache = static_cast<MLXCache*>(cache_ptr);
    auto& layer = cache->layers[layer_idx];

    const auto& k_arr = *static_cast<const array*>(k_full);
    const auto& v_arr = *static_cast<const array*>(v_full);

    if (layer.k_bfloat16 == nullptr) {
        layer.k_bfloat16 = new array(k_arr);
        layer.v_bfloat16 = new array(v_arr);
    } else {
        *layer.k_bfloat16 = k_arr;
        *layer.v_bfloat16 = v_arr;
    }

    layer.offset = k_arr.shape(2);
}

void mlx_cache_eval_all(void* cache_ptr, size_t n_layers) {
    auto cache = static_cast<MLXCache*>(cache_ptr);
    std::vector<array> to_eval;

    for (size_t i = 0; i < n_layers; i++) {
        if (cache->layers[i].k_bfloat16) {
            to_eval.push_back(*cache->layers[i].k_bfloat16);
            to_eval.push_back(*cache->layers[i].v_bfloat16);
        }
    }

    if (!to_eval.empty()) {
        eval(to_eval);
    }
}

} // extern "C"
