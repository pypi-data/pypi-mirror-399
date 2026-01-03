"""
Tokamino Python bindings using ctypes (zero dependencies).

Provides zero-copy tensor interchange with NumPy (via __array_interface__)
and PyTorch/JAX (via __dlpack__).
"""

import ctypes
import sys
from pathlib import Path
from typing import Any

# =============================================================================
# Library Loading
# =============================================================================


def _find_library_path() -> Path:
    """Find the tokamino shared library."""
    here = Path(__file__).parent

    # 1. Look for bundled file (release mode)
    for ext in [".so", ".dylib", ".dll"]:
        bundled = here / f"libtokamino{ext}"
        if bundled.exists():
            return bundled

    # 2. Look for Zig build output (dev mode)
    project_root = here.parent.parent.parent
    zig_out = project_root / "zig-out" / "lib"

    # Platform specific naming
    if sys.platform == "win32":
        target = zig_out / "tokamino.dll"
    elif sys.platform == "darwin":
        target = zig_out / "libtokamino.dylib"
    else:
        target = zig_out / "libtokamino.so"

    if target.exists():
        return target

    raise FileNotFoundError(
        f"Could not find tokamino library. "
        f"Run 'zig build' from the repository root first. "
        f"Expected: {target}"
    )


# Load library
_lib_path = _find_library_path()
_lib = ctypes.CDLL(str(_lib_path))

# =============================================================================
# Constants
# =============================================================================


class DType:
    """Data type enum (matches Zig)."""

    FLOAT32 = 0
    FLOAT64 = 1
    INT32 = 2
    INT64 = 3
    GROUPED_AFFINE_U4 = 25
    GROUPED_AFFINE_U8 = 26
    MLX_4BIT = GROUPED_AFFINE_U4
    MLX_8BIT = GROUPED_AFFINE_U8


class DeviceType:
    """Device type enum (DLPack standard)."""

    CPU = 1
    CUDA = 2
    CUDA_HOST = 3
    OPENCL = 4
    VULKAN = 7
    METAL = 8
    ROCM = 10


# Map dtype to numpy format string
_DTYPE_TO_TYPESTR = {
    DType.FLOAT32: "<f4",
    DType.FLOAT64: "<f8",
    DType.INT32: "<i4",
    DType.INT64: "<i8",
    DType.GROUPED_AFFINE_U4: "<u1",
    DType.GROUPED_AFFINE_U8: "<u1",
}

# Map dtype to element size
_DTYPE_TO_SIZE = {
    DType.FLOAT32: 4,
    DType.FLOAT64: 8,
    DType.INT32: 4,
    DType.INT64: 8,
    DType.GROUPED_AFFINE_U4: 1,
    DType.GROUPED_AFFINE_U8: 1,
}

# =============================================================================
# DLPack Structures (for __dlpack__ protocol)
# =============================================================================


class DLDevice(ctypes.Structure):
    """DLPack device descriptor."""

    _fields_ = [
        ("device_type", ctypes.c_int32),
        ("device_id", ctypes.c_int32),
    ]


class DLDataType(ctypes.Structure):
    """DLPack data type descriptor."""

    _fields_ = [
        ("code", ctypes.c_uint8),
        ("bits", ctypes.c_uint8),
        ("lanes", ctypes.c_uint16),
    ]


class DLTensor(ctypes.Structure):
    """DLPack tensor descriptor."""

    _fields_ = [
        ("data", ctypes.c_void_p),
        ("device", DLDevice),
        ("ndim", ctypes.c_int32),
        ("dtype", DLDataType),
        ("shape", ctypes.POINTER(ctypes.c_int64)),
        ("strides", ctypes.POINTER(ctypes.c_int64)),
        ("byte_offset", ctypes.c_uint64),
    ]


# Forward declaration for the deleter
DLManagedTensorDeleter = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


class DLManagedTensor(ctypes.Structure):
    """DLPack managed tensor with lifecycle management."""

    _fields_ = [
        ("dl_tensor", DLTensor),
        ("manager_ctx", ctypes.c_void_p),
        ("deleter", DLManagedTensorDeleter),
    ]


# =============================================================================
# Generate API Structures
# =============================================================================


class SamplingStrategy:
    """Sampling strategy enum."""

    GREEDY = 0
    TOP_K = 1
    TOP_P = 2


class SamplingParams(ctypes.Structure):
    """Sampling configuration."""

    _fields_ = [
        ("strategy", ctypes.c_uint32),
        ("temperature", ctypes.c_float),
        ("top_k", ctypes.c_uint32),
        ("top_p", ctypes.c_float),
    ]

    def __init__(
        self,
        strategy: int = SamplingStrategy.GREEDY,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
    ):
        super().__init__()
        self.strategy = strategy
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p


class GenerateConfig(ctypes.Structure):
    """Generation configuration."""

    _fields_ = [
        ("max_tokens", ctypes.c_uint32),
        ("sampling", SamplingParams),
        ("seed", ctypes.c_uint64),
    ]

    def __init__(
        self,
        max_tokens: int = 32,
        sampling: SamplingParams | None = None,
        seed: int = 0,
    ):
        super().__init__()
        self.max_tokens = max_tokens
        self.sampling = sampling or SamplingParams()
        self.seed = seed


class GenerateResult(ctypes.Structure):
    """Result from text generation."""

    _fields_ = [
        ("tokens", ctypes.POINTER(ctypes.c_uint32)),
        ("num_tokens", ctypes.c_size_t),
        ("prompt_len", ctypes.c_size_t),
        ("generated_len", ctypes.c_size_t),
        ("prefill_ns", ctypes.c_uint64),
        ("decode_ns", ctypes.c_uint64),
        ("error_msg", ctypes.c_char_p),
    ]


# Token callback function type
TokenCallbackFunc = ctypes.CFUNCTYPE(None, ctypes.c_uint32, ctypes.c_void_p)


