"""
Professional (gtop-style) dashboard layout for NeonHud.

Public entrypoints:
- build_top(theme) -> RenderableType
- build_pro_dashboard(theme=None) -> RenderableType    # thin wrapper for CLI compatibility
- run(interval=1.0, theme_name="classic") -> None      # manual live runner
"""

from __future__ import annotations

import time
from typing import Any

from rich.console import Console, RenderableType, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.live import Live
from rich.text import Text

from neonhud.collectors import cpu as cpu_col, mem as mem_col
from neonhud.collectors import procs as procs_col
from neonhud.collectors import disk as disk_col
from neonhud.collectors import net as net_col

from neonhud.ui.theme import get_theme, Theme
from neonhud.ui import process_table as proc_table
from neonhud.utils.bar import make_bar
from neonhud.utils.format import format_percent, format_bytes


# ---------------- CPU Panel ----------------


def build_cpu_panel(cpu: dict[str, Any], theme: Theme) -> Panel:
    total = float(cpu.get("percent_total", 0.0))
    per_core = cpu.get("per_cpu", [])

    lines: list[RenderableType] = []
    bar_total = make_bar(total, width=30)
    lines.append(
        Text(f"Total: {bar_total} {format_percent(total)}", style=theme.primary)
    )

    for idx, pct in enumerate(per_core):
        cbar = make_bar(pct, width=20)
        lines.append(
            Text(f"Core {idx}: {cbar} {format_percent(pct)}", style=theme.accent)
        )

    body = Group(*lines)
    return Panel(body, title="CPU", border_style=theme.accent)


# ---------------- Memory Panel ----------------


def build_memory_panel(mem: dict[str, Any], theme: Theme) -> Panel:
    percent = float(mem.get("percent", 0.0))
    used = int(mem.get("used", 0))
    total = int(mem.get("total", 0))

    bar = make_bar(percent, width=30)
    line = f"{bar} {format_percent(percent)} ({format_bytes(used)} / {format_bytes(total)})"

    body = Text(line, style=theme.primary)
    return Panel(body, title="Memory", border_style=theme.accent)


# ---------------- Simple snapshots (placeholders for later commits) ------------


def _disk_snapshot_panel(theme: Theme) -> Panel:
    c = disk_col.sample_counters()
    data = {
        "reads": format_bytes(int(c["read_bytes"])),
        "writes": format_bytes(int(c["write_bytes"])),
    }
    t = Columns(
        [
            Text(f"reads: {data['reads']}", style=theme.primary),
            Text(f"writes: {data['writes']}", style=theme.primary),
        ],
        equal=True,
        expand=True,
    )
    return Panel(t, title="Disk (cumulative)", border_style=theme.primary)


def _net_snapshot_panel(theme: Theme) -> Panel:
    c = net_col.sample_counters()
    data = {
        "sent": format_bytes(int(c["bytes_sent"])),
        "recv": format_bytes(int(c["bytes_recv"])),
    }
    t = Columns(
        [
            Text(f"sent: {data['sent']}", style=theme.primary),
            Text(f"recv: {data['recv']}", style=theme.primary),
        ],
        equal=True,
        expand=True,
    )
    return Panel(t, title="Network (cumulative)", border_style=theme.primary)


def _top_procs_panel(theme: Theme, limit: int = 8) -> Panel:
    rows = procs_col.sample(limit=limit, sort_by="cpu")
    table = proc_table.build_table(rows, theme=theme)
    return Panel(table, title="Processes", border_style=theme.primary)


# ---------------- Layout builders ---------------------------------------------


def build_top(theme: Theme) -> RenderableType:
    """
    Build top row: CPU + Memory side-by-side.
    """
    cpu_stats = cpu_col.sample()
    mem_stats = mem_col.sample()
    return Columns(
        [build_cpu_panel(cpu_stats, theme), build_memory_panel(mem_stats, theme)],
        equal=True,
        expand=True,
    )


def build_pro_dashboard(theme: Theme | None = None) -> RenderableType:
    """
    Thin wrapper used by CLI for now. Returns the current top-row layout.
    Later commits will expand this to full grid (overview, I/O, processes).
    """
    th = theme or get_theme("classic")
    return build_top(th)


# ---------------- Manual runner (dev convenience) -----------------------------


def run(interval: float = 1.0, theme_name: str = "classic") -> None:
    """
    Run the pro dashboard live (currently CPU + Memory only).
    """
    theme = get_theme(theme_name)
    console = Console()
    with Live(console=console, refresh_per_second=4) as live:
        try:
            while True:
                live.update(build_top(theme))
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[bold cyan]Exiting pro dashboard...[/]")
