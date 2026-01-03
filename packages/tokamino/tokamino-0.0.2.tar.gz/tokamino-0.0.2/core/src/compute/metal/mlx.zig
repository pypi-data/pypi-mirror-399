// Zig bindings for MLX quantized matmul - now implemented in Zig using mlx_graph API
const std = @import("std");
const mlx_graph = @import("graph.zig");

// ============================================================================
// Internal implementations using mlx_graph lazy API
// ============================================================================

fn mlx_quantized_matmul_4bit_impl(
    a_data: [*]const f32,
    m: usize,
    k: usize,
    w_data: [*]const u8,
    scales: [*]align(1) const u16,
    biases: [*]align(1) const u16,
    n: usize,
    group_size: usize,
    c_data: [*]f32,
) bool {
    // Create MLX arrays from input data
    const a_shape = [_]usize{ m, k };
    const a_handle = mlx_graph.mlx_array_from_float32(a_data, &a_shape, 2);
    defer mlx_graph.mlx_array_free(a_handle);

    // Packed weights: [n, k/8] uint32
    const w_u32 = @as([*]const u32, @ptrCast(@alignCast(w_data)));
    const packed_k = k / 8;
    const w_shape = [_]usize{ n, packed_k };
    const w_handle = mlx_graph.mlx_array_from_uint32(w_u32, &w_shape, 2);
    defer mlx_graph.mlx_array_free(w_handle);

    // Scales: [n, k/group_size] bfloat16
    const scales_shape = [_]usize{ n, k / group_size };
    const s_handle = mlx_graph.mlx_array_from_bfloat16(scales, &scales_shape, 2);
    defer mlx_graph.mlx_array_free(s_handle);

    // Biases: [n, k/group_size] bfloat16
    const b_handle = mlx_graph.mlx_array_from_bfloat16(biases, &scales_shape, 2);
    defer mlx_graph.mlx_array_free(b_handle);

    // Call quantized matmul
    const result_handle = mlx_graph.mlx_lazy_quantized_matmul(
        a_handle,
        w_handle,
        s_handle,
        b_handle,
        group_size,
        4, // bits
        true, // transpose
    );
    defer mlx_graph.mlx_array_free(result_handle);

    // Evaluate
    var handles = [_]mlx_graph.ArrayHandle{result_handle};
    mlx_graph.mlx_eval(&handles, 1);

    // Copy result back
    mlx_graph.mlx_array_to_float32(result_handle, c_data, m * n);

    return true;
}

fn mlx_rms_norm_impl(
    x_data: [*]const f32,
    weight_data: [*]const f32,
    batch: usize,
    seq_len: usize,
    dim: usize,
    eps: f32,
    out_data: [*]f32,
) bool {
    // Create arrays
    const x_shape = [_]usize{ batch, seq_len, dim };
    const x_handle = mlx_graph.mlx_array_from_float32(x_data, &x_shape, 3);
    defer mlx_graph.mlx_array_free(x_handle);

    const w_shape = [_]usize{dim};
    const w_handle = mlx_graph.mlx_array_from_float32(weight_data, &w_shape, 1);
    defer mlx_graph.mlx_array_free(w_handle);

    // Call RMS norm
    const result_handle = mlx_graph.mlx_lazy_rms_norm(x_handle, w_handle, eps);
    defer mlx_graph.mlx_array_free(result_handle);

    // Evaluate
    var handles = [_]mlx_graph.ArrayHandle{result_handle};
    mlx_graph.mlx_eval(&handles, 1);

    // Copy back
    mlx_graph.mlx_array_to_float32(result_handle, out_data, batch * seq_len * dim);

    return true;
}

fn mlx_rope_impl(
    x_data: [*]const f32,
    batch: usize,
    seq_len: usize,
    n_heads: usize,
    head_dim: usize,
    offset: c_int,
    rope_base: f32,
    out_data: [*]f32,
) bool {
    // Create array
    const x_shape = [_]usize{ batch, seq_len, n_heads, head_dim };
    const x_handle = mlx_graph.mlx_array_from_float32(x_data, &x_shape, 4);
    defer mlx_graph.mlx_array_free(x_handle);

    // Call RoPE
    const result_handle = mlx_graph.mlx_lazy_rope(x_handle, head_dim, @intCast(offset), rope_base);
    defer mlx_graph.mlx_array_free(result_handle);

    // Evaluate
    var handles = [_]mlx_graph.ArrayHandle{result_handle};
    mlx_graph.mlx_eval(&handles, 1);

    // Copy back
    mlx_graph.mlx_array_to_float32(result_handle, out_data, batch * seq_len * n_heads * head_dim);

    return true;
}

