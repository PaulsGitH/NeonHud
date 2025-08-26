from __future__ import annotations


def format_bytes(n: int) -> str:
    """
    Human-friendly bytes (binary units). Examples:
      0 -> "0 B"
      1536 -> "1.5 KiB"
      1048576 -> "1.0 MiB"
    """
    if n < 0:
        n = 0
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = float(n)
    idx = 0
    while size >= 1024.0 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    if idx == 0:
        return f"{int(size)} {units[idx]}"
    return f"{size:.1f} {units[idx]}"


def format_percent(p: float) -> str:
    """One decimal place percentage, clamped to [0,100]."""
    if p < 0.0:
        p = 0.0
    if p > 100.0:
        p = 100.0
    return f"{p:.1f}%"
