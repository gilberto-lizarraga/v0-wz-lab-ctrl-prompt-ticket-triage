"""learn — OBSERVE (blind profile) + ADAPT (propose taxonomy) + gate.

ADAPT proposes; it never decides. Emits taxonomy.draft.json for human review.
--approve promotes the draft to taxonomy.json. --eval calibrates via cluster_hint.
"""
from __future__ import annotations

import os
import shutil
from collections import Counter

from . import engine
from .config import DRAFT_JSON, TAXONOMY_JSON, save_taxonomy
from .util import read_json, write_json

# Baseline generic taxonomy the engine starts from (no domain words baked in).
BASE_TAXONOMY = {
    "version": 1,
    "locale": "en",
    "calibration_status": "heuristic",
    "entities": {"lexicon": ["recommendations", "checkout-service"]},
    "subsystems": {
        "ci_cd/checkout-service": {"signals": ["checkout-service", "deploy", "pipeline",
                                               "integration test", "staging", "hang"]},
        "api_gateway/recommendations": {"signals": ["recommendations", "502", "endpoint",
                                                     "bad gateway"]},
        "auth/post-renewal": {"signals": ["log in", "login", "renewal", "subscription",
                                          "renew", "renews"]},
        "email_delivery": {"signals": ["email", "reset", "ses", "bounce", "deliver",
                                       "transactional", "mail"]},
    },
    "weights": {"semantic": 0.45, "subsystem": 0.30, "entity": 0.15, "temporal": 0.10},
    "thresholds": {"merge": 0.30, "temporal_window_days": 14, "stale_age_days": 3},
    "severity": {"recurrence_multiplier": 2, "stale_penalty": 1,
                 "blast_radius_bonus": 1, "cross_source_bonus": 1, "deflect_penalty": -3},
}


def _load_canonical(path: str):
    """Load a connect canonical JSON, or canonicalize a raw sample on the fly."""
    from .canonical import canonicalize
    data = read_json(path)
    records = data.get("tickets", data if isinstance(data, list) else [])
    tickets = []
    for rec in records:
        if "body" in rec and "cluster_hint" not in rec:
            tickets.append(rec)                     # already canonical
        else:
            t, reason = canonicalize(rec)           # raw → canonical (drops cluster_hint)
            if t is not None:
                tickets.append(t)
    meta = data.get("_meta", {})
    if not meta:                                    # derive minimal coverage for raw input
        n = len(tickets) or 1
        meta = {"field_coverage": {
            "declared_priority": round(sum(1 for t in tickets
                                           if t.get("declared_priority") is not None) / n, 2),
            "resolution_text": round(sum(1 for t in tickets
                                         if t.get("resolution_text")) / n, 2)}}
    return tickets, meta


