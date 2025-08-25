from neonhud.collectors import mem


def test_mem_sample_shape():
    data = mem.sample()
    assert isinstance(data, dict)

    for key in ("total", "used", "available", "percent"):
        assert key in data

    assert isinstance(data["total"], int)
    assert isinstance(data["used"], int)
    assert isinstance(data["available"], int)
    assert isinstance(data["percent"], float)

    # sanity
    assert data["total"] >= data["used"] >= 0
    assert data["available"] >= 0
    assert 0.0 <= data["percent"] <= 100.0
