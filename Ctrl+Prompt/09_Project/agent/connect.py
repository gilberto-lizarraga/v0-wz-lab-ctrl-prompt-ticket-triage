"""Phase 0 — connect: the only boundary with a source.

Implements the --mock path fully (offline demo) and scaffolds live extraction.
Produces a self-contained canonical JSON with a _meta provenance block.
"""
from __future__ import annotations

import os
from collections import Counter

from .canonical import canonicalize, redact
from .util import ensure_data_dir, now_utc, parse_ts, read_json, write_json


def _profile(tickets: list[dict], n_extracted: int, discards: Counter,
             source_label: str, redacted: bool) -> dict:
    n = len(tickets) or 1
    def coverage(field):
        return round(sum(1 for t in tickets if t.get(field) not in (None, "")) / n, 2)

    times = [parse_ts(t["created_at"]) for t in tickets if parse_ts(t["created_at"])]
    span = (max(times) - min(times)).days if len(times) > 1 else 0
    prio_vocab = sorted({str(t.get("raw_extra", {}).get("priority") or
                             t.get("declared_priority")) for t in tickets})
    unmapped = sorted({k for t in tickets for k in t.get("raw_extra", {})})
    return {
        "connection": source_label,
        "extracted_at": now_utc().isoformat(),
        "n_extracted": n_extracted,
        "n_valid": len(tickets),
        "n_discarded": sum(discards.values()),
        "discard_reasons": dict(discards),
        "field_coverage": {
            "declared_priority": coverage("declared_priority"),
            "status": coverage("status"),
            "reporter": coverage("reporter"),
            "resolution_text": coverage("resolution_text"),
        },
        "sources": dict(Counter(t.get("source") for t in tickets if t.get("source"))),
        "priority_vocabulary": [p for p in prio_vocab if p and p != "None"],
        "unmapped_fields": unmapped,
        "temporal_span_days": span,
        "pii_redacted": redacted,
    }


def run(args) -> int:
    if args.test:
        print(f"connect --test {args.test}: (scaffold) validating auth + reachability …")
        print("  → configure connections.yaml + JIRA_* env vars for a live check.")
        return 0
    if args.discover:
        print(f"connect --discover {args.discover}: (scaffold) would sample fields/vocab.")
        print("  → run against the mock file to inventory the canonical shape instead.")
        return 0

    if not args.mock:
        print("Live extraction is scaffolded. For the demo use:")
        print("  agent connect --mock data/ticket-sample.json")
        print("Live path needs descriptors/*.yaml + connections.yaml + JIRA_* env vars.")
        return 2

    raw = read_json(args.mock)
    records = raw.get("tickets", raw if isinstance(raw, list) else [])
    project = args.project or os.path.splitext(os.path.basename(args.mock))[0]

    tickets, discards = [], Counter()
    for rec in records:
        t, reason = canonicalize(rec)
        if t is None:
            discards[reason] += 1
            continue
        if args.redact:
            t = redact(t)
        tickets.append(t)

    meta = _profile(tickets, len(records), discards, project, bool(args.redact))
    out = {"_meta": meta, "tickets": tickets}
    ensure_data_dir()
    path = os.path.join("data", f"{project}.canonical.json")
    write_json(path, out)

    print(f"connect: {len(records)} → {len(tickets)} valid "
          f"({meta['n_discarded']} discarded)")
    print(f"  sources: {meta['sources']}")
    print(f"  field_coverage: declared_priority={meta['field_coverage']['declared_priority']} "
          f"· resolution_text={meta['field_coverage']['resolution_text']}")
    print(f"  cluster_hint present in output: "
          f"{any('cluster_hint' in t.get('raw_extra', {}) for t in tickets)} (must be False)")
    print(f"  → {path}")
    return 0
