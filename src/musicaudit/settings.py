from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Settings:
    low_bitrate: int = 256
    low_bitrate_source: str = "default"
    bitrate_report: str = "summary"
    max_details: int = 25
    known_tokens: tuple[str, ...] = ("FAV",)
    enabled_rules: Optional[tuple[str, ...]] = None
    rule_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)


def resolve_settings(args, config: Dict[str, Any]) -> Settings:
    """
    Single source of truth for effective settings.

    Precedence for low_bitrate:
      1. CLI --low-bitrate
      2. rules.low-bitrate.threshold or rules.low-bitrate.minimum
      3. global low_bitrate
      4. default 256
    """
    rules_cfg = config.get("rules", {}) or {}
    low_rule_cfg = rules_cfg.get("low-bitrate", {}) or {}

    if getattr(args, "low_bitrate", None) is not None:
        low_bitrate = int(args.low_bitrate)
        low_bitrate_source = "cli"
    elif "threshold" in low_rule_cfg:
        low_bitrate = int(low_rule_cfg["threshold"])
        low_bitrate_source = "rule"
    elif "minimum" in low_rule_cfg:
        low_bitrate = int(low_rule_cfg["minimum"])
        low_bitrate_source = "rule"
    elif "low_bitrate" in config:
        low_bitrate = int(config["low_bitrate"])
        low_bitrate_source = "config"
    else:
        low_bitrate = 256
        low_bitrate_source = "default"

    if getattr(args, "max_details", None) is not None:
        max_details = int(args.max_details)
    else:
        max_details = int(config.get("max_details", 25))

    if getattr(args, "verbose", False) and max_details == 25:
        max_details = 100

    bitrate_report = getattr(args, "bitrate_report", None) or config.get(
        "bitrate_report", "summary"
    )

    known = set(config.get("known_tokens", []) or [])
    known.add("FAV")
    known.update(getattr(args, "known_token", []) or [])

    # Rule-specific allowed tokens are part of the effective token vocabulary.
    # Example:
    #
    # rules:
    #   unknown-token:
    #     allowed:
    #       - LIVE
    #       - DEMO
    unknown_token_cfg = rules_cfg.get("unknown-token", {}) or {}
    known.update(unknown_token_cfg.get("allowed", []) or [])

    enabled = getattr(args, "rule", None) or config.get("enabled_rules")
    enabled_tuple = tuple(enabled) if enabled else None

    return Settings(
        low_bitrate=low_bitrate,
        low_bitrate_source=low_bitrate_source,
        bitrate_report=bitrate_report,
        max_details=max_details,
        known_tokens=tuple(sorted(known)),
        enabled_rules=enabled_tuple,
        rule_config=rules_cfg,
    )
