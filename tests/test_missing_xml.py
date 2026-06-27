from musicaudit.cli import main


def test_missing_xml_reports_error_without_traceback(capsys, tmp_path):
    missing = tmp_path / "does_not_exist.xml"

    code = main(["health", "--apple-library", str(missing)])
    captured = capsys.readouterr()

    assert code == 2
    assert "ERROR:" in captured.err
    assert "XML file not found" in captured.err
    assert str(missing) in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_missing_xml_rules_reports_error_without_traceback(capsys, tmp_path):
    missing = tmp_path / "missing_library.xml"

    code = main(["rules", "--apple-library", str(missing)])
    captured = capsys.readouterr()

    assert code == 2
    assert "ERROR:" in captured.err
    assert "XML file not found" in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out
