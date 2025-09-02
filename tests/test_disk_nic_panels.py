from rich.console import Console
from neonhud.ui import panels
from neonhud.ui.theme import get_theme


def test_disks_panel_renders_devices():
    fake = {
        "sda": {
            "read_bps": 1024.0,
            "write_bps": 2048.0,
            "hist_r": [0, 512, 1024],
            "hist_w": [0, 1024, 2048],
        },
        "nvme0n1": {
            "read_bps": 4096.0,
            "write_bps": 0.0,
            "hist_r": [2048, 4096],
            "hist_w": [0, 0],
        },
    }
    panel = panels.build_disks_panel(fake, theme=get_theme("cyberpunk"))
    c = Console(record=True, width=100)
    c.print(panel)
    txt = c.export_text()
    assert "sda" in txt
    assert "nvme0n1" in txt
    assert "KiB/s" in txt or "MiB/s" in txt


def test_nics_panel_renders_interfaces():
    fake = {
        "eth0": {
            "recv_bps": 5000.0,
            "send_bps": 1000.0,
            "hist_rx": [1000, 2000, 5000],
            "hist_tx": [500, 800, 1000],
        },
        "wlan0": {"recv_bps": 0.0, "send_bps": 0.0, "hist_rx": [0], "hist_tx": [0]},
    }
    panel = panels.build_nics_panel(fake, theme=get_theme("cyberpunk"))
    c = Console(record=True, width=100)
    c.print(panel)
    txt = c.export_text()
    assert "eth0" in txt or "wlan0" in txt
    assert "RX" in txt and "TX" in txt
