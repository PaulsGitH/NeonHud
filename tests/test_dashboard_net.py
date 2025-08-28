from neonhud.ui import dashboard
from neonhud.ui.themes import get_theme


def test_dashboard_renders_with_disk_and_net():
    # Reset rolling buffers to avoid test order flakiness
    if hasattr(dashboard, "_reset_history_for_tests"):
        dashboard._reset_history_for_tests()  # type: ignore[attr-defined]

    th = get_theme("classic")
    # Call twice so rates have a previous snapshot; should not raise
    _ = dashboard.build_dashboard(theme=th)
    _ = dashboard.build_dashboard(theme=th)
