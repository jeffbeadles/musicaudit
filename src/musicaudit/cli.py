from __future__ import annotations

import argparse
from importlib.metadata import version

import sys

from .commands import (
    health,
    summary,
    tokens,
    playlists,
    stats,
    verify,
    diff,
    rules,
    snapshot,
    fix,
)


def build_parser() -> argparse.ArgumentParser:
    __version__ = version("musicaudit")
    parser = argparse.ArgumentParser(
        prog="musicaudit",
        description="Read-only music library QA toolkit for curated digital music collections.",
        epilog="Documentation: https://github.com/jeffbeadles/musicaudit",
    )
    parser.add_argument(
        "--version", action="version", version=f"musicaudit {__version__}"
    )

    sub = parser.add_subparsers(dest="command")

    health.register(sub)
    summary.register(sub)
    tokens.register(sub)
    playlists.register(sub)
    stats.register(sub)
    verify.register(sub)
    rules.register(sub)
    diff.register(sub)
    snapshot.register(sub)
    fix.register(sub)

    return parser


def main(argv=None) -> int:
    raw_args = argv if argv is not None else sys.argv[1:]
    parser = build_parser()

    if not raw_args:
        parser.print_help()
        return 2

    args = parser.parse_args(raw_args)
    if args.command is None:
        parser.print_help()
        return 2

    try:
        return args.func(args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
