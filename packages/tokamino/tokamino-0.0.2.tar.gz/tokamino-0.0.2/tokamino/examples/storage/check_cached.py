"""Check if a model is cached before loading."""

import tokamino
from tokamino.storage import LocalStorage

storage = LocalStorage()

model_id = "Qwen/Qwen3-0.6B"

if storage.exists(model_id):
    path = storage.get(model_id)
    print(f"{model_id} is cached at: {path}")

    # Load directly from cache (no download)
    session = tokamino.ChatSession(path)
    print(session("Hello!"))
else:
    print(f"{model_id} is not cached.")
    print("Run with resolve() to download:")
    print(f"  path = storage.resolve('{model_id}')")
