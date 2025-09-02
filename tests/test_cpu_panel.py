from rich.console import Console
from neonhud.ui import panels
from neonhud.ui.theme import get_theme


def test_cpu_panel_renders_per_core():
    fake_cpu = {"percent_total": 55.0, "per_core": [10.0, 50.0, 90.0]}
    panel = panels.build_cpu_panel(fake_cpu, theme=get_theme("cyberpunk"))

    console = Console(record=True, width=80)
    console.print(panel)
    text = console.export_text()

    assert "Core 0" in text
    assert "Core 1" in text
    assert "Core 2" in text
