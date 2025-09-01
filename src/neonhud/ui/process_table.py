"""
Process table rendering for NeonHud.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Any

from rich.table import Table
from rich.text import Text
from rich.console import Console

from neonhud.ui.theme import Theme, get_theme


def _fmt_cpu(pct: float) -> str:
    # clamp for safety
    v = 0.0 if pct is None else max(0.0, float(pct))
    return f"{v:5.1f}"


def _fmt_bytes(n: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    x = float(n if n is not None else 0)
    i = 0
    while x >= 1024.0 and i < len(units) - 1:
        x /= 1024.0
        i += 1
    return f"{x:6.1f} {units[i]}"


def build_table(
    rows: Iterable[Mapping[str, Any]],
    theme: Theme | None = None,
) -> Table:
    """
    Build a Rich Table for the process list.

    Required row keys:
      pid:int, name:str, cmdline:str, cpu_percent:float, rss_bytes:int
    """
    th = theme or get_theme("classic")

    table = Table(show_lines=False, expand=True, header_style=th.primary)
    table.add_column("PID", justify="right", no_wrap=True, header_style=th.primary)
    table.add_column("NAME", justify="left", overflow="fold", header_style=th.primary)
    table.add_column(
        "CMDLINE", justify="left", overflow="fold", header_style=th.primary
    )
    table.add_column("CPU%", justify="right", no_wrap=True, header_style=th.primary)
    table.add_column("RSS", justify="right", no_wrap=True, header_style=th.primary)

    for r in rows:
        pid = int(r.get("pid", 0))
        name = str(r.get("name", ""))
        cmd = str(r.get("cmdline", ""))
        cpu_pct = float(r.get("cpu_percent", 0.0))
        rss = int(r.get("rss_bytes", 0))

        # highlight hot CPU rows
        style = th.warning if cpu_pct >= 80.0 else th.accent

        table.add_row(
            Text(str(pid), style=style),
            Text(name, style=style),
            Text(cmd, style=style),
            Text(_fmt_cpu(cpu_pct), style=style),
            Text(_fmt_bytes(rss), style=style),
        )

    return table


def render_to_str(
    rows: Iterable[Mapping[str, Any]],
    theme: Theme | None = None,
    width: int = 100,
) -> str:
    """
    Render a process table to a plain string (used in tests).
    """
    th = theme or get_theme("classic")
    console = Console(record=True, width=width)
    console.print(build_table(rows, theme=th))
    return console.export_text()
