"""
Tokamino exceptions.

This module defines the exception hierarchy for tokamino:

    TokaminoError (base)
    ├── GenerationError - Errors during text generation
    │   └── EmptyPromptError - Empty prompt with no BOS token
    ├── ModelError - Errors loading or using models
    │   └── ModelNotFoundError - Model path doesn't exist
    ├── TokenizerError - Errors during tokenization
    └── ConvertError - Errors during model conversion

Usage:
    try:
        session.send("").collect()
    except tokamino.EmptyPromptError:
        print("Prompt cannot be empty for this model")
    except tokamino.GenerationError as e:
        print(f"Generation failed: {e}")
"""


class TokaminoError(Exception):
    """Base exception for all tokamino errors."""

    pass


# =============================================================================
# Generation Errors
# =============================================================================


class GenerationError(TokaminoError, RuntimeError):
    """Error during text generation."""

    pass


class EmptyPromptError(GenerationError, ValueError):
    """
    Empty prompt provided to a model without a BOS token.

    Some models (like Qwen) don't have a beginning-of-sequence (BOS) token,
    so they require at least one token in the prompt to start generation.

    Solutions:
    - Provide a non-empty prompt
    - Use chat=True to apply the chat template (adds tokens)
    - Use a model with a BOS token
    """

    def __init__(self, message: str = None):
        if message is None:
            message = (
                "Empty prompt provided but model has no BOS token. "
                "Provide a non-empty prompt or use chat=True."
            )
        super().__init__(message)


# =============================================================================
# Model Errors
# =============================================================================


class ModelError(TokaminoError, RuntimeError):
    """Error loading or using a model."""

    pass


class ModelNotFoundError(ModelError, FileNotFoundError):
    """Model path does not exist or is invalid."""

    pass


# =============================================================================
# Tokenizer Errors
# =============================================================================


class TokenizerError(TokaminoError, RuntimeError):
    """Error during tokenization."""

    pass
