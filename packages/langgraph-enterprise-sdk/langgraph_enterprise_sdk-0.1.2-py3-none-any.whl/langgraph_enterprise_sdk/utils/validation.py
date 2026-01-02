from typing import Any, Iterable


class ValidationException(ValueError):
    """
    Raised when validation fails.
    """
    pass


def require_non_empty(value: Any, name: str) -> None:
    """
    Validate that a value is not empty.
    """
    if value is None:
        raise ValidationException(f"{name} must not be None")

    if isinstance(value, (str, list, dict, tuple, set)) and not value:
        raise ValidationException(f"{name} must not be empty")


def require_one_of(value: Any, allowed: Iterable[Any], name: str) -> None:
    """
    Validate that a value is one of allowed options.
    """
    if value not in allowed:
        raise ValidationException(
            f"{name} must be one of {list(allowed)}, got '{value}'"
        )


def require_type(value: Any, expected_type: type, name: str) -> None:
    """
    Validate value type.
    """
    if not isinstance(value, expected_type):
        raise ValidationException(
            f"{name} must be of type {expected_type.__name__}"
        )
