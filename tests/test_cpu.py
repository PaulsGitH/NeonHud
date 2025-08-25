from neonhud.collectors import cpu


def test_cpu_sample_shape():
    data = cpu.sample()
    assert isinstance(data, dict)
    assert "percent_total" in data and "per_cpu" in data

    total = data["percent_total"]
    per_cpu = data["per_cpu"]

    assert isinstance(total, float)
    assert isinstance(per_cpu, list)
    assert len(per_cpu) >= 1
    assert all(isinstance(v, float) for v in per_cpu)

    # sanity ranges
    assert 0.0 <= total <= 100.0
    assert all(0.0 <= v <= 100.0 for v in per_cpu)
