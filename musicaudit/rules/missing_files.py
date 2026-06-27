from .base import Rule, RuleResult, register_rule


@register_rule
class MissingFilesRule(Rule):
    id = "missing-files"
    level = "ERROR"
    description = "XML references files that do not exist"

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, core["file_missing"])
