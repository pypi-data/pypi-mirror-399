"""
Prompt template engine for LLM applications.

Provides the Template class for creating reusable prompt templates with
Jinja2 syntax. Templates compile once and render quickly with different
variables.

Common Use Cases
----------------

**Few-shot learning**::

    template = Template('''
    {% for example in examples %}
    Input: {{example.input}}
    Output: {{example.output}}
    {% endfor %}
    Input: {{query}}
    Output:''')

**RAG (Retrieval-Augmented Generation)**::

    template = Template('''
    Context:
    {% for doc in documents %}
    [{{doc.source}}]: {{doc.content}}
    {% endfor %}

    Question: {{question}}
    Answer:''')

**Tool/Function calling**::

    template = Template('''
    Available tools:
    {% for tool in tools %}
    - {{tool.name}}: {{tool.description}}
    {% endfor %}

    Respond with JSON: {"tool": "...", "args": {...}}
    ''')

Quick Start
-----------

Create and use a template::

    from tokamino import Template

    # Create template
    t = Template("Hello {{ name }}!")

    # Render (three equivalent ways)
    t(name="World")           # Callable (recommended)
    t.format(name="World")    # Like str.format()
    t.render(name="World")    # Like Jinja2

See Also
--------
tokamino.ChatSession : Use templates with LLM chat.
"""

from .template import (
    Template,
    TemplateSyntaxError,
    UndefinedError,
)

__all__ = [
    "Template",
    "TemplateSyntaxError",
    "UndefinedError",
]
