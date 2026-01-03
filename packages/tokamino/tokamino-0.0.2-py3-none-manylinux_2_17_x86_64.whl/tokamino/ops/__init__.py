"""
tokamino.ops - Low-level compute operations.

Zero-copy operations implemented in Zig with DLPack interchange.
Works with any DLPack-compatible tensor library (PyTorch, JAX, etc).

All operations accept DLPack tensors and return OpsTensor objects,
which can be converted back via the __dlpack__ protocol.
"""

from typing import Any

from . import _bindings as _bind
from ._errors import (
    ArgumentError,
    DeviceError,
    DtypeError,
    ShapeError,
    TokaminoError,
)

# =============================================================================
# DType constants (must match DType in dtype.zig)
# =============================================================================


class DType:
    """Data type constants."""

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


# =============================================================================
# Tensor wrapper for ops results
# =============================================================================


class OpsTensor:
    """
    Tensor wrapper for ops results.

    Supports zero-copy interchange via DLPack protocol.
    """

    def __init__(self, ptr: int, owns_data: bool = True):
        """
        Initialize tensor from Zig pointer.

        Args:
            ptr: Pointer to Tensor
            owns_data: Whether this tensor owns its data (should free on del)
        """
        self._ptr = ptr
        self._owns_data = owns_data
        self._exported = False  # Track if exported via DLPack

    def __del__(self):
        if hasattr(self, "_ptr") and self._ptr and not self._exported:
            if self._owns_data:
                _bind.free_tensor(self._ptr)
            else:
                _bind.free_view(self._ptr)

    @property
    def shape(self) -> tuple:
        """Get tensor shape."""
        return _bind.get_shape(self._ptr)

    @property
    def dtype(self) -> int:
        """Get tensor dtype."""
        return _bind.get_dtype(self._ptr)

    @property
    def numel(self) -> int:
        """Get number of elements."""
        return _bind.get_numel(self._ptr)

    def __dlpack__(self, *, stream=None):
        """DLPack protocol for zero-copy export to PyTorch/JAX."""
        if self._exported:
            raise RuntimeError("Tensor already exported via DLPack")
        self._exported = True
        self._owns_data = False  # Transfer ownership to consumer
        return _bind.to_dlpack(self._ptr)

    def __dlpack_device__(self):
        """Return device tuple for DLPack."""
        return (1, 0)  # CPU, device 0

    def __repr__(self):
        return f"OpsTensor(shape={self.shape}, dtype={self.dtype})"


# =============================================================================
# Input handling
# =============================================================================


def _to_tensor_ptr(x: Any) -> tuple[int, bool]:
    """
    Convert input to tensor pointer.

    Returns
    -------
        Tuple of (pointer, is_view) where is_view indicates cleanup needed.
    """
    if isinstance(x, OpsTensor):
        return x._ptr, False
    if hasattr(x, "__dlpack__"):
        # Check for CUDA tensors - we only support CPU
        if hasattr(x, "device") and hasattr(x.device, "type") and x.device.type != "cpu":
            raise RuntimeError(f"Only CPU tensors are supported, got tensor on {x.device}")
        capsule = x.__dlpack__()
        ptr = _bind.from_dlpack(capsule)
        return ptr, True
    raise TypeError(f"Cannot convert {type(x).__name__} to tensor.")


# =============================================================================
# Operation decorators - reduce boilerplate
# =============================================================================


def _unary_op(bind_fn, doc=None):
    """Create a wrapper for unary operations (single input tensor)."""

    def wrapper(x: Any) -> OpsTensor:
        x_ptr, x_is_view = _to_tensor_ptr(x)
        try:
            return OpsTensor(bind_fn(x_ptr), owns_data=True)
        finally:
            if x_is_view:
                _bind.free_view(x_ptr)

    wrapper.__doc__ = doc
    wrapper.__name__ = bind_fn.__name__ if hasattr(bind_fn, "__name__") else "op"
    return wrapper


def _binary_op(bind_fn, doc=None):
    """Create a wrapper for binary operations (two input tensors)."""

    def wrapper(a: Any, b: Any) -> OpsTensor:
        a_ptr, a_view = _to_tensor_ptr(a)
        b_ptr, b_view = _to_tensor_ptr(b)
        try:
            return OpsTensor(bind_fn(a_ptr, b_ptr), owns_data=True)
        finally:
            if a_view:
                _bind.free_view(a_ptr)
            if b_view:
                _bind.free_view(b_ptr)

    wrapper.__doc__ = doc
    wrapper.__name__ = bind_fn.__name__ if hasattr(bind_fn, "__name__") else "op"
    return wrapper


def _unary_with_dim(bind_fn, doc=None):
    """Create a wrapper for unary ops with a dimension parameter."""

    def wrapper(x: Any, dim: int) -> OpsTensor:
        x_ptr, x_is_view = _to_tensor_ptr(x)
        try:
            ndim = _bind.get_ndim(x_ptr)
            # Handle negative dimensions
            if dim < 0:
                # For unsqueeze, output has ndim+1 dims, so -1 means ndim
                dim = ndim + 1 + dim
            # Validate dim range (for unsqueeze: 0 to ndim inclusive)
            if dim < 0 or dim > ndim:
                raise IndexError(f"Dimension out of range (got {dim}, expected 0 to {ndim})")
            return OpsTensor(bind_fn(x_ptr, dim), owns_data=True)
        finally:
            if x_is_view:
                _bind.free_view(x_ptr)

    wrapper.__doc__ = doc
    wrapper.__name__ = bind_fn.__name__ if hasattr(bind_fn, "__name__") else "op"
    return wrapper


