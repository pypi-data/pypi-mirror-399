"""
Generation output classes.

Provides Generator for streaming and GenerationOutput for results.
"""

import ctypes
import logging
from typing import TYPE_CHECKING

from .._errors import EmptyPromptError, GenerationError
from .._lib import get_lib
from .._types import SamplingParams

if TYPE_CHECKING:
    from .session import ChatSession

logger = logging.getLogger(__name__)


# C struct for generator config
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
        eos_tokens: list[int] | None = None,
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


def _setup_signatures():
    """Set up C function signatures."""
    lib = get_lib()

    lib.tokamino_generator_start.argtypes = [
        ctypes.c_void_p,  # session handle
        ctypes.c_char_p,  # prompt
        ctypes.POINTER(GeneratorConfig),  # config
    ]
    lib.tokamino_generator_start.restype = ctypes.c_void_p

    lib.tokamino_generator_current.argtypes = [ctypes.c_void_p]
    lib.tokamino_generator_current.restype = ctypes.c_uint32

    lib.tokamino_generator_next.argtypes = [ctypes.c_void_p]
    lib.tokamino_generator_next.restype = ctypes.c_uint32

    lib.tokamino_generator_finished.argtypes = [ctypes.c_void_p]
    lib.tokamino_generator_finished.restype = ctypes.c_bool

    lib.tokamino_generator_generated_count.argtypes = [ctypes.c_void_p]
    lib.tokamino_generator_generated_count.restype = ctypes.c_size_t

    lib.tokamino_generator_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_generator_free.restype = None


_setup_signatures()


