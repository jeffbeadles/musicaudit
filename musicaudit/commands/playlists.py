from __future__ import annotations

import shutil
import subprocess

from .common import add_common_args, add_detail_args, apply_settings, load_library
from ..reports.markdown import playlists_report
from ..util.formatting import write_or_print


def try_itunessmart_decode(xml_path, max_lines=300):
    exe = shutil.which("itunessmart")
    if not exe:
        return "itunessmart executable not found in PATH."

    commands = [
        [exe, str(xml_path)],
        [exe, "--input", str(xml_path)],
        [exe, "-i", str(xml_path)],
        [exe, "decode", str(xml_path)],
    ]
    for cmd in commands:
        try:
            result = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
        except Exception:
            continue
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        text = out or err
        if result.returncode == 0 and text:
            lines = text.splitlines()
            if len(lines) > max_lines:
                text = "\n".join(lines[:max_lines]) + f"\n... truncated after {max_lines} lines ..."
            return text
    return "Found itunessmart, but could not determine its command-line syntax automatically."


def run(args) -> int:
    library = load_library(args)
    args = apply_settings(args, library)
    decoded = try_itunessmart_decode(library.xml_path) if args.decode_smart else None
    return write_or_print(playlists_report(library, decoded, args.max_details), args.markdown)


def register(sub):
    p = sub.add_parser("playlists", help="Playlist and Smart Playlist audit.")
    add_common_args(p)
    add_detail_args(p)
    p.add_argument("--decode-smart", action="store_true")
    p.set_defaults(func=run)
