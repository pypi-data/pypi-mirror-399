"""Count tokens for context window management."""

import tokamino

tokenizer = tokamino.Tokenizer("Qwen/Qwen3-0.6B")

# Count tokens in a prompt
prompt = "Explain quantum computing in simple terms."
count = tokenizer.count_tokens(prompt)
print(f"Prompt has {count} tokens")

# Check if content fits in context window
max_context = 4096
document = "..." * 1000  # Your document here
doc_tokens = tokenizer.count_tokens(document)

if doc_tokens > max_context:
    print(f"Document too long: {doc_tokens} tokens (max {max_context})")
else:
    print(f"Document fits: {doc_tokens}/{max_context} tokens")
