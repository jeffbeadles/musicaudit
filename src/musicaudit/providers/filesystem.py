from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..model import Library
from ..settings import resolve_settings
from ..util.config import expand_path, load_config

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None


SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".m4a",
    ".mp4",
    ".aac",
    ".flac",
    ".alac",
    ".ogg",
    ".oga",
    ".opus",
    ".wav",
    ".aiff",
    ".aif",
}


def require_mutagen() -> None:
    if MutagenFile is None:
        raise RuntimeError(
            "filesystem provider requires mutagen. Install with: python3 -m pip install mutagen"
        )


def tag_first(tags: Any, names: List[str]) -> str:
    if not tags:
        return ""
    for name in names:
        if name in tags:
            val = tags[name]
            if isinstance(val, list) and val:
                return str(val[0])
            if hasattr(val, "text") and val.text:
                return str(val.text[0])
            return str(val)
    return ""


def extract_tags(audio: Any) -> Dict[str, str]:
    tags = audio.tags
    out = {
        "name": "",
        "artist": "",
        "album_artist": "",
        "album": "",
        "genre": "",
        "comments": "",
        "year": "",
    }
    if not tags:
        return out

    class_name = audio.__class__.__name__.lower()

    if "mp4" in class_name:
        out["name"] = tag_first(tags, ["\xa9nam"])
        out["artist"] = tag_first(tags, ["\xa9ART"])
        out["album_artist"] = tag_first(tags, ["aART"])
        out["album"] = tag_first(tags, ["\xa9alb"])
        out["genre"] = tag_first(tags, ["\xa9gen"])
        out["comments"] = tag_first(tags, ["\xa9cmt"])
        out["year"] = tag_first(tags, ["\xa9day"])
        return out

    lower_map = {str(k).lower(): k for k in tags.keys()}
    candidates = {
        "name": ["title"],
        "artist": ["artist"],
        "album_artist": ["albumartist", "album artist"],
        "album": ["album"],
        "genre": ["genre"],
        "comments": ["comment", "description"],
        "year": ["date", "year"],
    }
    for target, names in candidates.items():
        for name in names:
            if name in lower_map:
                out[target] = tag_first(tags, [lower_map[name]])
                break

    keys = set(str(k) for k in tags.keys())
    frame_map = {
        "name": ["TIT2"],
        "artist": ["TPE1"],
        "album_artist": ["TPE2"],
        "album": ["TALB"],
        "genre": ["TCON"],
        "year": ["TDRC", "TYER"],
    }
    for target, names in frame_map.items():
        if out[target]:
            continue
        for name in names:
            if name in keys:
                out[target] = tag_first(tags, [name])
                break

    # ID3 comments can have keys such as COMM::eng, COMM:description:eng,
    # or other variants. ffmpeg commonly writes comment metadata as
    # TXXX:comment. Accept either form when a normalized comment was not found.
    if not out["comments"]:
        for key in sorted(keys):
            if key.startswith("COMM") or key.lower() in {
                "txxx:comment",
                "txxx:comments",
            }:
                out["comments"] = tag_first(tags, [key])
                break

    return out


def find_lyrics(audio: Any) -> str:
    tags = audio.tags
    if not tags:
        return None
    keys = [str(k) for k in tags.keys()]

    return tags.get(
        next(
            (
                k
                for k in keys
                if k.startswith("USLT")
                or k.lower() in {"©lyr", "lyrics", "unsyncedlyrics"}
                or "lyrics" in k.lower()
            ),
            None,
        )
    )


def has_lyrics(audio: Any) -> bool:

    lyric_state = find_lyrics(audio)
    return lyric_state is not None


def has_artwork(audio: Any) -> bool:
    tags = audio.tags
    if not tags:
        return False
    keys = [str(k) for k in tags.keys()]
    return any(
        k.startswith("APIC")
        or k.lower() in {"covr", "metadata_block_picture"}
        or "picture" in k.lower()
        for k in keys
    )


def read_track(path: Path, root: Path, index: int) -> Dict[str, Any]:
    try:
        audio = MutagenFile(path)
    except Exception:
        audio = None

    rel = path.relative_to(root)
    persistent_id = "FS-" + str(rel).encode("utf-8", errors="replace").hex()

    track = {
        "track_id": str(index),
        "persistent_id": persistent_id,
        "name": path.stem,
        "artist": "",
        "album_artist": "",
        "album": "",
        "genre": "",
        "kind": path.suffix.lower().lstrip("."),
        "comments": "",
        "rating": None,
        "play_count": 0,
        "skip_count": 0,
        "date_added": None,
        "location": str(path),
        "path": path,
        "relative_path": str(rel),
        "size": path.stat().st_size if path.exists() else None,
        "bit_rate": None,
        "sample_rate": None,
        "year": None,
        "total_time": None,
        "filesystem_provider": True,
        "audio_readable": False,
        "embedded_lyrics": None,
        "embedded_has_lyrics": False,
        "embedded_has_artwork": False,
    }

    if audio is None:
        return track

    track["audio_readable"] = True

    tags = extract_tags(audio)
    track["name"] = tags.get("name") or track["name"]
    track["artist"] = tags.get("artist") or ""
    track["album_artist"] = tags.get("album_artist") or ""
    track["album"] = tags.get("album") or ""
    track["genre"] = tags.get("genre") or ""
    track["comments"] = tags.get("comments") or ""
    track["year"] = tags.get("year") or None

    info = getattr(audio, "info", None)
    if info:
        bitrate = getattr(info, "bitrate", None)
        if bitrate:
            track["bit_rate"] = int(round(bitrate / 1000))
        track["sample_rate"] = getattr(info, "sample_rate", None)
        length = getattr(info, "length", None)
        if length:
            track["total_time"] = int(round(length * 1000))

    track["embedded_lyrics"] = find_lyrics(audio)
    track["embedded_has_lyrics"] = has_lyrics(audio)
    track["embedded_has_artwork"] = has_artwork(audio)
    return track


def load_filesystem_library(args) -> Library:
    require_mutagen()
    config = load_config(getattr(args, "config", None))
    root_arg = getattr(args, "path", None) or config.get("music_root")
    if not root_arg:
        raise RuntimeError(
            "--path is required for filesystem provider unless music_root is set in config."
        )

    root = expand_path(root_arg)
    if not root.exists():
        raise RuntimeError(f"Music path not found: {root}")
    if not root.is_dir():
        raise RuntimeError(f"Music path is not a directory: {root}")

    settings = resolve_settings(args, config)

    extensions = set(SUPPORTED_EXTENSIONS)
    configured_exts = config.get("filesystem_extensions")
    if configured_exts:
        extensions = {("." + e.lower().lstrip(".")) for e in configured_exts}

    files = sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in extensions
    )
    tracks = [read_track(path, root, i + 1) for i, path in enumerate(files)]

    return Library(
        xml_path=root,
        tracks=tracks,
        playlists=[],
        known_tokens=set(settings.known_tokens),
        config=config,
        settings=settings,
    )
