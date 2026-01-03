"""Basic ChatSession usage."""

import tokamino

# Create a chat session with a model
session = tokamino.ChatSession("Qwen/Qwen3-0.6B")

# One-shot: get a complete response
response = session("What is 2+2?")
print(response)
