from neonhud.ui import pro_dash
from neonhud.ui.theme import get_theme


def test_build_top_renders():
    th = get_theme("classic")
    renderable = pro_dash.build_top(th)
    assert renderable is not None
