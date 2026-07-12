from pathlib import Path

from musicaudit.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_library.xml"


def test_fix_command_is_intentionally_unsupported(capsys):
    rc = main(["fix", "--apple-library", str(FIXTURE)])

    out = capsys.readouterr().out

    assert rc != 0
    assert "read-only" in out
    assert "will never modify" in out
