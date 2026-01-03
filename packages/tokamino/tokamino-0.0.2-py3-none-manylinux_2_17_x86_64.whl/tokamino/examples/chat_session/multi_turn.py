"""Multi-turn conversation with memory."""

import tokamino

session = tokamino.ChatSession("Qwen/Qwen3-0.6B")

# Set a system message
session.send("You are a math tutor.", role="system")

# First turn
session.send("What is 2+2?")
print("User: What is 2+2?")
print(f"Assistant: {session.last_response}")

# Second turn - the model remembers the context
session.send("And what is that times 3?")
print("\nUser: And what is that times 3?")
print(f"Assistant: {session.last_response}")

# Start fresh
session.new_chat()
print("\n--- New chat started ---")
