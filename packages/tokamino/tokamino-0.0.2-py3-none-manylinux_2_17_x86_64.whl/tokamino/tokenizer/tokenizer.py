"""
Tokenizer - Text encoding and decoding.

Tokenization is the process of converting text into tokens - the fundamental
units that language models understand. This module provides the Tokenizer class
for encoding text to tokens and decoding tokens back to text.
"""

import ctypes
import logging

from .._lib import get_lib
from .template import ChatTemplate
from .token_array import TokenArray

logger = logging.getLogger(__name__)

# =============================================================================
# C Struct Definitions
# =============================================================================


class EncodeResult(ctypes.Structure):
    """Result from encode operation (C struct)."""

    _fields_ = [
        ("tokens", ctypes.POINTER(ctypes.c_uint32)),
        ("num_tokens", ctypes.c_size_t),
        ("error_msg", ctypes.c_char_p),
    ]


class DecodeResult(ctypes.Structure):
    """Result from decode operation (C struct)."""

    _fields_ = [
        ("text", ctypes.POINTER(ctypes.c_char)),  # raw pointer, not null-terminated
        ("text_len", ctypes.c_size_t),
        ("error_msg", ctypes.c_char_p),
    ]


class EosTokenResult(ctypes.Structure):
    """Result from get_eos_tokens."""

    _fields_ = [
        ("tokens", ctypes.POINTER(ctypes.c_uint32)),
        ("num_tokens", ctypes.c_size_t),
    ]


class SpecialTokensResult(ctypes.Structure):
    """Result from get_special_tokens."""

    _fields_ = [
        ("bos_token_id", ctypes.c_int32),
        ("unk_token_id", ctypes.c_int32),
        ("pad_token_id", ctypes.c_int32),
    ]


class TokenizeResult(ctypes.Structure):
    """Result from tokenize operation (C struct)."""

    _fields_ = [
        ("tokens", ctypes.POINTER(ctypes.c_char_p)),  # Array of null-terminated strings
        ("num_tokens", ctypes.c_size_t),
        ("error_msg", ctypes.c_char_p),
    ]


# =============================================================================
# C Function Signatures Setup
# =============================================================================


