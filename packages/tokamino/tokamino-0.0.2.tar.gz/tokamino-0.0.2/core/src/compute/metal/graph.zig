/// Zig bindings for MLX lazy graph API
/// Keeps arrays on GPU using opaque handles, builds lazy computation graphs
/// Follows pattern from test_mlx_single.py for 243 t/s decode performance
const std = @import("std");

// ============================================================================
// Opaque handles - arrays stay on GPU!
// ============================================================================

/// Opaque handle to MLX array (GPU memory)
pub const ArrayHandle = ?*anyopaque;

/// Opaque handle to KV cache
pub const CacheHandle = ?*anyopaque;

// ============================================================================
// Array Pool - call reset() before each forward pass to reuse allocations
// ============================================================================

/// Reset array pool for next forward pass (eliminates heap allocations)
pub extern fn mlx_pool_reset() void;

/// Clear MLX memory cache - call periodically to prevent fragmentation
pub extern fn mlx_clear_memory_cache() void;

/// Get pool stats (for debugging)
pub extern fn mlx_pool_stats(pool_size: *usize, used: *usize) void;

/// Start counting operations (for debugging)
pub extern fn mlx_start_counting() void;

/// Stop counting and return op count
pub extern fn mlx_stop_counting() usize;

// ============================================================================
// Array Creation (CPU -> GPU)
// ============================================================================