def _unary_with_shape(bind_fn, doc=None):
    """Create a wrapper for unary ops with a shape parameter.

    Accepts shape as varargs or single tuple/list:
        op(x, 2, 3, 4) or op(x, (2, 3, 4)) or op(x, [2, 3, 4])
    """

    def wrapper(x: Any, *shape) -> OpsTensor:
        # Handle both op(x, 2, 3) and op(x, (2, 3))
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = tuple(shape[0])

        x_ptr, x_is_view = _to_tensor_ptr(x)
        try:
            return OpsTensor(bind_fn(x_ptr, shape), owns_data=True)
        finally:
            if x_is_view:
                _bind.free_view(x_ptr)

    wrapper.__doc__ = doc
    wrapper.__name__ = bind_fn.__name__ if hasattr(bind_fn, "__name__") else "op"
    return wrapper


# =============================================================================
# Activation operations (unary)
# =============================================================================

silu = _unary_op(_bind.silu, "SiLU activation: x * sigmoid(x)")


def gelu(x: Any, *, approximate: str = "tanh") -> OpsTensor:
    """
    GELU activation function.

    Args:
        x: Input tensor
        approximate: Approximation method ('tanh' or 'none')
            - 'tanh': Fast tanh approximation (default, matches PyTorch approximate='tanh')
            - 'none': Raises error (exact GELU not implemented)

    Returns
    -------
        GELU(x)

    Note:
        This implementation uses the tanh approximation which is standard for
        LLM inference and matches PyTorch's F.gelu(x, approximate='tanh').
    """
    if approximate not in ("tanh", "none"):
        raise ValueError(f"approximate must be 'tanh' or 'none', got '{approximate}'")
    if approximate == "none":
        raise NotImplementedError(
            "Exact GELU not implemented. Use approximate='tanh' (default) or "
            "compute manually: x * 0.5 * (1 + torch.erf(x / sqrt(2)))"
        )

    x_ptr, x_is_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.gelu(x_ptr), owns_data=True)
    finally:
        if x_is_view:
            _bind.free_view(x_ptr)


relu = _unary_op(_bind.relu, "ReLU activation: max(0, x)")
sigmoid = _unary_op(_bind.sigmoid, "Sigmoid activation: 1 / (1 + exp(-x))")
tanh = _unary_op(_bind.tanh, "Tanh activation")
rsqrt = _unary_op(_bind.rsqrt, "Reciprocal square root: 1 / sqrt(x)")


def softmax(x: Any, dim: int = -1) -> OpsTensor:
    """
    Softmax along specified dimension (PyTorch-compatible).

    Args:
        x: Input tensor
        dim: Dimension to apply softmax over (default: -1, last dim)

    Returns
    -------
        Output tensor with softmax applied
    """
    x_ptr, x_is_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.softmax(x_ptr, dim), owns_data=True)
    finally:
        if x_is_view:
            _bind.free_view(x_ptr)


# =============================================================================
# Linear algebra (binary)
# =============================================================================


def linear(x: Any, weight: Any, bias: Any = None) -> OpsTensor:
    """Compute linear projection: out = x @ weight.T + bias."""
    x_ptr, x_view = _to_tensor_ptr(x)
    w_ptr, w_view = _to_tensor_ptr(weight)
    b_ptr, b_view = (None, False) if bias is None else _to_tensor_ptr(bias)
    try:
        # Validate shapes: x is [..., in_features], weight is [out_features, in_features]
        x_shape = _bind.get_shape(x_ptr)
        w_shape = _bind.get_shape(w_ptr)
        if len(x_shape) == 0 or len(w_shape) != 2:
            raise ValueError("linear requires x to be at least 1D and weight to be 2D")
        if x_shape[-1] != w_shape[1]:
            raise ValueError(
                f"linear shape mismatch: x has {x_shape[-1]} features, weight expects {w_shape[1]}"
            )
        return OpsTensor(_bind.linear_bias(x_ptr, w_ptr, b_ptr), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)
        if w_view:
            _bind.free_view(w_ptr)
        if b_view:
            _bind.free_view(b_ptr)


def matmul(a: Any, b: Any) -> OpsTensor:
    """Compute matrix multiplication: out = a @ b."""
    a_ptr, a_view = _to_tensor_ptr(a)
    b_ptr, b_view = _to_tensor_ptr(b)
    try:
        # Validate shapes: a is [..., M, K], b is [..., K, N]
        a_shape = _bind.get_shape(a_ptr)
        b_shape = _bind.get_shape(b_ptr)
        if len(a_shape) < 2 or len(b_shape) < 2:
            raise ValueError(
                f"matmul requires at least 2D tensors, got {len(a_shape)}D and {len(b_shape)}D"
            )
        if a_shape[-1] != b_shape[-2]:
            raise ValueError(
                f"matmul shape mismatch: a has {a_shape[-1]} columns, b has {b_shape[-2]} rows"
            )
        return OpsTensor(_bind.matmul(a_ptr, b_ptr), owns_data=True)
    finally:
        if a_view:
            _bind.free_view(a_ptr)
        if b_view:
            _bind.free_view(b_ptr)