class Generator:
    """
    Iterator that streams tokens or text from generation.

    Generator is returned by `ChatSession.send()` and provides two ways
    to consume generated content:

    1. **Streaming** - Iterate for real-time chunks:

        >>> for chunk in session.send("Tell me a story"):
        ...     print(chunk, end="", flush=True)

    2. **Collect** - Get the complete result at once:

        >>> result = session.send("Hello").collect()
        >>> print(result.text)

    Chunking Behavior
    -----------------

    By default, chunks are yielded every 100ms for smooth display. Configure
    at session creation with `chunk_interval_ms`.

    Text vs Token Mode
    ------------------

    By default, yields decoded text strings. Configure at session creation
    with `text_mode=False` to yield lists of token IDs for lower-level
    processing.

    See Also
    --------
    ChatSession.send : Creates Generators.
    GenerationOutput : The result type from `.collect()`.
    """

    DONE_TOKEN = 0xFFFFFFFF

    def __init__(
        self,
        session: "ChatSession",
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_k: int,
        top_p: float,
        strategy: int,
        text_mode: bool,
        chunk_size: int | None,
        chunk_interval_ms: int,
        stop_sequences: list[list[int]] | None = None,
    ):
        """
        Initialize a Generator.

        This is an internal constructor. Users should get Generators
        from `ChatSession.send()`, not create them directly.
        """
        self._session = session
        self._text_mode = text_mode
        self._chunk_size = chunk_size
        self._chunk_interval_ms = chunk_interval_ms
        self._started = False
        self._finished = False
        self._gen_ptr = None
        self._tokens: list[int] = []
        self._first_token: int | None = None

        # Stop sequences (tokenized)
        self._stop_sequences = stop_sequences or []
        self._max_stop_len = max((len(s) for s in self._stop_sequences), default=0)

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
        self._chunk_buffer: list[int] = []
        self._last_flush_time: float = 0

    def _start(self):
        """Start the generator (lazy initialization)."""
        if self._started:
            return
        self._started = True

        logger.debug(
            "Starting generation: max_tokens=%d, temp=%.2f, top_k=%d",
            self._config.max_tokens,
            self._config.sampling.temperature,
            self._config.sampling.top_k,
        )

        lib = get_lib()
        self._gen_ptr = lib.tokamino_generator_start(
            self._session._ptr,
            self._prompt,
            ctypes.byref(self._config),
        )
        if not self._gen_ptr:
            # Check if this is an empty prompt error
            if len(self._prompt) == 0 or self._prompt == b"":
                raise EmptyPromptError()
            raise GenerationError("Failed to start generator")

        # Get first token (generated during prefill)
        self._first_token = lib.tokamino_generator_current(self._gen_ptr)
        self._tokens.append(self._first_token)
        logger.debug("Prefill complete, first token: %d", self._first_token)

        import time

        self._last_flush_time = time.time()

    def __iter__(self) -> "Generator":
        """Return self as iterator."""
        return self

    def __next__(self) -> str | list[int]:
        """
        Get the next chunk of generated content.

        Returns
        -------
            If text mode: a string chunk.
            If token mode: a list of token IDs.

        Raises
        ------
            StopIteration: When generation is complete.
            RuntimeError: If generation fails to start.
        """
        self._start()
        return self._next_chunk()

    def next(self) -> str | list[int]:
        """
        Get the next chunk of generated content.

        Alternative to using the iterator protocol. Raises StopIteration
        when generation is complete.

        Returns
        -------
            If text mode: a string chunk.
            If token mode: a list of token IDs.

        Example:
            >>> generator = session.send("Hello")
            >>> chunk = generator.next()
            >>> print(chunk)
        """
        return self.__next__()

    @property
    def finished(self) -> bool:
        """
        Check if generation is complete.

        Returns
        -------
            True if all tokens have been generated, False otherwise.
        """
        return self._finished

    def _should_flush(self) -> bool:
        """Check if we should flush the buffer."""
        if self._chunk_size is not None:
            return len(self._chunk_buffer) >= self._chunk_size
        else:
            import time

            elapsed_ms = (time.time() - self._last_flush_time) * 1000
            return elapsed_ms >= self._chunk_interval_ms

    def _flush_buffer(self) -> str | list[int]:
        """Flush buffer and return chunk (text or token list)."""
        import time

        if self._text_mode:
            result = self._session.decode(self._chunk_buffer)
        else:
            result = self._chunk_buffer.copy()
        self._chunk_buffer.clear()
        self._last_flush_time = time.time()
        return result

    def _check_stop_sequence(self) -> int | None:
        """Check if tokens end with any stop sequence.

        Returns the length of matched stop sequence, or None if no match.
        """
        if not self._stop_sequences:
            return None

        for stop_seq in self._stop_sequences:
            seq_len = len(stop_seq)
            if len(self._tokens) >= seq_len:
                if self._tokens[-seq_len:] == stop_seq:
                    return seq_len
        return None

    def _next_chunk(self) -> str | list[int]:
        """Yield next chunk of tokens or text."""
        import time

        lib = get_lib()

        # First token should be yielded immediately
        if self._first_token is not None:
            self._chunk_buffer.append(self._first_token)
            self._first_token = None
            self._last_flush_time = time.time()
            return self._flush_buffer()

        # If already finished, flush remaining or stop
        if self._finished:
            if self._chunk_buffer:
                return self._flush_buffer()
            raise StopIteration

        # Collect tokens until flush condition met
        while True:
            token = lib.tokamino_generator_next(self._gen_ptr)

            if token == self.DONE_TOKEN:
                self._finished = True
                if self._chunk_buffer:
                    return self._flush_buffer()
                raise StopIteration

            self._tokens.append(token)
            self._chunk_buffer.append(token)

            # Check for stop sequence match
            stop_len = self._check_stop_sequence()
            if stop_len is not None:
                # Remove the stop sequence tokens from output
                self._tokens = self._tokens[:-stop_len]
                # Remove from chunk buffer too (may be partial)
                remove_from_buffer = min(stop_len, len(self._chunk_buffer))
                self._chunk_buffer = self._chunk_buffer[:-remove_from_buffer]
                self._finished = True
                if self._chunk_buffer:
                    return self._flush_buffer()
                raise StopIteration

            if self._should_flush():
                return self._flush_buffer()

    def collect(self) -> "GenerationOutput":
        """
        Consume all tokens and return the complete result.

        This is useful when you want the full response without streaming.
        If iteration has already started, collects remaining tokens.

        Returns
        -------
            GenerationOutput containing the complete text and metadata.

        Raises
        ------
            RuntimeError: If generation fails to start.

        Example:
            >>> result = session.send("What is Python?").collect()
            >>> print(result.text)
            'Python is a programming language...'
            >>> print(f"Generated {result.generated_len} tokens")
        """
        lib = get_lib()
        self._start()

        # Consume first token if not yet consumed
        if self._first_token is not None:
            self._first_token = None

        # Consume remaining tokens
        while not self._finished:
            token = lib.tokamino_generator_next(self._gen_ptr)
            if token == self.DONE_TOKEN:
                self._finished = True
                break
            self._tokens.append(token)

            # Check for stop sequence match
            stop_len = self._check_stop_sequence()
            if stop_len is not None:
                # Remove the stop sequence tokens from output
                self._tokens = self._tokens[:-stop_len]
                self._finished = True
                break

        # Get stats
        generated_count = lib.tokamino_generator_generated_count(self._gen_ptr)

        # Decode all tokens
        text = self._session.decode(self._tokens)

        logger.debug(
            "Generation complete: %d tokens generated, %d total",
            generated_count,
            len(self._tokens),
        )

        return GenerationOutput(
            tokens=self._tokens.copy(),
            text=text,
            prompt_len=len(self._tokens) - generated_count,
            generated_len=generated_count,
            prefill_time_ms=0,
            decode_time_ms=0,
        )

    def __del__(self):
        """Free the generator."""
        if hasattr(self, "_gen_ptr") and self._gen_ptr:
            lib = get_lib()
            lib.tokamino_generator_free(self._gen_ptr)
            self._gen_ptr = None


