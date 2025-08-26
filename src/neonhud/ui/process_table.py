"""
Process table renderer (Rich).

Public helpers:
- build_table(rows) -> rich.table.Table
- render_to_str(rows) -> str (for tests or logging)
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from rich.table import Table
from rich.console import Console

from neonhud.utils.format import format_bytes, format_percent

if TYPE_CHECKING:
    # For typing only; avoids runtime import cycle
    from neonhud.collectors.procs import ProcessRow


def build_table(rows: "List[ProcessRow]") -> Table:
    """
    Build a Rich Table from a list of ProcessRow items.
    Columns:
      PID | NAME | CMDLINE | CPU% | RSS
    """
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("PID", justify="right", no_wrap=True)
    table.add_column("NAME", overflow="fold", ratio=1)
    table.add_column("CMDLINE", overflow="fold", ratio=3)
    table.add_column("CPU%", justify="right", no_wrap=True)
    table.add_column("RSS", justify="right", no_wrap=True)

    for r in rows:
        table.add_row(
            str(r["pid"]),
            r["name"],
            r["cmdline"],
            format_percent(r["cpu_percent"]),
            format_bytes(r["rss_bytes"]),
        )

    return table


def render_to_str(rows: "List[ProcessRow]") -> str:
    """
    Render the table to a string (useful for tests and debug logs).
    """
    console = Console(record=True, width=120)
    console.print(build_table(rows))
    return console.export_text()
