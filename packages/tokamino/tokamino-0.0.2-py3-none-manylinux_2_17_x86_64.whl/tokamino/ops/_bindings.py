"""
C API bindings for tokamino ops.

Low-level ctypes bindings to the Zig library functions.
"""

import ctypes

from .._lib import get_lib
from ._errors import check_error

# Get the library handle
_lib = get_lib()

# =============================================================================
# Type definitions
# =============================================================================


# Opaque pointer types
class _Tensor(ctypes.Structure):
    """Opaque tensor pointer."""

    pass


TensorPtr = ctypes.POINTER(_Tensor)


# DLManagedTensor structure (simplified - we only need the pointer)
class _DLManagedTensor(ctypes.Structure):
    """DLPack managed tensor."""

    pass


DLManagedTensorPtr = ctypes.POINTER(_DLManagedTensor)

# =============================================================================
# Function signatures
# =============================================================================

# from_dlpack: DLManagedTensor* -> Tensor*
_lib.tokamino_from_dlpack.argtypes = [ctypes.c_void_p]
_lib.tokamino_from_dlpack.restype = ctypes.c_void_p

# tensor_free_view: Tensor* -> void
_lib.tokamino_tensor_free_view.argtypes = [ctypes.c_void_p]
_lib.tokamino_tensor_free_view.restype = None

# rms_norm: out**, x*, weight*, eps -> error
_lib.tokamino_rms_norm.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_void_p,  # weight
    ctypes.c_float,  # eps
]
_lib.tokamino_rms_norm.restype = ctypes.c_int

# layer_norm: out**, x*, weight*, bias*, eps -> error
_lib.tokamino_layer_norm.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_void_p,  # weight
    ctypes.c_void_p,  # bias (can be null)
    ctypes.c_float,  # eps
]
_lib.tokamino_layer_norm.restype = ctypes.c_int

# silu: out**, x* -> error
_lib.tokamino_silu.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_silu.restype = ctypes.c_int

# gelu: out**, x* -> error
_lib.tokamino_gelu.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_gelu.restype = ctypes.c_int

# softmax: out**, x* -> error
_lib.tokamino_softmax.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_softmax.restype = ctypes.c_int

# softmax_dim: out**, x*, dim -> error (PyTorch-compatible)
_lib.tokamino_softmax_dim.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_int32,  # dim
]
_lib.tokamino_softmax_dim.restype = ctypes.c_int

# rope_freqs: out**, seq_len, head_dim, theta, offset -> error
_lib.tokamino_rope_freqs.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_size_t,  # seq_len
    ctypes.c_size_t,  # head_dim
    ctypes.c_float,  # theta
    ctypes.c_size_t,  # offset
]
_lib.tokamino_rope_freqs.restype = ctypes.c_int

# apply_rope: q*, k*, cos*, sin* -> error
_lib.tokamino_apply_rope.argtypes = [
    ctypes.c_void_p,  # q
    ctypes.c_void_p,  # k
    ctypes.c_void_p,  # cos
    ctypes.c_void_p,  # sin
]
_lib.tokamino_apply_rope.restype = ctypes.c_int

# linear: out**, x*, weight* -> error
_lib.tokamino_linear.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_void_p,  # weight
]
_lib.tokamino_linear.restype = ctypes.c_int

# sdpa: out**, q*, k*, v*, mask*, scale -> error (mask is optional)
_lib.tokamino_sdpa.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # q
    ctypes.c_void_p,  # k
    ctypes.c_void_p,  # v
    ctypes.c_void_p,  # mask (optional, can be NULL)
    ctypes.c_float,  # scale
]
_lib.tokamino_sdpa.restype = ctypes.c_int

# cat: out**, tensors*, num_tensors, dim -> error
_lib.tokamino_cat.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.POINTER(ctypes.c_void_p),  # tensors
    ctypes.c_size_t,  # num_tensors
    ctypes.c_int32,  # dim
]
_lib.tokamino_cat.restype = ctypes.c_int

# transpose: out**, x*, dim0, dim1 -> error
_lib.tokamino_transpose.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_int32,  # dim0
    ctypes.c_int32,  # dim1
]
_lib.tokamino_transpose.restype = ctypes.c_int

# matmul: out**, a*, b* -> error
_lib.tokamino_matmul.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # a
    ctypes.c_void_p,  # b
]
_lib.tokamino_matmul.restype = ctypes.c_int

# embedding: out**, indices*, weight* -> error
_lib.tokamino_embedding.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # indices
    ctypes.c_void_p,  # weight
]
_lib.tokamino_embedding.restype = ctypes.c_int

# relu: out**, x* -> error
_lib.tokamino_relu.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_relu.restype = ctypes.c_int

# sigmoid: out**, x* -> error
_lib.tokamino_sigmoid.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_sigmoid.restype = ctypes.c_int

# tanh: out**, x* -> error
_lib.tokamino_tanh.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_tanh.restype = ctypes.c_int

# rsqrt: out**, x* -> error
_lib.tokamino_rsqrt.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_rsqrt.restype = ctypes.c_int

# zeros: out**, shape*, ndim, dtype -> error
_lib.tokamino_zeros.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.POINTER(ctypes.c_int64),  # shape
    ctypes.c_size_t,  # ndim
    ctypes.c_uint32,  # dtype
]
_lib.tokamino_zeros.restype = ctypes.c_int

# ones: out**, shape*, ndim, dtype -> error
_lib.tokamino_ones.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.POINTER(ctypes.c_int64),  # shape
    ctypes.c_size_t,  # ndim
    ctypes.c_uint32,  # dtype
]
_lib.tokamino_ones.restype = ctypes.c_int

