// Library entry point for C API exports
//
// This file is the root for the shared library build.
// It exports all C API functions for FFI usage.

const capi = @import("capi/root.zig");

// Force the linker to export these symbols by referencing them in a comptime block
comptime {
    // Tensor API
    _ = &capi.tokamino_hello;
    _ = &capi.tokamino_tensor_create;
    _ = &capi.tokamino_tensor_zeros;
    _ = &capi.tokamino_tensor_test_embeddings;
    _ = &capi.tokamino_tensor_free;
    _ = &capi.tokamino_tensor_data_ptr;
    _ = &capi.tokamino_tensor_ndim;
    _ = &capi.tokamino_tensor_shape;
    _ = &capi.tokamino_tensor_strides;
    _ = &capi.tokamino_tensor_dtype;
    _ = &capi.tokamino_tensor_typestr;
    _ = &capi.tokamino_tensor_device_type;
    _ = &capi.tokamino_tensor_device_id;
    _ = &capi.tokamino_tensor_is_cpu;
    _ = &capi.tokamino_tensor_numel;
    _ = &capi.tokamino_tensor_element_size;
    _ = &capi.tokamino_tensor_to_dlpack;
    _ = &capi.tokamino_dlpack_capsule_name;
    _ = &capi.tokamino_dlpack_used_capsule_name;

    // Generate API
    _ = &capi.tokamino_session_create;
    _ = &capi.tokamino_session_create_with_seed;
    _ = &capi.tokamino_session_free;
    _ = &capi.tokamino_get_eos_tokens;
    _ = &capi.tokamino_apply_chat_template;
    _ = &capi.tokamino_generate;
    _ = &capi.tokamino_generate_stream;
    _ = &capi.tokamino_result_free;

    // Encode/Decode API
    _ = &capi.tokamino_encode;
    _ = &capi.tokamino_tokens_free;
    _ = &capi.tokamino_decode;
    _ = &capi.tokamino_text_free;

    // Generator API
    _ = &capi.tokamino_generator_start;
    _ = &capi.tokamino_generator_current;
    _ = &capi.tokamino_generator_next;
    _ = &capi.tokamino_generator_finished;
    _ = &capi.tokamino_generator_generated_count;
    _ = &capi.tokamino_generator_free;

    // Architecture API
    _ = &capi.tokamino_arch_init;
    _ = &capi.tokamino_arch_deinit;
    _ = &capi.tokamino_arch_register;
    _ = &capi.tokamino_arch_exists;
    _ = &capi.tokamino_arch_count;
    _ = &capi.tokamino_arch_list;
    _ = &capi.tokamino_arch_free_string;
    _ = &capi.tokamino_arch_detect;

    // Convert API
    _ = &capi.tokamino_convert;
    _ = &capi.tokamino_convert_free_string;
    _ = &capi.tokamino_convert_quant_types;

    // Ops API
    _ = &capi.tokamino_from_dlpack;
    _ = &capi.tokamino_tensor_free_view;
    _ = &capi.tokamino_rms_norm;
    _ = &capi.tokamino_silu;
    _ = &capi.tokamino_gelu;
    _ = &capi.tokamino_softmax;
    _ = &capi.tokamino_softmax_dim;
    _ = &capi.tokamino_rope_freqs;
    _ = &capi.tokamino_apply_rope;
    _ = &capi.tokamino_linear;
    _ = &capi.tokamino_sdpa;
    _ = &capi.tokamino_cat;
    _ = &capi.tokamino_transpose;
    _ = &capi.tokamino_matmul;
    _ = &capi.tokamino_embedding;
    _ = &capi.tokamino_relu;
    _ = &capi.tokamino_sigmoid;
    _ = &capi.tokamino_tanh;
    _ = &capi.tokamino_zeros;
    _ = &capi.tokamino_ones;
    _ = &capi.tokamino_arange;
    _ = &capi.tokamino_causal_mask;
    _ = &capi.tokamino_slice;
    _ = &capi.tokamino_reshape;
    _ = &capi.tokamino_split;
    _ = &capi.tokamino_unsqueeze;
    _ = &capi.tokamino_squeeze;
    _ = &capi.tokamino_expand;
    _ = &capi.tokamino_repeat_interleave;

    // Storage API
    _ = &capi.tokamino_storage_is_cached;
    _ = &capi.tokamino_storage_get_cached_path;
    _ = &capi.tokamino_storage_get_hf_home;
    _ = &capi.tokamino_storage_get_cache_dir;
    _ = &capi.tokamino_storage_list_models;
    _ = &capi.tokamino_storage_list_count;
    _ = &capi.tokamino_storage_list_get_id;
    _ = &capi.tokamino_storage_list_get_path;
    _ = &capi.tokamino_storage_list_free;
    _ = &capi.tokamino_storage_remove;
    _ = &capi.tokamino_storage_size;
    _ = &capi.tokamino_storage_total_size;
    _ = &capi.tokamino_storage_is_model_id;
    _ = &capi.tokamino_storage_download;
    _ = &capi.tokamino_storage_exists_remote;
    _ = &capi.tokamino_storage_list_remote;
    _ = &capi.tokamino_storage_search;
    _ = &capi.tokamino_storage_string_list_count;
    _ = &capi.tokamino_storage_string_list_get;
    _ = &capi.tokamino_storage_string_list_free;
}
