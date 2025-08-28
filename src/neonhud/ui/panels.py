"""
Dashboard panels for NeonHud (CPU + Memory).

Public helpers:
- build_cpu_panel(cpu: dict) -> Panel
- build_memory_panel(mem: dict) -> Panel
- build_overview(cpu: dict, mem: dict) -> RenderableType  (Columns)
- render_overview_to_str(cpu: dict, mem: dict) -> str
"""

from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.text import Text

from neonhud.utils.bar import make_bar
from neonhud.utils.format import format_percent
from neonhud.ui.themes import get_theme, Theme


def build_cpu_panel(cpu: dict[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme()
    total = float(cpu.get("percent_total", 0.0))
    bar = make_bar(total, width=24)
    body = Text(f"{bar}  {format_percent(total)}", style=th.primary)
    return Panel(body, title="CPU", border_style=th.accent)


def build_memory_panel(mem: dict[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme()
    percent = float(mem.get("percent", 0.0))
    bar = make_bar(percent, width=24)
    body = Text(f"{bar}  {format_percent(percent)}", style=th.primary)
    return Panel(body, title="Memory", border_style=th.accent)


def build_overview(
    cpu: dict[str, Any], mem: dict[str, Any], theme: Theme | None = None
) -> RenderableType:
    th = theme or get_theme()
    return Columns(
        [build_cpu_panel(cpu, th), build_memory_panel(mem, th)], equal=True, expand=True
    )


def render_overview_to_str(
    cpu: dict[str, Any], mem: dict[str, Any], theme: Theme | None = None
) -> str:
    th = theme or get_theme()
    console = Console(record=True, width=80)
    console.print(build_overview(cpu, mem, th))
    return console.export_text()