class EncodeResult(ctypes.Structure):
    """Result from encode operation (C struct)."""

    _fields_ = [
        ("tokens", ctypes.POINTER(ctypes.c_uint32)),
        ("num_tokens", ctypes.c_size_t),
        ("error_msg", ctypes.c_char_p),
    ]


class GeneratorConfig(ctypes.Structure):
    """Generator configuration (for iterator-style generation)."""

    _fields_ = [
        ("max_tokens", ctypes.c_uint32),
        ("sampling", SamplingParams),
        ("flush_interval_ms", ctypes.c_uint32),
        ("eos_tokens", ctypes.POINTER(ctypes.c_uint32)),
        ("num_eos_tokens", ctypes.c_size_t),
    ]

    def __init__(
        self,
        max_tokens: int = 32,
        sampling: SamplingParams | None = None,
        flush_interval_ms: int = 100,
        eos_tokens: list | None = None,
    ):
        super().__init__()
        self.max_tokens = max_tokens
        self.sampling = sampling or SamplingParams()
        self.flush_interval_ms = flush_interval_ms
        if eos_tokens:
            arr = (ctypes.c_uint32 * len(eos_tokens))(*eos_tokens)
            self._eos_arr = arr  # Keep reference
            self.eos_tokens = ctypes.cast(arr, ctypes.POINTER(ctypes.c_uint32))
            self.num_eos_tokens = len(eos_tokens)
        else:
            self.eos_tokens = None
            self.num_eos_tokens = 0


class EosTokenResult(ctypes.Structure):
    """Result from get_eos_tokens."""

    _fields_ = [
        ("tokens", ctypes.POINTER(ctypes.c_uint32)),
        ("num_tokens", ctypes.c_size_t),
    ]


class ModelInfoC(ctypes.Structure):
    """Model information from describe (C struct)."""

    _fields_ = [
        # Core architecture
        ("vocab_size", ctypes.c_int32),
        ("hidden_size", ctypes.c_int32),
        ("num_layers", ctypes.c_int32),
        ("num_heads", ctypes.c_int32),
        ("num_kv_heads", ctypes.c_int32),
        ("intermediate_size", ctypes.c_int32),
        ("max_seq_len", ctypes.c_int32),
        ("head_dim", ctypes.c_int32),
        # RoPE parameters
        ("rope_theta", ctypes.c_float),
        ("norm_eps", ctypes.c_float),
        # Quantization
        ("quant_bits", ctypes.c_int32),
        ("quant_group_size", ctypes.c_int32),
        # Architecture info (strings)
        ("model_type", ctypes.c_void_p),
        ("architecture", ctypes.c_void_p),
        # Flags
        ("tie_word_embeddings", ctypes.c_bool),
        ("use_gelu", ctypes.c_bool),
        # MoE
        ("num_experts", ctypes.c_int32),
        ("experts_per_token", ctypes.c_int32),
        # Error
        ("error_msg", ctypes.c_char_p),
    ]


class TokenArray:
    """
    Zero-copy token array wrapper around Zig-allocated memory.

    Supports NumPy via __array_interface__ for zero-copy access.
    Use `np.asarray(token_array)` to get a NumPy view.
    """

    def __init__(self, tokens_ptr, num_tokens: int):
        """
        Initialize from Zig-allocated token pointer.

        Args:
            tokens_ptr: Pointer to uint32 token IDs
            num_tokens: Number of tokens
        """
        self._ptr = tokens_ptr
        self._num_tokens = num_tokens
        self._owns_data = True

    def __len__(self) -> int:
        return self._num_tokens

    def __getitem__(self, idx: int) -> int:
        if idx < 0:
            idx = self._num_tokens + idx
        if idx < 0 or idx >= self._num_tokens:
            raise IndexError(f"Token index {idx} out of range [0, {self._num_tokens})")
        return self._ptr[idx]

    def tolist(self) -> list:
        """Convert to Python list (copies data)."""
        return [self._ptr[i] for i in range(self._num_tokens)]

    @property
    def __array_interface__(self) -> dict:
        """
        NumPy array interface for zero-copy access.

        Usage: np.asarray(token_array)
        """
        return {
            "version": 3,
            "shape": (self._num_tokens,),
            "typestr": "<u4",  # uint32 little-endian
            "data": (ctypes.addressof(self._ptr.contents), False),  # (ptr, read-only=False)
            "strides": (4,),  # 4 bytes per uint32
        }

    def __del__(self):
        """Free the tokens when garbage collected."""
        if hasattr(self, "_ptr") and self._ptr and self._owns_data:
            _lib.tokamino_tokens_free(self._ptr, self._num_tokens)
            self._ptr = None

    def __repr__(self) -> str:
        if self._num_tokens <= 10:
            tokens_str = str(self.tolist())
        else:
            first = [self._ptr[i] for i in range(5)]
            last = [self._ptr[i] for i in range(self._num_tokens - 3, self._num_tokens)]
            tokens_str = f"[{', '.join(map(str, first))}, ..., {', '.join(map(str, last))}]"
        return f"TokenArray({tokens_str}, len={self._num_tokens})"


# =============================================================================
# Function Signatures
# =============================================================================


