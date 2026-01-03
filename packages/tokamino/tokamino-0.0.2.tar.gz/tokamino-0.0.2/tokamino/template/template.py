"""
Template implementation.

Provides the Template class for Jinja2-compatible prompt templating.
"""

import ctypes
import json
from pathlib import Path
from typing import Any

from .._lib import get_lib


class TemplateSyntaxError(Exception):
    """Raised when template has invalid syntax."""

    pass


class UndefinedError(Exception):
    """Raised when template uses undefined variable."""

    pass


def _setup_template_signatures():
    """Set up C function signatures for template functions."""
    lib = get_lib()

    # Check if template_render exists
    if not hasattr(lib, "tokamino_template_render"):
        return False

    lib.tokamino_template_render.argtypes = [
        ctypes.c_char_p,  # template string
        ctypes.c_char_p,  # json variables
    ]
    lib.tokamino_template_render.restype = ctypes.c_void_p

    lib.tokamino_template_error.argtypes = []
    lib.tokamino_template_error.restype = ctypes.c_char_p

    return True


# Check if C API is available
_HAS_TEMPLATE_API = False
try:
    _HAS_TEMPLATE_API = _setup_template_signatures()
except Exception:
    pass


class Template:
    """
    Prompt template with Jinja2 syntax.

    A Template compiles once and can be rendered many times with different
    variables. Supports the full Jinja2 syntax including control flow,
    filters, and functions.

    Example:
        >>> from tokamino import Template

        # Create template
        >>> t = Template("Hello {{ name }}!")

        # Render with variables (three equivalent ways)
        >>> t(name="World")           # Callable (recommended)
        'Hello World!'
        >>> t.format(name="World")    # Like str.format()
        'Hello World!'
        >>> t.render(name="World")    # Like Jinja2
        'Hello World!'

        # RAG example
        >>> rag = Template('''
        ... Context:
        ... {% for doc in docs %}
        ... - {{ doc.content }}
        ... {% endfor %}
        ...
        ... Question: {{ question }}
        ... ''')
        >>> rag(docs=[{"content": "Paris is in France."}],
        ...      question="Where is Paris?")

    Supported Jinja2 features:
        - Variables: {{ name }}
        - Control flow: {% if %}, {% for %}, {% set %}, {% macro %}
        - Filters: | upper, | lower, | join, | default, etc.
        - Operators: +, -, *, /, in, not in, is, and, or
        - Functions: range(), dict(), namespace()

    Args:
        source: The template string with Jinja2 syntax.

    Raises
    ------
        TemplateSyntaxError: If the template has invalid syntax.
    """

    def __init__(self, source: str):
        """
        Create a new template.

        Args:
            source: Template string with Jinja2 syntax.

        Raises
        ------
            TemplateSyntaxError: If template syntax is invalid.
        """
        if not isinstance(source, str):
            raise TypeError(f"Template source must be str, got {type(source).__name__}")

        self._source = source
        self._validate_syntax()

    @classmethod
    def from_file(cls, path: str) -> "Template":
        """
        Load a template from a file.

        Args:
            path: Path to the template file.

        Returns
        -------
            A new Template instance.

        Raises
        ------
            FileNotFoundError: If the file doesn't exist.
            TemplateSyntaxError: If template syntax is invalid.

        Example:
            >>> template = Template.from_file("prompts/rag.j2")
            >>> result = template(documents=docs, question="...")
        """
        template_path = Path(path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        return cls(template_path.read_text())

    def _validate_syntax(self) -> None:
        """Validate template syntax on construction."""
        # Basic Python-side validation for quick errors
        # Check for unclosed tags (simple heuristic)
        if "{{" in self._source and "}}" not in self._source:
            raise TemplateSyntaxError("Syntax error: unclosed variable tag, expected }}")
        if "{%" in self._source and "%}" not in self._source:
            raise TemplateSyntaxError("Syntax error: unclosed block tag, expected %}")

        # Count opening/closing tags
        opens = self._source.count("{{") + self._source.count("{%")
        closes = self._source.count("}}") + self._source.count("%}")

        if opens != closes:
            raise TemplateSyntaxError(
                f"Syntax error: unclosed tag, {opens} opening vs {closes} closing"
            )

        # Validate via Zig compiler if API is available
        if _HAS_TEMPLATE_API:
            self._compile_check()

    def _compile_check(self) -> None:
        """Validate syntax by doing a test parse with empty context."""
        lib = get_lib()

        # Try to render with empty vars - syntax errors will surface
        result_ptr = lib.tokamino_template_render(
            self._source.encode("utf-8"),
            b"{}",  # Empty JSON object
        )

        if result_ptr is None:
            error_ptr = lib.tokamino_template_error()
            if error_ptr:
                error_msg = ctypes.cast(error_ptr, ctypes.c_char_p).value.decode("utf-8")
                # Only raise for parse/lex errors, not eval errors (undefined vars)
                if "ParseError" in error_msg or "LexError" in error_msg:
                    raise TemplateSyntaxError(f"Syntax error: {error_msg}")
                # Eval errors are OK at compile time - they happen due to undefined vars
        else:
            # Clean up the result
            lib.tokamino_text_free(result_ptr)

    def __call__(self, **variables: Any) -> str:
        """
        Render the template with the given variables.

        This is the recommended way to use templates - just call them
        like a function.

        Args:
            **variables: Variables to substitute in the template.

        Returns
        -------
            The rendered template string.

        Raises
        ------
            UndefinedError: If a required variable is not provided.

        Example:
            >>> t = Template("Hello {{ name }}!")
            >>> t(name="World")
            'Hello World!'
        """
        return self._render(variables)

    def format(self, **variables: Any) -> str:
        """
        Render the template with the given variables.

        Familiar API for Python developers used to str.format().

        Args:
            **variables: Variables to substitute in the template.

        Returns
        -------
            The rendered template string.

        Example:
            >>> t = Template("Hello {{ name }}!")
            >>> t.format(name="World")
            'Hello World!'
        """
        return self._render(variables)

    def render(self, **variables: Any) -> str:
        """
        Render the template with the given variables.

        Familiar API for Jinja2 users.

        Args:
            **variables: Variables to substitute in the template.

        Returns
        -------
            The rendered template string.

        Example:
            >>> t = Template("Hello {{ name }}!")
            >>> t.render(name="World")
            'Hello World!'
        """
        return self._render(variables)

    def _render(self, variables: dict[str, Any]) -> str:
        """Render the template with the given variables dictionary."""
        if not _HAS_TEMPLATE_API:
            raise NotImplementedError(
                "Template rendering requires C API extension.\n\n"
                "The Zig template engine exists but is not yet exposed via C API.\n"
                "Required: Add tokamino_template_render() to core/src/capi/generate.zig\n\n"
                "See tests/template/TODO_TEMPLATE.md for implementation details."
            )

        lib = get_lib()

        # Convert variables to JSON
        json_vars = json.dumps(variables)

        # Call C API
        result_ptr = lib.tokamino_template_render(
            self._source.encode("utf-8"),
            json_vars.encode("utf-8"),
        )

        if result_ptr is None:
            # Get error message
            error_ptr = lib.tokamino_template_error()
            if error_ptr:
                error_msg = ctypes.cast(error_ptr, ctypes.c_char_p).value.decode("utf-8")
                # Classify error type based on message
                error_lower = error_msg.lower()
                if "undefined" in error_lower or "undefinedvariable" in error_lower:
                    raise UndefinedError(error_msg)
                if "parse" in error_lower or "lex" in error_lower or "syntax" in error_lower:
                    raise TemplateSyntaxError(error_msg)
                # Default to syntax error for template issues
                raise TemplateSyntaxError(error_msg)
            raise TemplateSyntaxError("Template rendering failed")

        # Extract string and free
        text = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode("utf-8")
        lib.tokamino_text_free(result_ptr)

        return text

    @property
    def source(self) -> str:
        """The original template source string."""
        return self._source

    def __repr__(self) -> str:
        preview = self._source[:50]
        if len(self._source) > 50:
            preview += "..."
        return f"Template({preview!r})"

    def __str__(self) -> str:
        return self._source
