# Features — Disney Agent Support Tickets

> Scope: CLI-first. Five commands. Build in order. Source: brief §1, §5.
> Out of scope: any GUI/dashboard, and any auto-execution of fixes into production.

## P0 — Must be in the demo (non-negotiable)

| # | Command / Feature | Description |
|---|---|---|
| F1 | **`connect` — collection layer** | Pull tickets from a source and normalize to canonical JSON. **Live Jira** primary; `--mock` fallback; descriptor-driven multi-source. Emits `_meta` provenance. |
| F2 | **`learn` — ingest + profile + propose** | Ingest historical ticket/resolution data, profile the corpus (zero domain knowledge), and **propose** a taxonomy behind a human-review gate. |
| F3 | **`triage` — categorize + fix priority** | Deterministically cluster tickets, compute **effective priority**, and flag `INFLATED` / `SUPPRESSED` / `ALIGNED`. Corrects priority inflation. |
| F4 | **Root-cause clustering + ranking** | Collapse repeated tickets into root-cause incidents; rank by `severity_real × ticket_count`, not declared priority. **Entity veto** prevents mixing distinct services. |

## P1 — Highly desirable (the WOW / lean-in moment)

| # | Command / Feature | Description |
|---|---|---|
| F5 | **`solve` — RCA + playbook** | The LLM step: print root-cause hypothesis + `alternative_hypotheses`, **cited evidence[]**, and a numbered, terminal-ready resolution playbook. |
| F6 | **Trust / provenance layer** | `calibration_status`, threshold, taxonomy version and reviewer on every output; `unverified` / `heuristic` banners. This is what makes the playbook *trustworthy*. |
| F7 | **`report` — consolidated output** | 80/20 executive summary, incident table, priority-gap section, playbooks with banners. Formats: `md/html/json/terminal`. For the client decision-maker/SME. |

## P2 — Nice to have (if time allows)

| # | Feature | Description |
|---|---|---|
| F8 | **`--eval` calibration** | Use `cluster_hint` as a labeled set to sweep the merge threshold and report **F1** — the number to defend in front of judges. |
| F9 | **Cross-source flagging** | Explicitly mark clusters that span >1 source (Jira/Zendesk/PagerDuty). |
| F10 | **Embedding/LLM cache (SQLite)** | Avoid latency ruining the live pitch. |
| F11 | **Scale dataset to 50–100** | With adversarial cases: two services same symptom, feature request naming a service, legit 1-day-old P1, orphan tickets, two close-but-distinct clusters. |

## Build order (mirrors the master-prompt chunks)

```
0. Master prompt (ground rules, no code)
1. connect + canonical model + ticket data        → F1
2. learn + triage: clustering + RCA ranking (P0)   → F2 F3 F4
3. solve: playbook generation (P1)                 → F5 F6
4. report + --eval + iterate                       → F7 F8+
```

## Explicit out-of-scope
- Any GUI / web dashboard.
- Auto-execution / auto-remediation of fixes into production (playbooks are **printed**, never run).
- Writing/updating tickets back to the source.
- Real client data / PII without clearance.

**Source:** brief §1, §5.
