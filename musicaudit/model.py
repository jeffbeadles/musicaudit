from __future__ import annotations

import collections
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RATING_RE = re.compile(r"\bS([1-5])\b")
BAD_RATING_RE = re.compile(r"\bS([0-9]+)\b")
DEFAULT_KNOWN_TOKENS = {"FAV"}


@dataclass
class Library:
    xml_path: Path
    tracks: List[Dict[str, Any]]
    playlists: List[Dict[str, Any]]
    known_tokens: set[str]
    config: Dict[str, Any] = field(default_factory=dict)
    settings: Any = None


def analyze_comment_tokens(comments: str, known_tokens: set[str]) -> Dict[str, Any]:
    tokens = comments.split()
    rating_matches = RATING_RE.findall(comments)
    bad_rating_matches = BAD_RATING_RE.findall(comments)

    ratings = [f"S{x}" for x in rating_matches]
    bad_ratings = [f"S{x}" for x in bad_rating_matches if x not in {"1", "2", "3", "4", "5"}]

    known = set(known_tokens) | {f"S{i}" for i in range(1, 6)}
    unknown = [t for t in tokens if t not in known]

    return {
        "tokens": tokens,
        "ratings": ratings,
        "rating": ratings[0] if len(ratings) == 1 else None,
        "rating_value": int(rating_matches[0]) if len(rating_matches) == 1 else None,
        "missing_rating": len(ratings) == 0,
        "multiple_ratings": len(ratings) > 1,
        "bad_ratings": bad_ratings,
        "favorite": "FAV" in tokens,
        "unknown_tokens": unknown,
    }


def count_duplicates(tracks: List[Dict[str, Any]]) -> List[Tuple[Tuple[str, str, str], List[Dict[str, Any]]]]:
    groups: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = collections.defaultdict(list)
    for t in tracks:
        key = (
            str(t.get("artist", "")).strip().lower(),
            str(t.get("album", "")).strip().lower(),
            str(t.get("name", "")).strip().lower(),
        )
        if all(key):
            groups[key].append(t)
    return [(k, v) for k, v in groups.items() if len(v) > 1]