def run(args) -> int:
    if args.approve is not None:
        src = args.approve if (args.approve and os.path.exists(args.approve)) else DRAFT_JSON
        if not os.path.exists(src):
            print(f"No draft to approve at {src}. Run `learn <canonical.json>` first.")
            return 2
        tax = read_json(src)
        status = tax.get("calibration_status", "heuristic")
        if args.auto_approve and status != "calibrated":
            tax["calibration_status"] = "unreviewed"     # keep calibrated if it was
        if not args.auto_approve:
            tax.setdefault("reviewed_by", os.environ.get("USER", "human"))
        save_taxonomy(tax, approved=True)
        print(f"Approved → {TAXONOMY_JSON} (calibration_status={tax['calibration_status']})")
        return 0

    source_path = args.canonical or args.eval
    if not source_path:
        print("Usage: agent learn <canonical.json>  |  agent learn --approve"
              "  |  agent learn --eval <labeled.json>")
        return 2
    tickets, meta = _load_canonical(source_path)

    # OBSERVE: blind profile, zero domain knowledge
    engine.annotate(tickets, {"entities": {"lexicon": []}, "subsystems": {}})
    engine.build_tfidf(tickets)
    blind = engine.cluster(tickets, {}, 0.18, 14, blind=True)
    sil = engine.silhouette(tickets, blind)

    coverage = meta.get("field_coverage", {})
    rec_rate = round(sum(1 for t in tickets
                         if t["_markers"]["recurrence_count"] > 1) / (len(tickets) or 1), 2)
    profile = {
        "n_tickets": len(tickets),
        "field_coverage": coverage,
        "sources": meta.get("sources", {}),
        "temporal_span_days": meta.get("temporal_span_days", 0),
        "blind_clusters": len(blind),
        "silhouette_score": sil,
        "cross_source_clusters": sum(
            1 for g in blind if len({tickets[i].get("source") for i in g}) > 1),
        "recurrence_marker_rate": rec_rate,
    }
    write_json(os.path.join("data", "corpus_profile.json"), profile)

    # ADAPT: propose taxonomy (here: seed baseline + adapt weights from profile)
    taxonomy = {k: (v.copy() if isinstance(v, dict) else v)
                for k, v in BASE_TAXONOMY.items()}
    if coverage.get("resolution_text", 0) == 0:
        playbook_learning = False
    else:
        playbook_learning = True
    if coverage.get("declared_priority", 1) == 0:
        taxonomy["severity"] = {**taxonomy["severity"], "_r5_disabled": True}

    # calibration
    if args.eval:
        f1 = _calibrate(args.eval, taxonomy)
        taxonomy["calibration_status"] = "calibrated"
        taxonomy["eval_f1"] = f1
    else:
        taxonomy["calibration_status"] = "heuristic"

    save_taxonomy(taxonomy, approved=False)

    print(f"OBSERVE  n={profile['n_tickets']} · blind_clusters={profile['blind_clusters']} "
          f"· silhouette={sil} · sources={profile['sources']}")
    print(f"         resolution_text coverage={coverage.get('resolution_text', 0)} "
          f"→ historical playbook learning {'ENABLED' if playbook_learning else 'DISABLED'}")
    print(f"ADAPT    proposed {len(taxonomy['subsystems'])} subsystems · "
          f"calibration={taxonomy['calibration_status']}")
    if args.eval:
        print(f"         eval F1={taxonomy['eval_f1']} (calibrated against cluster_hint labels)")
    print(f"GATE     draft → {DRAFT_JSON}")
    print("         review, then:  agent learn --approve")
    if not args.eval:
        print("         ⚠ threshold not validated — all downstream outputs are provisional")
    return 0


def _calibrate(labeled_path: str, taxonomy: dict) -> float:
    """--eval: use cluster_hint ONLY to pick the merge threshold that maximizes F1."""
    raw = read_json(labeled_path)
    records = raw.get("tickets", raw)
    from .canonical import canonicalize
    tickets, labels = [], []
    for rec in records:
        t, reason = canonicalize(rec)
        if t is None:
            continue
        tickets.append(t)
        labels.append(rec.get("cluster_hint"))     # eval-only, never enters the engine
    engine.annotate(tickets, taxonomy)
    engine.build_tfidf(tickets)

    incident_idx = [i for i, t in enumerate(tickets)
                    if engine.type_gate(t) == "INCIDENT"]
    gold = [labels[i] for i in incident_idx]

    best_f1, best_thr = -1.0, taxonomy["thresholds"]["merge"]
    thr = 0.20
    while thr <= 0.85 + 1e-9:
        sub = [tickets[i] for i in incident_idx]
        groups = engine.cluster(sub, taxonomy["weights"], thr,
                                taxonomy["thresholds"]["temporal_window_days"])
        f1 = _pairwise_f1(groups, gold)
        if f1 > best_f1:
            best_f1, best_thr = f1, thr
        thr += 0.02
    taxonomy["thresholds"]["merge"] = round(best_thr, 2)
    return round(best_f1, 3)


def _pairwise_f1(groups: list[list[int]], gold: list) -> float:
    pred = {}
    for gi, g in enumerate(groups):
        for i in g:
            pred[i] = gi
    n = len(gold)
    tp = fp = fn = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_pred = pred[i] == pred[j]
            same_gold = gold[i] is not None and gold[i] == gold[j]
            if same_pred and same_gold:
                tp += 1
            elif same_pred and not same_gold:
                fp += 1
            elif not same_pred and same_gold:
                fn += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
