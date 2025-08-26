"""
Process table renderer (Rich).

Public helpers:
- build_table(rows, theme=None) -> rich.table.Table
- render_to_str(rows, theme=None) -> str (for tests or logging)
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING, Optional

from rich.table import Table
from rich.console import Console
from rich.text import Text

from neonhud.utils.format import format_bytes, format_percent
from neonhud.ui.themes import get_theme, Theme

if TYPE_CHECKING:
    # For typing only; avoids runtime import cycle
    from neonhud.collectors.procs import ProcessRow


def build_table(rows: "List[ProcessRow]", theme: Optional[Theme] = None) -> Table:
    """
    Build a Rich Table from a list of ProcessRow items.
    Columns:
      PID | NAME | CMDLINE | CPU% | RSS
    """
    th = theme or get_theme()

    table = Table(
        show_header=True,
        header_style=th.primary,  # header row style
        expand=True,
        style=th.background,  # table body base style (optional)
    )

    # IMPORTANT: also set header_style per column so Column.header_style matches tests
    table.add_column("PID", justify="right", no_wrap=True, header_style=th.primary)
    table.add_column("NAME", overflow="fold", ratio=1, header_style=th.primary)
    table.add_column("CMDLINE", overflow="fold", ratio=3, header_style=th.primary)
    table.add_column("CPU%", justify="right", no_wrap=True, header_style=th.primary)
    table.add_column("RSS", justify="right", no_wrap=True, header_style=th.primary)

    warn_threshold = 80.0  # %; could come from config later

    for r in rows:
        cpu_str = format_percent(r["cpu_percent"])
        # Use empty string when no style to satisfy mypy (Text(style expects str|Style))
        cpu_style = th.warning if r["cpu_percent"] >= warn_threshold else ""
        cpu_cell = Text(cpu_str, style=cpu_style)

        row_style = th.accent if r["cpu_percent"] >= warn_threshold else None

        table.add_row(
            str(r["pid"]),
            r["name"],
            r["cmdline"],
            cpu_cell,
            format_bytes(r["rss_bytes"]),
            style=row_style,
        )

    return table


def render_to_str(rows: "List[ProcessRow]", theme: Optional[Theme] = None) -> str:
    """
    Render the table to a string (useful for tests and debug logs).
    """
    th = theme or get_theme()
    console = Console(record=True, width=120)
    console.print(build_table(rows, theme=th))
    return console.export_text()