def embedding(input: Any = None, weight: Any = None, *, indices: Any = None) -> OpsTensor:
    """
    Embedding lookup: out = weight[indices].

    Supports both PyTorch-style and legacy calling conventions:
        embedding(indices, weight)  # PyTorch style (recommended)
        embedding(weight, indices)  # Legacy (deprecated, auto-detected)
        embedding(input=indices, weight=weight)  # Explicit kwargs

    Args:
        input: Index tensor (PyTorch-style first positional arg)
        weight: Embedding weight matrix [vocab_size, embed_dim]
        indices: Alias for input (legacy support)

    Returns
    -------
        Embedded values [*input_shape, embed_dim]
    """
    # Handle different calling conventions
    if indices is not None:
        # Called with indices= kwarg (legacy)
        idx, w = indices, weight
    elif input is not None and weight is not None:
        # Two positional args - detect order by dtype
        # If first arg is float and second is int, it's legacy (weight, indices)
        # If first arg is int and second is float, it's PyTorch (indices, weight)
        first_is_int = hasattr(input, "dtype") and str(input.dtype) in (
            "torch.int64",
            "torch.int32",
            "torch.long",
            "int64",
            "int32",
        )
        second_is_int = hasattr(weight, "dtype") and str(weight.dtype) in (
            "torch.int64",
            "torch.int32",
            "torch.long",
            "int64",
            "int32",
        )

        if first_is_int and not second_is_int:
            # PyTorch style: embedding(indices, weight)
            idx, w = input, weight
        elif second_is_int and not first_is_int:
            # Legacy style: embedding(weight, indices)
            idx, w = weight, input
        else:
            # Ambiguous - assume PyTorch style
            idx, w = input, weight
    else:
        raise TypeError("embedding() requires both indices and weight arguments")

    # Validate indices bounds if possible (PyTorch tensors)
    if hasattr(idx, "max") and hasattr(w, "shape"):
        vocab_size = w.shape[0]
        max_idx = int(idx.max().item()) if hasattr(idx.max(), "item") else int(idx.max())
        min_idx = int(idx.min().item()) if hasattr(idx.min(), "item") else int(idx.min())
        if max_idx >= vocab_size:
            raise IndexError(
                f"Index {max_idx} out of bounds for embedding with vocab_size={vocab_size}"
            )
        if min_idx < 0:
            raise IndexError(f"Negative index {min_idx} not allowed in embedding lookup")

    w_ptr, w_view = _to_tensor_ptr(w)
    idx_ptr, idx_view = _to_tensor_ptr(idx)
    try:
        return OpsTensor(_bind.embedding(w_ptr, idx_ptr), owns_data=True)
    finally:
        if w_view:
            _bind.free_view(w_ptr)
        if idx_view:
            _bind.free_view(idx_ptr)


# =============================================================================
# Normalization
# =============================================================================


def rms_norm(x: Any, weight: Any, eps: float = 1e-6) -> OpsTensor:
    """Compute RMS normalization.

    Formula: out = x * rsqrt(mean(x^2) + eps) * weight

    Args:
        x: Input tensor (any dtype: f32, f16, bf16)
        weight: Normalization weights [hidden_size]
        eps: Epsilon for numerical stability

    Returns
    -------
        Normalized tensor (same dtype as input)
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    w_ptr, w_view = _to_tensor_ptr(weight)
    try:
        return OpsTensor(_bind.rms_norm(x_ptr, w_ptr, eps), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)
        if w_view:
            _bind.free_view(w_ptr)


def layer_norm(x: Any, weight: Any, bias: Any = None, eps: float = 1e-5) -> OpsTensor:
    """Compute layer normalization.

    Formula: out = (x - mean) / sqrt(var + eps) * weight + bias

    Args:
        x: Input tensor (any dtype: f32, f16, bf16)
        weight: Normalization weights [hidden_size]
        bias: Optional bias [hidden_size]
        eps: Epsilon for numerical stability

    Returns
    -------
        Normalized tensor (same dtype as input)
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    w_ptr, w_view = _to_tensor_ptr(weight)
    b_ptr, b_view = (None, False) if bias is None else _to_tensor_ptr(bias)
    try:
        return OpsTensor(_bind.layer_norm(x_ptr, w_ptr, b_ptr, eps), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)
        if w_view:
            _bind.free_view(w_ptr)
        if b_view:
            _bind.free_view(b_ptr)


# =============================================================================
# Attention
# =============================================================================


def rope_freqs(
    seq_len: int,
    head_dim: int,
    theta: float = 10000.0,
    offset: int = 0,
) -> tuple:
    """
    Compute RoPE frequency tensors (cos and sin).

    Returns tensors compatible with PyTorch's RoPE implementation:
    - Both cos and sin have shape [seq_len, head_dim]
    - Values are repeat_interleaved: [c0, c0, c1, c1, ...]

    Args:
        seq_len: Maximum sequence length
        head_dim: Head dimension (must be even)
        theta: RoPE theta parameter
        offset: Position offset for continuing generation

    Returns
    -------
        Tuple of (cos, sin) OpsTensor objects, each [seq_len, head_dim]
    """
    # Get combined tensor [seq_len, head_dim] where first half is cos, second half is sin
    combined_ptr = _bind.rope_freqs(seq_len, head_dim, theta, offset)
    combined = OpsTensor(combined_ptr, owns_data=True)

    # Split into cos and sin (each [seq_len, head_dim/2])
    half_dim = head_dim // 2
    cos_half = slice_tensor(combined, [slice(None), slice(0, half_dim)])
    sin_half = slice_tensor(combined, [slice(None), slice(half_dim, None)])

    # Repeat interleave to get [seq_len, head_dim] for each
    cos = repeat_interleave(cos_half, 2, dim=1)
    sin = repeat_interleave(sin_half, 2, dim=1)

    return cos, sin


def apply_rope(q: Any, k: Any, cos: Any, sin: Any) -> None:
    """Apply RoPE to Q and K tensors in-place."""
    q_ptr, q_view = _to_tensor_ptr(q)
    k_ptr, k_view = _to_tensor_ptr(k)
    cos_ptr, cos_view = _to_tensor_ptr(cos)
    sin_ptr, sin_view = _to_tensor_ptr(sin)
    try:
        _bind.apply_rope(q_ptr, k_ptr, cos_ptr, sin_ptr)
    finally:
        if q_view:
            _bind.free_view(q_ptr)
        if k_view:
            _bind.free_view(k_ptr)
        if cos_view:
            _bind.free_view(cos_ptr)
        if sin_view:
            _bind.free_view(sin_ptr)


