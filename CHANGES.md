
# Version 1.0.2 (PENDING RELEASE)

##   Change for issue #4, allow rules to be disabled in config file
###   Rule selection criteria:
        --rule on the command line overrides all configuration settings.

        Otherwise, all rules are selected by default.
        enabled_rules limits the selection to the listed rules (allow list)
        disabled_rules removes listed rules from the selection (deny list)
        The resulting rule set is evaluated

##   Added musicaudit rules --show-rules command, to show rules & description
##   Added homebrew release to the roadmap
##   Added CHANGES.md to the README, and Pypi release page

---
# Version 1.0.1

##   Added support for python 3.9
##   Added contrib/ directory, and the first two examples;
       FILTER_SNAPSHOT_EXAMPLE.sh and SHOW_MISSING_LYRIC_FILES.sh
##   Added regression test for fix command

---
# Version 1.0.0

##   First stable, non-beta release

