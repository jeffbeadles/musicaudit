import json
from pathlib import Path

from musicaudit.cli import main


def snapshot(path: Path, tracks: list[dict]):
    path.write_text(json.dumps({
        "schema": "musicaudit.snapshot.v1",
        "source": "test",
        "provider": "filesystem",
        "tracks": tracks,
        "playlists": [],
    }), encoding="utf-8")


def base_track():
    return {
        "persistent_id": "FS-one",
        "relative_path": "one.mp3",
        "name": "One",
        "artist": "Artist",
        "album": "Album",
        "album_artist": "",
        "comments": "S5",
        "bit_rate": 192,
        "embedded_has_artwork": False,
        "embedded_has_lyrics": False,
        "audio_readable": True,
    }


def test_snapshot_diff_distinguishes_added_metadata(capsys, tmp_path):
    old = tmp_path / "before.json"
    new = tmp_path / "after.json"

    before = base_track()
    after = dict(before)
    after["album_artist"] = "Artist"
    after["embedded_has_artwork"] = True
    after["embedded_has_lyrics"] = True

    snapshot(old, [before])
    snapshot(new, [after])

    code = main(["diff", "--old", str(old), "--new", str(new), "--format", "json"])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["album_artist_changes"] == 1
    assert payload["summary"]["album_artist_added"] == 1
    assert payload["summary"]["album_artist_modified"] == 0
    assert payload["summary"]["album_artist_removed"] == 0
    assert payload["summary"]["artwork_changes"] == 1
    assert payload["summary"]["artwork_added"] == 1
    assert payload["summary"]["artwork_removed"] == 0
    assert payload["summary"]["lyrics_changes"] == 1
    assert payload["summary"]["lyrics_added"] == 1
    assert payload["summary"]["lyrics_removed"] == 0


def test_snapshot_diff_distinguishes_modified_and_removed_metadata(capsys, tmp_path):
    old = tmp_path / "before.json"
    new = tmp_path / "after.json"

    before = base_track()
    before["album_artist"] = "Old Artist"
    before["embedded_has_artwork"] = True
    before["embedded_has_lyrics"] = True

    after = dict(before)
    after["album_artist"] = "New Artist"
    after["embedded_has_artwork"] = False
    after["embedded_has_lyrics"] = False

    snapshot(old, [before])
    snapshot(new, [after])

    code = main(["diff", "--old", str(old), "--new", str(new), "--terse"])
    captured = capsys.readouterr()

    assert code == 0
    assert "album_artist_added=0" in captured.out
    assert "album_artist_modified=1" in captured.out
    assert "album_artist_removed=0" in captured.out
    assert "artwork_added=0" in captured.out
    assert "artwork_removed=1" in captured.out
    assert "lyrics_added=0" in captured.out
    assert "lyrics_removed=1" in captured.out
