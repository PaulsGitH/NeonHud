"""
NeonHud CLI entrypoint.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from rich.console import Console
from rich.live import Live

from neonhud.core import config as core_config
from neonhud.core.logging import get_logger
from neonhud.models import snapshot
from neonhud.collectors import procs
from neonhud.ui.theme import get_theme
from neonhud.ui import process_table, dashboard

log = get_logger()


def run(argv: list[str] | None = None) -> None:
    """
    Main CLI dispatcher (wrapped by error-handling in __main__).
    """
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
        "--theme",
        type=str,
        default=None,
        help="Theme name (overrides config)",
    )

    # `neonhud dash`
    dash_parser = subparsers.add_parser(
        "dash", help="Interactive Rich dashboard (CPU + Memory)"
    )
    dash_parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Refresh interval in seconds (overrides config)",
    )
    dash_parser.add_argument(
        "--theme",
        type=str,
        default=None,
        help="Theme name (overrides config)",
    )

    args = parser.parse_args(argv)

    if args.command == "report":
        log.info("Running report subcommand")
        snap = snapshot.build()
        if args.pretty:
            print(json.dumps(snap, indent=2))
        else:
            print(json.dumps(snap))
        log.info("Report complete")
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
            args.theme if args.theme is not None else str(cfg.get("theme", "classic"))
        )
        theme = get_theme(theme_name)

        console = Console()
        log.info(
            "Starting live process view (top) interval=%.2fs limit=%d theme=%s",
            interval,
            limit,
            theme_name,
        )
        with Live(console=console, refresh_per_second=8) as live:
            try:
                while True:
                    rows = procs.sample(limit=limit, sort_by="cpu")
                    table = process_table.build_table(rows, theme=theme)
                    live.update(table)
                    time.sleep(interval)
            except KeyboardInterrupt:
                console.print("\n[bold cyan]Exiting NeonHud top...[/]")
                log.info("Exiting process view")
                sys.exit(0)

        return

    if args.command == "dash":
        cfg = core_config.load_config()
        interval = (
            args.interval
            if args.interval is not None
            else float(cfg.get("refresh_interval", 2.0))
        )
        theme_name = (
            args.theme if args.theme is not None else str(cfg.get("theme", "classic"))
        )
        theme = get_theme(theme_name)

        console = Console()
        log.info(
            "Starting live dashboard view interval=%.2fs theme=%s", interval, theme_name
        )
        with Live(console=console, refresh_per_second=8) as live:
            try:
                while True:
                    live.update(dashboard.build_dashboard(theme=theme))
                    time.sleep(interval)
            except KeyboardInterrupt:
                console.print("\n[bold cyan]Exiting NeonHud dashboard...[/]")
                log.info("Exiting dashboard view")
                sys.exit(0)

        return

    # Fallback (should never happen with required=True)
    parser.print_help()
    sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    """
    Entry point with error handling.
    """
    log = get_logger()  # root app logger
    try:
        run(argv)
    except Exception as e:
        log.exception("Fatal error in NeonHud CLI: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
