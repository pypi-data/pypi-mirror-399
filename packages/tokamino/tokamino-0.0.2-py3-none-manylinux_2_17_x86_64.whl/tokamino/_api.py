"""
Top-level convenience functions for common operations.

These functions provide the simplest possible API for tokamino.
For more control, use the ChatSession and Tokenizer classes directly.

Thread Safety
-------------
These functions are thread-safe. Each thread gets its own cached model
instances via thread-local storage, so concurrent calls from different
threads won't interfere with each other.
"""

import logging
import threading
from collections.abc import Iterator

logger = logging.getLogger(__name__)

# Thread-local storage for per-thread model caching
_thread_local = threading.local()


def _get_client(model: str):
    """Get or create a cached Client for the current thread."""
    from .generate import Client

    if not hasattr(_thread_local, "clients"):
        _thread_local.clients = {}
    if model not in _thread_local.clients:
        logger.debug("Creating new Client for model: %s", model)
        _thread_local.clients[model] = Client(model)
    return _thread_local.clients[model]


def _get_tokenizer(model: str):
    """Get or create a cached Tokenizer for the current thread."""
    from .tokenizer import Tokenizer

    if not hasattr(_thread_local, "tokenizers"):
        _thread_local.tokenizers = {}
    if model not in _thread_local.tokenizers:
        logger.debug("Creating new Tokenizer for model: %s", model)
        _thread_local.tokenizers[model] = Tokenizer(model)
    return _thread_local.tokenizers[model]


def generate(
    model: str,
    prompt: str,
    *,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_k: int = 50,
    top_p: float = 0.9,
    system: str = "",
) -> str:
    """
    Generate text from a prompt.

    This is the simplest way to generate text with tokamino. It loads the model,
    applies the chat template, generates a response, and returns the text.

    For repeated generations with the same model, use `Client` directly to avoid
    reloading the model each time.

    Args:
        model: Model path or HuggingFace ID (e.g., "Qwen/Qwen3-0.6B").
            Local paths and HuggingFace model IDs are both supported.
            HuggingFace models are downloaded automatically on first use.

        prompt: The user's message or question.

        max_tokens: Maximum number of tokens to generate. Default is 256.
            One token is roughly 4 characters or 0.75 words in English.
            Set higher for longer responses, lower for quick answers.

        temperature: Controls randomness in generation. Default is 0.7.
            - 0.0: Deterministic (always picks most likely token)
            - 0.1-0.5: Focused and consistent
            - 0.7-1.0: Balanced creativity (recommended)
            - 1.0-2.0: More creative and varied
            Higher values produce more diverse but potentially less coherent text.

        top_k: Limits token selection to the k most likely tokens. Default is 50.
            Lower values (10-20) make output more focused.
            Higher values (50-100) allow more variety.
            Set to 0 to disable top-k filtering.

        top_p: Nucleus sampling threshold. Default is 0.9.
            Selects from the smallest set of tokens whose cumulative probability
            exceeds this threshold. 0.9 means "top 90% probability mass".
            Lower values (0.5-0.7) = more focused.
            Higher values (0.9-0.95) = more variety.

        system: Optional system prompt to set the assistant's behavior.
            Example: "You are a helpful coding assistant."

    Returns
    -------
        The generated text response.

    Raises
    ------
        RuntimeError: If the model cannot be loaded or generation fails.

    Example:
        >>> import tokamino
        >>> response = tokamino.generate("Qwen/Qwen3-0.6B", "What is 2+2?")
        >>> print(response)
        2+2 equals 4.

        >>> # With custom parameters
        >>> response = tokamino.generate(
        ...     "Qwen/Qwen3-0.6B",
        ...     "Write a haiku about coding",
        ...     max_tokens=50,
        ...     temperature=1.2,  # More creative
        ...     system="You are a poet.",
        ... )

    See Also
    --------
        - `stream()`: For real-time streaming output
        - `ChatSession`: For stateful chat with conversation history
    """
    client = _get_client(model)
    return client(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        system_prompt=system,
    )


