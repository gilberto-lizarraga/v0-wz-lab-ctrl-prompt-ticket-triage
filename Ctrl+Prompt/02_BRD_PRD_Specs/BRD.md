# BRD — Disney Agent Support Tickets

> Business Requirements. Source: brief §5, §11 (fully answered).
> ⚠️ Confirm real ticket volume with the client-side SRE before treating numbers as final.

## 1. Business case

Disney's DevOps/SRE team spends **~80% of its time on support tickets**, most of them recurring
or low-value, leaving near-zero room for innovation. The business goal is to **flip that ratio**
by attacking the root cause of the volume, not the symptoms.

The wedge is **deduplication + root-cause collapse**: turning a flat wall of "High Priority"
tickets into a small, ranked set of root-cause incidents, each with a trustworthy resolution
playbook. Fixing one root cause retires many tickets at once.

## 2. Business objectives & KPIs

| Objective | Metric | Target (demo-level) |
|---|---|---|
| Reduce triage load | Tickets collapsed into root causes | 13 actionable tickets → **4 root causes** on the 15-ticket sample |
| Reclaim innovation time | % volume attributable to top recurring causes | Surface the top ~3 causes driving the majority of volume |
| Reduce MTTR | Time from ticket to actionable playbook | A ranked, evidence-backed playbook printed in one `solve` run |
| Correct priority inflation | # tickets re-ranked (declared ≠ real) | Detect `INFLATED` / `SUPPRESSED` gaps automatically |
| Cross-source visibility | Root causes spanning >1 source | Flag clusters that appear across Jira / Zendesk / PagerDuty |

## 3. Scope

**In scope**
- CLI-first agent (five commands — see PRD): `connect · learn · triage · solve · report`.
- **Live Jira** integration (dev/sandbox board, API token) as the primary source.
- **Multi-source** collection via a descriptor-driven `connect` layer (Zendesk, PagerDuty,
  in-house trackers). `--mock` supported for offline demo resilience.
- LLM backend (e.g. **Amazon Bedrock** or similar) for root-cause analysis and playbooks.
- Synthetic / anonymized data only for the demo.

**Out of scope**
- Any GUI / web dashboard.
- Auto-execution of fixes into production (playbooks are printed, never run).
- Writing/updating tickets back to the source system.
- Real client data / PII without explicit clearance.

## 4. Stakeholders

| Role | Owner |
|---|---|
| Delivery lead | Luciano |
| Product owner | Ivan Rueda |
| R&D owner | Mich Galvez |
| Client decision-maker | TBD (interim: Daniela Martín) |
| Client SME (SRE) | TBD |

## 5. Business constraints & assumptions

- **Terminal-native users** — CLI is a deliberate fit, not a shortcut.
- **Jira is the only live source guaranteed**; other sources are demoed via mock/descriptor.
- Dev/sandbox **Jira API token must be confirmed available before build day**.
- Demo must survive a live-API outage → `--mock` path is a first-class fallback, not a patch.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Jira API/token unavailable at pitch | `--mock` fallback + pre-cached canonical JSON |
| Uncalibrated clustering → plausible-but-wrong groups | `calibration_status` on every output; F1 via `--eval` |
| Overfitting to 15 tickets | Scale to 50–100 with rule-breaking adversarial cases |
| Real PII leaks into a shareable report | `--redact` mandatory on real sources; `contains_raw_pii` banner |

**Source:** brief §5, §11.
