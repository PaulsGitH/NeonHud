"""
Theme registry for NeonHud.

Defines a Theme dataclass and a small registry of named themes.
Themes provide colors for UI elements (Rich-compatible style strings).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from neonhud.core import config


@dataclass(frozen=True)
class Theme:
    name: str
    primary: str  # table headers, titles
    accent: str  # highlights, separators
    warning: str  # high CPU usage, warnings
    background: str  # optional (not yet applied everywhere)


# Built-in themes
_THEMES: Dict[str, Theme] = {
    "classic": Theme(
        name="classic",
        primary="bold white",
        accent="cyan",
        warning="red",
        background="black",
    ),
    "cyberpunk": Theme(
        name="cyberpunk",
        primary="bold magenta",
        accent="bright_cyan",
        warning="bright_yellow",
        background="black",
    ),
}


def get_theme(name: str | None = None) -> Theme:
    """
    Resolve a theme by name, with fallback to config and then default.

    - If `name` provided, prefer that.
    - Else check config.load_config()["theme"].
    - Fallback to 'classic'.
    """
    if name and name in _THEMES:
        return _THEMES[name]

    cfg = config.load_config()
    cfg_name = cfg.get("theme", "classic")
    return _THEMES.get(cfg_name, _THEMES["classic"])
