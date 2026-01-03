"""
Storage backends for model management.

The storage module provides a unified interface for resolving and managing
model paths. Currently supports local filesystem storage (including HuggingFace
cache), with S3 and other backends planned for the future.

Classes
-------
Storage
    Abstract base class defining the storage interface.
LocalStorage
    Local filesystem storage using HuggingFace cache format.

Example
-------
>>> from tokamino.storage import LocalStorage
>>> storage = LocalStorage()
>>> storage.exists("Qwen/Qwen3-0.6B")
True
>>> storage.get("Qwen/Qwen3-0.6B")
'/home/user/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/main'
>>> list(storage.list())
['Qwen/Qwen3-0.6B', 'meta-llama/Llama-3.2-1B']
"""

from tokamino.storage.base import Storage
from tokamino.storage.local import LocalStorage

__all__ = ["Storage", "LocalStorage"]
