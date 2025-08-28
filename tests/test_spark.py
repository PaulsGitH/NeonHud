from neonhud.utils.spark import sparkline, DEFAULT_CHARS


def test_sparkline_basic_and_width():
    vals = [0, 1, 2, 3, 2, 1]
    s = sparkline(vals, DEFAULT_CHARS, max_width=4)
    assert isinstance(s, str)
    assert len(s) == 4  # truncated to last 4 points


def test_sparkline_zeroes_is_empty():
    assert sparkline([0, 0, 0]) == ""
    assert sparkline([]) == ""


def test_sparkline_monotonic_maps_full_range():
    # Increasing sequence should cover most of the ramp
    vals = [1, 2, 3, 4, 5, 6, 7, 8]
    s = sparkline(vals)
    assert len(s) == len(vals)
    assert s[-1] == DEFAULT_CHARS[-1]  # last should hit top glyph
