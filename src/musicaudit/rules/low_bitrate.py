from .base import Rule, RuleResult, register_rule


@register_rule
class LowBitrateRule(Rule):
    id = "low-bitrate"
    level = "WARN"
    description = "Tracks below configured bitrate threshold"
    long_description = "Tracks that have bitrates below configured threshold"

    def run(self, library, core):
        threshold = int(
            self.config.get("threshold", self.config.get("low_bitrate", 256))
        )
        desc = f"Tracks below {threshold} kbps"
        return RuleResult(self.id, self.level, desc, core["low_bitrate_tracks"])
