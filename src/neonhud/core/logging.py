"""
Logging setup for NeonHud.

Provides a configured logger with RichHandler if available.
Log level can be set via:
- Config file (key: log_level)
- Env var NEONHUD_LOG_LEVEL
- Defaults to INFO
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from neonhud.core import config as core_config

try:
    from rich.logging import RichHandler

    _HAS_RICH = True
except ImportError:
    RichHandler = None  # type: ignore
    _HAS_RICH = False


_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str = "neonhud") -> logging.Logger:
    """Return the global NeonHud logger, configuring it on first use."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    cfg = core_config.load_config()
    cfg_level = str(cfg.get("log_level", "")).upper()
    env_level = os.environ.get("NEONHUD_LOG_LEVEL", "").upper()

    level_str = env_level or cfg_level or "INFO"
    level = getattr(logging, level_str, logging.INFO)

    handlers: list[logging.Handler] = []
    if _HAS_RICH and RichHandler is not None:
        handlers.append(
            RichHandler(
                markup=True,
                rich_tracebacks=True,
                log_time_format="%H:%M:%S",
            )
        )
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        handlers=handlers,
        format="%(message)s",
    )

    _LOGGER = logging.getLogger(name)
    _LOGGER.setLevel(level)
    return _LOGGER
