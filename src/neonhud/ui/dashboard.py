"""
Dashboard view orchestration for NeonHud.

Renders:
- Top row: CPU + Memory overview (panels.build_overview)
- Bottom row: Disk I/O and Network I/O panels with animated sparklines

Design:
- Stateless collectors (cpu, mem, disk, net)
- Module-level rolling histories (deque) for Disk/Net to animate sparklines
- Each tick (build_dashboard call) computes deltas -> bytes/sec -> append history
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional

from rich.console import Console, RenderableType, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from neonhud.collectors import cpu, mem, disk, net
from neonhud.collectors.disk import DiskCounters, DiskRates
from neonhud.collectors.net import NetCounters, NetRates
from neonhud.ui import panels
from neonhud.ui.themes import get_theme, Theme
from neonhud.utils.spark import sparkline

# ---- History state for animated panels ---------------------------------------

_HISTORY_LEN = 60  # ~ last 60 ticks
_disk_read_bps: Deque[float] = deque(maxlen=_HISTORY_LEN)
_disk_write_bps: Deque[float] = deque(maxlen=_HISTORY_LEN)
_net_rx_bps: Deque[float] = deque(maxlen=_HISTORY_LEN)
_net_tx_bps: Deque[float] = deque(maxlen=_HISTORY_LEN)

_prev_disk: Optional[DiskCounters] = None
_prev_net: Optional[NetCounters] = None


def _format_bps(v: float) -> str:
    """
    Human-readable bytes/sec (B/s, KiB/s, MiB/s, GiB/s, TiB/s).
    """
    n = float(v)
    units = ["B/s", "KiB/s", "MiB/s", "GiB/s", "TiB/s"]
    i = 0
    while n >= 1024.0 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f"{n:.1f} {units[i]}"


def _disk_panel(theme: Theme) -> Panel:
    """
    Build Disk I/O panel: current read/write + sparklines.
    Updates history buffers as a side effect.
    """
    global _prev_disk
    curr: DiskCounters = disk.sample_counters()

    # Compute rates from prev
    rates: DiskRates = {"interval": 0.0, "read_bps": 0.0, "write_bps": 0.0}
    if _prev_disk is not None:
        rates = disk.rates_from(_prev_disk, curr)
    _prev_disk = curr

    # Append to history (even if zeros, for consistent animation)
    _disk_read_bps.append(float(rates["read_bps"]))
    _disk_write_bps.append(float(rates["write_bps"]))

    # Compose table with current values and sparkline
    tbl = Table.grid(padding=(0, 1))
    tbl.add_column(justify="left", no_wrap=True)
    tbl.add_column(justify="right", no_wrap=True)

    tbl.add_row(
        Text("Read", style=theme.accent),
        Text(_format_bps(float(rates["read_bps"])), style=theme.primary),
    )
    tbl.add_row(
        Text("Write", style=theme.accent),
        Text(_format_bps(float(rates["write_bps"])), style=theme.primary),
    )

    spark_read = sparkline(_disk_read_bps, max_width=36)
    spark_write = sparkline(_disk_write_bps, max_width=36)

    # Show sparklines beneath
    body = Group(
        tbl,
        Text(spark_read, style=theme.accent),
        Text(spark_write, style=theme.warning),
    )

    return Panel(
        body,
        title=Text("Disk I/O", style=theme.primary),
        border_style=theme.primary,
    )


def _net_panel(theme: Theme) -> Panel:
    """
    Build Network I/O panel: current rx/tx + sparklines.
    Updates history buffers as a side effect.
    """
    global _prev_net
    curr: NetCounters = net.sample_counters()

    # Compute rates from prev
    rates: NetRates = {"interval": 0.0, "tx_bps": 0.0, "rx_bps": 0.0}
    if _prev_net is not None:
        rates = net.rates_from(_prev_net, curr)
    _prev_net = curr

    _net_rx_bps.append(float(rates["rx_bps"]))
    _net_tx_bps.append(float(rates["tx_bps"]))

    tbl = Table.grid(padding=(0, 1))
    tbl.add_column(justify="left", no_wrap=True)
    tbl.add_column(justify="right", no_wrap=True)

    tbl.add_row(
        Text("Recv", style=theme.accent),
        Text(_format_bps(float(rates["rx_bps"])), style=theme.primary),
    )
    tbl.add_row(
        Text("Send", style=theme.accent),
        Text(_format_bps(float(rates["tx_bps"])), style=theme.primary),
    )

    spark_rx = sparkline(_net_rx_bps, max_width=36)
    spark_tx = sparkline(_net_tx_bps, max_width=36)

    body = Group(
        tbl,
        Text(spark_rx, style=theme.accent),
        Text(spark_tx, style=theme.warning),
    )

    return Panel(
        body,
        title=Text("Network I/O", style=theme.primary),
        border_style=theme.primary,
    )


def build_dashboard(theme: Theme | None = None) -> RenderableType:
    """
    Collect live stats and return a Rich renderable layout.

    Call this repeatedly in the CLI's Live loop to animate.
    """
    th = theme or get_theme()

    # Top row: CPU + Memory
    cpu_stats = cpu.sample()
    mem_stats = mem.sample()
    top = panels.build_overview(cpu_stats, mem_stats, theme=th)

    # Bottom row: Disk + Network
    disk_view = _disk_panel(th)
    net_view = _net_panel(th)

    # Compose a two-row layout
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=1),
    )
    layout["top"].update(top)

    # Bottom split left/right
    bottom = Layout()
    bottom.split_row(
        Layout(name="disk"),
        Layout(name="net"),
    )
    bottom["disk"].update(disk_view)
    bottom["net"].update(net_view)

    layout["bottom"].update(bottom)
    return layout


def render_dashboard_to_str(theme: Theme | None = None) -> str:
    """
    Render a one-off dashboard snapshot to string (for logging/tests).
    """
    th = theme or get_theme()
    console = Console(record=True, width=100)
    console.print(build_dashboard(theme=th))
    return console.export_text()


# Testing helpers (optional): ability to reset history between tests
def _reset_history_for_tests() -> None:
    _disk_read_bps.clear()
    _disk_write_bps.clear()
    _net_rx_bps.clear()
    _net_tx_bps.clear()
    global _prev_disk, _prev_net
    _prev_disk = None
    _prev_net = None
