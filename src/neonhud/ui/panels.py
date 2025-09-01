"""
Dashboard panels for NeonHud (CPU + Memory).

Public helpers:
- build_cpu_panel(cpu: dict) -> Panel
- build_memory_panel(mem: dict) -> Panel
- build_overview(cpu: dict, mem: dict) -> RenderableType  (Columns)
- render_overview_to_str(cpu: dict, mem: dict) -> str
"""

from __future__ import annotations

from typing import Any, List

from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console, RenderableType, Group
from rich.text import Text

from neonhud.utils.bar import make_bar
from neonhud.utils.format import format_percent, format_bytes
from neonhud.ui.theme import get_theme, Theme


def build_cpu_panel(cpu: dict[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    total = float(cpu.get("percent_total", 0.0))
    bar = make_bar(total, width=24)

    lines: List[Text] = [Text(f"{bar}  {format_percent(total)}", style=th.primary)]

    # Per-core breakdown
    per_core = cpu.get("per_core", [])
    for idx, pct in enumerate(per_core):
        cbar = make_bar(float(pct), width=12)
        lines.append(Text(f"Core {idx}: {cbar} {format_percent(pct)}", style=th.accent))

    body = Group(*lines)
    return Panel(body, title="CPU", border_style=th.accent)


def build_memory_panel(mem: dict[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    percent = float(mem.get("percent", 0.0))
    bar = make_bar(percent, width=24)

    used = int(mem.get("used", 0))
    total = int(mem.get("total", 0))

    body = Group(
        Text(f"{bar}  {format_percent(percent)}", style=th.primary),
        Text(f"Used: {format_bytes(used)} / {format_bytes(total)}", style=th.accent),
    )

    return Panel(body, title="Memory", border_style=th.accent)


def build_overview(
    cpu: dict[str, Any], mem: dict[str, Any], theme: Theme | None = None
) -> RenderableType:
    th = theme or get_theme("classic")
    return Columns(
        [build_cpu_panel(cpu, th), build_memory_panel(mem, th)],
        equal=True,
        expand=True,
    )


def render_overview_to_str(
    cpu: dict[str, Any], mem: dict[str, Any], theme: Theme | None = None
) -> str:
    th = theme or get_theme("classic")
    console = Console(record=True, width=80)
    console.print(build_overview(cpu, mem, th))
    return console.export_text()
