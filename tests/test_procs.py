from neonhud.collectors import procs


def test_procs_sample_shape_and_types():
    rows = procs.sample(limit=10, sort_by="cpu")
    assert isinstance(rows, list)

    # It's possible on extremely constrained environments to get 0 rows,
    # but in normal systems we expect at least 1.
    if rows:
        row = rows[0]
        # Required keys
        for k in ("pid", "name", "cmdline", "cpu_percent", "rss_bytes"):
            assert k in row

        assert isinstance(row["pid"], int)
        assert isinstance(row["name"], str)
        assert isinstance(row["cmdline"], str)
        assert isinstance(row["cpu_percent"], float)
        assert isinstance(row["rss_bytes"], int)

        # sanity
        assert row["pid"] >= 0
        assert 0.0 <= row["cpu_percent"] <= 100.0
        assert row["rss_bytes"] >= 0

    # Check alternative sort
    rows_rss = procs.sample(limit=5, sort_by="rss")
    assert isinstance(rows_rss, list)