def _setup_signatures():
    """Define C function signatures. Keep in sync with tokamino.h."""
    # Tensor Creation
    _lib.tokamino_tensor_create.argtypes = [
        ctypes.POINTER(ctypes.c_int64),  # shape
        ctypes.c_size_t,  # ndim
        ctypes.c_uint32,  # dtype
        ctypes.c_int32,  # device_type
        ctypes.c_int32,  # device_id
    ]
    _lib.tokamino_tensor_create.restype = ctypes.c_void_p

    _lib.tokamino_tensor_zeros.argtypes = [
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_size_t,
        ctypes.c_uint32,
    ]
    _lib.tokamino_tensor_zeros.restype = ctypes.c_void_p

    _lib.tokamino_tensor_test_embeddings.argtypes = []
    _lib.tokamino_tensor_test_embeddings.restype = ctypes.c_void_p

    _lib.tokamino_tensor_free.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_free.restype = None

    # Tensor Accessors
    _lib.tokamino_tensor_data_ptr.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_data_ptr.restype = ctypes.c_void_p

    _lib.tokamino_tensor_ndim.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_ndim.restype = ctypes.c_size_t

    _lib.tokamino_tensor_shape.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_shape.restype = ctypes.POINTER(ctypes.c_int64)

    _lib.tokamino_tensor_strides.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_strides.restype = ctypes.POINTER(ctypes.c_int64)

    _lib.tokamino_tensor_dtype.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_dtype.restype = ctypes.c_uint32

    _lib.tokamino_tensor_typestr.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_typestr.restype = ctypes.c_char_p

    _lib.tokamino_tensor_device_type.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_device_type.restype = ctypes.c_int32

    _lib.tokamino_tensor_device_id.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_device_id.restype = ctypes.c_int32

    _lib.tokamino_tensor_is_cpu.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_is_cpu.restype = ctypes.c_bool

    _lib.tokamino_tensor_numel.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_numel.restype = ctypes.c_size_t

    _lib.tokamino_tensor_element_size.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_element_size.restype = ctypes.c_size_t

    # DLPack API
    _lib.tokamino_tensor_to_dlpack.argtypes = [ctypes.c_void_p]
    _lib.tokamino_tensor_to_dlpack.restype = ctypes.c_void_p

    _lib.tokamino_dlpack_capsule_name.argtypes = []
    _lib.tokamino_dlpack_capsule_name.restype = ctypes.c_char_p

    _lib.tokamino_dlpack_used_capsule_name.argtypes = []
    _lib.tokamino_dlpack_used_capsule_name.restype = ctypes.c_char_p

    # Session Management
    _lib.tokamino_session_create.argtypes = [ctypes.c_char_p]
    _lib.tokamino_session_create.restype = ctypes.c_void_p

    _lib.tokamino_session_create_with_seed.argtypes = [ctypes.c_char_p, ctypes.c_uint64]
    _lib.tokamino_session_create_with_seed.restype = ctypes.c_void_p

    _lib.tokamino_session_free.argtypes = [ctypes.c_void_p]
    _lib.tokamino_session_free.restype = None

    # Model path resolution (HuggingFace Hub)
    _lib.tokamino_resolve_model_path.argtypes = [ctypes.c_char_p]
    _lib.tokamino_resolve_model_path.restype = ctypes.c_void_p  # Returns null-terminated string

    # EOS tokens and chat template
    _lib.tokamino_get_eos_tokens.argtypes = [ctypes.c_char_p]
    _lib.tokamino_get_eos_tokens.restype = EosTokenResult

    _lib.tokamino_session_get_eos_tokens.argtypes = [ctypes.c_void_p]
    _lib.tokamino_session_get_eos_tokens.restype = EosTokenResult

    _lib.tokamino_apply_chat_template.argtypes = [
        ctypes.c_void_p,  # session (can be null)
        ctypes.c_char_p,  # model_dir
        ctypes.c_char_p,  # messages_json
        ctypes.c_int,  # add_generation_prompt
    ]
    _lib.tokamino_apply_chat_template.restype = ctypes.c_void_p

    # Generation
    _lib.tokamino_generate.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.c_char_p,  # prompt
        ctypes.POINTER(GenerateConfig),  # config
    ]
    _lib.tokamino_generate.restype = GenerateResult

    _lib.tokamino_generate_stream.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.c_char_p,  # prompt
        ctypes.POINTER(GenerateConfig),  # config
        TokenCallbackFunc,  # callback
        ctypes.c_void_p,  # callback_data
    ]
    _lib.tokamino_generate_stream.restype = GenerateResult

    _lib.tokamino_result_free.argtypes = [ctypes.POINTER(GenerateResult)]
    _lib.tokamino_result_free.restype = None

    # Encode/Decode API
    _lib.tokamino_encode.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.POINTER(ctypes.c_char),  # text (raw pointer, not c_char_p which is null-terminated)
        ctypes.c_size_t,  # text_len
    ]
    _lib.tokamino_encode.restype = EncodeResult

    _lib.tokamino_tokens_free.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),  # tokens
        ctypes.c_size_t,  # num_tokens
    ]
    _lib.tokamino_tokens_free.restype = None

    # Use c_void_p instead of c_char_p to preserve pointer for freeing
    _lib.tokamino_decode.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.POINTER(ctypes.c_uint32),  # tokens
        ctypes.c_size_t,  # num_tokens
    ]
    _lib.tokamino_decode.restype = ctypes.c_void_p  # We'll cast to string manually

    _lib.tokamino_text_free.argtypes = [ctypes.c_void_p]
    _lib.tokamino_text_free.restype = None

    # Generator API
    _lib.tokamino_generator_start.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.c_char_p,  # prompt
        ctypes.POINTER(GeneratorConfig),  # config
    ]
    _lib.tokamino_generator_start.restype = ctypes.c_void_p

    _lib.tokamino_generator_current.argtypes = [ctypes.c_void_p]
    _lib.tokamino_generator_current.restype = ctypes.c_uint32

    _lib.tokamino_generator_next.argtypes = [ctypes.c_void_p]
    _lib.tokamino_generator_next.restype = ctypes.c_uint32

    _lib.tokamino_generator_finished.argtypes = [ctypes.c_void_p]
    _lib.tokamino_generator_finished.restype = ctypes.c_bool

    _lib.tokamino_generator_generated_count.argtypes = [ctypes.c_void_p]
    _lib.tokamino_generator_generated_count.restype = ctypes.c_size_t

    _lib.tokamino_generator_free.argtypes = [ctypes.c_void_p]
    _lib.tokamino_generator_free.restype = None

    # Model Description API
    _lib.tokamino_describe.argtypes = [ctypes.c_char_p]
    _lib.tokamino_describe.restype = ModelInfoC

    _lib.tokamino_model_info_free.argtypes = [ctypes.POINTER(ModelInfoC)]
    _lib.tokamino_model_info_free.restype = None

    # Architecture API
    _lib.tokamino_arch_init.argtypes = []
    _lib.tokamino_arch_init.restype = None

    _lib.tokamino_arch_deinit.argtypes = []
    _lib.tokamino_arch_deinit.restype = None

    _lib.tokamino_arch_register.argtypes = [ctypes.c_char_p]
    _lib.tokamino_arch_register.restype = ctypes.c_int32

    _lib.tokamino_arch_exists.argtypes = [ctypes.c_char_p]
    _lib.tokamino_arch_exists.restype = ctypes.c_bool

    _lib.tokamino_arch_count.argtypes = []
    _lib.tokamino_arch_count.restype = ctypes.c_size_t

    _lib.tokamino_arch_list.argtypes = []
    _lib.tokamino_arch_list.restype = ctypes.c_void_p

    _lib.tokamino_arch_free_string.argtypes = [ctypes.c_void_p]
    _lib.tokamino_arch_free_string.restype = None

    _lib.tokamino_arch_detect.argtypes = [ctypes.c_char_p]
    _lib.tokamino_arch_detect.restype = ctypes.c_char_p