class GenerationOutput:
    """
    Complete result from text generation.

    GenerationOutput is returned by `Generator.collect()` and contains
    the full generated text along with metadata about the generation.

    Attributes
    ----------
    text : str
        The generated text (decoded from tokens).

    tokens : List[int]
        All token IDs (prompt + generated).

    prompt_len : int
        Number of tokens in the prompt.

    generated_len : int
        Number of tokens that were generated.

    prefill_time_ms : float
        Time spent processing the prompt (milliseconds).

    decode_time_ms : float
        Time spent generating tokens (milliseconds).

    Example
    -------

        >>> result = session.send("What is Python?").collect()
        >>> print(result.text)
        'Python is a programming language...'

        >>> print(f"Prompt: {result.prompt_len} tokens")
        >>> print(f"Generated: {result.generated_len} tokens")

        >>> # Performance metrics
        >>> print(f"Speed: {result.tokens_per_second:.1f} tok/s")

    See Also
    --------
    Generator.collect : Creates GenerationOutput.
    ChatSession.send : Creates Generator for streaming.
    """

    def __init__(
        self,
        tokens: list[int],
        text: str,
        prompt_len: int,
        generated_len: int,
        prefill_time_ms: float,
        decode_time_ms: float,
    ):
        """
        Initialize a GenerationOutput.

        This is an internal constructor. Users get GenerationOutputs from
        `Generator.collect()`.
        """
        self.tokens = tokens
        self.text = text
        self.prompt_len = prompt_len
        self.generated_len = generated_len
        self.prefill_time_ms = prefill_time_ms
        self.decode_time_ms = decode_time_ms

    @property
    def total_time_ms(self) -> float:
        """
        Total generation time in milliseconds.

        Includes both prefill (prompt processing) and decode (generation).
        """
        return self.prefill_time_ms + self.decode_time_ms

    @property
    def tokens_per_second(self) -> float:
        """
        Generation speed in tokens per second.

        Measures decode performance (excludes prefill time). Returns 0
        if timing information is not available.
        """
        if self.decode_time_ms == 0:
            return 0
        return (self.generated_len - 1) * 1000 / self.decode_time_ms

    def __repr__(self) -> str:
        """Return string representation with text preview."""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"GenerationOutput(text={text_preview!r}, generated={self.generated_len} tokens)"

    def __str__(self) -> str:
        """Return the generated text."""
        return self.text