//// Create MLX array from float32 data (accepts unaligned pointers)
/// C++ signature: void* mlx_array_from_float32(const void* data, ...)
pub extern fn mlx_array_from_float32(
    data: *const anyopaque,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Create MLX array from uint32 data (accepts unaligned pointers from mmap)
/// C++ signature: void* mlx_array_from_uint32(const void* data, ...)
pub extern fn mlx_array_from_uint32(
    data: *const anyopaque,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Create MLX array from bfloat16 data (stored as u16)
/// C++ signature: void* mlx_array_from_bfloat16(const void* data, ...)
pub extern fn mlx_array_from_bfloat16(
    data: *const anyopaque,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Create MLX array from float16 (IEEE) data (stored as u16)
/// C++ signature: void* mlx_array_from_float16(const void* data, ...)
pub extern fn mlx_array_from_float16(
    data: *const anyopaque,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Create MLX array from uint8 data (used for MXFP4 scales)
pub extern fn mlx_array_from_uint8(
    data: [*]align(1) const u8,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Create MLX array from existing pointer (no-copy wrapper)
pub extern fn mlx_array_from_ptr(mlx_array_ptr: *anyopaque) ArrayHandle;

/// Free array handle
pub extern fn mlx_array_free(handle: ArrayHandle) void;

// ============================================================================
// Lazy Operations (return handles, don't execute!)
// ============================================================================

/// Quantized matmul - >>> Lazy: quantized_matmul
pub extern fn mlx_lazy_quantized_matmul(
    input: ArrayHandle,
    weights: ArrayHandle,
    scales: ArrayHandle,
    biases: ArrayHandle,
    group_size: usize,
    bits: usize,
    transpose: bool,
) ArrayHandle;

/// RMS norm - >>> Lazy: rms_norm
pub extern fn mlx_lazy_rms_norm(
    input: ArrayHandle,
    weight: ArrayHandle,
    eps: f32,
) ArrayHandle;

/// Add 1 to array (for Gemma3 RMSNorm: weight becomes 1 + weight)
pub extern fn mlx_add_one(arr: ArrayHandle) ArrayHandle;

/// Scale array by sqrt(d_model) for Gemma3 embedding scaling
pub extern fn mlx_scale_by_sqrt(arr: ArrayHandle, d_model: usize) ArrayHandle;

/// RoPE - >>> Lazy: rope
pub extern fn mlx_lazy_rope(
    input: ArrayHandle,
    head_dim: usize,
    offset: usize,
    rope_base: f32,
) ArrayHandle;

/// Scaled dot product attention - >>> Lazy: scaled_dot_product_attention
pub extern fn mlx_lazy_attention(
    q: ArrayHandle,
    k: ArrayHandle,
    v: ArrayHandle,
    scale: f32,
    causal: bool,
) ArrayHandle;

/// Fused quantized attention - >>> Lazy: Q @ K^T, scale, mask, softmax, @ V
/// All K/V inputs are quantized triplets (weights, scales, biases)
pub extern fn mlx_lazy_quantized_attention(
    q: ArrayHandle,
    k_weights: ArrayHandle,
    k_scales: ArrayHandle,
    k_biases: ArrayHandle,
    v_weights: ArrayHandle,
    v_scales: ArrayHandle,
    v_biases: ArrayHandle,
    mask: ArrayHandle, // null for decode, causal_mask for prefill
    scale: f32,
    group_size: usize,
    bits: usize,
) ArrayHandle;

/// SiLU activation - >>> Lazy: silu
pub extern fn mlx_lazy_silu(input: ArrayHandle) ArrayHandle;

/// Fused attention: Q/K/V proj -> reshape -> transpose -> QK norm -> RoPE -> cache -> attention -> output proj
/// Reduces ~15 FFI calls to 1 for the entire attention block
pub extern fn mlx_lazy_fused_attention(
    input: ArrayHandle,
    q_w: ArrayHandle,
    q_s: ArrayHandle,
    q_b: ArrayHandle,
    k_w: ArrayHandle,
    k_s: ArrayHandle,
    k_b: ArrayHandle,
    v_w: ArrayHandle,
    v_s: ArrayHandle,
    v_b: ArrayHandle,
    o_w: ArrayHandle,
    o_s: ArrayHandle,
    o_b: ArrayHandle,
    q_norm_w: ArrayHandle, // can be null
    k_norm_w: ArrayHandle, // can be null
    // Linear biases (optional, can be null) - for gpt-oss
    q_bias: ArrayHandle,
    k_bias: ArrayHandle,
    v_bias: ArrayHandle,
    o_bias: ArrayHandle,
    // Attention sinks (optional, can be null) - for gpt-oss
    attn_sinks: ArrayHandle,
    cache_ptr: CacheHandle,
    layer_idx: usize,
    n_heads: usize,
    n_kv_heads: usize,
    head_dim: usize,
    pos_offset: usize,
    rope_theta: f32,
    rms_eps: f32,
    group_size: usize,
    bits: usize,
    query_pre_attn_scalar: f32, // 0 for default (head_dim), >0 for custom (e.g., 256 for Gemma3)
    attention_multiplier: f32, // 0 for default, >0 uses this directly as scale (for Granite)
) ArrayHandle;

/// Fused FFN: gate_proj -> SiLU -> * up_proj -> down_proj
/// Reduces 5 FFI calls to 1 for better performance
pub extern fn mlx_lazy_fused_ffn(
    input: ArrayHandle,
    gate_w: ArrayHandle,
    gate_s: ArrayHandle,
    gate_b: ArrayHandle,
    up_w: ArrayHandle,
    up_s: ArrayHandle,
    up_b: ArrayHandle,
    down_w: ArrayHandle,
    down_s: ArrayHandle,
    down_b: ArrayHandle,
    group_size: usize,
    bits: usize,
    use_gelu: bool, // true for Gemma3, false for other models
) ArrayHandle;

/// Fused BF16 attention (non-quantized): Q/K/V proj -> reshape -> transpose -> QK norm -> RoPE -> cache -> attention -> output proj
/// Uses regular matmul instead of quantized_matmul
pub extern fn mlx_lazy_fused_attention_bf16(
    input: ArrayHandle,
    q_w: ArrayHandle,
    k_w: ArrayHandle,
    v_w: ArrayHandle,
    o_w: ArrayHandle,
    q_norm_w: ArrayHandle, // can be null
    k_norm_w: ArrayHandle, // can be null
    // Linear biases (optional, can be null) - for gpt-oss
    q_bias: ArrayHandle,
    k_bias: ArrayHandle,
    v_bias: ArrayHandle,
    o_bias: ArrayHandle,
    // Attention sinks (optional, can be null) - for gpt-oss
    attn_sinks: ArrayHandle,
    cache_ptr: CacheHandle,
    layer_idx: usize,
    n_heads: usize,
    n_kv_heads: usize,
    head_dim: usize,
    pos_offset: usize,
    rope_theta: f32,
    rms_eps: f32,
    query_pre_attn_scalar: f32, // 0 for default (head_dim), >0 for custom (e.g., 256 for Gemma3)
    attention_multiplier: f32, // 0 for default, >0 uses this directly as scale (for Granite)
) ArrayHandle;

/// Fused BF16 FFN (non-quantized): gate_proj -> SiLU -> * up_proj -> down_proj
/// Uses regular matmul instead of quantized_matmul
pub extern fn mlx_lazy_fused_ffn_bf16(
    input: ArrayHandle,
    gate_w: ArrayHandle,
    up_w: ArrayHandle,
    down_w: ArrayHandle,
) ArrayHandle;

/// Fused MoE FFN (MXFP4 quantized experts): router -> topk -> gather_qmm -> weighted sum
/// For gpt-oss model with 32 experts per layer, 4 active per token
/// Uses separate gate/up/down projections (not fused)
pub extern fn mlx_lazy_fused_moe_ffn_mxfp4(
    input: ArrayHandle,
    // Router weights (8-bit affine)
    router_w: ArrayHandle,
    router_s: ArrayHandle,
    router_b: ArrayHandle,
    router_bias: ArrayHandle, // can be null
    // Expert weights (MXFP4) - separate gate/up/down
    gate_w: ArrayHandle, // [num_experts, d_ff, packed_dim]
    gate_s: ArrayHandle, // scales
    up_w: ArrayHandle,
    up_s: ArrayHandle,
    down_w: ArrayHandle,
    down_s: ArrayHandle,
    // Expert biases (optional)
    gate_bias: ArrayHandle, // can be null
    up_bias: ArrayHandle, // can be null
    down_bias: ArrayHandle, // can be null
    // Config
    num_experts: usize,
    experts_per_token: usize,
    router_group_size: usize,
    expert_group_size: usize,
) ArrayHandle;

/// Dequantize - >>> Lazy: dequantize
pub extern fn mlx_lazy_dequantize(
    weights: ArrayHandle,
    scales: ArrayHandle,
    biases: ArrayHandle,
    group_size: usize,
    bits: usize,
) ArrayHandle;

/// Element-wise add - >>> Lazy
pub extern fn mlx_lazy_add(a: ArrayHandle, b: ArrayHandle) ArrayHandle;

/// Element-wise multiply - >>> Lazy
pub extern fn mlx_lazy_multiply(a: ArrayHandle, b: ArrayHandle) ArrayHandle;

/// Multiply by scalar - >>> Lazy
pub extern fn mlx_lazy_multiply_scalar(a: ArrayHandle, scalar: f32) ArrayHandle;

/// Softmax along axis - >>> Lazy
pub extern fn mlx_lazy_softmax(input: ArrayHandle, axis: c_int) ArrayHandle;

/// Create array filled with scalar value - >>> Lazy
pub extern fn mlx_lazy_full(
    shape: [*]const usize,
    ndim: usize,
    value: f32,
) ArrayHandle;

/// Upper triangular matrix - >>> Lazy
pub extern fn mlx_lazy_triu(input: ArrayHandle, k: c_int) ArrayHandle;

/// Matrix multiply - >>> Lazy
pub extern fn mlx_lazy_matmul(a: ArrayHandle, b: ArrayHandle) ArrayHandle;

/// Reshape - >>> Lazy
pub extern fn mlx_lazy_reshape(
    input: ArrayHandle,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Persistent reshape - heap-allocated, survives pool resets
pub extern fn mlx_persistent_reshape(
    input: ArrayHandle,
    shape: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Transpose - >>> Lazy
pub extern fn mlx_lazy_transpose(
    input: ArrayHandle,
    axes: [*]const usize,
    ndim: usize,
) ArrayHandle;

/// Combined reshape + transpose for better fusion - >>> Lazy
pub extern fn mlx_lazy_reshape_transpose(
    input: ArrayHandle,
    reshape_dims: [*]const usize,
    reshape_ndim: usize,
    transpose_axes: [*]const usize,
    transpose_ndim: usize,
) ArrayHandle;

/// Combined transpose + reshape for better fusion - >>> Lazy
pub extern fn mlx_lazy_transpose_reshape(
    input: ArrayHandle,
    transpose_axes: [*]const usize,
    transpose_ndim: usize,
    reshape_dims: [*]const usize,
    reshape_ndim: usize,
) ArrayHandle;

/// Embedding lookup - >>> Lazy
pub extern fn mlx_lazy_embedding(
    weights: ArrayHandle,
    indices: [*]const u32,
    n_indices: usize,
) ArrayHandle;

/// Embedding lookup from GPU array (lazy - for pipelined generation)
pub extern fn mlx_lazy_embedding_from_array(
    weights: ArrayHandle,
    indices: ArrayHandle,
) ArrayHandle;

/// Concatenate - >>> Lazy: concatenate arrays along axis
pub extern fn mlx_lazy_concatenate(
    a: ArrayHandle,
    b: ArrayHandle,
    axis: usize,
) ArrayHandle;

/// Repeat - >>> Lazy: repeat array along axis (for GQA)
pub extern fn mlx_lazy_repeat(
    input: ArrayHandle,
    repeats: usize,
    axis: usize,
) ArrayHandle;

/// Slice - >>> Lazy: extract slice from array
pub extern fn mlx_lazy_slice(
    input: ArrayHandle,
    starts: [*]const c_int,
    ends: [*]const c_int,
    ndim: usize,
) ArrayHandle;

/// Persistent slice - heap-allocated, survives pool resets
/// Use for weight slices that need to persist across forward passes
pub extern fn mlx_persistent_slice(
    input: ArrayHandle,
    starts: [*]const c_int,
    ends: [*]const c_int,
    ndim: usize,
) ArrayHandle;

/// Slice update - >>> Lazy: update slice of array
pub extern fn mlx_lazy_slice_update(
    input: ArrayHandle,
    update: ArrayHandle,
    starts: [*]const c_int,
    ends: [*]const c_int,
    ndim: usize,
) ArrayHandle;

// ============================================================================
// Graph Execution
// ============================================================================

/// Force evaluation - >>> C++ call: mx.eval()
/// THIS IS THE KEY: executes entire graph on GPU!
pub extern fn mlx_eval(handles: [*]ArrayHandle, n_handles: usize) void;

/// Async evaluation - >>> C++ call: mx.async_eval()
/// Starts GPU work in background, returns immediately.
/// Use for pipelining: start next token's eval while processing current token.
pub extern fn mlx_async_eval(handles: [*]ArrayHandle, n_handles: usize) void;

// ============================================================================
// Data Retrieval (GPU -> CPU, only when needed)
// ============================================================================

/// Copy data from GPU to CPU - >>> C++ call: np.array()
pub extern fn mlx_array_to_float32(
    handle: ArrayHandle,
    out: [*]f32,
    size: usize,
) void;

/// GPU-side argmax - returns array handle with token index
/// Use to avoid CPU roundtrip during sampling
pub extern fn mlx_lazy_argmax(handle: ArrayHandle, axis: c_int) ArrayHandle;

/// Get scalar u32 value from array (blocks until evaluated)
pub extern fn mlx_array_item_u32(handle: ArrayHandle) u32;

/// Extract last position from 3D logits tensor [B, L, V] -> [V]
/// Used for efficient argmax sampling from decode output
pub extern fn mlx_lazy_slice_last(handle: ArrayHandle) ArrayHandle;

/// Get array shape
extern fn mlx_array_shape(
    handle: ArrayHandle,
    shape: [*]usize,
    ndim: *usize,
) void;

// ============================================================================
// KV Cache
// ============================================================================

/// Create KV cache (quantized 4-bit)
extern fn mlx_cache_create(n_layers: usize) CacheHandle;

/// Create KV cache (bfloat16 - matches mlx_lm default)
extern fn mlx_cache_create_bfloat16(n_layers: usize) CacheHandle;

/// Free cache
extern fn mlx_cache_free(cache: CacheHandle) void;

/// Update buffer with new K/V (bfloat16) and return concatenated cache
extern fn mlx_cache_update_and_fetch_bfloat16(
    cache: CacheHandle,
    layer_idx: usize,
    k_new: ArrayHandle,
    v_new: ArrayHandle,
    k_out: *ArrayHandle,
    v_out: *ArrayHandle,
    is_prefill_out: *bool,
) void;

/// Get bfloat16 cache (non-quantized)
extern fn mlx_cache_get_bfloat16(
    cache: CacheHandle,
    layer_idx: usize,
    k_out: *ArrayHandle,
    v_out: *ArrayHandle,
) void;

/// Set full bfloat16 cache (fusion returns full cache, don't concatenate)
extern fn mlx_cache_set_full_bfloat16(
    cache: CacheHandle,
    layer_idx: usize,
    k_full: ArrayHandle,
    v_full: ArrayHandle,
) void;

/// Evaluate all cache arrays (force evaluation of lazy concatenations)
extern fn mlx_cache_eval_all(cache: CacheHandle, n_layers: usize) void;

/// Update buffer with new K/V (quantizes internally) and return quantized cache
extern fn mlx_cache_update_and_fetch(
    cache: CacheHandle,
    layer_idx: usize,
    k_new: ArrayHandle,
    v_new: ArrayHandle,
    k_out: *ArrayHandle,
    v_out: *ArrayHandle,
    is_prefill_out: *bool,
) void;

/// Get quantized cache triplets (weights, scales, biases) for K and V
extern fn mlx_cache_get_quantized(
    cache: CacheHandle,
    layer_idx: usize,
    k_weights_out: *ArrayHandle,
    k_scales_out: *ArrayHandle,
    k_biases_out: *ArrayHandle,
    v_weights_out: *ArrayHandle,
    v_scales_out: *ArrayHandle,
    v_biases_out: *ArrayHandle,
) void;

// ============================================================================
// High-level Zig wrappers
// ============================================================================

/// Convert i64 shape slice to usize array (max 8 dims)
fn shapeToUsize(shape_i64: []const i64) struct { shape: [8]usize, len: usize } {
    var shape: [8]usize = undefined;
    for (shape_i64, 0..) |dim, i| {
        shape[i] = @intCast(dim);
    }
    return .{ .shape = shape, .len = shape_i64.len };
}

/// Create MLX array from Zig slice (float32)
pub fn createArrayF32(data: []const f32, shape: []const i64) ArrayHandle {
    const s = shapeToUsize(shape);
    return mlx_array_from_float32(@ptrCast(data.ptr), &s.shape, s.len);
}

/// Create MLX array from Zig slice (uint32)
pub fn createArrayU32(data: []const u32, shape: []const i64) ArrayHandle {
    const s = shapeToUsize(shape);
    return mlx_array_from_uint32(@ptrCast(data.ptr), &s.shape, s.len);
}

/// Create MLX array from unaligned uint32 data (for mmap'd safetensor data)
pub fn createArrayU32Unaligned(data: [*]align(1) const u32, len: usize, shape: []const i64) ArrayHandle {
    _ = len; // used for bounds checking in caller
    const s = shapeToUsize(shape);
    // Cast to *const anyopaque to avoid alignment checks - C++ uses memcpy internally
    return mlx_array_from_uint32(@ptrCast(data), &s.shape, s.len);
}

/// Create MLX array from Zig slice (bfloat16 as u16)
pub fn createArrayBF16(data: []const u16, shape: []const i64) ArrayHandle {
    const s = shapeToUsize(shape);
    return mlx_array_from_bfloat16(@ptrCast(data.ptr), &s.shape, s.len);
}

/// Create MLX array from unaligned bfloat16 data (for mmap'd safetensor data)
pub fn createArrayBF16Unaligned(data: [*]align(1) const u16, len: usize, shape: []const i64) ArrayHandle {
    _ = len; // used for bounds checking in caller
    const s = shapeToUsize(shape);
    // Cast to *const anyopaque to avoid alignment checks - C++ uses memcpy internally
    return mlx_array_from_bfloat16(@ptrCast(data), &s.shape, s.len);
}

/// Create MLX array from Zig slice (float16/IEEE as u16)
pub fn createArrayF16(data: []const u16, shape: []const i64) ArrayHandle {
    const s = shapeToUsize(shape);
    return mlx_array_from_float16(@ptrCast(data.ptr), &s.shape, s.len);
}

/// Create MLX array from unaligned float16 data (for mmap'd safetensor data)
pub fn createArrayF16Unaligned(data: [*]align(1) const u16, len: usize, shape: []const i64) ArrayHandle {
    _ = len; // used for bounds checking in caller
    const s = shapeToUsize(shape);
    // Cast to *const anyopaque to avoid alignment checks - C++ uses memcpy internally
    return mlx_array_from_float16(@ptrCast(data), &s.shape, s.len);
}

/// Free MLX array
pub fn freeArray(handle: ArrayHandle) void {
    mlx_array_free(handle);
}

/// Evaluate all arrays - executes entire graph on GPU
pub fn eval(handles: []const ArrayHandle) void {
    mlx_eval(@ptrCast(@constCast(handles.ptr)), handles.len);
}

/// Async evaluate - starts GPU work in background, returns immediately
/// Use for pipelining to overlap CPU work with GPU work
pub fn asyncEval(handles: []const ArrayHandle) void {
    mlx_async_eval(@ptrCast(@constCast(handles.ptr)), handles.len);
}

/// Copy array data from GPU to CPU
pub fn copyToHost(handle: ArrayHandle, out: []f32) void {
    mlx_array_to_float32(handle, out.ptr, out.len);
}

/// Get array shape and dimensions
pub fn getShape(handle: ArrayHandle, shape_out: []usize) usize {
    var ndim: usize = 0;
    mlx_array_shape(handle, shape_out.ptr, &ndim);
    return ndim;
}

/// KV Cache wrapper
pub const Cache = struct {
    handle: CacheHandle,
    use_bfloat16: bool,

    /// Create cache with specified format
    /// use_bfloat16: true = bfloat16 cache (matches mlx_lm), false = quantized 4-bit
    pub fn init(n_layers: usize, use_bfloat16: bool) Cache {
        const handle = if (use_bfloat16)
            mlx_cache_create_bfloat16(n_layers)
        else
            mlx_cache_create(n_layers);
        return .{ .handle = handle, .use_bfloat16 = use_bfloat16 };
    }

    pub fn deinit(self: Cache) void {
        mlx_cache_free(self.handle);
    }

    /// Update buffer with new K/V and return concatenated cache
    pub fn updateAndFetch(self: Cache, layer_idx: usize, k_new: ArrayHandle, v_new: ArrayHandle) struct { k: ArrayHandle, v: ArrayHandle, is_prefill: bool } {
        var k: ArrayHandle = null;
        var v: ArrayHandle = null;
        var is_prefill: bool = false;

        if (self.use_bfloat16) {
            mlx_cache_update_and_fetch_bfloat16(self.handle, layer_idx, k_new, v_new, &k, &v, &is_prefill);
        } else {
            mlx_cache_update_and_fetch(self.handle, layer_idx, k_new, v_new, &k, &v, &is_prefill);
        }

        return .{ .k = k, .v = v, .is_prefill = is_prefill };
    }

    /// Get bfloat16 cache (non-quantized) - for use with regular attention
    pub fn get(self: Cache, layer_idx: usize) struct { k: ArrayHandle, v: ArrayHandle } {
        var k: ArrayHandle = null;
        var v: ArrayHandle = null;
        mlx_cache_get_bfloat16(self.handle, layer_idx, &k, &v);
        return .{ .k = k, .v = v };
    }

    /// Set full bfloat16 cache (fusion already concatenated, just store)
    pub fn setFull(self: Cache, layer_idx: usize, k_full: ArrayHandle, v_full: ArrayHandle) void {
        mlx_cache_set_full_bfloat16(self.handle, layer_idx, k_full, v_full);
    }

    /// Evaluate all cache arrays (force evaluation of lazy concatenations from fusion)
    pub fn evalAll(self: Cache, n_layers: usize) void {
        mlx_cache_eval_all(self.handle, n_layers);
    }

    /// Get quantized cache triplets for use with quantized_matmul
    pub fn getQuantized(self: Cache, layer_idx: usize) struct {
        k_weights: ArrayHandle,
        k_scales: ArrayHandle,
        k_biases: ArrayHandle,
        v_weights: ArrayHandle,
        v_scales: ArrayHandle,
        v_biases: ArrayHandle,
    } {
        var k_w: ArrayHandle = null;
        var k_s: ArrayHandle = null;
        var k_b: ArrayHandle = null;
        var v_w: ArrayHandle = null;
        var v_s: ArrayHandle = null;
        var v_b: ArrayHandle = null;
        mlx_cache_get_quantized(self.handle, layer_idx, &k_w, &k_s, &k_b, &v_w, &v_s, &v_b);
        return .{
            .k_weights = k_w,
            .k_scales = k_s,
            .k_biases = k_b,
            .v_weights = v_w,
            .v_scales = v_s,
            .v_biases = v_b,
        };
    }
};

// ============================================================================
// Compiled Layer Functions (FUSION OPTIMIZATION)
// ============================================================================

/// Opaque handle to compiled layer function
pub const CompiledLayerHandle = ?*anyopaque;
pub const LayerOutputHandle = ?*anyopaque;

/// Compile a transformer layer for maximum fusion
pub extern fn mlx_compile_layer(
    q_weight: ArrayHandle,
    q_scales: ArrayHandle,
    q_biases: ArrayHandle,
    k_weight: ArrayHandle,
    k_scales: ArrayHandle,
    k_biases: ArrayHandle,
    v_weight: ArrayHandle,
    v_scales: ArrayHandle,
    v_biases: ArrayHandle,
    o_weight: ArrayHandle,
    o_scales: ArrayHandle,
    o_biases: ArrayHandle,
    gate_weight: ArrayHandle,
    gate_scales: ArrayHandle,
    gate_biases: ArrayHandle,
    up_weight: ArrayHandle,
    up_scales: ArrayHandle,
    up_biases: ArrayHandle,
    down_weight: ArrayHandle,
    down_scales: ArrayHandle,
    down_biases: ArrayHandle,
    attn_norm: ArrayHandle,
    ffn_norm: ArrayHandle,
    q_norm: ArrayHandle,
    k_norm: ArrayHandle,
    n_heads: usize,
    n_kv_heads: usize,
    head_dim: usize,
    hidden_dim: usize,
    group_size: usize,
    bits: usize,
    rope_theta: f32,
    rms_eps: f32,
) CompiledLayerHandle;

/// Execute compiled layer forward pass (mutates cache internally like Python)
pub extern fn mlx_layer_forward(
    compiled_handle: CompiledLayerHandle,
    hidden: ArrayHandle,
    cache_ptr: CacheHandle,
    layer_idx: usize,
    pos_offset: usize,
) ArrayHandle;

/// Compiled layer wrapper
pub const CompiledLayer = struct {
    handle: CompiledLayerHandle,

    pub fn forward(
        self: CompiledLayer,
        hidden: ArrayHandle,
        cache_ptr: CacheHandle,
        layer_idx: usize,
        pos_offset: usize,
    ) ArrayHandle {
        return mlx_layer_forward(self.handle, hidden, cache_ptr, layer_idx, pos_offset);
    }
};

// ============================================================================
// FULLY FUSED MODEL: All layers in ONE C++ call (ZERO FFI overhead)
// ============================================================================

/// Opaque handle to fused model
pub const FusedModelHandle = ?*anyopaque;

/// Create fused model structure
pub extern fn mlx_fused_model_create(
    n_layers: usize,
    n_heads: usize,
    n_kv_heads: usize,
    head_dim: usize,
    hidden_dim: usize,
    group_size: usize,
    bits: usize,
    rope_theta: f32,
    rms_eps: f32,
) FusedModelHandle;

/// Set embedding weights (quantized)
pub extern fn mlx_fused_model_set_embeddings(
    model: FusedModelHandle,
    w: ArrayHandle,
    s: ArrayHandle,
    b: ArrayHandle,
) void;

/// Set final norm and lm_head weights
pub extern fn mlx_fused_model_set_final(
    model: FusedModelHandle,
    ln_w: ArrayHandle,
    lm_w: ArrayHandle,
    lm_s: ArrayHandle,
    lm_b: ArrayHandle,
) void;

/// Set custom RoPE frequencies (for Llama3-style scaling)
pub extern fn mlx_fused_model_set_rope_freqs(
    model: FusedModelHandle,
    freqs: ArrayHandle,
) void;

/// Set Gemma3-specific config (embedding scaling, GELU, attention scale)
pub extern fn mlx_fused_model_set_gemma3_config(
    model: FusedModelHandle,
    is_gemma3: bool,
    use_gelu: bool,
    query_pre_attn_scalar: f32,
) void;

/// Set Granite-specific config (scaling multipliers)
pub extern fn mlx_fused_model_set_granite_config(
    model: FusedModelHandle,
    is_granite: bool,
    embedding_multiplier: f32,
    attention_multiplier: f32,
    residual_multiplier: f32,
    logits_scaling: f32,
) void;

/// Set per-layer weights
pub extern fn mlx_fused_model_set_layer(
    model: FusedModelHandle,
    layer_idx: usize,
    ln1_w: ArrayHandle,
    q_w: ArrayHandle,
    q_s: ArrayHandle,
    q_b: ArrayHandle,
    k_w: ArrayHandle,
    k_s: ArrayHandle,
    k_b: ArrayHandle,
    v_w: ArrayHandle,
    v_s: ArrayHandle,
    v_b: ArrayHandle,
    o_w: ArrayHandle,
    o_s: ArrayHandle,
    o_b: ArrayHandle,
    ln2_w: ArrayHandle,
    gate_w: ArrayHandle,
    gate_s: ArrayHandle,
    gate_b: ArrayHandle,
    up_w: ArrayHandle,
    up_s: ArrayHandle,
    up_b: ArrayHandle,
    down_w: ArrayHandle,
    down_s: ArrayHandle,
    down_b: ArrayHandle,
    q_norm: ArrayHandle,
    k_norm: ArrayHandle,
    pre_ffn_norm: ArrayHandle,
    post_ffn_norm: ArrayHandle,
) void;

/// Single decode step: token_id -> next_token_id (ALL in C++, ZERO FFI overhead)
/// This is the key optimization: entire forward pass + argmax in one call
pub extern fn mlx_fused_decode_step(
    model: FusedModelHandle,
    cache: CacheHandle,
    token_id: u32,
    pos_offset: usize,
) u32;

// ===========================================================================
// TRUE PIPELINED DECODE - builds graph N+1 before materializing N
// ===========================================================================

/// Prime the pipeline: initializes with first token and builds first graph
/// Call once before the decode loop with the last prompt token
pub extern fn mlx_pipeline_prime(
    model: FusedModelHandle,
    cache: CacheHandle,
    first_token_id: u32,
    pos_offset: usize,
) void;

/// Pipeline step: returns current token, builds and queues next
/// This builds the graph for token N+1 BEFORE materializing token N.
/// Must call mlx_pipeline_prime first.
pub extern fn mlx_pipeline_step(
    model: FusedModelHandle,
    cache: CacheHandle,
    pos_offset: usize,
) u32;

/// Flush the pipeline: returns the last pending token
/// Call after the decode loop to get the final token
pub extern fn mlx_pipeline_flush() u32;

/// Batch decode: run entire decode loop in C++ to eliminate FFI overhead
/// Returns number of tokens generated
pub extern fn mlx_fused_decode_batch(
    model: FusedModelHandle,
    cache: CacheHandle,
    first_token: u32,
    start_pos: usize,
    out_tokens: [*]u32,
    max_tokens: usize,
    eos_ids: [*]const u32,
    n_eos_ids: usize,
) u32;

/// Free fused model
pub extern fn mlx_fused_model_free(model: FusedModelHandle) void;

/// Optimize fused model (fuse QKV and gate/up weights for faster inference)
/// Call after all layers are set
pub extern fn mlx_fused_model_optimize(model: FusedModelHandle) void;

// ===========================================================================
// FUSED DENSE MODEL - BFloat16 weights (non-quantized)
// ===========================================================================

/// Opaque handle to dense (BF16) fused model
pub const DenseModelHandle = ?*anyopaque;

/// Create dense model for BFloat16 weights
pub extern fn mlx_dense_model_create(
    n_layers: usize,
    n_heads: usize,
    n_kv_heads: usize,
    head_dim: usize,
    hidden_dim: usize,
    rope_theta: f32,
    rms_eps: f32,
) DenseModelHandle;

/// Set dense model embeddings (BF16)
pub extern fn mlx_dense_model_set_embeddings(
    model: DenseModelHandle,
    embed: ArrayHandle,
) void;

/// Set dense model final weights
pub extern fn mlx_dense_model_set_final(
    model: DenseModelHandle,
    ln_w: ArrayHandle,
    lm_head: ArrayHandle,
) void;

/// Set dense model layer weights
pub extern fn mlx_dense_model_set_layer(
    model: DenseModelHandle,
    layer_idx: usize,
    ln1_w: ArrayHandle,
    q_proj: ArrayHandle,
    k_proj: ArrayHandle,
    v_proj: ArrayHandle,
    o_proj: ArrayHandle,
    ln2_w: ArrayHandle,
    gate_proj: ArrayHandle,
    up_proj: ArrayHandle,
    down_proj: ArrayHandle,
    q_norm: ArrayHandle, // null if not present
    k_norm: ArrayHandle, // null if not present
) void;

/// Free dense model
pub extern fn mlx_dense_model_free(model: DenseModelHandle) void;

/// Prime dense pipeline with first token
pub extern fn mlx_dense_pipeline_prime(
    model: DenseModelHandle,
    cache: CacheHandle,
    first_token_id: u32,
    pos_offset: usize,
) void;

/// Dense pipeline step - returns current token, queues next
pub extern fn mlx_dense_pipeline_step(
    model: DenseModelHandle,
    cache: CacheHandle,
    pos_offset: usize,
) u32;

/// Flush dense pipeline - returns last pending token
pub extern fn mlx_dense_pipeline_flush() u32;

test "MLX graph API compiles" {
    _ = ArrayHandle;
    _ = CacheHandle;
    _ = Cache;
    _ = CompiledLayerHandle;
    _ = FusedModelHandle;
}
