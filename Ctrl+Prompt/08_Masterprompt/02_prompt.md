# 02_Prompt — P0: `learn` + `triage` (clustering + root-cause ranking)

## Context (what already exists)
- `connect` produces a canonical JSON (with `_meta`), tested via `--mock` on the sample.

## Attach
- `02_BRD_PRD_Specs/PRD.md` (rules R1–R6)
- `03_UXUI/cli-output-style.md`

## Build now

**1. `learn` (OBSERVE → ADAPT → gate)**
- OBSERVE: profile field coverage; embed `title+body` (Bedrock, SQLite cache); blind-cluster with
  `w_semantic = 1.0` (no taxonomy, no veto); emit `corpus_profile.json` with `n_tickets,
  field_coverage, sources, temporal_span_days, blind_clusters, silhouette_score,
  cross_source_clusters, recurrence_marker_rate, vocabulary_divergence`.
- ADAPT: discover entities (`*-service`, `/api/v*`, frequent n-grams); **propose** subsystems via
  the LLM; adapt weights from the profile; calibrate the merge threshold —
  - if a labeled subset ≥20 exists: sweep `merge ∈ [0.40..0.85]` step 0.01, maximize F1 →
    `calibration_status: calibrated` (report F1/precision/recall);
  - else: heuristic (histogram elbow) → `calibration_status: heuristic` and print the warning.
- Gate: emit `taxonomy.draft.yaml`; `agent learn --approve` copies it to `taxonomy.yaml`.
  `--auto-approve` allowed but stamps `calibration_status: unreviewed`.

**2. `triage` (deterministic, no LLM) — rules R1–R6**
- R1 extraction (entities, subsystem, markers; `recurrence_count` is an integer).
- R2 type gate → `INCIDENT | FEATURE_REQUEST | UNKNOWN`.
- R3 semantic normalization (subsystem boost; graceful when `subsystems` is empty).
- R4 similarity + agglomerative clustering (average linkage, no `k`) with the **entity veto**
  (never merge two non-empty disjoint entity sets). Validate `sum(weights)==1.0` at startup or
  **fail loudly**.
- R5 effective priority at cluster level → `INFLATED | SUPPRESSED | ALIGNED`. Disable if
  `field_coverage.declared_priority == 0`.
- R6 RCA queue ordered by `severity_real × ticket_count` (descending) — **not** declared priority.
- Precondition: an approved `taxonomy.yaml` exists, else abort pointing to the draft.

**3. Output** — match `cli-output-style.md`: clusters table (TICKETS/DECL./EFFECT./FLAG),
deflected list, and the calibration footer. `--json` twin.

## Acceptance (on the sample)
- OBSERVE: ~6 blind clusters, silhouette ≈ 0.41, high `vocabulary_divergence`,
  `resolution_text` absent 15/15.
- ADAPT: proposes ~4 subsystems, `w_subsystem → 0.35`, **heuristic** threshold, playbook learning
  disabled.
- `triage`: **4 incident clusters + 2 deflect**, `checkout-service` = SUPPRESSED,
  `recommendations` = INFLATED, `email_delivery` flagged cross-source.

## Validation before 03_prompt
- [ ] `learn` emits `corpus_profile.json` + `taxonomy.draft.yaml`; gate enforced
- [ ] `triage` reproduces the 4+2 clustering **without reading `cluster_hint`**
- [ ] entity veto + weight-sum check + priority flags all work
- [ ] calibration footer present on the output
