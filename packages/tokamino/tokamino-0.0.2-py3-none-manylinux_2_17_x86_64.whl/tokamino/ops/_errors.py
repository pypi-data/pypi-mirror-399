"""
Tokamino error handling.

Provides exception classes for ops errors and error code mapping.
"""


class TokaminoError(Exception):
    """Base exception for tokamino errors."""

    pass


class ShapeError(TokaminoError, ValueError):
    """Shape mismatch error."""

    pass


class DtypeError(TokaminoError, TypeError):
    """Unsupported or mismatched dtype."""

    pass


class DeviceError(TokaminoError, RuntimeError):
    """Device mismatch or unavailable."""

    pass


class ArgumentError(TokaminoError, ValueError):
    """Invalid argument error."""

    pass


# Error code to exception mapping
# Must match TokaminoError enum in core/src/capi/ops.zig
_ERROR_MAP = {
    0: None,  # Ok
    1: (ShapeError, "Shape mismatch"),
    2: (DtypeError, "Unsupported dtype"),
    3: (DeviceError, "Device mismatch"),
    4: (MemoryError, "Allocation failed"),
    5: (ArgumentError, "Invalid argument"),
    6: (RuntimeError, "Internal error"),
    7: (DeviceError, "Unsupported device"),
    8: (ArgumentError, "Null pointer"),
}


def check_error(code: int, context: str = "") -> None:
    """Check error code and raise appropriate exception if non-zero."""
    if code == 0:
        return

    error_info = _ERROR_MAP.get(code)
    if error_info is None:
        raise RuntimeError(
            f"Unknown error code {code}: {context}" if context else f"Unknown error code {code}"
        )

    exc_class, msg = error_info
    full_msg = f"{msg}: {context}" if context else msg
    raise exc_class(full_msg)
