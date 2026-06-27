from .base import Rule, RuleResult, register_rule


@register_rule
class DuplicateTrackRule(Rule):
    id = "duplicate-track"
    level = "WARN"
    description = "Duplicate Artist/Album/Title groups"

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, core["duplicates"])