_setup_signatures()


def _get_lib():
    """Get the library handle (for use by architecture.py)."""
    return _lib


# =============================================================================
# PyCapsule helpers for DLPack
# =============================================================================

# Get PyCapsule functions from Python C API
_PyCapsule_New = ctypes.pythonapi.PyCapsule_New
_PyCapsule_New.argtypes = [
    ctypes.c_void_p,  # pointer
    ctypes.c_char_p,  # name
    ctypes.c_void_p,  # destructor (can be NULL)
]
_PyCapsule_New.restype = ctypes.py_object

_PyCapsule_SetName = ctypes.pythonapi.PyCapsule_SetName
_PyCapsule_SetName.argtypes = [ctypes.py_object, ctypes.c_char_p]
_PyCapsule_SetName.restype = ctypes.c_int

# Capsule destructor type - takes a raw PyObject* pointer
PyCapsule_Destructor = ctypes.CFUNCTYPE(None, ctypes.c_void_p)


# =============================================================================
# PyCapsule Destructor Logic
# =============================================================================

# Setup C-API access for capsule manipulation
_PyCapsule_GetPointer = ctypes.pythonapi.PyCapsule_GetPointer
_PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
_PyCapsule_GetPointer.restype = ctypes.c_void_p

_PyCapsule_GetName = ctypes.pythonapi.PyCapsule_GetName
_PyCapsule_GetName.argtypes = [ctypes.py_object]
_PyCapsule_GetName.restype = ctypes.c_char_p


def _capsule_deleter(capsule_ptr):
    """
    Robust destructor for the DLPack capsule.

    Scenario A (Consumed): PyTorch renamed capsule to "used_dltensor".
                           We do nothing. PyTorch owns the memory.

    Scenario B (Unused):   Name is still "dltensor".
                           We must call the deleter to free Zig memory.

    Scenario C (Shutdown): Python is exiting. We do nothing to avoid
                           ctypes/GIL crashes. OS will reclaim memory.

    Args:
        capsule_ptr: Raw pointer to the PyCapsule object (c_void_p)
    """
    try:
        # Guard against interpreter shutdown - ctypes calls are unsafe then
        if sys.is_finalizing():
            return

        # Cast raw pointer to py_object for API calls
        capsule = ctypes.cast(capsule_ptr, ctypes.py_object)

        # Check if PyTorch/JAX already consumed (renamed) it
        name = _PyCapsule_GetName(capsule)

        # If name is None, something is wrong, bail out safely
        if not name:
            return

        # "used_dltensor" means consumer took ownership and will call deleter
        if name == b"used_dltensor":
            return

        # Capsule was NOT consumed - we must clean up
        ptr = _PyCapsule_GetPointer(capsule, name)
        if not ptr:
            return

        # Invoke the Zig deleter
        managed = ctypes.cast(ptr, ctypes.POINTER(DLManagedTensor)).contents
        if managed.deleter:
            managed.deleter(ptr)
    except Exception:
        # Silently ignore any errors during cleanup
        # This can happen during interpreter shutdown
        pass


# Keep a global reference to the CFUNCTYPE wrapper so it isn't GC'd
_dlpack_destructor = PyCapsule_Destructor(_capsule_deleter)

# =============================================================================
# Tensor Class
# =============================================================================


