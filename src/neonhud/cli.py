"""
NeonHud CLI entrypoint.
"""

from __future__ import annotations

import argparse
import sys
import time
import json

from rich.console import Console
from rich.live import Live

from neonhud.models import snapshot
from neonhud.collectors import procs
from neonhud.ui import process_table
from neonhud.ui.themes import get_theme
from neonhud.core import config as core_config


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="neonhud",
        description="NeonHud: Linux-native performance HUD (system metrics, TUI, systemd/RPM focus).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # `neonhud report`
    report_parser = subparsers.add_parser(
        "report", help="Print a JSON snapshot of system metrics"
    )
    report_parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON with indentation"
    )

    # `neonhud top`
    top_parser = subparsers.add_parser("top", help="Interactive Rich TUI of processes")
    top_parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Refresh interval in seconds (overrides config)",
    )
    top_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of processes to show (overrides config)",
    )
    top_parser.add_argument(
        "--theme", type=str, default=None, help="Theme name (overrides config)"
    )

    args = parser.parse_args(argv)

    if args.command == "report":
        snap = snapshot.build()
        if args.pretty:
            print(json.dumps(snap, indent=2))
        else:
            print(json.dumps(snap))
        return

    if args.command == "top":
        cfg = core_config.load_config()
        interval = (
            args.interval
            if args.interval is not None
            else float(cfg.get("refresh_interval", 2.0))
        )
        limit = (
            args.limit if args.limit is not None else int(cfg.get("process_limit", 15))
        )
        theme_name = (
            args.theme if args.theme is not None else cfg.get("theme", "classic")
        )
        theme = get_theme(theme_name)

        console = Console()
        with Live(console=console, refresh_per_second=8) as live:
            try:
                while True:
                    rows = procs.sample(limit=limit, sort_by="cpu")
                    table = process_table.build_table(rows, theme=theme)
                    live.update(table)
                    time.sleep(interval)
            except KeyboardInterrupt:
                console.print("\n[bold cyan]Exiting NeonHud top...[/]")
                sys.exit(0)

    # Fallback (should never happen with required=True)
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
