from neonhud.collectors import cpu, mem, procs


def test_collectors_emit_debug_and_return_data(caplog):
    caplog.set_level("DEBUG")

    c = cpu.sample()
    m = mem.sample()
    p = procs.sample(limit=5)

    # shape assertions
    assert "percent_total" in c
    assert "percent" in m
    assert isinstance(p, list)

    # emitted logs
    msgs = [rec.message for rec in caplog.records]
    assert any("CPU sample:" in m for m in msgs)
    assert any("Memory sample:" in m for m in msgs)
    assert any("Processes collected:" in m for m in msgs)