# arange: out**, n, dtype -> error
_lib.tokamino_arange.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_int64,  # n
    ctypes.c_uint32,  # dtype
]
_lib.tokamino_arange.restype = ctypes.c_int

# zeros_like: out**, x* -> error
_lib.tokamino_zeros_like.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_zeros_like.restype = ctypes.c_int

# topk: values**, indices**, x*, k -> error
_lib.tokamino_topk.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # values_ptr
    ctypes.POINTER(ctypes.c_void_p),  # indices_ptr
    ctypes.c_void_p,  # x
    ctypes.c_size_t,  # k
]
_lib.tokamino_topk.restype = ctypes.c_int

# causal_mask: out**, seq_len, dtype -> error
_lib.tokamino_causal_mask.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_size_t,  # seq_len
    ctypes.c_uint32,  # dtype
]
_lib.tokamino_causal_mask.restype = ctypes.c_int

# triu: out**, x*, diagonal -> error
_lib.tokamino_triu.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_int32,  # diagonal
]
_lib.tokamino_triu.restype = ctypes.c_int

# one_hot: out**, indices*, num_classes -> error
_lib.tokamino_one_hot.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # indices
    ctypes.c_size_t,  # num_classes
]
_lib.tokamino_one_hot.restype = ctypes.c_int

# greater_scalar: out**, x*, threshold -> error
_lib.tokamino_greater_scalar.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_float,  # threshold
]
_lib.tokamino_greater_scalar.restype = ctypes.c_int

# nonzero: out**, x* -> error
_lib.tokamino_nonzero.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
]
_lib.tokamino_nonzero.restype = ctypes.c_int

# where: out**, condition*, x*, y* -> error
_lib.tokamino_where.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # condition
    ctypes.c_void_p,  # x
    ctypes.c_void_p,  # y
]
_lib.tokamino_where.restype = ctypes.c_int

# index_add: out (inplace), dim, indices*, source* -> error
_lib.tokamino_index_add.argtypes = [
    ctypes.c_void_p,  # out (inplace)
    ctypes.c_int,  # dim
    ctypes.c_void_p,  # indices
    ctypes.c_void_p,  # source
]
_lib.tokamino_index_add.restype = ctypes.c_int

# slice: out**, x*, starts*, ends*, steps* -> error
_lib.tokamino_slice.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.POINTER(ctypes.c_int64),  # starts
    ctypes.POINTER(ctypes.c_int64),  # ends
    ctypes.POINTER(ctypes.c_int64),  # steps
]
_lib.tokamino_slice.restype = ctypes.c_int

# reshape: out**, x*, shape*, ndim -> error
_lib.tokamino_reshape.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.POINTER(ctypes.c_int64),  # shape
    ctypes.c_size_t,  # ndim
]
_lib.tokamino_reshape.restype = ctypes.c_int

# split: out_ptrs*, num_chunks*, x*, split_size, dim -> error
_lib.tokamino_split.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptrs
    ctypes.POINTER(ctypes.c_size_t),  # num_chunks
    ctypes.c_void_p,  # x
    ctypes.c_int64,  # split_size
    ctypes.c_int32,  # dim
]
_lib.tokamino_split.restype = ctypes.c_int

# unsqueeze: out**, x*, dim -> error
_lib.tokamino_unsqueeze.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_int32,  # dim
]
_lib.tokamino_unsqueeze.restype = ctypes.c_int

# squeeze: out**, x*, dim -> error
_lib.tokamino_squeeze.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_int32,  # dim
]
_lib.tokamino_squeeze.restype = ctypes.c_int

# expand: out**, x*, shape*, ndim -> error
_lib.tokamino_expand.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.POINTER(ctypes.c_int64),  # shape
    ctypes.c_size_t,  # ndim
]
_lib.tokamino_expand.restype = ctypes.c_int

# repeat_interleave: out**, x*, repeats, dim -> error
_lib.tokamino_repeat_interleave.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # x
    ctypes.c_int64,  # repeats
    ctypes.c_int32,  # dim
]
_lib.tokamino_repeat_interleave.restype = ctypes.c_int

# mxfp4_matmul: input*, weights*, scales*, output*, bias*, batch, in_f, out_f -> error
_lib.tokamino_mxfp4_matmul.argtypes = [
    ctypes.c_void_p,  # input_ptr (f32)
    ctypes.c_void_p,  # weight_blocks_ptr (u8)
    ctypes.c_void_p,  # scales_ptr (u8 E8M0)
    ctypes.c_void_p,  # output_ptr (f32)
    ctypes.c_void_p,  # bias_ptr (f32, optional)
    ctypes.c_size_t,  # batch
    ctypes.c_size_t,  # in_features
    ctypes.c_size_t,  # out_features
]
_lib.tokamino_mxfp4_matmul.restype = ctypes.c_int

# mxfp4_matmul_bf16: input*, weights*, scales*, output*, bias*, batch, in_f, out_f -> error
_lib.tokamino_mxfp4_matmul_bf16.argtypes = [
    ctypes.c_void_p,  # input_ptr (bf16 as u16)
    ctypes.c_void_p,  # weight_blocks_ptr (u8)
    ctypes.c_void_p,  # scales_ptr (u8 E8M0)
    ctypes.c_void_p,  # output_ptr (f32)
    ctypes.c_void_p,  # bias_ptr (f32, optional)
    ctypes.c_size_t,  # batch
    ctypes.c_size_t,  # in_features
    ctypes.c_size_t,  # out_features
]
_lib.tokamino_mxfp4_matmul_bf16.restype = ctypes.c_int

