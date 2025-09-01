"""
Dashboard layout: top row (CPU+Memory), bottom row (per-disk + per-NIC).
Maintains simple rate histories for sparklines with optional EMA smoothing.
"""

from __future__ import annotations
import os
from collections import deque
from typing import Deque, Dict, Any

from rich.columns import Columns
from rich.console import RenderableType, Console

from neonhud.collectors import cpu, mem as mem_col, disk, net
from neonhud.collectors.disk import DiskCounters
from neonhud.collectors.net import NetCounters
from neonhud.core import config as core_config
from neonhud.ui.theme import get_theme, Theme
from neonhud.ui import panels
from neonhud.utils.smooth import ema


# ---------------- Config helpers ----------------


def _as_bool(val: Any, default: bool = False) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        s = val.strip().lower()
        if s in {"1", "true", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "no", "n", "off"}:
            return False
    return default


def _history_len() -> int:
    env_val = os.environ.get("NEONHUD_HISTORY_LEN", "").strip()
    if env_val.isdigit():
        n = int(env_val)
        if n >= 4:
            return n
    cfg = core_config.load_config()
    try:
        n = int(cfg.get("history_len", 60))
        return max(4, n)
    except Exception:
        return 60


def _smoothing_enabled() -> bool:
    # Env overrides config
    env = os.environ.get("NEONHUD_SMOOTHING")
    if env is not None:
        return _as_bool(env, default=True)
    cfg = core_config.load_config()
    return _as_bool(cfg.get("smoothing", True), default=True)


def _smoothing_alpha() -> float:
    # Env overrides config
    env = os.environ.get("NEONHUD_SMOOTHING_ALPHA")
    if env is not None:
        try:
            a = float(env)
            return 0.0 if a < 0.0 else 1.0 if a > 1.0 else a
        except Exception:
            pass
    cfg = core_config.load_config()
    try:
        a = float(cfg.get("smoothing_alpha", 0.35))
        if a < 0.0:
            return 0.0
        if a > 1.0:
            return 1.0
        return a
    except Exception:
        return 0.35


# ---------------- Histories (per device/NIC) ----------------

_HLEN = _history_len()
_SMOOTH = _smoothing_enabled()
_ALPHA = _smoothing_alpha()

# per-device previous counters (disk)
_prev_disk_dev: Dict[str, DiskCounters] = {}
# per-nic previous counters (net)
_prev_net_nic: Dict[str, NetCounters] = {}

# histories for rates (sparklines)
_hist_disk_r: Dict[str, Deque[float]] = {}
_hist_disk_w: Dict[str, Deque[float]] = {}
_hist_nic_rx: Dict[str, Deque[float]] = {}
_hist_nic_tx: Dict[str, Deque[float]] = {}


def _dq_for(store: Dict[str, Deque[float]], key: str) -> Deque[float]:
    dq = store.get(key)
    if dq is None or dq.maxlen != _HLEN:
        # (Re)create deque if history length changed
        dq = deque(maxlen=_HLEN)
        store[key] = dq
    return dq


def _hist_view(seq: Deque[float]) -> list[float]:
    """Prepare history for UI: optionally smoothed list copy."""
    data = list(seq)
    if _SMOOTH and data:
        return ema(data, _ALPHA)
    return data


# ---------------- Build dashboard ----------------


def build_dashboard(theme: Theme | None = None) -> RenderableType:
    th = theme or get_theme("classic")

    # Top row: CPU + Memory overview
    cpu_stats = cpu.sample()
    mem_stats = mem_col.sample()
    top = panels.build_overview(cpu_stats, mem_stats, th)

    # ---------- Disk per-device ----------
    dev_counters: Dict[str, DiskCounters] = disk.sample_counters_per_device()
    dev_rates_view: Dict[str, Dict[str, Any]] = {}
    for dev, curr_d in dev_counters.items():
        prev_d: DiskCounters = _prev_disk_dev.get(dev) or curr_d
        drates = disk.rates_from(prev_d, curr_d, interval_sec=1.0)
        _prev_disk_dev[dev] = curr_d
        # update histories
        r_dq = _dq_for(_hist_disk_r, dev)
        w_dq = _dq_for(_hist_disk_w, dev)
        r_dq.append(drates["read_bps"])
        w_dq.append(drates["write_bps"])
        dev_rates_view[dev] = {
            "read_bps": drates["read_bps"],
            "write_bps": drates["write_bps"],
            "hist_r": _hist_view(r_dq),
            "hist_w": _hist_view(w_dq),
        }
    disks_panel = panels.build_disks_panel(dev_rates_view, th)

    # ---------- Net per-NIC ----------
    nic_counters: Dict[str, NetCounters] = net.sample_counters_per_nic()
    nic_rates_view: Dict[str, Dict[str, Any]] = {}
    for nic_name, curr_n in nic_counters.items():
        prev_n: NetCounters = _prev_net_nic.get(nic_name) or curr_n
        nrates = net.rates_from(prev_n, curr_n)  # derive dt from ts
        _prev_net_nic[nic_name] = curr_n
        # update histories
        rx_dq = _dq_for(_hist_nic_rx, nic_name)
        tx_dq = _dq_for(_hist_nic_tx, nic_name)
        rx_dq.append(nrates["recv_bps"])
        tx_dq.append(nrates["send_bps"])
        nic_rates_view[nic_name] = {
            "recv_bps": nrates["recv_bps"],
            "send_bps": nrates["send_bps"],
            "hist_rx": _hist_view(rx_dq),
            "hist_tx": _hist_view(tx_dq),
        }
    nics_panel = panels.build_nics_panel(nic_rates_view, th)

    bottom = Columns([disks_panel, nics_panel], equal=True, expand=True)
    return Columns([top, bottom], expand=True)


def render_dashboard_to_str(theme: Theme | None = None) -> str:
    th = theme or get_theme("classic")
    console = Console(record=True, width=100)
    console.print(build_dashboard(theme=th))
    return console.export_text()
