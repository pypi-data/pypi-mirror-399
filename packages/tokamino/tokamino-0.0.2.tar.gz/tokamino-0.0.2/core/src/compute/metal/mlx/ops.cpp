// MLX Bridge - Basic Lazy Operations
//
// Provides C-callable wrappers for MLX array operations.
// All operations are "lazy" - they build a computation graph without executing.
// Call mlx_eval() to execute the graph.

#include "common.h"

extern "C" {

// ============================================================================
// Arithmetic Operations
// ============================================================================

void* mlx_lazy_add(const void* a, const void* b) {
    return pool_array(*static_cast<const array*>(a) + *static_cast<const array*>(b));
}

void* mlx_lazy_multiply(const void* a, const void* b) {
    return pool_array(*static_cast<const array*>(a) * *static_cast<const array*>(b));
}

void* mlx_lazy_multiply_scalar(const void* a, float scalar) {
    return pool_array(*static_cast<const array*>(a) * scalar);
}

// ============================================================================
// Matrix Operations
// ============================================================================

void* mlx_lazy_matmul(const void* a, const void* b) {
    return pool_array(matmul(
        *static_cast<const array*>(a),
        *static_cast<const array*>(b)
    ));
}

void* mlx_lazy_quantized_matmul(
    const void* input, const void* weights, const void* scales, const void* biases,
    size_t group_size, size_t bits, bool transpose_weights
) {
    return pool_array(quantized_matmul(
        *static_cast<const array*>(input),
        *static_cast<const array*>(weights),
        *static_cast<const array*>(scales),
        *static_cast<const array*>(biases),
        transpose_weights,
        static_cast<int>(group_size),
        static_cast<int>(bits),
        "affine"
    ));
}

// ============================================================================
// Shape Operations
// ============================================================================

void* mlx_lazy_reshape(const void* input, const size_t* shape, size_t ndim) {
    // Optimized paths for common dimensions (avoid heap allocation)
    if (ndim == 2) {
        return pool_array(reshape(*static_cast<const array*>(input),
            {static_cast<int>(shape[0]), static_cast<int>(shape[1])}));
    } else if (ndim == 3) {
        return pool_array(reshape(*static_cast<const array*>(input),
            {static_cast<int>(shape[0]), static_cast<int>(shape[1]),
             static_cast<int>(shape[2])}));
    } else if (ndim == 4) {
        return pool_array(reshape(*static_cast<const array*>(input),
            {static_cast<int>(shape[0]), static_cast<int>(shape[1]),
             static_cast<int>(shape[2]), static_cast<int>(shape[3])}));
    }
    Shape s;
    for (size_t i = 0; i < ndim; i++) s.push_back(static_cast<int>(shape[i]));
    return pool_array(reshape(*static_cast<const array*>(input), s));
}

// Persistent reshape - heap-allocated, survives pool resets
void* mlx_persistent_reshape(const void* input, const size_t* shape, size_t ndim) {
    const auto& arr = *static_cast<const array*>(input);
    if (ndim == 2) {
        return new array(contiguous(reshape(arr,
            {static_cast<int>(shape[0]), static_cast<int>(shape[1])})));
    } else if (ndim == 3) {
        return new array(contiguous(reshape(arr,
            {static_cast<int>(shape[0]), static_cast<int>(shape[1]),
             static_cast<int>(shape[2])})));
    } else if (ndim == 4) {
        return new array(contiguous(reshape(arr,
            {static_cast<int>(shape[0]), static_cast<int>(shape[1]),
             static_cast<int>(shape[2]), static_cast<int>(shape[3])})));
    }
    Shape s;
    for (size_t i = 0; i < ndim; i++) s.push_back(static_cast<int>(shape[i]));
    return new array(contiguous(reshape(arr, s)));
}

void* mlx_lazy_transpose(const void* input, const size_t* axes, size_t ndim) {
    // Optimized paths for common dimensions
    if (ndim == 2) {
        return pool_array(transpose(*static_cast<const array*>(input),
            {static_cast<int>(axes[0]), static_cast<int>(axes[1])}));
    } else if (ndim == 3) {
        return pool_array(transpose(*static_cast<const array*>(input),
            {static_cast<int>(axes[0]), static_cast<int>(axes[1]),
             static_cast<int>(axes[2])}));
    } else if (ndim == 4) {
        return pool_array(transpose(*static_cast<const array*>(input),
            {static_cast<int>(axes[0]), static_cast<int>(axes[1]),
             static_cast<int>(axes[2]), static_cast<int>(axes[3])}));
    }
    std::vector<int> ax;
    for (size_t i = 0; i < ndim; i++) ax.push_back(static_cast<int>(axes[i]));
    return pool_array(transpose(*static_cast<const array*>(input), ax));
}

void* mlx_lazy_concatenate(const void* a, const void* b, size_t axis) {
    return pool_array(concatenate({
        *static_cast<const array*>(a),
        *static_cast<const array*>(b)
    }, static_cast<int>(axis)));
}

void* mlx_lazy_repeat(const void* input, size_t repeats, size_t axis) {
    return pool_array(repeat(
        *static_cast<const array*>(input),
        static_cast<int>(repeats),
        static_cast<int>(axis)
    ));
}

// ============================================================================
// Slicing Operations
// ============================================================================

void* mlx_lazy_slice(const void* input, const int* starts, const int* ends, size_t ndim) {
    const auto& arr = *static_cast<const array*>(input);
    Shape s(starts, starts + ndim);
    Shape e(ends, ends + ndim);
    return pool_array(slice(arr, s, e));
}

// Persistent slice - heap-allocated, survives pool resets
// Use for weight slices that need to persist across forward passes
void* mlx_persistent_slice(const void* input, const int* starts, const int* ends, size_t ndim) {
    const auto& arr = *static_cast<const array*>(input);
    Shape s(starts, starts + ndim);
    Shape e(ends, ends + ndim);
    // Use contiguous() to force a copy - ensures the slice is independent of the source
    return new array(contiguous(slice(arr, s, e)));
}

void* mlx_lazy_slice_last(const void* input) {
    // Extract last position from [B, L, V] -> [V]
    const auto& arr = *static_cast<const array*>(input);
    int seq_len = arr.shape(1);
    int vocab_size = arr.shape(2);
    Shape start = {0, seq_len - 1, 0};
    Shape stop = {1, seq_len, vocab_size};
    auto sliced = slice(arr, start, stop);
    return pool_array(reshape(sliced, {vocab_size}));
}

void* mlx_lazy_slice_update(
    const void* input, const void* update,
    const int* starts, const int* ends, size_t ndim
) {
    const auto& arr = *static_cast<const array*>(input);
    const auto& upd = *static_cast<const array*>(update);
    Shape s(starts, starts + ndim);
    Shape e(ends, ends + ndim);
    return pool_array(slice_update(arr, upd, s, e));
}

// ============================================================================
// Activation Functions
// ============================================================================

void* mlx_lazy_softmax(const void* input, int axis) {
    return pool_array(softmax(*static_cast<const array*>(input), axis));
}

void* mlx_lazy_silu(const void* input) {
    const auto& x = *static_cast<const array*>(input);
    return pool_array(x * sigmoid(x));
}

// ============================================================================
// Reduction Operations
// ============================================================================

void* mlx_lazy_argmax(const void* handle, int axis) {
    const auto& arr = *static_cast<const array*>(handle);
    return pool_array(argmax(arr, axis));
}

// ============================================================================
// Creation Operations
// ============================================================================

void* mlx_lazy_full(const size_t* shape, size_t ndim, float value) {
    Shape s;
    for (size_t i = 0; i < ndim; i++) s.push_back(static_cast<int>(shape[i]));
    return pool_array(full(s, value));
}

void* mlx_lazy_triu(const void* input, int k) {
    return pool_array(triu(*static_cast<const array*>(input), k));
}

// ============================================================================
// Embedding Operations
// ============================================================================

void* mlx_lazy_embedding(const void* weights, const uint32_t* indices, size_t n_indices) {
    array idx_arr(reinterpret_cast<const int32_t*>(indices),
                  {1, static_cast<int>(n_indices)}, int32);
    return pool_array(take(*static_cast<const array*>(weights), idx_arr, 0));
}

void* mlx_lazy_embedding_from_array(const void* weights, const void* indices_handle) {
    const auto& indices = *static_cast<const array*>(indices_handle);
    auto idx_arr = astype(reshape(indices, {1, -1}), int32);
    return pool_array(take(*static_cast<const array*>(weights), idx_arr, 0));
}

// ============================================================================
// Quantization Operations
// ============================================================================

void* mlx_lazy_dequantize(
    const void* weights, const void* scales, const void* biases,
    size_t group_size, size_t bits
) {
    return pool_array(dequantize(
        *static_cast<const array*>(weights),
        *static_cast<const array*>(scales),
        *static_cast<const array*>(biases),
        static_cast<int>(group_size),
        static_cast<int>(bits),
        "affine"
    ));
}

// ============================================================================
// Compound Operations (fused for convenience)
// ============================================================================

void* mlx_lazy_reshape_transpose(
    const void* input,
    const size_t* reshape_dims, size_t reshape_ndim,
    const size_t* transpose_axes, size_t transpose_ndim
) {
    Shape rs;
    for (size_t i = 0; i < reshape_ndim; i++)
        rs.push_back(static_cast<int>(reshape_dims[i]));
    std::vector<int> ax;
    for (size_t i = 0; i < transpose_ndim; i++)
        ax.push_back(static_cast<int>(transpose_axes[i]));
    auto reshaped = reshape(*static_cast<const array*>(input), rs);
    return pool_array(transpose(reshaped, ax));
}

void* mlx_lazy_transpose_reshape(
    const void* input,
    const size_t* transpose_axes, size_t transpose_ndim,
    const size_t* reshape_dims, size_t reshape_ndim
) {
    std::vector<int> ax;
    for (size_t i = 0; i < transpose_ndim; i++)
        ax.push_back(static_cast<int>(transpose_axes[i]));
    Shape rs;
    for (size_t i = 0; i < reshape_ndim; i++)
        rs.push_back(static_cast<int>(reshape_dims[i]));
    auto transposed = transpose(*static_cast<const array*>(input), ax);
    return pool_array(reshape(transposed, rs));
}

} // extern "C"
