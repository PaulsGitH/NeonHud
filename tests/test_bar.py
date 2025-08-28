from neonhud.utils.bar import make_bar


def test_make_bar_bounds_and_width():
    assert len(make_bar(0, width=10)) == 10
    assert len(make_bar(100, width=10)) == 10
    assert len(make_bar(37, width=10)) == 10

    # clamps
    assert len(make_bar(-50, width=8)) == 8
    assert len(make_bar(250, width=8)) == 8
