import json
from pathlib import Path

from musicaudit.cli import main


def test_snapshot_json_from_apple_library_is_valid(capsys):
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests" / "fixtures" / "sample_library.xml"

    code = main(["snapshot", "--apple-library", str(fixture)])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["schema"] == "musicaudit.snapshot.v1"
    assert payload["provider"] == "apple-library"


def test_snapshot_json_from_path_is_valid(capsys):
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests" / "reference-library"

    code = main(["snapshot", "--path", str(fixture)])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["schema"] == "musicaudit.snapshot.v1"
    assert payload["provider"] == "filesystem"
