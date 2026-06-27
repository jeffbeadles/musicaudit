import pytest

from musicaudit.cli import main


def test_xml_option_removed(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["health", "--xml", "Library.xml"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err
    assert "--xml" in captured.err


def test_apple_library_missing_is_friendly(capsys, tmp_path):
    missing = tmp_path / "missing.xml"
    code = main(["health", "--apple-library", str(missing)])
    captured = capsys.readouterr()
    assert code == 2
    assert "XML file not found" in captured.err
    assert "Traceback" not in captured.err


def test_path_implies_filesystem_provider(capsys, tmp_path):
    music = tmp_path / "music"
    music.mkdir()

    code = main(["rules", "--path", str(music), "--terse"])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out.startswith("PASS")
