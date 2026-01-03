"""Track download progress during conversion."""

import tokamino


def on_progress(current, total):
    """Track progress during model download."""
    percent = (current / total) * 100 if total > 0 else 0
    print(f"\rDownloading: {percent:.1f}%", end="", flush=True)


converter = tokamino.Converter()

# Convert with progress callback
model_path = converter("Qwen/Qwen3-0.6B", on_download=on_progress)
print(f"\nModel ready: {model_path}")
