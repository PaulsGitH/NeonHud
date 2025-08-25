"""
NeonHud CLI entrypoint.
"""

from __future__ import annotations

import argparse
import json
import sys

from neonhud.models import snapshot


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
        "--pretty",
        action="store_true",
        help="Pretty-print JSON with indentation",
    )

    args = parser.parse_args(argv)

    if args.command == "report":
        snap = snapshot.build()
        if args.pretty:
            print(json.dumps(snap, indent=2))
        else:
            print(json.dumps(snap))
        return

    # Fallback (should never happen with required=True)
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
