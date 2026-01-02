import logging
from typing import Any, Dict

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure structured logging.

    Safe to call multiple times.
    """
    logging.basicConfig(level=level)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """
    Get a structured logger.
    """
    return structlog.get_logger(name)


def log_event(logger, event: str, **fields: Dict[str, Any]) -> None:
    """
    Emit a structured log event.
    """
    logger.info(event, **fields)
