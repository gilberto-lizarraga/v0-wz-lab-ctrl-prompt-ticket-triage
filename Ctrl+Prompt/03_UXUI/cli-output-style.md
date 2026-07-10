# CLI Output Style — Disney Agent Support Tickets

> ⚠️ CLI-first, **not** a dashboard. The brief is explicit: users are exceptionally technical and
> terminal-native. Do **not** default to a web UI. Source: brief §4, §5.
> `Disney_Logo.webp` is kept for reference only — a CLI does not render it.

## Principles

1. **Readable in a terminal first.** Plain text, aligned columns, no heavy markdown. Assume an
   80–120 column terminal.
2. **Provenance is visible, not buried.** Every command ends with a calibration/trust footer.
   The engineer must know how much to trust the output *from the output itself*.
3. **Color is optional.** Use ANSI color for emphasis (flags, severities) but never depend on it
   — the tool must be legible when piped to a file or a CI log (`--no-color`).
4. **Machine-readable twin.** Every human view has a `--json` equivalent with identical content.

## Severity & flag conventions

| Token | Meaning | Suggested style |
|---|---|---|
| `INFLATED` | declared high, no progress, stale | yellow |
| `SUPPRESSED` | declared low, recurs ≥3× | red |
| `ALIGNED` | declared matches behavior | dim/green |
| `unverified` | no cited evidence / no resolution history | red banner |
| `heuristic` | threshold not calibrated | yellow banner |

## Command output sketches

### `connect`
```
$ agent connect --project jira-sre --since 90d
Probing jira-sre (jira_rest) … auth ok (200)
Extracted 87 → 84 valid (3 discarded: missing_body 3)
field_coverage: declared_priority 1.00 · status 1.00 · resolution_text 0.00
sources: Jira 84   priority_vocab: [P1,P2,P3,P4]
→ data/jira-sre-2026-07-10.canonical.json   (pii_redacted: true)
```

### `triage`
```
CLUSTERS (4 incidents · 2 deflect · 0 unknown)

  ID                          TICKETS  DECL.  EFFECT.  FLAG
  ci_cd/checkout-service            4     P2      P1   SUPPRESSED
  api_gateway/recommendations       3     P1      P2   INFLATED
  auth/post-renewal                 3     P2      P2   SUPPRESSED
  email_delivery                    3     P3      P2   ALIGNED  (cross-source)

DEFLECTED (2)
  TCK-10240  dark mode kids profile   → product backlog
  TCK-10244  avatar image size        → product backlog

  calibration: heuristic · taxonomy v1 · reviewed_by: null
```

### `solve`
```
ROOT CAUSE  ci_cd/checkout-service               confidence: HIGH
  Flaky integration test hangs the pipeline instead of failing fast.
  evidence: TCK-10231, TCK-10232, TCK-10236, TCK-10241
  alt: CI runner exhaustion during build peaks

PLAYBOOK
  1. Add a hard 10-min timeout to the integration-tests step
  2. Instrument the step to emit the currently running test name
  3. Reproduce with --repeat 50 to isolate the flaky test
  ...

  ⚠ heuristic threshold · no resolution history → playbook is a priori (unverified)
```

## Rules
- Numbers in any table must reconcile with `connect`'s `_meta` (e.g. "84 analyzed" vs "87 extracted").
- Never print a playbook as a firm conclusion without cited `evidence[]`.
- Banners (`heuristic` / `unverified` / `contains_raw_pii`) appear on the summary **and** per playbook.

**Source:** brief §4, §5.
