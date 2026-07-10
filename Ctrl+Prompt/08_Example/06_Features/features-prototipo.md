# Features — STAYSelect Dashboard Prototype

> Scope: read-only. The goal is to impress visually and demonstrate business value in minutes.

---

## P0 — Must be in the demo (non-negotiable)

| # | Feature | Description | CSV field |
|---|---|---|---|
| F1 | **KPI Cards** | Total bookings, Cancellation Rate, Avg Price/Room, Estimated Total Revenue | booking_status, avg_price_per_room |
| F2 | **Bookings by month** | Bar chart — reservation volume over time | arrival_month + arrival_year |
| F3 | **Reservations table** | Paginated list with search and filter by status (Canceled / Not_Canceled) | All fields |
| F4 | **Detail view** | Click on a row → see full reservation detail | Booking_ID and all its fields |
| F5 | **STAYSelect branding** | Logo, brand colors (blue + orange), clean typography | — |
| F6 | **Weather Widget** | Header widget with current weather in Cancún via Open-Meteo API — temperature, condition, icon | Real-time API |

---

## P1 — Highly desirable (adds WOW factor)

| # | Feature | Description | CSV field |
|---|---|---|---|
| F7 | **Channel distribution** | Pie or donut chart: Online vs Offline vs other | market_segment_type |
| F8 | **Room type distribution** | Which room types are booked most | room_type_reserved |
| F9 | **Date filter** | Date range selector for the full dashboard | arrival_year + arrival_month |
| F10 | **Cancellation rate visual** | Clear visual indicator of the cancellation percentage | booking_status |

---

## P2 — Nice to have (if time allows during hackathon)

| # | Feature | Description |
|---|---|---|
| F11 | Lead time distribution | Histogram of how many days in advance guests book |
| F12 | Repeated guests badge | Indicator for returning guests in the table |
| F13 | Special requests summary | How many reservations include special requests |

---

## Demo Notes

- The prototype loads the CSV directly — no real backend needed
- Dashboard → Table → Detail navigation must be fluid and without full page reloads
- Design should feel "enterprise" but clean — no random colors or amateur layouts
- If the client asks about the backend: *"today it reads from a CSV, but the architecture is ready to connect to your existing database"*
