from .base import Rule, RuleResult, register_rule


@register_rule
class UnknownTokenRule(Rule):
    id = "unknown-token"
    level = "WARN"
    description = "Unknown comment tokens"
    long_description = "Songs with unknown data in the comment field"

    def run(self, library, core):
        items = [
            {"token": token, "count": count}
            for token, count in sorted(core["unknown_token_counts"].items())
        ]
        return RuleResult(self.id, self.level, self.description, items)
