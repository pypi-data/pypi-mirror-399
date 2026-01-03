"""Few-shot learning with dynamic examples."""

from pathlib import Path

import tokamino

# Load template from file
template = tokamino.Template.from_file(str(Path(__file__).parent / "etc" / "few_shot.j2"))

# Build the prompt with examples
prompt = template(
    examples=[
        {"text": "I love this product!", "sentiment": "positive"},
        {"text": "Worst experience ever.", "sentiment": "negative"},
        {"text": "It arrived on Tuesday.", "sentiment": "neutral"},
    ],
    query="This exceeded my expectations!",
)

print(prompt)
