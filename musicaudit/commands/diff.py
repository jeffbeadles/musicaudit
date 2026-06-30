from __future__ import annotations

import collections
import json

from ..model import analyze_comment_tokens, DEFAULT_KNOWN_TOKENS
from ..providers.applemusic import read_plist, extract_tracks, extract_playlists
from ..util.config import expand_path, load_config
from ..util.formatting import fmt_int, write_or_print
from ..reports.markdown import header
from ..reports.json import diff_json_report


def track_key(t):
    return str(t.get("persistent_id") or t.get("relative_path") or t.get("path") or t.get("track_id"))


def comparable_path(t):
    return str(t.get("relative_path") or t.get("path") or "")


def text_transition(old_value, new_value):
    old_s = str(old_value or "").strip()
    new_s = str(new_value or "").strip()
    if not old_s and new_s:
        return "added"
    if old_s and not new_s:
        return "removed"
    if old_s != new_s:
        return "modified"
    return "unchanged"


def bool_transition(old_value, new_value):
    old_b = bool(old_value)
    new_b = bool(new_value)
    if not old_b and new_b:
        return "added"
    if old_b and not new_b:
        return "removed"
    if old_b != new_b:
        return "modified"
    return "unchanged"


def read_diff_input(path):
    p = expand_path(path)
    if not p.exists():
        raise RuntimeError(f"Diff input not found: {p}")

    if p.suffix.lower() == ".json":
        payload = json.loads(p.read_text(encoding="utf-8"))
        if payload.get("schema") != "musicaudit.snapshot.v1":
            raise RuntimeError(f"JSON diff input is not a musicaudit snapshot: {p}")
        return {
            "path": p,
            "kind": "snapshot",
            "tracks": payload.get("tracks", []) or [],
            "playlists": payload.get("playlists", []) or [],
            "payload": payload,
        }

    plist = read_plist(p)
    return {
        "path": p,
        "kind": "apple-library",
        "tracks": extract_tracks(plist),
        "playlists": extract_playlists(plist),
        "payload": None,
    }


