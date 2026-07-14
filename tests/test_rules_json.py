import json
from pathlib import Path
import re

from musicaudit.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "missing_album_artist.xml"


def test_missing_album_artist_json_is_valid(capsys):
    code = main(
        [
            "rules",
            "--apple-library",
            str(FIXTURE),
            "--rule",
            "missing-album-artist",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()

    assert code == 0
    assert captured.err == ""

    payload = json.loads(captured.out)

    assert payload["status"] == "PASS"  # WARN only does not fail by default
    assert payload["rules"][0]["id"] == "missing-album-artist"
    assert payload["rules"][0]["count"] == 1
    assert payload["rules"][0]["items"][0]["album"] == "Compilation Album"


def test_verify_json_is_valid(capsys):
    code = main(
        [
            "verify",
            "--apple-library",
            str(FIXTURE),
            "--rule",
            "missing-album-artist",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["rules"][0]["id"] == "missing-album-artist"


# Make sure that all of the long_descriptions resolve.
def test_show_rules(capsys):
    code = main(
        [
            "rules",
            "--show-rules",
            "--apple-library",
            str(FIXTURE),
        ]
    )
    captured = capsys.readouterr()
    missing_ldescriptions = re.findall(
        r"^(.*): None$", captured.out, flags=re.MULTILINE
    )

    assert code == 0
    assert captured.err == ""
    assert not missing_ldescriptions, (
        f"Found multiple items missing values: {missing_ldescriptions}"
    )
