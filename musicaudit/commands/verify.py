from __future__ import annotations

from .rules import run as rules_run
from .common import add_common_args, add_detail_args


def run(args) -> int:
    # verify is now a compatibility alias for rules.
    return rules_run(args)


def register(sub):
    p = sub.add_parser("verify", help="Compatibility alias for rules.")
    add_common_args(p)
    add_detail_args(p)
    p.add_argument("--scan-files", action="store_true")
    p.add_argument("--low-bitrate", type=int, default=None)
    p.add_argument("--terse", action="store_true")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--fail-warnings", action="store_true")
    p.add_argument("--rule", action="append")
    p.add_argument("--show-config", action="store_true", help="Show resolved configuration and exit.")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    p.set_defaults(func=run)