def scaled_dot_product_attention(
    q: Any,
    k: Any,
    v: Any,
    attn_mask: Any = None,
    dropout_p: float = 0.0,
    is_causal: bool = False,
    scale: float = None,
) -> OpsTensor:
    """
    Scaled dot-product attention (PyTorch-compatible).

    Computes: softmax(Q @ K.T / sqrt(d_k) + attn_mask) @ V

    Args:
        q: Query [batch, n_heads, seq_q, head_dim]
        k: Key [batch, n_heads, seq_kv, head_dim]
        v: Value [batch, n_heads, seq_kv, head_dim]
        attn_mask: Optional attention mask (additive, 0 = attend, -inf = mask)
                   Shape: [batch, n_heads, seq_q, seq_kv] or broadcastable
        dropout_p: Dropout probability (ignored, inference only)
        is_causal: If True, apply causal mask (overrides attn_mask)
        scale: Attention scale (default: 1/sqrt(head_dim))

    Returns
    -------
        Output tensor [batch, n_heads, seq_q, head_dim]
    """
    q_ptr, q_view = _to_tensor_ptr(q)
    k_ptr, k_view = _to_tensor_ptr(k)
    v_ptr, v_view = _to_tensor_ptr(v)

    # Handle attn_mask
    mask_ptr = None
    mask_view = False
    if is_causal:
        # Create causal mask based on sequence lengths
        seq_q = q.shape[2] if hasattr(q, "shape") else _bind.get_shape(q_ptr)[2]
        seq_k = k.shape[2] if hasattr(k, "shape") else _bind.get_shape(k_ptr)[2]
        # For causal, we need a mask of shape [seq_q, seq_k] with -inf for future positions
        mask_tensor = causal_mask(max(seq_q, seq_k), DType.FLOAT32)
        # Slice if needed for cross-attention
        if seq_q != seq_k:
            mask_tensor = slice_tensor(mask_tensor, [slice(None, seq_q), slice(None, seq_k)])
        mask_ptr = mask_tensor._ptr
        mask_view = False  # We own this
    elif attn_mask is not None:
        mask_ptr, mask_view = _to_tensor_ptr(attn_mask)

    try:
        return OpsTensor(_bind.sdpa(q_ptr, k_ptr, v_ptr, mask_ptr, scale or 0.0), owns_data=True)
    finally:
        if q_view:
            _bind.free_view(q_ptr)
        if k_view:
            _bind.free_view(k_ptr)
        if v_view:
            _bind.free_view(v_ptr)
        if mask_view:
            _bind.free_view(mask_ptr)


def attention_with_kv_cache(
    q: Any,
    k: Any,
    v: Any,
    kv_cache: "KVCache",
    layer_idx: int,
    scale: float = None,
) -> OpsTensor:
    """
    Attention with KV cache for efficient autoregressive decoding.

    This function:
    1. Updates the cache with new K/V tensors
    2. Performs SDPA with causal masking against all cached K/V
    3. Advances the cache position

    Args:
        q: Query [batch, n_heads, seq_len, head_dim]
        k: Key [batch, n_kv_heads, seq_len, head_dim] (new K for current step)
        v: Value [batch, n_kv_heads, seq_len, head_dim] (new V for current step)
        kv_cache: KVCache instance
        layer_idx: Layer index (0-indexed)
        scale: Attention scale (default: 1/sqrt(head_dim))

    Returns
    -------
        Output tensor [batch, n_heads, seq_len, head_dim]

    Example:
        cache = ops.KVCache(n_layers=32, n_kv_heads=8, head_dim=128, max_seq_len=4096)

        # Prefill phase
        for layer_idx in range(n_layers):
            q, k, v = project_qkv(hidden_states, layer_idx)
            out = ops.attention_with_kv_cache(q, k, v, cache, layer_idx)

        # Decode phase (one token at a time)
        for _ in range(max_new_tokens):
            for layer_idx in range(n_layers):
                q, k, v = project_qkv(hidden_states, layer_idx)
                out = ops.attention_with_kv_cache(q, k, v, cache, layer_idx)
    """
    q_ptr, q_view = _to_tensor_ptr(q)
    k_ptr, k_view = _to_tensor_ptr(k)
    v_ptr, v_view = _to_tensor_ptr(v)
    try:
        return OpsTensor(
            _bind.attention_with_kv_cache(
                q_ptr, k_ptr, v_ptr, kv_cache._ptr, layer_idx, scale or 0.0
            ),
            owns_data=True,
        )
    finally:
        if q_view:
            _bind.free_view(q_ptr)
        if k_view:
            _bind.free_view(k_ptr)
        if v_view:
            _bind.free_view(v_ptr)


def attention_with_sinks(
    q: Any,
    k: Any,
    v: Any,
    kv_cache: "KVCache",
    layer_idx: int,
    sinks: Any = None,
    sliding_window: int = 0,
    scale: float = None,
) -> OpsTensor:
    """
    Attention with KV cache, optional sinks, and sliding window.

    Extended version of attention_with_kv_cache that supports:
    - sinks: per-head learnable logits added to softmax denominator (GPT-OSS style)
    - sliding_window: limit attention to most recent N positions

    Args:
        q: Query [batch, n_heads, seq_len, head_dim]
        k: Key [batch, n_kv_heads, seq_len, head_dim]
        v: Value [batch, n_kv_heads, seq_len, head_dim]
        kv_cache: KVCache instance
        layer_idx: Layer index (0-indexed)
        sinks: Optional per-head sink logits [n_heads]
        sliding_window: Sliding window size (0 = disabled, full attention)
        scale: Attention scale (default: 1/sqrt(head_dim))

    Returns
    -------
        Output tensor [batch, n_heads, seq_len, head_dim]
    """
    q_ptr, q_view = _to_tensor_ptr(q)
    k_ptr, k_view = _to_tensor_ptr(k)
    v_ptr, v_view = _to_tensor_ptr(v)
    sinks_ptr, sinks_view = (None, False) if sinks is None else _to_tensor_ptr(sinks)
    try:
        return OpsTensor(
            _bind.attention_with_sinks(
                q_ptr,
                k_ptr,
                v_ptr,
                kv_cache._ptr,
                layer_idx,
                sinks_ptr,
                sliding_window,
                scale or 0.0,
            ),
            owns_data=True,
        )
    finally:
        if q_view:
            _bind.free_view(q_ptr)
        if k_view:
            _bind.free_view(k_ptr)
        if v_view:
            _bind.free_view(v_ptr)
        if sinks_view:
            _bind.free_view(sinks_ptr)


