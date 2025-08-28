#!/usr/bin/env sh
set -e

# Default log level if not provided
: "${NEONHUD_LOG_LEVEL:=INFO}"
export NEONHUD_LOG_LEVEL

# Pass all args to the CLI (e.g., "dash --interval 1")
exec neonhud "$@"
