"""
Library loading and core ctypes setup.

This module handles loading the tokamino shared library and provides
access to the raw C API for other modules.
"""

import ctypes
import sys
from pathlib import Path


def _find_library_path() -> Path:
    """Find the tokamino shared library."""
    here = Path(__file__).parent

    # 1. Look for bundled file (release mode)
    for ext in [".so", ".dylib", ".dll"]:
        bundled = here / f"libtokamino{ext}"
        if bundled.exists():
            return bundled

    # 2. Look for Zig build output (dev mode)
    project_root = here.parent
    zig_out = project_root / "zig-out" / "lib"

    # Platform specific naming
    if sys.platform == "win32":
        target = zig_out / "tokamino.dll"
    elif sys.platform == "darwin":
        target = zig_out / "libtokamino.dylib"
    else:
        target = zig_out / "libtokamino.so"

    if target.exists():
        return target

    raise FileNotFoundError(
        f"Could not find tokamino library. "
        f"Run 'zig build' from the repository root first. "
        f"Expected: {target}"
    )


# Load library
_lib_path = _find_library_path()
_lib = ctypes.CDLL(str(_lib_path))


def get_lib():
    """Get the library handle."""
    return _lib
