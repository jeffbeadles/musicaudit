from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..rules.engine import rules_have_failures


def json_safe(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]

    # Track-like objects are currently dictionaries, but keep this fallback
    # intentionally boring and predictable.
    return str(value)


def compact_track(track: dict) -> dict:
    return {
        "persistent_id": track.get("persistent_id"),
        "track_id": track.get("track_id"),
        "name": track.get("name"),
        "artist": track.get("artist"),
        "album_artist": track.get("album_artist"),
        "album": track.get("album"),
        "comments": track.get("comments"),
        "bit_rate": track.get("bit_rate"),
        "path": str(track.get("path")) if track.get("path") is not None else None,
    }


def json_rule_item(item: Any) -> Any:
    # Duplicate-track rule items are tuples of: (key, [track, track, ...])
    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
        return {
            "key": json_safe(item[0]),
            "tracks": [
                compact_track(t) if isinstance(t, dict) else json_safe(t)
                for t in item[1]
            ],
        }

    # XML tag mismatch items are tuples of: (track, label, xml_value, file_value)
    if isinstance(item, tuple) and len(item) == 4 and isinstance(item[0], dict):
        track, label, xml_value, file_value = item
        return {
            "track": compact_track(track),
            "field": label,
            "xml_value": xml_value,
            "file_value": file_value,
        }

    if isinstance(item, dict):
        # Track dictionaries are large; compact them if they look like tracks.
        if "name" in item and "artist" in item and "album" in item:
            return compact_track(item)
        return json_safe(item)

    return json_safe(item)


def rules_json_report(library, rules, fail_warnings: bool) -> tuple[str, int]:
    failed = rules_have_failures(rules, fail_warnings)

    payload = {
        "status": "FAIL" if failed else "PASS",
        "apple_library": str(library.xml_path),
        "summary": {
            "rules": len(rules),
            "failed": sum(
                1
                for r in rules
                if r.count > 0 and (r.level == "ERROR" or fail_warnings)
            ),
            "warnings": sum(1 for r in rules if r.count > 0 and r.level == "WARN"),
            "errors": sum(1 for r in rules if r.count > 0 and r.level == "ERROR"),
        },
        "rules": [
            {
                "id": r.id,
                "level": r.level,
                "status": "PASS" if r.passed else r.level,
                "description": r.description,
                "count": r.count,
                "items": [json_rule_item(item) for item in r.items],
            }
            for r in rules
        ],
    }

    return json.dumps(payload, indent=2, sort_keys=True) + "\n", 1 if failed else 0


def library_ref(library) -> dict:
    return {
        "source": str(library.xml_path),
        "provider": getattr(getattr(library, "settings", None), "provider", None),
    }


def core_summary(library, core, scan_files: bool, low_bitrate: int) -> dict:
    empty_smart = len([p for p in core["empty_playlists"] if p["is_smart"]])
    empty_standard = len([p for p in core["empty_playlists"] if not p["is_smart"]])

    payload = {
        "tracks": len(library.tracks),
        "artists": len(core["artists"]),
        "albums": len(core["albums"]),
        "playlists": len(library.playlists),
        "smart_playlists": core["smart_count"],
        "empty_smart_playlists": empty_smart,
        "empty_standard_playlists": empty_standard,
        "missing_files": len(core["file_missing"]),
        "missing_ratings": len(core["unrated_tracks"]),
        "invalid_ratings": len(core["invalid_tracks"]),
        "duplicate_groups": len(core["duplicates"]),
        "low_bitrate": {
            "threshold_kbps": low_bitrate,
            "count": len(core["low_bitrate_tracks"]),
        },
    }

    if scan_files:
        payload["embedded"] = {
            "lyrics_present": core["lyrics_count"],
            "lyrics_missing": core["lyrics_missing"],
            "artwork_present": core["artwork_count"],
            "artwork_missing": core["artwork_missing"],
            "unreadable_files": core["mutagen_unreadable"],
            "tag_mismatches": len(core["tag_mismatches"]),
        }

    return payload


