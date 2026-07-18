import json
from pathlib import Path

from musicaudit.cli import main


def snapshot(path: Path, tracks: list[dict]):
    payload = {
        "schema": "musicaudit.snapshot.v1",
        "source": "test",
        "provider": "filesystem",
        "tracks": tracks,
        "playlists": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_snapshot_json_from_fixture_is_valid(capsys):
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests" / "fixtures" / "sample_library.xml"

    code = main(["snapshot", "--apple-library", str(fixture)])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["schema"] == "musicaudit.snapshot.v1"
    assert payload["provider"] == "apple-library"
    assert payload["summary"]["tracks"] == 6
    assert len(payload["tracks"]) == 6


def test_diff_accepts_snapshot_json(capsys, tmp_path):
    old = tmp_path / "before.json"
    new = tmp_path / "after.json"

    base = {
        "persistent_id": "FS-abc",
        "track_id": "1",
        "relative_path": "Artist/Album/song.mp3",
        "path": "/old/Artist/Album/song.mp3",
        "name": "Song",
        "artist": "Artist",
        "album_artist": "Artist",
        "album": "Album",
        "comments": "S4",
        "bit_rate": 192,
        "embedded_has_artwork": False,
        "embedded_has_lyrics": False,
        "audio_readable": True,
    }
    changed = dict(base)
    changed.update(
        {
            "path": "/new/Artist/Album/song.mp3",
            "comments": "S5 FAV",
            "bit_rate": 256,
            "embedded_has_artwork": True,
        }
    )

    snapshot(old, [base])
    snapshot(new, [changed])

    code = main(["diff", "--old", str(old), "--new", str(new), "--format", "json"])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "CHANGES"
    assert payload["summary"]["rating_changes_existing"] == 1
    assert payload["summary"]["fav_changes_existing"] == 1
    assert payload["summary"]["comment_changes"] == 1
    assert payload["summary"]["bitrate_changes"] == 1
    assert payload["summary"]["artwork_changes"] == 1
    assert payload["summary"]["artwork_added"] == 1
    # Different absolute roots should not be path changes when relative paths match.
    assert payload["summary"]["path_changes"] == 0


def test_diff_identical_snapshot_json_has_no_changes(capsys, tmp_path):
    old = tmp_path / "before.json"
    new = tmp_path / "after.json"
    tracks = [
        {
            "persistent_id": "FS-one",
            "relative_path": "one.mp3",
            "name": "One",
            "artist": "Artist",
            "album": "Album",
            "comments": "S5",
            "bit_rate": 192,
            "embedded_has_artwork": True,
        }
    ]
    snapshot(old, tracks)
    snapshot(new, tracks)

    code = main(["diff", "--old", str(old), "--new", str(new), "--terse"])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out.startswith("NO CHANGES")