# mxfp4_linear: out**, input*, weights*, scales*, bias*, out_features -> error
_lib.tokamino_mxfp4_linear.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # input
    ctypes.c_void_p,  # weight_blocks
    ctypes.c_void_p,  # scales
    ctypes.c_void_p,  # bias (can be null)
    ctypes.c_size_t,  # out_features
]
_lib.tokamino_mxfp4_linear.restype = ctypes.c_int

# Tensor accessors (from wrapper.py, re-declared for ops)
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

_lib.tokamino_tensor_numel.argtypes = [ctypes.c_void_p]
_lib.tokamino_tensor_numel.restype = ctypes.c_size_t

_lib.tokamino_tensor_element_size.argtypes = [ctypes.c_void_p]
_lib.tokamino_tensor_element_size.restype = ctypes.c_size_t

_lib.tokamino_tensor_is_cpu.argtypes = [ctypes.c_void_p]
_lib.tokamino_tensor_is_cpu.restype = ctypes.c_bool

_lib.tokamino_tensor_to_dlpack.argtypes = [ctypes.c_void_p]
_lib.tokamino_tensor_to_dlpack.restype = ctypes.c_void_p

_lib.tokamino_tensor_free.argtypes = [ctypes.c_void_p]
_lib.tokamino_tensor_free.restype = None

# =============================================================================
# Wrapper functions
# =============================================================================


def from_dlpack(capsule) -> int:
    """
    Create a Tensor from a DLPack capsule (zero-copy).

    Args:
        capsule: PyCapsule containing DLManagedTensor*

    Returns
    -------
        Pointer to Tensor (as int)
    """
    # Set up PyCapsule_GetPointer signature (must set argtypes for proper calling)
    ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
    ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p

    # Extract the pointer from the PyCapsule (pass capsule directly, not wrapped)
    ptr = ctypes.pythonapi.PyCapsule_GetPointer(capsule, b"dltensor")

    result = _lib.tokamino_from_dlpack(ptr)
    if result is None or result == 0:
        raise RuntimeError("Failed to create tensor from DLPack")

    # Mark capsule as used (rename to prevent double-free)
    ctypes.pythonapi.PyCapsule_SetName.argtypes = [ctypes.py_object, ctypes.c_char_p]
    ctypes.pythonapi.PyCapsule_SetName.restype = ctypes.c_int
    ctypes.pythonapi.PyCapsule_SetName(capsule, b"used_dltensor")

    return result


def free_view(ptr: int) -> None:
    """Free a tensor view (does not free underlying data)."""
    _lib.tokamino_tensor_free_view(ptr)


def free_tensor(ptr: int) -> None:
    """Free a tensor and its data."""
    _lib.tokamino_tensor_free(ptr)


def rms_norm(x_ptr: int, weight_ptr: int, eps: float = 1e-6) -> int:
    """
    RMS normalization.

    Args:
        x_ptr: Input tensor pointer
        weight_ptr: Weight tensor pointer
        eps: Epsilon for numerical stability

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_rms_norm(ctypes.byref(out_ptr), x_ptr, weight_ptr, eps)
    check_error(err, "rms_norm")
    return out_ptr.value


def layer_norm(x_ptr: int, weight_ptr: int, bias_ptr: int | None, eps: float = 1e-5) -> int:
    """
    Layer normalization.

    Args:
        x_ptr: Input tensor pointer
        weight_ptr: Weight tensor pointer
        bias_ptr: Optional bias tensor pointer (can be None)
        eps: Epsilon for numerical stability

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_layer_norm(ctypes.byref(out_ptr), x_ptr, weight_ptr, bias_ptr, eps)
    check_error(err, "layer_norm")
    return out_ptr.value


def silu(x_ptr: int) -> int:
    """
    SiLU activation (x * sigmoid(x)).

    Args:
        x_ptr: Input tensor pointer

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_silu(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "silu")
    return out_ptr.value


def gelu(x_ptr: int) -> int:
    """
    GELU activation (approximate).

    Args:
        x_ptr: Input tensor pointer

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_gelu(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "gelu")
    return out_ptr.value


def softmax(x_ptr: int, dim: int = -1) -> int:
    """
    Softmax along specified dimension (PyTorch-compatible).

    Args:
        x_ptr: Input tensor pointer
        dim: Dimension to apply softmax over (default: -1, last dim)

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_softmax_dim(ctypes.byref(out_ptr), x_ptr, dim)
    check_error(err, "softmax")
    return out_ptr.value


def rope_freqs(seq_len: int, head_dim: int, theta: float = 10000.0, offset: int = 0) -> int:
    """
    Compute RoPE frequencies (combined cos/sin tensor).

    The C API returns a single tensor with shape [seq_len, head_dim] where:
    - First half of dim 1 contains cos values
    - Second half of dim 1 contains sin values

    Args:
        seq_len: Sequence length
        head_dim: Head dimension (must be even)
        theta: RoPE theta parameter (default: 10000.0)
        offset: Position offset for continuing generation

    Returns
    -------
        Combined tensor pointer [seq_len, head_dim]
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_rope_freqs(
        ctypes.byref(out_ptr),
        seq_len,
        head_dim,
        theta,
        offset,
    )
    check_error(err, "rope_freqs")
    return out_ptr.value


