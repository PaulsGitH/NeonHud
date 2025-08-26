from neonhud.collectors import procs
from neonhud.ui import process_table


def test_process_table_renders_text():
    rows = procs.sample(limit=5, sort_by="cpu")
    text = process_table.render_to_str(rows)
    assert isinstance(text, str)
    # Basic invariants: headers should be present
    assert "PID" in text
    assert "NAME" in text
    assert "CMDLINE" in text
    assert "CPU%" in text
    assert "RSS" in text
