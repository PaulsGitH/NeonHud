from neonhud.ui import panels
from neonhud.ui.themes import get_theme


def test_panels_render_overview_text():
    cpu = {"percent_total": 42.0, "per_cpu": [40.0, 44.0]}
    mem = {
        "total": 1024 * 1024 * 1024,
        "used": 512 * 1024 * 1024,
        "available": 512 * 1024 * 1024,
        "percent": 50.0,
    }

    th = get_theme("classic")
    text = panels.render_overview_to_str(cpu, mem, th)

    assert isinstance(text, str)
    assert "CPU" in text
    assert "Memory" in text
    # Should include the percent strings
    assert "42.0%" in text or "42.0 %" in text
    assert "50.0%" in text or "50.0 %" in text
