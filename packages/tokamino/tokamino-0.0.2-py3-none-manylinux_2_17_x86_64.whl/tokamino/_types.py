"""
Shared types, constants, and DLPack structures.

This module provides common types used across tokamino.
"""

import ctypes

# =============================================================================
# Constants
# =============================================================================


class DType:
    """Data type enum (matches Zig DType)."""

    FLOAT32 = 0
    FLOAT64 = 1
    INT32 = 2
    INT64 = 3
    FLOAT16 = 4
    BFLOAT16 = 5
    INT8 = 6
    INT16 = 7
    UINT8 = 8
    UINT16 = 9
    UINT32 = 10
    UINT64 = 11
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
DTYPE_TO_TYPESTR = {
    DType.FLOAT32: "<f4",
    DType.FLOAT64: "<f8",
    DType.INT32: "<i4",
    DType.INT64: "<i8",
    DType.FLOAT16: "<f2",
    DType.INT8: "<i1",
    DType.INT16: "<i2",
    DType.UINT8: "<u1",
    DType.UINT16: "<u2",
    DType.UINT32: "<u4",
    DType.UINT64: "<u8",
    DType.GROUPED_AFFINE_U4: "<u1",
    DType.GROUPED_AFFINE_U8: "<u1",
}

# Map dtype to element size
DTYPE_TO_SIZE = {
    DType.FLOAT32: 4,
    DType.FLOAT64: 8,
    DType.INT32: 4,
    DType.INT64: 8,
    DType.FLOAT16: 2,
    DType.INT8: 1,
    DType.INT16: 2,
    DType.UINT8: 1,
    DType.UINT16: 2,
    DType.UINT32: 4,
    DType.UINT64: 8,
    DType.GROUPED_AFFINE_U4: 1,
    DType.GROUPED_AFFINE_U8: 1,
}


# =============================================================================
# DLPack Structures
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
# Sampling Types
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