fn mlx_scaled_dot_product_attention_impl(
    q_data: [*]const f32,
    k_data: [*]const f32,
    v_data: [*]const f32,
    batch: usize,
    n_heads: usize,
    n_kv_heads: usize,
    seq_len: usize,
    kv_seq_len: usize,
    head_dim: usize,
    scale: f32,
    out_data: [*]f32,
) bool {
    // Create arrays
    const q_shape = [_]usize{ batch, n_heads, seq_len, head_dim };
    const q_handle = mlx_graph.mlx_array_from_float32(q_data, &q_shape, 4);
    defer mlx_graph.mlx_array_free(q_handle);

    const kv_shape = [_]usize{ batch, n_kv_heads, kv_seq_len, head_dim };
    const k_handle = mlx_graph.mlx_array_from_float32(k_data, &kv_shape, 4);
    const v_handle = mlx_graph.mlx_array_from_float32(v_data, &kv_shape, 4);

    // Handle GQA (grouped query attention)
    // If n_kv_heads < n_heads, we need to repeat K/V heads
    // For now, we'll call attention directly and let MLX handle it
    // TODO: Add repeat operation if MLX doesn't handle GQA automatically
    defer mlx_graph.mlx_array_free(k_handle);
    defer mlx_graph.mlx_array_free(v_handle);

    // Call attention
    const result_handle = mlx_graph.mlx_lazy_attention(q_handle, k_handle, v_handle, scale, true);
    defer mlx_graph.mlx_array_free(result_handle);

    // Evaluate
    var handles = [_]mlx_graph.ArrayHandle{result_handle};
    mlx_graph.mlx_eval(&handles, 1);

    // Copy back
    mlx_graph.mlx_array_to_float32(result_handle, out_data, batch * n_heads * seq_len * head_dim);

    return true;
}

fn mlx_silu_impl(
    x_data: [*]const f32,
    size: usize,
    out_data: [*]f32,
) bool {
    // Create array
    const x_shape = [_]usize{size};
    const x_handle = mlx_graph.mlx_array_from_float32(x_data, &x_shape, 1);
    defer mlx_graph.mlx_array_free(x_handle);

    // Call SiLU
    const result_handle = mlx_graph.mlx_lazy_silu(x_handle);
    defer mlx_graph.mlx_array_free(result_handle);

    // Evaluate
    var handles = [_]mlx_graph.ArrayHandle{result_handle};
    mlx_graph.mlx_eval(&handles, 1);

    // Copy back
    mlx_graph.mlx_array_to_float32(result_handle, out_data, size);

    return true;
}

// ============================================================================
// Export C ABI functions (for compatibility if needed externally)
// ============================================================================

export fn mlx_quantized_matmul_4bit(
    a_data: [*]const f32,
    m: usize,
    k: usize,
    w_data: [*]const u8,
    scales: [*]align(1) const u16,
    biases: [*]align(1) const u16,
    n: usize,
    group_size: usize,
    c_data: [*]f32,
) bool {
    return mlx_quantized_matmul_4bit_impl(a_data, m, k, w_data, scales, biases, n, group_size, c_data);
}

export fn mlx_rms_norm(
    x_data: [*]const f32,
    weight_data: [*]const f32,
    batch: usize,
    seq_len: usize,
    dim: usize,
    eps: f32,
    out_data: [*]f32,
) bool {
    return mlx_rms_norm_impl(x_data, weight_data, batch, seq_len, dim, eps, out_data);
}

export fn mlx_rope(
    x_data: [*]const f32,
    batch: usize,
    seq_len: usize,
    n_heads: usize,
    head_dim: usize,
    offset: c_int,
    rope_base: f32,
    out_data: [*]f32,
) bool {
    return mlx_rope_impl(x_data, batch, seq_len, n_heads, head_dim, offset, rope_base, out_data);
}

export fn mlx_scaled_dot_product_attention(
    q_data: [*]const f32,
    k_data: [*]const f32,
    v_data: [*]const f32,
    batch: usize,
    n_heads: usize,
    n_kv_heads: usize,
    seq_len: usize,
    kv_seq_len: usize,
    head_dim: usize,
    scale: f32,
    out_data: [*]f32,
) bool {
    return mlx_scaled_dot_product_attention_impl(q_data, k_data, v_data, batch, n_heads, n_kv_heads, seq_len, kv_seq_len, head_dim, scale, out_data);
}

