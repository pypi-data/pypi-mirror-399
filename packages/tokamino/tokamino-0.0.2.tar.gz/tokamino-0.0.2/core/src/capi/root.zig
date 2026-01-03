// C API module - exports all C-callable functions
//
// This module aggregates all C API exports for the library.
// Usage: const capi = @import("capi/root.zig");

pub const tensor = @import("tensor.zig");
pub const gen = @import("generate.zig");
pub const arch = @import("architecture.zig");
pub const ops = @import("ops.zig");
pub const conv = @import("convert.zig");
pub const storage = @import("storage.zig");

// Re-export all tensor C API functions at the top level
pub const tokamino_hello = tensor.tokamino_hello;
pub const tokamino_tensor_create = tensor.tokamino_tensor_create;
pub const tokamino_tensor_zeros = tensor.tokamino_tensor_zeros;
pub const tokamino_tensor_test_embeddings = tensor.tokamino_tensor_test_embeddings;
pub const tokamino_tensor_free = tensor.tokamino_tensor_free;
pub const tokamino_tensor_data_ptr = tensor.tokamino_tensor_data_ptr;
pub const tokamino_tensor_ndim = tensor.tokamino_tensor_ndim;
pub const tokamino_tensor_shape = tensor.tokamino_tensor_shape;
pub const tokamino_tensor_strides = tensor.tokamino_tensor_strides;
pub const tokamino_tensor_dtype = tensor.tokamino_tensor_dtype;
pub const tokamino_tensor_typestr = tensor.tokamino_tensor_typestr;
pub const tokamino_tensor_device_type = tensor.tokamino_tensor_device_type;
pub const tokamino_tensor_device_id = tensor.tokamino_tensor_device_id;
pub const tokamino_tensor_is_cpu = tensor.tokamino_tensor_is_cpu;
pub const tokamino_tensor_numel = tensor.tokamino_tensor_numel;
pub const tokamino_tensor_element_size = tensor.tokamino_tensor_element_size;
pub const tokamino_tensor_to_dlpack = tensor.tokamino_tensor_to_dlpack;
pub const tokamino_dlpack_capsule_name = tensor.tokamino_dlpack_capsule_name;
pub const tokamino_dlpack_used_capsule_name = tensor.tokamino_dlpack_used_capsule_name;

// Re-export generate C API functions
pub const tokamino_session_create = gen.tokamino_session_create;
pub const tokamino_session_create_with_seed = gen.tokamino_session_create_with_seed;
pub const tokamino_session_free = gen.tokamino_session_free;
pub const tokamino_resolve_model_path = gen.tokamino_resolve_model_path;
pub const tokamino_get_eos_tokens = gen.tokamino_get_eos_tokens;
pub const tokamino_apply_chat_template = gen.tokamino_apply_chat_template;
pub const tokamino_generate = gen.tokamino_generate;
pub const tokamino_generate_stream = gen.tokamino_generate_stream;
pub const tokamino_result_free = gen.tokamino_result_free;

// Re-export encode/decode C API functions
pub const tokamino_encode = gen.tokamino_encode;
pub const tokamino_tokens_free = gen.tokamino_tokens_free;
pub const tokamino_decode = gen.tokamino_decode;
pub const tokamino_decode_result_free = gen.tokamino_decode_result_free;
pub const tokamino_text_free = gen.tokamino_text_free;

// Re-export tokenizer-only C API functions (lightweight, no model weights)
pub const tokamino_tokenizer_create = gen.tokamino_tokenizer_create;
pub const tokamino_tokenizer_free = gen.tokamino_tokenizer_free;
pub const tokamino_tokenizer_encode = gen.tokamino_tokenizer_encode;
pub const tokamino_tokenizer_decode = gen.tokamino_tokenizer_decode;
pub const tokamino_tokenizer_get_eos_tokens = gen.tokamino_tokenizer_get_eos_tokens;
pub const tokamino_tokenizer_get_model_dir = gen.tokamino_tokenizer_get_model_dir;
pub const tokamino_tokenizer_get_vocab_size = gen.tokamino_tokenizer_get_vocab_size;
pub const tokamino_tokenizer_get_special_tokens = gen.tokamino_tokenizer_get_special_tokens;
pub const tokamino_tokenizer_id_to_token = gen.tokamino_tokenizer_id_to_token;
pub const tokamino_tokenizer_token_to_id = gen.tokamino_tokenizer_token_to_id;
pub const tokamino_tokenizer_tokenize = gen.tokamino_tokenizer_tokenize;
pub const tokamino_tokenize_result_free = gen.tokamino_tokenize_result_free;

// Re-export generator C API functions
pub const tokamino_generator_start = gen.tokamino_generator_start;
pub const tokamino_generator_current = gen.tokamino_generator_current;
pub const tokamino_generator_next = gen.tokamino_generator_next;
pub const tokamino_generator_finished = gen.tokamino_generator_finished;
pub const tokamino_generator_generated_count = gen.tokamino_generator_generated_count;
pub const tokamino_generator_free = gen.tokamino_generator_free;

// Re-export model description C API functions
pub const tokamino_describe = gen.tokamino_describe;
pub const tokamino_model_info_free = gen.tokamino_model_info_free;

// Re-export template C API functions
pub const tokamino_template_render = gen.tokamino_template_render;
pub const tokamino_template_error = gen.tokamino_template_error;