def analyze_diff(old_tracks, new_tracks, old_playlists, new_playlists, known_tokens):
    old_map = {track_key(t): t for t in old_tracks}
    new_map = {track_key(t): t for t in new_tracks}
    old_keys = set(old_map)
    new_keys = set(new_map)

    added = [new_map[k] for k in sorted(new_keys - old_keys)]
    removed = [old_map[k] for k in sorted(old_keys - new_keys)]
    common = sorted(old_keys & new_keys)

    rating_changed = []
    fav_changed = []
    comments_changed = []
    path_changed = []
    title_changed = []
    track_name_changed = []
    track_artist_changed = []
    album_changed = []
    album_artist_changed = []
    album_artist_added = []
    album_artist_modified = []
    album_artist_removed = []
    bitrate_changed = []
    artwork_changed = []
    artwork_added = []
    artwork_removed = []
    lyrics_changed = []
    lyrics_added = []
    lyrics_removed = []
    readable_changed = []

    added_with_ratings = collections.Counter()
    removed_with_ratings = collections.Counter()
    added_favorites = []
    removed_favorites = []

    for t in added:
        info = analyze_comment_tokens(t.get("comments") or "", known_tokens)
        if info["rating"]:
            added_with_ratings[info["rating"]] += 1
        if info["favorite"]:
            added_favorites.append(t)

    for t in removed:
        info = analyze_comment_tokens(t.get("comments") or "", known_tokens)
        if info["rating"]:
            removed_with_ratings[info["rating"]] += 1
        if info["favorite"]:
            removed_favorites.append(t)

    for k in common:
        o = old_map[k]
        n = new_map[k]
        ot = analyze_comment_tokens(o.get("comments") or "", known_tokens)
        nt = analyze_comment_tokens(n.get("comments") or "", known_tokens)
        if ot["rating"] != nt["rating"]:
            rating_changed.append((o, n, ot["rating"], nt["rating"]))
        if ot["favorite"] != nt["favorite"]:
            fav_changed.append((o, n, ot["favorite"], nt["favorite"]))
        if (o.get("comments") or "") != (n.get("comments") or ""):
            comments_changed.append((o, n))
        if comparable_path(o) != comparable_path(n):
            path_changed.append((o, n))
        if (o.get("name"), o.get("artist"), o.get("album")) != (n.get("name"), n.get("artist"), n.get("album")):
            title_changed.append((o, n))
        if (o.get("name") or "") != (n.get("name") or ""):
            track_name_changed.append((o, n))
        if (o.get("artist") or "") != (n.get("artist") or ""):
            track_artist_changed.append((o, n))
        if (o.get("album") or "") != (n.get("album") or ""):
            album_changed.append((o, n))
        album_artist_change = text_transition(o.get("album_artist"), n.get("album_artist"))
        if album_artist_change != "unchanged":
            album_artist_changed.append((o, n))
            if album_artist_change == "added":
                album_artist_added.append((o, n))
            elif album_artist_change == "removed":
                album_artist_removed.append((o, n))
            else:
                album_artist_modified.append((o, n))

        if o.get("bit_rate") != n.get("bit_rate"):
            bitrate_changed.append((o, n))

        artwork_change = bool_transition(o.get("embedded_has_artwork"), n.get("embedded_has_artwork"))
        if artwork_change != "unchanged":
            artwork_changed.append((o, n))
            if artwork_change == "added":
                artwork_added.append((o, n))
            elif artwork_change == "removed":
                artwork_removed.append((o, n))

        lyrics_change = bool_transition(o.get("embedded_has_lyrics"), n.get("embedded_has_lyrics"))
        if lyrics_change != "unchanged":
            lyrics_changed.append((o, n))
            if lyrics_change == "added":
                lyrics_added.append((o, n))
            elif lyrics_change == "removed":
                lyrics_removed.append((o, n))
        if o.get("audio_readable") != n.get("audio_readable"):
            readable_changed.append((o, n))

    def pmap(playlists):
        return {str(p.get("persistent_id") or p.get("name")): p for p in playlists}

    op = pmap(old_playlists)
    np = pmap(new_playlists)
    op_keys = set(op)
    np_keys = set(np)

    playlist_added = [np[k] for k in sorted(np_keys - op_keys)]
    playlist_removed = [op[k] for k in sorted(op_keys - np_keys)]
    smart_changed = []
    for k in sorted(op_keys & np_keys):
        if op[k].get("is_smart") or np[k].get("is_smart"):
            if op[k].get("smart_criteria_hash") != np[k].get("smart_criteria_hash") or op[k].get("smart_info_hash") != np[k].get("smart_info_hash"):
                smart_changed.append((op[k], np[k]))

    return locals()


def total_changes(d) -> int:
    keys = [
        "added",
        "removed",
        "rating_changed",
        "fav_changed",
        "comments_changed",
        "path_changed",
        "title_changed",
        "album_artist_changed",
        "bitrate_changed",
        "artwork_changed",
        "lyrics_changed",
        "readable_changed",
        "playlist_added",
        "playlist_removed",
        "smart_changed",
    ]
    return sum(len(d[k]) for k in keys)


