from __future__ import annotations

from ..providers.applemusic import load_library as load_applemusic_library
from ..providers.filesystem import load_filesystem_library
from ..analysis import audit_core
from ..util.formatting import write_or_print


def add_common_args(parser):
    parser.add_argument("--config", help="Optional config file.")
    parser.add_argument("--provider", choices=["applemusic", "filesystem"], default=None, help="Library provider. Usually inferred from --apple-library or --path.")
    parser.add_argument("--apple-library", dest="apple_library", help="Path to exported Apple Music/iTunes Library XML file.")
    parser.add_argument("--path", help="Path to a music directory. Implies --provider filesystem.")
    parser.add_argument("--markdown", "-o", help="Optional Markdown report output path.")
    parser.add_argument("--known-token", action="append", default=[], help="Additional valid comment token.")


def add_detail_args(parser):
    parser.add_argument("--max-details", type=int, default=None, help="Maximum detailed rows per section. Use 0 to suppress details.")
    parser.add_argument("--verbose", action="store_true", help="Shortcut for --max-details 100.")


def apply_settings(args, library):
    settings = library.settings
    args.low_bitrate = settings.low_bitrate
    args.low_bitrate_source = settings.low_bitrate_source
    args.max_details = settings.max_details
    if getattr(args, "bitrate_report", None) is None:
        args.bitrate_report = settings.bitrate_report
    return args


def resolve_provider(args):
    provider = getattr(args, "provider", None)
    has_path = bool(getattr(args, "path", None))
    has_apple_library = bool(getattr(args, "apple_library", None))

    if has_path and has_apple_library:
        raise RuntimeError("Specify only one library input: --apple-library or --path.")

    if provider:
        return provider
    if has_path:
        return "filesystem"
    return "applemusic"


def load_library(args):
    provider = resolve_provider(args)
    args.provider = provider
    if provider == "filesystem":
        return load_filesystem_library(args)
    return load_applemusic_library(args)
