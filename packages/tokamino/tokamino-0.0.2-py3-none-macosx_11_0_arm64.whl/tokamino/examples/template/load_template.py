"""Load and use prompt templates from files."""

from pathlib import Path

import tokamino

# Get the directory containing this script
TEMPLATE_DIR = Path(__file__).parent / "etc"


def load_template(name: str) -> tokamino.Template:
    """Load a template from the etc/ directory."""
    path = TEMPLATE_DIR / f"{name}.j2"
    return tokamino.Template.from_file(str(path))


# Load templates
few_shot = load_template("few_shot")
rag = load_template("rag")
tool_use = load_template("tool_use")
chain_of_thought = load_template("chain_of_thought")
summarize = load_template("summarize")
extract = load_template("extract")


if __name__ == "__main__":
    # Example: Few-shot sentiment analysis
    print("=== Few-Shot Template ===")
    prompt = few_shot(
        examples=[
            {"text": "I love this!", "sentiment": "positive"},
            {"text": "This is terrible.", "sentiment": "negative"},
            {"text": "It arrived.", "sentiment": "neutral"},
        ],
        query="Best purchase I ever made!",
    )
    print(prompt)
    print()

    # Example: RAG context
    print("=== RAG Template ===")
    prompt = rag(
        documents=[
            {"source": "FAQ", "content": "Returns accepted within 30 days."},
            {"source": "Policy", "content": "Refunds processed in 5-7 days."},
        ],
        question="How long do refunds take?",
    )
    print(prompt)
    print()

    # Example: Summarization
    print("=== Summarize Template ===")
    prompt = summarize(
        document_type="email",
        content="Hi team, I wanted to follow up on our Q3 planning...",
        num_sentences=2,
    )
    print(prompt)
