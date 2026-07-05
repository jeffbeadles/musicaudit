import json
from pathlib import Path

from musicaudit.cli import main


def snapshot(path: Path, tracks: list[dict]):
    path.write_text(
        json.dumps(
            {
                "schema": "musicaudit.snapshot.v1",
                "source": "test",
                "provider": "filesystem",
                "tracks": tracks,
                "playlists": [],
            }
        ),
        encoding="utf-8",
    )


def base_track():
    return {
        "persistent_id": "FS-one",
        "relative_path": "one.mp3",
        "name": "Old Name",
        "artist": "Old Artist",
        "album": "Old Album",
        "album_artist": "Album Artist",
        "comments": "S5",
        "bit_rate": 192,
        "embedded_has_artwork": True,
        "embedded_has_lyrics": False,
        "audio_readable": True,
    }


def test_snapshot_diff_splits_title_artist_album_changes_json(capsys, tmp_path):
    old = tmp_path / "before.json"
    new = tmp_path / "after.json"

    before = base_track()
    after = dict(before)
    after["name"] = "New Name"
    after["artist"] = "New Artist"
    after["album"] = "New Album"

    snapshot(old, [before])
    snapshot(new, [after])

    code = main(["diff", "--old", str(old), "--new", str(new), "--format", "json"])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["title_artist_album_changes"] == 1
    assert payload["summary"]["track_name_changes"] == 1
    assert payload["summary"]["track_artist_changes"] == 1
    assert payload["summary"]["album_title_changes"] == 1
    assert len(payload["items"]["track_name_changes"]) == 1
    assert len(payload["items"]["track_artist_changes"]) == 1
    assert len(payload["items"]["album_title_changes"]) == 1


def test_snapshot_diff_splits_title_artist_album_changes_terse(capsys, tmp_path):
    old = tmp_path / "before.json"
    new = tmp_path / "after.json"

    before = base_track()
    after = dict(before)
    after["name"] = "New Name"

    snapshot(old, [before])
    snapshot(new, [after])

    code = main(["diff", "--old", str(old), "--new", str(new), "--terse"])
    captured = capsys.readouterr()

    assert code == 0
    assert "title_artist_album_changes=1" in captured.out
    assert "track_name_changes=1" in captured.out
    assert "track_artist_changes=0" in captured.out
    assert "album_title_changes=0" in captured.out
