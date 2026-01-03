// MLX-native forward pass using LAZY GRAPH API
// Follows test_mlx_single.py exactly:
// 1. Build lazy computation graph (operations don't execute)
// 2. Call mx.eval() ONCE to execute entire graph on GPU
// 3. Copy ONLY logits to CPU for sampling
// Performance target: 243 t/s decode (matching Python MLX)

const std = @import("std");
const tensor_mod = @import("../../../tensor.zig");
const Tensor = tensor_mod.Tensor;
const loader = @import("../../../io/internal.zig").model_loader;
const dtype_mod = @import("../../../dtype.zig");
const mlx_graph = @import("../../../compute/metal/graph.zig");

const builtin = @import("builtin");

const ArrayHandle = mlx_graph.ArrayHandle;
pub const Cache = mlx_graph.Cache;

fn tensorToArray(t: *const Tensor) ArrayHandle {
    const shape = t.shape[0..@as(usize, @intCast(t.n_dims))];
    switch (t.dtype) {
        .f32 => return mlx_graph.createArrayF32(t.asSlice(f32), shape),
        .bf16 => {
            const len = t.data_size / 2;
            const ptr: [*]align(1) const u16 = @ptrCast(t.data_ptr);
            return mlx_graph.createArrayBF16Unaligned(ptr, len, shape);
        },
        .f16 => {
            const len = t.data_size / 2;
            const ptr: [*]align(1) const u16 = @ptrCast(t.data_ptr);
            return mlx_graph.createArrayF16Unaligned(ptr, len, shape);
        },
        else => @panic("tensorToArray: unsupported dtype"),
    }
}

/// Load a 1D norm weight tensor to MLX array.
/// Handles f32 (from GGUF), bf16, and f16 dtypes.
fn loadNormWeight(t: *const Tensor) ArrayHandle {
    switch (t.dtype) {
        .f32 => {
            // GGUF norms are F32 - convert element count correctly
            const len = t.data_size / 4;
            const shape = [_]usize{len};
            // Use raw pointer to avoid alignment requirements
            return mlx_graph.mlx_array_from_float32(@ptrCast(t.data_ptr), &shape, 1);
        },
        .f16 => {
            const len = t.data_size / 2;
            const shape = [_]i64{@intCast(len)};
            const ptr: [*]align(1) const u16 = @ptrCast(t.data_ptr);
            return mlx_graph.createArrayF16Unaligned(ptr, len, &shape);
        },
        .bf16 => {
            const len = t.data_size / 2;
            const shape = [_]i64{@intCast(len)};
            const ptr: [*]align(1) const u16 = @ptrCast(t.data_ptr);
            return mlx_graph.createArrayBF16Unaligned(ptr, len, &shape);
        },
        else => @panic("loadNormWeight: unsupported dtype"),
    }
}

/// Compute Llama3-style RoPE frequencies with wavelength-dependent scaling.
/// This implements the same formula as mlx_lm's Llama3RoPE class.
fn computeLlama3RopeFreqs(
    allocator: std.mem.Allocator,
    dims: usize,
    base: f32,
    factor: f32,
    low_freq_factor: f32,
    high_freq_factor: f32,
    old_context_len: i32,
) ![]f32 {
    const n_freqs = dims / 2;
    const freqs = try allocator.alloc(f32, n_freqs);
    errdefer allocator.free(freqs);

    const old_ctx: f32 = @floatFromInt(old_context_len);
    const low_freq_wavelen = old_ctx / low_freq_factor;
    const high_freq_wavelen = old_ctx / high_freq_factor;
    const dims_f: f32 = @floatFromInt(dims);

    for (0..n_freqs) |i| {
        const idx: f32 = @floatFromInt(i * 2);
        // Standard RoPE: freq = base^(2i/dims)
        const freq = std.math.pow(f32, base, idx / dims_f);
        const wavelen = 2.0 * std.math.pi * freq;

        if (wavelen > low_freq_wavelen) {
            // Long wavelengths: scale by factor (for extended context)
            freqs[i] = freq * factor;
        } else if (wavelen < high_freq_wavelen) {
            // Short wavelengths: keep original
            freqs[i] = freq;
        } else {
            // Medium wavelengths: smooth interpolation
            const smooth_factor = (old_ctx / wavelen - low_freq_factor) / (high_freq_factor - low_freq_factor);
            freqs[i] = freq / ((1.0 - smooth_factor) / factor + smooth_factor);
        }
    }

    return freqs;
}

