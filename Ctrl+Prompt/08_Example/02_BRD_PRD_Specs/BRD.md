# Business Requirements Document (BRD)
## STAYSelect — Operations Dashboard
**Version:** 1.0  
**Date:** 2026-05-26  
**Prepared by:** Wizeline — Product Discipline  
**For:** STAYSelect — VP / Operations Director

---

## 1. Executive Summary

STAYSelect is a hotel reservations platform in expansion that currently relies on third-party software to access and manage property data. This dependency creates vendor lock-in that limits operational autonomy, delays business visibility, and compromises the technology independence commitments made to its investors.

Wizeline proposes the development of a proprietary **Operations Dashboard** for STAYSelect — an internal tool that centralizes reservation visualization, operational metrics, and booking detail per property, eliminating vendor dependency for access to their own data.

---

## 2. Business Context

### 2.1 The company

STAYSelect operates a chain of hotel properties. The pilot property for this project is **Sunset Hotel**. The company is in an active expansion phase and has made formal commitments to its investors to achieve technological independence from its current vendor.

### 2.2 Current situation (AS-IS)

| Aspect | Current situation |
|---|---|
| Data access | Through external vendor software — no direct access |
| Reports | Generated manually or exported from the vendor |
| Operational visibility | Delayed, fragmented, and dependent on third parties |
| Flexibility | None — any change to reports requires the vendor |
| Data / AI strategy | Blocked by lack of own infrastructure |

### 2.3 The core problem

> STAYSelect has no direct, unified, or timely visibility into its own reservation operations. Every report depends on the vendor, creating operational delays and a technological dependency that the business can no longer sustain in its expansion phase.

---

## 3. Business Objectives

| ID | Objective | Success metric |
|---|---|---|
| OB-1 | Eliminate vendor dependency for operational data access | 100% of key reports available in proprietary tool |
| OB-2 | Give the operations team real-time visibility over reservations, cancellations, and revenue | Operations Director accesses the dashboard daily without needing to export reports |
| OB-3 | Lay the technological foundation for STAYSelect's data and AI strategy | Architecture ready to connect to real data sources in the next phase |
| OB-4 | Demonstrate progress toward technological independence to investors | Functional prototype presentable in Q3 2026 |

---

## 4. Stakeholders

| Role | Name / Area | Interest in the project |
|---|---|---|
| **Decision maker** | VP / Operations Director — STAYSelect | Operational efficiency, visibility into operations, reduced vendor dependency |
| **End users** | Operations Manager, Revenue Manager | Daily access to reservation metrics and booking detail |
| **Investors** | STAYSelect Board | Evidence of technological independence and readiness for AI strategy |
| **Provider** | Wizeline — Product Discipline | Demonstrate rapid delivery capability and value through AI prototyping |

---

## 5. Project Scope

### 5.1 IN scope — Phase 1 (this prototype)

- Operations dashboard with key reservation KPIs
- Data visualization for **Sunset Hotel** (pilot property)
- Property selector (UI prepared for multiple hotels, Sunset Hotel data in the demo)
- Reservations table with filters and search
- Individual reservation detail view
- Data read from reservations dataset (read-only)

### 5.2 OUT of scope — Phase 1

- Authentication and user management
- Creating, editing, or canceling reservations
- Real-time integration with external APIs or databases
- AI / ML module *(considered for future phases)*
- Billing or payments module
- Mobile app

### 5.3 Considerations for future phases

- Connection to STAYSelect's real database (replaces the CSV)
- Write module: create and manage reservations from the proprietary platform
- Implementation of AI models for cancellation prediction and price optimization
- Expansion to all properties in the chain

---

## 6. Business Requirements

| ID | Requirement | Priority | Justification |
|---|---|---|---|
| BR-1 | The system must show the current reservation status of Sunset Hotel without depending on the vendor | High | Primary project driver |
| BR-2 | The Operations Director must be able to see key KPIs within 10 seconds of opening the tool | High | Immediate operational visibility |
| BR-3 | The tool must allow filtering reservations by date, status, and booking channel | High | Daily operational need |
| BR-4 | It must be possible to view the full detail of any individual reservation | High | Resolution of operational issues |
| BR-5 | The design must reflect STAYSelect's brand identity | Medium | Team adoption of the tool |
| BR-6 | The architecture must be prepared to connect to real data in the next phase | Medium | Continuity of the technology roadmap |

---

## 7. Business Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Current vendor blocks access to historical data | Medium | High | The current dataset is sufficient for the prototype; data migration is in scope for the next phase |
| Internal resistance to tool change | Low | Medium | The dashboard is read-only — it doesn't replace existing workflows, it complements them |
| Investor expectations exceed the prototype scope | Medium | Medium | Clearly communicate that this is Phase 1 of a broader roadmap |

---

## 8. Business Acceptance Criteria

- [ ] The Operations Director can view Sunset Hotel reservation status without accessing the vendor's software
- [ ] The main KPIs (total bookings, cancellation rate, avg price, revenue) are visible on the main screen
- [ ] It is possible to filter and search reservations by key criteria
- [ ] The detail of any reservation is accessible with a single click
- [ ] The prototype is presentable to STAYSelect's investors as evidence of progress

---

*Document prepared as part of the "Prototype with v0 — From 0 to Hero!" program | Wizeline — Product Discipline*
