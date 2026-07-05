from __future__ import annotations

from ..providers.applemusic import load_library as load_applemusic_library
from ..providers.filesystem import load_filesystem_library


def add_common_args(parser):
    parser.add_argument("--config", help="Optional config file.")
    inputgroup = parser.add_mutually_exclusive_group(required=True)
    inputgroup.add_argument(
        "--apple-library",
        dest="apple_library",
        nargs="?",
        const="",
        default=None,
        help="Path to exported Apple Music/iTunes Library XML file.",
    )
    inputgroup.add_argument(
        "--path", nargs="?", const="", default=None, help="Path to a music directory."
    )
    parser.add_argument(
        "--markdown", "-o", help="Optional Markdown report output path."
    )
    parser.add_argument(
        "--known-token",
        action="append",
        default=[],
        help="Additional valid comment token.",
    )


def add_detail_args(parser):
    parser.add_argument(
        "--max-details",
        type=int,
        default=None,
        help="Maximum detailed rows per section. Use 0 to suppress details.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Shortcut for --max-details 100."
    )


def apply_settings(args, library):
    settings = library.settings
    args.low_bitrate = settings.low_bitrate
    args.low_bitrate_source = settings.low_bitrate_source
    args.max_details = settings.max_details
    if getattr(args, "bitrate_report", None) is None:
        args.bitrate_report = settings.bitrate_report
    return args


def resolve_provider(args):
    has_path = getattr(args, "path", None)
    has_apple_library = getattr(args, "apple_library", None)

    # Are both set?
    if (has_path is not None) and (has_apple_library is not None):
        # This should never happen, as the command line parser _should_ trap it,
        # but don't leave it to chance.
        raise RuntimeError("Specify only one input: --path or --apple-library.")

    if has_path is not None:
        return "filesystem"
    if has_apple_library is not None:
        return "applemusic"

    # This shouldn't be reached, as the command line parser should require
    #  one of the above to be set...  (but we still check anyway)
    raise RuntimeError("Missing input, specify: --path or --apple-library.")


def load_library(args):
    provider = resolve_provider(args)
    args.provider = provider
    if provider == "filesystem":
        return load_filesystem_library(args)
    return load_applemusic_library(args)
