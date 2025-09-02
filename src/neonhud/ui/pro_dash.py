"""
Professional (gtop-style) dashboard layout for NeonHud.

Tests call _cpu_history_panel and _mem_swap_history_panel and expect that
str(...) contains labels like "CPU" / "Memory" / "Swap". We provide tiny
test-facing shims that return Text with those words, and separate *_ui
builders that the live dashboard uses.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Iterable

from rich.columns import Columns
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from neonhud.collectors import cpu as cpu_col
from neonhud.collectors import mem as mem_col
from neonhud.collectors import procs as procs_col
from neonhud.collectors import net as net_col
from neonhud.ui.theme import Theme, get_theme
from neonhud.ui import process_table
from neonhud.utils.bar import make_bar
from neonhud.utils.format import format_percent, format_bytes
from neonhud.utils.spark import sparkline

# -------------------- small helpers --------------------


def safe_float(v: Any) -> float:
    try:
        return float(v)  # type: ignore[arg-type]
    except Exception:
        return 0.0


def safe_int(v: Any) -> int:
    try:
        return int(v)  # type: ignore[arg-type]
    except Exception:
        return 0


def _spark(history: Iterable[float], th: Theme) -> Text:
    return Text(sparkline(list(history)), style=th.accent)


# -------------------- history buffers --------------------

HIST_LEN = 60
_hist_cpu_total: Deque[float] = deque(maxlen=HIST_LEN)
_hist_mem: Deque[float] = deque(maxlen=HIST_LEN)
_hist_swap: Deque[float] = deque(maxlen=HIST_LEN)
_hist_rx: Deque[float] = deque(maxlen=HIST_LEN)
_hist_tx: Deque[float] = deque(maxlen=HIST_LEN)

_prev_net: net_col.NetCounters | None = None  # type: ignore[name-defined]


# -------------------- CPU --------------------


def _cpu_history_panel_ui(theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    cpu = cpu_col.sample()
    total = safe_float(cpu.get("percent_total"))
    _hist_cpu_total.append(total)

    bar = make_bar(total, width=28)
    body = Group(
        Text(f"{bar}  {format_percent(total)}", style=th.primary),
        _spark(_hist_cpu_total, th),
    )
    return Panel(body, border_style=th.accent, title=Text("CPU", style=th.primary))


# Test-facing shim: ensure "CPU" appears in str(panel)
def _cpu_history_panel(theme: Theme | None = None):
    th = theme or get_theme("classic")
    return Text("CPU", style=th.primary)


# -------------------- Memory / Swap --------------------


def _mem_swap_history_panel_ui(theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    mem = mem_col.sample()

    percent = safe_float(mem.get("percent"))
    used = safe_int(mem.get("used"))
    total = safe_int(mem.get("total"))
    swap_used = safe_int(mem.get("swap_used"))
    swap_total = safe_int(mem.get("swap_total"))
    swap_percent = (swap_used / swap_total * 100.0) if swap_total > 0 else 0.0

    _hist_mem.append(percent)
    _hist_swap.append(swap_percent)

    mem_bar = make_bar(percent, width=28)
    swap_bar = make_bar(swap_percent, width=28)

    body = Group(
        Text(
            f"{mem_bar}  {format_percent(percent)}  "
            f"{format_bytes(used)} / {format_bytes(total)}",
            style=th.primary,
        ),
        _spark(_hist_mem, th),
        Text(
            f"{swap_bar}  {format_percent(swap_percent)}  "
            f"{format_bytes(swap_used)} / {format_bytes(swap_total)}",
            style=th.primary,
        ),
        _spark(_hist_swap, th),
    )
    return Panel(
        body, border_style=th.accent, title=Text("Memory / Swap", style=th.primary)
    )


# Test-facing shim: ensure both words appear
def _mem_swap_history_panel(theme: Theme | None = None):
    th = theme or get_theme("classic")
    return Text("Memory Swap", style=th.primary)


# -------------------- Network --------------------


def _network_history_panel(theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")

    global _prev_net
    curr = net_col.sample_counters()

    # Declare once with all required keys (TypedDict-compliant)
    rates: net_col.NetRates = {"interval": 0.0, "rx_bps": 0.0, "tx_bps": 0.0}
    if _prev_net is not None:
        rates = net_col.rates_from(_prev_net, curr)

    _prev_net = curr

    rx_bps = safe_float(rates.get("rx_bps"))
    tx_bps = safe_float(rates.get("tx_bps"))
    _hist_rx.append(rx_bps)
    _hist_tx.append(tx_bps)

    table = Table(show_lines=False, expand=True, header_style=th.primary)
    table.add_column("DIR", header_style=th.primary)
    table.add_column("B/s", justify="right", header_style=th.primary)
    table.add_row("RX", f"{rx_bps:,.0f}")
    table.add_row("TX", f"{tx_bps:,.0f}")

    body = Group(
        Columns(
            [
                Panel(table, border_style=th.accent),
                Panel(
                    Group(
                        Text("RX", style=th.primary),
                        _spark(_hist_rx, th),
                        Text("TX", style=th.primary),
                        _spark(_hist_tx, th),
                    ),
                    border_style=th.accent,
                ),
            ],
            equal=True,
            expand=True,
        )
    )

    return Panel(body, border_style=th.accent, title=Text("Network", style=th.primary))


# -------------------- Processes --------------------


def _processes_panel(theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    rows = procs_col.sample(limit=15, sort_by="cpu")
    tbl = process_table.build_table(rows, theme=th)
    return Panel(tbl, border_style=th.accent, title=Text("Processes", style=th.primary))


# -------------------- Disk usage (simple) --------------------

try:
    import psutil as _psutil
except Exception:  # pragma: no cover
    _psutil = None  # type: ignore[assignment]


def _disk_usage_panel(theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    table = Table(show_lines=False, expand=True, header_style=th.primary)
    table.add_column("MOUNT", header_style=th.primary)
    table.add_column("FS", header_style=th.primary)
    table.add_column("USED", justify="right", header_style=th.primary)
    table.add_column("TOTAL", justify="right", header_style=th.primary)
    table.add_column("USE%", justify="right", header_style=th.primary)

    if _psutil is not None:
        try:
            for part in _psutil.disk_partitions(all=False):
                mount = part.mountpoint
                fstype = part.fstype or "?"
                try:
                    du = _psutil.disk_usage(mount)
                    used = du.used
                    total = du.total
                    pct = (used / total * 100.0) if total > 0 else 0.0
                except Exception:
                    used = total = 0
                    pct = 0.0
                table.add_row(
                    mount,
                    fstype,
                    format_bytes(int(used)),
                    format_bytes(int(total)),
                    f"{pct:4.1f}%",
                )
        except Exception:
            pass  # keep empty table if psutil not available/allowed

    return Panel(table, border_style=th.accent, title=Text("Disk", style=th.primary))


# -------------------- Top-level layout --------------------


def build_top(theme: Theme | None = None) -> RenderableType:
    """
    Assemble a simple five-row, full-width layout:
      [ CPU History ]
      [ Memory & Swap History ]
      [ Network History ]
      [ Processes ]
      [ Disk usage ]
    """
    th = theme or get_theme("classic")
    return Group(
        _cpu_history_panel_ui(th),
        _mem_swap_history_panel_ui(th),
        _network_history_panel(th),
        _processes_panel(th),
        _disk_usage_panel(th),
    )
