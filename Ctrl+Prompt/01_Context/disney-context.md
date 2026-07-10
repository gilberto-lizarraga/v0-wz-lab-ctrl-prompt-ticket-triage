# Context — Disney Agent Support Tickets

> ⚠️ Grounded in the fully-answered POC brief (score 14/20 · HIGH). Confirm the offshoring
> detail and exact ticket volume with **Luciano** before treating any number as final.

## The Company / Team

Disney's internal **DevOps / SRE team**. Over the last two years the team has burned
**~80% of its time on support tickets**, leaving almost no room for innovation. They are
also **training an offshore team** to absorb part of the load. The opportunity is to
**flip that 80/20 ratio**.

- **Delivery lead:** Luciano
- **Product owner:** Ivan Rueda
- **R&D owner:** Mich Galvez
- **Client-side decision-maker + SME:** TBD — route hackathon-week questions to
  **Daniela Martín** meanwhile.

## The Problem

Today the team:

- Spends ~80% of its time manually triaging incoming tickets, most of which are
  **recurring or low-value**.
- Has **no unified visibility across ticketing sources** (Jira, Zendesk, PagerDuty), so the
  same root-cause issue surfaces in multiple systems without ever being flagged as a pattern.
- Lets **truly urgent tickets get buried** among noise and priority-inflated requests.
- **Re-investigates the same recurring issues** over and over, because nothing surfaces the
  underlying pattern or root cause.

## What We Propose

A **CLI-first agent** for exceptionally technical, terminal-native SRE/DevOps engineers.
It does not answer tickets one by one — it **collapses N repeated tickets into a small set of
root-cause incidents** so the team fixes the problem once instead of mitigating the symptom
N times. It corrects the gap between *declared* priority and *observed* urgency, and emits an
auditable, ready-to-run **resolution playbook**.

> **The lean-in moment (build for this):** the CLI turning a chaotic wall of "High Priority"
> tickets into **one** clean root-cause incident with a **trustworthy playbook** — not the
> deflection step.

## The User

| Field | Detail |
|---|---|
| **Role** | SRE / DevOps engineer · on-call support lead |
| **Environment** | Terminal-native — a CLI is the deliberate choice, not a dashboard |
| **Goal** | Quickly tell which incoming tickets are truly urgent vs recurring, low-value noise |
| **Main pain** | Triage time spent on duplicates of known issues or non-urgent tickets |
| **Expected flow** | `connect` a source → `learn` history → `triage` incoming → `solve` the top incident → `report` |

## Volume (illustrative — confirm with SRE once assigned)

- **~120–150 tickets/week** feeding the queue.
- Demo runs on a **synthetic, anonymized** sample: 15 tickets across 5 realistic clusters,
  scaling to **50–100** for a more convincing clustering/ranking demo.

## Sources (multi-source by design — see 05_APIs)

Jira is the **primary, live** source in scope. But the core pain is **cross-source blindness**,
and the sample data itself already spans **Jira, Zendesk and PagerDuty**. The agent is therefore
built on a source-agnostic `connect` layer: **Jira live** for the demo, with Zendesk / PagerDuty /
in-house trackers onboarded as **descriptors** (config, not code). This is what lets the agent
flag "the same root cause is being reported in three systems."

## Guiding principle

> The agent may operate under uncertainty. It may not hide it.

Every output carries its provenance: which threshold was used, whether it was calibrated, what
evidence backs it, and whether a human reviewed the configuration. An SRE about to run steps
against production has the right to know whether a root cause came from a validated threshold or
a guess.

**Source:** brief §1–§4 (fully answered).