def apply_rope(q_ptr: int, k_ptr: int, cos_ptr: int, sin_ptr: int) -> None:
    """
    Apply RoPE to Q and K tensors in-place.

    Args:
        q_ptr: Q tensor pointer (modified in-place)
        k_ptr: K tensor pointer (modified in-place)
        cos_ptr: Cos frequencies tensor pointer
        sin_ptr: Sin frequencies tensor pointer
    """
    err = _lib.tokamino_apply_rope(q_ptr, k_ptr, cos_ptr, sin_ptr)
    check_error(err, "apply_rope")


def linear(x_ptr: int, weight_ptr: int) -> int:
    """Compute linear projection: out = x @ weight.T.

    Args:
        x_ptr: Input tensor pointer [batch, in_features]
        weight_ptr: Weight tensor pointer [out_features, in_features]

    Returns
    -------
        Output tensor pointer [batch, out_features]
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_linear(ctypes.byref(out_ptr), x_ptr, weight_ptr)
    check_error(err, "linear")
    return out_ptr.value


def linear_bias(x_ptr: int, weight_ptr: int, bias_ptr: int = None) -> int:
    """Compute linear projection with optional bias: out = x @ weight.T + bias.

    Args:
        x_ptr: Input tensor pointer [batch, in_features]
        weight_ptr: Weight tensor pointer [out_features, in_features]
        bias_ptr: Optional bias tensor pointer [out_features]

    Returns
    -------
        Output tensor pointer [batch, out_features]
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_linear_bias(ctypes.byref(out_ptr), x_ptr, weight_ptr, bias_ptr)
    check_error(err, "linear_bias")
    return out_ptr.value


def sdpa(
    q_ptr: int,
    k_ptr: int,
    v_ptr: int,
    attn_mask_ptr: int = None,
    scale: float = 0.0,
) -> int:
    """
    Scaled dot-product attention (PyTorch-compatible).

    Computes: softmax(Q @ K.T / sqrt(d_k) + attn_mask) @ V

    Args:
        q_ptr: Query tensor pointer [batch, n_heads, seq_q, head_dim]
        k_ptr: Key tensor pointer [batch, n_heads, seq_kv, head_dim]
        v_ptr: Value tensor pointer [batch, n_heads, seq_kv, head_dim]
        attn_mask_ptr: Optional attention mask pointer (additive, 0 = attend, -inf = mask)
        scale: Attention scale (0 = auto: 1/sqrt(head_dim))

    Returns
    -------
        Output tensor pointer [batch, n_heads, seq_q, head_dim]
    """
    # Convert mask pointer: None -> NULL, int -> c_void_p
    mask_arg = attn_mask_ptr if attn_mask_ptr is not None else None
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_sdpa(ctypes.byref(out_ptr), q_ptr, k_ptr, v_ptr, mask_arg, scale)
    check_error(err, "sdpa")
    return out_ptr.value


def cat(tensor_ptrs: list, dim: int = 0) -> int:
    """Concatenate tensors along a dimension."""
    n = len(tensor_ptrs)
    arr = (ctypes.c_void_p * n)(*tensor_ptrs)
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_cat(ctypes.byref(out_ptr), arr, n, dim)
    check_error(err, "cat")
    return out_ptr.value


def transpose(x_ptr: int, dim0: int, dim1: int) -> int:
    """Transpose tensor dimensions."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_transpose(ctypes.byref(out_ptr), x_ptr, dim0, dim1)
    check_error(err, "transpose")
    return out_ptr.value


def matmul(a_ptr: int, b_ptr: int) -> int:
    """Compute matrix multiplication: out = a @ b."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_matmul(ctypes.byref(out_ptr), a_ptr, b_ptr)
    check_error(err, "matmul")
    return out_ptr.value


def embedding(indices_ptr: int, weight_ptr: int) -> int:
    """Perform embedding lookup: out = weight[indices]."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_embedding(ctypes.byref(out_ptr), indices_ptr, weight_ptr)
    check_error(err, "embedding")
    return out_ptr.value


def relu(x_ptr: int) -> int:
    """ReLU activation."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_relu(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "relu")
    return out_ptr.value


def sigmoid(x_ptr: int) -> int:
    """Sigmoid activation."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_sigmoid(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "sigmoid")
    return out_ptr.value


def tanh(x_ptr: int) -> int:
    """Tanh activation."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_tanh(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "tanh")
    return out_ptr.value


def rsqrt(x_ptr: int) -> int:
    """Reciprocal square root: 1 / sqrt(x)."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_rsqrt(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "rsqrt")
    return out_ptr.value


def zeros(shape: tuple, dtype: int = 0) -> int:
    """Create tensor filled with zeros."""
    n = len(shape)
    shape_arr = (ctypes.c_int64 * n)(*shape)
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_zeros(ctypes.byref(out_ptr), shape_arr, n, dtype)
    check_error(err, "zeros")
    return out_ptr.value


def ones(shape: tuple, dtype: int = 0) -> int:
    """Create tensor filled with ones."""
    n = len(shape)
    shape_arr = (ctypes.c_int64 * n)(*shape)
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_ones(ctypes.byref(out_ptr), shape_arr, n, dtype)
    check_error(err, "ones")
    return out_ptr.value


def arange(n: int, dtype: int = 0) -> int:
    """Create arange tensor [0, 1, ..., n-1]."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_arange(ctypes.byref(out_ptr), n, dtype)
    check_error(err, "arange")
    return out_ptr.value


