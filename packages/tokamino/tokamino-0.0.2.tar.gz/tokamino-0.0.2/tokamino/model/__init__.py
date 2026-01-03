"""
Model module for model inspection and architecture information.

Provides:
- describe: Get model architecture information
- ModelInfo: Model configuration data class
"""

from .describe import ModelInfo, describe

__all__ = [
    "describe",
    "ModelInfo",
]