/// Load model weights as MLX array handles (GPU)
/// Call this ONCE at startup, keep handles for entire session
pub fn loadWeightsToGPU(allocator: std.mem.Allocator, loaded: *loader.LoadedModel) !*WeightHandles {
    if (builtin.os.tag != .macos) {
        return error.MLXNotAvailable;
    }

    const blocks = loaded.blocks;

    // MoE models are now supported
    const is_moe = loaded.config.num_experts > 0;
    if (is_moe) {
        std.log.info("MoE model detected - {d} experts, {d} active per token", .{ loaded.config.num_experts, loaded.config.experts_per_token });
    }

    var handles = try allocator.create(WeightHandles);
    // Initialize all optional fields to null to avoid undefined memory
    handles.fused_model = null;
    handles.dense_model = null;
    handles.compiled_layers = null;
    handles.is_moe = is_moe;
    handles.num_experts = if (is_moe) @intCast(loaded.config.num_experts) else 0;
    handles.experts_per_token = if (is_moe) @intCast(loaded.config.experts_per_token) else 0;

    // Gemma3 configuration (set by `src/models/gemma.zig` via runtime flags)
    // Detect Gemma3 by non-zero weight offset (1.0 for (1+w) formulation)
    handles.is_gemma3 = loaded.runtime.weight_offset != 0.0;
    handles.d_model = @intCast(loaded.config.d_model);
    if (handles.is_gemma3) {
        std.log.info("Gemma3 model detected - embedding scaling and (1+w) RMSNorm enabled", .{});
    }

    // Granite configuration (set by `src/models/granite.zig` via runtime flags)
    handles.is_granite = loaded.runtime.use_granite_multipliers;
    handles.embedding_multiplier = loaded.config.embedding_multiplier;
    handles.attention_multiplier = loaded.config.attention_multiplier;
    handles.residual_multiplier = loaded.config.residual_multiplier;
    handles.logits_scaling = loaded.config.logits_scaling;
    if (handles.is_granite) {
        std.log.info("Granite model detected - embedding={d:.2}, attention={d:.6}, residual={d:.2}, logits={d:.1}", .{
            handles.embedding_multiplier,
            handles.attention_multiplier,
            handles.residual_multiplier,
            handles.logits_scaling,
        });
    }

    errdefer allocator.destroy(handles);

    // Detect if model is quantized based on original weight dtype (before f32 conversion)
    const is_quantized = loaded.original_weight_dtype == .grouped_affine_u4 or loaded.original_weight_dtype == .grouped_affine_u8;
    handles.is_quantized = is_quantized;

    // Load embedding weights
    // Keep embeddings quantized - will dequantize during lookup
    handles.embed_tokens_quantized = null;
    handles.embed_tokens = null;
    if (is_quantized) {
        // For quantized models, token_embeddings uses grouped_affine_u4/u8 dtype
        const embed_dtype = loaded.token_embeddings.dtype;
        if (embed_dtype == .grouped_affine_u4 or embed_dtype == .grouped_affine_u8) {
            const bits: usize = if (embed_dtype == .grouped_affine_u8) 8 else 4;
            const qw = try loadQuantizedWeight(&loaded.token_embeddings, bits);
            const qw_ptr = try allocator.create(WeightHandles.QuantizedWeight);
            qw_ptr.* = qw;
            handles.embed_tokens_quantized = qw_ptr;
        } else {
            // Quantized model but non-quantized embeddings (rare)
            const embed_data = loaded.token_embeddings.asSlice(f32);
            const embed_shape = loaded.token_embeddings.shape;
            const embed_ndim = @as(usize, @intCast(loaded.token_embeddings.n_dims));
            handles.embed_tokens = mlx_graph.createArrayF32(
                embed_data,
                embed_shape[0..embed_ndim],
            );
        }
    } else {
        // Non-quantized model - use the already-loaded embeddings tensor.
        const embed_shape = loaded.token_embeddings.shape[0..@as(usize, @intCast(loaded.token_embeddings.n_dims))];
        switch (loaded.token_embeddings.dtype) {
            .bf16 => {
                const embed_len = loaded.token_embeddings.data_size / 2;
                const embed_ptr: [*]align(1) const u16 = @ptrCast(loaded.token_embeddings.data_ptr);
                handles.embed_tokens = mlx_graph.createArrayBF16Unaligned(embed_ptr, embed_len, embed_shape);
            },
            .f16 => {
                const embed_len = loaded.token_embeddings.data_size / 2;
                const embed_ptr: [*]align(1) const u16 = @ptrCast(loaded.token_embeddings.data_ptr);
                handles.embed_tokens = mlx_graph.createArrayF16Unaligned(embed_ptr, embed_len, embed_shape);
            },
            .f32 => {
                handles.embed_tokens = mlx_graph.createArrayF32(loaded.token_embeddings.asSlice(f32), embed_shape);
            },
            else => return error.InvalidTensorType,
        }
    }

    // Load per-layer weights
    handles.layers = try allocator.alloc(WeightHandles.LayerWeights, blocks.len);
    errdefer allocator.free(handles.layers);

    // Initialize all layer weights to default values (null for optional fields)
    for (handles.layers) |*layer| {
        layer.* = WeightHandles.LayerWeights{
            .ln1_weight = null,
            .ln2_weight = null,
        };
    }

    for (blocks, 0..) |*block, i| {
        // ln1_weight - load in native dtype (bf16, f16, or f32 for GGUF)
        var ln1_arr = loadNormWeight(block.ln1_weight);
        // Gemma3 uses (1 + weight) for RMSNorm
        if (handles.is_gemma3) {
            ln1_arr = mlx_graph.mlx_add_one(ln1_arr);
        }
        handles.layers[i].ln1_weight = ln1_arr;

        // ln2_weight - load in native dtype (bf16, f16, or f32 for GGUF)
        var ln2_arr = loadNormWeight(block.ln2_weight);
        // Gemma3 uses (1 + weight) for RMSNorm
        if (handles.is_gemma3) {
            ln2_arr = mlx_graph.mlx_add_one(ln2_arr);
        }
        handles.layers[i].ln2_weight = ln2_arr;

        handles.layers[i].is_quantized = is_quantized;

        if (is_quantized) {
            // Detect bits from quantized weight dtype - use o_proj which is always non-null
            const bits: usize = if (block.o_proj.dtype == .grouped_affine_u8) 8 else 4;

            // Q/K/V/O projections (quantized)
            handles.layers[i].q_proj = try loadQuantizedWeight(block.q_proj.?, bits);
            handles.layers[i].k_proj = try loadQuantizedWeight(block.k_proj.?, bits);
            handles.layers[i].v_proj = try loadQuantizedWeight(block.v_proj.?, bits);
            handles.layers[i].o_proj = try loadQuantizedWeight(block.o_proj, bits);

            // FFN weights (quantized) - w1/w2/w3 are null for MoE models
            if (block.w1) |w1| {
                handles.layers[i].w1 = try loadQuantizedWeight(w1, bits);
            }
            if (block.w2) |w2| {
                handles.layers[i].w2 = try loadQuantizedWeight(w2, bits);
            }
            if (block.w3) |w3| {
                handles.layers[i].w3 = try loadQuantizedWeight(w3, bits);
            }
        } else {
            // Non-quantized model - use already-loaded block weights.
            handles.layers[i].q_proj_bf16 = tensorToArray(block.q_proj.?);
            handles.layers[i].k_proj_bf16 = tensorToArray(block.k_proj.?);
            handles.layers[i].v_proj_bf16 = tensorToArray(block.v_proj.?);
            handles.layers[i].o_proj_bf16 = tensorToArray(block.o_proj);

            // FFN weights (BF16/F16/F32) - only for dense models
            if (!is_moe) {
                if (block.w1) |w1| handles.layers[i].w1_bf16 = tensorToArray(w1);
                if (block.w2) |w2| handles.layers[i].w2_bf16 = tensorToArray(w2);
                if (block.w3) |w3| handles.layers[i].w3_bf16 = tensorToArray(w3);
            }
        }

        // Optional attention biases/sinks are loaded by `src/models/*:sanitize()`
        // (e.g. GPT-OSS) and stored in the loader-stage block weights.
        if (block.q_bias) |b| handles.layers[i].q_bias = mlx_graph.createArrayF32(b, &[_]i64{@intCast(b.len)});
        if (block.k_bias) |b| handles.layers[i].k_bias = mlx_graph.createArrayF32(b, &[_]i64{@intCast(b.len)});
        if (block.v_bias) |b| handles.layers[i].v_bias = mlx_graph.createArrayF32(b, &[_]i64{@intCast(b.len)});
        if (block.o_bias) |b| handles.layers[i].o_bias = mlx_graph.createArrayF32(b, &[_]i64{@intCast(b.len)});
        if (block.sinks) |s| handles.layers[i].attn_sinks = mlx_graph.createArrayF32(s, &[_]i64{@intCast(s.len)});

        // QK normalization (Qwen3/Gemma3) - optional, load in native dtype (f32, f16, or bf16)
        if (block.q_norm) |q_norm_tensor| {
            var q_norm_arr = loadNormWeight(q_norm_tensor);
            // Gemma3 uses (1 + weight) for all RMSNorm including Q/K norms
            if (handles.is_gemma3) {
                q_norm_arr = mlx_graph.mlx_add_one(q_norm_arr);
            }
            handles.layers[i].q_norm = q_norm_arr;
        } else {
            handles.layers[i].q_norm = null;
        }

        if (block.k_norm) |k_norm_tensor| {
            var k_norm_arr = loadNormWeight(k_norm_tensor);
            // Gemma3 uses (1 + weight) for all RMSNorm including Q/K norms
            if (handles.is_gemma3) {
                k_norm_arr = mlx_graph.mlx_add_one(k_norm_arr);
            }
            handles.layers[i].k_norm = k_norm_arr;
        } else {
            handles.layers[i].k_norm = null;
        }

        // Gemma3 FFN layer norms (4 norms per block) - optional
        if (block.pre_ffn_norm) |pre_ffn_norm_tensor| {
            var norm_arr = loadNormWeight(pre_ffn_norm_tensor);
            // Gemma3 uses (1 + weight) for RMSNorm
            if (handles.is_gemma3) {
                norm_arr = mlx_graph.mlx_add_one(norm_arr);
            }
            handles.layers[i].pre_ffn_norm = norm_arr;
        } else {
            handles.layers[i].pre_ffn_norm = null;
        }

        if (block.post_ffn_norm) |post_ffn_norm_tensor| {
            var norm_arr = loadNormWeight(post_ffn_norm_tensor);
            // Gemma3 uses (1 + weight) for RMSNorm
            if (handles.is_gemma3) {
                norm_arr = mlx_graph.mlx_add_one(norm_arr);
            }
            handles.layers[i].post_ffn_norm = norm_arr;
        } else {
            handles.layers[i].post_ffn_norm = null;
        }

        // Initialize MoE weights to null (will be loaded separately for MoE models)
        handles.layers[i].moe = null;
    }

    // Load MoE weights for each layer (already sanitized by model hooks).
    if (is_moe) {
        for (0..blocks.len) |i| {
            const mw = blocks[i].moe_weights orelse continue;
            if (!mw.use_mxfp4) return error.NotImplemented;
            const num_experts: usize = mw.experts.len;
            if (num_experts == 0) return error.InvalidValue;

            const moe_weights = try allocator.create(WeightHandles.MoEWeights);
            errdefer allocator.destroy(moe_weights);

            // Initialize with defaults
            moe_weights.* = .{
                .router_w = undefined,
                .gate_w = undefined,
                .gate_s = undefined,
                .up_w = undefined,
                .up_s = undefined,
                .down_w = undefined,
                .down_s = undefined,
                .router_group_size = 0, // unused for non-quantized router
                .expert_group_size = 32,
                .num_experts = num_experts,
                .experts_per_token = mw.experts_per_token,
            };

            // Router weights are stored for CPU as f32 [d_model, num_experts].
            // MLX fused op expects router_w shaped [num_experts, d_model] and transposes internally.
            if (mw.router_weight.n_dims != 2 or mw.router_weight.dtype != .f32) return error.InvalidShape;
            const router_shape = mw.router_weight.shape[0..@intCast(mw.router_weight.n_dims)];
            var router_arr = mlx_graph.createArrayF32(mw.router_weight.asSlice(f32), router_shape);
            const router_axes = [_]usize{ 1, 0 };
            router_arr = mlx_graph.mlx_lazy_transpose(router_arr, &router_axes, 2);
            moe_weights.router_w = router_arr;
            moe_weights.router_s = null;
            moe_weights.router_b = null;

            if (mw.router_bias) |rb| {
                moe_weights.router_bias = mlx_graph.createArrayF32(rb, &[_]i64{@intCast(rb.len)});
            }

            const e0 = mw.experts[0];
            const is_mlx_format = e0.gate_proj != null;

            // Load expert weights
            if (is_mlx_format) {
                // MLX format: separate gate/up/down projections
                const gate0 = e0.gate_proj orelse return error.MissingField;
                const up0 = e0.up_proj orelse return error.MissingField;
                if (gate0.n_dims != 2 or up0.n_dims != 2) return error.InvalidShape;

                const d_ff: usize = @intCast(gate0.shape[0]);
                const gate_packed_dim: usize = @intCast(@divExact(gate0.shape[1], 4));
                const up_packed_dim: usize = @intCast(@divExact(up0.shape[1], 4));

                const gate_shape_i64 = [_]i64{ @intCast(num_experts), @intCast(d_ff), @intCast(gate_packed_dim) };
                moe_weights.gate_w = mlx_graph.createArrayU32Unaligned(
                    @as([*]align(1) const u32, @ptrCast(gate0.data_ptr)),
                    (gate0.data_size * num_experts) / 4,
                    &gate_shape_i64,
                );
                const gate_sc0 = e0.gate_scales orelse return error.MissingScales;
                const gate_groups: usize = gate_sc0.len / d_ff;
                const gate_scales_shape = [_]usize{ num_experts, d_ff, gate_groups };
                moe_weights.gate_s = mlx_graph.mlx_array_from_uint8(gate_sc0.ptr, &gate_scales_shape, 3);

                const up_shape_i64 = [_]i64{ @intCast(num_experts), @intCast(d_ff), @intCast(up_packed_dim) };
                moe_weights.up_w = mlx_graph.createArrayU32Unaligned(
                    @as([*]align(1) const u32, @ptrCast(up0.data_ptr)),
                    (up0.data_size * num_experts) / 4,
                    &up_shape_i64,
                );
                const up_sc0 = e0.up_scales orelse return error.MissingScales;
                const up_groups: usize = up_sc0.len / d_ff;
                const up_scales_shape = [_]usize{ num_experts, d_ff, up_groups };
                moe_weights.up_s = mlx_graph.mlx_array_from_uint8(up_sc0.ptr, &up_scales_shape, 3);

                if (e0.gate_bias) |b0| {
                    const bias_shape_i64 = [_]i64{ @intCast(num_experts), @intCast(d_ff) };
                    const bias_ptr = @as([*]const f32, @ptrCast(b0.ptr));
                    moe_weights.gate_bias = mlx_graph.createArrayF32(bias_ptr[0 .. b0.len * num_experts], &bias_shape_i64);
                }
                if (e0.up_bias) |b0| {
                    const bias_shape_i64 = [_]i64{ @intCast(num_experts), @intCast(d_ff) };
                    const bias_ptr = @as([*]const f32, @ptrCast(b0.ptr));
                    moe_weights.up_bias = mlx_graph.createArrayF32(bias_ptr[0 .. b0.len * num_experts], &bias_shape_i64);
                }
            } else {
                // HF format: fused gate_up_proj with INTERLEAVED rows (not concatenated!)
                // gate_up_proj_blocks: [num_experts, 2*d_ff, num_groups, block_size] uint8
                // Row 0 = gate[0], Row 1 = up[0], Row 2 = gate[1], Row 3 = up[1], etc.
                // We need to de-interleave: reshape [E, 2*D, P] -> [E, D, 2, P] then slice
                const gate_up0 = e0.gate_up_proj orelse return error.MissingField;
                if (gate_up0.n_dims != 2) return error.InvalidShape;

                const d_ff_times_2_u: usize = @intCast(gate_up0.shape[0]);
                const d_ff_u: usize = d_ff_times_2_u / 2;
                const packed_dim: usize = @intCast(@divExact(gate_up0.shape[1], 4));
                const n_experts_u: usize = num_experts;

                // Create as [num_experts, 2*d_ff, packed_dim] uint32
                // Note: createArrayU32Unaligned needs i64 shape, extern functions need usize
                const u32_shape_i64 = [_]i64{ @intCast(n_experts_u), @intCast(d_ff_times_2_u), @intCast(packed_dim) };
                const fused_w = mlx_graph.createArrayU32Unaligned(
                    @as([*]align(1) const u32, @ptrCast(gate_up0.data_ptr)),
                    (gate_up0.data_size * num_experts) / 4,
                    &u32_shape_i64,
                );

                // Reshape [E, 2*D, P] -> [E, D, 2, P] to group interleaved rows
                const reshaped_shape = [_]usize{ n_experts_u, d_ff_u, 2, packed_dim };
                const reshaped_w = mlx_graph.mlx_lazy_reshape(fused_w, &reshaped_shape, 4);

                // Slice to de-interleave: gate = [:, :, 0, :], up = [:, :, 1, :]
                const n_experts: c_int = @intCast(n_experts_u);
                const d_ff: c_int = @intCast(d_ff_u);
                const packed_dim_c: c_int = @intCast(packed_dim);

                // gate_w: [E, D, 0:1, P] -> squeeze to [E, D, P]
                const gate_w_start = [_]c_int{ 0, 0, 0, 0 };
                const gate_w_end = [_]c_int{ n_experts, d_ff, 1, packed_dim_c };
                const gate_w_4d = mlx_graph.mlx_lazy_slice(reshaped_w, &gate_w_start, &gate_w_end, 4);
                const gate_w_shape = [_]usize{ n_experts_u, d_ff_u, packed_dim };
                // Use persistent_reshape for final weight - must survive pool resets
                moe_weights.gate_w = mlx_graph.mlx_persistent_reshape(gate_w_4d, &gate_w_shape, 3);

                // up_w: [E, D, 1:2, P] -> squeeze to [E, D, P]
                const up_w_start = [_]c_int{ 0, 0, 1, 0 };
                const up_w_end = [_]c_int{ n_experts, d_ff, 2, packed_dim_c };
                const up_w_4d = mlx_graph.mlx_lazy_slice(reshaped_w, &up_w_start, &up_w_end, 4);
                const up_w_shape = [_]usize{ n_experts_u, d_ff_u, packed_dim };
                moe_weights.up_w = mlx_graph.mlx_persistent_reshape(up_w_4d, &up_w_shape, 3);

                const gate_up_sc0 = e0.gate_up_scales orelse return error.MissingScales;
                const s_num_groups_u: usize = gate_up_sc0.len / d_ff_times_2_u;
                const fused_s_shape = [_]usize{ n_experts_u, d_ff_times_2_u, s_num_groups_u };
                const fused_s = mlx_graph.mlx_array_from_uint8(gate_up_sc0.ptr, &fused_s_shape, 3);

                // Reshape [E, 2*D, G] -> [E, D, 2, G] then slice
                const s_reshaped_shape = [_]usize{ n_experts_u, d_ff_u, 2, s_num_groups_u };
                const reshaped_s = mlx_graph.mlx_lazy_reshape(fused_s, &s_reshaped_shape, 4);

                const s_num_groups: c_int = @intCast(s_num_groups_u);
                const gate_s_start = [_]c_int{ 0, 0, 0, 0 };
                const gate_s_end = [_]c_int{ n_experts, d_ff, 1, s_num_groups };
                const gate_s_4d = mlx_graph.mlx_lazy_slice(reshaped_s, &gate_s_start, &gate_s_end, 4);
                const gate_s_shape = [_]usize{ n_experts_u, d_ff_u, s_num_groups_u };
                moe_weights.gate_s = mlx_graph.mlx_persistent_reshape(gate_s_4d, &gate_s_shape, 3);

                const up_s_start = [_]c_int{ 0, 0, 1, 0 };
                const up_s_end = [_]c_int{ n_experts, d_ff, 2, s_num_groups };
                const up_s_4d = mlx_graph.mlx_lazy_slice(reshaped_s, &up_s_start, &up_s_end, 4);
                const up_s_shape = [_]usize{ n_experts_u, d_ff_u, s_num_groups_u };
                moe_weights.up_s = mlx_graph.mlx_persistent_reshape(up_s_4d, &up_s_shape, 3);

                if (e0.gate_up_bias) |b0| {
                    const fused_bias_shape_i64 = [_]i64{ @intCast(n_experts_u), @intCast(d_ff_times_2_u) };
                    const bias_ptr = @as([*]const f32, @ptrCast(b0.ptr));
                    const fused_bias = mlx_graph.createArrayF32(bias_ptr[0 .. b0.len * num_experts], &fused_bias_shape_i64);

                    // Reshape [E, 2*D] -> [E, D, 2] then slice
                    const bias_reshaped_shape = [_]usize{ n_experts_u, d_ff_u, 2 };
                    const reshaped_bias = mlx_graph.mlx_lazy_reshape(fused_bias, &bias_reshaped_shape, 3);

                    const bias_gate_start = [_]c_int{ 0, 0, 0 };
                    const bias_gate_end = [_]c_int{ n_experts, d_ff, 1 };
                    const gate_bias_3d = mlx_graph.mlx_lazy_slice(reshaped_bias, &bias_gate_start, &bias_gate_end, 3);
                    const bias_shape = [_]usize{ n_experts_u, d_ff_u };
                    moe_weights.gate_bias = mlx_graph.mlx_persistent_reshape(gate_bias_3d, &bias_shape, 2);

                    const bias_up_start = [_]c_int{ 0, 0, 1 };
                    const bias_up_end = [_]c_int{ n_experts, d_ff, 2 };
                    const up_bias_3d = mlx_graph.mlx_lazy_slice(reshaped_bias, &bias_up_start, &bias_up_end, 3);
                    moe_weights.up_bias = mlx_graph.mlx_persistent_reshape(up_bias_3d, &bias_shape, 2);
                }
            }

            // Down projection (MXFP4) - uses already-loaded expert weights.
            if (e0.down_proj.n_dims != 2) return error.InvalidShape;
            const down_rows: usize = @intCast(e0.down_proj.shape[0]);
            const down_packed_dim: usize = @intCast(@divExact(e0.down_proj.shape[1], 4));
            const down_shape_i64 = [_]i64{ @intCast(num_experts), @intCast(down_rows), @intCast(down_packed_dim) };
            moe_weights.down_w = mlx_graph.createArrayU32Unaligned(
                @as([*]align(1) const u32, @ptrCast(e0.down_proj.data_ptr)),
                (e0.down_proj.data_size * num_experts) / 4,
                &down_shape_i64,
            );
            const down_sc0 = e0.down_scales orelse return error.MissingScales;
            const down_groups: usize = down_sc0.len / down_rows;
            const down_scales_shape = [_]usize{ num_experts, down_rows, down_groups };
            moe_weights.down_s = mlx_graph.mlx_array_from_uint8(down_sc0.ptr, &down_scales_shape, 3);
            if (e0.down_bias) |b0| {
                const bias_shape_i64 = [_]i64{ @intCast(num_experts), @intCast(down_rows) };
                const bias_ptr = @as([*]const f32, @ptrCast(b0.ptr));
                moe_weights.down_bias = mlx_graph.createArrayF32(bias_ptr[0 .. b0.len * num_experts], &bias_shape_i64);
            }

            handles.layers[i].moe = moe_weights;
        }
    }

    // Load final layer norm - in native dtype (bf16, f16, or f32 for GGUF)
    var ln_final_arr = loadNormWeight(&loaded.ln_final);
    // Gemma3 uses (1 + weight) for RMSNorm
    if (handles.is_gemma3) {
        ln_final_arr = mlx_graph.mlx_add_one(ln_final_arr);
    }
    handles.ln_final = ln_final_arr;

    // Load LM head
    handles.lm_head_quantized = null;
    handles.lm_head = null;
    if (is_quantized) {
        // Quantized model - keep lm_head quantized
        if (loaded.lm_head.dtype == .grouped_affine_u4 or loaded.lm_head.dtype == .grouped_affine_u8) {
            const lm_bits: usize = if (loaded.lm_head.dtype == .grouped_affine_u8) 8 else 4;
            const qw = try loadQuantizedWeight(&loaded.lm_head, lm_bits);
            const qw_ptr = try allocator.create(WeightHandles.QuantizedWeight);
            qw_ptr.* = qw;
            handles.lm_head_quantized = qw_ptr;
        } else {
            // Quantized model but non-quantized lm_head
            const lm_head_data = loaded.lm_head.asSlice(f32);
            const lm_head_shape = loaded.lm_head.shape;
            handles.lm_head = mlx_graph.createArrayF32(
                lm_head_data,
                lm_head_shape[0..@as(usize, @intCast(loaded.lm_head.n_dims))],
            );
        }
    } else {
        // Non-quantized model - use the already-loaded lm_head tensor.
        const lm_shape = loaded.lm_head.shape[0..@as(usize, @intCast(loaded.lm_head.n_dims))];
        switch (loaded.lm_head.dtype) {
            .bf16 => {
                const lm_len = loaded.lm_head.data_size / 2;
                const lm_ptr: [*]align(1) const u16 = @ptrCast(loaded.lm_head.data_ptr);
                handles.lm_head = mlx_graph.createArrayBF16Unaligned(lm_ptr, lm_len, lm_shape);
            },
            .f16 => {
                const lm_len = loaded.lm_head.data_size / 2;
                const lm_ptr: [*]align(1) const u16 = @ptrCast(loaded.lm_head.data_ptr);
                handles.lm_head = mlx_graph.createArrayF16Unaligned(lm_ptr, lm_len, lm_shape);
            },
            .f32 => {
                handles.lm_head = mlx_graph.createArrayF32(loaded.lm_head.asSlice(f32), lm_shape);
            },
            else => return error.InvalidTensorType,
        }
    }

    // Initialize compiled layers to null (will be compiled on first use or via compileLayersForFusion)
    handles.compiled_layers = null;

    // Initialize fused model to null (will be created via createFusedModel)
    handles.fused_model = null;

    return handles;
}

