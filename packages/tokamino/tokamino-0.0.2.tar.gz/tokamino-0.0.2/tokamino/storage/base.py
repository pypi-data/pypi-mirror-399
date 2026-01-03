"""
Abstract base class for storage backends.

Defines the interface that all storage backends must implement.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator


class Storage(ABC):
    """
    Abstract base class for model storage backends.

    Storage backends manage model files - finding, downloading, and organizing
    models from various sources. This base class defines the common interface
    that all storage backends implement.

    Subclasses
    ----------
    LocalStorage
        Local filesystem storage using HuggingFace cache format.

    Future backends may include S3Storage, GCSStorage, etc.

    Examples
    --------
    All storage backends share the same interface:

    >>> storage = LocalStorage()  # or S3Storage(), etc.
    >>> storage.exists("Qwen/Qwen3-0.6B")
    True
    >>> storage.get("Qwen/Qwen3-0.6B")
    '/path/to/model'
    >>> list(storage.list())
    ['Qwen/Qwen3-0.6B', 'meta-llama/Llama-3.2-1B']
    """

    @property
    @abstractmethod
    def base_path(self) -> str:
        """
        Get the base path for this storage backend.

        Returns
        -------
        str
            The root path where models are stored.
        """
        ...

    @abstractmethod
    def resolve(self, model: str) -> str | None:
        """
        Resolve a model path or ID to a local directory.

        May download the model if not available locally.

        Parameters
        ----------
        model : str
            Model path or identifier.

        Returns
        -------
        str or None
            Absolute path to model directory, or None if resolution failed.
        """
        ...

    @abstractmethod
    def get(self, model_id: str) -> str | None:
        """
        Get the local path for a cached model.

        Unlike resolve(), this does NOT download missing models.

        Parameters
        ----------
        model_id : str
            Model identifier.

        Returns
        -------
        str or None
            Path to cached model directory, or None if not cached.
        """
        ...

    @abstractmethod
    def exists(self, model_id: str) -> bool:
        """
        Check if a model is available in this storage backend.

        Parameters
        ----------
        model_id : str
            Model identifier.

        Returns
        -------
        bool
            True if model is available.
        """
        ...

    @abstractmethod
    def list(self) -> Iterator[str]:
        """
        List all available models in this storage backend.

        Yields
        ------
        str
            Model identifiers.
        """
        ...

    @abstractmethod
    def size(self, model_id: str | None = None) -> int:
        """
        Get size of stored models in bytes.

        Parameters
        ----------
        model_id : str, optional
            Specific model to check. If None, returns total size.

        Returns
        -------
        int
            Size in bytes.
        """
        ...

    @abstractmethod
    def download(
        self,
        model_id: str,
        *,
        force: bool = False,
        on_progress: Callable[[int, int, str], None] | None = None,
        token: str | None = None,
    ) -> str | None:
        """
        Download a model to this storage backend.

        Parameters
        ----------
        model_id : str
            Model identifier.
        force : bool, optional
            Force re-download even if cached. Default False.
        on_progress : callable, optional
            Progress callback: fn(downloaded_bytes, total_bytes, filename).
        token : str, optional
            Authentication token if needed.

        Returns
        -------
        str or None
            Path to downloaded model, or None on error.
        """
        ...
