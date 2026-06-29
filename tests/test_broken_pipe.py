import sys

from musicaudit.util.formatting import write_or_print


class BrokenStdout:
    def write(self, _text):
        raise BrokenPipeError()

    def flush(self):
        raise BrokenPipeError()


def test_broken_pipe_does_not_raise(monkeypatch):
    monkeypatch.setattr(sys, "stdout", BrokenStdout())

    code = write_or_print("large report\n")

    assert code == 0