/// Create fully fused model for decode (all 28 layers in one C++ call)
/// This eliminates ALL FFI overhead during decode - huge performance win!
/// Supports both quantized (4-bit/8-bit) and dense (BF16) models.
pub fn createFusedModel(allocator: std.mem.Allocator, weights: *WeightHandles, config: anytype) !void {
    if (weights.fused_model != null) return; // Already created
    if (weights.dense_model != null) return; // Already created dense

    // MoE models don't support fused model optimization (yet)
    if (weights.is_moe) return;

    const n_layers: usize = @intCast(config.n_layers);
    const n_heads: usize = @intCast(config.n_heads);
    const n_kv_heads: usize = @intCast(config.n_kv_groups);
    const head_dim: usize = @intCast(config.head_dim);
    const hidden_dim: usize = @intCast(config.d_model);

    if (weights.is_quantized) {
        // QUANTIZED PATH: Use FusedModelWeights with quantized_matmul
        const group_size = weights.layers[0].q_proj.?.group_size;
        const bits = weights.layers[0].q_proj.?.bits;

        const fused = mlx_graph.mlx_fused_model_create(
            n_layers,
            n_heads,
            n_kv_heads,
            head_dim,
            hidden_dim,
            group_size,
            bits,
            config.rope_theta,
            config.norm_eps,
        );

        // Set embeddings (must be quantized for fused model)
        if (weights.embed_tokens_quantized) |qw| {
            mlx_graph.mlx_fused_model_set_embeddings(fused, qw.weights, qw.scales, qw.biases);
        } else {
            return error.FusedModelRequiresQuantizedEmbeddings;
        }

        // Set final weights
        if (weights.lm_head_quantized) |qw| {
            mlx_graph.mlx_fused_model_set_final(fused, weights.ln_final, qw.weights, qw.scales, qw.biases);
        } else {
            return error.FusedModelRequiresQuantizedLMHead;
        }

        // Set per-layer weights
        for (weights.layers, 0..) |*layer, i| {
            mlx_graph.mlx_fused_model_set_layer(
                fused,
                i,
                layer.ln1_weight,
                layer.q_proj.?.weights,
                layer.q_proj.?.scales,
                layer.q_proj.?.biases,
                layer.k_proj.?.weights,
                layer.k_proj.?.scales,
                layer.k_proj.?.biases,
                layer.v_proj.?.weights,
                layer.v_proj.?.scales,
                layer.v_proj.?.biases,
                layer.o_proj.?.weights,
                layer.o_proj.?.scales,
                layer.o_proj.?.biases,
                layer.ln2_weight,
                layer.w1.?.weights, // gate
                layer.w1.?.scales,
                layer.w1.?.biases,
                layer.w3.?.weights, // up
                layer.w3.?.scales,
                layer.w3.?.biases,
                layer.w2.?.weights, // down
                layer.w2.?.scales,
                layer.w2.?.biases,
                if (layer.q_norm) |qn| qn else null,
                if (layer.k_norm) |kn| kn else null,
                if (layer.pre_ffn_norm) |n| n else null,
                if (layer.post_ffn_norm) |n| n else null,
            );
        }

        weights.fused_model = fused;

        // Set Gemma3 config if this is a Gemma3 model
        if (weights.is_gemma3) {
            mlx_graph.mlx_fused_model_set_gemma3_config(
                fused,
                true,
                config.use_gelu,
                config.query_pre_attn_scalar,
            );
        }

        // Set Granite config if this is a Granite model
        if (weights.is_granite) {
            mlx_graph.mlx_fused_model_set_granite_config(
                fused,
                true,
                config.embedding_multiplier,
                config.attention_multiplier,
                config.residual_multiplier,
                config.logits_scaling,
            );
        }

        // Set Llama3 RoPE frequencies if configured
        if (config.rope_scaling.rope_type == .llama3) {
            std.log.info("Setting Llama3 RoPE frequencies (factor={d}, low_freq={d}, high_freq={d})", .{
                config.rope_scaling.factor,
                config.rope_scaling.low_freq_factor,
                config.rope_scaling.high_freq_factor,
            });
            const freqs = computeLlama3RopeFreqs(
                allocator,
                @intCast(config.head_dim),
                config.rope_theta,
                config.rope_scaling.factor,
                config.rope_scaling.low_freq_factor,
                config.rope_scaling.high_freq_factor,
                @intCast(config.rope_scaling.original_max_position_embeddings),
            ) catch {
                std.log.warn("Failed to compute Llama3 RoPE frequencies, using standard RoPE", .{});
                return;
            };
            defer allocator.free(freqs);
            std.log.info("Computed {d} rope frequencies, first={d}, last={d}", .{
                freqs.len,
                freqs[0],
                freqs[freqs.len - 1],
            });
            const freqs_array = mlx_graph.createArrayF32(freqs, &[_]i64{@intCast(freqs.len)});
            mlx_graph.mlx_fused_model_set_rope_freqs(fused, freqs_array);
        }

        // Pre-evaluate all weights to ensure GPU transfer happens upfront
        mlx_graph.mlx_fused_model_optimize(fused);
    } else {
        // DENSE PATH: Use FusedDenseModel with dense matmul (BF16)
        const dense = mlx_graph.mlx_dense_model_create(
            n_layers,
            n_heads,
            n_kv_heads,
            head_dim,
            hidden_dim,
            config.rope_theta,
            config.norm_eps,
        );

        // Set embeddings (BF16)
        if (weights.embed_tokens) |et| {
            mlx_graph.mlx_dense_model_set_embeddings(dense, et);
        } else {
            return error.DenseModelRequiresEmbeddings;
        }

        // Set final weights (BF16)
        if (weights.lm_head) |lmh| {
            mlx_graph.mlx_dense_model_set_final(dense, weights.ln_final, lmh);
        } else {
            return error.DenseModelRequiresLMHead;
        }

        // Set per-layer weights (BF16)
        for (weights.layers, 0..) |*layer, i| {
            mlx_graph.mlx_dense_model_set_layer(
                dense,
                i,
                layer.ln1_weight,
                layer.q_proj_bf16.?,
                layer.k_proj_bf16.?,
                layer.v_proj_bf16.?,
                layer.o_proj_bf16.?,
                layer.ln2_weight,
                layer.w1_bf16.?, // gate
                layer.w3_bf16.?, // up
                layer.w2_bf16.?, // down
                if (layer.q_norm) |qn| qn else null,
                if (layer.k_norm) |kn| kn else null,
            );
        }

        weights.dense_model = dense;
    }
}

