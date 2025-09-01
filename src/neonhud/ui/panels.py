"""
Dashboard panels for NeonHud (CPU + Memory).
"""

from __future__ import annotations
from typing import Any
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console, Group, RenderableType
from rich.text import Text

from neonhud.utils.bar import make_bar
from neonhud.utils.format import format_percent
from neonhud.ui.theme import get_theme, Theme


def build_cpu_panel(cpu: dict[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")

    total = float(cpu.get("percent_total", 0.0))
    lines: list[Text] = [
        Text(f"{make_bar(total, 24)}  {format_percent(total)}", style=th.primary)
    ]

    # Accept either key: per_core (tests/compat) or per_cpu (collector)
    per_list = cpu.get("per_core")
    if per_list is None:
        per_list = cpu.get("per_cpu", [])

    for idx, pct in enumerate(per_list):
        cbar = make_bar(float(pct), width=20)
        # NB: label is "Core {idx}" to match tests
        lines.append(Text(f"Core {idx}: {cbar} {format_percent(pct)}", style=th.accent))

    body = Group(*lines)
    return Panel(body, title="CPU", border_style=th.accent)


def build_memory_panel(mem: dict[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    percent = float(mem.get("percent", 0.0))
    bar = make_bar(percent, width=24)
    body = Text(f"{bar}  {format_percent(percent)}", style=th.primary)
    return Panel(body, title="Memory", border_style=th.accent)


def build_overview(
    cpu: dict[str, Any], mem: dict[str, Any], theme: Theme | None = None
) -> RenderableType:
    th = theme or get_theme("classic")
    return Columns(
        [build_cpu_panel(cpu, th), build_memory_panel(mem, th)], equal=True, expand=True
    )


def render_overview_to_str(
    cpu: dict[str, Any], mem: dict[str, Any], theme: Theme | None = None
) -> str:
    th = theme or get_theme("classic")
    console = Console(record=True, width=80)
    console.print(build_overview(cpu, mem, th))
    return console.export_text()
