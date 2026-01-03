"""
Local filesystem storage backend.

Handles HuggingFace cache format and local model directories.
All operations are implemented in Zig for performance and consistency.
"""

import ctypes
import os
from collections.abc import Callable, Iterator

from tokamino._lib import get_lib
from tokamino.storage.base import Storage

# C callback types for progress reporting
ProgressCallback = ctypes.CFUNCTYPE(None, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_void_p)
FileStartCallback = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_void_p)


class DownloadOptions(ctypes.Structure):
    """Download options structure matching Zig DownloadOptions."""

    _fields_ = [
        ("token", ctypes.c_char_p),
        ("progress_callback", ProgressCallback),
        ("file_start_callback", FileStartCallback),
        ("user_data", ctypes.c_void_p),
        ("force", ctypes.c_bool),
    ]


def _setup_lib():
    """Set up C API function signatures."""
    lib = get_lib()

    # Path resolution (from generate.zig)
    lib.tokamino_resolve_model_path.argtypes = [ctypes.c_char_p]
    lib.tokamino_resolve_model_path.restype = ctypes.c_void_p

    lib.tokamino_text_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_text_free.restype = None

    # Storage API - Cache operations
    lib.tokamino_storage_is_cached.argtypes = [ctypes.c_char_p]
    lib.tokamino_storage_is_cached.restype = ctypes.c_int

    lib.tokamino_storage_get_cached_path.argtypes = [ctypes.c_char_p]
    lib.tokamino_storage_get_cached_path.restype = ctypes.c_void_p

    lib.tokamino_storage_get_hf_home.argtypes = []
    lib.tokamino_storage_get_hf_home.restype = ctypes.c_void_p

    lib.tokamino_storage_get_cache_dir.argtypes = [ctypes.c_char_p]
    lib.tokamino_storage_get_cache_dir.restype = ctypes.c_void_p

    lib.tokamino_storage_list_models.argtypes = []
    lib.tokamino_storage_list_models.restype = ctypes.c_void_p

    lib.tokamino_storage_list_count.argtypes = [ctypes.c_void_p]
    lib.tokamino_storage_list_count.restype = ctypes.c_size_t

    lib.tokamino_storage_list_get_id.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    lib.tokamino_storage_list_get_id.restype = ctypes.c_char_p

    lib.tokamino_storage_list_get_path.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    lib.tokamino_storage_list_get_path.restype = ctypes.c_char_p

    lib.tokamino_storage_list_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_storage_list_free.restype = None

    lib.tokamino_storage_remove.argtypes = [ctypes.c_char_p]
    lib.tokamino_storage_remove.restype = ctypes.c_int

    lib.tokamino_storage_size.argtypes = [ctypes.c_char_p]
    lib.tokamino_storage_size.restype = ctypes.c_uint64

    lib.tokamino_storage_total_size.argtypes = []
    lib.tokamino_storage_total_size.restype = ctypes.c_uint64

    lib.tokamino_storage_is_model_id.argtypes = [ctypes.c_char_p]
    lib.tokamino_storage_is_model_id.restype = ctypes.c_int

    # Storage API - Remote operations
    lib.tokamino_storage_download.argtypes = [ctypes.c_char_p, ctypes.POINTER(DownloadOptions)]
    lib.tokamino_storage_download.restype = ctypes.c_void_p

    lib.tokamino_storage_exists_remote.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.tokamino_storage_exists_remote.restype = ctypes.c_int

    lib.tokamino_storage_list_remote.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.tokamino_storage_list_remote.restype = ctypes.c_void_p

    lib.tokamino_storage_search.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
    lib.tokamino_storage_search.restype = ctypes.c_void_p

    lib.tokamino_storage_string_list_count.argtypes = [ctypes.c_void_p]
    lib.tokamino_storage_string_list_count.restype = ctypes.c_size_t

    lib.tokamino_storage_string_list_get.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    lib.tokamino_storage_string_list_get.restype = ctypes.c_char_p

    lib.tokamino_storage_string_list_free.argtypes = [ctypes.c_void_p]
    lib.tokamino_storage_string_list_free.restype = None

    return lib


