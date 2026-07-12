#!/bin/sh
# This utility will show the paths to files that are missing lyrics
# Run it as SHOW_MISSING_LYRIC_FILES.sh --path ~/Music
# 
# It requires musicaudit and jq to be in your path

ERRORS=""
for cmd in musicaudit jq ; do
   if ! command -v "$cmd" >/dev/null 2>&1; then
      echo "Error: This requires $cmd to be in your path" >&2
      ERRORS="YES"
   fi
done

test -n "$ERRORS" && exit 1 # Exit if any command was not found

exec musicaudit rules \
   --rule missing-lyrics \
   --format json \
   "$@" | 
   jq -r '.rules[].items[].path'

# Not reached
