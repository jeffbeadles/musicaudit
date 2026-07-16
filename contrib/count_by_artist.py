#!/usr/bin/env python3
"""
This utility takes the input from musicaudit snapshot, and returns a
report of the number of songs in the collection by each artist.

It is called like:

$ musicaudit snapshot --path ... | count_by_artist.py
"""

import collections
import json
import sys

if sys.stdin.isatty():
    print(
        "Error: This utility requires input from musicaudit piped to it.",
        file=sys.stderr,
    )
    print("Usage: musicaudit snapshot --path ... | count_by_artist.py", file=sys.stderr)
    sys.exit(1)

try:
    # Parse JSON from musicaudit
    data = json.load(sys.stdin)

    # Count all occurrences of each artist
    tracks = data.get("tracks", [])
    artists = [track.get("artist") for track in tracks if track.get("artist")]
    artist_counts = collections.Counter(artists)
    track_count = len(tracks)

    # Print the total number of artists
    print(f"Total Artists: {len(artist_counts)}, Songs: {track_count}\n")
    print(f"{'Rank':<4} | {'Count':<6} | Artist\n{'-' * 30}")

    # Sort by count (largest first) and then alphabetically by name
    # Print each artist and count of their songs in the collection,
    # largest count first.
    rank = 1
    for artist, count in artist_counts.most_common():
        print(f"{rank:>4} | {count:>6} | {artist}")
        rank = rank + 1

except (json.JSONDecodeError, KeyError) as e:
    print(
        f"""Error processing input: {e}
(is the input JSON?)

Typical usage is:
    musicaudit snapshot --path ... | count_by_artist.py
""",
        file=sys.stderr,
    )

    sys.exit(1)
