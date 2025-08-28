import subprocess
import sys


def test_cli_invalid_command_exits_cleanly():
    # Run with invalid subcommand, should exit nonzero
    cmd = [sys.executable, "-m", "neonhud.cli", "doesnotexist"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.returncode != 0
    # stderr should mention "usage"
    assert b"usage:" in proc.stderr or b"usage:" in proc.stdout