/// Free all GPU weight handles
pub fn freeWeights(allocator: std.mem.Allocator, handles: *WeightHandles) void {
    if (handles.embed_tokens) |et| {
        mlx_graph.freeArray(et);
    }
    if (handles.embed_tokens_quantized) |qw| {
        freeQuantizedWeight(qw.*);
        allocator.destroy(qw);
    }

    for (handles.layers) |*layer| {
        mlx_graph.freeArray(layer.ln1_weight);
        // Free quantized weights if present
        if (layer.q_proj) |qw| freeQuantizedWeight(qw);
        if (layer.k_proj) |qw| freeQuantizedWeight(qw);
        if (layer.v_proj) |qw| freeQuantizedWeight(qw);
        if (layer.o_proj) |qw| freeQuantizedWeight(qw);
        // Free BF16 weights if present
        if (layer.q_proj_bf16) |h| mlx_graph.freeArray(h);
        if (layer.k_proj_bf16) |h| mlx_graph.freeArray(h);
        if (layer.v_proj_bf16) |h| mlx_graph.freeArray(h);
        if (layer.o_proj_bf16) |h| mlx_graph.freeArray(h);
        mlx_graph.freeArray(layer.ln2_weight);
        // FFN quantized
        if (layer.w1) |qw| freeQuantizedWeight(qw);
        if (layer.w2) |qw| freeQuantizedWeight(qw);
        if (layer.w3) |qw| freeQuantizedWeight(qw);
        // FFN BF16
        if (layer.w1_bf16) |h| mlx_graph.freeArray(h);
        if (layer.w2_bf16) |h| mlx_graph.freeArray(h);
        if (layer.w3_bf16) |h| mlx_graph.freeArray(h);
        if (layer.q_norm) |qn| mlx_graph.freeArray(qn);
        if (layer.k_norm) |kn| mlx_graph.freeArray(kn);
    }
    allocator.free(handles.layers);

    mlx_graph.freeArray(handles.ln_final);
    if (handles.lm_head) |lh| mlx_graph.freeArray(lh);
    if (handles.lm_head_quantized) |qw| {
        freeQuantizedWeight(qw.*);
        allocator.destroy(qw);
    }

    // Free fused model if created
    if (handles.fused_model) |fm| {
        mlx_graph.mlx_fused_model_free(fm);
    }
    // Free dense model if created
    if (handles.dense_model) |dm| {
        mlx_graph.mlx_dense_model_free(dm);
    }

    allocator.destroy(handles);
}

