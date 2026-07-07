from __future__ import annotations

from .common import add_common_args, add_detail_args, apply_settings, load_library
from ..analysis import audit_core
from ..reports.markdown import tokens_report
from ..util.formatting import write_or_print


def run(args) -> int:
    library = load_library(args)
    args = apply_settings(args, library)
    core = audit_core(library, False, 256)
    return write_or_print(tokens_report(library, core, args.max_details), args.output)


def register(sub):
    p = sub.add_parser("tokens", help="Comment-token audit.")
    add_common_args(p)
    add_detail_args(p)
    p.set_defaults(func=run)