# =============================================================================
# Shape operations
# =============================================================================


def cat(tensors: list, dim: int = 0) -> OpsTensor:
    """Concatenate tensors along a dimension."""
    if len(tensors) == 0:
        raise ValueError("cat requires at least one tensor")

    ptrs, views = [], []
    for t in tensors:
        ptr, is_view = _to_tensor_ptr(t)
        ptrs.append(ptr)
        views.append((ptr, is_view))

    try:
        # Validate shapes are compatible
        shapes = [_bind.get_shape(ptr) for ptr in ptrs]
        ndim = len(shapes[0])
        dim_normalized = dim if dim >= 0 else ndim + dim

        if dim_normalized < 0 or dim_normalized >= ndim:
            raise IndexError(f"Dimension {dim} out of range for {ndim}D tensor")

        for i, shape in enumerate(shapes[1:], 1):
            if len(shape) != ndim:
                raise ValueError(
                    f"All tensors must have same ndim. Tensor 0 has {ndim}D, tensor {i} has {len(shape)}D"
                )
            for d, (s0, si) in enumerate(zip(shapes[0], shape, strict=True)):
                if d != dim_normalized and s0 != si:
                    raise ValueError(f"Tensors have incompatible shapes at dim {d}: {s0} vs {si}")

        return OpsTensor(_bind.cat(ptrs, dim), owns_data=True)
    finally:
        for ptr, is_view in views:
            if is_view:
                _bind.free_view(ptr)


def transpose(x: Any, dim0: int, dim1: int) -> OpsTensor:
    """Transpose tensor dimensions."""
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.transpose(x_ptr, dim0, dim1), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


reshape = _unary_with_shape(_bind.reshape, "Reshape tensor to new shape.")
expand = _unary_with_shape(_bind.expand, "Expand tensor to new shape (broadcasting).")
unsqueeze = _unary_with_dim(_bind.unsqueeze, "Add dimension of size 1.")