fn loadQuantizedWeight(tensor: *const Tensor, bits: usize) !WeightHandles.QuantizedWeight {
    const gaffine_meta = tensor.gaffine orelse return error.NotQuantized;

    // Weights are packed uint32
    // Note: tensor.shape has been modified to unpacked dimensions by model_loader
    // We need to reconstruct the packed shape from the actual data
    // Use align(1) pointer cast - data may be unaligned from mmap
    const w_data = @as([*]align(1) const u32, @ptrCast(tensor.data_ptr));
    const w_len = tensor.data_size / @sizeOf(u32);

    // Packed shape: [n, k/8] for 4-bit, [n, k/4] for 8-bit (8 or 4 values per u32)
    const n: usize = @intCast(tensor.shape[0]);
    const k_packed = w_len / n; // Calculate from actual data
    const packed_shape = [_]usize{ n, k_packed };

    // Call extern directly with unaligned pointer
    const weights = mlx_graph.mlx_array_from_uint32(
        w_data,
        &packed_shape,
        2,
    );

    // Scales and biases are f16/bf16 (stored as u16)
    // MLX quantized_matmul expects 2D: [n, k_unpacked/group_size]
    // Weight is packed: packed_shape[1] * 32 / bits = unpacked dimension
    const k_unpacked = k_packed * 32 / bits;
    const n_groups = k_unpacked / gaffine_meta.group_size;

    // Use align(1) for scales/biases too - mmap data may be unaligned
    const scales_data = @as([*]align(1) const u16, @ptrCast(gaffine_meta.scales.ptr));
    const scales_shape = [_]usize{ n, n_groups };

    // Use correct dtype (F16 or BF16) based on model
    const scales = if (gaffine_meta.scales_dtype == .f16)
        mlx_graph.mlx_array_from_float16(scales_data, &scales_shape, 2)
    else
        mlx_graph.mlx_array_from_bfloat16(scales_data, &scales_shape, 2);

    const biases_data = @as([*]align(1) const u16, @ptrCast(gaffine_meta.biases.ptr));
    const biases = if (gaffine_meta.scales_dtype == .f16)
        mlx_graph.mlx_array_from_float16(biases_data, &scales_shape, 2)
    else
        mlx_graph.mlx_array_from_bfloat16(biases_data, &scales_shape, 2);

    return .{
        .weights = weights,
        .scales = scales,
        .biases = biases,
        .group_size = gaffine_meta.group_size,
        .bits = bits,
    };
}

fn freeQuantizedWeight(qw: WeightHandles.QuantizedWeight) void {
    mlx_graph.freeArray(qw.weights);
    mlx_graph.freeArray(qw.scales);
    mlx_graph.freeArray(qw.biases);
}

/// Compile all transformer layers for fusion optimization
/// Call this ONCE after loadWeightsToGPU for maximum performance
/// NOTE: Only works for quantized models. BF16 models skip compilation.
pub fn compileLayersForFusion(allocator: std.mem.Allocator, handles: *WeightHandles, config: anytype) !void {
    if (handles.compiled_layers != null) return; // Already compiled
    if (!handles.is_quantized) return; // BF16 models don't use compiled layers

    const n_heads: usize = @intCast(config.n_heads);
    const n_kv_heads: usize = @intCast(config.n_kv_groups);
    const head_dim: usize = @intCast(config.head_dim);
    const hidden_dim: usize = @intCast(config.d_model);
    const norm_eps = config.norm_eps;
    const rope_theta = config.rope_theta;

    const compiled = try allocator.alloc(mlx_graph.CompiledLayer, handles.layers.len);
    errdefer allocator.free(compiled);

    for (handles.layers, 0..) |*layer, i| {
        const handle = mlx_graph.mlx_compile_layer(
            layer.q_proj.?.weights,
            layer.q_proj.?.scales,
            layer.q_proj.?.biases,
            layer.k_proj.?.weights,
            layer.k_proj.?.scales,
            layer.k_proj.?.biases,
            layer.v_proj.?.weights,
            layer.v_proj.?.scales,
            layer.v_proj.?.biases,
            layer.o_proj.?.weights,
            layer.o_proj.?.scales,
            layer.o_proj.?.biases,
            layer.w1.?.weights,
            layer.w1.?.scales,
            layer.w1.?.biases, // gate
            layer.w3.?.weights,
            layer.w3.?.scales,
            layer.w3.?.biases, // up
            layer.w2.?.weights,
            layer.w2.?.scales,
            layer.w2.?.biases, // down
            layer.ln1_weight,
            layer.ln2_weight,
            layer.q_norm orelse null,
            layer.k_norm orelse null,
            n_heads,
            n_kv_heads,
            head_dim,
            hidden_dim,
            layer.q_proj.?.group_size,
            layer.q_proj.?.bits,
            rope_theta,
            norm_eps,
        );
        compiled[i] = .{ .handle = handle };
    }

    handles.compiled_layers = compiled;
}

/// Weight handles - weights loaded as MLX arrays, kept on GPU
pub const WeightHandles = struct {
    // Embeddings (either quantized, bf16, or f32)
    embed_tokens: ?ArrayHandle, // f32/bf16 embeddings
    embed_tokens_quantized: ?*QuantizedWeight, // Quantized embeddings

    // Per-layer weights
    layers: []LayerWeights,

    // Compiled layer functions (for fusion optimization)
    compiled_layers: ?[]mlx_graph.CompiledLayer,

    // Fully fused model (all layers in one C++ call - ZERO FFI overhead)
    fused_model: mlx_graph.FusedModelHandle,
    // Dense model for BF16 weights (non-quantized)
    dense_model: mlx_graph.DenseModelHandle = null,

    // Final
    ln_final: ArrayHandle,
    lm_head: ?ArrayHandle, // F32/BF16 lm_head
    lm_head_quantized: ?*QuantizedWeight, // Quantized lm_head

    // Track if model is quantized (affects which forward path to use)
    is_quantized: bool = true,

    // MoE configuration
    is_moe: bool = false,
    num_experts: usize = 0,
    experts_per_token: usize = 0,

    // Gemma3 configuration
    is_gemma3: bool = false,
    d_model: usize = 0, // For embedding scaling

    // Granite configuration (scaling multipliers)
    is_granite: bool = false,
    embedding_multiplier: f32 = 1.0,
    attention_multiplier: f32 = 0.0, // 0 means use default 1/sqrt(head_dim)
    residual_multiplier: f32 = 1.0,
    logits_scaling: f32 = 1.0,

    /// MoE weight structure for MXFP4 quantized experts
    /// Supports both MLX format (quantized router, separate gate/up) and
    /// HuggingFace/OpenAI format (BF16 router, fused gate_up)
    pub const MoEWeights = struct {
        // Router weights
        // For MLX format: 8-bit affine quantized (router_w=U32, router_s/router_b=BF16)
        // For HF format: BF16 unquantized (router_w=BF16, router_s/router_b=null)
        router_w: ArrayHandle,
        router_s: ?ArrayHandle = null, // null for BF16 router
        router_b: ?ArrayHandle = null, // null for BF16 router
        router_bias: ?ArrayHandle = null, // Optional linear layer bias

        // Expert weights (MXFP4) - separate gate/up/down
        gate_w: ArrayHandle, // [num_experts, d_ff, packed_dim]
        gate_s: ArrayHandle, // scales
        up_w: ArrayHandle,
        up_s: ArrayHandle,
        down_w: ArrayHandle,
        down_s: ArrayHandle,

        // Expert biases (optional)
        gate_bias: ?ArrayHandle = null, // [num_experts, d_ff]
        up_bias: ?ArrayHandle = null,
        down_bias: ?ArrayHandle = null,

        router_group_size: usize = 64, // 64 for 8-bit router
        expert_group_size: usize = 32, // 32 for MXFP4
        num_experts: usize,
        experts_per_token: usize,
    };

    pub const LayerWeights = struct {
        ln1_weight: ArrayHandle,
        // Quantized weights (grouped-affine u4/u8)
        q_proj: ?QuantizedWeight = null,
        k_proj: ?QuantizedWeight = null,
        v_proj: ?QuantizedWeight = null,
        o_proj: ?QuantizedWeight = null,
        // Linear biases for attention (gpt-oss and similar)
        q_bias: ?ArrayHandle = null,
        k_bias: ?ArrayHandle = null,
        v_bias: ?ArrayHandle = null,
        o_bias: ?ArrayHandle = null,
        // Attention sinks (gpt-oss) - per-head scaling for attention
        attn_sinks: ?ArrayHandle = null,
        // BF16 weights (non-quantized)
        q_proj_bf16: ?ArrayHandle = null,
        k_proj_bf16: ?ArrayHandle = null,
        v_proj_bf16: ?ArrayHandle = null,
        o_proj_bf16: ?ArrayHandle = null,
        ln2_weight: ArrayHandle,
        // FFN - quantized
        w1: ?QuantizedWeight = null,
        w2: ?QuantizedWeight = null,
        w3: ?QuantizedWeight = null,
        // FFN - BF16
        w1_bf16: ?ArrayHandle = null,
        w2_bf16: ?ArrayHandle = null,
        w3_bf16: ?ArrayHandle = null,
        // QK normalization (Qwen3 specific) - optional
        q_norm: ?ArrayHandle = null,
        k_norm: ?ArrayHandle = null,
        // Gemma3 FFN norms (4 norms per block) - optional
        pre_ffn_norm: ?ArrayHandle = null,
        post_ffn_norm: ?ArrayHandle = null,
        // Track if this layer is quantized
        is_quantized: bool = true,
        // MoE weights (for MoE models, replaces w1/w2/w3)
        moe: ?*MoEWeights = null,
    };

    pub const QuantizedWeight = struct {
        weights: ArrayHandle, // Packed uint32
        scales: ArrayHandle, // BF16
        biases: ArrayHandle, // BF16
        group_size: usize,
        bits: usize,
    };
};