def zeros_like(x_ptr: int) -> int:
    """Create zeros tensor with same shape/dtype as input."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_zeros_like(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "zeros_like")
    return out_ptr.value


def topk(x_ptr: int, k: int) -> tuple:
    """Top-k selection along last dimension. Returns (values_ptr, indices_ptr)."""
    values_ptr = ctypes.c_void_p()
    indices_ptr = ctypes.c_void_p()
    err = _lib.tokamino_topk(ctypes.byref(values_ptr), ctypes.byref(indices_ptr), x_ptr, k)
    check_error(err, "topk")
    return values_ptr.value, indices_ptr.value


def causal_mask(seq_len: int, dtype: int = 0) -> int:
    """Create causal attention mask."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_causal_mask(ctypes.byref(out_ptr), seq_len, dtype)
    check_error(err, "causal_mask")
    return out_ptr.value


def triu(x_ptr: int, diagonal: int = 0) -> int:
    """Upper triangular matrix."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_triu(ctypes.byref(out_ptr), x_ptr, diagonal)
    check_error(err, "triu")
    return out_ptr.value


def one_hot(indices_ptr: int, num_classes: int) -> int:
    """One-hot encoding. Returns [N, num_classes] float32 tensor."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_one_hot(ctypes.byref(out_ptr), indices_ptr, num_classes)
    check_error(err, "one_hot")
    return out_ptr.value


def greater_scalar(x_ptr: int, threshold: float) -> int:
    """Element-wise greater than. Returns int64 tensor with 1 where x > threshold."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_greater_scalar(ctypes.byref(out_ptr), x_ptr, threshold)
    check_error(err, "greater_scalar")
    return out_ptr.value


def nonzero(x_ptr: int) -> int:
    """Return indices where tensor is non-zero. Returns [num_nonzero, ndim] int64."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_nonzero(ctypes.byref(out_ptr), x_ptr)
    check_error(err, "nonzero")
    return out_ptr.value


def where(condition_ptr: int, x_ptr: int, y_ptr: int) -> int:
    """Element-wise selection: where(condition, x, y)."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_where(ctypes.byref(out_ptr), condition_ptr, x_ptr, y_ptr)
    check_error(err, "where")
    return out_ptr.value


def index_add(out_ptr: int, dim: int, indices_ptr: int, source_ptr: int) -> None:
    """In-place index_add: out[indices] += source along dim."""
    err = _lib.tokamino_index_add(out_ptr, dim, indices_ptr, source_ptr)
    check_error(err, "index_add")


def to_dlpack(ptr: int):
    """
    Convert tensor to DLPack capsule.

    Args:
        ptr: Tensor pointer

    Returns
    -------
        PyCapsule containing DLManagedTensor*
    """
    dl_ptr = _lib.tokamino_tensor_to_dlpack(ptr)
    if dl_ptr is None or dl_ptr == 0:
        raise RuntimeError("Failed to convert tensor to DLPack")

    # Create PyCapsule with deleter
    PyCapsule_New = ctypes.pythonapi.PyCapsule_New
    PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
    PyCapsule_New.restype = ctypes.py_object

    # Note: The deleter is handled by DLPack protocol - consumer calls it
    capsule = PyCapsule_New(dl_ptr, b"dltensor", None)
    return capsule


# Tensor info functions
def get_shape(ptr: int) -> tuple:
    """Get tensor shape as tuple."""
    ndim = _lib.tokamino_tensor_ndim(ptr)
    shape_ptr = _lib.tokamino_tensor_shape(ptr)
    return tuple(shape_ptr[i] for i in range(ndim))


def get_dtype(ptr: int) -> int:
    """Get tensor dtype enum value."""
    return _lib.tokamino_tensor_dtype(ptr)


def get_numel(ptr: int) -> int:
    """Get number of elements."""
    return _lib.tokamino_tensor_numel(ptr)


def get_ndim(ptr: int) -> int:
    """Get number of dimensions."""
    return _lib.tokamino_tensor_ndim(ptr)


def slice_tensor(x_ptr: int, starts: list, ends: list, steps: list) -> int:
    """
    Slice tensor along multiple dimensions.

    Args:
        x_ptr: Input tensor pointer
        starts: Start indices for each dimension
        ends: End indices for each dimension (maxInt for "to end")
        steps: Step sizes for each dimension

    Returns
    -------
        Output tensor pointer
    """
    ndim = len(starts)
    starts_arr = (ctypes.c_int64 * ndim)(*starts)
    ends_arr = (ctypes.c_int64 * ndim)(*ends)
    steps_arr = (ctypes.c_int64 * ndim)(*steps)
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_slice(ctypes.byref(out_ptr), x_ptr, starts_arr, ends_arr, steps_arr)
    check_error(err, "slice")
    return out_ptr.value


def reshape(x_ptr: int, shape: tuple) -> int:
    """
    Reshape tensor.

    Args:
        x_ptr: Input tensor pointer
        shape: New shape (use -1 for one inferred dimension)

    Returns
    -------
        Output tensor pointer
    """
    ndim = len(shape)
    shape_arr = (ctypes.c_int64 * ndim)(*shape)
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_reshape(ctypes.byref(out_ptr), x_ptr, shape_arr, ndim)
    check_error(err, "reshape")
    return out_ptr.value


def split(x_ptr: int, split_size: int, dim: int = 0, max_chunks: int = 64) -> list:
    """
    Split tensor into chunks along dimension.

    Args:
        x_ptr: Input tensor pointer
        split_size: Size of each chunk
        dim: Dimension to split along
        max_chunks: Maximum number of chunks to allocate

    Returns
    -------
        List of output tensor pointers
    """
    out_ptrs = (ctypes.c_void_p * max_chunks)()
    num_chunks = ctypes.c_size_t()
    err = _lib.tokamino_split(out_ptrs, ctypes.byref(num_chunks), x_ptr, split_size, dim)
    check_error(err, "split")
    return [out_ptrs[i] for i in range(num_chunks.value)]


def unsqueeze(x_ptr: int, dim: int) -> int:
    """
    Add dimension of size 1.

    Args:
        x_ptr: Input tensor pointer
        dim: Position to add dimension

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_unsqueeze(ctypes.byref(out_ptr), x_ptr, dim)
    check_error(err, "unsqueeze")
    return out_ptr.value


