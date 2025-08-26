"""
Config loader for NeonHud.
Search order:
1. Env var NEONHUD_CONFIG (path to config file)
2. OS default config dir (~/.config/neonhud/config.toml on Linux/Mac,
   %APPDATA%/NeonHud/config.toml on Windows)
3. Built-in defaults
"""

from __future__ import annotations
import os
import tomllib
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "theme": "classic",
    "refresh_interval": 2.0,
    "process_limit": 15,
}


def _default_config_path() -> Path:
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
        return Path(base) / "NeonHud" / "config.toml"
    else:  # Linux/Mac
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        return Path(base) / "neonhud" / "config.toml"


def load_config() -> Dict[str, Any]:
    """Load config dict, falling back to defaults if missing/invalid."""
    path = None
    env_path = os.environ.get("NEONHUD_CONFIG")
    if env_path:
        path = Path(env_path)
    else:
        path = _default_config_path()

    if path and path.is_file():
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            merged = {**DEFAULT_CONFIG, **data}
            return merged
        except Exception:
            return dict(DEFAULT_CONFIG)
    else:
        return dict(DEFAULT_CONFIG)