def terse_diff(d) -> str:
    lines = ["NO CHANGES" if total_changes(d) == 0 else "CHANGES", ""]
    lines += [
        f"new_songs={fmt_int(len(d['added']))}",
        f"removed_songs={fmt_int(len(d['removed']))}",
        f"rating_changes_existing={fmt_int(len(d['rating_changed']))}",
        f"fav_changes_existing={fmt_int(len(d['fav_changed']))}",
        f"new_favorites={fmt_int(len(d['added_favorites']))}",
        f"removed_favorites={fmt_int(len(d['removed_favorites']))}",
        f"comment_changes={fmt_int(len(d['comments_changed']))}",
        f"path_changes={fmt_int(len(d['path_changed']))}",
        f"title_artist_album_changes={fmt_int(len(d['title_changed']))}",
        f"track_name_changes={fmt_int(len(d['track_name_changed']))}",
        f"track_artist_changes={fmt_int(len(d['track_artist_changed']))}",
        f"album_title_changes={fmt_int(len(d['album_changed']))}",
        f"album_artist_added={fmt_int(len(d['album_artist_added']))}",
        f"album_artist_modified={fmt_int(len(d['album_artist_modified']))}",
        f"album_artist_removed={fmt_int(len(d['album_artist_removed']))}",
        f"bitrate_changes={fmt_int(len(d['bitrate_changed']))}",
        f"artwork_added={fmt_int(len(d['artwork_added']))}",
        f"artwork_removed={fmt_int(len(d['artwork_removed']))}",
        f"lyrics_added={fmt_int(len(d['lyrics_added']))}",
        f"lyrics_removed={fmt_int(len(d['lyrics_removed']))}",
        f"readability_changes={fmt_int(len(d['readable_changed']))}",
        f"new_playlists={fmt_int(len(d['playlist_added']))}",
        f"removed_playlists={fmt_int(len(d['playlist_removed']))}",
        f"smart_playlist_changes={fmt_int(len(d['smart_changed']))}",
        "",
    ]
    return "\n".join(lines)


