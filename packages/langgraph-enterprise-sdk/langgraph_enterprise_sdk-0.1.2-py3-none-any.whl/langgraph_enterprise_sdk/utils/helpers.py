import uuid
from datetime import datetime
from typing import Any, Dict


def generate_id(prefix: str | None = None) -> str:
    """
    Generate a deterministic-friendly unique ID.
    """
    uid = uuid.uuid4().hex
    return f"{prefix}_{uid}" if prefix else uid


def utc_now() -> datetime:
    """
    Get current UTC timestamp.
    """
    return datetime.utcnow()


def deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries without mutation.

    ZAD:
    - Returns a new dict
    """
    result = dict(base)
    for key, value in updates.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