/// MLX-native transformer forward pass using LAZY GRAPH API
/// Following test_mlx_single.py pattern exactly
/// Returns handle to logits array (still on GPU!)
pub fn transformerForwardLazy(
    allocator: std.mem.Allocator,
    weights: *const WeightHandles,
    input_ids: []const u32,
    config: anytype,
    cache: ?Cache,
    pos_offset: usize,
    use_compiled: bool,
) !ArrayHandle {
    if (builtin.os.tag != .macos) {
        return error.MLXNotAvailable;
    }

    // NOTE: Tracing requires forcing evaluation of intermediate values. This is unsafe for the
    // Metal backend when a KV cache is enabled, because the fused attention primitive updates the
    // cache as a side effect. Evaluating mid-graph can therefore mutate the cache multiple times.
    var trace = std.posix.getenv("TOKAMINO_TRACE_METAL_UNSAFE") != null;
    if (trace and cache != null) trace = false;
    const phase: []const u8 = if (input_ids.len == 1) "decode" else "prefill";

    // NOTE: Don't call mlx_pool_reset() here - arrays from previous tokens must stay valid
    // Pool reset should only happen at the START of a full generation sequence

    const n_heads: usize = @intCast(config.n_heads);
    const n_kv_heads: usize = @intCast(config.n_kv_groups);
    const head_dim: usize = @intCast(config.head_dim);
    const norm_eps = config.norm_eps;
    const n_layers: usize = @intCast(config.n_layers);
    const seq_len = input_ids.len;
    const use_compiled_effective = use_compiled and !trace;

    // >>> LAZY: embedding lookup
    var hidden: ArrayHandle = undefined;
    if (weights.embed_tokens_quantized) |qw| {
        // Quantized embedding lookup: take rows, then dequantize
        // Create 1D indices array
        const indices_data = input_ids.ptr;
        const indices_len = seq_len;

        // 1. Take quantized weight rows
        const qw_rows = mlx_graph.mlx_lazy_embedding(qw.weights, indices_data, indices_len);
        // 2. Take corresponding scales
        const scales_rows = mlx_graph.mlx_lazy_embedding(qw.scales, indices_data, indices_len);
        // 3. Take corresponding biases
        const biases_rows = mlx_graph.mlx_lazy_embedding(qw.biases, indices_data, indices_len);

        // 4. Dequantize the rows
        hidden = mlx_graph.mlx_lazy_dequantize(qw_rows, scales_rows, biases_rows, qw.group_size, qw.bits);
    } else {
        // F32 embedding lookup
        hidden = mlx_graph.mlx_lazy_embedding(
            weights.embed_tokens.?,
            input_ids.ptr,
            seq_len,
        );
    }

    // Embedding scaling:
    // - Granite: multiply by embedding_multiplier (e.g., 12.0)
    // - Gemma3: multiply by sqrt(hidden_dim)
    if (weights.is_granite and weights.embedding_multiplier != 1.0) {
        hidden = mlx_graph.mlx_lazy_multiply_scalar(hidden, weights.embedding_multiplier);
    } else if (weights.is_gemma3) {
        hidden = mlx_graph.mlx_scale_by_sqrt(hidden, @intCast(weights.d_model));
    }

    if (trace) {
        try traceLastHiddenVector(allocator, "metal", phase, null, hidden, seq_len, @intCast(weights.d_model));
    }

    // NOTE: Causal mask is now computed inside fused attention in C++

    // Process each transformer layer
    // DEBUG: Track if we're using fusion
    var used_fusion: bool = false;

    for (0..n_layers) |layer_idx| {
        // *** FUSION OPTIMIZATION: Use compiled layer only for decode (seq_len == 1) ***
        if (use_compiled_effective and weights.compiled_layers != null and seq_len == 1) {
            const compiled = weights.compiled_layers.?;
            used_fusion = true;

            // Compiled layer mutates cache internally (matches Python mlx_lm)
            if (cache) |c| {
                if (c.use_bfloat16) {
                    hidden = compiled[layer_idx].forward(hidden, c.handle, layer_idx, pos_offset);
                } else {
                    // Quantized cache not supported with fusion yet - fall through to manual path
                    used_fusion = false;
                }
            } else {
                // No cache - use compiled layer without cache
                hidden = compiled[layer_idx].forward(hidden, null, layer_idx, pos_offset);
            }

            if (used_fusion) {
                if (trace) {
                    try traceLastHiddenVector(allocator, "metal", phase, layer_idx, hidden, seq_len, @intCast(weights.d_model));
                }
                continue; // Skip manual graph building
            }
        }

        // *** Use fused operations for maximum performance ***
        const layer_weights = weights.layers[layer_idx];

        // 1. >>> LAZY: RMS norm (attention input)
        const normed = mlx_graph.mlx_lazy_rms_norm(
            hidden,
            layer_weights.ln1_weight,
            norm_eps,
        );

        // 2-10. >>> LAZY: Fused attention block
        // Single FFI call for: Q/K/V proj -> reshape -> transpose -> QK norm -> RoPE -> cache -> attention -> output proj
        const attn_proj = if (layer_weights.is_quantized) blk: {
            // Quantized path
            const cache_handle = if (cache) |c| c.handle else null;
            break :blk mlx_graph.mlx_lazy_fused_attention(
                normed,
                layer_weights.q_proj.?.weights,
                layer_weights.q_proj.?.scales,
                layer_weights.q_proj.?.biases,
                layer_weights.k_proj.?.weights,
                layer_weights.k_proj.?.scales,
                layer_weights.k_proj.?.biases,
                layer_weights.v_proj.?.weights,
                layer_weights.v_proj.?.scales,
                layer_weights.v_proj.?.biases,
                layer_weights.o_proj.?.weights,
                layer_weights.o_proj.?.scales,
                layer_weights.o_proj.?.biases,
                if (layer_weights.q_norm) |qn| qn else null,
                if (layer_weights.k_norm) |kn| kn else null,
                // Linear biases (optional, for gpt-oss and similar)
                if (layer_weights.q_bias) |b| b else null,
                if (layer_weights.k_bias) |b| b else null,
                if (layer_weights.v_bias) |b| b else null,
                if (layer_weights.o_bias) |b| b else null,
                // Attention sinks (optional, for gpt-oss)
                if (layer_weights.attn_sinks) |s| s else null,
                cache_handle,
                layer_idx,
                n_heads,
                n_kv_heads,
                head_dim,
                pos_offset,
                config.rope_theta,
                norm_eps,
                layer_weights.q_proj.?.group_size,
                layer_weights.q_proj.?.bits,
                config.query_pre_attn_scalar,
                weights.attention_multiplier,
            );
        } else blk: {
            // BF16 path - use non-quantized fused attention
            const cache_handle = if (cache) |c| c.handle else null;
            break :blk mlx_graph.mlx_lazy_fused_attention_bf16(
                normed,
                layer_weights.q_proj_bf16.?,
                layer_weights.k_proj_bf16.?,
                layer_weights.v_proj_bf16.?,
                layer_weights.o_proj_bf16.?,
                if (layer_weights.q_norm) |qn| qn else null,
                if (layer_weights.k_norm) |kn| kn else null,
                // Linear biases (optional, for gpt-oss and similar)
                if (layer_weights.q_bias) |b| b else null,
                if (layer_weights.k_bias) |b| b else null,
                if (layer_weights.v_bias) |b| b else null,
                if (layer_weights.o_bias) |b| b else null,
                // Attention sinks (optional, for gpt-oss)
                if (layer_weights.attn_sinks) |s| s else null,
                cache_handle,
                layer_idx,
                n_heads,
                n_kv_heads,
                head_dim,
                pos_offset,
                config.rope_theta,
                norm_eps,
                config.query_pre_attn_scalar,
                weights.attention_multiplier,
            );
        };

        // 11. >>> LAZY: Residual connection
        // For Gemma3: apply post_attention_layernorm to attn output before residual
        const attn_for_residual = if (weights.is_gemma3)
            mlx_graph.mlx_lazy_rms_norm(attn_proj, layer_weights.ln2_weight, norm_eps)
        else
            attn_proj;
        // Granite: scale layer output by residual_multiplier before adding to residual
        const scaled_attn = if (weights.is_granite and weights.residual_multiplier != 1.0)
            mlx_graph.mlx_lazy_multiply_scalar(attn_for_residual, weights.residual_multiplier)
        else
            attn_for_residual;
        const hidden_1 = mlx_graph.mlx_lazy_add(hidden, scaled_attn);

        // 12. >>> LAZY: Second RMS norm (pre-FFN)
        // For Gemma3: use pre_ffn_norm, otherwise use ln2_weight
        const normed_2 = if (weights.is_gemma3 and layer_weights.pre_ffn_norm != null)
            mlx_graph.mlx_lazy_rms_norm(hidden_1, layer_weights.pre_ffn_norm.?, norm_eps)
        else
            mlx_graph.mlx_lazy_rms_norm(hidden_1, layer_weights.ln2_weight, norm_eps);

        // 13-15. >>> LAZY: FFN (dense or MoE)
        const ffn_out = if (layer_weights.moe) |moe| blk: {
            // MoE path: router -> topk -> gather_qmm -> weighted sum
            break :blk mlx_graph.mlx_lazy_fused_moe_ffn_mxfp4(
                normed_2,
                // Router weights (8-bit affine or BF16)
                moe.router_w,
                if (moe.router_s) |rs| rs else null, // null for BF16 router
                if (moe.router_b) |rb| rb else null, // null for BF16 router
                if (moe.router_bias) |rb| rb else null, // Unwrap optional
                // Expert weights (MXFP4) - separate gate/up/down
                moe.gate_w,
                moe.gate_s,
                moe.up_w,
                moe.up_s,
                moe.down_w,
                moe.down_s,
                // Expert biases (unwrap optionals)
                if (moe.gate_bias) |gb| gb else null,
                if (moe.up_bias) |ub| ub else null,
                if (moe.down_bias) |db| db else null,
                // Config
                moe.num_experts,
                moe.experts_per_token,
                moe.router_group_size,
                moe.expert_group_size,
            );
        } else if (layer_weights.is_quantized) blk: {
            // Quantized dense FFN path
            break :blk mlx_graph.mlx_lazy_fused_ffn(
                normed_2,
                layer_weights.w1.?.weights, // gate
                layer_weights.w1.?.scales,
                layer_weights.w1.?.biases,
                layer_weights.w3.?.weights, // up
                layer_weights.w3.?.scales,
                layer_weights.w3.?.biases,
                layer_weights.w2.?.weights, // down
                layer_weights.w2.?.scales,
                layer_weights.w2.?.biases,
                layer_weights.w1.?.group_size,
                layer_weights.w1.?.bits,
                weights.is_gemma3, // use_gelu for Gemma3
            );
        } else blk: {
            // BF16 dense FFN path
            break :blk mlx_graph.mlx_lazy_fused_ffn_bf16(
                normed_2,
                layer_weights.w1_bf16.?, // gate
                layer_weights.w3_bf16.?, // up
                layer_weights.w2_bf16.?, // down
            );
        };

        // 16. >>> LAZY: Final residual
        // For Gemma3: apply post_feedforward_layernorm to FFN output before residual
        const ffn_for_residual = if (weights.is_gemma3 and layer_weights.post_ffn_norm != null)
            mlx_graph.mlx_lazy_rms_norm(ffn_out, layer_weights.post_ffn_norm.?, norm_eps)
        else
            ffn_out;
        // Granite: scale layer output by residual_multiplier before adding to residual
        const scaled_ffn = if (weights.is_granite and weights.residual_multiplier != 1.0)
            mlx_graph.mlx_lazy_multiply_scalar(ffn_for_residual, weights.residual_multiplier)
        else
            ffn_for_residual;
        hidden = mlx_graph.mlx_lazy_add(hidden_1, scaled_ffn);

        if (trace) {
            try traceLastHiddenVector(allocator, "metal", phase, layer_idx, hidden, seq_len, @intCast(weights.d_model));
        }
    }

    // Final layer norm
    const final_normed = mlx_graph.mlx_lazy_rms_norm(
        hidden,
        weights.ln_final,
        norm_eps,
    );

    // LM head projection
    const logits = if (weights.lm_head_quantized) |qw| blk: {
        // Use quantized matmul (lm_head already in correct orientation for transpose=true)
        break :blk mlx_graph.mlx_lazy_quantized_matmul(
            final_normed,
            qw.weights,
            qw.scales,
            qw.biases,
            qw.group_size,
            qw.bits,
            true, // transpose
        );
    } else blk: {
        // F32 matmul - need to transpose
        const transpose_axes = [_]usize{ 1, 0 };
        const lm_head_t = mlx_graph.mlx_lazy_transpose(weights.lm_head.?, &transpose_axes, 2);
        break :blk mlx_graph.mlx_lazy_matmul(final_normed, lm_head_t);
    };

    // Granite: divide logits by logits_scaling (not multiply!)
    const scaled_logits = if (weights.is_granite and weights.logits_scaling != 1.0)
        mlx_graph.mlx_lazy_multiply_scalar(logits, 1.0 / weights.logits_scaling)
    else
        logits;

    // Return handle - DON'T eval() yet, DON'T copy to CPU yet!
    // Caller will eval() and copy
    return scaled_logits;
}

