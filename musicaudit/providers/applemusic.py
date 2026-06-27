from __future__ import annotations

import hashlib
import plistlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse

from ..model import Library
from ..util.config import expand_path, load_config
from ..settings import resolve_settings


def location_to_path(location: str) -> Optional[Path]:
    if not location:
        return None
    parsed = urlparse(location)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return expand_path(location)


def read_plist(xml_path: Path) -> Dict[str, Any]:
    with xml_path.open("rb") as f:
        return plistlib.load(f)


def data_hash(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bytes):
        data = value
    else:
        data = str(value).encode("utf-8", errors="replace")
    return hashlib.sha256(data).hexdigest()[:16]


def extract_tracks(plist: Dict[str, Any]) -> List[Dict[str, Any]]:
    tracks = []
    for track_id, track in plist.get("Tracks", {}).items():
        if track.get("Track Type") != "File":
            continue

        media_kind = str(track.get("Media Kind", ""))
        if media_kind and media_kind.lower() not in {"song", "music", "unknown"}:
            continue

        loc = track.get("Location", "")
        path = location_to_path(loc)

        tracks.append(
            {
                "track_id": str(track_id),
                "persistent_id": track.get("Persistent ID") or str(track_id),
                "name": track.get("Name", ""),
                "artist": track.get("Artist", ""),
                "album_artist": track.get("Album Artist", ""),
                "album": track.get("Album", ""),
                "genre": track.get("Genre", ""),
                "kind": track.get("Kind", ""),
                "comments": track.get("Comments", "") or "",
                "rating": track.get("Rating"),
                "play_count": track.get("Play Count", 0),
                "skip_count": track.get("Skip Count", 0),
                "date_added": track.get("Date Added"),
                "location": loc,
                "path": path,
                "size": track.get("Size"),
                "bit_rate": track.get("Bit Rate"),
                "sample_rate": track.get("Sample Rate"),
                "year": track.get("Year"),
                "total_time": track.get("Total Time"),
            }
        )
    return tracks


def extract_playlists(plist: Dict[str, Any]) -> List[Dict[str, Any]]:
    output = []
    for playlist in plist.get("Playlists", []):
        items = playlist.get("Playlist Items", []) or []
        is_smart = "Smart Info" in playlist or "Smart Criteria" in playlist
        output.append(
            {
                "name": playlist.get("Name", ""),
                "is_smart": is_smart,
                "item_count": len(items),
                "persistent_id": playlist.get("Playlist Persistent ID"),
                "folder": bool(playlist.get("Folder")),
                "visible": playlist.get("Visible", True),
                "smart_info_hash": data_hash(playlist.get("Smart Info")) if is_smart else "-",
                "smart_criteria_hash": data_hash(playlist.get("Smart Criteria")) if is_smart else "-",
            }
        )
    return output


def load_library(args) -> Library:
    config = load_config(getattr(args, "config", None))
    xml_arg = getattr(args, "xml", None) or config.get("library_xml")
    if not xml_arg:
        raise RuntimeError("--xml is required unless library_xml is set in config.")

    xml_path = expand_path(xml_arg)
    if not xml_path.exists():
        raise RuntimeError(f"XML file not found: {xml_path}")

    plist = read_plist(xml_path)
    tracks = extract_tracks(plist)
    playlists = extract_playlists(plist)

    settings = resolve_settings(args, config)

    return Library(
        xml_path=xml_path,
        tracks=tracks,
        playlists=playlists,
        known_tokens=set(settings.known_tokens),
        config=config,
        settings=settings,
    )
