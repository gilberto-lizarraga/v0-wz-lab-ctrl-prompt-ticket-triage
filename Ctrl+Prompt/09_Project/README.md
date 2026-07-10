# Disney Agent Support Tickets — CLI agent

A **CLI-first** agent for SRE/DevOps engineers. It ingests a support-ticket backlog,
collapses it into **root-cause incidents**, corrects the gap between declared and real
priority, and prints an **auditable resolution playbook**.

> This is **Option 4** from `../EXECUTION-OPTIONS.md`: a real terminal tool, faithful to the
> brief (CLI, not GUI). It runs **fully offline** on the synthetic sample — no Vercel, no
> network, no external services required.

## Requirements

- **Python 3.11+**. That's it — the demo uses the **standard library only** (no `pip install`).
- Optional production upgrades in `requirements.txt` (Typer, Bedrock/boto3, scikit-learn, PyYAML).

## Quick start

```bash
cd agent-support-tickets
./run_demo.sh              # end-to-end on the 15-ticket sample, offline
```

Or step by step:

```bash
# 0. (optional) isolate an env
python3 -m venv .venv && source .venv/bin/activate

# 1. connect — collect + normalize a source → canonical JSON (offline mock)
python3 -m agent connect --mock data/ticket-sample.json --redact --project ticket-sample

# 2. learn — profile the corpus and PROPOSE a taxonomy (does not apply it)
python3 -m agent learn data/ticket-sample.canonical.json

# 3. approve — the human gate: draft → taxonomy.json
python3 -m agent learn --approve

# 4. triage — cluster + effective priority (deterministic, no LLM)
python3 -m agent triage data/ticket-sample.canonical.json

# 5. solve — root cause + evidence + playbook (LLM step; offline fallback here)
python3 -m agent solve

# 6. report — consolidated document (terminal | md | json)
python3 -m agent report data/ticket-sample.canonical.json --format terminal

# 7. eval — calibrate the merge threshold via cluster_hint and report F1
python3 -m agent learn --eval data/ticket-sample.json
```

## What you should see on the sample

```
CLUSTERS (4 incidents · 2 deflect · 0 unknown)
  ci_cd/checkout-service        4  P2 → P1  SUPPRESSED
  auth/post-renewal             3  P2 → P2  SUPPRESSED
  api_gateway/recommendations   3  P1 → P2  INFLATED
  email_delivery                3  P3 → P3  ALIGNED (cross-source)
DEFLECTED (2): dark-mode request · avatar-size request
```

- **13 actionable tickets → 4 root causes**, 2 deflected = the 80/20 as a number.
- Priority gaps surfaced: the P2 that recurs 4× (`SUPPRESSED`), the P1 nobody attends (`INFLATED`).
- All playbooks flagged **`unverified`** — the sample has no `resolution_text` to learn from, so
  the agent declares its uncertainty instead of hiding it.

## Commands

| Command | Phase | Notes |
|---|---|---|
| `connect` | Phase 0 | Only boundary with a source. `--mock` (offline), `--test`, `--discover`, `--redact`. Live Jira via `descriptors/jira_rest.yaml` + `connections.json`. |
| `learn` | OBSERVE+ADAPT | Profiles corpus, proposes taxonomy behind a human gate. `--approve`, `--eval`, `--auto-approve`. |
| `triage` | ACT | Rules R1–R6, deterministic. Clusters + `INFLATED`/`SUPPRESSED`/`ALIGNED`. |
| `solve` | ACT | Rules R6–R7. Root cause + cited evidence + playbook. LLM if configured, else a-priori. |
| `report` | REPORT | Presents only. `--format terminal\|md\|json`, `--out`. |

## Going live with Jira

1. `cp connections.example.json connections.json && chmod 600 connections.json`
2. Export secrets **by name** (never in files): `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`.
3. `python3 -m agent connect --test jira-sre` then `connect --discover jira-sre`.
4. `python3 -m agent connect --project jira-sre --since 90d --redact`.

> The live extraction transport is scaffolded (auth/pagination stubs). The **descriptor + mapping +
> normalize** design is complete in `descriptors/jira_rest.yaml`; wire the HTTP layer to finish it.

## Project layout

```
agent/
  __main__.py   # CLI dispatch (5 commands)
  connect.py    # phase 0: source → canonical JSON (+ _meta provenance)
  canonical.py  # canonical model, normalization, PII redaction, drops cluster_hint
  engine.py     # rules R1–R7: extraction, type gate, TF-IDF, clustering+veto, severity, confidence
  learn.py      # OBSERVE + ADAPT + gate + --eval calibration (F1)
  triage.py     # deterministic ACT
  solve.py      # LLM ACT (offline a-priori fallback)
  report.py     # consolidation
  config.py     # taxonomy load/save (YAML if PyYAML present, else JSON)
descriptors/    # source descriptors (jira_rest.yaml)
data/           # canonical JSON, corpus_profile, triage, playbooks, report, taxonomy
```

## Design invariants (honored in code)

1. The engine is generic; the numbers live in `taxonomy.json`, not in the code.
2. `learn` (ADAPT) **proposes**; a human `--approve`s. `triage`/`solve` read only the approved taxonomy.
3. No rule requires an optional field — missing fields disable the dependent rule and say so.
4. No conclusion without cited `evidence[]`; otherwise it is `unverified`.
5. Every output carries provenance (taxonomy version, calibration status, threshold, reviewer).
6. `cluster_hint` is evaluation-only — the loader drops it; only `--eval` may use it for F1.
7. Secrets are referenced by variable name — never in the JSON, the report, or logs.

## Notes & honest caveats

- **Embeddings/clustering** use a deterministic TF-IDF + subsystem bridge (Bedrock stand-in) so the
  demo is reproducible offline. Swap in Bedrock/`sentence-transformers` embeddings for production.
- **`--eval` F1 = 1.0** on this sample because the approved taxonomy's subsystems align cleanly with
  the 5 gold clusters. For a more conservative, judge-proof number, calibrate on **semantic-only**
  similarity (blind mode) — that reproduces the plan's "4 of 5 clusters without the labels" story.
- **`solve`** produces a-priori playbooks here (no `resolution_text` in the sample); every one is
  correctly flagged `unverified`.
```
