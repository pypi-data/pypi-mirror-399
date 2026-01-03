"""
Converter implementation.

Provides the Converter class and convert function for model quantization.
"""

from __future__ import annotations

import ctypes
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from .._lib import get_lib

__all__ = ["convert", "Converter", "ConvertError"]


class ConvertError(Exception):
    """
    Raised when model conversion fails.

    This exception is raised when the conversion process encounters an error,
    such as:

    - Model not found (invalid HuggingFace ID or local path)
    - Network errors when downloading from HuggingFace
    - Unsupported model architecture
    - Disk space issues
    - Invalid model files (corrupted weights, missing config)

    The exception message contains details about what went wrong.

    Examples
    --------
    >>> try:
    ...     tokamino.convert("nonexistent/model", bits=4)
    ... except tokamino.ConvertError as e:
    ...     print(f"Conversion failed: {e}")
    Conversion failed: Model not found
    """

    pass


# =============================================================================
# C Types
# =============================================================================


class ConvertFormat:
    """Output format for conversion."""

    NATIVE = 0  # K-quant in SafeTensors (default)
    MLX = 1  # Grouped-affine for MLX compatibility


class NativeQuantType:
    """Native quantization types (K-quants)."""

    Q4_0 = 0  # Basic 4-bit symmetric
    Q4_K_M = 1  # 4-bit K-quant with mixed precision
    Q5_K = 2  # 5-bit K-quant
    Q6_K = 3  # 6-bit K-quant (default for bits=4)
    Q8_0 = 4  # 8-bit symmetric (default for bits=8)
    F16 = 5  # No quantization


# Map string quant names to enum values
QUANT_NAME_TO_ENUM = {
    "q4_0": NativeQuantType.Q4_0,
    "q4_k_m": NativeQuantType.Q4_K_M,
    "q5_k": NativeQuantType.Q5_K,
    "q6_k": NativeQuantType.Q6_K,
    "q8_0": NativeQuantType.Q8_0,
    "f16": NativeQuantType.F16,
}

# Valid quantization types for native format
NATIVE_QUANT_TYPES = frozenset(QUANT_NAME_TO_ENUM.keys())

# Valid bit widths for MLX format
MLX_BITS = frozenset({4, 8})


# Progress callback type for C
ProgressCallbackFunc = ctypes.CFUNCTYPE(
    None,
    ctypes.c_size_t,  # current
    ctypes.c_size_t,  # total
    ctypes.c_char_p,  # tensor_name
    ctypes.c_void_p,  # user_data
)


class ConvertOptions(ctypes.Structure):
    """Conversion options (C struct)."""

    _fields_ = [
        ("format", ctypes.c_uint32),
        ("quant", ctypes.c_uint32),
        ("bits", ctypes.c_uint32),
        ("group_size", ctypes.c_uint32),
        ("force", ctypes.c_bool),
        ("progress_callback", ProgressCallbackFunc),
        ("progress_user_data", ctypes.c_void_p),
    ]


class ConvertResult(ctypes.Structure):
    """Result from conversion (C struct).

    Note: We use c_void_p instead of c_char_p for string fields to avoid
    ctypes auto-converting to bytes. This is necessary because:
    1. c_char_p auto-converts to Python bytes when accessed
    2. When we call tokamino_convert_free_string, ctypes would create a
       NEW temporary buffer for the bytes, not the original pointer
    3. The Zig allocator would then try to free an invalid pointer

    With c_void_p, we keep the original pointer and can safely free it.
    """

    _fields_ = [
        ("output_path", ctypes.c_void_p),
        ("error_msg", ctypes.c_void_p),
        ("success", ctypes.c_bool),
    ]


# =============================================================================
# Setup C API signatures
# =============================================================================

_lib = None
_signatures_setup = False


def _setup_signatures():
    """Set up C API function signatures."""
    global _lib, _signatures_setup
    if _signatures_setup:
        return

    _lib = get_lib()

    _lib.tokamino_convert.argtypes = [
        ctypes.c_char_p,  # model_path
        ctypes.c_char_p,  # output_dir
        ctypes.POINTER(ConvertOptions),  # options
    ]
    _lib.tokamino_convert.restype = ConvertResult

    _lib.tokamino_convert_free_string.argtypes = [ctypes.c_void_p]
    _lib.tokamino_convert_free_string.restype = None

    _lib.tokamino_convert_quant_types.argtypes = []
    _lib.tokamino_convert_quant_types.restype = ctypes.c_char_p

    _signatures_setup = True


# =============================================================================
# Converter Class
# =============================================================================


