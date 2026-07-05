from pathlib import Path

from musicaudit.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_library.xml"
FIXTURE_AFTER = ROOT / "tests" / "fixtures" / "sample_library_after.xml"


def run_main(args, capsys):
    code = main(args)
    output = capsys.readouterr().out
    return code, output


def test_health_fixture_reports_expected_counts(capsys):
    code, output = run_main(["health", "--apple-library", str(FIXTURE)], capsys)
    assert code == 0
    assert "Songs: 6" in output
    assert "Missing S# ratings: 1" in output
    assert "Empty smart playlists: 1" in output
    assert "Empty standard playlists: 1" in output


def test_rules_fixture_reports_expected_failures(capsys):
    code, output = run_main(
        [
            "rules",
            "--apple-library",
            str(FIXTURE),
            "--rule",
            "missing-rating",
            "--rule",
            "unknown-token",
            "--rule",
            "duplicate-track",
        ],
        capsys,
    )
    assert code == 0
    assert "| `missing-rating` | ERROR | ERROR | 1 |" in output
    assert "| `unknown-token` | WARN | WARN | 1 |" in output
    assert "| `duplicate-track` | WARN | WARN | 1 |" in output


def test_rules_terse_fixture(capsys):
    code, output = run_main(
        [
            "rules",
            "--apple-library",
            str(FIXTURE),
            "--rule",
            "missing-rating",
            "--terse",
        ],
        capsys,
    )
    assert code == 0
    assert output.startswith("FAIL")
    assert "missing_rating=1" in output


def test_low_bitrate_fixture_config_file(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        f"apple_library_xml: {FIXTURE}\nrules:\n  low-bitrate:\n    minimum: 12\n",
        encoding="utf-8",
    )

    code, output = run_main(
        [
            "rules",
            "--apple-library",
            str(FIXTURE),
            "--config",
            str(cfg),
            "--rule",
            "low-bitrate",
            "--show-config",
        ],
        capsys,
    )
    assert code == 0
    assert "low_bitrate=12" in output
    assert "low_bitrate_source=rule" in output

    code, output = run_main(
        [
            "rules",
            "--apple-library",
            str(FIXTURE),
            "--config",
            str(cfg),
            "--rule",
            "low-bitrate",
            "--terse",
        ],
        capsys,
    )
    assert code == 0
    assert "low_bitrate=0" in output


def test_diff_reports_new_favorite(capsys):
    code, output = run_main(
        ["diff", "--old", str(FIXTURE), "--new", str(FIXTURE_AFTER)], capsys
    )
    assert code == 0
    assert "New songs with FAV: 1" in output
    assert "New Favorite" in output


def test_verify_alias_runs_on_fixture(capsys):
    code, output = run_main(
        [
            "verify",
            "--apple-library",
            str(FIXTURE),
            "--rule",
            "missing-rating",
            "--terse",
        ],
        capsys,
    )
    assert code == 0
    assert output.startswith("FAIL")
    assert "missing_rating=1" in output