def squeeze(x_ptr: int, dim: int = -1) -> int:
    """
    Remove dimensions of size 1.

    Args:
        x_ptr: Input tensor pointer
        dim: Specific dimension to squeeze (-1 = all)

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_squeeze(ctypes.byref(out_ptr), x_ptr, dim)
    check_error(err, "squeeze")
    return out_ptr.value


def expand(x_ptr: int, shape: tuple) -> int:
    """
    Expand tensor to new shape (broadcasting).

    Args:
        x_ptr: Input tensor pointer
        shape: New shape (use -1 to keep original size)

    Returns
    -------
        Output tensor pointer
    """
    ndim = len(shape)
    shape_arr = (ctypes.c_int64 * ndim)(*shape)
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_expand(ctypes.byref(out_ptr), x_ptr, shape_arr, ndim)
    check_error(err, "expand")
    return out_ptr.value


def repeat_interleave(x_ptr: int, repeats: int, dim: int) -> int:
    """
    Repeat elements along dimension.

    Args:
        x_ptr: Input tensor pointer
        repeats: Number of times to repeat each element
        dim: Dimension along which to repeat

    Returns
    -------
        Output tensor pointer
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_repeat_interleave(ctypes.byref(out_ptr), x_ptr, repeats, dim)
    check_error(err, "repeat_interleave")
    return out_ptr.value


def mxfp4_matmul(
    input_ptr: int,
    weight_blocks_ptr: int,
    scales_ptr: int,
    output_ptr: int,
    bias_ptr: int | None,
    batch: int,
    in_features: int,
    out_features: int,
) -> None:
    """
    MXFP4 matrix multiplication with native E8M0 scales (no pre-conversion).

    Args:
        input_ptr: Input tensor data pointer (f32)
        weight_blocks_ptr: Packed 4-bit weights data pointer (u8)
        scales_ptr: E8M0 scales data pointer (u8, NOT pre-converted)
        output_ptr: Output tensor data pointer (f32, pre-allocated)
        bias_ptr: Optional bias data pointer (f32)
        batch: Batch size
        in_features: Input feature dimension
        out_features: Output feature dimension
    """
    err = _lib.tokamino_mxfp4_matmul(
        input_ptr,
        weight_blocks_ptr,
        scales_ptr,
        output_ptr,
        bias_ptr if bias_ptr else None,
        batch,
        in_features,
        out_features,
    )
    check_error(err, "mxfp4_matmul")


def mxfp4_matmul_bf16(
    input_ptr: int,
    weight_blocks_ptr: int,
    scales_ptr: int,
    output_ptr: int,
    bias_ptr: int | None,
    batch: int,
    in_features: int,
    out_features: int,
) -> None:
    """
    MXFP4 matrix multiplication with bfloat16 input (zero-copy).

    Converts bf16->f32 on-the-fly in the kernel, avoiding Python-side copies.

    Args:
        input_ptr: Input tensor data pointer (bf16 as u16)
        weight_blocks_ptr: Packed 4-bit weights data pointer (u8)
        scales_ptr: E8M0 scales data pointer (u8, NOT pre-converted)
        output_ptr: Output tensor data pointer (f32, pre-allocated)
        bias_ptr: Optional bias data pointer (f32)
        batch: Batch size
        in_features: Input feature dimension
        out_features: Output feature dimension
    """
    err = _lib.tokamino_mxfp4_matmul_bf16(
        input_ptr,
        weight_blocks_ptr,
        scales_ptr,
        output_ptr,
        bias_ptr if bias_ptr else None,
        batch,
        in_features,
        out_features,
    )
    check_error(err, "mxfp4_matmul_bf16")


# =============================================================================
# KV Cache bindings
# =============================================================================

# kv_cache_create: n_layers, n_kv_heads, head_dim, max_seq_len, sliding_window -> KVCache*
_lib.tokamino_kv_cache_create.argtypes = [
    ctypes.c_size_t,  # n_layers
    ctypes.c_size_t,  # n_kv_heads
    ctypes.c_size_t,  # head_dim
    ctypes.c_size_t,  # max_seq_len
    ctypes.c_size_t,  # sliding_window
]
_lib.tokamino_kv_cache_create.restype = ctypes.c_void_p

# kv_cache_destroy: cache* -> void
_lib.tokamino_kv_cache_destroy.argtypes = [ctypes.c_void_p]
_lib.tokamino_kv_cache_destroy.restype = None

# kv_cache_update: cache*, layer_idx, k*, v* -> error
_lib.tokamino_kv_cache_update.argtypes = [
    ctypes.c_void_p,  # cache
    ctypes.c_size_t,  # layer_idx
    ctypes.c_void_p,  # k
    ctypes.c_void_p,  # v
]
_lib.tokamino_kv_cache_update.restype = ctypes.c_int

# kv_cache_advance: cache*, steps -> void
_lib.tokamino_kv_cache_advance.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
_lib.tokamino_kv_cache_advance.restype = None

