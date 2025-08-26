from neonhud.core import config


def test_default_config_loads():
    cfg = config.load_config()
    assert isinstance(cfg, dict)
    assert "theme" in cfg
    assert "refresh_interval" in cfg
    assert "process_limit" in cfg