class Tensor:
    """
    Zero-copy tensor wrapper around Zig-allocated memory.

    Supports:
    - NumPy via __array_interface__ (CPU only)
    - PyTorch/JAX via __dlpack__ (CPU and GPU)
    """

    def __init__(self, ptr: int):
        """
        Initialize tensor from a Zig pointer.

        Args:
            ptr: Pointer to Tensor (from C API)
        """
        if not ptr:
            raise ValueError("Cannot create Tensor from null pointer")
        self._ptr = ptr
        self._owns_data = True  # Track if we still own the data

    @property
    def shape(self) -> tuple[int, ...]:
        """Get tensor shape."""
        ndim = _lib.tokamino_tensor_ndim(self._ptr)
        shape_ptr = _lib.tokamino_tensor_shape(self._ptr)
        return tuple(shape_ptr[i] for i in range(ndim))

    @property
    def strides(self) -> tuple[int, ...]:
        """Get tensor strides (in elements)."""
        ndim = _lib.tokamino_tensor_ndim(self._ptr)
        strides_ptr = _lib.tokamino_tensor_strides(self._ptr)
        return tuple(strides_ptr[i] for i in range(ndim))

    @property
    def dtype(self) -> int:
        """Get dtype enum value."""
        return _lib.tokamino_tensor_dtype(self._ptr)

    @property
    def ndim(self) -> int:
        """Get number of dimensions."""
        return _lib.tokamino_tensor_ndim(self._ptr)

    @property
    def numel(self) -> int:
        """Get total number of elements."""
        return _lib.tokamino_tensor_numel(self._ptr)

    @property
    def data_ptr(self) -> int:
        """Get raw data pointer."""
        return _lib.tokamino_tensor_data_ptr(self._ptr)

    @property
    def device_type(self) -> int:
        """Get device type."""
        return _lib.tokamino_tensor_device_type(self._ptr)

    @property
    def device_id(self) -> int:
        """Get device id."""
        return _lib.tokamino_tensor_device_id(self._ptr)

    @property
    def is_cpu(self) -> bool:
        """Check if tensor is on CPU."""
        return _lib.tokamino_tensor_is_cpu(self._ptr)

    @property
    def __array_interface__(self) -> dict:
        """
        NumPy array interface for zero-copy access.

        Raises
        ------
            RuntimeError: If tensor is not on CPU
        """
        if not self.is_cpu:
            raise RuntimeError(
                "__array_interface__ only supports CPU tensors. Use __dlpack__ for GPU tensors."
            )

        typestr = _lib.tokamino_tensor_typestr(self._ptr).decode("utf-8")
        elem_size = _lib.tokamino_tensor_element_size(self._ptr)

        # Convert element strides to byte strides
        strides_bytes = tuple(s * elem_size for s in self.strides)

        return {
            "version": 3,
            "shape": self.shape,
            "typestr": typestr,
            "data": (self.data_ptr, False),  # (ptr, read-only=False)
            "strides": strides_bytes,
        }

    def __dlpack__(
        self,
        *,
        stream: int | None = None,
        max_version: tuple | None = None,
        dl_device: tuple | None = None,
        copy: bool | None = None,
    ) -> Any:
        """
        DLPack protocol for PyTorch/JAX zero-copy access.

        Note: After calling __dlpack__, ownership transfers to the consumer.
        The consumer (PyTorch/JAX) will call the deleter when done.
        This Tensor wrapper becomes invalid after dlpack export.

        Args:
            stream: CUDA stream (optional, for GPU sync)
            max_version: Maximum DLPack version supported (ignored, we use v0)
            dl_device: Target device (ignored)
            copy: Whether to copy (ignored, we never copy)

        Returns
        -------
            PyCapsule containing DLManagedTensor*
        """
        if not self._owns_data:
            raise RuntimeError("Tensor data already exported via DLPack")

        # Get DLManagedTensor* from Zig
        dlpack_ptr = _lib.tokamino_tensor_to_dlpack(self._ptr)
        if not dlpack_ptr:
            raise RuntimeError("Failed to create DLPack tensor")

        # Transfer ownership - consumer will free via deleter
        # Mark that we no longer own the data (deleter will free Tensor)
        self._owns_data = False

        # Wrap in PyCapsule with destructor for proper cleanup
        # - If consumed by PyTorch: renamed to "used_dltensor", destructor no-ops
        # - If never consumed: destructor calls Zig deleter to free memory
        capsule = _PyCapsule_New(
            dlpack_ptr,
            b"dltensor",
            _dlpack_destructor,
        )

        return capsule

    def __dlpack_device__(self) -> tuple[int, int]:
        """
        DLPack device protocol.

        Returns
        -------
            Tuple of (device_type, device_id)
        """
        return (self.device_type, self.device_id)

    def __del__(self):
        """Free the tensor when garbage collected."""
        if hasattr(self, "_ptr") and self._ptr and self._owns_data:
            _lib.tokamino_tensor_free(self._ptr)
            self._ptr = None

    def __repr__(self) -> str:
        dtype_names = {
            DType.FLOAT32: "float32",
            DType.FLOAT64: "float64",
            DType.INT32: "int32",
            DType.INT64: "int64",
        }
        device_names = {
            DeviceType.CPU: "cpu",
            DeviceType.CUDA: "cuda",
        }
        dtype_name = dtype_names.get(self.dtype, f"dtype{self.dtype}")
        device_name = device_names.get(self.device_type, f"device{self.device_type}")
        device_str = f"{device_name}:{self.device_id}" if self.device_id else device_name
        return f"Tensor(shape={self.shape}, dtype={dtype_name}, device={device_str})"


# =============================================================================
# Public API
# =============================================================================


def zeros(shape: tuple[int, ...], dtype: int = DType.FLOAT32) -> Tensor:
    """
    Create a tensor filled with zeros.

    Args:
        shape: Tensor shape
        dtype: Data type (DType.FLOAT32, etc.)

    Returns
    -------
        New Tensor filled with zeros
    """
    shape_arr = (ctypes.c_int64 * len(shape))(*shape)
    ptr = _lib.tokamino_tensor_zeros(shape_arr, len(shape), dtype)
    if not ptr:
        raise RuntimeError("Failed to create tensor")
    return Tensor(ptr)


def empty(
    shape: tuple[int, ...],
    dtype: int = DType.FLOAT32,
    device_type: int = DeviceType.CPU,
    device_id: int = 0,
) -> Tensor:
    """
    Create an uninitialized tensor.

    Args:
        shape: Tensor shape
        dtype: Data type
        device_type: Device type (DeviceType.CPU, etc.)
        device_id: Device ID

    Returns
    -------
        New uninitialized Tensor
    """
    shape_arr = (ctypes.c_int64 * len(shape))(*shape)
    ptr = _lib.tokamino_tensor_create(shape_arr, len(shape), dtype, device_type, device_id)
    if not ptr:
        raise RuntimeError("Failed to create tensor")
    return Tensor(ptr)


def get_test_embeddings() -> Tensor:
    """
    Get a test tensor with sample embeddings (10x1536 float32).

    Returns
    -------
        Tensor with sample data
    """
    ptr = _lib.tokamino_tensor_test_embeddings()
    if not ptr:
        raise RuntimeError("Failed to create test tensor")
    return Tensor(ptr)


