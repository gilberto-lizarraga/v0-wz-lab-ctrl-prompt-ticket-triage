# Context — STAYSelect Hotel Booking Platform

## The Company

**STAYSelect** is a hotel reservation management company currently in expansion. They operate with third-party software to read and manage their bookings, which creates a vendor lock-in that limits their growth and autonomy.

**Logo:** STAYSelect — Hotel Booking Platform
**Brand colors:** Blue (#1A6FA8), Teal (#1B8FA8), Orange/coral (#E8622A)

**Pilot property:** Sunset Hotel — Cancún, Quintana Roo, México
**Coordinates:** `21.1619° N, -86.8515° W` (used for the weather widget)

---

## The Problem

STAYSelect today:
- Depends on external software they don't control to access their own reservation data
- Has no unified visibility into their operations (reports, dashboards, booking detail)
- Is in a growth phase and has committed to investors to become independent of that vendor lock
- Needs this tool as a foundation for their future AI and ML strategy *(out of scope for the prototype)*

---

## What Wizeline Proposes

A **proprietary operational dashboard** — read-only in this phase — where the STAYSelect team can:

1. View key metrics of their hotel operation in real time
2. Analyze reservation patterns, cancellations, and revenue
3. Look up the full detail of any individual booking
4. Stop depending on manual reports from the external vendor

**Key sales message:** *"This prototype is the proof that in days — not months — we can give you the tool that breaks your vendor dependency and lays the foundation for your data strategy."*

---

## Prototype User

| Field | Detail |
|---|---|
| **Role** | Hotel Operations Manager / Revenue Manager |
| **Goal** | Monitor reservations, occupancy, and revenue without relying on manual vendor reports |
| **Main pain** | Delayed and fragmented visibility into their own operations |
| **Expected action** | Open dashboard → filter by date/type → review a specific booking detail |

---

## Prototype Scope

**IN scope:**
- Dashboard with core KPIs (total bookings, cancellation rate, avg price, occupancy)
- Visualizations: bookings by month, by room type, by channel, by status
- Reservations table with filters and search
- Individual reservation detail view

**OUT of scope:**
- Login / authentication
- Writing or editing reservations
- Real integrations with external APIs
- AI / ML module (mentioned as future vision to the client)

---

## Dataset

File: `../04_Data_Sources/Hotel Reservations.csv`

Key fields:
- `Booking_ID` — unique identifier
- `arrival_year`, `arrival_month`, `arrival_date` — arrival dates
- `room_type_reserved` — room type
- `market_segment_type` — channel (Online, Offline, etc.)
- `avg_price_per_room` — average price per night
- `booking_status` — Canceled / Not_Canceled
- `no_of_adults`, `no_of_children` — group composition
- `no_of_special_requests` — special requests
- `lead_time` — days in advance the reservation was made