def verbose_diff(old_input, new_input, d) -> str:
    lines = header("Music Library Diff")
    lines += [f"Old input: `{old_input}`", f"New input: `{new_input}`", "", "## Summary", ""]
    lines += [
        f"- New songs: {fmt_int(len(d['added']))}",
        f"- Removed songs: {fmt_int(len(d['removed']))}",
        f"- Rating changes on existing songs: {fmt_int(len(d['rating_changed']))}",
        f"- FAV changes on existing songs: {fmt_int(len(d['fav_changed']))}",
        f"- New songs with FAV: {fmt_int(len(d['added_favorites']))}",
        f"- Removed songs with FAV: {fmt_int(len(d['removed_favorites']))}",
        f"- Comment changes: {fmt_int(len(d['comments_changed']))}",
        f"- Path changes: {fmt_int(len(d['path_changed']))}",
        f"- Title/artist/album changes: {fmt_int(len(d['title_changed']))}",
        f"- Track name changes: {fmt_int(len(d['track_name_changed']))}",
        f"- Track artist changes: {fmt_int(len(d['track_artist_changed']))}",
        f"- Album title changes: {fmt_int(len(d['album_changed']))}",
        f"- Album artist added: {fmt_int(len(d['album_artist_added']))}",
        f"- Album artist modified: {fmt_int(len(d['album_artist_modified']))}",
        f"- Album artist removed: {fmt_int(len(d['album_artist_removed']))}",
        f"- Bitrate changes: {fmt_int(len(d['bitrate_changed']))}",
        f"- Embedded artwork added: {fmt_int(len(d['artwork_added']))}",
        f"- Embedded artwork removed: {fmt_int(len(d['artwork_removed']))}",
        f"- Embedded lyrics added: {fmt_int(len(d['lyrics_added']))}",
        f"- Embedded lyrics removed: {fmt_int(len(d['lyrics_removed']))}",
        f"- Readability changes: {fmt_int(len(d['readable_changed']))}",
        f"- New playlists: {fmt_int(len(d['playlist_added']))}",
        f"- Removed playlists: {fmt_int(len(d['playlist_removed']))}",
        f"- Smart playlist changes: {fmt_int(len(d['smart_changed']))}",
        "",
    ]

    max_details = 25
    if d["added_favorites"]:
        lines += ["## First 25 New Favorite Songs", ""]
        for t in d["added_favorites"][:max_details]:
            info = analyze_comment_tokens(t.get("comments") or "", set())
            rating = info["rating"] or "missing rating"
            lines.append(f"- {t.get('artist', '')} - {t.get('name', '')} ({t.get('album', '')}) [{rating} FAV]")
        lines.append("")

    if d["rating_changed"]:
        lines += ["## First 25 Rating Changes", ""]
        for o, n, old_rating, new_rating in d["rating_changed"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}: {old_rating or 'missing'} -> {new_rating or 'missing'}")
        lines.append("")

    if d["track_name_changed"]:
        lines += ["## First 25 Track Name Changes", ""]
        for o, n in d["track_name_changed"][:max_details]:
            lines.append(f"- {n.get('artist', '')}: `{o.get('name', '')}` -> `{n.get('name', '')}`")
        lines.append("")

    if d["track_artist_changed"]:
        lines += ["## First 25 Track Artist Changes", ""]
        for o, n in d["track_artist_changed"][:max_details]:
            lines.append(f"- {n.get('name', '')}: `{o.get('artist', '')}` -> `{n.get('artist', '')}`")
        lines.append("")

    if d["album_changed"]:
        lines += ["## First 25 Album Title Changes", ""]
        for o, n in d["album_changed"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}: `{o.get('album', '')}` -> `{n.get('album', '')}`")
        lines.append("")

    if d["album_artist_added"]:
        lines += ["## First 25 Album Artist Additions", ""]
        for o, n in d["album_artist_added"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}: added `{n.get('album_artist', '')}`")
        lines.append("")

    if d["album_artist_modified"]:
        lines += ["## First 25 Album Artist Modifications", ""]
        for o, n in d["album_artist_modified"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}: `{o.get('album_artist', '')}` -> `{n.get('album_artist', '')}`")
        lines.append("")

    if d["album_artist_removed"]:
        lines += ["## First 25 Album Artist Removals", ""]
        for o, n in d["album_artist_removed"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}: removed `{o.get('album_artist', '')}`")
        lines.append("")

    if d["artwork_added"]:
        lines += ["## First 25 Embedded Artwork Additions", ""]
        for o, n in d["artwork_added"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}")
        lines.append("")

    if d["artwork_removed"]:
        lines += ["## First 25 Embedded Artwork Removals", ""]
        for o, n in d["artwork_removed"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}")
        lines.append("")

    if d["lyrics_added"]:
        lines += ["## First 25 Embedded Lyrics Additions", ""]
        for o, n in d["lyrics_added"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}")
        lines.append("")

    if d["lyrics_removed"]:
        lines += ["## First 25 Embedded Lyrics Removals", ""]
        for o, n in d["lyrics_removed"][:max_details]:
            lines.append(f"- {n.get('artist', '')} - {n.get('name', '')}")
        lines.append("")

    if d["smart_changed"]:
        lines += ["## Smart Playlist Changes", ""]
        for o, n in d["smart_changed"][:max_details]:
            lines.append(f"- {n.get('name')}: criteria {o.get('smart_criteria_hash')} -> {n.get('smart_criteria_hash')}; info {o.get('smart_info_hash')} -> {n.get('smart_info_hash')}")
        lines.append("")

    return "\n".join(lines)


def run(args) -> int:
    config = load_config(getattr(args, "config", None))
    known_tokens = set(DEFAULT_KNOWN_TOKENS)
    known_tokens.update(config.get("known_tokens", []) or [])
    known_tokens.update(args.known_token or [])

    old_input = read_diff_input(args.old)
    new_input = read_diff_input(args.new)

    d = analyze_diff(
        old_input["tracks"],
        new_input["tracks"],
        old_input["playlists"],
        new_input["playlists"],
        known_tokens,
    )

    if args.format == "json":
        report, code = diff_json_report(old_input["path"], new_input["path"], d)
        return write_or_print(report, args.markdown) or code

    report = terse_diff(d) if args.terse else verbose_diff(old_input["path"], new_input["path"], d)
    return write_or_print(report, args.markdown)


def register(sub):
    p = sub.add_parser("diff", help="Compare Apple library XML files or musicaudit snapshot JSON files.")
    p.add_argument("--config")
    p.add_argument("--old", required=True)
    p.add_argument("--new", required=True)
    p.add_argument("--markdown", "-o")
    p.add_argument("--known-token", action="append", default=[])
    p.add_argument("--terse", action="store_true")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.set_defaults(func=run)
