"""Shared helpers: IO, tokenization, dates. Stdlib only."""
from __future__ import annotations

import json
import math
import os
import re
from datetime import datetime, timezone

DATA_DIR = os.environ.get("AGENT_DATA_DIR", "data")

_STOPWORDS = {
    "the", "a", "an", "to", "of", "for", "on", "in", "at", "is", "are", "was",
    "were", "be", "been", "and", "or", "but", "with", "this", "that", "these",
    "those", "it", "its", "as", "by", "from", "some", "no", "not", "up", "out",
    "over", "than", "then", "so", "if", "into", "their", "they", "them", "has",
    "have", "had", "user", "users", "report", "reports", "reported", "says",
    "said", "week", "last", "still", "again", "same", "about", "20", "10",
}

# Keep hyphenated tokens (checkout-service), api paths (/api/v2/x), numbers (502).
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-/\.]*")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    try:
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None


def tokenize(text: str) -> list[str]:
    text = (text or "").lower()
    toks = _TOKEN_RE.findall(text)
    return [t.strip("./-") for t in toks
            if len(t.strip("./-")) >= 2 and t.strip("./-") not in _STOPWORDS]


def ensure_data_dir() -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR


def write_json(path: str, obj) -> None:
    ensure_data_dir()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


def read_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    keys = a.keys() & b.keys()
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