fn traceLastHiddenVector(
    allocator: std.mem.Allocator,
    comptime backend: []const u8,
    phase: []const u8,
    layer: ?usize,
    hidden: mlx_graph.ArrayHandle,
    seq_len: usize,
    d_model: usize,
) !void {
    if (seq_len == 0) return;

    // Slice [B=1, L, D] -> [1,1,D].
    var starts: [3]c_int = .{ 0, @intCast(seq_len - 1), 0 };
    var ends: [3]c_int = .{ 1, @intCast(seq_len), @intCast(d_model) };
    const slice = mlx_graph.mlx_lazy_slice(hidden, &starts, &ends, 3);
    defer mlx_graph.freeArray(slice);

    // Reshape -> [D].
    var shape: [1]usize = .{d_model};
    const flat = mlx_graph.mlx_lazy_reshape(slice, &shape, 1);
    defer mlx_graph.freeArray(flat);

    mlx_graph.eval(&.{flat});

    const buf = try allocator.alloc(f32, d_model);
    defer allocator.free(buf);
    mlx_graph.copyToHost(flat, buf);

    var minv: f32 = buf[0];
    var maxv: f32 = buf[0];
    var sum: f64 = 0;
    var sumsq: f64 = 0;
    for (buf) |x| {
        if (x < minv) minv = x;
        if (x > maxv) maxv = x;
        sum += x;
        sumsq += @as(f64, x) * @as(f64, x);
    }
    const mean: f64 = sum / @as(f64, @floatFromInt(buf.len));
    const rms: f64 = @sqrt(sumsq / @as(f64, @floatFromInt(buf.len)));
    const a = buf[0];
    const b = if (buf.len > 1) buf[1] else 0;
    const c = if (buf.len > 2) buf[2] else 0;
    const d = if (buf.len > 3) buf[3] else 0;

    if (layer) |i| {
        std.debug.print("TRACE backend={s} phase={s} layer={} hidden_last min={d:.6} max={d:.6} mean={d:.6} rms={d:.6} first4=[{d:.6},{d:.6},{d:.6},{d:.6}]\n", .{
            backend, phase, i, minv, maxv, mean, rms, a, b, c, d,
        });
    } else {
        std.debug.print("TRACE backend={s} phase={s} layer=embed hidden_last min={d:.6} max={d:.6} mean={d:.6} rms={d:.6} first4=[{d:.6},{d:.6},{d:.6},{d:.6}]\n", .{
            backend, phase, minv, maxv, mean, rms, a, b, c, d,
        });
    }
}

