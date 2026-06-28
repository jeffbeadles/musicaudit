import json
from pathlib import Path

from musicaudit.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_library.xml"
FIXTURE_AFTER = ROOT / "tests" / "fixtures" / "sample_library_after.xml"


def test_health_json_is_valid(capsys):
    code = main(["health", "--apple-library", str(FIXTURE), "--format", "json"])
    captured = capsys.readouterr()
    assert code in (0, 1)
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert "status" in payload
    assert payload["health"]["tracks"] == 6


def test_summary_json_is_valid(capsys):
    code = main(["summary", "--apple-library", str(FIXTURE), "--format", "json"])
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["health"]["tracks"] == 6
    assert "ratings" in payload
    assert "bitrates" in payload


def test_diff_json_is_valid(capsys):
    code = main(["diff", "--old", str(FIXTURE), "--new", str(FIXTURE_AFTER), "--format", "json"])
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "CHANGES"
    assert payload["summary"]["new_songs"] == 1
    assert payload["summary"]["new_favorites"] == 1


def test_stats_markdown_numbers_are_not_bold(capsys):
    code = main(["stats", "--apple-library", str(FIXTURE)])
    captured = capsys.readouterr()
    assert code == 0
    assert "**" not in captured.out
