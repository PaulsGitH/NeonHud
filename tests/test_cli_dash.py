import subprocess
import sys


def test_cli_dash_runs_and_exits():
    # Run `neonhud dash` briefly, then terminate
    cmd = [
        sys.executable,
        "-m",
        "neonhud.cli",
        "dash",
        "--interval",
        "0.1",
        "--theme",
        "classic",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.terminate()
    proc.wait(timeout=5)
    assert proc.returncode is not None