# =============================================================================
# Model Description
# =============================================================================


class ModelInfo:
    """
    Model architecture and configuration information.

    Attributes
    ----------
        vocab_size: Vocabulary size
        hidden_size: Hidden dimension (d_model)
        num_layers: Number of transformer layers
        num_heads: Number of attention heads
        num_kv_heads: Number of key-value heads (for GQA)
        intermediate_size: FFN intermediate dimension
        max_seq_len: Maximum sequence length
        head_dim: Dimension per attention head
        rope_theta: RoPE base frequency
        norm_eps: Layer norm epsilon
        quant_bits: Quantization bits (4, 8, or 16 for fp16)
        quant_group_size: Quantization group size
        model_type: Model type string (e.g., "qwen3", "llama")
        architecture: Architecture class name (e.g., "Qwen3ForCausalLM")
        tie_word_embeddings: Whether embeddings are tied
        use_gelu: Whether GELU activation is used
        num_experts: Number of MoE experts (0 if not MoE)
        experts_per_token: Experts used per token (for MoE)
    """

    def __init__(
        self,
        vocab_size: int,
        hidden_size: int,
        num_layers: int,
        num_heads: int,
        num_kv_heads: int,
        intermediate_size: int,
        max_seq_len: int,
        head_dim: int,
        rope_theta: float,
        norm_eps: float,
        quant_bits: int,
        quant_group_size: int,
        model_type: str | None,
        architecture: str | None,
        tie_word_embeddings: bool,
        use_gelu: bool,
        num_experts: int,
        experts_per_token: int,
    ):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.intermediate_size = intermediate_size
        self.max_seq_len = max_seq_len
        self.head_dim = head_dim
        self.rope_theta = rope_theta
        self.norm_eps = norm_eps
        self.quant_bits = quant_bits
        self.quant_group_size = quant_group_size
        self.model_type = model_type
        self.architecture = architecture
        self.tie_word_embeddings = tie_word_embeddings
        self.use_gelu = use_gelu
        self.num_experts = num_experts
        self.experts_per_token = experts_per_token

    @property
    def is_quantized(self) -> bool:
        """Whether the model is quantized (not fp16)."""
        return self.quant_bits < 16

    @property
    def is_moe(self) -> bool:
        """Whether the model uses Mixture of Experts."""
        return self.num_experts > 0

    def __repr__(self) -> str:
        quant_str = f"Q{self.quant_bits}" if self.is_quantized else "FP16"
        return (
            f"ModelInfo({self.architecture or self.model_type or 'unknown'}, "
            f"layers={self.num_layers}, hidden={self.hidden_size}, "
            f"heads={self.num_heads}, {quant_str})"
        )


def describe(model: str) -> ModelInfo:
    """
    Get model architecture and configuration information.

    Args:
        model: Path to model directory or HuggingFace model ID.
               - Local path: directory containing config.json
               - HuggingFace ID: e.g., "Qwen/Qwen3-0.6B"

    Returns
    -------
        ModelInfo with model configuration

    Raises
    ------
        RuntimeError: If model cannot be loaded or parsed
    """
    result = _lib.tokamino_describe(model.encode("utf-8"))

    if result.error_msg:
        error = result.error_msg.decode("utf-8")
        raise RuntimeError(f"Failed to describe model '{model}': {error}")

    # Extract strings before freeing
    model_type = None
    if result.model_type:
        model_type = ctypes.cast(result.model_type, ctypes.c_char_p).value.decode("utf-8")

    architecture = None
    if result.architecture:
        architecture = ctypes.cast(result.architecture, ctypes.c_char_p).value.decode("utf-8")

    info = ModelInfo(
        vocab_size=result.vocab_size,
        hidden_size=result.hidden_size,
        num_layers=result.num_layers,
        num_heads=result.num_heads,
        num_kv_heads=result.num_kv_heads,
        intermediate_size=result.intermediate_size,
        max_seq_len=result.max_seq_len,
        head_dim=result.head_dim,
        rope_theta=result.rope_theta,
        norm_eps=result.norm_eps,
        quant_bits=result.quant_bits,
        quant_group_size=result.quant_group_size,
        model_type=model_type,
        architecture=architecture,
        tie_word_embeddings=result.tie_word_embeddings,
        use_gelu=result.use_gelu,
        num_experts=result.num_experts,
        experts_per_token=result.experts_per_token,
    )

    # Free the C strings
    _lib.tokamino_model_info_free(ctypes.byref(result))

    return info


# =============================================================================
# Session Class for Text Generation
# =============================================================================


