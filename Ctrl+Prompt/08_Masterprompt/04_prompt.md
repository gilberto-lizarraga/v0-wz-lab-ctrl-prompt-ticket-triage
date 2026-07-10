# 04_Prompt — `report`, `--eval`, and iteration

## Context (what already exists)
- `connect → learn → triage → solve` all run on the sample end to end.

## Attach
- `02_BRD_PRD_Specs/PRD.md` (§4.5)
- `03_UXUI/cli-output-style.md`

## Build now

**1. `report` (presents, does not compute)**
- Inputs: `corpus_profile.json` (learn) · clusters+severity (triage) · playbooks (solve) ·
  `connect`'s `_meta`.
- Structure:
  1. **Provenance cover** — source, extraction counts, calibration, PII status.
  2. **Executive 80/20 summary** — one sentence with numbers ("13 actionable tickets collapsed
     into 4 root causes; 2 deflected").
  3. **Incident table** — ordered by `severity_real × ticket_count`; declared vs effective + flag.
  4. **Priority gaps** — the `INFLATED` / `SUPPRESSED` cases (most actionable for a lead).
  5. **Playbooks** — root cause, confidence, cited evidence, alternative; banners preserved.
  6. **Deflect & unknown** — what left the pipeline and where.
  7. **Calibration appendix** — F1/precision/recall if `--eval` ran, else "clusters are provisional".
- Formats: `--format terminal | md | json`. Every figure reconciles with `_meta`
  ("84 analyzed" vs "87 extracted, 3 discarded"). If `contains_raw_pii: true`, warn before the cover.

**2. `--eval` (the judge-facing metric)**
- `agent learn --eval 04_Data_Sources/ticket-sample.json` uses `cluster_hint` **only** to calibrate
  the merge threshold and compute **F1** vs the labels; moves `calibration_status`
  heuristic → calibrated. `cluster_hint` must never reach inference otherwise.

**3. Iterate**
- Scale the dataset to **50–100 tickets** with adversarial cases: two services with the same
  symptom (entity veto), a feature request that names a service (R2 gate), a legit 1-day-old P1
  (INFLATED false-positive check), orphan tickets (size-1 clusters), two close-but-distinct
  clusters (threshold). Cache embeddings + LLM responses in SQLite.

## Acceptance
- `agent report --format md` renders the 4+2 result with the priority-gap section and
  `unverified` playbooks, every figure reconciling with `_meta`.
- `--eval` prints a defensible F1: "reconstructed 4 of 5 clusters without seeing the labels."

## Validation (demo-ready)
- [ ] `report` presents only; no new logic; figures reconcile with `_meta`
- [ ] Calibration banner on the cover **and** every playbook
- [ ] `--eval` reports F1 and flips calibration status
- [ ] End-to-end runs offline via `--mock`, and live via the Jira descriptor