/// Transformer forward pass with GPU token handle (for pipelined generation)
/// This allows building the graph lazily without waiting for the token value
/// Exactly mirrors transformerForwardLazy but uses mlx_lazy_embedding_from_array
pub fn transformerForwardFromGPUToken(
    allocator: std.mem.Allocator,
    weights: *const WeightHandles,
    token_handle: ArrayHandle, // GPU array with token index (from argmax)
    config: anytype,
    cache: ?Cache,
    pos_offset: usize,
) !ArrayHandle {
    if (builtin.os.tag != .macos) {
        return error.MLXNotAvailable;
    }

    // Same caveat as transformerForwardLazy: tracing is unsafe with KV cache side effects.
    var trace = std.posix.getenv("TOKAMINO_TRACE_METAL_UNSAFE") != null;
    if (trace and cache != null) trace = false;

    const n_heads: usize = @intCast(config.n_heads);
    const n_kv_heads: usize = @intCast(config.n_kv_groups);
    const head_dim: usize = @intCast(config.head_dim);
    const norm_eps = config.norm_eps;
    const n_layers: usize = @intCast(config.n_layers);

    // >>> LAZY: embedding lookup from GPU token handle
    var hidden: ArrayHandle = undefined;
    if (weights.embed_tokens_quantized) |qw| {
        // Quantized embedding: take rows then dequantize
        const qw_rows = mlx_graph.mlx_lazy_embedding_from_array(qw.weights, token_handle);
        const scales_rows = mlx_graph.mlx_lazy_embedding_from_array(qw.scales, token_handle);
        const biases_rows = mlx_graph.mlx_lazy_embedding_from_array(qw.biases, token_handle);
        hidden = mlx_graph.mlx_lazy_dequantize(qw_rows, scales_rows, biases_rows, qw.group_size, qw.bits);
    } else {
        hidden = mlx_graph.mlx_lazy_embedding_from_array(weights.embed_tokens.?, token_handle);
    }

    // Process each transformer layer (same as transformerForwardLazy)
    for (0..n_layers) |layer_idx| {
        const layer_weights = weights.layers[layer_idx];

        // 1. >>> LAZY: RMS norm (attention input)
        const normed = mlx_graph.mlx_lazy_rms_norm(
            hidden,
            layer_weights.ln1_weight,
            norm_eps,
        );

        // 2-10. >>> LAZY: Fused attention block
        const attn_proj = if (layer_weights.is_quantized) blk: {
            // Quantized path
            const cache_handle = if (cache) |c| c.handle else null;
            break :blk mlx_graph.mlx_lazy_fused_attention(
                normed,
                layer_weights.q_proj.?.weights,
                layer_weights.q_proj.?.scales,
                layer_weights.q_proj.?.biases,
                layer_weights.k_proj.?.weights,
                layer_weights.k_proj.?.scales,
                layer_weights.k_proj.?.biases,
                layer_weights.v_proj.?.weights,
                layer_weights.v_proj.?.scales,
                layer_weights.v_proj.?.biases,
                layer_weights.o_proj.?.weights,
                layer_weights.o_proj.?.scales,
                layer_weights.o_proj.?.biases,
                if (layer_weights.q_norm) |qn| qn else null,
                if (layer_weights.k_norm) |kn| kn else null,
                // Linear biases (optional, for gpt-oss and similar)
                if (layer_weights.q_bias) |b| b else null,
                if (layer_weights.k_bias) |b| b else null,
                if (layer_weights.v_bias) |b| b else null,
                if (layer_weights.o_bias) |b| b else null,
                // Attention sinks (optional, for gpt-oss)
                if (layer_weights.attn_sinks) |s| s else null,
                cache_handle,
                layer_idx,
                n_heads,
                n_kv_heads,
                head_dim,
                pos_offset,
                config.rope_theta,
                norm_eps,
                layer_weights.q_proj.?.group_size,
                layer_weights.q_proj.?.bits,
                config.query_pre_attn_scalar,
                weights.attention_multiplier,
            );
        } else blk: {
            // BF16 path - use non-quantized fused attention
            const cache_handle = if (cache) |c| c.handle else null;
            break :blk mlx_graph.mlx_lazy_fused_attention_bf16(
                normed,
                layer_weights.q_proj_bf16.?,
                layer_weights.k_proj_bf16.?,
                layer_weights.v_proj_bf16.?,
                layer_weights.o_proj_bf16.?,
                if (layer_weights.q_norm) |qn| qn else null,
                if (layer_weights.k_norm) |kn| kn else null,
                // Linear biases (optional, for gpt-oss and similar)
                if (layer_weights.q_bias) |b| b else null,
                if (layer_weights.k_bias) |b| b else null,
                if (layer_weights.v_bias) |b| b else null,
                if (layer_weights.o_bias) |b| b else null,
                // Attention sinks (optional, for gpt-oss)
                if (layer_weights.attn_sinks) |s| s else null,
                cache_handle,
                layer_idx,
                n_heads,
                n_kv_heads,
                head_dim,
                pos_offset,
                config.rope_theta,
                norm_eps,
                config.query_pre_attn_scalar,
                weights.attention_multiplier,
            );
        };

        // 11. >>> LAZY: Residual connection
        // For Gemma3: apply post_attention_layernorm to attn output before residual
        const attn_for_residual = if (weights.is_gemma3)
            mlx_graph.mlx_lazy_rms_norm(attn_proj, layer_weights.ln2_weight, norm_eps)
        else
            attn_proj;
        // Granite: scale layer output by residual_multiplier before adding to residual
        const scaled_attn = if (weights.is_granite and weights.residual_multiplier != 1.0)
            mlx_graph.mlx_lazy_multiply_scalar(attn_for_residual, weights.residual_multiplier)
        else
            attn_for_residual;
        const hidden_1 = mlx_graph.mlx_lazy_add(hidden, scaled_attn);

        // 12. >>> LAZY: Second RMS norm (pre-FFN)
        // For Gemma3: use pre_ffn_norm, otherwise use ln2_weight
        const normed_2 = if (weights.is_gemma3 and layer_weights.pre_ffn_norm != null)
            mlx_graph.mlx_lazy_rms_norm(hidden_1, layer_weights.pre_ffn_norm.?, norm_eps)
        else
            mlx_graph.mlx_lazy_rms_norm(hidden_1, layer_weights.ln2_weight, norm_eps);

        // 13-15. >>> LAZY: FFN (dense or MoE)
        const ffn_out = if (layer_weights.moe) |moe| blk: {
            // MoE path: router -> topk -> gather_qmm -> weighted sum
            break :blk mlx_graph.mlx_lazy_fused_moe_ffn_mxfp4(
                normed_2,
                // Router weights (8-bit affine or BF16)
                moe.router_w,
                if (moe.router_s) |rs| rs else null, // null for BF16 router
                if (moe.router_b) |rb| rb else null, // null for BF16 router
                if (moe.router_bias) |rb| rb else null, // Unwrap optional
                // Expert weights (MXFP4) - separate gate/up/down
                moe.gate_w,
                moe.gate_s,
                moe.up_w,
                moe.up_s,
                moe.down_w,
                moe.down_s,
                // Expert biases (unwrap optionals)
                if (moe.gate_bias) |gb| gb else null,
                if (moe.up_bias) |ub| ub else null,
                if (moe.down_bias) |db| db else null,
                // Config
                moe.num_experts,
                moe.experts_per_token,
                moe.router_group_size,
                moe.expert_group_size,
            );
        } else if (layer_weights.is_quantized) blk: {
            // Quantized dense FFN path
            break :blk mlx_graph.mlx_lazy_fused_ffn(
                normed_2,
                layer_weights.w1.?.weights, // gate
                layer_weights.w1.?.scales,
                layer_weights.w1.?.biases,
                layer_weights.w3.?.weights, // up
                layer_weights.w3.?.scales,
                layer_weights.w3.?.biases,
                layer_weights.w2.?.weights, // down
                layer_weights.w2.?.scales,
                layer_weights.w2.?.biases,
                layer_weights.w1.?.group_size,
                layer_weights.w1.?.bits,
                weights.is_gemma3, // use_gelu for Gemma3
            );
        } else blk: {
            // BF16 dense FFN path
            break :blk mlx_graph.mlx_lazy_fused_ffn_bf16(
                normed_2,
                layer_weights.w1_bf16.?, // gate
                layer_weights.w3_bf16.?, // up
                layer_weights.w2_bf16.?, // down
            );
        };

        // 16. >>> LAZY: Final residual
        // For Gemma3: apply post_feedforward_layernorm to FFN output before residual
        const ffn_for_residual = if (weights.is_gemma3 and layer_weights.post_ffn_norm != null)
            mlx_graph.mlx_lazy_rms_norm(ffn_out, layer_weights.post_ffn_norm.?, norm_eps)
        else
            ffn_out;
        // Granite: scale layer output by residual_multiplier before adding to residual
        const scaled_ffn = if (weights.is_granite and weights.residual_multiplier != 1.0)
            mlx_graph.mlx_lazy_multiply_scalar(ffn_for_residual, weights.residual_multiplier)
        else
            ffn_for_residual;
        hidden = mlx_graph.mlx_lazy_add(hidden_1, scaled_ffn);

        if (trace) {
            // Token-handle path is always decode-like (seq_len=1).
            try traceLastHiddenVector(allocator, "metal", "decode", layer_idx, hidden, 1, @intCast(weights.d_model));
        }
    }

    // Final layer norm
    const final_normed = mlx_graph.mlx_lazy_rms_norm(
        hidden,
        weights.ln_final,
        norm_eps,
    );

    // LM head projection
    const logits = if (weights.lm_head_quantized) |qw| blk: {
        break :blk mlx_graph.mlx_lazy_quantized_matmul(
            final_normed,
            qw.weights,
            qw.scales,
            qw.biases,
            qw.group_size,
            qw.bits,
            true, // transpose
        );
    } else blk: {
        const transpose_axes = [_]usize{ 1, 0 };
        const lm_head_t = mlx_graph.mlx_lazy_transpose(weights.lm_head.?, &transpose_axes, 2);
        break :blk mlx_graph.mlx_lazy_matmul(final_normed, lm_head_t);
    };

    // Granite: divide logits by logits_scaling (not multiply!)
    const scaled_logits = if (weights.is_granite and weights.logits_scaling != 1.0)
        mlx_graph.mlx_lazy_multiply_scalar(logits, 1.0 / weights.logits_scaling)
    else
        logits;

    return scaled_logits;
}
