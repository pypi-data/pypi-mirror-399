"""
ChatSession - Stateful text generation with language models.

The ChatSession class is the main interface for generating text with LLMs.
It loads a model and provides a simple send() method for multi-turn conversations.
"""

import logging

from .._lib import get_lib
from .._types import SamplingStrategy
from ..tokenizer import Tokenizer
from .output import Generator

logger = logging.getLogger(__name__)


class ChatSession(Tokenizer):
    """
    Stateful chat session with a language model.

    ChatSession loads a model and maintains conversation state across turns.
    It extends Tokenizer, so you can also use it for encoding/decoding text.

    Quick Start
    -----------

    The simplest way to use ChatSession:

        >>> session = ChatSession("Qwen/Qwen3-0.6B")

        >>> # Quick one-liner (blocking)
        >>> answer = session("What is 2+2?")

        >>> # Stream a response
        >>> for chunk in session.send("Tell me a story"):
        ...     print(chunk, end="", flush=True)

        >>> # Get full result with metadata
        >>> result = session.send("Hello").collect()
        >>> print(result.text)

    Multi-turn conversations maintain history automatically:

        >>> session.system("You are a math tutor.")
        >>> for chunk in session.send("What is 2+2?"):
        ...     print(chunk, end="")
        >>> for chunk in session.send("And 3+3?"):  # Remembers context
        ...     print(chunk, end="")

    Generation Parameters
    ---------------------

    Set parameters at creation or adjust them anytime via properties:

        >>> # Set at creation
        >>> session = ChatSession("model", temperature=1.2, max_tokens=100)

        >>> # Adjust later
        >>> session.temperature = 0.3  # More focused
        >>> session.max_tokens = 50    # Shorter responses

    **temperature** (default: 0.7)
        Controls randomness. Higher = more creative, lower = more focused.

    **top_k** (default: 50)
        Limits selection to the k most likely next tokens.

    **top_p** (default: 0.9)
        Nucleus sampling threshold.

    **max_tokens** (default: 256)
        Maximum number of tokens to generate.

    Attributes
    ----------
    history : list[dict]
        Current conversation history (user and assistant messages).
    temperature : float
        Current temperature setting (read/write).
    max_tokens : int
        Current max tokens setting (read/write).
    top_k : int
        Current top-k setting (read/write).
    top_p : float
        Current top-p setting (read/write).

    See Also
    --------
    Tokenizer : For tokenization without loading model weights.
    """

    # ChatSession uses full model (not tokenizer-only)
    _is_tokenizer_only: bool = False

    def __init__(
        self,
        model: str,
        seed: int = 0,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        strategy: int = SamplingStrategy.TOP_K,
        stop_sequences: list[str] | None = None,
        chunk_interval_ms: int = 100,
        text_mode: bool = True,
    ):
        """
        Create a new ChatSession for a model.

        Loads the full model including weights, which may take a few seconds
        depending on model size. Once loaded, generation is fast.

        Args:
            model: Path to model directory or HuggingFace model ID.
                - Local path: `"./models/qwen"` or `"/path/to/model"`
                - HuggingFace: `"Qwen/Qwen3-0.6B"` (downloaded automatically)

            seed: Random seed for reproducible sampling. Default is 0, which
                uses a time-based seed for different results each run. Set
                to a specific value (e.g., 42) for reproducible output.

            max_tokens: Maximum tokens to generate per response. Default 256.

            temperature: Randomness control (0.0-2.0). Default 0.7.
                - 0.0 = deterministic (greedy)
                - 0.7 = balanced
                - 1.5+ = creative

            top_k: Top-k sampling parameter. Default 50.

            top_p: Nucleus sampling threshold. Default 0.9.

            strategy: Sampling strategy. Default TOP_K.

            stop_sequences: List of strings that will stop generation when
                encountered. Each string is tokenized and matched as a token
                sequence. Default None (only stop on EOS tokens).

            chunk_interval_ms: Milliseconds between streaming chunks. Default 100.

            text_mode: If True (default), stream yields text strings.
                If False, yields lists of token IDs.

        Raises:
            RuntimeError: If the model cannot be loaded.

        Example:
            >>> session = ChatSession("Qwen/Qwen3-0.6B")

            >>> # With custom parameters
            >>> session = ChatSession(
            ...     "Qwen/Qwen3-0.6B",
            ...     seed=42,
            ...     temperature=0.3,
            ...     max_tokens=100,
            ... )

            >>> # With stop sequences
            >>> session = ChatSession(
            ...     "Qwen/Qwen3-0.6B",
            ...     stop_sequences=["\\n\\n", "END"],
            ... )

            >>> # Use as context manager
            >>> with ChatSession("Qwen/Qwen3-0.6B") as session:
            ...     for chunk in session.send("Hello!"):
            ...         print(chunk, end="")
        """
        logger.debug("Creating ChatSession for %s", model)
        self._seed = seed
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p
        self._strategy = strategy
        self._stop_sequences_raw = stop_sequences or []
        self._stop_sequences_tokens: list[list[int]] | None = None  # Tokenized lazily
        self._chunk_interval_ms = chunk_interval_ms
        self._text_mode = text_mode
        self._chat_history: list[dict] = []
        self._system_prompt: str | None = None
        super().__init__(model)
        logger.info("ChatSession loaded: %s", self._model_dir)

    def _create_handle(self):
        """Create session handle with seed support."""
        lib = get_lib()
        if self._seed == 0:
            return lib.tokamino_session_create(self._model_dir.encode("utf-8"))
        return lib.tokamino_session_create_with_seed(self._model_dir.encode("utf-8"), self._seed)

    # -------------------------------------------------------------------------
    # Generation parameter properties (read/write)
    # -------------------------------------------------------------------------

    @property
    def temperature(self) -> float:
        """Current temperature setting."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set temperature (0.0-2.0)."""
        self._temperature = value

    @property
    def max_tokens(self) -> int:
        """Current max tokens setting."""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set max tokens."""
        self._max_tokens = value

    @property
    def top_k(self) -> int:
        """Current top-k setting."""
        return self._top_k

    @top_k.setter
    def top_k(self, value: int) -> None:
        """Set top-k."""
        self._top_k = value

    @property
    def top_p(self) -> float:
        """Current top-p setting."""
        return self._top_p

    @top_p.setter
    def top_p(self, value: float) -> None:
        """Set top-p."""
        self._top_p = value

    @property
    def strategy(self) -> int:
        """Current sampling strategy."""
        return self._strategy

    @strategy.setter
    def strategy(self, value: int) -> None:
        """Set sampling strategy."""
        self._strategy = value

    @property
    def stop_sequences(self) -> list[str]:
        """Current stop sequences (as strings)."""
        return self._stop_sequences_raw.copy()

    @stop_sequences.setter
    def stop_sequences(self, value: list[str]) -> None:
        """Set stop sequences. Each string will be tokenized."""
        self._stop_sequences_raw = value or []
        self._stop_sequences_tokens = None  # Clear cache, re-tokenize on next use

    def _get_stop_sequence_tokens(self) -> list[list[int]]:
        """Get tokenized stop sequences (lazy tokenization)."""
        if self._stop_sequences_tokens is None:
            self._stop_sequences_tokens = []
            for seq in self._stop_sequences_raw:
                # Tokenize without special tokens to get clean token sequence
                tokens = list(self.encode(seq))
                if tokens:  # Only add non-empty sequences
                    self._stop_sequences_tokens.append(tokens)
        return self._stop_sequences_tokens

    # -------------------------------------------------------------------------
    # Primary API
    # -------------------------------------------------------------------------

    def send(self, message: str) -> Generator:
        """
        Send a message and stream the response.

        This is the primary method for chat interactions. Each call:
        1. Adds your message to conversation history
        2. Returns a Generator for streaming the response
        3. Saves the assistant's response to history when collected

        Args:
            message: The user's message.

        Returns:
            A Generator that yields text chunks. Iterate for streaming,
            or call `.collect()` to get the complete result.

        Example:
            >>> session = ChatSession("Qwen/Qwen3-0.6B")
            >>> session.system("You are helpful.")

            >>> # Stream the response
            >>> for chunk in session.send("What is Python?"):
            ...     print(chunk, end="", flush=True)
            >>> print()

            >>> # Follow-up (history is maintained)
            >>> for chunk in session.send("Tell me more"):
            ...     print(chunk, end="")

            >>> # Get full result with metadata
            >>> result = session.send("What else?").collect()
            >>> print(result.text)
            >>> print(f"{result.tokens_per_second:.1f} tok/s")
        """
        logger.debug("send() called: %d chars, history=%d", len(message), len(self._chat_history))

        # Add user message to history
        self._chat_history.append({"role": "user", "content": message})

        # Build messages for template
        messages = []
        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})
        messages.extend(self._chat_history)
        formatted_prompt = self.apply_chat_template(messages)

        logger.debug("Formatted prompt: %d chars", len(formatted_prompt))

        # Create generator that will save response to history when collected
        return _HistoryTrackingGenerator(
            session=self,
            prompt=formatted_prompt,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            top_k=self._top_k,
            top_p=self._top_p,
            strategy=self._strategy,
            text_mode=self._text_mode,
            chunk_interval_ms=self._chunk_interval_ms,
            stop_sequences=self._get_stop_sequence_tokens(),
            history=self._chat_history,
        )

    def system(self, message: str) -> None:
        """
        Set the system prompt.

        The system prompt defines the assistant's behavior and persona.
        It's included at the start of every conversation.

        Args:
            message: The system prompt text.

        Example:
            >>> session = ChatSession("Qwen/Qwen3-0.6B")
            >>> session.system("You are a helpful coding assistant.")
            >>> session.system("Always be concise.")  # Replaces previous
        """
        logger.debug("system() set: %d chars", len(message))
        self._system_prompt = message

    def __call__(self, message: str) -> Generator:
        """
        Shorthand for send().

        Example:
            >>> session = ChatSession("Qwen/Qwen3-0.6B")

            >>> # Streaming
            >>> for chunk in session("Tell me a story"):
            ...     print(chunk, end="")

            >>> # Or collect
            >>> result = session("What is 2+2?").collect()
            >>> print(result.text)
        """
        return self.send(message)

    def new_chat(self) -> None:
        """
        Start a new conversation.

        Clears the conversation history but keeps the system prompt
        and all generation parameters.

        Example:
            >>> session.system("You are helpful.")
            >>> session.send("What is Python?").collect()
            >>> session.new_chat()  # Clear history, keep system prompt
            >>> session.send("What is Java?").collect()  # Fresh conversation
        """
        logger.debug("new_chat() clearing %d messages", len(self._chat_history))
        self._chat_history = []

    def reset(self) -> None:
        """
        Reset the session completely.

        Clears the conversation history AND the system prompt.
        Generation parameters are preserved.

        Example:
            >>> session.system("You are a pirate.")
            >>> session.send("Hello!").collect()
            >>> session.reset()  # Clear everything
            >>> session.send("Hello!").collect()  # No longer a pirate
        """
        logger.debug("reset() clearing history and system prompt")
        self._chat_history = []
        self._system_prompt = None

    @property
    def history(self) -> list[dict]:
        """
        The current conversation history.

        Returns a copy of the history (modifications won't affect the session).

        Returns:
            List of message dicts with 'role' and 'content' keys.

        Example:
            >>> for msg in session.history:
            ...     print(f"{msg['role']}: {msg['content'][:50]}...")
        """
        return self._chat_history.copy()

    def __enter__(self):
        """Support for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        self._free_handle()
        return False

    def __repr__(self) -> str:
        return f"ChatSession({self._model_dir!r})"


class _HistoryTrackingGenerator(Generator):
    """
    Generator that saves the response to history when collected.

    This ensures that even when streaming, the complete response
    is added to the conversation history.
    """

    def __init__(
        self,
        session,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_k: int,
        top_p: float,
        strategy: int,
        text_mode: bool,
        chunk_interval_ms: int,
        stop_sequences: list[list[int]],
        history: list[dict],
    ):
        super().__init__(
            session=session,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            strategy=strategy,
            text_mode=text_mode,
            chunk_size=None,
            chunk_interval_ms=chunk_interval_ms,
            stop_sequences=stop_sequences,
        )
        self._history = history
        self._collected_text = []

    def __next__(self) -> str:
        """Get next chunk and track for history."""
        chunk = super().__next__()
        self._collected_text.append(chunk)
        return chunk

    def collect(self):
        """Collect all chunks and save to history."""
        result = super().collect()
        # Save complete response to history
        self._history.append({"role": "assistant", "content": result.text})
        return result
