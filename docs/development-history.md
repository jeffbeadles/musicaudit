
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

It was also used to detect a major metadata corruption issue when a 3rd party tool
(who will remain nameless and blameless) was used to update missing album art that
also corrupted other metadata in the music collection.

This event drove the creation of the snapshot/diff functionality, to be able to
detect issues like this in the future before they become widespread.

Many of these issues would not have been discovered without the
validation rules implemented by musicaudit.
