from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None


def require_mutagen() -> None:
    if MutagenFile is None:
        raise RuntimeError("--scan-files requires mutagen. Install with: python3 -m pip install mutagen")


def tag_first(tags: Any, names: List[str]) -> str:
    if not tags:
        return ""
    for name in names:
        if name in tags:
            val = tags[name]
            if isinstance(val, list) and val:
                return str(val[0])
            return str(val)
    return ""


def extract_common_tags(audio: Any) -> Dict[str, str]:
    tags = audio.tags
    if not tags:
        return {}

    out = {
        "title": "",
        "artist": "",
        "album": "",
        "albumartist": "",
        "comment": "",
    }

    class_name = audio.__class__.__name__.lower()

    if "mp4" in class_name:
        out["title"] = tag_first(tags, ["\xa9nam"])
        out["artist"] = tag_first(tags, ["\xa9ART"])
        out["album"] = tag_first(tags, ["\xa9alb"])
        out["albumartist"] = tag_first(tags, ["aART"])
        out["comment"] = tag_first(tags, ["\xa9cmt"])
        return out

    lower_map = {str(k).lower(): k for k in tags.keys()}
    for target, candidates in {
        "title": ["title"],
        "artist": ["artist"],
        "album": ["album"],
        "albumartist": ["albumartist", "album artist"],
        "comment": ["comment", "description"],
    }.items():
        for c in candidates:
            if c in lower_map:
                out[target] = tag_first(tags, [lower_map[c]])
                break

    if not any(out.values()):
        keys = set(str(k) for k in tags.keys())
        frame_map = {
            "title": ["TIT2"],
            "artist": ["TPE1"],
            "album": ["TALB"],
            "albumartist": ["TPE2"],
            "comment": ["COMM::eng", "COMM"],
        }
        for target, candidates in frame_map.items():
            for c in candidates:
                if c in keys:
                    val = tags[c]
                    out[target] = str(val.text[0]) if hasattr(val, "text") and val.text else str(val)
                    break

    return out


def read_audio_details(path: Path) -> Dict[str, Any]:
    details = {
        "readable": False,
        "has_lyrics": None,
        "has_artwork": None,
        "format_name": None,
        "bitrate": None,
        "sample_rate": None,
        "channels": None,
        "length": None,
        "tags": {},
    }

    if MutagenFile is None:
        return details

    try:
        audio = MutagenFile(path)
    except Exception:
        return details

    if audio is None:
        return details

    details["readable"] = True
    details["format_name"] = audio.__class__.__name__

    info = getattr(audio, "info", None)
    if info:
        details["bitrate"] = getattr(info, "bitrate", None)
        details["sample_rate"] = getattr(info, "sample_rate", None)
        details["channels"] = getattr(info, "channels", None)
        details["length"] = getattr(info, "length", None)

    tags = audio.tags
    if not tags:
        details["has_lyrics"] = False
        details["has_artwork"] = False
        return details

    keys = [str(k) for k in tags.keys()]

    details["has_lyrics"] = any(
        k.startswith("USLT")
        or k.lower() in {"©lyr", "lyrics", "unsyncedlyrics"}
        or "lyrics" in k.lower()
        for k in keys
    )

    details["has_artwork"] = any(
        k.startswith("APIC")
        or k.lower() in {"covr", "metadata_block_picture"}
        or "picture" in k.lower()
        for k in keys
    )

    try:
        details["tags"] = extract_common_tags(audio)
    except Exception:
        details["tags"] = {}

    return details
