import shutil
import subprocess
import json
from pathlib import Path

import pytest

from musicaudit.cli import main


def make_mp3(path: Path, title: str, comment: str = "S5"):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not installed")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
        "-b:a", "128k",
        "-metadata", f"title={title}",
        "-metadata", "artist=Artist",
        "-metadata", "album=Album",
        "-metadata", f"comment={comment}",
        str(path),
    ], check=True)


def test_missing_artwork_json_items_are_tracks(tmp_path, capsys):
    music = tmp_path / "music"
    music.mkdir()
    make_mp3(music / "missing-artwork.mp3", "Missing Artwork")

    code = main([
        "rules",
        "--path", str(music),
        "--rule", "missing-artwork",
        "--format", "json",
    ])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    rule = payload["rules"][0]

    assert rule["id"] == "missing-artwork"
    assert rule["count"] == 1
    assert rule["items"] != [None]
    assert rule["items"][0]["name"] == "Missing Artwork"
    assert rule["items"][0]["path"].endswith("missing-artwork.mp3")


def test_missing_lyrics_json_items_are_tracks(tmp_path, capsys):
    music = tmp_path / "music"
    music.mkdir()
    make_mp3(music / "missing-lyrics.mp3", "Missing Lyrics")

    code = main([
        "rules",
        "--path", str(music),
        "--rule", "missing-lyrics",
        "--format", "json",
    ])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    rule = payload["rules"][0]

    assert rule["id"] == "missing-lyrics"
    assert rule["count"] == 1
    assert rule["items"] != [None]
    assert rule["items"][0]["name"] == "Missing Lyrics"
