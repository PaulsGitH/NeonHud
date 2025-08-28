"""
Process list collector.

Returns a list of typed dicts (top-N by CPU% by default):
[
  {
    "pid": int,
    "name": str,
    "cmdline": str,
    "cpu_percent": float,  # 0.0–100.0 (normalized across CPUs)
    "rss_bytes": int
  },
  ...
]
"""

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict, Any

import psutil
from neonhud.core.logging import get_logger

log = get_logger()

SortKey = Literal["cpu", "rss"]


class ProcessRow(TypedDict):
    pid: int
    name: str
    cmdline: str
    cpu_percent: float
    rss_bytes: int


def _flatten_cmdline(cmdline: Optional[List[str]], name: str) -> str:
    """
    Turn a list of argv tokens into a single string, with sensible fallbacks.
    Trims to ~120 chars for stable table rendering later.
    """
    if not cmdline:
        return name
    text = " ".join(x for x in cmdline if x is not None)
    text = text.strip() or name
    if len(text) > 120:
        return text[:117] + "..."
    return text


def sample(limit: int = 50, sort_by: SortKey = "cpu") -> List[ProcessRow]:
    """
    Collect a snapshot of running processes.

    - Uses psutil.process_iter with attribute prefetch to be efficient.
    - Handles AccessDenied/Zombie/NoSuchProcess gracefully (skips).
    - Normalizes per-process CPU% to a 0–100 scale across logical CPUs.
    """
    log.debug("Collecting process metrics (limit=%d, sort_by=%s)", limit, sort_by)

    attrs = ["pid", "name", "cmdline", "cpu_percent", "memory_info"]
    rows: List[ProcessRow] = []

    ncpu = psutil.cpu_count(logical=True) or 1
    ncpu_f = float(ncpu)

    for p in psutil.process_iter(attrs=attrs):
        try:
            info: dict[str, Any] = p.info  # type: ignore[assignment]

            pid_obj = info.get("pid", p.pid)
            pid = int(pid_obj) if isinstance(pid_obj, (int, float)) else int(p.pid)

            name_obj = info.get("name")
            name = str(name_obj) if isinstance(name_obj, str) else f"pid:{pid}"

            cmdline_obj = info.get("cmdline")
            cmdline_list: Optional[List[str]] = (
                cmdline_obj if isinstance(cmdline_obj, list) else None
            )

            cpu_obj = info.get("cpu_percent")
            raw_cpu_pct = float(cpu_obj) if isinstance(cpu_obj, (int, float)) else 0.0

            # Normalize to 0–100 across CPUs and clamp
            cpu_pct = raw_cpu_pct / ncpu_f
            if cpu_pct < 0.0:
                cpu_pct = 0.0
            if cpu_pct > 100.0:
                cpu_pct = 100.0

            meminfo = info.get("memory_info")
            rss = int(getattr(meminfo, "rss", 0) or 0)

            rows.append(
                ProcessRow(
                    pid=pid,
                    name=name,
                    cmdline=_flatten_cmdline(cmdline_list, name),
                    cpu_percent=round(cpu_pct, 1),
                    rss_bytes=rss,
                )
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    if not rows:
        log.debug("Processes collected: 0 rows")
        return []

    if sort_by == "rss":
        rows.sort(key=lambda r: r["rss_bytes"], reverse=True)
    else:
        rows.sort(key=lambda r: (r["cpu_percent"], r["rss_bytes"]), reverse=True)

    if limit > 0:
        rows = rows[:limit]

    log.debug("Processes collected: %d rows", len(rows))
    return rows
