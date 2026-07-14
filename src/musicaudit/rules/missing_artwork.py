from .base import Rule, RuleResult, register_rule


@register_rule
class MissingArtworkRule(Rule):
    id = "missing-artwork"
    level = "WARN"
    description = "Tracks missing embedded artwork"
    long_description = "Songs that do not have artwork embedded"
    requires_scan_files = True

    def run(self, library, core):
        return RuleResult(
            self.id, self.level, self.description, core["artwork_missing_tracks"]
        )
