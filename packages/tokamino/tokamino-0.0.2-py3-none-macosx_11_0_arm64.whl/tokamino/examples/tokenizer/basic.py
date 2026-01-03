"""Basic tokenization."""

import tokamino

tokenizer = tokamino.Tokenizer("Qwen/Qwen3-0.6B")

# Encode text to tokens
tokens = tokenizer.encode("Hello, world!")
print(f"Tokens: {tokens}")

# Decode tokens back to text
text = tokenizer.decode(tokens)
print(f"Text: {text}")