class Converter:
    """
    Model converter for quantizing HuggingFace models.

    The Converter class provides an interface for converting models to
    optimized quantized formats. It uses the native C library for fast,
    efficient conversion.

    Quick Start
    -----------

    Convert a model to 4-bit quantized format::

        >>> converter = Converter()
        >>> path = converter("Qwen/Qwen3-0.6B", bits=4)
        >>> print(path)
        models/models--Qwen--Qwen3-0.6B-Q6_K

    With progress tracking::

        >>> def on_progress(current, total, name):
        ...     print(f"[{current}/{total}] {name}")
        >>> path = converter("Qwen/Qwen3-0.6B", bits=4, progress=on_progress)

    Attributes
    ----------
    output_dir : str
        Default output directory for converted models.

    See Also
    --------
    convert : Function-based API for one-off conversions.
    ChatSession : Load and use converted models for inference.
    """

    def __init__(self, output_dir: str = "models"):
        """
        Create a new Converter.

        Args:
            output_dir: Default directory for converted models. Can be
                overridden per-conversion using the `output` parameter.
        """
        _setup_signatures()
        self._output_dir = output_dir

    def __call__(
        self,
        model: str,
        *,
        format: Literal["native", "mlx"] = "native",
        bits: int | None = None,
        quant: str | None = None,
        group_size: int = 64,
        output: str | None = None,
        force: bool = False,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> str:
        """
        Convert a HuggingFace model to a quantized format.

        This method downloads a model from HuggingFace (or uses a local path),
        quantizes the weights to reduce memory usage, and saves the result.

        Parameters
        ----------
        model : str
            Model to convert. Can be:

            - **HuggingFace ID**: ``"Qwen/Qwen3-0.6B"``, ``"meta-llama/Llama-3-8B"``
            - **Local path**: ``"./my-model"`` or ``"/path/to/model"``

        format : {"native", "mlx"}, default "native"
            Output format:

            - ``"native"``: K-quant format (best quality, tokamino only)
            - ``"mlx"``: Grouped-affine format (MLX compatible)

        bits : int, optional
            Quantization bit width (4 or 8). For native format:

            - ``4``: Uses Q6_K (excellent quality)
            - ``8``: Uses Q8_0 (near-lossless)
            - ``None``: Preserve original precision

        quant : str, optional
            Explicit K-quant type for native format. Options:
            ``"q4_0"``, ``"q4_k_m"``, ``"q5_k"``, ``"q6_k"``, ``"q8_0"``, ``"f16"``

            Cannot be used with ``format="mlx"`` or together with ``bits``.

        group_size : int, default 64
            Group size for MLX format. Ignored for native format.

        output : str, optional
            Output directory. Defaults to the converter's output_dir.

        force : bool, default False
            If True, overwrite existing output directory.

        progress : callable, optional
            Progress callback. Called with ``(current, total, tensor_name)``.

        Returns
        -------
        str
            Absolute path to the converted model directory.

        Raises
        ------
        ConvertError
            If conversion fails.
        ValueError
            If invalid parameter combinations are provided.

        Examples
        --------
        Basic conversion::

            >>> converter = Converter()
            >>> path = converter("Qwen/Qwen3-0.6B", bits=4)

        With explicit K-quant type::

            >>> path = converter("Qwen/Qwen3-0.6B", quant="q4_k_m")

        With progress reporting::

            >>> def show_progress(cur, tot, name):
            ...     print(f"[{cur+1}/{tot}] {name}")
            >>> path = converter("Qwen/Qwen3-0.6B", bits=4, progress=show_progress)
        """
        # Validate parameters
        _validate_params(format=format, bits=bits, quant=quant)

        # Build options struct
        options = ConvertOptions()
        options.format = ConvertFormat.NATIVE if format == "native" else ConvertFormat.MLX
        options.bits = bits or 0
        options.quant = (
            QUANT_NAME_TO_ENUM.get(quant, NativeQuantType.Q6_K) if quant else NativeQuantType.Q6_K
        )
        options.group_size = group_size
        options.force = force

        # Setup progress callback if provided
        # We need to keep a reference to the callback to prevent GC
        self._progress_callback_ref = None
        if progress:

            def c_progress(current, total, name_ptr, user_data):
                name = name_ptr.decode("utf-8") if name_ptr else ""
                progress(current, total, name)

            self._progress_callback_ref = ProgressCallbackFunc(c_progress)
            options.progress_callback = self._progress_callback_ref
            options.progress_user_data = None
        else:
            options.progress_callback = ProgressCallbackFunc()
            options.progress_user_data = None

        # Call C API
        output_dir = output or self._output_dir
        result = _lib.tokamino_convert(
            model.encode("utf-8"),
            output_dir.encode("utf-8"),
            ctypes.byref(options),
        )

        # Check result
        if not result.success:
            error_msg = "Unknown error"
            if result.error_msg:
                # Cast void* to char* and decode
                error_msg = ctypes.cast(result.error_msg, ctypes.c_char_p).value.decode("utf-8")
                _lib.tokamino_convert_free_string(result.error_msg)
            raise ConvertError(error_msg)

        # Extract output path
        output_path = ""
        if result.output_path:
            # Cast void* to char* and decode
            output_path = ctypes.cast(result.output_path, ctypes.c_char_p).value.decode("utf-8")
            _lib.tokamino_convert_free_string(result.output_path)

        return str(Path(output_path).absolute())

    @property
    def output_dir(self) -> str:
        """Default output directory for converted models."""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value: str) -> None:
        """Set the default output directory."""
        self._output_dir = value

    @staticmethod
    def quant_types() -> list[str]:
        """
        Get available quantization types for native format.

        Returns
        -------
        list[str]
            List of quantization type names.

        Example
        -------
        >>> Converter.quant_types()
        ['q4_0', 'q4_k_m', 'q5_k', 'q6_k', 'q8_0', 'f16']
        """
        return sorted(NATIVE_QUANT_TYPES)

    def __repr__(self) -> str:
        return f"Converter(output_dir={self._output_dir!r})"


