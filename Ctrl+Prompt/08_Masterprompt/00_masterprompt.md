# 00_Masterprompt — Project Rector Prompt

## Files to attach before sending this prompt

- `01_Context/disney-context.md` — business context (the 80% problem, the users, the goal)
- `02_BRD_PRD_Specs/PRD.md` — product spec (six commands, phases, rules R1–R7)
- `03_UXUI/cli-output-style.md` — terminal output conventions
- `05_APIs/README.md` — live Jira + multi-source `connect` layer
- `06_Features/features-disney.md` — prioritized feature list
- `04_Data_Sources/ticket-sample.json` — the 15-ticket synthetic sample

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

We're going to build together a **CLI-first agent** called **Disney Agent Support Tickets** —
a terminal tool for SRE/DevOps engineers that ingests a support-ticket backlog, collapses it into
**root-cause incidents**, corrects the gap between declared and real priority, and prints an
**auditable resolution playbook**.

Before writing a single line of code, carefully read the attached files:
- `disney-context.md` — who the client is, the ~80%-on-tickets problem, and what we must demonstrate
- `PRD.md` — the product: six commands, the three-phase architecture, and engine rules R1–R7
- `cli-output-style.md` — this is a **terminal tool, not a dashboard**; follow the output style
- `05_APIs/README.md` — Jira is **live**; other sources come through a descriptor-driven layer

This first prompt establishes the ground rules. **Do not generate code yet.**

### Project stack (stdlib-first; libraries are an optional production upgrade)

The shipped reference build runs on the **Python standard library only** — zero installs, so the
demo can't be broken by a missing dependency on stage. Each stdlib choice has a documented
production upgrade you can swap in when needed.

- **Language:** Python 3.11+
- **CLI framework:** `argparse` (stdlib). *Upgrade:* Typer.
- **Embeddings:** deterministic **TF-IDF cosine** (stdlib). *Upgrade:* Amazon Bedrock (Titan/Cohere)
  via `boto3`, or local `sentence-transformers`.
- **Clustering:** pure-Python agglomerative (average linkage, no predefined `k`). *Upgrade:* scikit-learn.
- **LLM (RCA + playbooks):** optional — deterministic a-priori playbooks when no LLM is configured.
  *Upgrade:* Amazon Bedrock (Claude on Bedrock), the only step that would call an LLM.
- **Config:** **JSON** by default — `connections.json`, `descriptors/*.json`, `taxonomy.json`.
  YAML is auto-detected and used if PyYAML is present.
- **Cache:** SQLite (embeddings + LLM responses) for the live path, so latency doesn't ruin the demo.
- **Data:** synthetic / anonymized only in this phase.

### Non-negotiable ground rules

1. **CLI only. No GUI, no dashboard, no web server.** Output is designed for a terminal.
2. **Six commands:** `run` + `connect · learn · triage · solve · report`. `learn/triage/solve` are
   the brief's core three; `connect` (live Jira + multi-source) and `report` are kept in scope;
   **`run` chains the whole pipeline in one command** (the simple path) — the granular commands
   still exist for inspecting a stage.
3. **`connect` is the only boundary with a source.** Everything downstream runs over a canonical
   JSON. `--mock` loads that JSON directly — a first-class fallback, not a special case.
   Ship a launcher `bin/agent` so the commands are first-class (`agent connect …`).
4. **Multi-source by descriptor:** Jira live is primary; Zendesk/PagerDuty/file sources are
   onboarded as config (`descriptors/*.json`), never as new code. Each `connections.json` entry is
   an independent **account/company** (own `base_url`, own credential env vars, own project via
   `query`/`vars`).
5. **ADAPT proposes, it never decides.** `learn` emits `taxonomy.draft.json`; a human approves it
   into `taxonomy.json`, which is the only config `triage`/`solve` read.
6. **No rule requires an optional field.** If a field is missing, the dependent rule is disabled
   and **declares so** — it never fails or invents a default.
7. **No conclusion without cited `evidence[]`.** Otherwise the output is `unverified` and printed
   as a hypothesis, not a fact. Playbooks are printed, **never auto-executed**.
8. **Provenance on every output:** taxonomy version, `calibration_status`, merge threshold, reviewer.
9. **`cluster_hint` is evaluation-only.** The production loader drops it explicitly; it may be used
   solely by `--eval` to compute F1.
10. **Secrets by variable name, never by value.** Never in the canonical JSON, the report, or logs.

### Collaboration rules

1. **If anything about the spec, data, or a design decision is unclear — ask before executing.**
2. **Do not build features I haven't asked for.** Suggest improvements; don't implement unconfirmed.
3. **Each build prompt is autonomous** — it states what already exists, what to build, and what
   context files apply. Read the full context before generating.
4. **Keep provenance and degradation behavior consistent** across every command.

### What I need from you now

Confirm that:
1. You read and understood the Disney context and the PRD.
2. You're clear on the stack, the six commands, and the ten ground rules.
3. You have any questions before we start building.

If everything is clear, reply with a **5-point summary** of what you'll build and how you'll
approach it, so we validate alignment before the first code prompt.

─────────────────────────────────────────────────────────────────────────────

---

## Validation before advancing to 01_prompt

- [ ] The assistant confirms it read the Disney context + PRD
- [ ] It confirms the stack (Python stdlib-first; Typer/Bedrock/scikit-learn as optional upgrades)
- [ ] It confirms CLI-only + the six commands (`run` + the five) + the human gate
- [ ] It has no blocking questions, or they were resolved
- [ ] Its summary correctly reflects: run → (connect → learn → triage → solve → report)

**Only advance to `01_prompt.md` when this checklist is complete.**
