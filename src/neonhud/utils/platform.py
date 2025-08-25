"""
Host/platform utilities (cross-platform-friendly).
"""

from __future__ import annotations

from typing import Dict
import platform
import socket


def platform_host() -> Dict[str, str]:
    """
    Return a minimal host profile:
      - hostname: system hostname
      - os: human-friendly OS string
      - kernel: kernel or OS release (Linux kernel, Windows build)
    """
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"

    sys_name = platform.system() or "UnknownOS"
    release = platform.release() or ""
    # e.g., "Linux 6.9.3" or "Windows 11" etc.
    os_string = f"{sys_name} {release}".strip()

    # On Linux, kernel == release. On others, it's still informative.
    kernel = release

    return {
        "hostname": hostname,
        "os": os_string,
        "kernel": kernel,
    }
