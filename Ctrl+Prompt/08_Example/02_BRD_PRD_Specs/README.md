# 02_BRD_PRD_Specs

Business and product requirements documents that guide v0 on what to build.

## Contents

- **BRD.md** — Business Requirements Document: executive summary, AS-IS situation, business objectives, stakeholders, scope, risks, and acceptance criteria
- **PRD.md** — Product Requirements Document: personas, 3-screen architecture, data sources, full screen specs with exact column definitions and KPI calculations, user stories, and acceptance criteria per feature

## Quick Reference (for the Masterprompt)

**Product:** STAYSelect Operations Dashboard
**Type:** Web app — read-only, single page application
**User:** Hotel Operations Manager / Revenue Manager

**Main flow:**
1. User opens the dashboard → sees KPIs and charts of current state
2. Navigates to the reservations table → filters by status, date, or channel
3. Clicks on a reservation → sees the full detail view
4. Can return to the dashboard from any point

**Technical constraints:**
- No login required
- No data writes or edits
- Reads from local CSV (Hotel Reservations.csv)
- Must look good on laptop screen (1440px)
