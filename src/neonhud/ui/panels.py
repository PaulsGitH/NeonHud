"""
Dashboard panels for NeonHud (CPU + Memory + I/O) with cyberpunk polish.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Sequence, cast

from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console, RenderableType, Group
from rich.text import Text

from neonhud.utils.bar import make_bar
from neonhud.utils.format import format_percent, format_bytes
from neonhud.ui.theme import get_theme, Theme
from neonhud.utils.spark import sparkline


# ---------------- Helpers ----------------


def _title(text: str, theme: Theme) -> Text:
    # neon-styled bracketed title
    return Text(f"⟡ {text} ⟡", style=theme.primary)


def _fmt_bps(v: float) -> str:
    units = ["B/s", "KiB/s", "MiB/s", "GiB/s", "TiB/s"]
    x = float(v)
    i = 0
    while x >= 1024.0 and i < len(units) - 1:
        x /= 1024.0
        i += 1
    return f"{x:5.1f} {units[i]}"


# ---------------- CPU ----------------


def build_cpu_panel(cpu: Mapping[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    total = float(cpu.get("percent_total", 0.0))
    bar = make_bar(total, width=24)

    lines: List[Text] = [Text(f"{bar}  {format_percent(total)}", style=th.primary)]

    # Optional mini-sparkline of total CPU (provided by dashboard)
    hist_total = cpu.get("hist_total")
    if isinstance(hist_total, list) and hist_total:
        s = sparkline([float(x) for x in hist_total][-40:])
        lines.append(Text(f"load {s}", style=th.accent))

    # Accept either per_core (compat/test) or per_cpu (collector)
    per_list = cpu.get("per_core")
    if per_list is None:
        per_list = cpu.get("per_cpu", [])

    per_seq: Sequence[float] = (
        cast(Sequence[float], per_list) if isinstance(per_list, list) else []
    )
    for idx, pct in enumerate(per_seq):
        cbar = make_bar(float(pct), width=12)
        lines.append(Text(f"Core {idx}: {cbar} {format_percent(pct)}", style=th.accent))

    return Panel(Group(*lines), title=_title("CPU", th), border_style=th.accent)


# --------------- Memory ----------------


def build_memory_panel(mem: Mapping[str, Any], theme: Theme | None = None) -> Panel:
    th = theme or get_theme("classic")
    percent = float(mem.get("percent", 0.0))
    bar = make_bar(percent, width=24)

    used = int(mem.get("used", 0))
    total = int(mem.get("total", 0))

    lines: List[Text] = [
        Text(f"{bar}  {format_percent(percent)}", style=th.primary),
        Text(f"Used: {format_bytes(used)} / {format_bytes(total)}", style=th.accent),
    ]

    # Optional mini-sparkline of memory % (provided by dashboard)
    hist_pct = mem.get("hist_percent")
    if isinstance(hist_pct, list) and hist_pct:
        s = sparkline([float(x) for x in hist_pct][-40:])
        lines.append(Text(f"trend {s}", style=th.accent))

    return Panel(Group(*lines), title=_title("Memory", th), border_style=th.accent)


# --------------- Disk per-device ----------------


def build_disks_panel(
    dev_rates: Mapping[str, Mapping[str, Any]],
    theme: Theme | None = None,
) -> Panel:
    """
    dev_rates: {
      device: {
        "read_bps": float,
        "write_bps": float,
        "hist_r": list[float],
        "hist_w": list[float],
      }
    }
    """
    th = theme or get_theme("classic")
    lines: List[Text] = []
    order = sorted(
        dev_rates.items(),
        key=lambda kv: max(
            float(kv[1].get("read_bps", 0.0)), float(kv[1].get("write_bps", 0.0))
        ),
        reverse=True,
    )
    for name, r in order:
        hist_r = cast(
            List[float], list(map(float, cast(Sequence[float], r.get("hist_r", []))))
        )
        hist_w = cast(
            List[float], list(map(float, cast(Sequence[float], r.get("hist_w", []))))
        )
        sr = sparkline(hist_r[-20:] or [0.0])
        sw = sparkline(hist_w[-20:] or [0.0])
        line = (
            f"{name:<8} R {_fmt_bps(float(r.get('read_bps', 0.0)))} {sr}   "
            f"W {_fmt_bps(float(r.get('write_bps', 0.0)))} {sw}"
        )
        lines.append(Text(line, style=th.primary))
    body = Group(*lines) if lines else Text("No disk activity", style=th.accent)
    return Panel(
        body, title=_title("Disk I/O (per device)", th), border_style=th.primary
    )


# --------------- Network per-NIC ----------------


def build_nics_panel(
    nic_rates: Mapping[str, Mapping[str, Any]],
    theme: Theme | None = None,
) -> Panel:
    """
    nic_rates: {
      nic: {
        "recv_bps": float,
        "send_bps": float,
        "hist_rx": list[float],
        "hist_tx": list[float],
      }
    }
    """
    th = theme or get_theme("classic")
    lines: List[Text] = []
    order = sorted(
        nic_rates.items(),
        key=lambda kv: max(
            float(kv[1].get("recv_bps", 0.0)), float(kv[1].get("send_bps", 0.0))
        ),
        reverse=True,
    )
    for name, r in order:
        hist_rx = cast(
            List[float], list(map(float, cast(Sequence[float], r.get("hist_rx", []))))
        )
        hist_tx = cast(
            List[float], list(map(float, cast(Sequence[float], r.get("hist_tx", []))))
        )
        srx = sparkline(hist_rx[-20:] or [0.0])
        stx = sparkline(hist_tx[-20:] or [0.0])
        line = (
            f"{name:<8} RX {_fmt_bps(float(r.get('recv_bps', 0.0)))} {srx}   "
            f"TX {_fmt_bps(float(r.get('send_bps', 0.0)))} {stx}"
        )
        lines.append(Text(line, style=th.primary))
    body = Group(*lines) if lines else Text("No network activity", style=th.accent)
    return Panel(
        body, title=_title("Network I/O (per interface)", th), border_style=th.primary
    )


# --------------- Overview (top row) ----------------


def build_overview(
    cpu: Mapping[str, Any], mem: Mapping[str, Any], theme: Theme | None = None
) -> RenderableType:
    th = theme or get_theme("classic")
    return Columns(
        [build_cpu_panel(cpu, th), build_memory_panel(mem, th)],
        equal=True,
        expand=True,
    )


def render_overview_to_str(
    cpu: Mapping[str, Any], mem: Mapping[str, Any], theme: Theme | None = None
) -> str:
    th = theme or get_theme("classic")
    console = Console(record=True, width=80)
    console.print(build_overview(cpu, mem, th))
    return console.export_text()
