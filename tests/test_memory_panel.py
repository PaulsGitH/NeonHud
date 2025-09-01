# tests/test_memory_panel.py
from rich.console import Console
from neonhud.ui import panels
from neonhud.ui.theme import get_theme


def test_memory_panel_renders_with_used_and_total():
    fake_mem = {"percent": 42.0, "used": 4 * 1024**3, "total": 16 * 1024**3}
    panel = panels.build_memory_panel(fake_mem, theme=get_theme("cyberpunk"))

    console = Console(record=True, width=80)
    console.print(panel)
    text = console.export_text()

    assert "42.0%" in text or "42%" in text
    assert "Used:" in text
    assert "GiB" in text
