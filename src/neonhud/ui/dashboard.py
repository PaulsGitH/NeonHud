"""
Dashboard view orchestration for NeonHud.

Ties collectors (cpu, memory) into the panel renderers.
"""

from __future__ import annotations

from rich.console import Console, RenderableType

from neonhud.collectors import cpu, mem  # ← use mem, not memory
from neonhud.ui import panels
from neonhud.ui.themes import get_theme, Theme


def build_dashboard(theme: Theme | None = None) -> RenderableType:
    """
    Collect live CPU + memory stats and return a Rich renderable.
    """
    th = theme or get_theme()
    cpu_stats = cpu.sample()
    mem_stats = mem.sample()
    return panels.build_overview(cpu_stats, mem_stats, theme=th)


def render_dashboard_to_str(theme: Theme | None = None) -> str:
    """
    Render a one-off dashboard snapshot to string (for logging/tests).
    """
    th = theme or get_theme()
    console = Console(record=True, width=100)
    console.print(build_dashboard(theme=th))
    return console.export_text()
