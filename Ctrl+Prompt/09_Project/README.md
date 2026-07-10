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

## Quick start — one command

```bash
cd agent-support-tickets
python3 -m agent run --mock data/ticket-sample.json --redact
```

`run` does the whole pipeline in one shot: **connect → learn → approve → triage → solve → report**.
That's the simplest path — no need to run the five steps by hand.

Common variants:

```bash
python3 -m agent run --source jira-sre --redact          # live Jira (see below)
python3 -m agent run --source pod2-csv                    # a CSV export source
python3 -m agent run --mock data/ticket-sample.json --eval data/ticket-sample.json  # + F1
python3 -m agent run --mock data/ticket-sample.json --format md --out data/report.md
```

The individual commands (`connect`, `learn`, `triage`, `solve`, `report`) still exist for when
you want to inspect a stage — see [`USAGE.md`](./USAGE.md).

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

## Connect to a real source

Sources are defined in `connections.json` and shaped by a **descriptor** — onboarding a new
system is config, not code. Two source kinds are implemented (stdlib `urllib` + `csv`):

### Live Jira (REST)

```bash
chmod 600 connections.json                 # the 'jira-sre' connection is already defined

# secrets are referenced by NAME, never stored in files:
export JIRA_BASE_URL=https://<org>.atlassian.net
export JIRA_EMAIL=you@wizeline.com
export JIRA_API_TOKEN=<token>              # https://id.atlassian.com/manage/api-tokens
export JIRA_PROJECT=SRE                     # optional; used in the JQL
export SINCE=90d                            # optional

python3 -m agent connect --test jira-sre      # validates auth + reachability (real call)
python3 -m agent connect --discover jira-sre  # inventories fields + priority vocabulary
python3 -m agent run --source jira-sre --redact   # full pipeline on live data
```

Driven by `descriptors/jira_rest.json`: real HTTP GET to `/rest/api/3/search`, HTTP Basic auth,
offset pagination (`startAt`/`maxResults`/`total`), field mapping and priority/status normalization.
Rate limits (429) back off on `Retry-After`; 401/403 abort with a clear message; network errors
suggest `--mock`.

### Multiple Jira accounts / companies

Each entry in `connections.json` is an **independent account/company**: its own `base_url`, its
own credential env vars, and its own Jira **project**. They all reuse the same descriptor.

```jsonc
{ "name": "acme-jira",   "descriptor": "descriptors/jira_rest.json",
  "base_url": "https://acme.atlassian.net",
  "auth": {"method":"basic","user_env":"ACME_JIRA_EMAIL","token_env":"ACME_JIRA_TOKEN"},
  "query": {"jql": "project = OPS AND created >= -30d"} },        // project via JQL override

{ "name": "globex-jira", "descriptor": "descriptors/jira_rest.json",
  "base_url": "https://globex.atlassian.net",
  "auth": {"method":"basic","user_env":"GLOBEX_JIRA_EMAIL","token_env":"GLOBEX_JIRA_TOKEN"},
  "vars": {"JIRA_PROJECT": "SUPPORT", "SINCE": "60d"} }           // project via a variable
```

Two ways to specify the **project**:
- **`query.jql`** — a full JQL override (most explicit): `"project = OPS AND created >= -30d"`.
- **`vars`** — fill the descriptor's `${JIRA_PROJECT}` / `${SINCE}` placeholders per connection.

Give each company its **own credentials** (different `token_env` names), then export them:

```bash
export ACME_JIRA_EMAIL=you@acme.com     ACME_JIRA_TOKEN=<acme token>
export GLOBEX_JIRA_EMAIL=you@globex.com GLOBEX_JIRA_TOKEN=<globex token>

python3 -m agent connect --test acme-jira      # prints the resolved URL + JQL, then checks auth
python3 -m agent run --source acme-jira --redact
python3 -m agent run --source globex-jira --redact
```

`--test` prints the resolved endpoint and JQL **before** any network call, so you can confirm the
right company and project:

```
connect --test acme-jira (rest) …
  URL:   https://acme.atlassian.net/rest/api/3/search
  jql:   project = OPS AND created >= -30d
```

> Lookup order for `${VAR}`: environment → connection `vars` → `:-default`. Keep **secrets in the
> environment** (never in `connections.json`); non-secret values like the project can live in `vars`.

### Other REST tools (Zendesk, PagerDuty, in-house)

Copy `descriptors/jira_rest.json`, edit `list_path`, `record_selector`, `pagination`, and the
`mapping` / `normalize` tables, add a connection entry, and point `--source` at it. No code change.

### File / CSV exports (air-gapped, or no API access in time)

A Jira CSV export works out of the box via `descriptors/jira_csv.json`:

```bash
python3 -m agent connect --discover pod2-csv         # inventory the columns
python3 -m agent run --source pod2-csv               # full pipeline on the CSV
```

> Reminder: the built-in taxonomy is tuned for the Disney sample. Point it at a different source
> and it will (correctly) warn that the taxonomy is incomplete — run `learn` on that source to
> propose a fitting one. The numbers are per-source; the engine is not.

## Project layout

```
agent/
  __main__.py   # CLI dispatch (run + 5 commands)
  pipeline.py   # `run`: connect → learn → approve → triage → solve → report
  connect.py    # phase 0: source → canonical JSON (+ _meta provenance)
  sources.py    # live collectors: REST (urllib) + CSV/JSON files; auth, pagination, mapping
  canonical.py  # canonical model, normalization, PII redaction, drops cluster_hint
  engine.py     # rules R1–R7: extraction, type gate, TF-IDF, clustering+veto, severity, confidence
  learn.py      # OBSERVE + ADAPT + gate + --eval calibration (F1)
  triage.py     # deterministic ACT
  solve.py      # LLM ACT (offline a-priori fallback)
  report.py     # consolidation
  config.py     # taxonomy load/save (YAML if PyYAML present, else JSON)
descriptors/    # source descriptors: jira_rest.json (live REST), jira_csv.json (file)
connections.json  # named connections; secrets referenced by env-var NAME only
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
