import shutil
import subprocess
from pathlib import Path

import pytest

from musicaudit.cli import main


def make_mp3(path: Path, title: str, comment: str = "S5", bitrate: str = "192k"):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not installed")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
        "-b:a", bitrate,
        "-metadata", f"title={title}",
        "-metadata", "artist=Artist",
        "-metadata", "album=Album",
        "-metadata", f"comment={comment}",
        str(path),
    ], check=True)


def test_summary_bitrate_bucket_matches_low_bitrate_rule(tmp_path, capsys):
    music = tmp_path / "music"
    music.mkdir()

    for i in range(3):
        make_mp3(music / f"track-{i}.mp3", f"Track {i}", "S5", "192k")

    code = main([
        "rules",
        "--path", str(music),
        "--low-bitrate", "64",
        "--rule", "low-bitrate",
        "--format", "json",
    ])
    rules_out = capsys.readouterr().out
    assert code == 0
    assert '"count": 0' in rules_out

    code = main([
        "summary",
        "--path", str(music),
        "--low-bitrate", "64",
    ])
    summary_out = capsys.readouterr().out
    assert code == 0

    assert "Below 64 kbps: 0" not in summary_out
    assert "Below 64 kbps: 3" not in summary_out
    assert "64-255 kbps: 3" in summary_out


def test_summary_bitrate_bucket_reports_true_low_bitrate(tmp_path, capsys):
    music = tmp_path / "music"
    music.mkdir()

    make_mp3(music / "low.mp3", "Low", "S5", "32k")

    code = main([
        "summary",
        "--path", str(music),
        "--low-bitrate", "64",
    ])
    summary_out = capsys.readouterr().out
    assert code == 0
    assert "Below 64 kbps: 1" in summary_out
