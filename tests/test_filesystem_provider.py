import shutil
import subprocess
from pathlib import Path

import pytest

from musicaudit.cli import main


def make_mp3(path: Path, title: str, artist: str, album: str, comment: str, bitrate: str = "128k"):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not installed")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
        "-b:a", bitrate,
        "-metadata", f"title={title}",
        "-metadata", f"artist={artist}",
        "-metadata", f"album={album}",
        "-metadata", f"comment={comment}",
        str(path),
    ], check=True)


def test_filesystem_provider_rules(tmp_path, capsys):
    music = tmp_path / "music"
    music.mkdir()

    make_mp3(music / "good.mp3", "Good Song", "Artist A", "Album A", "S5", "128k")
    make_mp3(music / "missing-rating.mp3", "Missing Rating", "Artist B", "Album B", "", "128k")
    make_mp3(music / "low-bitrate.mp3", "Low Bitrate", "Artist C", "Album C", "S3", "32k")

    code = main([
        "rules",
        "--provider", "filesystem",
        "--path", str(music),
        "--low-bitrate", "64",
        "--rule", "missing-rating",
        "--rule", "low-bitrate",
        "--terse",
    ])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out.startswith("FAIL")
    assert "missing_rating=1" in captured.out
    assert "low_bitrate=1" in captured.out


def test_filesystem_provider_json(tmp_path, capsys):
    music = tmp_path / "music"
    music.mkdir()

    make_mp3(music / "track.mp3", "Track", "Artist", "Album", "S5", "128k")

    code = main([
        "rules",
        "--provider", "filesystem",
        "--path", str(music),
        "--rule", "missing-rating",
        "--format", "json",
    ])
    captured = capsys.readouterr()

    assert code == 0
    assert '"id": "missing-rating"' in captured.out
    assert '"count": 0' in captured.out
