from __future__ import annotations

import os
import sys
from pathlib import Path


def fmt_int(n) -> str:
    return f"{n:,}"


def fmt_percent(part, total) -> str:
    if not total:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"


def write_or_print(report: str, markdown_path=None) -> int:
    if markdown_path:
        path = Path(markdown_path).expanduser()
        path.write_text(report, encoding="utf-8")
        return 0

    try:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
    except BrokenPipeError:
        # Normal Unix pipeline behavior: downstream command exited early.
        # Redirect stdout to /dev/null so interpreter shutdown does not try
        # to flush the already-broken stream and emit another warning.
        try:
            sys.stdout = open(os.devnull, "w")
        except Exception:
            pass
        return 0

    return 0