# kv_cache_length: cache* -> size_t
_lib.tokamino_kv_cache_length.argtypes = [ctypes.c_void_p]
_lib.tokamino_kv_cache_length.restype = ctypes.c_size_t

# kv_cache_reset: cache* -> void
_lib.tokamino_kv_cache_reset.argtypes = [ctypes.c_void_p]
_lib.tokamino_kv_cache_reset.restype = None

# kv_cache_get_k: out**, cache*, layer_idx -> error
_lib.tokamino_kv_cache_get_k.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.c_void_p,
    ctypes.c_size_t,
]
_lib.tokamino_kv_cache_get_k.restype = ctypes.c_int

# kv_cache_get_v: out**, cache*, layer_idx -> error
_lib.tokamino_kv_cache_get_v.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.c_void_p,
    ctypes.c_size_t,
]
_lib.tokamino_kv_cache_get_v.restype = ctypes.c_int


def kv_cache_create(
    n_layers: int,
    n_kv_heads: int,
    head_dim: int,
    max_seq_len: int,
    sliding_window: int = 0,
) -> int:
    """Create a new KV cache."""
    ptr = _lib.tokamino_kv_cache_create(n_layers, n_kv_heads, head_dim, max_seq_len, sliding_window)
    if ptr is None or ptr == 0:
        raise MemoryError("Failed to create KV cache")
    return ptr


def kv_cache_destroy(cache_ptr: int) -> None:
    """Destroy a KV cache."""
    _lib.tokamino_kv_cache_destroy(cache_ptr)


def kv_cache_update(cache_ptr: int, layer_idx: int, k_ptr: int, v_ptr: int) -> None:
    """Update KV cache with new K/V tensors."""
    err = _lib.tokamino_kv_cache_update(cache_ptr, layer_idx, k_ptr, v_ptr)
    check_error(err, "kv_cache_update")


def kv_cache_advance(cache_ptr: int, steps: int) -> None:
    """Advance cache position."""
    _lib.tokamino_kv_cache_advance(cache_ptr, steps)


def kv_cache_length(cache_ptr: int) -> int:
    """Get current cache length."""
    return _lib.tokamino_kv_cache_length(cache_ptr)


def kv_cache_reset(cache_ptr: int) -> None:
    """Reset cache to empty state."""
    _lib.tokamino_kv_cache_reset(cache_ptr)


def kv_cache_get_k(cache_ptr: int, layer_idx: int) -> int | None:
    """Get K cache tensor for a layer."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_kv_cache_get_k(ctypes.byref(out_ptr), cache_ptr, layer_idx)
    check_error(err, "kv_cache_get_k")
    return out_ptr.value if out_ptr.value else None


def kv_cache_get_v(cache_ptr: int, layer_idx: int) -> int | None:
    """Get V cache tensor for a layer."""
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_kv_cache_get_v(ctypes.byref(out_ptr), cache_ptr, layer_idx)
    check_error(err, "kv_cache_get_v")
    return out_ptr.value if out_ptr.value else None


# attention_with_kv_cache: out**, q*, k*, v*, cache*, layer_idx, scale -> error
_lib.tokamino_attention_with_kv_cache.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # q
    ctypes.c_void_p,  # k
    ctypes.c_void_p,  # v
    ctypes.c_void_p,  # cache
    ctypes.c_size_t,  # layer_idx
    ctypes.c_float,  # scale
]
_lib.tokamino_attention_with_kv_cache.restype = ctypes.c_int


def attention_with_kv_cache(
    q_ptr: int,
    k_ptr: int,
    v_ptr: int,
    cache_ptr: int,
    layer_idx: int,
    scale: float = 0.0,
) -> int:
    """
    Attention with KV cache.

    Performs SDPA using cached K/V from previous positions with causal masking.
    Updates the cache with new K/V and advances the cache position.

    Args:
        q_ptr: Query tensor pointer [batch, n_heads, seq_len, head_dim]
        k_ptr: Key tensor pointer [batch, n_kv_heads, seq_len, head_dim]
        v_ptr: Value tensor pointer [batch, n_kv_heads, seq_len, head_dim]
        cache_ptr: KVCache pointer
        layer_idx: Layer index (0-indexed)
        scale: Attention scale (0 = auto: 1/sqrt(head_dim))

    Returns
    -------
        Output tensor pointer [batch, n_heads, seq_len, head_dim]
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_attention_with_kv_cache(
        ctypes.byref(out_ptr), q_ptr, k_ptr, v_ptr, cache_ptr, layer_idx, scale
    )
    check_error(err, "attention_with_kv_cache")
    return out_ptr.value


# attention_with_sinks: out**, q*, k*, v*, cache*, layer_idx, sinks*, sliding_window, scale -> error
_lib.tokamino_attention_with_sinks.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # q
    ctypes.c_void_p,  # k
    ctypes.c_void_p,  # v
    ctypes.c_void_p,  # cache
    ctypes.c_size_t,  # layer_idx
    ctypes.c_void_p,  # sinks (can be null)
    ctypes.c_size_t,  # sliding_window
    ctypes.c_float,  # scale
]
_lib.tokamino_attention_with_sinks.restype = ctypes.c_int


