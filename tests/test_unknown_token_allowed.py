from argparse import Namespace

from musicaudit.settings import resolve_settings
from musicaudit.cli import main


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


def test_unknown_token_allowed_is_added_to_known_tokens():
    config = {
        "rules": {
            "unknown-token": {
                "allowed": ["LIVE", "DEMO"]
            }
        }
    }

    settings = resolve_settings(args(), config)

    assert "LIVE" in settings.known_tokens
    assert "DEMO" in settings.known_tokens


def test_unknown_token_allowed_config_affects_cli_rule(tmp_path, capsys):
    fixture = __import__("pathlib").Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "sample_library.xml"
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        f"library_xml: {fixture}\n"
        "rules:\n"
        "  unknown-token:\n"
        "    allowed:\n"
        "      - LIVE\n",
        encoding="utf-8",
    )

    code = main(["rules", "--config", str(cfg), "--rule", "unknown-token", "--terse"])
    captured = capsys.readouterr()

    assert code == 0
    assert "unknown_token=0" in captured.out
