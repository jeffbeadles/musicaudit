from .base import Rule, RuleResult, register_rule


@register_rule
class InvalidRatingRule(Rule):
    id = "invalid-rating"
    level = "ERROR"
    description = "Tracks with invalid or multiple S# rating tokens"

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, core["invalid_tracks"])
