"""
TokenArray - Zero-copy token container.

TokenArray wraps token data from the Zig runtime, providing efficient
access with automatic memory management. It supports zero-copy NumPy
conversion for high-performance workflows.
"""

import ctypes
from collections.abc import Iterator

from .._lib import get_lib


class TokenArray:
    """
    A sequence of token IDs with zero-copy NumPy support.

    TokenArray is returned by `Tokenizer.encode()` and provides efficient
    access to token data. The underlying memory is managed by the Zig
    runtime and automatically freed when the TokenArray is garbage collected.

    Key Features
    ------------

    **Zero-copy NumPy conversion** - No data copying when converting to NumPy:

        >>> import numpy as np
        >>> tokens = tokenizer.encode("Hello world")
        >>> arr = np.asarray(tokens)  # Zero-copy view
        >>> print(arr.dtype)
        uint32

    **Standard sequence operations** - Works like a Python list:

        >>> len(tokens)
        2
        >>> tokens[0]
        9707
        >>> tokens[-1]  # Negative indexing
        1879

    **Convert to list** - When you need a regular Python list:

        >>> tokens.tolist()
        [9707, 1879]

    Memory Management
    -----------------

    TokenArray owns its memory and frees it when garbage collected. The
    NumPy array returned by `np.asarray()` is a view into this memory -
    it becomes invalid if the TokenArray is deleted:

        >>> tokens = tokenizer.encode("Hello")
        >>> arr = np.asarray(tokens)
        >>> del tokens  # Memory freed!
        >>> arr[0]      # Undefined behavior - don't do this!

    To keep the data, copy it:

        >>> arr = np.array(tokens)  # np.array copies, np.asarray doesn't

    See Also
    --------
    Tokenizer.encode : Creates TokenArrays from text.
    Tokenizer.decode : Converts TokenArrays back to text.
    """

    def __init__(self, tokens_ptr, num_tokens: int):
        """
        Initialize from a Zig-allocated token pointer.

        This is an internal constructor. Users should get TokenArrays from
        `Tokenizer.encode()`, not create them directly.

        Args:
            tokens_ptr: Pointer to uint32 token IDs (Zig-allocated).
            num_tokens: Number of tokens in the array.
        """
        self._ptr = tokens_ptr
        self._num_tokens = num_tokens
        self._owns_data = True

    def __len__(self) -> int:
        """
        Return the number of tokens.

        Example:
            >>> tokens = tokenizer.encode("Hello world")
            >>> len(tokens)
            2
        """
        return self._num_tokens

    def __getitem__(self, idx: int) -> int:
        """
        Get a token ID by index.

        Supports negative indexing (e.g., -1 for last token).

        Args:
            idx: Token index (0-based, or negative from end).

        Returns
        -------
            The token ID at that position.

        Raises
        ------
            IndexError: If index is out of range.

        Example:
            >>> tokens = tokenizer.encode("Hello")
            >>> tokens[0]      # First token
            9707
            >>> tokens[-1]     # Last token
            9707
        """
        if idx < 0:
            idx = self._num_tokens + idx
        if idx < 0 or idx >= self._num_tokens:
            raise IndexError(f"Token index {idx} out of range [0, {self._num_tokens})")
        return self._ptr[idx]

    def __iter__(self) -> Iterator[int]:
        """
        Iterate over token IDs.

        Example:
            >>> tokens = tokenizer.encode("Hi")
            >>> for token_id in tokens:
            ...     print(token_id)
        """
        for i in range(self._num_tokens):
            yield self._ptr[i]

    def tolist(self) -> list[int]:
        """
        Convert to a Python list.

        This copies the data into a new Python list. Use this when you
        need a regular list, or when you need to keep the data after
        the TokenArray is deleted.

        Returns
        -------
            A new list containing the token IDs.

        Example:
            >>> tokens = tokenizer.encode("Hello world")
            >>> token_list = tokens.tolist()
            >>> print(token_list)
            [9707, 1879]
            >>> type(token_list)
            <class 'list'>
        """
        return [self._ptr[i] for i in range(self._num_tokens)]

    @property
    def __array_interface__(self) -> dict:
        """
        NumPy array interface for zero-copy access.

        This allows NumPy to create an array view directly over the
        underlying memory without copying. Use `np.asarray(tokens)`.

        Returns
        -------
            Dictionary conforming to NumPy's array interface protocol.

        Example:
            >>> import numpy as np
            >>> tokens = tokenizer.encode("Hello world")
            >>> arr = np.asarray(tokens)  # Zero-copy!
            >>> print(arr.shape, arr.dtype)
            (2,) uint32
        """
        return {
            "version": 3,
            "shape": (self._num_tokens,),
            "typestr": "<u4",  # uint32 little-endian
            "data": (ctypes.addressof(self._ptr.contents), False),
            "strides": (4,),  # 4 bytes per uint32
        }

    def __del__(self):
        """Free the token memory when garbage collected."""
        if hasattr(self, "_ptr") and self._ptr and self._owns_data:
            lib = get_lib()
            lib.tokamino_tokens_free(self._ptr, self._num_tokens)
            self._ptr = None

    def __repr__(self) -> str:
        """Return string representation showing token IDs."""
        if self._num_tokens <= 10:
            tokens_str = str(self.tolist())
        else:
            first = [self._ptr[i] for i in range(5)]
            last = [self._ptr[i] for i in range(self._num_tokens - 3, self._num_tokens)]
            tokens_str = f"[{', '.join(map(str, first))}, ..., {', '.join(map(str, last))}]"
        return f"TokenArray({tokens_str}, len={self._num_tokens})"

    def __eq__(self, other) -> bool:
        """Compare two TokenArrays for equality."""
        if isinstance(other, TokenArray):
            if len(self) != len(other):
                return False
            return all(self[i] == other[i] for i in range(len(self)))
        if isinstance(other, list):
            if len(self) != len(other):
                return False
            return all(self[i] == other[i] for i in range(len(self)))
        return NotImplemented
