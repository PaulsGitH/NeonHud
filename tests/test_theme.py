from neonhud.ui import theme


def test_get_theme_known_and_unknown():
    th = theme.get_theme("cyberpunk")
    assert th.primary == "bold magenta"
    assert th.accent == "cyan"

    default = theme.get_theme("unknown")
    assert default == theme.CLASSIC
