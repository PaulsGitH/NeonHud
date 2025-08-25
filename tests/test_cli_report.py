import json
import subprocess
import sys


def test_cli_report_runs(tmp_path):
    # Run as module: python -m neonhud.cli report --pretty
    cmd = [sys.executable, "-m", "neonhud.cli", "report", "--pretty"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Must be valid JSON
    data = json.loads(proc.stdout)
    assert "schema" in data
    assert "cpu" in data
    assert "memory" in data
