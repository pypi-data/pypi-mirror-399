"""Convert a HuggingFace model for local use."""

import tokamino

converter = tokamino.Converter()

# Convert a model from HuggingFace (downloads and converts)
model_path = converter("Qwen/Qwen3-0.6B")
print(f"Model saved to: {model_path}")

# Now use it
session = tokamino.ChatSession(model_path)
print(session("Hello!"))
