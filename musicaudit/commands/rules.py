from __future__ import annotations

from .common import add_common_args, add_detail_args, apply_settings
from ..providers.applemusic import load_library
from ..providers.audio import require_mutagen
from ..analysis import audit_core
from ..rules.engine import run_rules
from ..reports.markdown import rules_report
from ..util.formatting import write_or_print


def run(args) -> int:
    if args.scan_files:
        require_mutagen()
    library = load_library(args)
    args = apply_settings(args, library)
    enabled_rules = args.rule or library.config.get("enabled_rules")
    if getattr(args, "show_config", False):
        print(f"library_xml={library.xml_path}")
        print(f"low_bitrate={args.low_bitrate}")
        print(f"low_bitrate_source={getattr(args, 'low_bitrate_source', 'default')}")
        print(f"config_low_bitrate={library.config.get('low_bitrate', '-')}")
        rules_cfg = library.config.get("rules", {}) or {}
        print(f"rule_low_bitrate_config={rules_cfg.get('low-bitrate', {})}")
        return 0

    core = audit_core(library, args.scan_files, args.low_bitrate)
    results = run_rules(
        library,
        core,
        args.scan_files,
        args.low_bitrate,
        enabled_rules,
        low_bitrate_source=args.low_bitrate_source,
    )
    report, code = rules_report(library, results, args.max_details, args.fail_warnings, args.terse)
    write_or_print(report, args.markdown)
    return code if args.strict else 0


def register(sub):
    p = sub.add_parser("rules", help="Run built-in music library QA rules.")
    add_common_args(p)
    add_detail_args(p)
    p.add_argument("--scan-files", action="store_true")
    p.add_argument("--low-bitrate", type=int, default=None)
    p.add_argument("--terse", action="store_true")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--fail-warnings", action="store_true")
    p.add_argument("--rule", action="append")
    p.add_argument("--show-config", action="store_true", help="Show resolved configuration and exit.")
    p.set_defaults(func=run)
