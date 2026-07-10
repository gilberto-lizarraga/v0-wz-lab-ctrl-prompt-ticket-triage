"""Canonical ticket model + normalization. Section 4 of the plan.

Degradation rule: optional fields may be absent; nothing invents defaults.
cluster_hint is evaluation-only and is dropped here explicitly.
"""
from __future__ import annotations

import re

from .util import parse_ts

# declared_priority → integer scale 0..4 (0 = most severe)
PRIORITY_MAP = {
    "p0": 0, "p1": 0, "p2": 1, "p3": 2, "p4": 3,
    "urgent": 0, "high": 1, "normal": 2, "medium": 2, "low": 3,
}
PRIORITY_LABEL = {0: "P1", 1: "P2", 2: "P3", 3: "P4", 4: "P4"}

STATUS_MAP = {
    "new": "open", "open": "open", "to do": "open",
    "pending": "in_progress", "in progress": "in_progress",
    "solved": "resolved", "done": "resolved", "closed": "resolved",
    "resolved": "resolved",
}

REQUIRED = ("id", "title", "body", "created_at")

# fields the loader must NEVER promote into the engine
_EVAL_ONLY = {"cluster_hint"}


def normalize_priority(raw) -> int | None:
    if raw is None:
        return None
    key = str(raw).strip().lower()
    return PRIORITY_MAP.get(key)


def normalize_status(raw) -> str | None:
    if raw is None:
        return None
    return STATUS_MAP.get(str(raw).strip().lower(), "open")


def canonicalize(raw: dict) -> tuple[dict | None, str | None]:
    """Return (canonical_ticket, discard_reason). Drops eval-only fields."""
    body = raw.get("body") or raw.get("description") or raw.get("summary") or ""
    ticket = {
        "id": raw.get("id"),
        "title": raw.get("title") or "",
        "body": body,
        "created_at": raw.get("created_at"),
        "source": raw.get("source"),
        "reporter": raw.get("reporter"),
        "declared_priority": normalize_priority(raw.get("priority")
                                                if "priority" in raw
                                                else raw.get("declared_priority")),
        "status": normalize_status(raw.get("status")),
        "resolution_text": raw.get("resolution_text") or raw.get("resolution"),
        "raw_extra": {k: v for k, v in raw.items()
                      if k not in {"id", "title", "body", "description", "summary",
                                   "created_at", "source", "reporter", "priority",
                                   "declared_priority", "status", "resolution_text",
                                   "resolution"} and k not in _EVAL_ONLY},
    }
    # validate REQUIRED
    for field in REQUIRED:
        if not ticket.get(field):
            return None, f"missing_{field}"
    if parse_ts(ticket["created_at"]) is None:
        return None, "missing_created_at"
    return ticket, None


_PII_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PII_TOKEN = re.compile(r"\b[A-Za-z0-9]{20,}\b")


def redact(ticket: dict) -> dict:
    for field in ("title", "body"):
        val = ticket.get(field) or ""
        val = _PII_EMAIL.sub("[email]", val)
        val = _PII_TOKEN.sub("[token]", val)
        ticket[field] = val
    return ticket
