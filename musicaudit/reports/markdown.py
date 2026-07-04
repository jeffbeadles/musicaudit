from __future__ import annotations

import datetime as dt
import math
import collections

from .. import __version__
from ..analysis import bitrate_label, bitrate_bucket
from ..rules.engine import rules_have_failures
from ..util.formatting import fmt_int, fmt_percent


def header(title: str, xml_path=None) -> list[str]:
    lines = [f"# {title}", ""]
    lines.append(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if xml_path:
        lines.append(f"Library: `{xml_path}`")
    lines.append(f"musicaudit version: {__version__}")
    lines.append("")
    return lines


def append_track(lines, t, prefix="-"):
    lines.append(f"{prefix} {t.get('artist', '')} - {t.get('name', '')} ({t.get('album', '')})")


def append_details(lines, core, low_bitrate: int, max_details: int, playlists=None):
    if max_details <= 0:
        lines.append("Detailed listings suppressed because `--max-details 0` was used.")
        lines.append("")
        return

    if core["unknown_token_counts"]:
        lines.append(f"### Most Common Unknown Comment Tokens, Top {max_details}")
        lines.append("")
        for tok, count in core["unknown_token_counts"].most_common(max_details):
            lines.append(f"- `{tok}`: {fmt_int(count)}")
        lines.append("")

    if core["unrated_tracks"][:max_details]:
        lines.append(f"### First {max_details} Unrated Tracks")
        lines.append("")
        for t in core["unrated_tracks"][:max_details]:
            append_track(lines, t)
        lines.append("")

    if core["low_bitrate_tracks"][:max_details]:
        lines.append(f"### First {max_details} Low Bitrate Tracks Below {low_bitrate} kbps")
        lines.append("")
        for t in core["low_bitrate_tracks"][:max_details]:
            lines.append(f"- {bitrate_label(t.get('bit_rate'))}: {t.get('artist', '')} - {t.get('name', '')} ({t.get('album', '')})")
        lines.append("")

    if core["file_missing"][:max_details]:
        lines.append(f"### First {max_details} Missing Files")
        lines.append("")
        for t in core["file_missing"][:max_details]:
            lines.append(f"- {t.get('artist', '')} - {t.get('name', '')}: `{t.get('path')}`")
        lines.append("")

    if core["invalid_tracks"][:max_details]:
        lines.append(f"### First {max_details} Invalid Rating Token Tracks")
        lines.append("")
        for t in core["invalid_tracks"][:max_details]:
            lines.append(f"- {t.get('artist', '')} - {t.get('name', '')}: `{t.get('comments')}`")
        lines.append("")

    if core["duplicates"][:max_details]:
        lines.append(f"### First {max_details} Duplicate Artist/Album/Title Groups")
        lines.append("")
        for _, group in core["duplicates"][:max_details]:
            sample = group[0]
            lines.append(f"- {sample.get('artist', '')} - {sample.get('album', '')} - {sample.get('name', '')}: {len(group)} copies")
        lines.append("")

    if core.get("tag_mismatches") and core["tag_mismatches"][:max_details]:
        lines.append(f"### First {max_details} XML/File Tag Mismatches")
        lines.append("")
        for t, label, xml_val, tag_val in core["tag_mismatches"][:max_details]:
            lines.append(f"- {t.get('artist', '')} - {t.get('name', '')}: {label}: XML=`{xml_val}` File=`{tag_val}`")
        lines.append("")


def health_report(library, core, scan_files: bool, low_bitrate: int) -> str:
    lines = header("Music Library Health Check", library.xml_path)
    empty_smart = len([p for p in core["empty_playlists"] if p["is_smart"]])
    empty_standard = len([p for p in core["empty_playlists"] if not p["is_smart"]])

    lines += [
        "## Health Check",
        "",
        f"- Songs: {fmt_int(len(library.tracks))}",
        f"- Artists: {fmt_int(len(core['artists']))}",
        f"- Albums: {fmt_int(len(core['albums']))}",
        f"- Playlists: {fmt_int(len(library.playlists))}",
        f"- Smart playlists: {fmt_int(core['smart_count'])}",
        f"- Empty smart playlists: {fmt_int(empty_smart)}",
        f"- Empty standard playlists: {fmt_int(empty_standard)}",
        f"- Missing files: {fmt_int(len(core['file_missing']))}",
        f"- Missing S# ratings: {fmt_int(len(core['unrated_tracks']))}",
        f"- Invalid/multiple S# ratings: {fmt_int(len(core['invalid_tracks']))}",
        f"- Duplicate Artist/Album/Title groups: {fmt_int(len(core['duplicates']))}",
        f"- Low bitrate tracks below {low_bitrate} kbps: {fmt_int(len(core['low_bitrate_tracks']))}",
    ]
    if scan_files:
        lines += [
            f"- Missing embedded lyrics: {fmt_int(core['lyrics_missing'])}",
            f"- Missing embedded artwork: {fmt_int(core['artwork_missing'])}",
            f"- XML/file tag mismatches: {fmt_int(len(core['tag_mismatches']))}",
        ]
    lines.append("")
    return "\n".join(lines)


def terse_health(library, core, scan_files: bool, low_bitrate: int) -> str:
    fail_checks = [
        len(core["file_missing"]),
        len(core["unrated_tracks"]),
        len(core["invalid_tracks"]),
    ]
    if scan_files:
        fail_checks.extend([core["mutagen_unreadable"]])

    status = "FAIL" if any(x > 0 for x in fail_checks) else "PASS"
    empty_smart = len([p for p in core["empty_playlists"] if p["is_smart"]])
    empty_standard = len([p for p in core["empty_playlists"] if not p["is_smart"]])

    lines = [
        status,
        "",
        f"tracks={fmt_int(len(library.tracks))}",
        f"playlists={fmt_int(len(library.playlists))}",
        f"smart_playlists={fmt_int(core['smart_count'])}",
        f"empty_smart_playlists={fmt_int(empty_smart)}",
        f"empty_standard_playlists={fmt_int(empty_standard)}",
        f"missing_files={fmt_int(len(core['file_missing']))}",
        f"missing_ratings={fmt_int(len(core['unrated_tracks']))}",
        f"invalid_ratings={fmt_int(len(core['invalid_tracks']))}",
        f"duplicates={fmt_int(len(core['duplicates']))}",
        f"low_bitrate_below_{low_bitrate}kbps={fmt_int(len(core['low_bitrate_tracks']))}",
    ]
    if scan_files:
        lines += [
            f"missing_lyrics={fmt_int(core['lyrics_missing'])}",
            f"missing_artwork={fmt_int(core['artwork_missing'])}",
            f"unreadable_files={fmt_int(core['mutagen_unreadable'])}",
            f"xml_file_tag_mismatches={fmt_int(len(core['tag_mismatches']))}",
        ]
    lines.append("")
    return "\n".join(lines)


def summary_report(library, core, scan_files: bool, bitrate_report_mode: str, low_bitrate: int, max_details: int) -> str:
    lines = header("Music Library Audit", library.xml_path)
    lines.append(health_report(library, core, scan_files, low_bitrate).split("## Health Check", 1)[1].strip())
    lines.append("")

    total = len(library.tracks)
    lines += ["## Ratings from Comment Tokens", ""]
    for i in range(5, 0, -1):
        key = f"S{i}"
        count = core["rating_counts"][key]
        lines.append(f"- {key}: {fmt_int(count)} ({fmt_percent(count, total)})")
    lines.append(f"- Unrated / missing S#: {fmt_int(len(core['unrated_tracks']))} ({fmt_percent(len(core['unrated_tracks']), total)})")
    lines.append(f"- FAV: {fmt_int(core['favorites'])} ({fmt_percent(core['favorites'], total)})")
    lines.append("")

    lines += ["## Formats", ""]
    for ext, count in core["ext_counts"].most_common():
        lines.append(f"- {ext}: {fmt_int(count)}")
    lines.append("")

    append_bitrate(lines, library.tracks, bitrate_report_mode, low_bitrate)

    lines += ["## Embedded Metadata from Actual Files", ""]
    if scan_files:
        lines += [
            f"- Lyrics embedded: {fmt_int(core['lyrics_count'])}",
            f"- Lyrics missing: {fmt_int(core['lyrics_missing'])}",
            f"- Artwork embedded: {fmt_int(core['artwork_count'])}",
            f"- Artwork missing: {fmt_int(core['artwork_missing'])}",
            f"- Files unreadable by mutagen: {fmt_int(core['mutagen_unreadable'])}",
            "",
        ]
    else:
        lines += ["Skipped. Use `--scan-files` to inspect embedded lyrics and artwork directly from audio files.", ""]

    append_details(lines, core, low_bitrate, max_details, library.playlists)
    return "\n".join(lines)


def append_bitrate(lines, tracks, mode: str, low_bitrate: int):
    if mode == "none":
        return

    all_counts = collections.Counter()
    summary_counts = collections.Counter()
    low_counts = collections.Counter()

    for t in tracks:
        br = t.get("bit_rate")
        all_counts[bitrate_label(br)] += 1
        summary_counts[bitrate_bucket(br, low_bitrate)] += 1
        try:
            br_int = int(br) if br else 0
        except Exception:
            br_int = 0
        if br_int and br_int < low_bitrate:
            low_counts[bitrate_label(br)] += 1

    if mode == "summary":
        lines += ["## Bitrate Summary", ""]
        for key in ["Lossless / Hi-Res", "320 kbps and above", "256-319 kbps", f"{low_bitrate}-255 kbps", f"Below {low_bitrate} kbps", "unknown"]:
            if summary_counts[key]:
                lines.append(f"- {key}: {fmt_int(summary_counts[key])}")
        lines.append("")
    elif mode == "exceptions":
        lines += [f"## Low Bitrate Exceptions Below {low_bitrate} kbps", ""]
        if not low_counts:
            lines.append("- None")
        else:
            for label, count in sorted(low_counts.items()):
                lines.append(f"- {label}: {fmt_int(count)}")
        lines.append("")
    elif mode == "full":
        lines += ["## Bitrates from Apple Music XML", ""]
        for label, count in sorted(all_counts.items()):
            lines.append(f"- {label}: {fmt_int(count)}")
        lines.append("")


def tokens_report(library, core, max_details: int) -> str:
    lines = header("Music Library Token Audit", library.xml_path)
    total = len(library.tracks)
    lines += ["## Rating Tokens", ""]
    for i in range(5, 0, -1):
        key = f"S{i}"
        count = core["rating_counts"][key]
        lines.append(f"- {key}: {fmt_int(count)} ({fmt_percent(count, total)})")
    lines.append(f"- Missing S#: {fmt_int(len(core['unrated_tracks']))} ({fmt_percent(len(core['unrated_tracks']), total)})")
    lines.append(f"- FAV: {fmt_int(core['favorites'])} ({fmt_percent(core['favorites'], total)})")
    lines.append("")
    append_details(lines, core, 256, max_details)
    return "\n".join(lines)


def playlists_report(library, decode_output: str | None, max_details: int) -> str:
    playlists = library.playlists
    lines = header("Music Library Playlist Audit", library.xml_path)

    smart = [p for p in playlists if p["is_smart"]]
    standard = [p for p in playlists if not p["is_smart"] and not p["folder"]]
    folders = [p for p in playlists if p["folder"]]
    empty_smart = [p for p in playlists if p["is_smart"] and p["item_count"] == 0]
    empty_standard = [p for p in playlists if not p["is_smart"] and not p["folder"] and p["item_count"] == 0]

    lines += [
        "## Playlist Summary",
        "",
        f"- Total playlists: {fmt_int(len(playlists))}",
        f"- Smart playlists: {fmt_int(len(smart))}",
        f"- Standard playlists: {fmt_int(len(standard))}",
        f"- Playlist folders: {fmt_int(len(folders))}",
        f"- Empty smart playlists: {fmt_int(len(empty_smart))}",
        f"- Empty standard playlists: {fmt_int(len(empty_standard))}",
        "",
        "## Smart Playlist Inventory",
        "",
        "| Playlist | Items | Smart Criteria Hash | Smart Info Hash |",
        "|---|---:|---|---|",
    ]
    for p in sorted(smart, key=lambda x: x["name"].lower()):
        lines.append(f"| {p['name']} | {fmt_int(p['item_count'])} | `{p['smart_criteria_hash']}` | `{p['smart_info_hash']}` |")
    lines.append("")

    if max_details > 0:
        lines += [f"## Largest Playlists, First {max_details}", ""]
        for p in sorted(playlists, key=lambda x: x["item_count"], reverse=True)[:max_details]:
            kind = "folder" if p["folder"] else ("smart" if p["is_smart"] else "standard")
            lines.append(f"- {p['name']} - {fmt_int(p['item_count'])} items ({kind})")
        lines.append("")

    if decode_output:
        lines += ["## itunessmart Decode", "", "```text", decode_output, "```", ""]

    return "\n".join(lines)


def stats_report(library, core, max_details: int, histogram_scale: str, histogram_width: int) -> str:
    lines = header("Music Library Statistics", library.xml_path)
    rating_values = [v for v in core["rating_values"] if isinstance(v, int)]
    avg_rating = sum(rating_values) / len(rating_values) if rating_values else 0

    lines += ["## Ratings", "", f"- Average rating: {avg_rating:.2f}"]
    if rating_values:
        sorted_vals = sorted(rating_values)
        mid = len(sorted_vals) // 2
        median = sorted_vals[mid] if len(sorted_vals) % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        lines.append(f"- Median rating: {median:.1f}")
    lines.append("")

    lines += ["### Rating Histogram", "", f"Scale: `{histogram_scale}`", ""]
    max_count = max([core["rating_counts"][f"S{i}"] for i in range(1, 6)] or [1])
    for i in range(5, 0, -1):
        key = f"S{i}"
        count = core["rating_counts"][key]
        bar = histogram_bar(count, max_count, histogram_width, histogram_scale)
        lines.append(f"- {key}: {bar} {fmt_int(count)}")
    lines.append("")

    lines += ["## Formats", ""]
    for ext, count in core["ext_counts"].most_common():
        lines.append(f"- {ext}: {fmt_int(count)}")
    lines.append("")

    genres = collections.Counter(t.get("genre") or "unknown" for t in library.tracks)
    lines += [f"## Top Genres, First {max_details}", ""]
    for genre, count in genres.most_common(max_details):
        lines.append(f"- {genre}: {fmt_int(count)}")
    lines.append("")

    return "\n".join(lines)


def histogram_bar(count: int, max_count: int, width: int, scale: str) -> str:
    if count <= 0 or max_count <= 0:
        return ""
    if scale == "linear":
        bar_len = int((count / max_count) * width)
    elif scale == "log":
        bar_len = int((math.log10(count + 1) / math.log10(max_count + 1)) * width)
    else:
        bar_len = int((math.sqrt(count) / math.sqrt(max_count)) * width)
    return "#" * max(1, bar_len)


def rules_report(library, rules, max_details: int, fail_warnings: bool, terse: bool):
    failed = rules_have_failures(rules, fail_warnings)

    if terse:
        lines = ["FAIL" if failed else "PASS", ""]
        for r in rules:
            lines.append(f"{r.id.replace('-', '_')}={fmt_int(r.count)}")
        lines.append("")
        return "\n".join(lines), 1 if failed else 0

    lines = header("Music Library Rule Check", library.xml_path)
    lines += ["FAIL" if failed else "PASS", "", "## Rules", ""]
    lines += ["| Rule | Level | Status | Count | Description |", "|---|---|---|---:|---|"]
    for r in rules:
        status = "PASS" if r.passed else r.level
        lines.append(f"| `{r.id}` | {r.level} | {status} | {fmt_int(r.count)} | {r.description} |")
    lines.append("")

    if max_details > 0:
        lines += ["## Rule Details", ""]
        for r in rules:
            if r.count == 0:
                continue
            lines += [f"### {r.id}", "", r.description, ""]
            for item in r.items[:max_details]:
                if item is None:
                    continue
                if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], list):
                    sample = item[1][0]
                    lines.append(f"- {sample.get('artist', '')} - {sample.get('album', '')} - {sample.get('name', '')}: {len(item[1])} copies")
                elif isinstance(item, tuple) and len(item) == 4:
                    t, label, xml_val, tag_val = item
                    lines.append(f"- {t.get('artist', '')} - {t.get('name', '')}: {label}: XML=`{xml_val}` File=`{tag_val}`")
                elif isinstance(item, dict) and "token" in item:
                    lines.append(f"- `{item['token']}`: {fmt_int(item['count'])}")
                elif isinstance(item, dict):
                    lines.append(f"- {item}")
                else:
                    try:
                        lines.append(f"- {item.get('artist', '')} - {item.get('name', '')} ({item.get('album', '')})")
                    except Exception:
                        lines.append(f"- {item}")
            lines.append("")

    return "\n".join(lines), 1 if failed else 0