def attention_with_sinks(
    q_ptr: int,
    k_ptr: int,
    v_ptr: int,
    cache_ptr: int,
    layer_idx: int,
    sinks_ptr: int | None = None,
    sliding_window: int = 0,
    scale: float = 0.0,
) -> int:
    """
    Attention with KV cache, optional sinks, and sliding window.

    This is an extended version of attention_with_kv_cache that supports:
    - sinks: per-head learnable logits added to softmax denominator (GPT-OSS style)
    - sliding_window: limit attention to most recent N positions (0 = disabled)

    Args:
        q_ptr: Query tensor pointer [batch, n_heads, seq_len, head_dim]
        k_ptr: Key tensor pointer [batch, n_kv_heads, seq_len, head_dim]
        v_ptr: Value tensor pointer [batch, n_kv_heads, seq_len, head_dim]
        cache_ptr: KVCache pointer
        layer_idx: Layer index (0-indexed)
        sinks_ptr: Optional sink logits tensor pointer [n_heads]
        sliding_window: Sliding window size (0 = disabled)
        scale: Attention scale (0 = auto: 1/sqrt(head_dim))

    Returns
    -------
        Output tensor pointer [batch, n_heads, seq_len, head_dim]
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_attention_with_sinks(
        ctypes.byref(out_ptr),
        q_ptr,
        k_ptr,
        v_ptr,
        cache_ptr,
        layer_idx,
        sinks_ptr,
        sliding_window,
        scale,
    )
    check_error(err, "attention_with_sinks")
    return out_ptr.value


# =============================================================================
# Quantized Linear bindings (Q4_0, Q8_0)
# =============================================================================

# linear_q4: out**, input*, weights*, bias*, out_features -> error
_lib.tokamino_linear_q4.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # input
    ctypes.c_void_p,  # weights
    ctypes.c_void_p,  # bias (can be null)
    ctypes.c_size_t,  # out_features
]
_lib.tokamino_linear_q4.restype = ctypes.c_int

# linear_q8: out**, input*, weights*, bias*, out_features -> error
_lib.tokamino_linear_q8.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),  # out_ptr
    ctypes.c_void_p,  # input
    ctypes.c_void_p,  # weights
    ctypes.c_void_p,  # bias (can be null)
    ctypes.c_size_t,  # out_features
]
_lib.tokamino_linear_q8.restype = ctypes.c_int


def linear_q4(
    input_ptr: int,
    weights_ptr: int,
    bias_ptr: int | None,
    out_features: int,
) -> int:
    """
    Q4_0 quantized linear layer.

    Args:
        input_ptr: Input tensor pointer [batch, in_features] as f32
        weights_ptr: Weights pointer (BlockQ4_0 format as uint8)
        bias_ptr: Optional bias pointer [out_features] as f32
        out_features: Number of output features

    Returns
    -------
        Output tensor pointer [batch, out_features] as f32
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_linear_q4(
        ctypes.byref(out_ptr), input_ptr, weights_ptr, bias_ptr, out_features
    )
    check_error(err, "linear_q4")
    return out_ptr.value


def linear_q8(
    input_ptr: int,
    weights_ptr: int,
    bias_ptr: int | None,
    out_features: int,
) -> int:
    """
    Q8_0 quantized linear layer.

    Args:
        input_ptr: Input tensor pointer [batch, in_features] as f32
        weights_ptr: Weights pointer (BlockQ8_0 format as uint8)
        bias_ptr: Optional bias pointer [out_features] as f32
        out_features: Number of output features

    Returns
    -------
        Output tensor pointer [batch, out_features] as f32
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_linear_q8(
        ctypes.byref(out_ptr), input_ptr, weights_ptr, bias_ptr, out_features
    )
    check_error(err, "linear_q8")
    return out_ptr.value


def mxfp4_linear(
    input_ptr: int,
    weights_ptr: int,
    scales_ptr: int,
    bias_ptr: int | None,
    out_features: int,
) -> int:
    """
    MXFP4 linear layer (Tensor-based, allocates output).

    Args:
        input_ptr: Input tensor pointer [batch, in_features] as f32 or bf16
        weights_ptr: Packed 4-bit weights pointer [out_features * n_groups * 16] as uint8
        scales_ptr: E8M0 scales pointer [out_features * n_groups] as uint8
        bias_ptr: Optional bias pointer [out_features] as f32
        out_features: Number of output features

    Returns
    -------
        Output tensor pointer [batch, out_features] as f32
    """
    out_ptr = ctypes.c_void_p()
    err = _lib.tokamino_mxfp4_linear(
        ctypes.byref(out_ptr), input_ptr, weights_ptr, scales_ptr, bias_ptr, out_features
    )
    check_error(err, "mxfp4_linear")
    return out_ptr.value


def mxfp4_matmul_f32scales(
    input_ptr: int,
    weight_blocks_ptr: int,
    scales_ptr: int,
    output_ptr: int,
    bias_ptr: int | None,
    batch: int,
    in_features: int,
    out_features: int,
) -> None:
    """
    MXFP4 matrix multiplication with pre-converted f32 scales (faster path).

    Uses 4x more memory for scales but avoids per-group E8M0 conversion.

    Args:
        input_ptr: Input tensor data pointer (f32)
        weight_blocks_ptr: Packed 4-bit weights data pointer (u8)
        scales_ptr: Pre-converted scales data pointer (f32)
        output_ptr: Output tensor data pointer (f32, pre-allocated)
        bias_ptr: Optional bias data pointer (f32)
        batch: Batch size
        in_features: Input feature dimension
        out_features: Output feature dimension
    """
    err = _lib.tokamino_mxfp4_matmul_f32scales(
        input_ptr,
        weight_blocks_ptr,
        scales_ptr,
        output_ptr,
        bias_ptr if bias_ptr else None,
        batch,
        in_features,
        out_features,
    )
    check_error(err, "mxfp4_matmul_f32scales")
