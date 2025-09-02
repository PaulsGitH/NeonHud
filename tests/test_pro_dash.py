from neonhud.ui import pro_dash
from neonhud.ui.theme import get_theme


def test_build_top_renders_and_is_renderable():
    th = get_theme("classic")
    renderable = pro_dash.build_top(th)
    assert renderable is not None


def test_cpu_history_panel_includes_label():
    th = get_theme("classic")
    panel = pro_dash._cpu_history_panel(th)
    assert "CPU" in str(panel)


def test_mem_swap_history_panel_includes_labels():
    th = get_theme("classic")
    panel = pro_dash._mem_swap_history_panel(th)
    text = str(panel)
    assert "Memory" in text
    assert "Swap" in text
