from .base import Rule, RuleResult, register_rule


@register_rule
class XmlTagMismatchRule(Rule):
    id = "xml-tag-mismatch"
    level = "WARN"
    description = "XML metadata differs from embedded file tags"
    long_description = "Songs with mismatched XML and song tag data"
    requires_scan_files = True

    def run(self, library, core):
        return RuleResult(self.id, self.level, self.description, core["tag_mismatches"])