def stream(
    model: str,
    prompt: str,
    *,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_k: int = 50,
    top_p: float = 0.9,
    system: str = "",
) -> Iterator[str]:
    r"""Stream generated text in real-time.

    Like `generate()`, but yields text chunks as they're produced instead of
    waiting for the complete response. This is ideal for chat interfaces where
    you want to show text appearing word-by-word.

    Args:
        model: Model path or HuggingFace ID (e.g., "Qwen/Qwen3-0.6B").

        prompt: The user's message or question.

        max_tokens: Maximum number of tokens to generate. Default is 256.

        temperature: Controls randomness (0.0-2.0). Default is 0.7.
            See `generate()` for detailed explanation.

        top_k: Top-k sampling parameter. Default is 50.

        top_p: Nucleus sampling threshold. Default is 0.9.

        system: Optional system prompt.

    Yields
    ------
        Text chunks as they are generated. Chunks are yielded roughly every
        100ms for smooth display.

    Raises
    ------
        RuntimeError: If the model cannot be loaded or generation fails.

    Example:
        >>> import tokamino
        >>> for chunk in tokamino.stream("Qwen/Qwen3-0.6B", "Tell me a joke"):
        ...     print(chunk, end="", flush=True)
        ... print()  # Final newline

        >>> # In a web application (e.g., FastAPI)
        >>> async def chat_endpoint(prompt: str):
        ...     def generate():
        ...         for chunk in tokamino.stream("model", prompt):
        ...             yield f"data: {chunk}\n\n"
        ...     return StreamingResponse(generate())

    See Also
    --------
        - `generate()`: For getting the complete response at once
        - `ChatSession`: For stateful chat with conversation history
    """
    client = _get_client(model)
    yield from client.generate(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        system_prompt=system,
        text=True,
    )


def encode(
    model: str,
    text: str,
) -> list[int]:
    """
    Convert text to token IDs.

    Tokenization splits text into tokens (subword units) that the model
    understands. This is useful for:
    - Counting tokens before sending to an API with token limits
    - Understanding how the model sees your text
    - Preprocessing for batch operations

    Args:
        model: Model path or HuggingFace ID. The tokenizer is loaded from
            the model's tokenizer.json file.

        text: The text to tokenize.

    Returns
    -------
        List of token IDs (integers). Each ID maps to a token in the
        model's vocabulary.

    Raises
    ------
        RuntimeError: If the model path is invalid or tokenizer fails to load.

    Example:
        >>> import tokamino

        >>> # Count tokens
        >>> tokens = tokamino.encode("Qwen/Qwen3-0.6B", "Hello, world!")
        >>> print(f"Token count: {len(tokens)}")
        Token count: 4

        >>> # See the actual token IDs
        >>> print(tokens)
        [9707, 11, 1879, 0]

        >>> # Check if text fits in context window
        >>> long_text = "..." * 1000
        >>> if len(tokamino.encode("model", long_text)) > 4096:
        ...     print("Text too long!")

    See Also
    --------
        - `decode()`: Convert token IDs back to text
        - `Tokenizer`: For advanced tokenization (vocabulary access, special tokens)
    """
    tokenizer = _get_tokenizer(model)
    return tokenizer.encode(text).tolist()


def decode(
    model: str,
    tokens: list[int],
) -> str:
    """
    Convert token IDs back to text.

    This reverses the tokenization process, reconstructing the original
    text from token IDs.

    Args:
        model: Model path or HuggingFace ID. Must match the model used
            for encoding.

        tokens: List of token IDs to decode.

    Returns
    -------
        The decoded text string.

    Raises
    ------
        RuntimeError: If the model path is invalid or decoding fails.

    Example:
        >>> import tokamino

        >>> # Round-trip: encode then decode
        >>> tokens = tokamino.encode("Qwen/Qwen3-0.6B", "Hello!")
        >>> text = tokamino.decode("Qwen/Qwen3-0.6B", tokens)
        >>> print(text)
        Hello!

        >>> # Decode specific token IDs
        >>> text = tokamino.decode("Qwen/Qwen3-0.6B", [9707, 11, 1879, 0])
        >>> print(text)
        Hello, world!

    See Also
    --------
        - `encode()`: Convert text to token IDs
        - `Tokenizer`: For advanced tokenization
    """
    tokenizer = _get_tokenizer(model)
    return tokenizer.decode(tokens)


def clear_cache() -> None:
    """
    Clear the model cache for the current thread.

    tokamino caches loaded models per-thread to avoid reloading on repeated
    calls to `generate()`, `stream()`, `encode()`, and `decode()`. Call this
    function to free memory when you're done with cached models.

    Note: This only clears the cache for the calling thread. Other threads
    retain their own cached models.

    Example:
        >>> import tokamino
        >>> tokamino.generate("model", "Hello")  # Model loaded and cached
        >>> tokamino.generate("model", "World")  # Uses cached model
        >>> tokamino.clear_cache()  # Free memory for this thread
    """
    if hasattr(_thread_local, "clients"):
        _thread_local.clients.clear()
    if hasattr(_thread_local, "tokenizers"):
        _thread_local.tokenizers.clear()
