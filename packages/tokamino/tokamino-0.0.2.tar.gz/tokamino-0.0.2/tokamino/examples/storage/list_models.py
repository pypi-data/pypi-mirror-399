"""List cached models."""

from tokamino.storage import LocalStorage

storage = LocalStorage()

print("Cached models:")
for model_id in storage.list():
    size_mb = storage.size(model_id) / (1024 * 1024)
    print(f"  {model_id} ({size_mb:.1f} MB)")

total_mb = storage.size() / (1024 * 1024)
print(f"\nTotal cache size: {total_mb:.1f} MB")
