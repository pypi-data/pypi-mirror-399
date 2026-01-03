"""Hatch build hook for compiling the native Zig library."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class ZigBuildHook(BuildHookInterface):
    """Build hook that compiles the Zig native library before packaging."""

    PLUGIN_NAME = "zig-build"

    def initialize(self, version: str, build_data: dict) -> None:
        """Run the Zig build before packaging."""
        if self.target_name == "sdist":
            # Don't build for sdist - just include source
            return

        root = Path(self.root)
        lib_name = self._get_lib_name()
        target_lib = root / "tokamino" / lib_name
        target_metallib = root / "tokamino" / "mlx.metallib"

        # Check if library already exists (pre-built in CI)
        if target_lib.exists():
            self._log(f"Using existing {lib_name}")
            self._copy_metallib(root, target_metallib)
            return

        # Build from source
        self._log("Building native library from source...")
        self._run_build(root)

        # Copy library to package
        built_lib = root / "zig-out" / "lib" / lib_name
        if not built_lib.exists():
            raise RuntimeError(f"Build failed: {built_lib} not found")

        shutil.copy2(built_lib, target_lib)
        self._log(f"Copied {lib_name} to tokamino/")

        # Copy Metal library on macOS (required for GPU, ~3MB with JIT mode)
        self._copy_metallib(root, target_metallib)

    def _get_lib_name(self) -> str:
        """Get platform-specific library name."""
        system = platform.system()
        if system == "Darwin":
            return "libtokamino.dylib"
        elif system == "Windows":
            return "tokamino.dll"
        else:
            return "libtokamino.so"

    def _run_build(self, root: Path) -> None:
        """Run the build commands."""
        env = os.environ.copy()

        # Check for required tools
        if not shutil.which("zig"):
            raise RuntimeError(
                "Zig compiler not found. Install from https://ziglang.org/download/"
            )
        if not shutil.which("cmake"):
            raise RuntimeError("CMake not found. Install cmake to build from source.")

        # Run make deps
        self._log("Cloning dependencies...")
        subprocess.run(
            ["make", "deps"],
            cwd=root,
            env=env,
            check=True,
        )

        # Run zig build
        self._log("Compiling with Zig...")
        cmd = ["zig", "build", "-Drelease"]

        # Metal GPU acceleration is enabled by default on macOS
        # MLX is built from source in make deps

        subprocess.run(cmd, cwd=root, env=env, check=True)

        # Strip the binary
        lib_path = root / "zig-out" / "lib" / self._get_lib_name()
        if lib_path.exists() and shutil.which("strip"):
            self._log("Stripping binary...")
            subprocess.run(["strip", str(lib_path)], check=False)

    def _copy_metallib(self, root: Path, target: Path) -> None:
        """Copy Metal library on macOS if available."""
        if platform.system() != "Darwin":
            return
        if target.exists():
            return

        # Check possible metallib locations
        metallib_paths = [
            root / "deps" / "mlx-src" / "build" / "mlx" / "backend" / "metal" / "kernels" / "mlx.metallib",
        ]
        for src in metallib_paths:
            if src.exists():
                shutil.copy2(src, target)
                self._log(f"Copied mlx.metallib ({src.stat().st_size // 1024}KB)")
                return

    def _log(self, msg: str) -> None:
        """Log build progress."""
        print(f"[zig-build] {msg}", file=sys.stderr)
