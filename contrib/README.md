# musicaudit CONTRIB

## This is a collection of tools and utilities that can be used with musicaudit.

Many of them are used along with the snapshot data, which can provide a lot
of information about your collection quickly and easily.

These are just examples and samples, and are meant both as tools that can
be used directly, as well as to inspire what could be done.

If you have something you would like added, please file an issue on github.

----------

* FILTER_SNAPSHOT_EXAMPLE.sh - Will output a single line per track in your
  collection with the specified metadata you desire, optionally in csv format
```code
   musicaudit snapshot --path ~/Music | FILTER_SNAPSHOT_EXAMPLE.sh [csv]
```

* SHOW_MISSING_LYRIC_FILES.sh - Will run musicaudit, and show a list of
  files that are missing embedded lyrics.  It is an example that
  automatically calls musicaudit for you.
```code
   SHOW_MISSING_LYRIC_FILES.sh --path ~/Music
```

* count_by_artist.py - Will output a list of the artists in your
  collection, ranked by the number of songs by each artist.
```code
   musicaudit snapshot --path ~/Music | count_by_artist.py
```


