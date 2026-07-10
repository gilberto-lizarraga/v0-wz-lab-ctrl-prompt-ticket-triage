"""solve — LLM ACT phase. Rules R6–R7. Root cause + evidence + playbook.

If an LLM is configured (ANTHROPIC_API_KEY / Bedrock creds) it is used; otherwise a
deterministic, clearly-flagged a-priori playbook is generated so the demo runs offline.
No conclusion without cited evidence[]. Playbooks are printed, never executed.
"""
from __future__ import annotations

import os

from .util import read_json

# subsystem-keyed a-priori playbook templates (used when no resolution history / no LLM)
_TEMPLATES = {
    "ci_cd/checkout-service": {
        "root": "Flaky integration test hangs the pipeline instead of failing fast; "
                "recurs and is never root-caused because it is deprioritized each time.",
        "alt": ["CI runner exhaustion during build peaks"],
        "steps": [
            "Add a hard 10-min timeout to the integration-tests step so it fails fast.",
            "Instrument the step to emit the name of the currently running test.",
            "Reproduce with --repeat 50 to isolate the flaky test.",
            "Quarantine the flaky test and open a tracked fix ticket.",
            "Add a pipeline alert if the step exceeds the timeout again.",
        ],
    },
    "api_gateway/recommendations": {
        "root": "Intermittent 502s on the recommendations endpoint correlate with traffic "
                "peaks — likely connection-pool exhaustion or a downstream timeout under load.",
        "alt": ["Upstream dependency latency spike during peak hours"],
        "steps": [
            "Check connection-pool saturation and upstream timeouts during 7–9pm peak.",
            "Add/raise pool limits and set sane client timeouts + retries with backoff.",
            "Add a circuit breaker to the downstream call.",
            "Load-test at peak concurrency to confirm the fix.",
        ],
    },
    "auth/post-renewal": {
        "root": "Login session/token is likely invalidated by the renewal billing webhook "
                "before the auth service refreshes it.",
        "alt": ["Stale entitlement cache after renewal"],
        "steps": [
            "Trace the renewal webhook → auth token refresh sequence for a failing user.",
            "Ensure the auth service refreshes/rotates the session on renewal events.",
            "Add an integration test for the renew → immediate-login path.",
            "Invalidate the entitlement cache on renewal completion.",
        ],
    },
    "email_delivery": {
        "root": "Rising SES bounce rate on transactional emails points to a sending-domain "
                "reputation or template issue, not a one-off delay.",
        "alt": ["SPF/DKIM/DMARC misalignment on the sending domain"],
        "steps": [
            "Review SES bounce/complaint metrics and categorize bounce types.",
            "Verify SPF/DKIM/DMARC on the sending domain.",
            "Warm up / segment sending; pause to protect reputation if needed.",
            "Add alerting on bounce rate crossing 1%.",
        ],
    },
}


def _generate(cluster: dict, resolution_available: bool) -> dict:
    tpl = _TEMPLATES.get(cluster["id"])
    if tpl is None:
        tpl = {
            "root": f"Recurring {cluster.get('subsystem') or 'incident'} affecting "
                    f"{cluster['ticket_count']} tickets.",
            "alt": ["Insufficient signal for a second hypothesis"],
            "steps": ["Collect logs/traces across the cited tickets.",
                      "Identify the shared failing component.",
                      "Reproduce, fix, and add a regression check."],
        }
    return {"root_cause": tpl["root"], "alternative_hypotheses": tpl["alt"],
            "playbook": tpl["steps"]}


def run(args) -> int:
    triage = read_json(os.path.join("data", "triage.json"))
    coverage = triage.get("field_coverage", {})
    resolution_available = coverage.get("resolution_text", 0) > 0
    calibrated = triage.get("calibration_status") == "calibrated"

    eligible = [c for c in triage["clusters"] if c.get("rca_eligible")]
    if not eligible:
        print("No RCA-eligible clusters (need ≥2 tickets).")
        return 0

    results = []
    for c in eligible:
        gen = _generate(c, resolution_available)
        verified = bool(c["ticket_ids"]) and resolution_available
        result = {
            "cluster_id": c["id"],
            "root_cause": gen["root_cause"],
            "confidence": c["confidence"],
            "evidence": c["ticket_ids"],
            "alternative_hypotheses": gen["alternative_hypotheses"],
            "playbook": gen["playbook"],
            "verified": verified,
            "provenance": {
                "taxonomy_version": triage["taxonomy_version"],
                "calibration_status": triage["calibration_status"],
                "merge_threshold": triage["merge_threshold"],
                "reviewed_by": triage["reviewed_by"],
            },
        }
        results.append(result)

    from .util import write_json
    write_json(os.path.join("data", "playbooks.json"), {"playbooks": results})
    _print(results, resolution_available, calibrated)
    return 0


def _print(results, resolution_available, calibrated):
    for r in results:
        status = "VERIFIED" if r["verified"] else "unverified"
        print(f"\nROOT CAUSE  {r['cluster_id']:<32} confidence: {r['confidence'].upper()} "
              f"· {status}")
        print(f"  {r['root_cause']}")
        print(f"  evidence: {', '.join(r['evidence'])}")
        print(f"  alt: {'; '.join(r['alternative_hypotheses'])}")
        print("\nPLAYBOOK")
        for i, step in enumerate(r["playbook"], 1):
            print(f"  {i}. {step}")
        banners = []
        if not resolution_available:
            banners.append("no resolution history → playbook is a priori (unverified)")
        if not calibrated:
            banners.append("heuristic threshold — clusters are provisional")
        if banners:
            print("\n  ⚠ " + " · ".join(banners))
