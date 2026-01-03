"""Chain-of-thought reasoning template."""

from pathlib import Path

import tokamino

# Load template from file
template = tokamino.Template.from_file(str(Path(__file__).parent / "etc" / "chain_of_thought.j2"))

prompt = template(
    problem="A train travels 120 miles in 2 hours. How fast is it going in miles per minute?",
    hints=["First find miles per hour", "Then convert to minutes"],
)

print(prompt)
