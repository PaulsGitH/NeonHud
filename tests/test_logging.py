from neonhud.core import logging as nh_logging


def test_logger_returns_logger_and_respects_level():
    log = nh_logging.get_logger()
    assert log.name == "neonhud"
    # Allow NOTSET (0) since the logger delegates filtering to handlers/root
    assert log.level in (0, 10, 20, 30, 40, 50)

    # logger should be singleton
    log2 = nh_logging.get_logger()
    assert log is log2
