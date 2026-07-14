from .base import Rule, RuleResult, register_rule


@register_rule
class UnreadableFileRule(Rule):
    id = "unreadable-file"
    level = "ERROR"
    description = "Files unreadable by mutagen"
    long_description = "Files that are not readable, or corrupt when processing"
    requires_scan_files = True

    def run(self, library, core):
        return RuleResult(
            self.id, self.level, self.description, core["mutagen_unreadable_tracks"]
        )
