from neonhud.ui import process_table
from neonhud.ui.themes import Theme


def test_process_table_uses_theme_header_style():
    # Minimal fake rows to avoid depending on live system load
    rows = [
        {
            "pid": 1,
            "name": "init",
            "cmdline": "init",
            "cpu_percent": 0.0,
            "rss_bytes": 1024,
        },
        {
            "pid": 2,
            "name": "worker",
            "cmdline": "worker --task",
            "cpu_percent": 95.0,
            "rss_bytes": 2048,
        },
    ]

    th = Theme(
        name="test",
        primary="bold magenta",
        accent="cyan",
        warning="yellow",
        background="black",
    )
    table = process_table.build_table(rows, theme=th)

    # Header style should match theme.primary
    for col in table.columns:
        assert col.header_style == th.primary
