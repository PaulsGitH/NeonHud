"""
NeonHud CLI entrypoint.
"""

from __future__ import annotations

import argparse
import sys
import time

from rich.console import Console
from rich.live import Live

from neonhud.models import snapshot
from neonhud.collectors import procs
from neonhud.ui import process_table


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
        "--interval", type=float, default=2.0, help="Refresh interval in seconds"
    )
    top_parser.add_argument(
        "--limit", type=int, default=15, help="Number of processes to show"
    )

    args = parser.parse_args(argv)

    if args.command == "report":
        import json

        snap = snapshot.build()
        if args.pretty:
            print(json.dumps(snap, indent=2))
        else:
            print(json.dumps(snap))
        return

    if args.command == "top":
        console = Console()
        with Live(console=console, refresh_per_second=4) as live:
            try:
                while True:
                    rows = procs.sample(limit=args.limit, sort_by="cpu")
                    table = process_table.build_table(rows)
                    live.update(table)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                console.print("\n[bold cyan]Exiting NeonHud top...[/]")
                sys.exit(0)

    # Fallback (should never happen with required=True)
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
