
# Version TBD

### Fixed bug where exported lyric data was not always a string (sometimes a list). It's a string.
### Added contrib/snapshot_rating-fav-lyrics-csv.py - snapshot consumer for data exporting



# Version 1.0.3 (2026.07.17)

### Fixed bug where provider name was always "none" in snapshots, and added regression tests
### Added support to export embedded lyric data in the snapshots
### Added support for .json.gz input in musicaudit diff --old/--new
### Added README.md to the contrib/ directory
### Added contrib/count_by_artist.py, a utility to display artists ranked by the number of songs in your collection, using the musicaudit snapshot data.
### Changes for links in README.md and pyproject.toml so they'll work on pypi
### Updated roadmap for disabled_rules and homebrew changes completed.


# Version 1.0.2 (2026.07.13)

###   Change for issue #4, allow rules to be disabled in config file
####   Rule selection criteria:
        --rule on the command line overrides all configuration settings.

        Otherwise, all rules are selected by default.
        enabled_rules limits the selection to the listed rules (allow list)
        disabled_rules removes listed rules from the selection (deny list)
        The resulting rule set is evaluated

###   Added musicaudit rules --show-rules command, to show rules & description
###   Added support for installing via homebrew
###   Added CHANGES.md to the README, and Pypi release page

---
# Version 1.0.1

###   Added support for python 3.9
###   Added contrib/ directory, and the first two examples;
       FILTER_SNAPSHOT_EXAMPLE.sh and SHOW_MISSING_LYRIC_FILES.sh
###   Added regression test for fix command

---
# Version 1.0.0

###   First stable, non-beta release

