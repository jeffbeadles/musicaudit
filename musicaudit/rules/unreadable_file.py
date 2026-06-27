from .base import Rule, RuleResult, register_rule


@register_rule
class UnreadableFileRule(Rule):
    id = "unreadable-file"
    level = "ERROR"
    description = "Files unreadable by mutagen"
    requires_scan_files = True

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, [None] * core["mutagen_unreadable"])
