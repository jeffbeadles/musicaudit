from .base import Rule, RuleResult, register_rule


@register_rule
class DuplicateTrackRule(Rule):
    id = "duplicate-track"
    level = "WARN"
    description = "Duplicate Artist/Album/Title groups"
    long_description = "Tracks that have the same artist, album, and title"

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, core["duplicates"])
