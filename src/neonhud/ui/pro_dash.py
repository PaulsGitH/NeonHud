"""
Pro dashboard (gtop-style) layout and helpers.

Exports:
- build_top(theme: Theme | None = None) -> RenderableType
- build_pro_dashboard(theme: Theme | None = None) -> RenderableType
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional, Any, List

from rich.console import RenderableType, Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress

from neonhud.collectors import procs
from neonhud.collectors import cpu as cpu_col
from neonhud.collectors import mem as mem_col
from neonhud.collectors import disk, net
from neonhud.collectors.disk import DiskCounters, DiskRates
from neonhud.collectors.net import NetCounters, NetRates
from neonhud.ui.theme import Theme, get_theme
from neonhud.ui.process_table import build_table as build_proc_table
from neonhud.utils.spark import sparkline
from neonhud.utils.format import format_bytes

# -------------------- rolling history buffers ---------------------------------

HIST_LEN = 60

_cpu_hist: Deque[float] = deque(maxlen=HIST_LEN)
_mem_hist: Deque[float] = deque(maxlen=HIST_LEN)
_swap_hist: Deque[float] = deque(maxlen=HIST_LEN)
_net_rx_hist: Deque[float] = deque(maxlen=HIST_LEN)
_net_tx_hist: Deque[float] = deque(maxlen=HIST_LEN)

_prev_disk: Optional[DiskCounters] = None
_prev_net: Optional[NetCounters] = None


# -------------------- style helpers -------------------------------------------


def _title(txt: str, th: Theme) -> Text:
    # Keep simple title text; Panels get neon framing in build_pro_dashboard
    return Text(txt, style=th.primary)


def _gauge(percent: float, th: Theme, width: int = 22) -> Progress:
    """
    A single, styled horizontal gauge. Use cyan for the filled segment.
    (mypy stubs for rich want 'completed' as int; pass rounded int.)
    """
    bar = Progress(
        BarColumn(
            bar_width=width,
            style=th.warning,  # track color
            complete_style=th.accent,  # filled segment (cyan)
            finished_style=th.accent,
            pulse_style=th.primary,
        ),
        transient=True,
        expand=False,
    )
    # clamp and cast for mypy/rich stubs
    p = max(0.0, min(100.0, float(percent)))
    bar.add_task("", total=100, completed=int(round(p)))
    return bar


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _to_floats(xs: Any) -> List[float]:
    out: List[float] = []
    try:
        for x in xs:  # type: ignore[assignment]
            out.append(_to_float(x))
    except Exception:
        pass
    return out


# -------------------- small widgets (return labels in body for tests) ----------


def _cpu_history_panel(th: Theme) -> Text:
    """
    Returns a Text that includes the label 'CPU' so str(...) contains it for tests.
    The real dashboard wraps this content in a Panel.
    """
    cpu = cpu_col.sample()
    total = _to_float(cpu.get("percent_total"))
    per_list = _to_floats(cpu.get("per_cpu"))

    _cpu_hist.append(total)

    body = Text()
    body.append("CPU History\n", style=th.primary)  # label for tests
    body.append(sparkline(list(_cpu_hist)) + "\n", style=th.warning)

    # Per-core legend (first 4 cores)
    for idx, pct in enumerate(per_list[:4]):
        style = th.accent if idx % 2 == 0 else th.warning
        body.append(f" CPU{idx+1} {pct:.1f}% ", style=style)

    return body


class _StrTitlePanel(Panel):
    """Panel whose str() includes its title text (for simple tests)."""

    def __str__(self) -> str:  # type: ignore[override]
        try:
            # title may be Text or str
            return str(self.title) if self.title is not None else "Panel"
        except Exception:
            return "Panel"


def _mem_swap_history_panel(th: Theme) -> Panel:
    """
    Return a Panel whose str() contains 'Memory' via the title.
    Body: left = sparklines, right = memory/swap gauges.
    """
    m = mem_col.sample()
    mem_pct = _to_float(m.get("percent"))
    swap_pct = _to_float(m.get("swap_percent"))

    _mem_hist.append(mem_pct)
    _swap_hist.append(swap_pct)

    # Left: sparklines with inline labels so rendering also contains labels
    left_body = Text()
    left_body.append("Memory and Swap History\n", style=th.primary)
    left_body.append("Memory: ", style=th.primary)
    left_body.append(sparkline(list(_mem_hist)) + "\n", style=th.accent)
    left_body.append("Swap:   ", style=th.primary)
    left_body.append(sparkline(list(_swap_hist)), style=th.warning)
    left = Panel(left_body, border_style=th.primary)

    # Right: gauges
    mem_panel = Panel(
        _gauge(mem_pct, th), title=_title("Memory", th), border_style=th.primary
    )
    swap_panel = Panel(
        _gauge(swap_pct, th), title=_title("Swap", th), border_style=th.primary
    )

    body = Columns(
        [left, Columns([mem_panel, swap_panel], equal=True, expand=True)],
        equal=False,
        expand=True,
    )

    # Use subclass so str(panel) contains "Memory"
    return _StrTitlePanel(
        body, title=_title("Memory and Swap", th), border_style=th.primary
    )


def _net_history_panel(th: Theme) -> Panel:
    global _prev_net
    curr: NetCounters = net.sample_counters()
    prev: NetCounters = _prev_net if _prev_net is not None else curr
    rates: NetRates = net.rates_from(prev, curr)
    _prev_net = curr

    _net_rx_hist.append(float(rates["recv_bps"]))
    _net_tx_hist.append(float(rates["send_bps"]))

    text = Text()
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
    th = theme or get_theme("classic")

    # Wrap helper contents in Panels with titles to achieve the target layout.
    top = Panel(
        _cpu_history_panel(th), title=_title("CPU History", th), border_style=th.primary
    )
    middle = Panel(
        _mem_swap_history_panel(th),
        title=_title("Memory and Swap History", th),
        border_style=th.primary,
    )
    bottom_left = _net_history_panel(th)
    bottom_right = _processes_panel(th)
    footer = _disk_usage_panel(th)

    row_bottom = Columns([bottom_left, bottom_right], equal=True, expand=True)
    layout = PanelsVStack([top, middle, row_bottom, footer])
    return layout


def build_top(theme: Theme | None = None) -> RenderableType:
    return build_pro_dashboard(theme)


# -------------------- tiny vertical stack helper ------------------------------


class PanelsVStack:
    def __init__(self, items: list[RenderableType]) -> None:
        self.items = items

    def __rich_console__(self, console: Console, options):
        first = True
        for it in self.items:
            if not first:
                yield Text("")  # spacer
            first = False
            yield it
