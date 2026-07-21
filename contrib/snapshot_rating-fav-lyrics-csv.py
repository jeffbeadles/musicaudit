#!/usr/bin/env python3
"""
Read musicaudit snapshot JSON from standard input and report each track's
rating, favorite status, embedded-lyrics length, and path.

Typical usage:

    musicaudit snapshot --path ... | snapshot_rating-fav-lyrics.py [args]
"""

import json
import re
import sys
import csv
import argparse


def main():

    parser = argparse.ArgumentParser(
        description="Consume musicaudit snapshot json, and create csv file to be used for importing into other music programs.",
        epilog=(
            """
            Typical usage:
    musicaudit snapshot --path ... | %(prog)s [args]
    """
        ),
    )
    parser.add_argument(
        "--plexmode",
        action="store_true",
        default=False,
        help="Enable transformations for plex for ratings and favorites (default: off)",
    )
    parser.add_argument(
        "--lyrics",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Include lyrics in csv file (default: --no-lyrics)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w", encoding="utf-8"),
        help="Output file for results (default stdout)",
        default=sys.stdout,
    )

    args = parser.parse_args()

    if sys.stdin.isatty():
        print(
            f"""Error: This utility requires musicaudit snapshot JSON on standard input.
            See {sys.argv[0]} --help for more information""",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(
            f"""Error processing input: {error}

    Error: This utility requires musicaudit snapshot JSON on standard input.
    See {sys.argv[0]} --help for more information
    """,
            file=sys.stderr,
        )
        sys.exit(1)

    csv_header = ["Path", "Rating", "Favorite", "Lyrics"]

    with args.output as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_header)

        tracks = data.get("tracks")
        if not isinstance(tracks, list):
            print(
                "Error: Input does not appear to be musicaudit snapshot JSON "
                "(missing or invalid 'tracks' list).",
                file=sys.stderr,
            )
            sys.exit(1)

        for track in tracks:
            comment = track.get("comments") or ""
            path = track.get("path") or ""
            lyrics = track.get("embedded_lyrics")

            tokens = set(comment.split())

            rating = next(
                (token[1:] for token in tokens if re.fullmatch(r"S[1-5]", token)),
                0,
            )

            favorite = "YES" if "FAV" in tokens else ""

            if not args.lyrics:  # Lyrics disabled?
                lyrics = ""
            elif lyrics is None:  # No lyrics available?
                lyrics = ""
            elif not isinstance(lyrics, str):  # Lyrics are some unknown type? (bad)
                print(
                    f"Error: Unexpected embedded_lyrics type for {path}: ",
                    type(lyrics),
                    file=sys.stderr,
                )
                print(f"{lyrics}")
                sys.exit(1)

            if args.plexmode:
                # Transformations for plex
                rating = int(rating) * 2  # plex is 0-10 not 0-5
                favorite = int(bool(favorite))  # 1 or 0

            writer.writerow([path, rating, favorite, lyrics])


if __name__ == "__main__":
    main()
