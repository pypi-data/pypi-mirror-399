"""Streaming responses token by token."""

import tokamino

session = tokamino.ChatSession("Qwen/Qwen3-0.6B")

# Stream tokens as they're generated
for chunk in session.send("Tell me a short joke"):
    print(chunk, end="", flush=True)
print()
