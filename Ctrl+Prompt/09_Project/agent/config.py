"""Config loading. Prefers YAML if PyYAML is present, else JSON. Stdlib fallback."""
from __future__ import annotations

import json
import os

try:                      # optional: nicer YAML configs in production
    import yaml           # type: ignore
    _HAVE_YAML = True
except ImportError:
    _HAVE_YAML = False

TAXONOMY_JSON = "taxonomy.json"
TAXONOMY_YAML = "taxonomy.yaml"
DRAFT_JSON = os.path.join("data", "taxonomy.draft.json")


def _load(path: str):
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yaml", ".yml")) and _HAVE_YAML:
            return yaml.safe_load(fh)
        return json.load(fh)


def load_taxonomy():
    """Return the approved taxonomy dict, or None if not approved yet."""
    for path in (TAXONOMY_YAML, TAXONOMY_JSON):
        if os.path.exists(path):
            return _load(path)
    return None


def save_taxonomy(obj, approved: bool = False):
    path = TAXONOMY_JSON if approved else DRAFT_JSON
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    return path


def validate_weights(taxonomy) -> None:
    w = taxonomy["weights"]
    total = round(sum(w.values()), 6)
    if total != 1.0:
        raise SystemExit(f"FATAL: taxonomy weights must sum to 1.0 (got {total})")
