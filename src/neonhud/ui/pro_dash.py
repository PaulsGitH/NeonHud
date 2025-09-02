"""
Professional (gtop-style) dashboard layout for NeonHud.

This module provides a single entrypoint:
    build_pro_dashboard(theme: Theme | None = None) -> RenderableType

It composes existing collectors and simple panels into a one-screen overview.
It’s intentionally light so CLI wiring and tests succeed; later commits can
enhance visuals (sparklines, per-core graphs, etc.).
"""

from __future__ import annotations

from typing import Any, Mapping

from rich.console import RenderableType
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from neonhud.collectors import cpu as cpu_col
from neonhud.collectors import mem as mem_col
from neonhud.collectors import procs as procs_col
from neonhud.collectors import disk as disk_col
from neonhud.collectors import net as net_col

from neonhud.ui.theme import Theme, get_theme
from neonhud.ui import panels as basic_panels
from neonhud.ui import process_table as proc_table
from neonhud.utils.format import format_bytes, format_percent


def _kv_table(title: str, data: Mapping[str, Any], *, theme: Theme) -> Panel:
    """Small two-column key/value table wrapped in a Panel."""
    t = Table.grid(padding=(0, 1))
    t.add_column(justify="left", style=theme.accent, no_wrap=True)
    t.add_column(justify="right", style=theme.primary, no_wrap=True)
    for k, v in data.items():
        t.add_row(str(k), str(v))
    return Panel(t, title=title, border_style=theme.primary)


def _disk_snapshot_panel(theme: Theme) -> Panel:
    c = disk_col.sample_counters()
    data = {
        "reads": format_bytes(int(c["read_bytes"])),
        "writes": format_bytes(int(c["write_bytes"])),
    }
    return _kv_table("Disk (cumulative)", data, theme=theme)


def _net_snapshot_panel(theme: Theme) -> Panel:
    c = net_col.sample_counters()
    data = {
        "sent": format_bytes(int(c["bytes_sent"])),
        "recv": format_bytes(int(c["bytes_recv"])),
    }
    return _kv_table("Network (cumulative)", data, theme=theme)


def _top_procs_panel(theme: Theme, limit: int = 8) -> Panel:
    rows = procs_col.sample(limit=limit, sort_by="cpu")
    table = proc_table.build_table(rows, theme=theme)
    return Panel(table, title="Processes", border_style=theme.primary)


def build_pro_dashboard(theme: Theme | None = None) -> RenderableType:
    """
    Compose a single-screen dashboard:
      ┌───────────────┬────────────────┐
      │   CPU panel   │  Memory panel  │   (top row)
      ├───────────────┼────────────────┤
      │ Disk snapshot │ Net snapshot   │   (middle row)
      └────────────────┴────────────────┘
      [   Processes table (full width)  ] (bottom)
    """
    th = theme or get_theme("classic")

    # Top row: CPU + Memory (reuse existing compact panels)
    cpu_stats = cpu_col.sample()
    mem_stats = mem_col.sample()
    top = Columns(
        [basic_panels.build_cpu_panel(cpu_stats, th), basic_panels.build_memory_panel(mem_stats, th)],
        equal=True,
        expand=True,
    )

    # Middle row: Disk + Network cumulative snapshots
    middle = Columns([_disk_snapshot_panel(th), _net_snapshot_panel(th)], equal=True, expand=True)

    # Bottom: Processes
    procs = _top_procs_panel(th, limit=8)

    # Stack rows vertically using a simple grid table to avoid Layout complexity
    grid = Table.grid(expand=True)
    # Titles for rows (subtle neon look)
    grid.add_row(Panel(top, title=Text("Overview", style=th.primary), border_style=th.accent))
    grid.add_row(Panel(middle, title=Text("I/O", style=th.primary), border_style=th.accent))
    grid.add_row(procs)

    return grid