// Re-export architecture C API functions
pub const tokamino_arch_init = arch.tokamino_arch_init;
pub const tokamino_arch_deinit = arch.tokamino_arch_deinit;
pub const tokamino_arch_register = arch.tokamino_arch_register;
pub const tokamino_arch_exists = arch.tokamino_arch_exists;
pub const tokamino_arch_count = arch.tokamino_arch_count;
pub const tokamino_arch_list = arch.tokamino_arch_list;
pub const tokamino_arch_free_string = arch.tokamino_arch_free_string;
pub const tokamino_arch_detect = arch.tokamino_arch_detect;

// Re-export ops C API functions
pub const tokamino_from_dlpack = ops.tokamino_from_dlpack;
pub const tokamino_tensor_free_view = ops.tokamino_tensor_free_view;
pub const tokamino_rms_norm = ops.tokamino_rms_norm;
pub const tokamino_silu = ops.tokamino_silu;
pub const tokamino_gelu = ops.tokamino_gelu;
pub const tokamino_softmax = ops.tokamino_softmax;
pub const tokamino_softmax_dim = ops.tokamino_softmax_dim;
pub const tokamino_rope_freqs = ops.tokamino_rope_freqs;
pub const tokamino_apply_rope = ops.tokamino_apply_rope;
pub const tokamino_linear = ops.tokamino_linear;
pub const tokamino_sdpa = ops.tokamino_sdpa;
pub const tokamino_cat = ops.tokamino_cat;
pub const tokamino_transpose = ops.tokamino_transpose;
pub const tokamino_matmul = ops.tokamino_matmul;
pub const tokamino_embedding = ops.tokamino_embedding;
pub const tokamino_relu = ops.tokamino_relu;
pub const tokamino_sigmoid = ops.tokamino_sigmoid;
pub const tokamino_tanh = ops.tokamino_tanh;
pub const tokamino_zeros = ops.tokamino_zeros;
pub const tokamino_ones = ops.tokamino_ones;
pub const tokamino_arange = ops.tokamino_arange;
pub const tokamino_causal_mask = ops.tokamino_causal_mask;
pub const tokamino_slice = ops.tokamino_slice;
pub const tokamino_reshape = ops.tokamino_reshape;
pub const tokamino_split = ops.tokamino_split;
pub const tokamino_unsqueeze = ops.tokamino_unsqueeze;
pub const tokamino_squeeze = ops.tokamino_squeeze;
pub const tokamino_expand = ops.tokamino_expand;
pub const tokamino_repeat_interleave = ops.tokamino_repeat_interleave;

// Re-export convert C API functions
pub const tokamino_convert = conv.tokamino_convert;
pub const tokamino_convert_free_string = conv.tokamino_convert_free_string;
pub const tokamino_convert_quant_types = conv.tokamino_convert_quant_types;

// Re-export storage C API functions
pub const tokamino_storage_is_cached = storage.tokamino_storage_is_cached;
pub const tokamino_storage_get_cached_path = storage.tokamino_storage_get_cached_path;
pub const tokamino_storage_get_hf_home = storage.tokamino_storage_get_hf_home;
pub const tokamino_storage_get_cache_dir = storage.tokamino_storage_get_cache_dir;
pub const tokamino_storage_list_models = storage.tokamino_storage_list_models;
pub const tokamino_storage_list_count = storage.tokamino_storage_list_count;
pub const tokamino_storage_list_get_id = storage.tokamino_storage_list_get_id;
pub const tokamino_storage_list_get_path = storage.tokamino_storage_list_get_path;
pub const tokamino_storage_list_free = storage.tokamino_storage_list_free;
pub const tokamino_storage_remove = storage.tokamino_storage_remove;
pub const tokamino_storage_size = storage.tokamino_storage_size;
pub const tokamino_storage_total_size = storage.tokamino_storage_total_size;
pub const tokamino_storage_is_model_id = storage.tokamino_storage_is_model_id;
pub const tokamino_storage_download = storage.tokamino_storage_download;
pub const tokamino_storage_exists_remote = storage.tokamino_storage_exists_remote;
pub const tokamino_storage_list_remote = storage.tokamino_storage_list_remote;
pub const tokamino_storage_search = storage.tokamino_storage_search;
pub const tokamino_storage_string_list_count = storage.tokamino_storage_string_list_count;
pub const tokamino_storage_string_list_get = storage.tokamino_storage_string_list_get;
pub const tokamino_storage_string_list_free = storage.tokamino_storage_string_list_free;
pub const CachedModelList = storage.CachedModelList;
pub const StringList = storage.StringList;
pub const DownloadOptions = storage.DownloadOptions;

// Re-export types
pub const Tensor = tensor.Tensor;
pub const DType = tensor.DType;
pub const Device = tensor.Device;
pub const DLManagedTensor = tensor.DLManagedTensor;
pub const TokaminoError = ops.TokaminoError;
pub const SessionHandle = gen.SessionHandle;
pub const TokenizerHandle = gen.TokenizerHandle;
pub const GenerateResult = gen.GenerateResult;
pub const GenerateConfig = gen.GenerateConfig;
pub const GeneratorConfig = gen.GeneratorConfig;
pub const GeneratorHandle = gen.GeneratorHandle;
pub const SamplingParams = gen.SamplingParams;
pub const EncodeResult = gen.EncodeResult;
pub const DecodeResult = gen.DecodeResult;
pub const TokenizeResult = gen.TokenizeResult;
pub const SpecialTokensResult = gen.SpecialTokensResult;
pub const ModelInfo = gen.ModelInfo;
pub const ConvertOptions = conv.ConvertOptions;
pub const ConvertResult = conv.ConvertResult;
pub const ConvertFormat = conv.ConvertFormat;
pub const NativeQuantType = conv.NativeQuantType;
