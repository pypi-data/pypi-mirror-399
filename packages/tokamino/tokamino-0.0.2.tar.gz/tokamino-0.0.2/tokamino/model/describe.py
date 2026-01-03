"""
Model description and inspection.

Provides functions to inspect model architecture without loading weights.
"""

import ctypes

from .._lib import get_lib


# C struct for model info
class ModelInfoC(ctypes.Structure):
    """Model information from describe (C struct)."""

    _fields_ = [
        ("vocab_size", ctypes.c_int32),
        ("hidden_size", ctypes.c_int32),
        ("num_layers", ctypes.c_int32),
        ("num_heads", ctypes.c_int32),
        ("num_kv_heads", ctypes.c_int32),
        ("intermediate_size", ctypes.c_int32),
        ("max_seq_len", ctypes.c_int32),
        ("head_dim", ctypes.c_int32),
        ("rope_theta", ctypes.c_float),
        ("norm_eps", ctypes.c_float),
        ("quant_bits", ctypes.c_int32),
        ("quant_group_size", ctypes.c_int32),
        ("model_type", ctypes.c_void_p),
        ("architecture", ctypes.c_void_p),
        ("tie_word_embeddings", ctypes.c_bool),
        ("use_gelu", ctypes.c_bool),
        ("num_experts", ctypes.c_int32),
        ("experts_per_token", ctypes.c_int32),
        ("error_msg", ctypes.c_char_p),
    ]


def _setup_signatures():
    """Set up C function signatures."""
    lib = get_lib()

    lib.tokamino_describe.argtypes = [ctypes.c_char_p]
    lib.tokamino_describe.restype = ModelInfoC

    lib.tokamino_model_info_free.argtypes = [ctypes.POINTER(ModelInfoC)]
    lib.tokamino_model_info_free.restype = None


_setup_signatures()


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
        quant_bits: Quantization bits (4, 8, or 16)
        quant_group_size: Quantization group size
        model_type: Model type string (e.g., "qwen3", "llama")
        architecture: Architecture class name
        tie_word_embeddings: Whether embeddings are tied
        use_gelu: Whether GELU activation is used
        num_experts: Number of MoE experts (0 if not MoE)
        experts_per_token: Experts used per token
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

    Reads config.json without loading model weights.

    Args:
        model: Path to model directory or HuggingFace model ID

    Returns
    -------
        ModelInfo with model configuration

    Raises
    ------
        RuntimeError: If model cannot be loaded or parsed

    Example:
        >>> info = describe("Qwen/Qwen3-0.6B")
        >>> print(f"Layers: {info.num_layers}")
        >>> print(f"Hidden: {info.hidden_size}")
    """
    lib = get_lib()
    result = lib.tokamino_describe(model.encode("utf-8"))

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
    lib.tokamino_model_info_free(ctypes.byref(result))

    return info
