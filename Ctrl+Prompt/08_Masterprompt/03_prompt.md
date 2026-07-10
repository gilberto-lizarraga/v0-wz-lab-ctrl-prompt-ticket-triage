# 03_Prompt — P1: `solve` (RCA + resolution playbook)

## Context (what already exists)
- `triage` produces ordered incident clusters + effective priority from an approved `taxonomy.json`.

## Attach
- `02_BRD_PRD_Specs/PRD.md` (rules R6–R7)
- `03_UXUI/cli-output-style.md`

## Build now

**`solve` (the only LLM step)** — process the RCA queue from `triage` (R6 eligibility, R6 order).

**Chained prompts (three, not one monolith):**
1. **Classification** — input: one ticket → strict JSON
   `{subsystem, entities[], error_signals[], recurrence_count}`.
2. **Root cause** — input: all tickets in the cluster + historical `resolution_text` if present →
   `{root_cause, confidence: high|medium|low, evidence: [ids], alternative_hypotheses: [...]}`.
   `alternative_hypotheses` is **mandatory** (a single hypothesis is guessing, not reasoning).
3. **Playbook** — input: the accepted root cause → numbered plain-text steps (terminal, no heavy
   markdown, **no auto-execution**).

**R7 confidence + evidence:**
- `high` ≥3 tickets ∧ ≥2 sources · `medium` ≥2 tickets · `low` 1 ticket.
- Every output cites `evidence[]` (ticket IDs). **Without evidence → `unverified`**, printed as a
  hypothesis, not a conclusion.

**Rejection / banner rules:**
| Condition | Result |
|---|---|
| `evidence[]` empty | `unverified` — not a firm conclusion |
| `confidence: low` (single ticket) | printed as a hypothesis |
| `field_coverage.resolution_text == 0` | banner: "no resolution history; playbook is a priori" |
| `calibration_status != calibrated` | warning banner on every playbook |

**Output contract (also `--json`):**
```
cluster_id · root_cause · confidence · evidence[] · alternative_hypotheses[] · playbook[]
provenance: { taxonomy_version, calibration_status, merge_threshold, reviewed_by }
```

## Acceptance (on the sample)
- Emits root causes for the 4 incident clusters, each with cited evidence IDs and an alternative
  hypothesis.
- **Every playbook is flagged `unverified`** (no `resolution_text` in the sample) and carries the
  heuristic banner — the tool declares its uncertainty rather than hiding it.

## Validation before 04_prompt
- [ ] Three chained prompts return strict JSON at each stage
- [ ] `alternative_hypotheses` always present; `evidence[]` always cited
- [ ] `unverified` / `heuristic` / "a priori" banners fire correctly
- [ ] provenance block attached to every playbook