def squeeze(x: Any, dim: int = None) -> OpsTensor:
    """Remove dimensions of size 1."""
    x_ptr, x_view = _to_tensor_ptr(x)
    actual_dim = -1 if dim is None else dim
    try:
        return OpsTensor(_bind.squeeze(x_ptr, actual_dim), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def repeat_interleave(x: Any, repeats: int, dim: int) -> OpsTensor:
    """Repeat elements along dimension."""
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.repeat_interleave(x_ptr, repeats, dim), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def split(x: Any, split_size_or_sizes, dim: int = 0) -> list:
    """
    Split tensor into chunks along dimension.

    Args:
        x: Input tensor
        split_size_or_sizes: Either an int (equal chunks) or list of ints (specific sizes)
        dim: Dimension to split along

    Returns
    -------
        List of tensors
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        shape = _bind.get_shape(x_ptr)
        ndim = len(shape)
        dim = dim if dim >= 0 else ndim + dim
        dim_size = shape[dim]

        if isinstance(split_size_or_sizes, int):
            # Equal chunks - build list of sizes
            split_size = split_size_or_sizes
            sizes = [split_size] * (dim_size // split_size)
            remainder = dim_size % split_size
            if remainder > 0:
                sizes.append(remainder)
        else:
            sizes = split_size_or_sizes

        # Use slicing to create each chunk
        results = []
        offset = 0
        for size in sizes:
            slices = [slice(None)] * ndim
            slices[dim] = slice(offset, offset + size)
            results.append(slice_tensor(x, slices))
            offset += size
        return results
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def chunk(x: Any, chunks: int, dim: int = 0) -> list:
    """Split tensor into approximately equal chunks."""
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        shape = _bind.get_shape(x_ptr)
        ndim = len(shape)
        dim = dim if dim >= 0 else ndim + dim
        dim_size = shape[dim]

        # Calculate sizes for each chunk (as equal as possible)
        base_size = dim_size // chunks
        remainder = dim_size % chunks
        sizes = [base_size + (1 if i < remainder else 0) for i in range(chunks)]

        # Use slicing to create each chunk
        results = []
        offset = 0
        for size in sizes:
            if size > 0:  # Skip empty chunks
                slices = [slice(None)] * ndim
                slices[dim] = slice(offset, offset + size)
                results.append(slice_tensor(x, slices))
                offset += size
        return results
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def slice_tensor(x: Any, slices: list) -> OpsTensor:
    """Slice tensor along multiple dimensions."""
    x_ptr, x_view = _to_tensor_ptr(x)
    ndim = _bind.get_ndim(x_ptr)
    shape = _bind.get_shape(x_ptr)

    starts, ends, steps = [], [], []
    for d in range(ndim):
        dim_size = shape[d]
        if d < len(slices):
            s = slices[d]
            if isinstance(s, slice):
                start = s.start if s.start is not None else 0
                end = s.stop if s.stop is not None else dim_size
                step = s.step if s.step is not None else 1
            elif isinstance(s, tuple):
                start, end, step = s
            else:
                start, end, step = s, s + 1, 1
        else:
            start, end, step = 0, dim_size, 1
        starts.append(start)
        ends.append(end)
        steps.append(step)

    try:
        return OpsTensor(_bind.slice_tensor(x_ptr, starts, ends, steps), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


# =============================================================================
# Creation operations
# =============================================================================


def zeros(*size, dtype: int = None) -> OpsTensor:
    """
    Create tensor filled with zeros.

    Args:
        *size: Shape as varargs or single tuple/list
            zeros(4, 8) or zeros((4, 8)) or zeros([4, 8])
        dtype: Data type (default: float32)

    Returns
    -------
        Zero-filled tensor
    """
    # Handle both zeros(4, 8) and zeros((4, 8))
    if len(size) == 1 and isinstance(size[0], (tuple, list)):
        shape = tuple(size[0])
    else:
        shape = size

    # Validate shape to prevent overflow/crash
    numel = 1
    for dim in shape:
        if dim < 0:
            raise ValueError(f"Negative dimension in shape: {shape}")
        numel *= dim
        if numel > 2**48:  # ~256TB, clearly impossible
            raise MemoryError(f"Shape too large: {shape}")
    return OpsTensor(_bind.zeros(shape, dtype or DType.FLOAT32), owns_data=True)


def ones(*size, dtype: int = None) -> OpsTensor:
    """
    Create tensor filled with ones.

    Args:
        *size: Shape as varargs or single tuple/list
            ones(4, 8) or ones((4, 8)) or ones([4, 8])
        dtype: Data type (default: float32)

    Returns
    -------
        One-filled tensor
    """
    # Handle both ones(4, 8) and ones((4, 8))
    if len(size) == 1 and isinstance(size[0], (tuple, list)):
        shape = tuple(size[0])
    else:
        shape = size

    # Validate shape to prevent overflow/crash
    numel = 1
    for dim in shape:
        if dim < 0:
            raise ValueError(f"Negative dimension in shape: {shape}")
        numel *= dim
        if numel > 2**48:  # ~256TB, clearly impossible
            raise MemoryError(f"Shape too large: {shape}")
    return OpsTensor(_bind.ones(shape, dtype or DType.FLOAT32), owns_data=True)


def arange(start_or_end, end=None, step=1, *, dtype: int = None) -> OpsTensor:
    """
    Create arange tensor.

    Args:
        start_or_end: If end is None, this is end (start=0). Otherwise, this is start.
        end: End value (exclusive)
        step: Step size (default: 1)
        dtype: Data type (default: int64 for integer args, float32 for float args)

    Examples
    --------
        arange(5)        # [0, 1, 2, 3, 4]
        arange(2, 5)     # [2, 3, 4]
        arange(0, 10, 2) # [0, 2, 4, 6, 8]

    Returns
    -------
        1D tensor with values from start to end
    """
    if end is None:
        start, end = 0, start_or_end
    else:
        start = start_or_end

    if step <= 0:
        raise ValueError(f"step must be positive, got {step}")

    # Check if any value is float
    is_float = isinstance(start, float) or isinstance(end, float) or isinstance(step, float)

    # For now, only support simple arange(n) in Zig with integer step
    if start == 0 and step == 1 and not is_float:
        import math

        n = max(0, int(math.ceil((end - start) / step)))
        return OpsTensor(
            _bind.arange(n, dtype if dtype is not None else DType.INT64), owns_data=True
        )
    else:
        # Delegate to PyTorch for complex cases (start != 0, step != 1, or float values)
        import torch

        # Determine dtype: use float32 for float args, int64 for int args
        if dtype is None:
            torch_dtype = torch.float32 if is_float else torch.int64
        else:
            # Map our dtype to torch dtype
            torch_dtype = torch.float32 if dtype == DType.FLOAT32 else torch.int64
        result = torch.arange(start, end, step, dtype=torch_dtype)
        # Convert via DLPack
        ptr = _bind.from_dlpack(result.__dlpack__())
        return OpsTensor(ptr, owns_data=True)


def causal_mask(seq_len: int, dtype: int = None) -> OpsTensor:
    """Create causal attention mask [seq_len, seq_len]."""
    return OpsTensor(_bind.causal_mask(seq_len, dtype or DType.FLOAT32), owns_data=True)


def triu(x: Any, diagonal: int = 0) -> OpsTensor:
    """Upper triangular matrix - zeros out elements below the diagonal."""
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.triu(x_ptr, diagonal), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def zeros_like(x: Any) -> OpsTensor:
    """Create zeros tensor with same shape/dtype as input."""
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.zeros_like(x_ptr), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def topk(x: Any, k: int) -> tuple:
    """
    Top-k selection along last dimension.

    Args:
        x: Input tensor [*, n]
        k: Number of top elements to return

    Returns
    -------
        Tuple of (values, indices) where each is [*, k]
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        # Validate k against last dimension
        shape = _bind.get_shape(x_ptr)
        if len(shape) == 0:
            raise ValueError("topk requires at least 1D tensor")
        last_dim = shape[-1]
        if k > last_dim:
            raise ValueError(f"k ({k}) cannot be greater than last dimension size ({last_dim})")
        if k < 1:
            raise ValueError(f"k ({k}) must be at least 1")
        values_ptr, indices_ptr = _bind.topk(x_ptr, k)
        return OpsTensor(values_ptr, owns_data=True), OpsTensor(indices_ptr, owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def one_hot(indices: Any, num_classes: int) -> "OpsTensor":
    """
    One-hot encoding.

    Args:
        indices: 1D int tensor [N] with values in [0, num_classes)
        num_classes: Number of classes

    Returns
    -------
        Float32 tensor [N, num_classes] with one-hot encoding
    """
    idx_ptr, idx_view = _to_tensor_ptr(indices)
    try:
        return OpsTensor(_bind.one_hot(idx_ptr, num_classes), owns_data=True)
    finally:
        if idx_view:
            _bind.free_view(idx_ptr)


def greater_scalar(x: Any, threshold: float):
    """
    Element-wise greater than comparison.

    Args:
        x: Input tensor
        threshold: Scalar threshold

    Returns
    -------
        Bool tensor with True where x > threshold, False otherwise
    """
    # Use PyTorch directly for bool support (Zig doesn't have bool dtype)
    if hasattr(x, "__gt__"):
        return x > threshold

    # Fallback to Zig implementation (returns int64)
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.greater_scalar(x_ptr, threshold), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def nonzero(x: Any) -> "OpsTensor":
    """
    Return indices where tensor is non-zero.

    Args:
        x: Input tensor

    Returns
    -------
        Int64 tensor [num_nonzero, ndim] with indices
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    try:
        return OpsTensor(_bind.nonzero(x_ptr), owns_data=True)
    finally:
        if x_view:
            _bind.free_view(x_ptr)


def where(condition: Any, x: Any, y: Any) -> "OpsTensor":
    """
    Element-wise selection: where(condition, x, y).

    Args:
        condition: Boolean/int condition tensor
        x: Values where condition is true
        y: Values where condition is false

    Returns
    -------
        Tensor with x where condition, y elsewhere
    """
    # Convert bool tensors to int64 (Zig doesn't support bool dtype)
    if hasattr(condition, "dtype") and hasattr(condition, "to"):
        import torch

        if condition.dtype == torch.bool:
            condition = condition.to(torch.int64)

    cond_ptr, cond_view = _to_tensor_ptr(condition)
    x_ptr, x_view = _to_tensor_ptr(x)
    y_ptr, y_view = _to_tensor_ptr(y)
    try:
        return OpsTensor(_bind.where(cond_ptr, x_ptr, y_ptr), owns_data=True)
    finally:
        if cond_view:
            _bind.free_view(cond_ptr)
        if x_view:
            _bind.free_view(x_ptr)
        if y_view:
            _bind.free_view(y_ptr)


def index_add_(out: "OpsTensor", dim: int, indices: Any, source: Any) -> None:
    """
    In-place indexed addition: out[indices] += source along dim.

    Args:
        out: Output tensor (modified in-place)
        dim: Dimension to index along
        indices: 1D indices tensor
        source: Source values to add
    """
    idx_ptr, idx_view = _to_tensor_ptr(indices)
    src_ptr, src_view = _to_tensor_ptr(source)
    try:
        _bind.index_add(out._ptr, dim, idx_ptr, src_ptr)
    finally:
        if idx_view:
            _bind.free_view(idx_ptr)
        if src_view:
            _bind.free_view(src_ptr)


# =============================================================================
# KV Cache
# =============================================================================


class KVCache:
    """
    KV cache for efficient autoregressive inference.

    Stores K and V tensors for all layers, enabling incremental decoding
    without recomputing past key-value pairs.

    Example:
        cache = ops.KVCache(
            n_layers=32,
            n_kv_heads=8,
            head_dim=128,
            max_seq_len=4096,
        )

        # During forward pass for each layer
        cache.update(layer_idx, k, v)

        # Get cached K/V for attention
        cached_k = cache.get_k(layer_idx)
        cached_v = cache.get_v(layer_idx)

        # After processing, advance position
        cache.advance(seq_len)
    """

    def __init__(
        self,
        n_layers: int,
        n_kv_heads: int,
        head_dim: int,
        max_seq_len: int,
        sliding_window: int = 0,
        dtype: int = None,
        device: str = "cpu",
    ):
        """
        Create a new KV cache.

        Args:
            n_layers: Number of transformer layers
            n_kv_heads: Number of key-value heads (may differ from query heads in GQA)
            head_dim: Dimension of each head
            max_seq_len: Maximum sequence length to cache
            sliding_window: Sliding window size (0 = disabled)
            dtype: Data type (default: float32)
            device: Device ("cpu" or "metal")
        """
        self._ptr = _bind.kv_cache_create(
            n_layers, n_kv_heads, head_dim, max_seq_len, sliding_window
        )
        self.n_layers = n_layers
        self.n_kv_heads = n_kv_heads
        self.head_dim = head_dim
        self.max_seq_len = max_seq_len
        self.sliding_window = sliding_window

    def __del__(self):
        if hasattr(self, "_ptr") and self._ptr:
            _bind.kv_cache_destroy(self._ptr)

    def update(self, layer_idx: int, k: Any, v: Any) -> None:
        """
        Update cache with new K/V tensors for a layer.

        Args:
            layer_idx: Layer index (0-indexed)
            k: Key tensor [seq_len, n_kv_heads, head_dim]
            v: Value tensor [seq_len, n_kv_heads, head_dim]
        """
        if layer_idx < 0 or layer_idx >= self.n_layers:
            raise IndexError(f"Layer index {layer_idx} out of range [0, {self.n_layers})")

        k_ptr, k_view = _to_tensor_ptr(k)
        v_ptr, v_view = _to_tensor_ptr(v)
        try:
            # Validate K/V shapes match cache configuration
            k_shape = _bind.get_shape(k_ptr)
            v_shape = _bind.get_shape(v_ptr)

            if len(k_shape) != 3 or len(v_shape) != 3:
                raise ValueError(
                    f"K/V must be 3D [seq_len, n_kv_heads, head_dim], got {len(k_shape)}D and {len(v_shape)}D"
                )

            if k_shape[1] != self.n_kv_heads or k_shape[2] != self.head_dim:
                raise ValueError(
                    f"K shape mismatch: got [{k_shape[1]}, {k_shape[2]}], expected [{self.n_kv_heads}, {self.head_dim}]"
                )

            if v_shape[1] != self.n_kv_heads or v_shape[2] != self.head_dim:
                raise ValueError(
                    f"V shape mismatch: got [{v_shape[1]}, {v_shape[2]}], expected [{self.n_kv_heads}, {self.head_dim}]"
                )

            _bind.kv_cache_update(self._ptr, layer_idx, k_ptr, v_ptr)
        finally:
            if k_view:
                _bind.free_view(k_ptr)
            if v_view:
                _bind.free_view(v_ptr)

    def advance(self, steps: int = 1) -> None:
        """Advance cache position by number of tokens processed."""
        _bind.kv_cache_advance(self._ptr, steps)

    def get_length(self) -> int:
        """Get number of tokens currently cached."""
        return _bind.kv_cache_length(self._ptr)

    def reset(self) -> None:
        """Clear cache and reset to empty state."""
        _bind.kv_cache_reset(self._ptr)

    def get_k(self, layer_idx: int) -> OpsTensor:
        """
        Get cached K tensor for a layer.

        Args:
            layer_idx: Layer index (0-indexed)

        Returns
        -------
            K tensor [seq_len, n_kv_heads, head_dim] or None if empty
        """
        ptr = _bind.kv_cache_get_k(self._ptr, layer_idx)
        if ptr is None:
            return None
        return OpsTensor(ptr, owns_data=False)

    def get_v(self, layer_idx: int) -> OpsTensor:
        """
        Get cached V tensor for a layer.

        Args:
            layer_idx: Layer index (0-indexed)

        Returns
        -------
            V tensor [seq_len, n_kv_heads, head_dim] or None if empty
        """
        ptr = _bind.kv_cache_get_v(self._ptr, layer_idx)
        if ptr is None:
            return None
        return OpsTensor(ptr, owns_data=False)

    def __repr__(self):
        return (
            f"KVCache(n_layers={self.n_layers}, n_kv_heads={self.n_kv_heads}, "
            f"head_dim={self.head_dim}, max_seq_len={self.max_seq_len}, "
            f"length={self.get_length()})"
        )


# =============================================================================
# Quantized Linear Operations (Q4_0, Q8_0)
# =============================================================================


def linear_q4(
    x: Any,
    weights: Any,
    out_features: int,
    bias: Any = None,
) -> OpsTensor:
    """
    Q4_0 quantized linear layer (zero-copy).

    Computes: out = x @ weights^T + bias
    Weights are in GGML Q4_0 format (4-bit symmetric quantization).

    Args:
        x: Input tensor [batch, in_features] as f32 (DLPack-compatible)
        weights: Q4_0 weights as uint8 buffer (BlockQ4_0 format, DLPack-compatible)
        out_features: Number of output features
        bias: Optional bias [out_features] as f32

    Returns
    -------
        Output tensor [batch, out_features] as f32
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    w_ptr, w_view = _to_tensor_ptr(weights)
    b_ptr, b_view = (None, False) if bias is None else _to_tensor_ptr(bias)

    try:
        return OpsTensor(
            _bind.linear_q4(x_ptr, w_ptr, b_ptr, out_features),
            owns_data=True,
        )
    finally:
        if x_view:
            _bind.free_view(x_ptr)
        if w_view:
            _bind.free_view(w_ptr)
        if b_view:
            _bind.free_view(b_ptr)


def linear_q8(
    x: Any,
    weights: Any,
    out_features: int,
    bias: Any = None,
) -> OpsTensor:
    """
    Q8_0 quantized linear layer (zero-copy).

    Computes: out = x @ weights^T + bias
    Weights are in GGML Q8_0 format (8-bit symmetric quantization).

    Args:
        x: Input tensor [batch, in_features] as f32 (DLPack-compatible)
        weights: Q8_0 weights as uint8 buffer (BlockQ8_0 format, DLPack-compatible)
        out_features: Number of output features
        bias: Optional bias [out_features] as f32

    Returns
    -------
        Output tensor [batch, out_features] as f32
    """
    x_ptr, x_view = _to_tensor_ptr(x)
    w_ptr, w_view = _to_tensor_ptr(weights)
    b_ptr, b_view = (None, False) if bias is None else _to_tensor_ptr(bias)

    try:
        return OpsTensor(
            _bind.linear_q8(x_ptr, w_ptr, b_ptr, out_features),
            owns_data=True,
        )
    finally:
        if x_view:
            _bind.free_view(x_ptr)
        if w_view:
            _bind.free_view(w_ptr)
        if b_view:
            _bind.free_view(b_ptr)


# =============================================================================
# MXFP4 Quantized Operations
# =============================================================================


def mxfp4_matmul(
    x: Any,
    weight_blocks: Any,
    scales: Any,
    bias: Any = None,
) -> OpsTensor:
    """
    MXFP4 matrix multiplication (zero-copy).

    Computes: out = x @ weights^T + bias
    Weights are in MXFP4 format (4-bit microscaling).

    Args:
        x: Input tensor [batch, in_features] - bf16 or f32 (DLPack-compatible)
        weight_blocks: Packed 4-bit weights [out_features, n_groups, 16] as uint8
        scales: E8M0 scales [out_features, n_groups] as uint8
        bias: Optional bias [out_features] as f32

    Returns
    -------
        Output tensor [batch, out_features] as f32
    """
    # Infer out_features from weight_blocks shape
    out_features = weight_blocks.shape[0]

    x_ptr, x_view = _to_tensor_ptr(x)
    w_ptr, w_view = _to_tensor_ptr(weight_blocks)
    s_ptr, s_view = _to_tensor_ptr(scales)
    b_ptr, b_view = (None, False) if bias is None else _to_tensor_ptr(bias)

    try:
        return OpsTensor(
            _bind.mxfp4_linear(x_ptr, w_ptr, s_ptr, b_ptr, out_features),
            owns_data=True,
        )
    finally:
        if x_view:
            _bind.free_view(x_ptr)
        if w_view:
            _bind.free_view(w_ptr)
        if s_view:
            _bind.free_view(s_ptr)
        if b_view:
            _bind.free_view(b_ptr)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Exceptions
    "TokaminoError",
    "ShapeError",
    "DtypeError",
    "DeviceError",
    "ArgumentError",
    # Types
    "DType",
    "OpsTensor",
    # Activations
    "silu",
    "gelu",
    "relu",
    "sigmoid",
    "tanh",
    "softmax",
    "rsqrt",
    # Linear algebra
    "linear",
    "matmul",
    "embedding",
    # Normalization
    "rms_norm",
    "layer_norm",
    # Attention
    "rope_freqs",
    "apply_rope",
    "scaled_dot_product_attention",
    "attention_with_kv_cache",
    "attention_with_sinks",
    # KV Cache
    "KVCache",
    # Shape operations
    "cat",
    "transpose",
    "reshape",
    "expand",
    "unsqueeze",
    "squeeze",
    "repeat_interleave",
    "split",
    "chunk",
    "slice_tensor",
    # Creation
    "zeros",
    "ones",
    "arange",
    "causal_mask",
    "zeros_like",
    "topk",
    "triu",
    # MoE primitives
    "one_hot",
    "greater_scalar",
    "nonzero",
    "where",
    "index_add_",
    # Quantized ops
    "mxfp4_matmul",
    "linear_q4",
    "linear_q8",
]
