from __future__ import annotations

from .common import add_common_args, apply_settings, load_library
from ..analysis import audit_core
from ..reports.markdown import health_report, terse_health
from ..reports.json import health_json_report
from ..util.formatting import write_or_print


def run(args) -> int:
    library = load_library(args)
    if getattr(args, "provider", None) == "filesystem":
        args.scan_files = True
    args = apply_settings(args, library)
    core = audit_core(library, args.scan_files, args.low_bitrate)
    if args.format == "json":
        report, code = health_json_report(
            library, core, args.scan_files, args.low_bitrate
        )
        return write_or_print(report, args.markdown) or code

    report = (
        terse_health(library, core, args.scan_files, args.low_bitrate)
        if args.terse
        else health_report(library, core, args.scan_files, args.low_bitrate)
    )
    return write_or_print(report, args.markdown)


def register(sub):
    p = sub.add_parser("health", help="Compact health-check report.")
    add_common_args(p)
    p.add_argument("--scan-files", action="store_true")
    p.add_argument("--low-bitrate", type=int, default=None)
    p.add_argument("--terse", action="store_true")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.set_defaults(func=run)
