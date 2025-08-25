from importlib import import_module


def test_cli_imports():
    mod = import_module("neonhud.cli")
    assert hasattr(mod, "main")
