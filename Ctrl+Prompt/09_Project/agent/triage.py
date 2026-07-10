"""triage — deterministic ACT phase. Rules R1–R6. No LLM.

Reads an approved taxonomy. Produces clusters, effective priority, and the RCA queue.
"""
from __future__ import annotations

import os

from . import engine
from .config import load_taxonomy, validate_weights
from .util import parse_ts, read_json, write_json


def _load_canonical(path: str):
    data = read_json(path)
    return data.get("tickets", data), data.get("_meta", {})


def _slug(cluster_tickets, subsystem):
    if subsystem:
        return subsystem
    return f"cluster/{cluster_tickets[0]['id']}"


def run(args) -> int:
    taxonomy = load_taxonomy()
    if taxonomy is None:
        print("No approved taxonomy.json. Run `learn` then `learn --approve` first.")
        return 2
    validate_weights(taxonomy)

    tickets, meta = _load_canonical(args.canonical)
    engine.annotate(tickets, taxonomy)
    engine.build_tfidf(tickets)

    # R2 type gate
    incidents, deflected, unknown = [], [], []
    for t in tickets:
        kind = engine.type_gate(t)
        t["_type"] = kind
        (incidents if kind == "INCIDENT"
         else deflected if kind == "FEATURE_REQUEST" else unknown).append(t)

    # R3+R4 clustering with veto (incidents only)
    groups = engine.cluster(incidents, taxonomy["weights"],
                            taxonomy["thresholds"]["merge"],
                            taxonomy["thresholds"]["temporal_window_days"])

    times = [parse_ts(t["created_at"]) for t in tickets if parse_ts(t["created_at"])]
    ref_time = max(times) if times else None
    stale_age = taxonomy["thresholds"]["stale_age_days"]

    clusters = []
    for g in groups:
        cts = [incidents[i] for i in g]
        subsystem = None
        for c in cts:
            if c["_subsystem"]:
                subsystem = c["_subsystem"]
                break
        eff = engine.effective_priority(cts, taxonomy["severity"], stale_age, ref_time)
        clusters.append({
            "id": _slug(cts, subsystem),
            "subsystem": subsystem,
            "ticket_ids": [c["id"] for c in cts],
            "ticket_count": len(cts),
            "confidence": engine.confidence(cts),
            **eff,
        })

    # R6 RCA queue: severity_real × ticket_count, descending (not declared priority)
    clusters.sort(key=lambda c: c["severity_real"] * c["ticket_count"], reverse=True)
    for c in clusters:
        c["rca_eligible"] = c["ticket_count"] >= 2

    out = {
        "taxonomy_version": taxonomy["version"],
        "calibration_status": taxonomy.get("calibration_status", "heuristic"),
        "merge_threshold": taxonomy["thresholds"]["merge"],
        "reviewed_by": taxonomy.get("reviewed_by"),
        "field_coverage": meta.get("field_coverage", {}),
        "clusters": clusters,
        "deflected": [{"id": t["id"], "title": t["title"]} for t in deflected],
        "unknown": [{"id": t["id"], "title": t["title"]} for t in unknown],
    }
    write_json(os.path.join("data", "triage.json"), out)
    _print(out)
    return 0


def _print(out):
    clusters, deflected, unknown = out["clusters"], out["deflected"], out["unknown"]
    print(f"\nCLUSTERS ({len(clusters)} incidents · {len(deflected)} deflect · "
          f"{len(unknown)} unknown)\n")
    print(f"  {'ID':<32}{'TICKETS':>8}  {'DECL.':>5}  {'EFFECT.':>7}  FLAG")
    for c in clusters:
        decl = c["declared"] or "—"
        xs = "  (cross-source)" if c["cross_source"] else ""
        print(f"  {c['id']:<32}{c['ticket_count']:>8}  {decl:>5}  "
              f"{c['effective']:>7}  {c['flag']}{xs}")
    if deflected:
        print(f"\nDEFLECTED ({len(deflected)})")
        for d in deflected:
            print(f"  {d['id']:<12} {d['title'][:44]:<44} → product backlog")
    if unknown:
        pct = round(100 * len(unknown) / max(sum(
            [len(clusters), len(deflected), len(unknown)]), 1))
        print(f"\nUNKNOWN ({len(unknown)})")
        if pct > 30:
            print("  ⚠ UNKNOWN > 30% of volume — the taxonomy is probably incomplete")
    print(f"\n  calibration: {out['calibration_status']} · taxonomy v{out['taxonomy_version']} "
          f"· merge {out['merge_threshold']} · reviewed_by: {out['reviewed_by']}")
