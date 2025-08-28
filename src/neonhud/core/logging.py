"""
Logging setup for NeonHud.

Provides a configured logger with RichHandler if available.
Log level can be set via:
- Config file (key: log_level)
- Env var NEONHUD_LOG_LEVEL
- Defaults to INFO

Design:
- Singleton logger named "neonhud"
- Logger level set to NOTSET so root/handlers control filtering
- Handlers write to STDERR so CLI JSON on STDOUT isn't polluted
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from neonhud.core import config as core_config

try:
    from rich.console import Console
    from rich.logging import RichHandler

    _HAS_RICH = True
except Exception:
    Console = None  # type: ignore
    RichHandler = None  # type: ignore
    _HAS_RICH = False

_LOGGER: Optional[logging.Logger] = None
_CONFIGURED = False


def _configure_once() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    cfg = core_config.load_config()
    cfg_level = str(cfg.get("log_level", "")).upper()
    env_level = os.environ.get("NEONHUD_LOG_LEVEL", "").upper()

    level_str = env_level or cfg_level or "INFO"
    level = getattr(logging, level_str, logging.INFO)

    handlers: list[logging.Handler] = []
    if _HAS_RICH and RichHandler is not None and Console is not None:
        handlers.append(
            RichHandler(
                console=Console(stderr=True),  # send logs to STDERR
                markup=True,
                rich_tracebacks=True,
                log_time_format="%H:%M:%S",
            )
        )
    else:
        handlers.append(logging.StreamHandler(stream=sys.stderr))

    # Configure root logger once
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format="%(message)s",
    )
    _CONFIGURED = True


def get_logger() -> logging.Logger:
    """
    Return the global NeonHud logger (singleton).
    - Name is always "neonhud"
    - Level is NOTSET so tests (caplog) and root handlers control filtering
    """
    global _LOGGER
    _configure_once()

    if _LOGGER is None:
        logger = logging.getLogger("neonhud")
        logger.setLevel(logging.NOTSET)  # allow root/handlers to decide
        _LOGGER = logger

    return _LOGGER
