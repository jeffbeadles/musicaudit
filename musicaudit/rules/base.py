from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


@dataclass
class RuleResult:
    id: str
    level: str
    description: str
    items: List[Any]

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def passed(self) -> bool:
        return self.count == 0


class Rule:
    id = ""
    level = "WARN"
    description = ""

    def __init__(self, config=None):
        self.config = config or {}

    def run(self, library, core) -> RuleResult:
        raise NotImplementedError


_RULES = {}


def register_rule(cls):
    rule_id = getattr(cls, "id", None)
    if not rule_id:
        raise ValueError(f"Rule class {cls.__name__} is missing id")
    _RULES[rule_id] = cls
    return cls


def registered_rule_classes():
    return dict(_RULES)
