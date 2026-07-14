from __future__ import annotations

from .common import add_common_args, add_detail_args, apply_settings, load_library
from ..providers.audio import require_mutagen
from ..analysis import audit_core
from ..rules.engine import run_rules, find_rules, rule_long_descriptions
from ..reports.markdown import rules_report
from ..reports.json import rules_json_report
from ..util.formatting import write_or_print


def run(args) -> int:
    if getattr(args, "show_rules", False):
        print("Rules and a description of what they do")
        for key, value in rule_long_descriptions().items():
            print(f"{key:<20}: {value}")

        return 0

    if args.scan_files:
        require_mutagen()
    library = load_library(args)
    if getattr(args, "provider", None) == "filesystem":
        args.scan_files = True
    args = apply_settings(args, library)
    enabled_rules = args.rule or library.config.get("enabled_rules")
    if getattr(args, "show_config", False):
        print("Warning - This option is deprecated and will be going away")
        print(f"Library={library.xml_path}")
        print(f"low_bitrate={args.low_bitrate}")
        print(f"low_bitrate_source={getattr(args, 'low_bitrate_source', 'default')}")
        print(f"config_low_bitrate={library.config.get('low_bitrate', '-')}")
        rules_cfg = library.config.get("rules", {}) or {}
        print(f"rule_low_bitrate_config={rules_cfg.get('low-bitrate', {})}")

        rulelist = find_rules(library)
        print(f"rule_list={rulelist}")
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
    if args.format == "json":
        report, code = rules_json_report(library, results, args.fail_warnings)
    else:
        report, code = rules_report(
            library, results, args.max_details, args.fail_warnings, args.terse
        )
    write_or_print(report, args.output)
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
    p.add_argument(
        "--show-rules",
        action="store_true",
        help="Show all rules and exit.",
    )
    p.add_argument(
        "--show-config",
        action="store_true",
        help="Show resolved configuration and exit (deprecated).",
    )
    p.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    p.set_defaults(func=run)