# =============================================================================
# Convenience Function
# =============================================================================


def convert(
    model: str,
    *,
    format: Literal["native", "mlx"] = "native",
    bits: int | None = None,
    quant: str | None = None,
    group_size: int = 64,
    output: str = "models",
    force: bool = False,
    progress: Callable[[int, int, str], None] | None = None,
) -> str:
    """
    Convert a HuggingFace model to a quantized format for efficient inference.

    This is a convenience function that creates a temporary Converter and
    calls it. For repeated conversions, create a Converter instance directly.

    Parameters
    ----------
    model : str
        Model to convert. Can be:

        - **HuggingFace ID**: ``"Qwen/Qwen3-0.6B"``, ``"meta-llama/Llama-3-8B"``
        - **Local path**: ``"./my-model"`` or ``"/path/to/model"``

    format : {"native", "mlx"}, default "native"
        Output format:

        - ``"native"``: K-quant format (Q4_K_M, Q6_K, Q8_0). Best quality per
          bit, optimized for tokamino. **Recommended for most users.**
        - ``"mlx"``: Grouped-affine format compatible with Apple MLX.

    bits : int, optional
        Quantization bit width. Valid values:

        - ``4``: 4-bit quantization (~4x memory reduction)
        - ``8``: 8-bit quantization (~2x memory reduction)
        - ``None``: Preserve original precision (no quantization)

    quant : str, optional
        Explicit K-quant type for native format. Options:

        - ``"q4_0"``: Basic 4-bit (fast, lower quality)
        - ``"q4_k_m"``: 4-bit K-quant with mixed precision
        - ``"q5_k"``: 5-bit K-quant
        - ``"q6_k"``: 6-bit K-quant **[default for bits=4]**
        - ``"q8_0"``: 8-bit symmetric **[default for bits=8]**
        - ``"f16"``: No quantization

    group_size : int, default 64
        Group size for MLX format. Ignored for native format.

    output : str, default "models"
        Directory where the converted model will be saved.

    force : bool, default False
        If True, overwrite existing output directory.

    progress : callable, optional
        Progress callback. Called with ``(current, total, tensor_name)``.

    Returns
    -------
    str
        Absolute path to the converted model directory.

    Raises
    ------
    ConvertError
        If conversion fails.
    ValueError
        If invalid parameter combinations are provided.

    Examples
    --------
    Basic conversion::

        import tokamino

        path = tokamino.convert("Qwen/Qwen3-0.6B", bits=4)
        session = tokamino.ChatSession(path)
        print(session("What is 2+2?"))

    With progress reporting::

        def show_progress(current, total, name):
            pct = (current + 1) / total * 100
            print(f"[{pct:5.1f}%] {name}")

        path = tokamino.convert("Qwen/Qwen3-0.6B", bits=4, progress=show_progress)

    See Also
    --------
    Converter : Class-based API for more control.
    ChatSession : Load and use converted models for inference.
    """
    converter = Converter(output_dir=output)
    return converter(
        model,
        format=format,
        bits=bits,
        quant=quant,
        group_size=group_size,
        force=force,
        progress=progress,
    )


# =============================================================================
# Validation
# =============================================================================


def _validate_params(
    *,
    format: str,
    bits: int | None,
    quant: str | None,
) -> None:
    """Validate parameter combinations."""
    if format not in ("native", "mlx"):
        raise ValueError(f"format must be 'native' or 'mlx', got {format!r}")

    if format == "mlx":
        if quant is not None:
            raise ValueError(
                "quant= cannot be used with format='mlx'. "
                "MLX format only supports bits=4 or bits=8."
            )
        if bits is not None and bits not in MLX_BITS:
            raise ValueError(f"MLX format only supports bits=4 or bits=8, got bits={bits}")

    if format == "native":
        if quant is not None and quant not in NATIVE_QUANT_TYPES:
            raise ValueError(f"quant must be one of {sorted(NATIVE_QUANT_TYPES)}, got {quant!r}")
        if bits is not None and bits not in (4, 8):
            raise ValueError(f"bits must be 4 or 8, got {bits}")
        if quant is not None and bits is not None:
            raise ValueError("Cannot specify both quant= and bits=")
