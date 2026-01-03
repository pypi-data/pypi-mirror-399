"""
Single source of truth for public subpackages.

This module defines which subpackages are part of the public API.
Used by:
- docs/_build/docgen.py for documentation generation
- tests/linter/test_exports.py for export validation

To add a new public subpackage:
1. Add it to PUBLIC_SUBPACKAGES below
2. Ensure it has __all__ defined
3. Run `make lint` to validate
4. Run `make docs` to generate documentation
"""

# Subpackages that are part of the public API
# Each must have __all__ defined with public classes
PUBLIC_SUBPACKAGES = [
    "tokamino.tokenizer",
    "tokamino.chat_session",
    "tokamino.template",
    "tokamino.converter",
    "tokamino.storage",
    "tokamino.model",
]


def get_public_subpackages() -> list[str]:
    """Get list of public subpackage names."""
    return PUBLIC_SUBPACKAGES.copy()
