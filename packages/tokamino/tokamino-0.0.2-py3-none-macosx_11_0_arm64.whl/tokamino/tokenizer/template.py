"""
Chat template formatting.

Provides Jinja2-compatible chat template rendering for LLM prompts.
"""

import ctypes
import json

from .._lib import get_lib


def _setup_signatures():
    """Set up C function signatures for template functions."""
    lib = get_lib()

    # New unified API: messages JSON + add_generation_prompt
    lib.tokamino_apply_chat_template.argtypes = [
        ctypes.c_void_p,  # session (can be null)
        ctypes.c_char_p,  # model_dir
        ctypes.c_char_p,  # messages_json
        ctypes.c_int,  # add_generation_prompt
    ]
    lib.tokamino_apply_chat_template.restype = ctypes.c_void_p

    lib.tokamino_text_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_text_free.restype = None


_setup_signatures()


# Type alias for messages
Message = dict[str, str | list | dict]


def apply_chat_template(
    model_path: str,
    messages: list[Message],
    add_generation_prompt: bool = True,
) -> str:
    """
    Apply a model's chat template with a list of messages.

    Supports multi-turn conversations, tool calls, and assistant prefill.

    Args:
        model_path: Path to model directory containing tokenizer_config.json
        messages: List of message dicts with 'role' and 'content' keys.
                  Roles can be: 'system', 'user', 'assistant', 'tool'
        add_generation_prompt: Whether to add the assistant prompt marker at the end

    Returns
    -------
        Formatted prompt string

    Example:
        >>> prompt = apply_chat_template(
        ...     "models/qwen",
        ...     messages=[
        ...         {"role": "system", "content": "You are helpful."},
        ...         {"role": "user", "content": "Hello!"},
        ...         {"role": "assistant", "content": "Hi there!"},
        ...         {"role": "user", "content": "How are you?"},
        ...     ],
        ... )
    """
    lib = get_lib()

    messages_json = json.dumps(messages)

    result_ptr = lib.tokamino_apply_chat_template(
        None,
        model_path.encode("utf-8"),
        messages_json.encode("utf-8"),
        1 if add_generation_prompt else 0,
    )

    if result_ptr:
        text = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")
        lib.tokamino_text_free(result_ptr)
        return text

    # Fallback: return last user message content
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


class ChatTemplate:
    """
    Chat template formatter for a specific model.

    Loads the chat template from the model's tokenizer_config.json
    and provides methods to format prompts.

    Example:
        >>> template = ChatTemplate("models/qwen")

        # Multi-turn conversation
        >>> prompt = template.apply([
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi!"},
        ...     {"role": "user", "content": "How are you?"},
        ... ])
    """

    def __init__(self, model_path: str):
        """
        Initialize chat template for a model.

        Args:
            model_path: Path to model directory
        """
        self._model_path = model_path

    def apply(
        self,
        messages: list[Message],
        add_generation_prompt: bool = True,
    ) -> str:
        """
        Apply the chat template with a list of messages.

        Supports multi-turn conversations, tool calls, and assistant prefill.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            add_generation_prompt: Whether to add assistant prompt at end.

        Returns
        -------
            Formatted prompt string
        """
        return apply_chat_template(self._model_path, messages, add_generation_prompt)

    def __repr__(self) -> str:
        return f"ChatTemplate({self._model_path!r})"
