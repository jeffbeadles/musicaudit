#!/bin/sh
# This will filter a snapshot dump to only output specified fields.
# If called with the argument csv, it will output in csv format. The default is JSON.
# Called as musicaudit snapshot --path /path/ | FILTER_SNAPSHOT_EXAMPLE.sh [csv]
#
# Note: This requires jq to be in your path

# These are the fields to be output.
Q='["Artist", "Album Artist", "Album", "Sample Rate", "Genre", "Song Name", "Path"], (.tracks[] | [.artist, .album_artist, .album, .sample_rate, .genre, .name, .path])'

case "$1" in
   csv|CSV) Q="$Q | @csv"; shift;;
esac

exec jq -r "$Q"
# Not reached...
#EOF
