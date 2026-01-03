"""Basic prompt template."""

import tokamino

# Create a reusable prompt template
template = tokamino.Template("""
Summarize the following {{document_type}} in 2-3 sentences:

{{content}}
""")

# Use with different inputs
email_prompt = template(
    document_type="email", content="Hi team, just wanted to follow up on the Q3 planning meeting..."
)

article_prompt = template(
    document_type="article", content="Scientists have discovered a new species of deep-sea fish..."
)

print("Email prompt:")
print(email_prompt)
