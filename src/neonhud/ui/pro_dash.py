# src/neonhud/ui/pro_dash.py
"""
Pro dashboard (gtop-style) layout and helpers.

Exports:
- build_top(theme: Theme | None = None) -> RenderableType
- build_pro_dashboard(theme: Theme | None = None) -> RenderableType  (alias used by CLI)
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional, Any

from rich.console import RenderableType, Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.text import Text

from neonhud.collectors import procs
from neonhud.collectors import cpu as cpu_col
from neonhud.collectors import mem as mem_col
from neonhud.collectors import disk, net
from neonhud.collectors.disk import DiskCounters, DiskRates
from neonhud.collectors.net import NetCounters, NetRates
from neonhud.ui.theme import Theme, get_theme
from neonhud.ui.process_table import build_table as build_proc_table
from neonhud.utils.spark import sparkline
from neonhud.utils.format import format_percent, format_bytes

# -------------------- rolling history buffers ---------------------------------

HIST_LEN = 60

_cpu_hist: Deque[float] = deque(maxlen=HIST_LEN)
_mem_hist: Deque[float] = deque(maxlen=HIST_LEN)
_swap_hist: Deque[float] = deque(maxlen=HIST_LEN)
_net_rx_hist: Deque[float] = deque(maxlen=HIST_LEN)
_net_tx_hist: Deque[float] = deque(maxlen=HIST_LEN)

_prev_disk: Optional[DiskCounters] = None
_prev_net: Optional[NetCounters] = None


def _title(txt: str, th: Theme) -> Text:
    return Text(txt, style=th.primary)


# -------------------- small widgets -------------------------------------------


def _cpu_history_panel(th: Theme) -> Panel:
    cpu = cpu_col.sample()
    total_raw: Any = cpu.get("percent_total", 0.0)
    total = float(total_raw)
    _cpu_hist.append(total)
    body = Text(sparkline(list(_cpu_hist)), style=th.accent)
    return Panel(body, title=_title("CPU History", th), border_style=th.primary)


def _mem_swap_history_panel(th: Theme) -> RenderableType:
    m = mem_col.sample()
    mem_pct_raw: Any = m.get("percent", 0.0)
    swap_pct_raw: Any = m.get("swap_percent", 0.0)
    mem_pct = float(mem_pct_raw)
    swap_pct = float(swap_pct_raw)
    _mem_hist.append(mem_pct)
    _swap_hist.append(swap_pct)

    left = Panel(
        Text(sparkline(list(_mem_hist)), style=th.accent)
        + Text("\n", style=th.accent)
        + Text(sparkline(list(_swap_hist)), style=th.warning),
        title=_title("Memory and Swap History", th),
        border_style=th.primary,
    )

    mem_gauge = Panel(
        Text(format_percent(mem_pct), style=th.primary),
        title=_title("Memory", th),
        border_style=th.accent,
    )
    swap_gauge = Panel(
        Text(format_percent(swap_pct), style=th.primary),
        title=_title("Swap", th),
        border_style=th.accent,
    )

    right = Columns([mem_gauge, swap_gauge], equal=True, expand=True)
    return Columns([left, right], equal=False, expand=True)


def _net_history_panel(th: Theme) -> Panel:
    global _prev_net
    curr: NetCounters = net.sample_counters()
    prev: NetCounters = _prev_net if _prev_net is not None else curr
    rates: NetRates = net.rates_from(prev, curr)
    _prev_net = curr

    _net_rx_hist.append(float(rates["recv_bps"]))
    _net_tx_hist.append(float(rates["send_bps"]))

    text = Text()
    # format_bytes expects int; cast safely from float
    text.append(
        f"Receiving: {format_bytes(int(rates['recv_bps']))}/s\n", style=th.primary
    )
    text.append(
        f"Transferring: {format_bytes(int(rates['send_bps']))}/s\n", style=th.primary
    )
    text.append(sparkline(list(_net_rx_hist)), style=th.accent)
    text.append("\n")
    text.append(sparkline(list(_net_tx_hist)), style=th.warning)
    return Panel(text, title=_title("Network History", th), border_style=th.primary)


def _disk_usage_panel(th: Theme) -> Panel:
    # Show recent read/write throughput
    global _prev_disk
    curr: DiskCounters = disk.sample_counters()
    prev: DiskCounters = _prev_disk if _prev_disk is not None else curr
    rates: DiskRates = disk.rates_from(prev, curr)
    _prev_disk = curr

    body = Text(
        f"Read  {format_bytes(int(rates['read_bps']))}/s\n"
        f"Write {format_bytes(int(rates['write_bps']))}/s\n",
        style=th.primary,
    )
    return Panel(body, title=_title("Disk usage", th), border_style=th.primary)


def _processes_panel(th: Theme) -> Panel:
    rows = procs.sample(limit=12, sort_by="cpu")
    tbl: Table = build_proc_table(rows, theme=th)
    return Panel(tbl, title=_title("Processes", th), border_style=th.primary)


# -------------------- main layout ---------------------------------------------


def build_pro_dashboard(theme: Theme | None = None) -> RenderableType:
    """
    Full 2×2 + footer layout approximating gtop:
      [CPU History]
      [Memory+Swap History | Memory | Swap]
      [Network History | Processes]
      [Disk usage] (footer-sized)
    """
    th = theme or get_theme("classic")

    top = _cpu_history_panel(th)
    middle = _mem_swap_history_panel(th)
    bottom_left = _net_history_panel(th)
    bottom_right = _processes_panel(th)
    footer = _disk_usage_panel(th)

    row_bottom = Columns([bottom_left, bottom_right], equal=True, expand=True)
    layout = PanelsVStack([top, middle, row_bottom, footer])
    return layout


def build_top(theme: Theme | None = None) -> RenderableType:
    """
    Alias used by tests: returns a renderable snapshot of the pro dashboard.
    """
    return build_pro_dashboard(theme)


# -------------------- tiny vertical stack helper ------------------------------


class PanelsVStack:
    """
    Lightweight container that stacks renderables vertically.
    Rich will render each item in order with a blank line between.
    """

    def __init__(self, items: list[RenderableType]) -> None:
        self.items = items

    def __rich_console__(self, console: Console, options):
        first = True
        for it in self.items:
            if not first:
                yield Text("")  # vertical spacing
            first = False
            yield it
