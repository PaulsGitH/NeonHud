from neonhud.ui import dashboard
from neonhud.ui.themes import get_theme


def test_dashboard_renders_with_live_collectors():
    th = get_theme("classic")
    text = dashboard.render_dashboard_to_str(th)

    assert isinstance(text, str)
    # CPU and Memory headers should appear
    assert "CPU" in text
    assert "Memory" in text
