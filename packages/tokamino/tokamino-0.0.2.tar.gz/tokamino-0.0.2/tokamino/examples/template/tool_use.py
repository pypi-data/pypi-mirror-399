"""Tool/function calling prompt template."""

from pathlib import Path

import tokamino

# Load template from file
template = tokamino.Template.from_file(str(Path(__file__).parent / "etc" / "tool_use.j2"))

tools = [
    {"name": "search", "description": "Search the web for information", "parameters": ["query"]},
    {
        "name": "calculate",
        "description": "Perform mathematical calculations",
        "parameters": ["expression"],
    },
    {
        "name": "weather",
        "description": "Get current weather for a location",
        "parameters": ["city", "country"],
    },
]

prompt = template(tools=tools, user_request="What's the weather in Tokyo?")

print(prompt)
