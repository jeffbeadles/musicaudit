from __future__ import annotations

import importlib
import pkgutil

from .base import registered_rule_classes


def discover_rules():
    # Import every module in this package so @register_rule decorators run.
    package_name = __name__
    for module_info in pkgutil.iter_modules(__path__):
        name = module_info.name
        if name in {"base"} or name.startswith("_"):
            continue
        importlib.import_module(f"{package_name}.{name}")
    return registered_rule_classes()
