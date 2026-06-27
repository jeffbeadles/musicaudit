#!/bin/sh
set -eu

out="${1:-tests/reference-library/audio}"
mkdir -p "$out"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg is required" >&2
  exit 1
fi

make_mp3() {
  file="$1"
  title="$2"
  artist="$3"
  album="$4"
  comment="$5"
  bitrate="$6"

  ffmpeg -hide_banner -loglevel error -y \
    -f lavfi -i sine=frequency=440:duration=1 \
    -b:a "$bitrate" \
    -metadata title="$title" \
    -metadata artist="$artist" \
    -metadata album="$album" \
    -metadata comment="$comment" \
    "$out/$file"
}

make_mp3 "good.mp3" "Good Song" "Reference Artist" "Reference Album" "S5" "128k"
make_mp3 "missing-rating.mp3" "Missing Rating" "Reference Artist" "Reference Album" "" "128k"
make_mp3 "low-bitrate.mp3" "Low Bitrate" "Reference Artist" "Reference Album" "S3" "32k"
make_mp3 "duplicate-a.mp3" "Duplicate Song" "Reference Artist" "Duplicate Album" "S4" "128k"
make_mp3 "duplicate-b.mp3" "Duplicate Song" "Reference Artist" "Duplicate Album" "S4" "128k"

echo "Generated reference audio in $out"
