from .base import Rule, RuleResult, register_rule


@register_rule
class MissingRatingRule(Rule):
    id = "missing-rating"
    level = "ERROR"
    description = "Tracks missing S# rating token"

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, core["unrated_tracks"])
