from __future__ import annotations

from .common import add_common_args, add_detail_args, apply_settings
from ..providers.applemusic import load_library
from ..providers.audio import require_mutagen
from ..analysis import audit_core
from ..reports.markdown import summary_report
from ..util.formatting import write_or_print


def run(args) -> int:
    if args.scan_files:
        require_mutagen()
    library = load_library(args)
    args = apply_settings(args, library)
    core = audit_core(library, args.scan_files, args.low_bitrate)
    report = summary_report(library, core, args.scan_files, args.bitrate_report, args.low_bitrate, args.max_details)
    return write_or_print(report, args.markdown)


def register(sub):
    p = sub.add_parser("summary", help="Full library audit report.")
    add_common_args(p)
    add_detail_args(p)
    p.add_argument("--scan-files", action="store_true")
    p.add_argument("--bitrate-report", choices=["summary", "full", "exceptions", "none"], default=None)
    p.add_argument("--low-bitrate", type=int, default=None)
    p.set_defaults(func=run)
