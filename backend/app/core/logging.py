"""
Centralized logging configuration.

Import `get_logger(__name__)` in any module instead of calling
`logging.getLogger` directly, so log formatting/level stays consistent
across the app.
"""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
