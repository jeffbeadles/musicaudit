# musicaudit

musicaudit is a read-only validation tool for your digital music collection.

It helps identify missing metadata, duplicate tracks, inconsistent tagging, and unintended changes without ever modifying your music files.

Who is musicaudit for?

* People who maintain large music collections.
* Users who edit metadata with tools like Apple Music, Fusion, MusicBrainz Picard, Mp3tag, Kid3, etc.
* Anyone who wants confidence that metadata changes didn't introduce unexpected changes.

You've spent years curating your music collection. You trust the tools you use, but mistakes happen. musicaudit helps you verify the health of your collection, detect unintended changes and missing metadata, and maintain confidence in it - all without ever modifying your collection."

musicaudit will scan your collection, either by scanning a directory structure with music files, or an iTunes Library.xml file.

It can generate reports of missing metadata like alburm artists, artwork, or lyrics.  It can also do things like finding duplicate tracks, files with low bitrates, missing files, and much more.

These reports are available in human-readable format or JSON, so they can be
processed by other programs.

Musicaudit is not a music player, tag editor, or library manager.
It is an audit and quality assurance tool, and will never change your collection.

musicaudit deliberately separates diagnosis from treatment.  It just reports facts.

----------------------

How to run musicaudit?

Installation and how to run information is in GETTING-STARTED.md, but a quick
example is:

```
musicaudit health --path ~/Music
or
musicaudit health --apple-music ~/Music/Library.xml
```

To see all available commands:

```
musicaudit --help
```

To see all options for a sub command, health for example:

```
musicaudit health --help
```


## Documentation

- [Getting Started](GETTING-STARTED.md)
- [FAQ](FAQ.md)
- [Roadmap](ROADMAP.md)
- [License](LICENSE-2.0)
- [Philosophy](docs/philosophy.md)
- [Development History](docs/development-history.md)
- [Contributing](CONTRIBUTING.md)


