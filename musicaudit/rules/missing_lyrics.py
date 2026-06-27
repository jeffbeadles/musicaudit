from .base import Rule, RuleResult, register_rule


@register_rule
class MissingLyricsRule(Rule):
    id = "missing-lyrics"
    level = "WARN"
    description = "Tracks missing embedded lyrics"
    requires_scan_files = True

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, [None] * core["lyrics_missing"])
