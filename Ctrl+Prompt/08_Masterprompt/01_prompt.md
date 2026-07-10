# 01_Prompt — Foundation: canonical model + `connect` + ticket data

## Context (what already exists)
- The master prompt (`00_masterprompt.md`) established the stack, the six commands, and the ten
  ground rules. Nothing has been coded yet.

## Attach
- `05_APIs/README.md`
- `04_Data_Sources/ticket-sample.json`

## Build now

**1. Project skeleton**
- A Typer app `agent` with the five subcommands stubbed: `connect`, `learn`, `triage`, `solve`,
  `report`. Only `connect` is implemented in this prompt; the rest print "not yet implemented".

**2. Canonical ticket model**
```
id (req) · title (req) · body (req) · created_at (req)
source · reporter · declared_priority (0..4, 0=most severe) · status {open,in_progress,resolved}
resolution_text · raw_extra (unmapped fields, preserved not read)
```
- Enforce the **degradation rule**: optional fields may be absent; nothing invents defaults.

**3. `connect` command (the only source boundary)**
- `--mock <file.json>`: load a canonical JSON directly (implement this path first, using the
  sample). Explicitly **drop `cluster_hint`** when building tickets.
- `--project <name>`: descriptor-driven collection. Support `kind: rest | file` minimally.
- Live **Jira** via `descriptors/jira_rest.json` + `connections.json` (basic auth, token by env
  var name). Include `--test` (auth + reachability) and `--discover` (sample + field/vocab inventory).
- `--redact` (mask emails/names/tokens on real sources). `--since <window>`.
- Map + normalize per descriptor; unknown vocab → `default` **and log it**; capture unmapped →
  `raw_extra`; discard records missing REQUIRED fields (count + reason).
- Write `data/<project>-<date>.canonical.json` with a `_meta` block:
  `n_extracted, n_valid, n_discarded, discard_reasons, field_coverage, sources,
  priority_vocabulary, unmapped_fields, temporal_span_days, pii_redacted`.

**4. Secrets**
- Secrets by env-var **name** only. Verify `600` on `connections.json`. Never write secrets to the
  JSON or logs.

## Acceptance
- `agent connect --mock 04_Data_Sources/ticket-sample.json` produces a canonical JSON of 15 tickets
  with a correct `_meta` (declared_priority coverage 1.0, resolution_text 0.0, sources Jira/Zendesk/
  PagerDuty), and `cluster_hint` is **absent** from every ticket.
- `agent connect --test jira-sre` cleanly reports auth success/failure without extracting.

## Validation before 02_prompt
- [ ] Canonical model + degradation rule implemented
- [ ] `--mock` path works on the sample and drops `cluster_hint`
- [ ] `_meta` provenance block is complete and reconciles counts
- [ ] Jira descriptor + `--test`/`--discover` scaffolded; secrets by name only
