"""Centralized logging configuration for the Excel Product Engine.

Products should call ``get_logger(__name__)`` rather than using ``print``
or instantiating their own handlers, so log output stays consistent and
controllable in one place (see section 26 of the engine spec).
"""

from __future__ import annotations

import logging
import sys

_ENGINE_LOGGER_NAME = "excel_engine"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root engine logger.

    Idempotent — safe to call multiple times (e.g. once per test), it
    will not attach duplicate handlers.
    """
    root = logging.getLogger(_ENGINE_LOGGER_NAME)
    if root.handlers:
        root.setLevel(level)
        return

    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger, e.g. get_logger('core.workbook')."""
    configure_logging()
    return logging.getLogger(f"{_ENGINE_LOGGER_NAME}.{name}")
