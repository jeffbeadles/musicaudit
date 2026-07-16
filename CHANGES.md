
# Version <TBD>

### Added support to export embedded lyric data in the snapshots
### Added contrib/count_by_artist.py, a utility to display artists ranked by the number of songs in your collection, using the musicaudit snapshot data.
### Added README.md to the contrib/ directory


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