class LocalStorage(Storage):
    """
    Local filesystem storage for models.

    Uses the HuggingFace cache directory (~/.cache/huggingface/hub) by default.
    All operations are implemented in Zig for performance and consistency
    with the core runtime.

    Examples
    --------
    >>> storage = LocalStorage()
    >>> storage.exists("Qwen/Qwen3-0.6B")
    True
    >>> storage.get("Qwen/Qwen3-0.6B")
    '/home/user/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/main'
    >>> list(storage.list())
    ['Qwen/Qwen3-0.6B', 'meta-llama/Llama-3.2-1B']

    Remote Operations
    -----------------
    >>> # Search for models on HuggingFace
    >>> list(storage.search("qwen", limit=5))
    ['Qwen/Qwen3-0.6B', 'Qwen/Qwen3-4B', ...]

    >>> # List files in a remote repo
    >>> list(storage.list_remote("Qwen/Qwen3-0.6B"))
    ['config.json', 'model.safetensors', 'tokenizer.json', ...]

    >>> # Download with progress
    >>> def on_progress(downloaded, total, filename):
    ...     print(f"{filename}: {downloaded}/{total}")
    >>> storage.download("Qwen/Qwen3-0.6B", on_progress=on_progress)
    """

    def __init__(self):
        """Initialize local storage with HuggingFace cache."""
        self._lib = _setup_lib()
        self._token = os.environ.get("HF_TOKEN")

    @property
    def base_path(self) -> str:
        """
        Get the HuggingFace cache directory path.

        Returns
        -------
        str
            Path to the HuggingFace hub cache (e.g., ~/.cache/huggingface/hub).
        """
        ptr = self._lib.tokamino_storage_get_hf_home()
        if not ptr:
            raise RuntimeError("Could not determine HuggingFace home directory")
        path = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
        self._lib.tokamino_text_free(ptr)
        return path + "/hub"

    # =========================================================================
    # Local Cache Operations
    # =========================================================================

    def resolve(self, model: str) -> str | None:
        """
        Resolve a model path or ID to a local directory.

        Handles both local paths and HuggingFace model IDs. If the model
        is not cached, it will be downloaded from HuggingFace.

        Parameters
        ----------
        model : str
            Local path or HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").

        Returns
        -------
        str or None
            Absolute path to model directory, or None if resolution failed.
        """
        ptr = self._lib.tokamino_resolve_model_path(model.encode("utf-8"))
        if not ptr:
            return None
        path = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
        self._lib.tokamino_text_free(ptr)
        return path

    def get(self, model_id: str) -> str | None:
        """
        Get the local path for a cached model.

        Unlike resolve(), this does NOT download missing models.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").

        Returns
        -------
        str or None
            Path to cached model directory, or None if not cached.
        """
        ptr = self._lib.tokamino_storage_get_cached_path(model_id.encode("utf-8"))
        if not ptr:
            return None
        path = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
        self._lib.tokamino_text_free(ptr)
        return path

    def cache_dir(self, model_id: str) -> str | None:
        """
        Get the cache directory for a model ID.

        Returns the HF cache directory path (e.g., ~/.cache/huggingface/hub/models--org--name),
        regardless of whether the model is actually cached.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").

        Returns
        -------
        str or None
            Cache directory path, or None on error.
        """
        ptr = self._lib.tokamino_storage_get_cache_dir(model_id.encode("utf-8"))
        if not ptr:
            return None
        path = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
        self._lib.tokamino_text_free(ptr)
        return path

    def exists(self, model_id: str) -> bool:
        """
        Check if a model is cached locally with valid weights.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").

        Returns
        -------
        bool
            True if model is cached with valid weights.
        """
        return self._lib.tokamino_storage_is_cached(model_id.encode("utf-8")) == 1

    def list(self) -> Iterator[str]:
        """
        List all cached models with valid weights.

        Yields
        ------
        str
            Model IDs in "org/name" format.
        """
        list_ptr = self._lib.tokamino_storage_list_models()
        if not list_ptr:
            return

        try:
            count = self._lib.tokamino_storage_list_count(list_ptr)
            for i in range(count):
                model_id = self._lib.tokamino_storage_list_get_id(list_ptr, i)
                if model_id:
                    yield model_id.decode("utf-8")
        finally:
            self._lib.tokamino_storage_list_free(list_ptr)

    def remove(self, model_id: str) -> bool:
        """
        Remove a cached model.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").

        Returns
        -------
        bool
            True if model was removed, False if it wasn't cached or error.
        """
        return self._lib.tokamino_storage_remove(model_id.encode("utf-8")) == 1

    def clear(self) -> int:
        """
        Remove all cached models.

        Returns
        -------
        int
            Number of models removed.
        """
        count = 0
        for model_id in list(self.list()):
            if self.remove(model_id):
                count += 1
        return count

    def size(self, model_id: str | None = None) -> int:
        """
        Get size of cached models in bytes.

        Parameters
        ----------
        model_id : str, optional
            Specific model to check. If None, returns total cache size.

        Returns
        -------
        int
            Size in bytes.
        """
        if model_id:
            return self._lib.tokamino_storage_size(model_id.encode("utf-8"))
        return self._lib.tokamino_storage_total_size()

    # =========================================================================
    # Remote Operations (HuggingFace API)
    # =========================================================================

    def download(
        self,
        model_id: str,
        *,
        force: bool = False,
        on_progress: Callable[[int, int, str], None] | None = None,
        token: str | None = None,
    ) -> str | None:
        """
        Download a model from HuggingFace Hub.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").
        force : bool, optional
            Force re-download even if cached. Default False.
        on_progress : callable, optional
            Progress callback: fn(downloaded_bytes, total_bytes, filename).
        token : str, optional
            HuggingFace API token. Falls back to HF_TOKEN env var.

        Returns
        -------
        str or None
            Path to downloaded model, or None on error.
        """
        # Use provided token or fall back to env var
        tok = token or self._token
        tok_bytes = tok.encode("utf-8") if tok else None

        # Store callbacks to prevent garbage collection
        current_file = [""]

        @ProgressCallback
        def progress_cb(downloaded, total, user_data):
            if on_progress:
                on_progress(downloaded, total, current_file[0])

        @FileStartCallback
        def file_start_cb(filename, user_data):
            if filename:
                current_file[0] = filename.decode("utf-8")

        # Build options struct
        options = DownloadOptions()
        options.token = tok_bytes
        options.force = force
        options.user_data = None

        if on_progress:
            options.progress_callback = progress_cb
            options.file_start_callback = file_start_cb
        else:
            options.progress_callback = ProgressCallback()
            options.file_start_callback = FileStartCallback()

        ptr = self._lib.tokamino_storage_download(model_id.encode("utf-8"), ctypes.byref(options))

        if not ptr:
            return None

        path = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
        self._lib.tokamino_text_free(ptr)
        return path

    def exists_remote(self, model_id: str, token: str | None = None) -> bool:
        """
        Check if a model exists on HuggingFace Hub.

        Makes an API call to HuggingFace.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").
        token : str, optional
            HuggingFace API token for private models.

        Returns
        -------
        bool
            True if model exists on HuggingFace.
        """
        tok = token or self._token
        tok_bytes = tok.encode("utf-8") if tok else None

        return self._lib.tokamino_storage_exists_remote(model_id.encode("utf-8"), tok_bytes) == 1

    def list_remote(self, model_id: str, token: str | None = None) -> Iterator[str]:
        """
        List files in a remote HuggingFace repository.

        Makes an API call to HuggingFace.

        Parameters
        ----------
        model_id : str
            HuggingFace model ID (e.g., "Qwen/Qwen3-0.6B").
        token : str, optional
            HuggingFace API token for private models.

        Yields
        ------
        str
            Filenames in the repository.
        """
        tok = token or self._token
        tok_bytes = tok.encode("utf-8") if tok else None

        list_ptr = self._lib.tokamino_storage_list_remote(model_id.encode("utf-8"), tok_bytes)

        if not list_ptr:
            return

        try:
            count = self._lib.tokamino_storage_string_list_count(list_ptr)
            for i in range(count):
                filename = self._lib.tokamino_storage_string_list_get(list_ptr, i)
                if filename:
                    yield filename.decode("utf-8")
        finally:
            self._lib.tokamino_storage_string_list_free(list_ptr)

    def search(
        self,
        query: str,
        limit: int = 10,
        token: str | None = None,
    ) -> Iterator[str]:
        """
        Search for models on HuggingFace Hub.

        Searches for text-generation models matching the query.

        Parameters
        ----------
        query : str
            Search query (e.g., "qwen", "llama").
        limit : int, optional
            Maximum number of results. Default 10.
        token : str, optional
            HuggingFace API token.

        Yields
        ------
        str
            Model IDs matching the search query.
        """
        tok = token or self._token
        tok_bytes = tok.encode("utf-8") if tok else None

        list_ptr = self._lib.tokamino_storage_search(query.encode("utf-8"), limit, tok_bytes)

        if not list_ptr:
            return

        try:
            count = self._lib.tokamino_storage_string_list_count(list_ptr)
            for i in range(count):
                model_id = self._lib.tokamino_storage_string_list_get(list_ptr, i)
                if model_id:
                    yield model_id.decode("utf-8")
        finally:
            self._lib.tokamino_storage_string_list_free(list_ptr)

    # =========================================================================
    # Utility
    # =========================================================================

    @staticmethod
    def is_model_id(path: str) -> bool:
        """
        Check if a string looks like a HuggingFace model ID.

        Parameters
        ----------
        path : str
            String to check.

        Returns
        -------
        bool
            True if it looks like "org/model" format.
        """
        lib = get_lib()
        lib.tokamino_storage_is_model_id.argtypes = [ctypes.c_char_p]
        lib.tokamino_storage_is_model_id.restype = ctypes.c_int
        return lib.tokamino_storage_is_model_id(path.encode("utf-8")) == 1
