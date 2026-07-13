import pytest

"""
Ensure regression tests never read the user's real configuration.
Tests must explicitly create any configuration they require.
"""


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    config_home = tmp_path / "config"
    config_home.mkdir()

    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.setenv("HOME", str(tmp_path))
