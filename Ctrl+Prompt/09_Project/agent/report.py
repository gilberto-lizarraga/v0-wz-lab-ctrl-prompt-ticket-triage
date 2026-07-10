"""report — consolidate connect/triage/solve into a readable document.

Presents; does not compute. Every figure reconciles with connect's _meta.
Formats: terminal | md | json.
"""
from __future__ import annotations

import json
import os

from .util import read_json


def _load_all(canonical_path: str):
    canonical = read_json(canonical_path)
    triage = read_json(os.path.join("data", "triage.json"))
    pb_path = os.path.join("data", "playbooks.json")
    playbooks = read_json(pb_path)["playbooks"] if os.path.exists(pb_path) else []
    return canonical.get("_meta", {}), triage, playbooks


def run(args) -> int:
    meta, triage, playbooks = _load_all(args.canonical)
    n_incident = sum(c["ticket_count"] for c in triage["clusters"])
    top = [c for c in triage["clusters"] if c["ticket_count"] >= 2]
    gaps = [c for c in triage["clusters"] if c["flag"] in ("INFLATED", "SUPPRESSED")]

    if args.format == "json":
        print(json.dumps({"meta": meta, "triage": triage, "playbooks": playbooks},
                         indent=2, ensure_ascii=False))
        return 0

    md = args.format == "md"
    H1 = "# " if md else ""
    H2 = "## " if md else ""
    lines = []
    lines.append(f"{H1}Disney Agent Support Tickets — Incident Report")
    lines.append("")
    lines.append(f"{H2}Provenance")
    lines.append(f"Source:      {meta.get('connection')} · extracted {meta.get('extracted_at')}")
    lines.append(f"Volume:      {meta.get('n_extracted')} extracted → "
                 f"{meta.get('n_valid')} valid ({meta.get('n_discarded')} discarded)")
    lines.append(f"Calibration: {triage['calibration_status']} · threshold "
                 f"{triage['merge_threshold']} · taxonomy v{triage['taxonomy_version']} · "
                 f"reviewed_by: {triage['reviewed_by']}")
    lines.append(f"PII:         {'redacted' if meta.get('pii_redacted') else 'not redacted'}")
    lines.append("")
    lines.append(f"{H2}Executive summary")
    lines.append(f"{n_incident} actionable tickets collapsed into {len(triage['clusters'])} "
                 f"root-cause incidents; {len(triage['deflected'])} deflected to product.")
    lines.append("")
    lines.append(f"{H2}Incidents (ranked by severity × volume)")
    lines.append(f"  {'ID':<32}{'TIX':>4}  {'DECL':>4}  {'EFF':>4}  FLAG")
    for c in triage["clusters"]:
        lines.append(f"  {c['id']:<32}{c['ticket_count']:>4}  {c['declared'] or '—':>4}  "
                     f"{c['effective']:>4}  {c['flag']}"
                     + ("  (cross-source)" if c["cross_source"] else ""))
    lines.append("")
    lines.append(f"{H2}Priority gaps (most actionable)")
    if gaps:
        for c in gaps:
            lines.append(f"  {c['flag']:<11} {c['id']} — declared {c['declared']}, "
                         f"behaves like {c['effective']} (recurs {c['recurrence_count']}×)")
    else:
        lines.append("  none")
    lines.append("")
    lines.append(f"{H2}Playbooks")
    for p in playbooks:
        tag = "VERIFIED" if p["verified"] else "unverified"
        lines.append(f"  • {p['cluster_id']} [{p['confidence']}/{tag}]")
        lines.append(f"    root cause: {p['root_cause']}")
        lines.append(f"    evidence: {', '.join(p['evidence'])}")
    lines.append("")
    lines.append(f"{H2}Deflected / Unknown")
    for d in triage["deflected"]:
        lines.append(f"  deflect  {d['id']}  {d['title']}")
    lines.append("")
    lines.append(f"{H2}Calibration appendix")
    if triage["calibration_status"] == "calibrated":
        lines.append("  Calibrated via --eval against cluster_hint labels (see learn output for F1).")
    else:
        lines.append("  Threshold is heuristic — clusters are PROVISIONAL. Run `learn --eval` "
                     "to report F1 against labels.")

    text = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"report written → {args.out}")
    else:
        print(text)
    return 0
