"""
Rich-powered live dashboard for NeonHud.

Layout:
- Top row: CPU + Memory overview (panels.build_overview)
- Bottom rows: Disk I/O and Network I/O with live rates
"""

from __future__ import annotations

from typing import Deque, Optional
from collections import deque

from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from neonhud.collectors import cpu, mem
from neonhud.collectors.disk import (
    DiskCounters,
    DiskRates,
    sample_counters as disk_sample_counters,
    rates_from as disk_rates_from,
)
from neonhud.collectors.net import (
    NetCounters,
    NetRates,
    sample_counters as net_sample_counters,
    rates_from as net_rates_from,
)
from neonhud.core import config as core_config
from neonhud.ui import panels
from neonhud.ui.theme import get_theme, Theme
from neonhud.utils.spark import sparkline

# -------------------- History length (configurable) ----------------------------


def _resolve_history_len() -> int:
    # 1) Env override
    import os

    env_val = os.environ.get("NEONHUD_HISTORY_LEN", "").strip()
    if env_val.isdigit():
        n = int(env_val)
        if n >= 4:
            return n

    # 2) Config
    cfg = core_config.load_config()
    try:
        val = cfg.get("history_len", 60)
        n = int(val)
        if n >= 4:
            return n
    except Exception:
        pass

    # 3) Default
    return 60


_HISTORY_LEN = _resolve_history_len()

_disk_read_hist: Deque[float] = deque(maxlen=_HISTORY_LEN)
_disk_write_hist: Deque[float] = deque(maxlen=_HISTORY_LEN)
_net_rx_hist: Deque[float] = deque(maxlen=_HISTORY_LEN)
_net_tx_hist: Deque[float] = deque(maxlen=_HISTORY_LEN)

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


def _panel_title(text: str, theme: Theme) -> Text:
    # Styled title to match the rest of the UI
    return Text(f"⟡ {text} ⟡", style=theme.primary)


# -------------------- Panels ---------------------------------------------------


def _disk_panel(theme: Theme) -> Panel:
    """
    Build Disk I/O panel: current read/write + sparklines.
    Updates history buffers as a side effect.
    """
    global _prev_disk
    curr: DiskCounters = disk_sample_counters()

    # Compute rates from previous sample
    if _prev_disk is None:
        # DiskRates only has read_bps/write_bps (no interval)
        rates: DiskRates = {"read_bps": 0.0, "write_bps": 0.0}
    else:
        rates = disk_rates_from(_prev_disk, curr)

    _prev_disk = curr

    _disk_read_hist.append(float(rates["read_bps"]))
    _disk_write_hist.append(float(rates["write_bps"]))

    read_line = sparkline(list(_disk_read_hist)) if _disk_read_hist else ""
    write_line = sparkline(list(_disk_write_hist)) if _disk_write_hist else ""

    table = Table(show_header=False, expand=True)
    table.add_row(
        Text("Read:", style=theme.primary),
        Text(_format_bps(float(rates["read_bps"])), style=theme.accent),
        Text(read_line, style=theme.accent),
    )
    table.add_row(
        Text("Write:", style=theme.primary),
        Text(_format_bps(float(rates["write_bps"])), style=theme.accent),
        Text(write_line, style=theme.accent),
    )

    return Panel(
        table, title=_panel_title("Disk I/O", theme), border_style=theme.primary
    )


def _net_panel(theme: Theme) -> Panel:
    """
    Build Network I/O panel: current rx/tx + sparklines.
    Updates history buffers as a side effect.
    """
    global _prev_net
    curr: NetCounters = net_sample_counters()

    # Compute rates from previous sample
    if _prev_net is None:
        rates: NetRates = {"interval": 0.0, "rx_bps": 0.0, "tx_bps": 0.0}
    else:
        rates = net_rates_from(_prev_net, curr)

    _prev_net = curr

    _net_rx_hist.append(float(rates["rx_bps"]))
    _net_tx_hist.append(float(rates["tx_bps"]))

    rx_line = sparkline(list(_net_rx_hist)) if _net_rx_hist else ""
    tx_line = sparkline(list(_net_tx_hist)) if _net_tx_hist else ""

    table = Table(show_header=False, expand=True)
    table.add_row(
        Text("Recv:", style=theme.primary),
        Text(_format_bps(float(rates["rx_bps"])), style=theme.accent),
        Text(rx_line, style=theme.accent),
    )
    table.add_row(
        Text("Send:", style=theme.primary),
        Text(_format_bps(float(rates["tx_bps"])), style=theme.accent),
        Text(tx_line, style=theme.accent),
    )

    return Panel(
        table, title=_panel_title("Network I/O", theme), border_style=theme.primary
    )


# -------------------- Public API ----------------------------------------------


def build_dashboard(theme: Theme | None = None) -> RenderableType:
    """
    Collect live stats and return a Rich renderable layout.
    Call this repeatedly in the CLI's Live loop to animate.
    """
    th = theme or get_theme("classic")

    # Top row: CPU + Memory overview
    cpu_stats = cpu.sample()
    mem_stats = mem.sample()
    top = panels.build_overview(cpu_stats, mem_stats, theme=th)

    # Bottom row: Disk I/O + Net I/O
    bottom = Columns([_disk_panel(th), _net_panel(th)], equal=True, expand=True)

    return Columns([top, bottom], expand=True)


def render_dashboard_to_str(theme: Theme | None = None) -> str:
    """
    Render a one-off dashboard snapshot to string (for logging/tests).
    """
    th = theme or get_theme("classic")
    console = Console(record=True, width=100)
    console.print(build_dashboard(theme=th))
    return console.export_text()