class Session:
    """
    LLM inference session for text generation.

    Example:
        >>> session = Session("path/to/model")
        >>> result = session.generate("Hello, world!")
        >>> print(result.text)

        # HuggingFace model ID (downloads automatically if not cached)
        >>> session = Session("Qwen/Qwen3-0.6B")
    """

    def __init__(self, model: str, seed: int = 0):
        """
        Create a new generation session.

        Args:
            model: Path to model directory or HuggingFace model ID.
                   - Local path: directory containing config.json, model.safetensors, tokenizer.json
                   - HuggingFace ID: e.g., "Qwen/Qwen3-0.6B" (downloads automatically)
            seed: Random seed (0 = use time-based seed)
        """
        # Resolve model path (handles HuggingFace downloads)
        resolved_ptr = _lib.tokamino_resolve_model_path(model.encode("utf-8"))
        if not resolved_ptr:
            raise RuntimeError(
                f"Failed to resolve model path '{model}'. "
                f"Provide a valid local path or HuggingFace model ID (e.g., 'Qwen/Qwen3-0.6B')."
            )

        self._model_dir = ctypes.cast(resolved_ptr, ctypes.c_char_p).value.decode("utf-8")
        _lib.tokamino_text_free(resolved_ptr)

        model_path = self._model_dir.encode("utf-8")
        if seed == 0:
            self._ptr = _lib.tokamino_session_create(model_path)
        else:
            self._ptr = _lib.tokamino_session_create_with_seed(model_path, seed)

        if not self._ptr:
            raise RuntimeError(f"Failed to load model from {self._model_dir}")

        # Load EOS tokens from session (includes <end_of_turn> and <eos> tokens)
        eos_result = _lib.tokamino_session_get_eos_tokens(self._ptr)
        if eos_result.tokens and eos_result.num_tokens > 0:
            self._eos_tokens = [eos_result.tokens[i] for i in range(eos_result.num_tokens)]
            _lib.tokamino_tokens_free(eos_result.tokens, eos_result.num_tokens)
        else:
            self._eos_tokens = []

    def apply_chat_template(self, user_msg: str, system_msg: str = "") -> str:
        """
        Apply the model's chat template to format a prompt.

        Args:
            user_msg: User message content
            system_msg: Optional system message

        Returns
        -------
            Formatted prompt string, or original user_msg if template fails
        """
        result_ptr = _lib.tokamino_apply_chat_template(
            None,
            self._model_dir.encode("utf-8"),
            system_msg.encode("utf-8"),
            user_msg.encode("utf-8"),
        )
        if result_ptr:
            text = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")
            _lib.tokamino_text_free(result_ptr)
            return text
        return user_msg  # Fallback to raw prompt

    def generate(
        self,
        prompt: str,
        max_tokens: int = 32,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        strategy: int = SamplingStrategy.GREEDY,
        text: bool = False,
        chunk_size: int | None = None,
        chunk_interval_ms: int = 100,
        system_prompt: str = "",
        chat: bool = True,
    ) -> "TokenGenerator":
        """
        Generate tokens from a prompt. Returns an iterator that yields chunks.

        Args:
            prompt: Input prompt text (user message if chat=True)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (1.0 = normal, 0 = greedy)
            top_k: Top-k sampling value
            top_p: Top-p (nucleus) sampling value
            strategy: Sampling strategy (GREEDY, TOP_K, TOP_P)
            text: If True, yields decoded text (str), else token lists (list[int])
            chunk_size: Yield every N tokens (if set, ignores chunk_interval_ms)
            chunk_interval_ms: Yield based on time interval (default 100ms)
            system_prompt: System prompt for chat mode
            chat: If True, apply chat template (default True)

        Returns
        -------
            TokenGenerator iterator that yields chunks:
            - text=True: yields str chunks
            - text=False: yields list[int] token chunks

        Examples
        --------
            # Text chunks (time-based, default 100ms)
            for chunk in session.generate("Hello", max_tokens=100, text=True):
                print(chunk, end="", flush=True)

            # Token chunks (time-based)
            for tokens in session.generate("Hello", max_tokens=100):
                print(tokens)  # list of ints

            # Fixed chunk size (10 tokens per yield)
            for tokens in session.generate("Hello", max_tokens=100, chunk_size=10):
                print(tokens)

            # Single token at a time
            for tokens in session.generate("Hello", max_tokens=100, chunk_size=1):
                print(tokens[0])

            # Collect all at once
            result = session.generate("Hello", max_tokens=100).collect()
            print(result.text)
        """
        # Apply chat template if enabled
        if chat:
            formatted_prompt = self.apply_chat_template(prompt, system_prompt)
        else:
            formatted_prompt = prompt

        return TokenGenerator(
            session=self,
            prompt=formatted_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            strategy=strategy,
            text_mode=text,
            chunk_size=chunk_size,
            chunk_interval_ms=chunk_interval_ms,
        )

    def encode(self, text: str) -> TokenArray:
        """
        Encode text to token IDs.

        Args:
            text: Input text string

        Returns
        -------
            TokenArray with zero-copy NumPy support via __array_interface__

        Example:
            >>> tokens = session.encode("Hello world")
            >>> import numpy as np
            >>> arr = np.asarray(tokens)  # Zero-copy view
        """
        text_bytes = text.encode("utf-8")
        # Create a char array from bytes (supports null bytes, unlike c_char_p)
        text_array = (ctypes.c_char * len(text_bytes)).from_buffer_copy(text_bytes)
        result = _lib.tokamino_encode(self._ptr, text_array, len(text_bytes))

        if result.error_msg:
            error = result.error_msg.decode("utf-8")
            raise RuntimeError(f"Encode failed: {error}")

        return TokenArray(result.tokens, result.num_tokens)

    def decode(self, tokens, num_tokens: int | None = None) -> str:
        """
        Decode token IDs to text.

        Args:
            tokens: TokenArray, list of ints, or pointer to token IDs
            num_tokens: Number of tokens (required if tokens is a pointer)

        Returns
        -------
            Decoded text string

        Example:
            >>> text = session.decode(tokens)
            >>> text = session.decode([128000, 15339, 1917])
        """
        if isinstance(tokens, TokenArray):
            tokens_ptr = tokens._ptr
            num_tokens = len(tokens)
        elif isinstance(tokens, list):
            arr = (ctypes.c_uint32 * len(tokens))(*tokens)
            tokens_ptr = ctypes.cast(arr, ctypes.POINTER(ctypes.c_uint32))
            num_tokens = len(tokens)
        else:
            tokens_ptr = tokens
            if num_tokens is None:
                raise ValueError("num_tokens required when passing raw pointer")

        text_ptr = _lib.tokamino_decode(self._ptr, tokens_ptr, num_tokens)
        if not text_ptr:
            return ""

        # Cast void* to char* and read the string
        text = ctypes.cast(text_ptr, ctypes.c_char_p).value.decode("utf-8")
        _lib.tokamino_text_free(text_ptr)
        return text

    def __del__(self):
        """Free the session when garbage collected."""
        if hasattr(self, "_ptr") and self._ptr:
            _lib.tokamino_session_free(self._ptr)
            self._ptr = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._ptr:
            _lib.tokamino_session_free(self._ptr)
            self._ptr = None
        return False


