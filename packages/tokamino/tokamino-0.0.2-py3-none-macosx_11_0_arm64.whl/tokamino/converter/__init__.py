"""
Model Conversion API.

This module provides functionality to convert HuggingFace models to optimized
quantized formats for efficient inference with tokamino.

Two Output Formats
------------------

**Native Format** (default, recommended)
    Uses K-quant quantization (Q4_K_M, Q6_K, Q8_0) stored in SafeTensors.
    Provides the best quality-per-bit and is optimized for tokamino's runtime.
    Only works with tokamino.

**MLX Format**
    Uses grouped-affine quantization compatible with Apple's MLX framework.
    Use this when you need to share models with MLX users or run on both
    tokamino and MLX.

When to Convert
---------------

Convert models when you want to:

- Reduce memory usage (4-bit uses ~4x less memory than 16-bit)
- Speed up inference on CPU (quantized models are faster)
- Deploy models to resource-constrained environments

Quick Start
-----------

Convert a model to 4-bit quantized format::

    import tokamino

    # Using the Converter class (recommended for repeated conversions)
    converter = tokamino.Converter()
    path = converter("Qwen/Qwen3-0.6B", bits=4)

    # Or use the convert function for one-off conversions
    path = tokamino.convert("Qwen/Qwen3-0.6B", bits=4)

    # Use the converted model
    session = tokamino.ChatSession(path)
    response = session("Hello!")

See Also
--------
tokamino.ChatSession : Load and run inference on converted models.
tokamino.generate : Quick one-off generation without explicit conversion.
"""

from .converter import (
    MLX_BITS,
    NATIVE_QUANT_TYPES,
    QUANT_NAME_TO_ENUM,
    Converter,
    ConvertError,
    ConvertFormat,
    NativeQuantType,
    convert,
)

__all__ = [
    "Converter",
    "convert",
    "ConvertError",
    "ConvertFormat",
    "NativeQuantType",
    "QUANT_NAME_TO_ENUM",
    "NATIVE_QUANT_TYPES",
    "MLX_BITS",
]
