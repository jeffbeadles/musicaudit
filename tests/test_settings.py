from argparse import Namespace

from musicaudit.settings import resolve_settings


def args(**kwargs):
    defaults = {
        "low_bitrate": None,
        "max_details": None,
        "verbose": False,
        "bitrate_report": None,
        "known_token": [],
        "rule": None,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_default_low_bitrate():
    s = resolve_settings(args(), {})
    assert s.low_bitrate == 256
    assert s.low_bitrate_source == "default"


def test_global_config_low_bitrate():
    s = resolve_settings(args(), {"low_bitrate": 128})
    assert s.low_bitrate == 128
    assert s.low_bitrate_source == "config"


def test_rule_minimum_low_bitrate():
    s = resolve_settings(args(), {"rules": {"low-bitrate": {"minimum": 12}}})
    assert s.low_bitrate == 12
    assert s.low_bitrate_source == "rule"


def test_rule_threshold_low_bitrate():
    s = resolve_settings(args(), {"rules": {"low-bitrate": {"threshold": 10}}})
    assert s.low_bitrate == 10
    assert s.low_bitrate_source == "rule"


def test_cli_overrides_rule_and_global_low_bitrate():
    s = resolve_settings(
        args(low_bitrate=64),
        {"low_bitrate": 128, "rules": {"low-bitrate": {"minimum": 12}}},
    )
    assert s.low_bitrate == 64
    assert s.low_bitrate_source == "cli"


def test_verbose_changes_max_details_default_only():
    s = resolve_settings(args(verbose=True), {})
    assert s.max_details == 100

    s = resolve_settings(args(verbose=True, max_details=7), {})
    assert s.max_details == 7
