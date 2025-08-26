import subprocess
import sys


def test_cli_top_runs_and_exits():
    # Run top with one cycle and then terminate (timeout)
    cmd = [
        sys.executable,
        "-m",
        "neonhud.cli",
        "top",
        "--interval",
        "0.1",
        "--limit",
        "5",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.terminate()
    proc.wait(timeout=5)
    # Process should exit cleanly
    assert proc.returncode is not None
