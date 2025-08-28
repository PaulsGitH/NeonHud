from neonhud.collectors import net


def test_net_counters_shape():
    c = net.sample_counters()
    assert "ts" in c and "bytes_sent" in c and "bytes_recv" in c
    assert isinstance(c["ts"], float)
    assert isinstance(c["bytes_sent"], int)
    assert isinstance(c["bytes_recv"], int)


def test_net_rates_from_prev_curr():
    prev = {"ts": 10.0, "bytes_sent": 500, "bytes_recv": 1200}
    curr = {"ts": 13.0, "bytes_sent": 1100, "bytes_recv": 1500}
    r = net.rates_from(prev, curr)
    assert r["interval"] == 3.0
    # tx: (1100-500)/3 = 200; rx: (1500-1200)/3 = 100
    assert abs(r["tx_bps"] - 200.0) < 1e-6
    assert abs(r["rx_bps"] - 100.0) < 1e-6


def test_net_zero_interval_safe():
    r = net.rates_from(
        {"ts": 1.0, "bytes_sent": 0, "bytes_recv": 0},
        {"ts": 1.0, "bytes_sent": 1, "bytes_recv": 1},
    )
    assert r["interval"] == 0.0
    assert r["tx_bps"] == 0.0 and r["rx_bps"] == 0.0
