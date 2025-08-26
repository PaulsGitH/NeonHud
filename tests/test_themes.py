from neonhud.ui import themes


def test_get_theme_default_and_custom():
    # Should return a Theme
    t = themes.get_theme()
    assert isinstance(t, themes.Theme)
    assert t.name in ("classic", "cyberpunk")

    # Explicit by name
    t2 = themes.get_theme("cyberpunk")
    assert t2.name == "cyberpunk"

    # Invalid name falls back
    t3 = themes.get_theme("doesnotexist")
    assert t3.name in ("classic", "cyberpunk")