def health_json_report(
    library, core, scan_files: bool, low_bitrate: int
) -> tuple[str, int]:
    fail_checks = [
        len(core["file_missing"]),
        len(core["unrated_tracks"]),
        len(core["invalid_tracks"]),
    ]
    if scan_files:
        fail_checks.append(core["mutagen_unreadable"])

    status = "FAIL" if any(x > 0 for x in fail_checks) else "PASS"
    payload = {
        "status": status,
        "library": {
            "source": str(library.xml_path),
        },
        "health": core_summary(library, core, scan_files, low_bitrate),
    }
    return json.dumps(
        payload, indent=2, sort_keys=True
    ) + "\n", 1 if status == "FAIL" else 0


def bitrate_summary(tracks, low_bitrate: int) -> dict:
    from ..analysis import bitrate_bucket, bitrate_label
    import collections

    summary_counts = collections.Counter()
    all_counts = collections.Counter()
    low_counts = collections.Counter()

    for t in tracks:
        br = t.get("bit_rate")
        summary_counts[bitrate_bucket(br, low_bitrate)] += 1
        all_counts[bitrate_label(br)] += 1
        try:
            br_int = int(br) if br else 0
        except Exception:
            br_int = 0
        if br_int and br_int < low_bitrate:
            low_counts[bitrate_label(br)] += 1

    return {
        "summary": dict(sorted(summary_counts.items())),
        "all": dict(sorted(all_counts.items())),
        "below_threshold": dict(sorted(low_counts.items())),
    }


def summary_json_report(
    library, core, scan_files: bool, low_bitrate: int
) -> tuple[str, int]:
    total = len(library.tracks)
    payload = {
        "status": "OK",
        "library": {
            "source": str(library.xml_path),
        },
        "health": core_summary(library, core, scan_files, low_bitrate),
        "ratings": {f"S{i}": core["rating_counts"][f"S{i}"] for i in range(5, 0, -1)},
        "unrated": len(core["unrated_tracks"]),
        "favorites": core["favorites"],
        "formats": dict(core["ext_counts"].most_common()),
        "bitrates": bitrate_summary(library.tracks, low_bitrate),
    }

    if total:
        payload["rating_percentages"] = {
            f"S{i}": round((core["rating_counts"][f"S{i}"] / total) * 100, 2)
            for i in range(5, 0, -1)
        }
        payload["rating_percentages"]["unrated"] = round(
            (len(core["unrated_tracks"]) / total) * 100, 2
        )
        payload["rating_percentages"]["favorites"] = round(
            (core["favorites"] / total) * 100, 2
        )

    if scan_files:
        payload["embedded"] = {
            "lyrics_present": core["lyrics_count"],
            "lyrics_missing": core["lyrics_missing"],
            "artwork_present": core["artwork_count"],
            "artwork_missing": core["artwork_missing"],
            "unreadable_files": core["mutagen_unreadable"],
            "tag_mismatches": len(core["tag_mismatches"]),
        }

    return json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n", 0