class TokenGenerator:
    """
    Iterator that yields chunks of tokens or text from generation.

    Chunking is controlled by:
    - chunk_size: Yield every N tokens (if set, ignores interval)
    - chunk_interval_ms: Yield based on time interval (default 100ms)
    """

    DONE_TOKEN = 0xFFFFFFFF

    def __init__(
        self,
        session: "Session",
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_k: int,
        top_p: float,
        strategy: int,
        text_mode: bool,
        chunk_size: int | None,
        chunk_interval_ms: int,
    ):
        self._session = session
        self._text_mode = text_mode
        self._chunk_size = chunk_size
        self._chunk_interval_ms = chunk_interval_ms
        self._started = False
        self._finished = False
        self._gen_ptr = None
        self._tokens: list = []
        self._first_token: int | None = None

        # Build config with EOS tokens
        sampling = SamplingParams(
            strategy=strategy,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )
        self._config = GeneratorConfig(
            max_tokens=max_tokens,
            sampling=sampling,
            flush_interval_ms=chunk_interval_ms,
            eos_tokens=session._eos_tokens if session._eos_tokens else None,
        )
        self._prompt = prompt.encode("utf-8")

        # Buffer for chunking
        self._chunk_buffer: list = []
        self._last_flush_time: float = 0

    def _start(self):
        """Start the generator (lazy initialization)."""
        if self._started:
            return
        self._started = True

        self._gen_ptr = _lib.tokamino_generator_start(
            self._session._ptr,
            self._prompt,
            ctypes.byref(self._config),
        )
        if not self._gen_ptr:
            raise RuntimeError("Failed to start generator")

        # Get first token (generated during prefill)
        self._first_token = _lib.tokamino_generator_current(self._gen_ptr)
        self._tokens.append(self._first_token)

        import time

        self._last_flush_time = time.time()

    def __iter__(self):
        return self

    def __next__(self):
        """Get next chunk (list of tokens or text string)."""
        self._start()
        return self._next_chunk()

    def _should_flush(self) -> bool:
        """Check if we should flush the buffer."""
        if self._chunk_size is not None:
            # Size-based: flush when buffer reaches chunk_size
            return len(self._chunk_buffer) >= self._chunk_size
        else:
            # Time-based: flush when interval elapsed
            import time

            elapsed_ms = (time.time() - self._last_flush_time) * 1000
            return elapsed_ms >= self._chunk_interval_ms

    def _flush_buffer(self):
        """Flush buffer and return chunk (text or token list)."""
        import time

        if self._text_mode:
            result = self._session.decode(self._chunk_buffer)
        else:
            result = self._chunk_buffer.copy()
        self._chunk_buffer.clear()
        self._last_flush_time = time.time()
        return result

    def _next_chunk(self):
        """Yield next chunk of tokens or text."""
        import time

        # First token should be yielded immediately (users want to see output start)
        if self._first_token is not None:
            self._chunk_buffer.append(self._first_token)
            self._first_token = None
            # Yield first token immediately, reset flush timer for subsequent chunks
            self._last_flush_time = time.time()
            return self._flush_buffer()

        # If already finished, flush remaining or stop
        if self._finished:
            if self._chunk_buffer:
                return self._flush_buffer()
            raise StopIteration

        # Collect tokens until flush condition met
        while True:
            token = _lib.tokamino_generator_next(self._gen_ptr)

            if token == self.DONE_TOKEN:
                self._finished = True
                if self._chunk_buffer:
                    return self._flush_buffer()
                raise StopIteration

            self._tokens.append(token)
            self._chunk_buffer.append(token)

            # Check if we should flush after adding token
            if self._should_flush():
                return self._flush_buffer()

    def collect(self) -> "GenerationOutput":
        """
        Consume all remaining tokens and return a GenerationOutput.

        If iteration has already started, collects remaining tokens.
        """
        self._start()

        # Consume first token if not yet consumed
        if self._first_token is not None:
            self._first_token = None

        # Consume remaining tokens
        while not self._finished:
            token = _lib.tokamino_generator_next(self._gen_ptr)
            if token == self.DONE_TOKEN:
                self._finished = True
                break
            self._tokens.append(token)

        # Get stats
        generated_count = _lib.tokamino_generator_generated_count(self._gen_ptr)

        # Decode all tokens
        text = self._session.decode(self._tokens)

        return GenerationOutput(
            tokens=self._tokens.copy(),
            text=text,
            prompt_len=len(self._tokens) - generated_count,
            generated_len=generated_count,
            prefill_time_ms=0,  # TODO: expose from Zig
            decode_time_ms=0,  # TODO: expose from Zig
        )

    def __del__(self):
        """Free the generator."""
        if hasattr(self, "_gen_ptr") and self._gen_ptr:
            _lib.tokamino_generator_free(self._gen_ptr)
            self._gen_ptr = None


class GenerationOutput:
    """
    Output from text generation.

    Tokens are stored as a TokenArray with zero-copy NumPy access.
    """

    def __init__(
        self,
        tokens: TokenArray,
        text: str,
        prompt_len: int,
        generated_len: int,
        prefill_time_ms: float,
        decode_time_ms: float,
    ):
        self.tokens = tokens
        self.text = text
        self.prompt_len = prompt_len
        self.generated_len = generated_len
        self.prefill_time_ms = prefill_time_ms
        self.decode_time_ms = decode_time_ms

    @property
    def total_time_ms(self) -> float:
        """Total generation time in milliseconds."""
        return self.prefill_time_ms + self.decode_time_ms

    @property
    def tokens_per_second(self) -> float:
        """Decode tokens per second."""
        if self.decode_time_ms == 0:
            return 0
        return (self.generated_len - 1) * 1000 / self.decode_time_ms

    def __repr__(self) -> str:
        return (
            f"GenerationOutput(text={self.text!r}, "
            f"generated={self.generated_len} tokens, "
            f"time={self.total_time_ms:.1f}ms, "
            f"speed={self.tokens_per_second:.1f} tok/s)"
        )
