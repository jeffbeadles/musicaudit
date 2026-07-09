from __future__ import annotations

from typing import List, Optional

from . import discover_rules


def rule_config(
    config: dict, rule_id: str, low_bitrate: int, low_bitrate_source: str = "default"
) -> dict:
    rules_cfg = config.get("rules", {}) or {}
    specific = dict(rules_cfg.get(rule_id, {}) or {})
    merged = dict(specific)
    merged["threshold"] = int(low_bitrate)
    merged["low_bitrate"] = int(low_bitrate)
    merged["low_bitrate_source"] = low_bitrate_source
    return merged


# Get unfiltered list of all rules, for help/usage
def find_rules(library):
    classes = discover_rules()

    selected = sorted(classes.keys())

    return selected


def run_rules(
    library,
    core,
    scan_files: bool,
    low_bitrate: int,
    enabled_rules: Optional[List[str]] = None,
    low_bitrate_source: str = "default",
):
    classes = discover_rules()
    config = library.config or {}

    if enabled_rules:
        selected = enabled_rules
    else:
        configured = config.get("enabled_rules")
        selected = configured if configured else sorted(classes.keys())

    results = []
    for rule_id in selected:
        cls = classes.get(rule_id)
        if cls is None:
            results.append(_unknown_rule_result(rule_id))
            continue

        if getattr(cls, "requires_scan_files", False) and not scan_files:
            continue

        cfg = rule_config(config, rule_id, low_bitrate, low_bitrate_source)
        rule = cls(cfg)

        level_override = cfg.get("level") or cfg.get("severity")
        if level_override:
            rule.level = str(level_override).upper()

        enabled = cfg.get("enabled", True)
        if enabled is False:
            continue

        results.append(rule.run(library, core))

    return results


def _unknown_rule_result(rule_id: str):
    from .base import RuleResult

    return RuleResult(
        "unknown-rule",
        "ERROR",
        f"Configured rule does not exist: {rule_id}",
        [{"rule": rule_id}],
    )


def rules_have_failures(rules, fail_warnings: bool = False) -> bool:
    for r in rules:
        if r.count <= 0:
            continue
        if r.level == "ERROR":
            return True
        if fail_warnings and r.level == "WARN":
            return True
    return False