def diff_json_report(old_input, new_input, d) -> tuple[str, int]:
    def change_track_pair(pair):
        o, n = pair[0], pair[1]
        return {
            "old": compact_track(o),
            "new": compact_track(n),
        }

    def transition_items(key, old_field, new_field):
        return [
            {
                "track": compact_track(n),
                old_field: o.get(old_field.replace("old_", "")),
                new_field: n.get(new_field.replace("new_", "")),
                "old": compact_track(o),
                "new": compact_track(n),
            }
            for o, n in d[key]
        ]

    payload = {
        "status": "NO_CHANGES",
        "old": str(old_input),
        "new": str(new_input),
        "summary": {
            "new_songs": len(d["added"]),
            "removed_songs": len(d["removed"]),
            "rating_changes_existing": len(d["rating_changed"]),
            "fav_changes_existing": len(d["fav_changed"]),
            "new_favorites": len(d["added_favorites"]),
            "removed_favorites": len(d["removed_favorites"]),
            "comment_changes": len(d["comments_changed"]),
            "path_changes": len(d["path_changed"]),
            "title_artist_album_changes": len(d["title_changed"]),
            "track_name_changes": len(d.get("track_name_changed", [])),
            "track_artist_changes": len(d.get("track_artist_changed", [])),
            "album_title_changes": len(d.get("album_changed", [])),
            "album_artist_changes": len(d.get("album_artist_changed", [])),
            "album_artist_added": len(d.get("album_artist_added", [])),
            "album_artist_modified": len(d.get("album_artist_modified", [])),
            "album_artist_removed": len(d.get("album_artist_removed", [])),
            "bitrate_changes": len(d.get("bitrate_changed", [])),
            "artwork_changes": len(d.get("artwork_changed", [])),
            "artwork_added": len(d.get("artwork_added", [])),
            "artwork_removed": len(d.get("artwork_removed", [])),
            "lyrics_changes": len(d.get("lyrics_changed", [])),
            "lyrics_added": len(d.get("lyrics_added", [])),
            "lyrics_removed": len(d.get("lyrics_removed", [])),
            "readability_changes": len(d.get("readable_changed", [])),
            "new_playlists": len(d["playlist_added"]),
            "removed_playlists": len(d["playlist_removed"]),
            "smart_playlist_changes": len(d["smart_changed"]),
        },
        "items": {
            "new_songs": [compact_track(t) for t in d["added"]],
            "removed_songs": [compact_track(t) for t in d["removed"]],
            "new_favorites": [compact_track(t) for t in d["added_favorites"]],
            "removed_favorites": [compact_track(t) for t in d["removed_favorites"]],
            "rating_changes": [
                {
                    "track": compact_track(n),
                    "old_rating": old_rating,
                    "new_rating": new_rating,
                }
                for o, n, old_rating, new_rating in d["rating_changed"]
            ],
            "favorite_changes": [
                {
                    "track": compact_track(n),
                    "old_favorite": old_fav,
                    "new_favorite": new_fav,
                }
                for o, n, old_fav, new_fav in d["fav_changed"]
            ],
            "comment_changes": [
                change_track_pair(pair) for pair in d["comments_changed"]
            ],
            "path_changes": [change_track_pair(pair) for pair in d["path_changed"]],
            "title_artist_album_changes": [
                change_track_pair(pair) for pair in d["title_changed"]
            ],
            "track_name_changes": [
                change_track_pair(pair) for pair in d.get("track_name_changed", [])
            ],
            "track_artist_changes": [
                change_track_pair(pair) for pair in d.get("track_artist_changed", [])
            ],
            "album_title_changes": [
                change_track_pair(pair) for pair in d.get("album_changed", [])
            ],
            "album_artist_changes": [
                change_track_pair(pair) for pair in d.get("album_artist_changed", [])
            ],
            "album_artist_added": [
                change_track_pair(pair) for pair in d.get("album_artist_added", [])
            ],
            "album_artist_modified": [
                change_track_pair(pair) for pair in d.get("album_artist_modified", [])
            ],
            "album_artist_removed": [
                change_track_pair(pair) for pair in d.get("album_artist_removed", [])
            ],
            "bitrate_changes": [
                change_track_pair(pair) for pair in d.get("bitrate_changed", [])
            ],
            "artwork_changes": [
                change_track_pair(pair) for pair in d.get("artwork_changed", [])
            ],
            "artwork_added": [
                change_track_pair(pair) for pair in d.get("artwork_added", [])
            ],
            "artwork_removed": [
                change_track_pair(pair) for pair in d.get("artwork_removed", [])
            ],
            "lyrics_changes": [
                change_track_pair(pair) for pair in d.get("lyrics_changed", [])
            ],
            "lyrics_added": [
                change_track_pair(pair) for pair in d.get("lyrics_added", [])
            ],
            "lyrics_removed": [
                change_track_pair(pair) for pair in d.get("lyrics_removed", [])
            ],
            "readability_changes": [
                change_track_pair(pair) for pair in d.get("readable_changed", [])
            ],
            "new_playlists": [json_safe(p) for p in d["playlist_added"]],
            "removed_playlists": [json_safe(p) for p in d["playlist_removed"]],
            "smart_playlist_changes": [
                {"old": json_safe(o), "new": json_safe(n)}
                for o, n in d["smart_changed"]
            ],
        },
    }

    if any(payload["summary"].values()):
        payload["status"] = "CHANGES"

    return json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n", 0
