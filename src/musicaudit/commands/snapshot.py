from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .common import add_common_args, apply_settings, load_library
from ..analysis import audit_core
from ..reports.json import compact_track, json_safe
from ..util.formatting import write_or_print


SNAPSHOT_SCHEMA = "musicaudit.snapshot.v1"


def snapshot_track(track: dict, root: Path | None = None) -> dict:
    item = compact_track(track)

    path = track.get("path")
    if path is not None:
        item["path"] = str(path)
        try:
            if root is not None:
                item["relative_path"] = str(
                    Path(path).resolve().relative_to(root.resolve())
                )
        except Exception:
            item["relative_path"] = None
    else:
        item["relative_path"] = None

    item.update(
        {
            "genre": track.get("genre"),
            "kind": track.get("kind"),
            "year": track.get("year"),
            "size": track.get("size"),
            "sample_rate": track.get("sample_rate"),
            "total_time": track.get("total_time"),
            "embedded_lyrics": track.get("embedded_lyrics"),
            "embedded_has_lyrics": track.get("embedded_has_lyrics"),
            "embedded_has_artwork": track.get("embedded_has_artwork"),
            "audio_readable": track.get("audio_readable"),
        }
    )
    return item


def build_snapshot(library, core, scan_files: bool, low_bitrate: int) -> dict:
    root = None
    try:
        if getattr(library, "xml_path", None):
            p = Path(library.xml_path)
            if p.exists() and p.is_dir():
                root = p
    except Exception:
        root = None

    return {
        "schema": SNAPSHOT_SCHEMA,
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": str(library.xml_path),
        "provider": getattr(getattr(library, "settings", None), "provider", None),
        "settings": {
            "scan_files": scan_files,
            "low_bitrate": low_bitrate,
        },
        "summary": {
            "tracks": len(library.tracks),
            "playlists": len(library.playlists),
            "missing_files": len(core["file_missing"]),
            "missing_ratings": len(core["unrated_tracks"]),
            "invalid_ratings": len(core["invalid_tracks"]),
            "duplicate_groups": len(core["duplicates"]),
            "low_bitrate": len(core["low_bitrate_tracks"]),
            "lyrics_missing": core.get("lyrics_missing"),
            "artwork_missing": core.get("artwork_missing"),
            "unreadable_files": core.get("mutagen_unreadable"),
        },
        "tracks": [snapshot_track(t, root) for t in library.tracks],
        "playlists": json_safe(library.playlists),
    }


def run(args) -> int:
    library = load_library(args)
    if getattr(args, "provider", None) == "filesystem":
        args.scan_files = True

    args = apply_settings(args, library)
    core = audit_core(library, args.scan_files, args.low_bitrate)

    payload = build_snapshot(library, core, args.scan_files, args.low_bitrate)
    report = json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n"
    return write_or_print(report, args.output)


def register(sub):
    p = sub.add_parser("snapshot", help="Create a JSON snapshot for later diffing.")
    add_common_args(p)
    p.add_argument("--scan-files", action="store_true")
    p.add_argument("--low-bitrate", type=int, default=None)
    p.set_defaults(func=run)
