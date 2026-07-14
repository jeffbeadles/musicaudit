from .base import Rule, RuleResult, register_rule


@register_rule
class EmptyStandardPlaylistRule(Rule):
    id = "empty-standard-playlist"
    level = "WARN"
    description = "Empty standard playlists"
    long_description = "Standard iTunes playlists that have no songs"

    def run(self, library, core):
        # Empty smart playlists are not errors. They are often validation checks.
        empty_standard = [p for p in core["empty_playlists"] if not p["is_smart"]]
        return RuleResult(self.id, self.level, self.description, empty_standard)
