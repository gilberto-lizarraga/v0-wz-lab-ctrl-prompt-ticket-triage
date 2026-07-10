# CLI Usage Guide — `agent`

Complete command reference for the Disney Agent Support Tickets CLI. For the project overview
and quick start, see [`README.md`](./README.md).

- **Invocation:** `python3 -m agent <command> [options]`
- **Runtime:** Python 3.11+, standard library only (no install).
- **Pipeline order:** `connect → learn → learn --approve → triage → solve → report`
  (`learn --eval` is optional, for calibration).

---

## Table of contents

1. [Concepts](#concepts)
2. [Global usage](#global-usage)
3. [`connect`](#connect)
4. [`learn`](#learn)
5. [`triage`](#triage)
6. [`solve`](#solve)
7. [`report`](#report)
8. [File artifacts](#file-artifacts)
9. [Exit codes](#exit-codes)
10. [Environment variables](#environment-variables)
11. [Troubleshooting](#troubleshooting)
12. [End-to-end example](#end-to-end-example)

---

## Concepts

| Term | Meaning |
|---|---|
| **Canonical JSON** | The normalized ticket file produced by `connect`. Everything downstream reads this, never a live source. |
| **Taxonomy** | The only per-client config (`taxonomy.json`). Holds subsystems, weights, thresholds. The engine has no domain words. |
| **The gate** | `learn` only *proposes* a taxonomy draft; a human `--approve`s it before `triage`/`solve` can run. |
| **Provenance** | Every output states taxonomy version, calibration status, merge threshold, and reviewer. |
| **Flags** | `INFLATED` (declared high, no progress), `SUPPRESSED` (declared low, recurs ≥3×), `ALIGNED`. |
| **`unverified`** | A playbook with no resolution history / no cited evidence — printed as a hypothesis, not fact. |

---

## Global usage

```bash
python3 -m agent --version
python3 -m agent --help
python3 -m agent <command> --help
```

| Command | Phase | One-liner |
|---|---|---|
| `connect` | Phase 0 | Collect + normalize a source into canonical JSON |
| `learn`   | OBSERVE + ADAPT | Profile the corpus, propose a taxonomy, calibrate |
| `triage`  | ACT | Cluster tickets + compute effective priority (deterministic) |
| `solve`   | ACT | Root cause + evidence + resolution playbook (LLM step) |
| `report`  | REPORT | Consolidate everything into a readable document |

---

## `connect`

Collect tickets from a source and write a self-contained canonical JSON with a `_meta`
provenance block. This is the **only** command that talks to an external system.

```bash
python3 -m agent connect [--mock FILE] [--project NAME] [--since WINDOW]
                         [--redact] [--test NAME] [--discover NAME]
```

| Option | Description |
|---|---|
| `--mock FILE` | Load a canonical or raw JSON **offline** (the demo path). Raw fields are normalized; `cluster_hint` is dropped. |
| `--project NAME` | Neutral label for the source container. Defaults to the mock filename. |
| `--since WINDOW` | Source-native time window (e.g. `90d`). Used by the live path. |
| `--redact` | Mask emails / long tokens in `title` and `body` before writing. |
| `--test NAME` | Validate auth + reachability only, then exit (live path). |
| `--discover NAME` | Sample the source and inventory fields + vocabularies (live path). |

**Example (offline):**
```bash
python3 -m agent connect --mock data/ticket-sample.json --redact --project ticket-sample
```
```
connect: 15 → 15 valid (0 discarded)
  sources: {'Jira': 4, 'PagerDuty': 4, 'Zendesk': 7}
  field_coverage: declared_priority=1.0 · resolution_text=0.0
  cluster_hint present in output: False (must be False)
  → data/ticket-sample.canonical.json
```

**Output:** `data/<project>.canonical.json` with `_meta` (extraction counts, field coverage,
sources, priority vocabulary, unmapped fields, temporal span, PII flag) + `tickets[]`.

> Live extraction (Jira) is descriptor-driven via `descriptors/jira_rest.yaml` and
> `connections.json`; the transport layer is scaffolded (see README "Going live with Jira").

---

## `learn`

Profile the corpus with zero domain knowledge (OBSERVE), then **propose** a taxonomy (ADAPT).
Nothing is applied until a human approves it.

```bash
python3 -m agent learn <canonical.json>          # profile + propose a draft
python3 -m agent learn --approve [DRAFT]         # gate: promote draft → taxonomy.json
python3 -m agent learn --auto-approve            # CI/demo: approve, stamp 'unreviewed'
python3 -m agent learn --eval <labeled.json>     # calibrate threshold, report F1
```

| Option | Description |
|---|---|
| `<canonical.json>` | Positional: the file from `connect`. Required unless approving/eval-only. |
| `--approve [DRAFT]` | Promote a draft to `taxonomy.json`. With no path, approves the latest draft. |
| `--auto-approve` | Approve without review; stamps `calibration_status: unreviewed` on every output. |
| `--eval LABELED_JSON` | Use `cluster_hint` **only** to sweep the merge threshold and report **F1**. |

**Propose a taxonomy:**
```bash
python3 -m agent learn data/ticket-sample.canonical.json
```
```
OBSERVE  n=15 · blind_clusters=6 · silhouette=0.377 · sources={'Jira': 4, ...}
         resolution_text coverage=0.0 → historical playbook learning DISABLED
ADAPT    proposed 4 subsystems · calibration=heuristic
GATE     draft → data/taxonomy.draft.json
         review, then:  agent learn --approve
         ⚠ threshold not validated — all downstream outputs are provisional
```

**Approve (the human gate):**
```bash
python3 -m agent learn --approve
# Approved → taxonomy.json (calibration_status=heuristic)
```

**Calibrate + F1:**
```bash
python3 -m agent learn --eval data/ticket-sample.json
# ADAPT ... calibration=calibrated · eval F1=1.0
```

**Outputs:** `data/corpus_profile.json`, `data/taxonomy.draft.json`, and (on approve) `taxonomy.json`.

---

## `triage`

Deterministic execution (rules R1–R6, no LLM): classify, cluster with the entity veto, compute
effective priority, and order the RCA queue. Requires an approved `taxonomy.json`.

```bash
python3 -m agent triage <canonical.json>
```

**Example:**
```bash
python3 -m agent triage data/ticket-sample.canonical.json
```
```
CLUSTERS (4 incidents · 2 deflect · 0 unknown)

  ID                               TICKETS  DECL.  EFFECT.  FLAG
  ci_cd/checkout-service                 4     P2       P1  SUPPRESSED
  auth/post-renewal                      3     P2       P2  SUPPRESSED
  api_gateway/recommendations            3     P1       P2  INFLATED
  email_delivery                         3     P3       P3  ALIGNED  (cross-source)

DEFLECTED (2)
  TCK-10240    Feature request: dark mode for kids profile   → product backlog
  TCK-10244    Can I get a bigger avatar image size option?  → product backlog

  calibration: heuristic · taxonomy v1 · merge 0.3 · reviewed_by: <you>
```

**Behavior notes:**
- Fails loudly if `taxonomy.json` weights don't sum to `1.0`.
- Aborts (exit 2) if no approved taxonomy exists — pointing to the draft.
- If `declared_priority` coverage is 0, the DECL./FLAG columns are omitted (R5 disabled).
- Warns if `UNKNOWN` exceeds 30% of volume (taxonomy likely incomplete).

**Output:** `data/triage.json` (clusters, flags, RCA queue, deflected, unknown).

---

## `solve`

The only LLM step (rules R6–R7). For each RCA-eligible cluster (≥2 tickets), produce a root-cause
hypothesis with **cited evidence**, a mandatory alternative hypothesis, and a numbered playbook.
Reads `data/triage.json`.

```bash
python3 -m agent solve
```

**Example (excerpt):**
```
ROOT CAUSE  ci_cd/checkout-service           confidence: MEDIUM · unverified
  Flaky integration test hangs the pipeline instead of failing fast; ...
  evidence: TCK-10231, TCK-10236, TCK-10232, TCK-10241
  alt: CI runner exhaustion during build peaks

PLAYBOOK
  1. Add a hard 10-min timeout to the integration-tests step so it fails fast.
  2. Instrument the step to emit the name of the currently running test.
  ...
  ⚠ no resolution history → playbook is a priori (unverified) · heuristic threshold
```

**Behavior notes:**
- Uses an LLM if configured (Bedrock / `ANTHROPIC_API_KEY`); otherwise a deterministic a-priori
  playbook, clearly flagged.
- Without `resolution_text` in the corpus, every playbook is `unverified` (an honest hypothesis).
- Confidence: `high` (≥3 tickets ∧ ≥2 sources) · `medium` (≥2) · `low` (1).

**Output:** `data/playbooks.json`.

---

## `report`

Consolidate `connect` + `triage` + `solve` into one document. Presents only; introduces no new
logic. Every figure reconciles with `connect`'s `_meta`.

```bash
python3 -m agent report <canonical.json> [--format terminal|md|json] [--out FILE]
```

| Option | Description |
|---|---|
| `<canonical.json>` | Positional: the file from `connect` (for the provenance cover). |
| `--format` | `terminal` (default), `md`, or `json`. |
| `--out FILE` | Write to a file instead of stdout. |

**Examples:**
```bash
python3 -m agent report data/ticket-sample.canonical.json                     # terminal
python3 -m agent report data/ticket-sample.canonical.json --format md --out data/report.md
python3 -m agent report data/ticket-sample.canonical.json --format json > out.json
```

**Sections:** Provenance cover · Executive 80/20 summary · Incident table · Priority gaps ·
Playbooks · Deflected/Unknown · Calibration appendix.

---

## File artifacts

All written under `data/` (override with `AGENT_DATA_DIR`):

| File | Written by | Contents |
|---|---|---|
| `<project>.canonical.json` | `connect` | Normalized tickets + `_meta` provenance |
| `corpus_profile.json` | `learn` | Blind-clustering stats (silhouette, sources, coverage) |
| `taxonomy.draft.json` | `learn` | Proposed taxonomy (pending review) |
| `taxonomy.json` (repo root) | `learn --approve` | Approved taxonomy — the only config ACT reads |
| `triage.json` | `triage` | Clusters, flags, RCA queue, deflected |
| `playbooks.json` | `solve` | Root causes, evidence, playbooks, provenance |
| `report.md` | `report --out` | Rendered report |

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `2` | Usage / precondition error (e.g. missing taxonomy, no `--mock` and no live config) |
| other | Uncaught error (stack trace printed) |

`triage` also calls `SystemExit` with a `FATAL:` message if taxonomy weights don't sum to 1.0.

---

## Environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `AGENT_DATA_DIR` | all | Output directory (default `data`) |
| `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` | `connect` (live) | Jira auth — referenced by **name**, never stored in files |
| `ANTHROPIC_API_KEY` / `AWS_*` | `solve` | Optional LLM backend for root cause + playbooks |

Secrets are never written to the canonical JSON, the report, or logs.

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `No approved taxonomy.json` | Run `learn <canonical.json>` then `learn --approve`. |
| `connect` prints "Live extraction is scaffolded" | You ran `connect` without `--mock` and without live config. Use `--mock data/ticket-sample.json`. |
| `FATAL: taxonomy weights must sum to 1.0` | Edit `taxonomy.json` so `weights` sum to exactly 1.0. |
| `learn --eval` reports F1 = 1.0 | The taxonomy subsystems align 1:1 with the gold clusters. For a conservative number, calibrate on semantic-only similarity (see README caveats). |
| All playbooks show `unverified` | Expected on the sample — there is no `resolution_text` to learn from. |
| `report` errors on missing `triage.json` | Run `triage` (and `solve`) before `report`. |

---

## End-to-end example

```bash
cd agent-support-tickets

# One shot:
./run_demo.sh

# Or manually:
python3 -m agent connect --mock data/ticket-sample.json --redact --project ticket-sample
python3 -m agent learn   data/ticket-sample.canonical.json
python3 -m agent learn   --approve
python3 -m agent triage  data/ticket-sample.canonical.json
python3 -m agent solve
python3 -m agent report  data/ticket-sample.canonical.json --format md --out data/report.md
python3 -m agent learn   --eval data/ticket-sample.json      # optional: F1
```

Expected: **4 incident clusters + 2 deflected**, `checkout-service` = `SUPPRESSED`,
`recommendations` = `INFLATED`, all playbooks `unverified`.
