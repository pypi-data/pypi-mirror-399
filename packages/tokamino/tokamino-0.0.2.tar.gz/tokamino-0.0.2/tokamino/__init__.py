"""
Tokamino - Fast LLM inference in pure Python.

Tokamino runs large language models locally with a simple Python API.
No PyTorch, no dependencies beyond the standard library.

Quick Start
-----------

Generate text in one line:

    >>> import tokamino
    >>> tokamino.generate("Qwen/Qwen3-0.6B", "What is 2+2?")
    '2+2 equals 4.'

Stream responses in real-time:

    >>> for chunk in tokamino.stream("Qwen/Qwen3-0.6B", "Tell me a joke"):
    ...     print(chunk, end="", flush=True)

Count tokens (useful for context limits):

    >>> len(tokamino.encode("Qwen/Qwen3-0.6B", "Hello world"))
    2


Core Classes
------------

The four main classes for different tasks:

- `ChatSession` - Stateful chat with an LLM (load once, chat many times)
- `Tokenizer` - Tokenize text without loading model weights
- `Template` - Prompt templates with Jinja2 syntax
- `Converter` - Convert HuggingFace models to optimized formats


When to Use What
----------------

**Use the functions** (`generate`, `stream`, `encode`, `decode`) when:
- You want the simplest possible code
- You're doing one-off operations
- You don't need fine-grained control

**Use `ChatSession`** when:
- You're generating multiple responses (avoids reloading the model)
- You need multi-turn chat with conversation history
- You want full control over sampling parameters

**Use `Tokenizer`** when:
- You only need tokenization, not generation
- You want the fastest possible loading (doesn't load model weights)
- You're counting tokens or preprocessing text


Examples
--------
Multi-turn chat with history:

    >>> session = tokamino.ChatSession("Qwen/Qwen3-0.6B")
    >>> session.system("You are a math tutor.")
    >>> session.send("What is 2+2?").collect().text
    '2+2 equals 4.'
    >>> session.send("And 3+3?").collect().text
    '3+3 equals 6.'

Streaming with a ChatSession:

    >>> session = tokamino.ChatSession("Qwen/Qwen3-0.6B")
    >>> for chunk in session.send("Tell me a story"):
    ...     print(chunk, end="", flush=True)

Convert a model to 4-bit quantized format:

    >>> converter = tokamino.Converter()
    >>> path = converter("Qwen/Qwen3-0.6B", bits=4)
    >>> session = tokamino.ChatSession(path)

Prompt templates with variables:

    >>> template = tokamino.Template('''
    ... Answer the question based on the context.
    ...
    ... Context: {{ context }}
    ...
    ... Question: {{ question }}
    ... ''')
    >>> prompt = template(context="Paris is in France.", question="Where is Paris?")


Supported Models
----------------

tokamino supports many popular model architectures:

- Qwen2, Qwen2.5, Qwen3
- LLaMA 2, LLaMA 3, LLaMA 3.2
- Mistral, Ministral
- Gemma 2, Gemma 3
- Phi-3, Phi-4
- And more (see documentation)

Models can be specified as:
- HuggingFace IDs: "Qwen/Qwen3-0.6B" (downloaded automatically)
- Local paths: "./models/my-model"
"""

# Top-level convenience functions
from tokamino._api import (
    clear_cache,
    decode,
    encode,
    generate,
    stream,
)

# Logging
from tokamino._logging import setup_logging

# Primary classes
from tokamino.chat_session import ChatSession
from tokamino.converter import Converter, convert
from tokamino.model import describe
from tokamino.storage import Storage
from tokamino.template import Template
from tokamino.tokenizer import Tokenizer

__version__ = "0.0.1"

__all__ = [
    # Top-level functions
    "generate",
    "stream",
    "encode",
    "decode",
    "clear_cache",
    "convert",
    "describe",
    "setup_logging",
    # Primary classes
    "ChatSession",
    "Tokenizer",
    "Template",
    "Converter",
    "Storage",
]
