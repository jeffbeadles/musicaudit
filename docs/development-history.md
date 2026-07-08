
During the development of musicaudit, the author's personal music
collection (approximately 4,500 tracks) was used as a validation corpus.

The development process uncovered and corrected more than 60 issues,
including:

- duplicate files
- missing ratings
- inconsistent comments
- metadata inconsistencies
- missing embedded artwork
- missing embedded lyrics

It was also used to detect a major metadata corruption issue after a third-party metadata editor (who will remain nameless and blameless) was used to update missing album artwork. While the intended changes were successful, the tool also made extensive unintended modifications to other metadata.

This experience led directly to the creation of the snapshot and diff commands. They allow users to capture the state of a music collection before making changes, compare it afterward, and understand exactly what changed before those changes become widespread.

Many of these issues would not have been discovered without the
validation rules implemented by musicaudit.

Also, originally musicaudit was only used by referencing the Library.xml file exported by iTunes.  This revealed a pretty substantial issue as iTunes does not store a lot of the metadata in the music files, but rather in internal databases.  This lead to the addition of an abstraction of data "providers", currently "apple-library" for iTunes, and "path" for reading the metadata directly from music files.

In the future, providers could be added for other environments, like beets, jellyfin, and others.

The future will be driven by the needs of users, balanced by the core and guiding principles of musicaudit.

