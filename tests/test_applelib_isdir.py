from pathlib import Path

from musicaudit.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_applelib_is_a_directory(capsys):
    code = main(["health", "--apple-library", "."])

    assert code == 2
