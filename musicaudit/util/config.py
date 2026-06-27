from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None


DEFAULT_CONFIG_PATHS = [
    "~/.config/musicaudit/config.yaml",
    "~/.musicaudit.yaml",
]


def expand_path(path: str | Path) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(path)))).resolve()


def load_config(path: Optional[str]) -> Dict[str, Any]:
    candidates = []
    if path:
        candidates.append(expand_path(path))
    else:
        candidates.extend(expand_path(p) for p in DEFAULT_CONFIG_PATHS)

    for p in candidates:
        if p.exists():
            if yaml is None:
                raise RuntimeError(
                    f"Config file found at {p}, but PyYAML is not installed. "
                    "Install with: python3 -m pip install pyyaml"
                )
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise RuntimeError(f"Config file must contain a mapping: {p}")
            return data

    return {}