def _setup_signatures():
    """Set up C function signatures for tokenizer functions."""
    lib = get_lib()

    # -------------------------------------------------------------------------
    # Session creation (for full inference, used by Session subclass)
    # -------------------------------------------------------------------------
    lib.tokamino_session_create.argtypes = [ctypes.c_char_p]
    lib.tokamino_session_create.restype = ctypes.c_void_p

    lib.tokamino_session_create_with_seed.argtypes = [ctypes.c_char_p, ctypes.c_uint64]
    lib.tokamino_session_create_with_seed.restype = ctypes.c_void_p

    lib.tokamino_session_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_session_free.restype = None

    # -------------------------------------------------------------------------
    # Tokenizer-only API (lightweight, no model weights)
    # -------------------------------------------------------------------------
    lib.tokamino_tokenizer_create.argtypes = [ctypes.c_char_p]
    lib.tokamino_tokenizer_create.restype = ctypes.c_void_p

    lib.tokamino_tokenizer_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_tokenizer_free.restype = None

    lib.tokamino_tokenizer_encode.argtypes = [
        ctypes.c_void_p,  # tokenizer handle
        ctypes.POINTER(ctypes.c_char),  # text (raw pointer, not c_char_p which is null-terminated)
        ctypes.c_size_t,  # text_len
    ]
    lib.tokamino_tokenizer_encode.restype = EncodeResult

    lib.tokamino_tokenizer_decode.argtypes = [
        ctypes.c_void_p,  # tokenizer handle
        ctypes.POINTER(ctypes.c_uint32),  # tokens
        ctypes.c_size_t,  # num_tokens
    ]
    lib.tokamino_tokenizer_decode.restype = DecodeResult

    lib.tokamino_decode_result_free.argtypes = [
        ctypes.POINTER(ctypes.c_char),  # text
        ctypes.c_size_t,  # text_len
    ]
    lib.tokamino_decode_result_free.restype = None

    lib.tokamino_tokenizer_get_eos_tokens.argtypes = [ctypes.c_void_p]
    lib.tokamino_tokenizer_get_eos_tokens.restype = EosTokenResult

    lib.tokamino_tokenizer_get_model_dir.argtypes = [ctypes.c_void_p]
    lib.tokamino_tokenizer_get_model_dir.restype = ctypes.c_void_p

    # -------------------------------------------------------------------------
    # Vocabulary access API
    # -------------------------------------------------------------------------
    lib.tokamino_tokenizer_get_vocab_size.argtypes = [ctypes.c_void_p]
    lib.tokamino_tokenizer_get_vocab_size.restype = ctypes.c_size_t

    lib.tokamino_tokenizer_get_special_tokens.argtypes = [ctypes.c_void_p]
    lib.tokamino_tokenizer_get_special_tokens.restype = SpecialTokensResult

    lib.tokamino_tokenizer_id_to_token.argtypes = [
        ctypes.c_void_p,  # tokenizer handle
        ctypes.c_int32,  # token_id
    ]
    lib.tokamino_tokenizer_id_to_token.restype = ctypes.c_void_p

    lib.tokamino_tokenizer_token_to_id.argtypes = [
        ctypes.c_void_p,  # tokenizer handle
        ctypes.POINTER(ctypes.c_char),  # token
        ctypes.c_size_t,  # token_len
    ]
    lib.tokamino_tokenizer_token_to_id.restype = ctypes.c_int32

    lib.tokamino_tokenizer_tokenize.argtypes = [
        ctypes.c_void_p,  # tokenizer handle
        ctypes.POINTER(ctypes.c_char),  # text
        ctypes.c_size_t,  # text_len
    ]
    lib.tokamino_tokenizer_tokenize.restype = TokenizeResult

    lib.tokamino_tokenize_result_free.argtypes = [
        ctypes.POINTER(ctypes.c_char_p),  # tokens array
        ctypes.c_size_t,  # num_tokens
    ]
    lib.tokamino_tokenize_result_free.restype = None

    # -------------------------------------------------------------------------
    # Model path resolution
    # -------------------------------------------------------------------------
    lib.tokamino_resolve_model_path.argtypes = [ctypes.c_char_p]
    lib.tokamino_resolve_model_path.restype = ctypes.c_void_p

    # -------------------------------------------------------------------------
    # Encode/Decode (session-based, used by Session subclass)
    # -------------------------------------------------------------------------
    lib.tokamino_encode.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.POINTER(ctypes.c_char),  # text (raw pointer, not c_char_p which is null-terminated)
        ctypes.c_size_t,  # text_len
    ]
    lib.tokamino_encode.restype = EncodeResult

    lib.tokamino_decode.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.POINTER(ctypes.c_uint32),  # tokens
        ctypes.c_size_t,  # num_tokens
    ]
    lib.tokamino_decode.restype = DecodeResult

    lib.tokamino_tokens_free.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
    ]
    lib.tokamino_tokens_free.restype = None

    lib.tokamino_text_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_text_free.restype = None

    # -------------------------------------------------------------------------
    # EOS tokens (session-based)
    # -------------------------------------------------------------------------
    lib.tokamino_get_eos_tokens.argtypes = [ctypes.c_char_p]
    lib.tokamino_get_eos_tokens.restype = EosTokenResult

    lib.tokamino_session_get_eos_tokens.argtypes = [ctypes.c_void_p]
    lib.tokamino_session_get_eos_tokens.restype = EosTokenResult


_setup_signatures()


# =============================================================================
# Tokenizer Class
# =============================================================================