export fn mlx_silu(
    x_data: [*]const f32,
    size: usize,
    out_data: [*]f32,
) bool {
    return mlx_silu_impl(x_data, size, out_data);
}

/// Grouped-affine u4 quantized matrix multiplication using Metal GPU (MLX backend)
/// A: [m x k] f32
/// B: [k x n] grouped-affine u4 (w_data + scales + biases)
/// C: [m x n] f32 output
pub fn matmulGaffineU4(
    a: []const f32,
    m: usize,
    k: usize,
    w_data: []const u8,
    scales: []align(1) const u16,
    biases: []align(1) const u16,
    n: usize,
    group_size: usize,
    c: []f32,
) !void {
    std.debug.assert(a.len >= m * k);
    std.debug.assert(c.len >= m * n);

    const success = mlx_quantized_matmul_4bit(
        a.ptr,
        m,
        k,
        w_data.ptr,
        scales.ptr,
        biases.ptr,
        n,
        group_size,
        c.ptr,
    );

    if (!success) return error.MLXMatmulFailed;
}

// Legacy alias for older call sites.
pub const matmulMLX4Bit = matmulGaffineU4;

/// RMS normalization using MLX
/// x: [batch, seq_len, dim]
/// weight: [dim]
/// out: [batch, seq_len, dim]
pub fn rmsNorm(
    x: []const f32,
    weight: []const f32,
    batch: usize,
    seq_len: usize,
    dim: usize,
    eps: f32,
    out: []f32,
) !void {
    std.debug.assert(x.len >= batch * seq_len * dim);
    std.debug.assert(weight.len >= dim);
    std.debug.assert(out.len >= batch * seq_len * dim);

    const success = mlx_rms_norm(
        x.ptr,
        weight.ptr,
        batch,
        seq_len,
        dim,
        eps,
        out.ptr,
    );

    if (!success) return error.MLXRmsNormFailed;
}

/// RoPE using MLX
/// x: [batch, seq_len, n_heads, head_dim]
/// offset: position offset for autoregressive generation
/// out: [batch, seq_len, n_heads, head_dim]
pub fn rope(
    x: []const f32,
    batch: usize,
    seq_len: usize,
    n_heads: usize,
    head_dim: usize,
    offset: usize,
    rope_base: f32,
    out: []f32,
) !void {
    std.debug.assert(x.len >= batch * seq_len * n_heads * head_dim);
    std.debug.assert(out.len >= batch * seq_len * n_heads * head_dim);

    const success = mlx_rope(
        x.ptr,
        batch,
        seq_len,
        n_heads,
        head_dim,
        @intCast(offset),
        rope_base,
        out.ptr,
    );

    if (!success) return error.MLXRopeFailed;
}

/// Scaled dot product attention using MLX
/// q: [batch, n_heads, seq_len, head_dim]
/// k: [batch, n_kv_heads, kv_seq_len, head_dim]
/// v: [batch, n_kv_heads, kv_seq_len, head_dim]
/// out: [batch, n_heads, seq_len, head_dim]
pub fn scaledDotProductAttention(
    q: []const f32,
    k: []const f32,
    v: []const f32,
    batch: usize,
    n_heads: usize,
    n_kv_heads: usize,
    seq_len: usize,
    kv_seq_len: usize,
    head_dim: usize,
    scale: f32,
    out: []f32,
) !void {
    std.debug.assert(q.len >= batch * n_heads * seq_len * head_dim);
    std.debug.assert(k.len >= batch * n_kv_heads * kv_seq_len * head_dim);
    std.debug.assert(v.len >= batch * n_kv_heads * kv_seq_len * head_dim);
    std.debug.assert(out.len >= batch * n_heads * seq_len * head_dim);

    const success = mlx_scaled_dot_product_attention(
        q.ptr,
        k.ptr,
        v.ptr,
        batch,
        n_heads,
        n_kv_heads,
        seq_len,
        kv_seq_len,
        head_dim,
        scale,
        out.ptr,
    );

    if (!success) return error.MLXAttentionFailed;
}

/// SiLU activation using MLX
pub fn silu(
    x: []const f32,
    out: []f32,
) !void {
    std.debug.assert(x.len == out.len);

    const success = mlx_silu(
        x.ptr,
        x.len,
        out.ptr,
    );

    if (!success) return error.MLXSiluFailed;
}
