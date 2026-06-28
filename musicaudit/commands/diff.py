from __future__ import annotations

import collections

from ..model import analyze_comment_tokens, DEFAULT_KNOWN_TOKENS
from ..providers.applemusic import read_plist, extract_tracks, extract_playlists
from ..util.config import expand_path, load_config
from ..util.formatting import fmt_int, write_or_print
from ..reports.markdown import header
from ..reports.json import diff_json_report


def track_key(t):
    return str(t.get("persistent_id") or t.get("track_id"))


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
        if str(o.get("path")) != str(n.get("path")):
            path_changed.append((o, n))
        if (o.get("name"), o.get("artist"), o.get("album")) != (n.get("name"), n.get("artist"), n.get("album")):
            title_changed.append((o, n))

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
        if op[k]["is_smart"] or np[k]["is_smart"]:
            if op[k]["smart_criteria_hash"] != np[k]["smart_criteria_hash"] or op[k]["smart_info_hash"] != np[k]["smart_info_hash"]:
                smart_changed.append((op[k], np[k]))

    return locals()


def terse_diff(d) -> str:
    total_changes = sum(
        len(d[k])
        for k in [
            "added",
            "removed",
            "rating_changed",
            "fav_changed",
            "comments_changed",
            "path_changed",
            "title_changed",
            "playlist_added",
            "playlist_removed",
            "smart_changed",
        ]
    )
    lines = ["NO CHANGES" if total_changes == 0 else "CHANGES", ""]
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
        f"new_playlists={fmt_int(len(d['playlist_added']))}",
        f"removed_playlists={fmt_int(len(d['playlist_removed']))}",
        f"smart_playlist_changes={fmt_int(len(d['smart_changed']))}",
        "",
    ]
    return "\n".join(lines)


def verbose_diff(old_xml, new_xml, d) -> str:
    lines = header("Music Library Diff")
    lines += [f"Old XML: `{old_xml}`", f"New XML: `{new_xml}`", "", "## Summary", ""]
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

    if d["smart_changed"]:
        lines += ["## Smart Playlist Changes", ""]
        for o, n in d["smart_changed"][:max_details]:
            lines.append(f"- {n.get('name')}: criteria {o['smart_criteria_hash']} -> {n['smart_criteria_hash']}; info {o['smart_info_hash']} -> {n['smart_info_hash']}")
        lines.append("")

    return "\n".join(lines)


def run(args) -> int:
    config = load_config(getattr(args, "config", None))
    known_tokens = set(DEFAULT_KNOWN_TOKENS)
    known_tokens.update(config.get("known_tokens", []) or [])
    known_tokens.update(args.known_token or [])

    old_xml = expand_path(args.old)
    new_xml = expand_path(args.new)

    old_plist = read_plist(old_xml)
    new_plist = read_plist(new_xml)

    d = analyze_diff(
        extract_tracks(old_plist),
        extract_tracks(new_plist),
        extract_playlists(old_plist),
        extract_playlists(new_plist),
        known_tokens,
    )

    if args.format == "json":
        report, code = diff_json_report(old_xml, new_xml, d)
        return write_or_print(report, args.markdown) or code

    report = terse_diff(d) if args.terse else verbose_diff(old_xml, new_xml, d)
    return write_or_print(report, args.markdown)


def register(sub):
    p = sub.add_parser("diff", help="Compare two exported Apple Music/iTunes XML files.")
    p.add_argument("--config")
    p.add_argument("--old", required=True)
    p.add_argument("--new", required=True)
    p.add_argument("--markdown", "-o")
    p.add_argument("--known-token", action="append", default=[])
    p.add_argument("--terse", action="store_true")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.set_defaults(func=run)
