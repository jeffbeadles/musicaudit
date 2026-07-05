import pytest

from musicaudit.cli import build_parser, main


def test_top_level_help_runs(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "musicaudit" in capsys.readouterr().out


def test_command_help_runs(capsys):
    for command in [
        "health",
        "summary",
        "tokens",
        "playlists",
        "stats",
        "rules",
        "verify",
        "diff",
    ]:
        with pytest.raises(SystemExit) as exc:
            main([command, "--help"])
        assert exc.value.code == 0
        assert command in capsys.readouterr().out


def test_version_runs(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "musicaudit" in capsys.readouterr().out


def test_parser_builds_all_commands():
    parser = build_parser()
    subparser_action = next(
        action
        for action in parser._actions
        if action.__class__.__name__ == "_SubParsersAction"
    )
    commands = set(subparser_action.choices)
    assert {
        "health",
        "summary",
        "tokens",
        "playlists",
        "stats",
        "rules",
        "verify",
        "diff",
    } <= commands
