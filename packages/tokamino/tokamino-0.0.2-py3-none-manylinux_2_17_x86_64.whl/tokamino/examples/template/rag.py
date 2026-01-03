"""RAG (Retrieval-Augmented Generation) prompt template."""

from pathlib import Path

import tokamino

# Load template from file
template = tokamino.Template.from_file(str(Path(__file__).parent / "etc" / "rag.j2"))

# Simulate retrieved documents
documents = [
    {"source": "FAQ", "content": "Our return policy allows returns within 30 days."},
    {"source": "Terms", "content": "Refunds are processed within 5-7 business days."},
]

prompt = template(documents=documents, question="How long do refunds take?")

print(prompt)
