from __future__ import annotations

import collections
from typing import Any, Dict, List

from .model import analyze_comment_tokens, count_duplicates
from .providers.audio import read_audio_details


def normalize_ext(path, kind: str = "") -> str:
    if path and path.suffix:
        return path.suffix.lower().lstrip(".")
    return kind.lower() if kind else "unknown"


def bitrate_label(bit_rate: Any) -> str:
    if not bit_rate:
        return "unknown"
    try:
        br = int(bit_rate)
    except Exception:
        return "unknown"
    if br >= 1000:
        return f"{round(br / 1000)} Mbps"
    return f"{br} kbps"


def bitrate_bucket(bit_rate: Any, low_threshold: int) -> str:
    if not bit_rate:
        return "unknown"
    try:
        br = int(bit_rate)
    except Exception:
        return "unknown"
    if br == 0:
        return "unknown"
    if br < low_threshold:
        return f"Below {low_threshold} kbps"
    if br >= 900:
        return "Lossless / Hi-Res"
    if br >= 320:
        return "320 kbps and above"
    if br >= 256:
        return "256-319 kbps"
    return f"Below {low_threshold} kbps"


def audit_core(library, scan_files: bool, low_bitrate: int) -> Dict[str, Any]:
    tracks = library.tracks
    playlists = library.playlists
    known_tokens = library.known_tokens

    artists = {t.get("artist", "") for t in tracks if t.get("artist")}
    albums = {
        (t.get("album_artist") or t.get("artist", ""), t.get("album", ""))
        for t in tracks
        if t.get("album")
    }

    rating_counts = collections.Counter()
    rating_values = []
    invalid_tracks = []
    unrated_tracks = []
    favorites = 0
    unknown_token_counts = collections.Counter()

    for t in tracks:
        token_info = analyze_comment_tokens(t["comments"], known_tokens)
        t["token_info"] = token_info

        if token_info["rating"]:
            rating_counts[token_info["rating"]] += 1
            rating_values.append(token_info["rating_value"])
        else:
            unrated_tracks.append(t)

        if token_info["favorite"]:
            favorites += 1

        if token_info["multiple_ratings"] or token_info["bad_ratings"]:
            invalid_tracks.append(t)

        for tok in token_info["unknown_tokens"]:
            unknown_token_counts[tok] += 1

    file_missing = []
    file_existing = []
    ext_counts = collections.Counter()
    kind_counts = collections.Counter()
    low_bitrate_tracks = []
    lyrics_count = 0
    lyrics_missing = 0
    artwork_count = 0
    artwork_missing = 0
    mutagen_unreadable = 0
    tag_mismatches = []

    for t in tracks:
        path = t.get("path")
        exists = bool(path and path.exists())
        if exists:
            file_existing.append(t)
        else:
            file_missing.append(t)

        ext_counts[normalize_ext(path, t.get("kind", ""))] += 1
        kind_counts[str(t.get("kind", "unknown"))] += 1

        try:
            br_int = int(t.get("bit_rate")) if t.get("bit_rate") else 0
        except Exception:
            br_int = 0

        if br_int and br_int < low_bitrate:
            low_bitrate_tracks.append(t)

        if t.get("filesystem_provider"):
            if not t.get("audio_readable"):
                mutagen_unreadable += 1
            if t.get("embedded_has_lyrics"):
                lyrics_count += 1
            else:
                lyrics_missing += 1
            if t.get("embedded_has_artwork"):
                artwork_count += 1
            else:
                artwork_missing += 1

        elif scan_files and exists:
            details = read_audio_details(path)
            t["audio_details"] = details
            if not details["readable"]:
                mutagen_unreadable += 1
            if details["has_lyrics"] is True:
                lyrics_count += 1
            elif details["has_lyrics"] is False:
                lyrics_missing += 1
            if details["has_artwork"] is True:
                artwork_count += 1
            elif details["has_artwork"] is False:
                artwork_missing += 1

            tags = details.get("tags") or {}
            for xml_key, tag_key, label in [
                ("name", "title", "Title"),
                ("artist", "artist", "Artist"),
                ("album", "album", "Album"),
            ]:
                xml_val = str(t.get(xml_key) or "").strip()
                tag_val = str(tags.get(tag_key) or "").strip()
                if xml_val and tag_val and xml_val != tag_val:
                    tag_mismatches.append((t, label, xml_val, tag_val))

    duplicates = count_duplicates(tracks)
    smart_count = sum(1 for p in playlists if p["is_smart"])
    standard_count = sum(1 for p in playlists if not p["is_smart"] and not p["folder"])
    folder_count = sum(1 for p in playlists if p["folder"])
    empty_playlists = [p for p in playlists if not p["folder"] and p["item_count"] == 0]

    return {
        "artists": artists,
        "albums": albums,
        "rating_counts": rating_counts,
        "rating_values": rating_values,
        "invalid_tracks": invalid_tracks,
        "unrated_tracks": unrated_tracks,
        "favorites": favorites,
        "unknown_token_counts": unknown_token_counts,
        "file_missing": file_missing,
        "file_existing": file_existing,
        "ext_counts": ext_counts,
        "kind_counts": kind_counts,
        "low_bitrate_tracks": low_bitrate_tracks,
        "lyrics_count": lyrics_count,
        "lyrics_missing": lyrics_missing,
        "artwork_count": artwork_count,
        "artwork_missing": artwork_missing,
        "mutagen_unreadable": mutagen_unreadable,
        "tag_mismatches": tag_mismatches,
        "duplicates": duplicates,
        "smart_count": smart_count,
        "standard_count": standard_count,
        "folder_count": folder_count,
        "empty_playlists": empty_playlists,
    }