class Tokenizer:
    """
    Tokenizer for encoding text to tokens and decoding tokens to text.

    A tokenizer converts text into tokens - the fundamental units that language
    models process. Each token is represented by an integer ID from the model's
    vocabulary (typically 32,000 to 150,000+ tokens).

    Tokenization splits text into subword pieces. For example, "tokenization"
    might become ["token", "ization"]. This allows models to handle any text,
    including rare words and multiple languages.

    Attributes
    ----------
    model_path : str
        The resolved path to the model directory.

    vocab_size : int
        Number of tokens in the vocabulary.

    eos_tokens : List[int]
        Token IDs that signal end of generation.

    bos_token_id : Optional[int]
        Beginning-of-sequence token ID, or None if not defined.

    pad_token_id : Optional[int]
        Padding token ID, or None if not defined.

    See Also
    --------
    tokamino.encode : Convenience function for one-off encoding.
    tokamino.decode : Convenience function for one-off decoding.
    Client : For text generation with full model.
    """

    # Flag to indicate whether this is a lightweight tokenizer-only handle
    _is_tokenizer_only: bool = True

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def __init__(self, model: str):
        """
        Create a tokenizer for a model.

        The tokenizer is loaded from the model's `tokenizer.json` file.
        This is a lightweight operation that doesn't load model weights.

        Args:
            model: Path to model directory or HuggingFace model ID.
                - Local path: `"./models/qwen"` or `"/path/to/model"`
                - HuggingFace: `"Qwen/Qwen3-0.6B"` (downloaded automatically)

        Raises
        ------
            RuntimeError: If the model path is invalid or tokenizer files
                are missing.

        Example:
            >>> # From HuggingFace (downloads on first use)
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # From local path
            >>> tokenizer = Tokenizer("./models/my-model")

            >>> # Check what was loaded
            >>> print(tokenizer.vocab_size)
            151936
        """
        logger.debug("Creating Tokenizer for %s", model)
        self._model_dir = self._resolve_model_path(model)
        self._ptr = self._create_handle()
        if not self._ptr:
            raise RuntimeError(f"Failed to load tokenizer from {self._model_dir}")
        self._load_eos_tokens()
        self._load_special_tokens()
        self._chat_template = ChatTemplate(self._model_dir)
        logger.debug("Tokenizer loaded: %s", self._model_dir)

    def _resolve_model_path(self, model: str) -> str:
        """Resolve model path (local or HuggingFace)."""
        lib = get_lib()
        resolved_ptr = lib.tokamino_resolve_model_path(model.encode("utf-8"))
        if not resolved_ptr:
            raise RuntimeError(
                f"Failed to resolve model path '{model}'. "
                f"Provide a valid local path or HuggingFace model ID."
            )
        model_dir = ctypes.cast(resolved_ptr, ctypes.c_char_p).value.decode("utf-8")
        lib.tokamino_text_free(resolved_ptr)
        return model_dir

    def _create_handle(self):
        """Create the internal handle. Subclasses can override."""
        lib = get_lib()
        return lib.tokamino_tokenizer_create(self._model_dir.encode("utf-8"))

    def _load_eos_tokens(self):
        """Load EOS token IDs from the model."""
        lib = get_lib()
        if self._is_tokenizer_only:
            eos_result = lib.tokamino_tokenizer_get_eos_tokens(self._ptr)
        else:
            eos_result = lib.tokamino_session_get_eos_tokens(self._ptr)
        if eos_result.tokens and eos_result.num_tokens > 0:
            self._eos_tokens = [eos_result.tokens[i] for i in range(eos_result.num_tokens)]
            lib.tokamino_tokens_free(eos_result.tokens, eos_result.num_tokens)
        else:
            self._eos_tokens = []

    def _load_special_tokens(self):
        """Load special token IDs from the model."""
        lib = get_lib()
        if self._is_tokenizer_only:
            result = lib.tokamino_tokenizer_get_special_tokens(self._ptr)
        else:
            tmp = lib.tokamino_tokenizer_create(self._model_dir.encode("utf-8"))
            if not tmp:
                self._bos_token_id = None
                self._unk_token_id = None
                self._pad_token_id = None
                return
            result = lib.tokamino_tokenizer_get_special_tokens(tmp)
            lib.tokamino_tokenizer_free(tmp)
        # -1 means not set
        self._bos_token_id = result.bos_token_id if result.bos_token_id >= 0 else None
        self._unk_token_id = result.unk_token_id if result.unk_token_id >= 0 else None
        self._pad_token_id = result.pad_token_id if result.pad_token_id >= 0 else None

    @property
    def model_path(self) -> str:
        """
        The resolved path to the model directory.

        This is the actual filesystem path after resolving HuggingFace IDs
        or relative paths.

        Returns
        -------
            Absolute path to the model directory.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")
            >>> tokenizer.model_path
            '/home/user/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/...'
        """
        return self._model_dir

    def _free_handle(self):
        """Free the internal handle."""
        if hasattr(self, "_ptr") and self._ptr:
            lib = get_lib()
            if self._is_tokenizer_only:
                lib.tokamino_tokenizer_free(self._ptr)
            else:
                lib.tokamino_session_free(self._ptr)
            self._ptr = None

    def __del__(self):
        """Free the tokenizer resources."""
        self._free_handle()

    def __repr__(self) -> str:
        return f"Tokenizer({self._model_dir!r})"

    # =========================================================================
    # Core Encoding/Decoding
    # =========================================================================

    def encode(self, text: str) -> TokenArray:
        """
        Convert text to token IDs.

        Tokenization splits text into subword pieces and maps each piece to
        its integer ID from the vocabulary. The result is a `TokenArray` that
        supports zero-copy NumPy conversion.

        Args:
            text: The text to tokenize. Can contain any Unicode characters
                including emojis and non-Latin scripts.

        Returns
        -------
            TokenArray containing the token IDs. Use `len()` to get the
            count, `list()` or `.tolist()` to convert to a Python list,
            or `np.asarray()` for zero-copy NumPy access.

        Raises
        ------
            RuntimeError: If encoding fails (rare, usually indicates
                corrupted tokenizer files).

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # Basic encoding
            >>> tokens = tokenizer.encode("Hello, world!")
            >>> print(len(tokens))
            4

            >>> # Get the actual token IDs
            >>> print(tokens.tolist())
            [9707, 11, 1879, 0]

            >>> # Zero-copy NumPy access (efficient for large texts)
            >>> import numpy as np
            >>> arr = np.asarray(tokens)
            >>> print(arr.dtype)
            uint32

            >>> # Check if text fits in context window
            >>> if len(tokenizer.encode(long_text)) > 4096:
            ...     print("Text is too long!")

        Note:
            Token counts vary by model and language. English averages about
            1 token per 4 characters. Other languages may use more tokens.

        See Also
        --------
            decode : Convert token IDs back to text.
            tokenize : Get token strings instead of IDs.
            count_tokens : Convenience method for just the count.
        """
        lib = get_lib()
        text_bytes = text.encode("utf-8")
        # Create a char array from bytes (supports null bytes, unlike c_char_p)
        text_array = (ctypes.c_char * len(text_bytes)).from_buffer_copy(text_bytes)
        if self._is_tokenizer_only:
            result = lib.tokamino_tokenizer_encode(self._ptr, text_array, len(text_bytes))
        else:
            result = lib.tokamino_encode(self._ptr, text_array, len(text_bytes))

        if result.error_msg:
            error = result.error_msg.decode("utf-8")
            raise RuntimeError(f"Encode failed: {error}")

        return TokenArray(result.tokens, result.num_tokens)

    def decode(
        self,
        tokens: TokenArray | list[int],
        num_tokens: int | None = None,
    ) -> str:
        """
        Convert token IDs back to text.

        This reverses the encoding process, reconstructing the original text
        from token IDs. The output is UTF-8 text.

        Args:
            tokens: Token IDs to decode. Can be a `TokenArray` (from encode()),
                a Python list of integers, or a raw ctypes pointer.

            num_tokens: Number of tokens (only required when passing a raw
                pointer, otherwise ignored).

        Returns
        -------
            The decoded text string.

        Raises
        ------
            RuntimeError: If decoding fails (e.g., invalid token IDs).
            ValueError: If `num_tokens` is missing when using a raw pointer.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # Decode a TokenArray
            >>> tokens = tokenizer.encode("Hello!")
            >>> text = tokenizer.decode(tokens)
            >>> print(text)
            Hello!

            >>> # Decode a list of IDs
            >>> text = tokenizer.decode([9707, 11, 1879, 0])
            >>> print(text)
            Hello, world!

            >>> # Round-trip encoding
            >>> original = "The quick brown fox"
            >>> assert tokenizer.decode(tokenizer.encode(original)) == original

        Note:
            Decoding is not always a perfect inverse of encoding. Some
            whitespace normalization may occur, and invalid token sequences
            may produce unexpected output.

        See Also
        --------
            encode : Convert text to token IDs.
        """
        lib = get_lib()

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

        if self._is_tokenizer_only:
            result = lib.tokamino_tokenizer_decode(self._ptr, tokens_ptr, num_tokens)
        else:
            result = lib.tokamino_decode(self._ptr, tokens_ptr, num_tokens)

        if result.error_msg:
            error = result.error_msg.decode("utf-8")
            raise RuntimeError(f"Decode failed: {error}")

        if not result.text or result.text_len == 0:
            return ""

        # Extract bytes using length (supports null bytes in output)
        text_bytes = ctypes.string_at(result.text, result.text_len)
        text = text_bytes.decode("utf-8")
        lib.tokamino_decode_result_free(result.text, result.text_len)
        return text

    def tokenize(self, text: str) -> list[str]:
        """
        Split text into token strings.

        Unlike `encode()` which returns integer IDs, this returns the actual
        string pieces that the tokenizer produces. This is useful for
        understanding how the model "sees" your text.

        Args:
            text: The text to tokenize.

        Returns
        -------
            List of token strings. Note that tokens may include special
            characters like 'Ġ' (representing a leading space in GPT-style
            tokenizers) or '▁' (in SentencePiece tokenizers).

        Raises
        ------
            RuntimeError: If tokenization fails.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # See how text is split
            >>> tokenizer.tokenize("Hello, world!")
            ['Hello', ',', ' world', '!']

            >>> # Subword tokenization in action
            >>> tokenizer.tokenize("tokenization")
            ['token', 'ization']

            >>> # Special characters show word boundaries
            >>> tokenizer.tokenize("The quick brown fox")
            ['The', ' quick', ' brown', ' fox']

        Note:
            This is less efficient than `encode()` because it allocates
            strings. Use `encode()` for performance-critical code.

        See Also
        --------
            encode : Get token IDs (more efficient).
            id_to_token : Convert a single ID to its string.
        """
        lib = get_lib()
        text_bytes = text.encode("utf-8")
        text_array = (ctypes.c_char * len(text_bytes)).from_buffer_copy(text_bytes)

        result = lib.tokamino_tokenizer_tokenize(self._ptr, text_array, len(text_bytes))

        if result.error_msg:
            error = result.error_msg.decode("utf-8")
            raise RuntimeError(f"Tokenize failed: {error}")

        if not result.tokens or result.num_tokens == 0:
            return []

        # Extract token strings
        tokens = []
        for i in range(result.num_tokens):
            token_ptr = result.tokens[i]
            if token_ptr:
                tokens.append(token_ptr.decode("utf-8"))
            else:
                tokens.append("")

        lib.tokamino_tokenize_result_free(result.tokens, result.num_tokens)
        return tokens

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text.

        A convenience method that returns just the token count without
        allocating the full token array.

        Args:
            text: The text to count tokens for.

        Returns
        -------
            Number of tokens.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # Check token count
            >>> count = tokenizer.count_tokens("Hello, world!")
            >>> print(f"Tokens: {count}")
            Tokens: 4

            >>> # Validate context window limits
            >>> MAX_CONTEXT = 4096
            >>> prompt = build_prompt(user_input)
            >>> if tokenizer.count_tokens(prompt) > MAX_CONTEXT:
            ...     # Truncate or summarize...

        See Also
        --------
            encode : Get the actual token IDs.
        """
        # TODO: Could optimize with a C API that only returns count
        tokens = self.encode(text)
        return len(tokens)

    # =========================================================================
    # Vocabulary Access
    # =========================================================================

    @property
    def vocab_size(self) -> int:
        """
        The number of tokens in the vocabulary.

        This is the total number of unique tokens the model can produce,
        including special tokens. Common sizes are 32,000 (LLaMA), 50,000
        (GPT-2), and 150,000+ (Qwen, multilingual models).

        Returns
        -------
            Vocabulary size as an integer.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")
            >>> print(f"Vocab size: {tokenizer.vocab_size:,}")
            Vocab size: 151,936
        """
        lib = get_lib()
        return lib.tokamino_tokenizer_get_vocab_size(self._ptr)

    def id_to_token(self, token_id: int) -> str | None:
        """
        Get the string representation of a token ID.

        Args:
            token_id: The token ID to look up (0 to vocab_size-1).

        Returns
        -------
            The token string, or None if the ID is out of range.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # Look up specific tokens
            >>> tokenizer.id_to_token(0)
            '!'

            >>> # Decode token by token
            >>> tokens = tokenizer.encode("Hi")
            >>> for tid in tokens.tolist():
            ...     print(f"{tid} -> {tokenizer.id_to_token(tid)!r}")
            9707 -> 'Hi'

            >>> # Out of range returns None
            >>> tokenizer.id_to_token(999999999)
            None

        See Also
        --------
            token_to_id : Reverse lookup (string to ID).
        """
        lib = get_lib()
        result_ptr = lib.tokamino_tokenizer_id_to_token(self._ptr, token_id)
        if not result_ptr:
            return None
        token = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")
        lib.tokamino_text_free(result_ptr)
        return token

    def token_to_id(self, token: str) -> int | None:
        """
        Get the ID of a token string.

        Args:
            token: The token string to look up. Must be an exact match
                for a token in the vocabulary.

        Returns
        -------
            The token ID, or None if the token is not in the vocabulary.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # Look up known tokens
            >>> tokenizer.token_to_id("hello")
            14990

            >>> # Unknown tokens return None
            >>> tokenizer.token_to_id("xyzzy123")
            None

            >>> # Case sensitive
            >>> tokenizer.token_to_id("Hello")  # Different from "hello"
            9707

        See Also
        --------
            id_to_token : Reverse lookup (ID to string).
        """
        lib = get_lib()
        token_bytes = token.encode("utf-8")
        token_array = (ctypes.c_char * len(token_bytes)).from_buffer_copy(token_bytes)
        result = lib.tokamino_tokenizer_token_to_id(self._ptr, token_array, len(token_bytes))
        if result < 0:
            return None
        return result

    # =========================================================================
    # Special Tokens
    # =========================================================================

    @property
    def eos_tokens(self) -> list[int]:
        """
        Token IDs that signal the end of generation.

        Most models have one or more "end of sequence" tokens that tell
        the model to stop generating. Some models have multiple EOS tokens
        (e.g., both `<|endoftext|>` and `<|im_end|>` in chat models).

        Returns
        -------
            List of EOS token IDs. May be empty if the model doesn't
            define EOS tokens.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")
            >>> print(tokenizer.eos_tokens)
            [151645, 151643]

            >>> # See what they represent
            >>> for eos_id in tokenizer.eos_tokens:
            ...     print(f"{eos_id} -> {tokenizer.id_to_token(eos_id)!r}")
            151645 -> '<|im_end|>'
            151643 -> '<|endoftext|>'
        """
        return self._eos_tokens.copy()

    @property
    def bos_token_id(self) -> int | None:
        """
        The beginning-of-sequence token ID.

        Some models prepend this token to indicate the start of input.
        Not all models use a BOS token.

        Returns
        -------
            BOS token ID, or None if not defined.

        Example:
            >>> tokenizer = Tokenizer("meta-llama/Llama-2-7b")
            >>> print(tokenizer.bos_token_id)
            1
            >>> print(tokenizer.id_to_token(1))
            '<s>'
        """
        return self._bos_token_id

    @property
    def unk_token_id(self) -> int | None:
        """
        The unknown token ID.

        Used when the tokenizer encounters text it can't tokenize (rare
        with modern subword tokenizers).

        Returns
        -------
            UNK token ID, or None if not defined.
        """
        return self._unk_token_id

    @property
    def pad_token_id(self) -> int | None:
        """
        The padding token ID.

        Used to pad sequences to equal length in batch processing.
        Not all models define a padding token.

        Returns
        -------
            PAD token ID, or None if not defined.
        """
        return self._pad_token_id

    # =========================================================================
    # Chat Templates
    # =========================================================================

    @property
    def chat_template(self) -> ChatTemplate:
        """
        The chat template formatter for this model.

        Chat templates format conversations into the specific format the
        model expects. Each model family has its own format (ChatML for
        Qwen, Llama format for LLaMA, etc.).

        Returns
        -------
            ChatTemplate instance for this model.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")
            >>> template = tokenizer.chat_template
            >>> prompt = template.apply([
            ...     {"role": "user", "content": "Hello!"}
            ... ])
        """
        return self._chat_template

    def apply_chat_template(
        self,
        messages: list,
        add_generation_prompt: bool = True,
    ) -> str:
        """
        Format a conversation using the model's chat template.

        Chat templates convert a list of messages into the specific format
        the model was trained on. This is essential for chat/instruct models
        to work correctly.

        Args:
            messages: List of message dictionaries. Each message must have:
                - `role`: One of "system", "user", "assistant", or "tool"
                - `content`: The message text

            add_generation_prompt: If True (default), adds the assistant's
                turn marker at the end, prompting the model to generate a
                response. Set to False for assistant prefill (where you
                provide the start of the assistant's response).

        Returns
        -------
            Formatted prompt string ready for the model.

        Raises
        ------
            RuntimeError: If template rendering fails.

        Example:
            >>> tokenizer = Tokenizer("Qwen/Qwen3-0.6B")

            >>> # Simple user message
            >>> prompt = tokenizer.apply_chat_template([
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ])
            >>> print(prompt)
            <|im_start|>user
            What is 2+2?<|im_end|>
            <|im_start|>assistant

            >>> # With system message
            >>> prompt = tokenizer.apply_chat_template([
            ...     {"role": "system", "content": "You are a math tutor."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ])

            >>> # Multi-turn conversation
            >>> prompt = tokenizer.apply_chat_template([
            ...     {"role": "user", "content": "Hi!"},
            ...     {"role": "assistant", "content": "Hello! How can I help?"},
            ...     {"role": "user", "content": "What's the weather?"}
            ... ])

            >>> # Assistant prefill (for constrained generation)
            >>> prompt = tokenizer.apply_chat_template([
            ...     {"role": "user", "content": "Count to 5"},
            ...     {"role": "assistant", "content": "1, 2, 3,"}
            ... ], add_generation_prompt=False)

        See Also
        --------
            Client.chat : Higher-level chat API with automatic history.
        """
        return self._chat_template.apply(messages, add_generation_prompt)
