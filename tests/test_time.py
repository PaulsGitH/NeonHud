from neonhud.utils import now_utc_iso


def test_now_utc_iso_format():
    s = now_utc_iso()
    # Simple structural checks
    assert s.endswith("Z")
    assert "T" in s
    # YYYY-MM-DDTHH:MM:SSZ -> length 20
    assert len(s) == 20
