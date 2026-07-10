# Context — QueueAI Ticket Support Triage

## The Company

**QueueAI** is an AI-powered ticket triage platform that automatically classifies and prioritizes incoming support tickets in real time. It reads ticket context the way a senior support engineer would, while filtering out the noise that gets misclassified as urgent. The result: critical problems reach the right team immediately, without the delays or human error of manual triage.

**Logo:** QueueAI — Ticket Support Triage
**Brand colors:** Iris (#5B4FE8), Persian green (#17A589), Charcoal navy (#2E2E38)

---

## The Problem

DevOps and support teams today:
- Spend the majority of their time (~80% by some estimates) manually triaging incoming tickets, most of which are recurring or low-value
- Have no unified visibility across ticketing sources (Jira, Zendesk, PagerDuty), so the same root-cause issue can surface in multiple systems without ever being flagged as a pattern
- Let truly urgent tickets get buried among noise and low-priority requests, since triage is manual and inconsistent
- Re-investigate the same recurring issues over and over because nothing surfaces the underlying pattern or root cause
- Need this tool as a foundation for a broader AI-driven support strategy *(out of scope for the prototype)*

---

## What QueueAI Proposes

An **AI-powered ticket triage prototype** — classification only in this phase — where the support/DevOps team can:

1. See every incoming ticket automatically classified by priority (P0–P4) based on its actual content, not just its source
2. Spot recurring clusters of tickets pointing to the same underlying issue, with a suggested root cause and frequency ranking
3. Distinguish tickets that are genuinely urgent from those that only look urgent on the surface
4. Flag low-value tickets (e.g. feature requests) as deflection candidates instead of routing them into DevOps triage

**Key sales message:** *"This prototype is the proof that in days — not months — we can show you which 20% of your tickets are eating 80% of your team's time, and stop the same issues from repeating unnoticed."*

---

## Prototype User

| Field | Detail |
|---|---|
| **Role** | DevOps engineer / on-call support lead |
| **Goal** | Quickly tell which incoming tickets are truly urgent and which are recurring, low-value noise |
| **Main pain** | Spending most triage time on tickets that are duplicates of known issues or not actually urgent |
| **Expected action** | Open dashboard → review auto-classified tickets by priority → drill into a recurring cluster's suggested root cause |

---

## Prototype Scope

**IN scope:**
- LLM-based classification of tickets into P0–P4 priority levels
- Clustering of recurring/duplicate tickets pointing to the same root cause
- Dashboard showing tickets grouped by priority and by cluster, with frequency ranking
- Ticket detail view showing the classification and its cluster context

**OUT of scope:**
- Login / authentication
- Writing or updating tickets back to the source system (Jira, Zendesk, PagerDuty)
- Live integrations with source ticketing systems (uses synthetic sample data in this phase)
- Automated remediation or auto-resolution of tickets (mentioned as future vision to the client)

---

## Dataset

File: `ticket-sample.json`

Key fields:
- `id` — unique ticket identifier
- `title` — short ticket summary
- `description` — full ticket text
- `source` — originating system (Jira, Zendesk, PagerDuty)
- `priority` — assigned priority label (P0–P4)
- `status` — current ticket status (e.g. Open)
- `created_at` — timestamp the ticket was created
- `reporter` — user or bot that filed the ticket
- `cluster_hint` — label indicating which recurring issue cluster the ticket belongs to

The sample also includes a `cluster_summary_for_demo` array, used to demonstrate pattern detection across tickets:
- `cluster` — name of the recurring issue
- `ticket_count` — number of tickets in that cluster
- `frequency_rank` — how often this cluster occurs relative to others
- `suggested_root_cause` — the underlying cause the cluster likely points to
