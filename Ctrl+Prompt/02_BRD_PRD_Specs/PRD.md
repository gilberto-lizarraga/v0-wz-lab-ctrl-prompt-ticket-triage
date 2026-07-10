# PRD — Disney Agent Support Tickets

> Product Requirements. Source: brief §5, §11 + `generic-agent-plan.md` architecture.
> CLI-first. No GUI. Live Jira + multi-source `connect` layer.

## 1. Product summary

A command-line agent that ingests support tickets from **any board** (Jira live for the demo),
groups them into **root-cause incidents**, corrects the gap between declared priority and real
urgency, and emits **auditable, evidence-backed resolution playbooks**.

## 2. Architecture — three phases + connect + report

```
CONNECT ──► OBSERVE ──► ADAPT ──► ACT ──► REPORT
(collect)   (profile)  (propose) (execute)(present)
                          │
                   HUMAN GATE: ADAPT proposes, it never self-approves
```

The critical dependency: **the adaptation phase cannot self-approve.** A poorly inferred
taxonomy produces plausible, wrong clusters and confident playbooks over false root causes —
the most expensive, hardest-to-detect failure. A human approves the taxonomy before ACT runs.

## 3. Commands (the six-command scope)

| Command | Phase | What it does |
|---|---|---|
| **`run`** | ALL | One command that chains the whole pipeline: `connect → learn → approve → triage → solve → report`. The simple path. |
| **`connect`** | Phase 0 | Talks to a source (Jira live / mock / descriptor), normalizes to a canonical JSON. The **only** boundary with an external system. |
| **`learn`** | OBSERVE + ADAPT | Profiles the corpus with zero domain knowledge, then **proposes** a domain taxonomy for human review. |
| **`triage`** | ACT | Deterministically classifies, clusters, and computes **effective priority** vs declared. No LLM. |
| **`solve`** | ACT | The only LLM step: root-cause hypothesis + evidence + step-by-step playbook per cluster. |
| **`report`** | REPORT | Consolidates clusters, priority gaps and playbooks into a readable document with provenance. |

> Brief §5 names `learn`/`triage`/`solve` as the core three. `connect` and `report` are kept as
> explicit supporting commands: `connect` is what makes **live Jira + multi-source** real, and
> `report` is the artifact for the client-side decision-maker/SME. **`run`** was added so the whole
> pipeline is one command instead of five manual steps; the granular commands remain for inspecting
> a stage. A `bin/agent` launcher makes them first-class (`agent connect …`).

## 4. Functional requirements

### 4.1 `connect` (multi-source, mock + live)
- Descriptor-driven: `rest` / `graphql` / `file` kinds (`descriptors/*.json`). Onboarding a source
  = writing a descriptor (config), not code.
- **Jira live** via API token; secrets referenced **by variable name**, never by value.
- **Multiple accounts/companies:** each `connections.json` entry has its own `base_url`, its own
  credential env vars, and its own Jira project via a `query.jql` override or `vars` placeholders.
- `--mock <file.json>` skips transport for offline demo.
- `--discover` inventories fields/vocabularies before a full pull; `--test` validates auth first.
- `--redact` masks PII on real sources. Unknown vocab values map to `default` **and are logged**.
- Output: a self-contained **canonical JSON** with a `_meta` provenance block (field coverage,
  vocabularies, counts, discards, time span). Everything downstream runs over this JSON.

### 4.2 `learn` (OBSERVE → ADAPT → gate)
- OBSERVE: normalize, profile field coverage, embed `title+body`, blind-cluster (no taxonomy),
  emit `corpus_profile.json` (silhouette, vocabulary_divergence, cross-source clusters).
- ADAPT: discover entities, propose subsystems (LLM), **calibrate merge threshold** against a
  labeled subset (F1 sweep) or fall back to a heuristic and **say so**.
- Gate: emits `taxonomy.draft.json`; `triage`/`solve` read **only** the approved `taxonomy.json`
  (YAML auto-detected if PyYAML is present). `--auto-approve` exists for CI/demo and `run`, but
  stamps `calibration_status: unreviewed`.

### 4.3 `triage` (deterministic engine, rules R1–R6)
- R1 extraction · R2 type gate (INCIDENT / FEATURE_REQUEST / UNKNOWN) · R3+R4 clustering with
  **entity veto** · R5 effective priority (`INFLATED` / `SUPPRESSED` / `ALIGNED`) · R6 RCA queue
  ordered by `severity_real × ticket_count` — **not** by declared priority.

### 4.4 `solve` (LLM, rules R6–R7)
- Chained prompts: classify → root-cause (+ `alternative_hypotheses`, mandatory) → playbook.
- R7 confidence + **cited evidence[]**. Without evidence → `unverified`, printed as a hypothesis,
  never as a firm conclusion. Playbooks are plain terminal text, numbered, no auto-execution.

### 4.5 `report`
- Provenance cover · executive 80/20 summary · incident table · priority-gap section ·
  playbooks with banners · deflect/unknown · calibration appendix (F1 if `--eval` ran).
- Formats: `terminal | md | json`. Every figure reconciles with `connect`'s `_meta`.

## 5. Non-functional requirements
- **Stack:** stdlib-first (runs with zero installs); Typer/Bedrock/scikit-learn/PyYAML are optional
  production upgrades. Config is JSON by default, YAML if PyYAML is present.
- **Provenance on every output** (taxonomy version, calibration status, threshold, reviewer).
- **Degradation rule:** no rule may *require* an optional field; missing → rule disabled + declared.
- **`cluster_hint` is evaluation-only** — the production loader drops it explicitly.
- **Latency:** cache embeddings + LLM responses (SQLite) so the pitch isn't ruined by latency.
- **Security:** `600` on credentials file; secrets never in JSON, report or logs.

## 6. Success criteria (on the 15-ticket sample)
- Reconstruct the **5 clusters without reading `cluster_hint`** (report F1 with `--eval`).
- Collapse **13 actionable tickets → 4 root causes**, deflect 2 → the 80/20 as a number.
- Show the priority gap: `checkout-service` P2 recurring 4× = `SUPPRESSED`;
  `recommendations` P1 unattended = `INFLATED`.
- All playbooks correctly flagged `unverified` (no `resolution_text` in the sample to learn from).

**Source:** brief §5, §11.
