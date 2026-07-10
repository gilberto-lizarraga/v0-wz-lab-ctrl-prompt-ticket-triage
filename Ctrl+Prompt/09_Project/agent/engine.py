"""Engine rules R1–R7 (invariant across boards) + embeddings + clustering.

Consumes taxonomy config; does not contain domain words itself.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from .canonical import PRIORITY_LABEL
from .util import cosine, jaccard, parse_ts, tokenize

# ── entity extraction patterns (R1) ────────────────────────────────────────
_RE_API = re.compile(r"/api/v\d+/[\w\-]+")
_RE_SERVICE = re.compile(r"\b[a-z][a-z0-9]*-service\b")

# ── type markers (R2), domain-independent ──────────────────────────────────
_ERROR = ["error", "fail", "failing", "failure", "timeout", "timing out", "hang",
          "hung", "stuck", "froze", "freeze", "crash", "502", "500", "503", "504",
          "bounce", "not working", "not arrive", "never arrive", "delayed"]
_DESIRE = ["feature request", "can i get", "would like", "wants", "please add",
           "toggle", "option", "request"]
_RECUR = ["again", "still", "same as", "pattern", "recurring", "becoming a pattern",
          "continue", "twice", "no rca", "third", "fourth", "second"]
_ORDINAL = re.compile(r"(\d+)(?:st|nd|rd|th)")
_ORDINAL_WORD = {"second": 2, "third": 3, "fourth": 4, "fifth": 5}


def extract_entities(text: str, lexicon: list[str]) -> set[str]:
    low = text.lower()
    ents = set(_RE_SERVICE.findall(low)) | set(_RE_API.findall(low))
    for term in lexicon:
        if term.lower() in low:
            ents.add(term.lower())
    return ents


def recurrence_count(text: str) -> int:
    low = text.lower()
    best = 1
    for m in _ORDINAL.findall(low):
        best = max(best, int(m))
    for word, val in _ORDINAL_WORD.items():
        if word in low:
            best = max(best, val)
    if any(sig in low for sig in _RECUR):
        best = max(best, 2)
    return best


def markers(text: str) -> dict:
    low = text.lower()
    return {
        "error": any(sig in low for sig in _ERROR),
        "desire": any(sig in low for sig in _DESIRE),
        "recurrence_count": recurrence_count(low),
    }


def assign_subsystem(text: str, subsystems: dict) -> str | None:
    low = text.lower()
    best, best_hits = None, 0
    for name, cfg in subsystems.items():
        hits = sum(1 for sig in cfg.get("signals", []) if sig.lower() in low)
        if hits > best_hits:
            best, best_hits = name, hits
    return best


# ── R1: annotate every ticket ──────────────────────────────────────────────
def annotate(tickets: list[dict], taxonomy: dict) -> None:
    lexicon = taxonomy.get("entities", {}).get("lexicon", [])
    subsystems = taxonomy.get("subsystems", {})
    for t in tickets:
        text = f"{t['title']} {t['body']}"
        t["_entities"] = extract_entities(text, lexicon)
        t["_subsystem"] = assign_subsystem(text, subsystems)
        t["_markers"] = markers(text)
        t["_tokens"] = tokenize(text)


# ── R2: type gate ──────────────────────────────────────────────────────────
def type_gate(t: dict) -> str:
    m = t["_markers"]
    has_entity = bool(t["_entities"])
    if m["desire"] and not m["error"] and not has_entity:
        return "FEATURE_REQUEST"
    if m["error"] or has_entity:
        return "INCIDENT"
    return "UNKNOWN"


# ── embeddings: TF-IDF vectors (Bedrock stand-in, deterministic & offline) ──
def build_tfidf(tickets: list[dict]) -> None:
    df = Counter()
    for t in tickets:
        for tok in set(t["_tokens"]):
            df[tok] += 1
    n = len(tickets) or 1
    idf = {tok: math.log((1 + n) / (1 + d)) + 1 for tok, d in df.items()}
    for t in tickets:
        tf = Counter(t["_tokens"])
        length = len(t["_tokens"]) or 1
        t["_vec"] = {tok: (c / length) * idf[tok] for tok, c in tf.items()}


# ── R4: similarity with entity veto ────────────────────────────────────────
def similarity(a: dict, b: dict, weights: dict, window_days: float) -> float:
    ea, eb = a["_entities"], b["_entities"]
    if ea and eb and not (ea & eb):        # entity veto (hard rule)
        return 0.0
    sem = cosine(a["_vec"], b["_vec"])
    sub = 1.0 if (a["_subsystem"] and a["_subsystem"] == b["_subsystem"]) else 0.0
    ent = jaccard(ea, eb)
    da, db = parse_ts(a["created_at"]), parse_ts(b["created_at"])
    if da and db:
        tmp = math.exp(-abs((da - db).days) / max(window_days, 1))
    else:
        tmp = 0.0
    return (weights["semantic"] * sem + weights["subsystem"] * sub
            + weights["entity"] * ent + weights["temporal"] * tmp)


# ── R4: agglomerative clustering, average linkage, no predefined k ──────────
def cluster(tickets: list[dict], weights: dict, threshold: float,
            window_days: float, blind: bool = False) -> list[list[int]]:
    if blind:
        weights = {"semantic": 1.0, "subsystem": 0.0, "entity": 0.0, "temporal": 0.0}
    n = len(tickets)
    groups = [[i] for i in range(n)]

    def group_sim(g1, g2) -> float:
        if blind:  # no veto in blind mode
            vals = [cosine(tickets[i]["_vec"], tickets[j]["_vec"]) for i in g1 for j in g2]
        else:
            vals = [similarity(tickets[i], tickets[j], weights, window_days)
                    for i in g1 for j in g2]
        return sum(vals) / len(vals) if vals else 0.0

    while True:
        best, bi, bj = threshold, -1, -1
        for x in range(len(groups)):
            for y in range(x + 1, len(groups)):
                s = group_sim(groups[x], groups[y])
                if s >= best:
                    best, bi, bj = s, x, y
        if bi < 0:
            break
        groups[bi] = groups[bi] + groups[bj]
        groups.pop(bj)
    return groups


# ── R5: effective priority (cluster level) ─────────────────────────────────
def effective_priority(cluster_tickets: list[dict], severity_cfg: dict,
                       stale_age_days: int, ref_time) -> dict:
    declared = [t["declared_priority"] for t in cluster_tickets
                if t["declared_priority"] is not None]
    has_declared = bool(declared)
    base = (4 - min(declared)) if has_declared else 0  # P1(0)->4 .. P4(3)->1

    rec = max(t["_markers"]["recurrence_count"] for t in cluster_tickets)
    reporters = {t.get("reporter") for t in cluster_tickets if t.get("reporter")}
    sources = {t.get("source") for t in cluster_tickets if t.get("source")}

    stale = any(
        (t.get("status") == "open"
         and parse_ts(t["created_at"])
         and (ref_time - parse_ts(t["created_at"])).days > stale_age_days)
        for t in cluster_tickets)

    score = base
    score += severity_cfg.get("recurrence_multiplier", 2) * (rec - 1)
    score += severity_cfg.get("stale_penalty", 1) * (1 if stale else 0)
    score += severity_cfg.get("blast_radius_bonus", 1) * (1 if len(reporters) > 1 else 0)
    score += severity_cfg.get("cross_source_bonus", 1) * (1 if len(sources) > 1 else 0)

    if score >= 10:
        eff_idx = 0
    elif score >= 7:
        eff_idx = 1
    elif score >= 4:
        eff_idx = 2
    else:
        eff_idx = 3

    decl_idx = min(declared) if has_declared else None
    flag = "ALIGNED"
    if has_declared:
        if rec >= 3 and decl_idx >= 1:
            flag = "SUPPRESSED"
        elif decl_idx <= 1 and stale and eff_idx > decl_idx:
            flag = "INFLATED"

    return {
        "has_declared": has_declared,
        "declared": PRIORITY_LABEL[decl_idx] if has_declared else None,
        "effective": PRIORITY_LABEL[eff_idx],
        "severity_real": score,
        "recurrence_count": rec,
        "unique_reporters": len(reporters),
        "unique_sources": len(sources),
        "stale": stale,
        "cross_source": len(sources) > 1,
        "flag": flag,
    }


# ── R7: confidence ─────────────────────────────────────────────────────────
def confidence(cluster_tickets: list[dict]) -> str:
    n = len(cluster_tickets)
    sources = {t.get("source") for t in cluster_tickets if t.get("source")}
    if n >= 3 and len(sources) >= 2:
        return "high"
    if n >= 2:
        return "medium"
    return "low"


def silhouette(tickets: list[dict], groups: list[list[int]]) -> float:
    """Cheap silhouette over semantic cosine; 0 if not computable."""
    if len(groups) < 2:
        return 0.0
    label = {}
    for gi, g in enumerate(groups):
        for i in g:
            label[i] = gi

    def dist(i, j):
        return 1 - cosine(tickets[i]["_vec"], tickets[j]["_vec"])

    scores = []
    for i in range(len(tickets)):
        same = [dist(i, j) for j in range(len(tickets)) if j != i and label[j] == label[i]]
        a = sum(same) / len(same) if same else 0.0
        b_vals = []
        for gi, g in enumerate(groups):
            if gi == label[i]:
                continue
            other = [dist(i, j) for j in g]
            if other:
                b_vals.append(sum(other) / len(other))
        b = min(b_vals) if b_vals else 0.0
        denom = max(a, b)
        scores.append((b - a) / denom if denom else 0.0)
    return round(sum(scores) / len(scores), 3) if scores else 0.0
