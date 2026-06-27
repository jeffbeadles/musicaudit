from __future__ import annotations

from .common import add_common_args, add_detail_args, apply_settings, load_library
from ..analysis import audit_core
from ..reports.markdown import stats_report
from ..util.formatting import write_or_print


def run(args) -> int:
    library = load_library(args)
    args = apply_settings(args, library)
    core = audit_core(library, False, args.low_bitrate)
    return write_or_print(stats_report(library, core, args.max_details, args.histogram_scale, args.histogram_width), args.markdown)


def register(sub):
    p = sub.add_parser("stats", help="Collector-oriented statistics.")
    add_common_args(p)
    add_detail_args(p)
    p.add_argument("--low-bitrate", type=int, default=None)
    p.add_argument("--histogram-scale", choices=["sqrt", "log", "linear"], default="sqrt")
    p.add_argument("--histogram-width", type=int, default=40)
    p.set_defaults(func=run)
