import sys
import subprocess


def test_cli_pro_runs_help():
    # Ensure the command is registered and help renders
    cmd = [sys.executable, "-m", "neonhud.cli", "pro", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "neonhud pro" in proc.stdout or "gtop-style" in proc.stdout
