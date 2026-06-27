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
            "tracks": [compact_track(t) if isinstance(t, dict) else json_safe(t) for t in item[1]],
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
        "library_xml": str(library.xml_path),
        "summary": {
            "rules": len(rules),
            "failed": sum(1 for r in rules if r.count > 0 and (r.level == "ERROR" or fail_warnings)),
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
