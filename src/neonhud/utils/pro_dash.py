"""
Pro Dashboard scaffold (gtop-style segmented grid).
"""

from __future__ import annotations

from rich.layout import Layout
from rich.console import RenderableType
from rich.panel import Panel

from neonhud.core import config as core_config
from neonhud.utils.history import HistoryBuffer


# Shared history buffers
CPU_HISTORY = HistoryBuffer(
    maxlen=int(core_config.load_config().get("history_len", 120))
)
MEM_HISTORY = HistoryBuffer(
    maxlen=int(core_config.load_config().get("history_len", 120))
)
NET_HISTORY = HistoryBuffer(
    maxlen=int(core_config.load_config().get("history_len", 120))
)


def _placeholder(title: str) -> Panel:
    return Panel(f"{title} (stub)", title=title)


def build_pro_dashboard() -> RenderableType:
    """
    Build the segmented dashboard grid (scaffold only).
    """
    layout = Layout(name="root")

    # Top row: CPU history
    layout.split_column(
        Layout(name="cpu_hist", size=15),
        Layout(name="middle", size=15),
        Layout(name="bottom"),
    )

    # Middle row: Memory + Swap + donuts
    layout["middle"].split_row(
        Layout(name="mem_hist"),
        Layout(name="mem_donuts"),
    )

    # Bottom row: Net + Disk + Processes
    layout["bottom"].split_row(
        Layout(name="net_hist"),
        Layout(name="disk_proc"),
    )
    layout["disk_proc"].split_column(
        Layout(name="disk_donut", size=8),
        Layout(name="proc_table"),
    )

    # For now: placeholders
    layout["cpu_hist"].update(_placeholder("CPU History"))
    layout["mem_hist"].update(_placeholder("Memory/Swap History"))
    layout["mem_donuts"].update(_placeholder("Mem/Swap Donuts"))
    layout["net_hist"].update(_placeholder("Network History"))
    layout["disk_donut"].update(_placeholder("Disk Donut"))
    layout["proc_table"].update(_placeholder("Processes"))

    return layout
