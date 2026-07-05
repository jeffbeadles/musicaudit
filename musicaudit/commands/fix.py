from .common import add_common_args, add_detail_args
from ..util.formatting import write_or_print


def run(args) -> int:
    write_or_print("""
NOTICE: musicaudit is intentionally read-only.

This command exists to document a project contract:
 -> musicaudit will never modify your music collection.

Use 'verify', 'rules', 'summary', or 'diff' to identify issues.
Use other tools to make changes.

""")
    return 1


## Developers, See docs/philosophy.md for the rationale.


def register(sub):
    p = sub.add_parser("fix", help="fix command")
    add_common_args(p)
    add_detail_args(p)
    p.set_defaults(func=run)
