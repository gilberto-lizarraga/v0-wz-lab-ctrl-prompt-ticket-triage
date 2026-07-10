# Product Requirements Document (PRD)
## STAYSelect — Operations Dashboard
**Version:** 1.0  
**Date:** 2026-05-26  
**Prepared by:** Wizeline — Product Discipline  
**Reference:** BRD v1.0

---

## 1. Product Vision

> An operational dashboard that gives STAYSelect full visibility over their reservations — in their own tool, with their own brand, without depending on anyone else.

**Prototype internal tagline:** *"Your data, your tool, your decision."*

---

## 2. Users

### Primary persona — Operations Manager

| Field | Detail |
|---|---|
| **Fictional name** | Carlos Mendoza |
| **Role** | Operations Manager — Sunset Hotel |
| **Goal** | Review reservation status every morning and answer their director's questions in minutes |
| **Current frustration** | Has to log into vendor software, export a report, open it in Excel, and manually build the number they need |
| **Definition of success** | Opens the dashboard, sees everything they need on one screen, without exporting anything |

### Secondary persona — Operations Director

| Field | Detail |
|---|---|
| **Role** | VP / Operations Director — STAYSelect |
| **Goal** | Make fast decisions based on the real status of the properties |
| **Expected use** | Reviews the dashboard in board meetings or when needing to justify decisions |

---

## 3. Application Architecture

### 3.1 Screens

```
┌─────────────────────────────────────────────┐
│  HEADER: STAYSelect Logo + Hotel Selector   │
│          [Sunset Hotel ▼]                   │
├─────────────────────────────────────────────┤
│                                             │
│  NAV: Dashboard  |  Reservations            │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  [SCREEN 1: DASHBOARD]                      │
│  KPI Cards + Charts                         │
│                                             │
│  [SCREEN 2: RESERVATIONS]                   │
│  Table with filters + search                │
│                                             │
│  [SCREEN 3: RESERVATION DETAIL]             │
│  Full view of a single booking              │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.2 Data sources

| Source | Type | Use |
|---|---|---|
| `Hotel Reservations.csv` | Local file | All metrics, charts and reservations table |
| Open-Meteo API | Public REST API (free, no key required) | Real-time weather widget — Cancún, QRoo |

- The CSV is loaded on app start using PapaParse
- The weather API is called when the header mounts — no key, no authentication
- All reservation data corresponds to **Sunset Hotel, Cancún**

---

## 4. Screen Specifications

---

### SCREEN 1 — Dashboard

**Goal:** Executive view of Sunset Hotel's operational status.

#### 4.1 Global header
- STAYSelect logo (left)
- Hotel selector: dropdown with "Sunset Hotel" selected (read-only in this prototype)
- Active property name always visible
- **Weather Widget** (right side of header): current temperature + condition icon + "Cancún, MX"
  - Real-time data via Open-Meteo API
  - `latitude: 21.1619, longitude: -86.8515`
  - Shows: WMO icon + temperature in °C + city name
  - Loading skeleton while loading, silent on failure (does not break the dashboard)

#### 4.2 KPI Cards (top row)
Four metric cards, always visible:

| Card | Metric | Calculation | Format |
|---|---|---|---|
| Total Bookings | Total reservations | COUNT(Booking_ID) | Integer |
| Cancellation Rate | % cancellations | COUNT(Canceled) / COUNT(total) × 100 | Percentage with 1 decimal |
| Avg Price / Night | Average price per night | AVG(avg_price_per_room) | Currency with 2 decimals |
| Est. Revenue | Total estimated revenue | SUM(avg_price_per_room × (no_of_weekend_nights + no_of_week_nights)) | Short currency format (e.g. $2.4M) |

#### 4.3 Chart — Bookings by month
- Type: vertical bar chart or line chart
- X axis: month/year (arrival_month + arrival_year)
- Y axis: number of bookings
- Color-coded differentiating Canceled vs Not_Canceled (stacked or double line)

#### 4.4 Chart — Distribution by channel
- Type: donut chart
- Segments: Online, Offline, Corporate, Aviation, Complementary (market_segment_type)
- Legend with percentage per segment

#### 4.5 Chart — Reservations by room type
- Type: horizontal bar chart
- Y axis: Room_Type 1 … Room_Type 7
- X axis: number of reservations
- Single brand color (STAYSelect blue)

#### 4.6 Date filter (global)
- Range selector: start month — end month
- Affects all KPI Cards and charts on the screen
- Default: all available data

---

### SCREEN 2 — Reservations

**Goal:** Full reservation list with search and filter capabilities.

#### 4.7 Filter bar
| Filter | Type | Options |
|---|---|---|
| Status | Dropdown | All / Not_Canceled / Canceled |
| Channel | Dropdown | All / Online / Offline / Corporate / Aviation / Complementary |
| Room type | Dropdown | All / Room_Type 1…7 |
| Search | Text input | Search by Booking_ID |

#### 4.8 Reservations table
Visible columns:

| Column | CSV field | Format |
|---|---|---|
| Booking ID | Booking_ID | Badge/chip |
| Arrival | arrival_date/month/year | DD/MMM/YYYY |
| Guests | no_of_adults + no_of_children | "2 adults, 1 child" |
| Room | room_type_reserved | Clean name (e.g. "Type 1") |
| Nights | no_of_weekend_nights + no_of_week_nights | Total nights |
| Price/night | avg_price_per_room | $XXX.XX |
| Channel | market_segment_type | Color badge |
| Status | booking_status | Green chip (Not_Canceled) / red (Canceled) |
| Action | — | "View detail" button |

- Pagination: 20 rows per page
- Click on row → navigates to that reservation's detail
- Results counter: "Showing X of Y reservations"

---

### SCREEN 3 — Reservation Detail

**Goal:** Full view of all data for a single reservation.

#### 4.9 Layout
- "← Back to Reservations" button at the top
- Header with Booking_ID highlighted and status chip (Canceled / Not_Canceled)
- Two columns of grouped data:

**Left column — Stay information:**
- Arrival date
- Number of nights (weekday + weekend)
- Room type
- Meal plan (type_of_meal_plan)
- Required parking (required_car_parking_space)

**Right column — Guest and booking information:**
- Adults and children
- Booking channel (market_segment_type)
- Lead time (days in advance)
- Returning guest (repeated_guest) — special badge if true
- Special requests (no_of_special_requests)
- Average price per night
- History: previous cancellations / previous non-canceled bookings

---

## 5. Non-Functional Requirements

| ID | Requirement | Detail |
|---|---|---|
| RNF-1 | Performance | The dashboard must load completely in under 3 seconds with the full dataset |
| RNF-2 | Resolution | Optimized for 1440px width (standard laptop) |
| RNF-3 | Navigation | No page reloads — smooth navigation between screens |
| RNF-4 | Branding | STAYSelect colors, logo, and typography on all screens |
| RNF-5 | Accessibility | Readable text contrast, minimum font size 14px |

---

## 6. User Stories

### Epic: Operational Visibility

**US-01** — As an Operations Manager, I want to see Sunset Hotel's main KPIs as soon as I open the tool, so I don't have to generate a report manually.

**US-02** — As an Operations Manager, I want to see the booking trend by month, so I can identify occupancy patterns and anticipate low-demand periods.

**US-03** — As an Operations Director, I want to see the cancellation rate prominently displayed, so I can make quick decisions about booking policies.

**US-04** — As an Operations Manager, I want to filter reservations by status, channel, and date, so I can quickly find the records I need to review.

**US-05** — As an Operations Manager, I want to see the full detail of a reservation with a single click, so I can resolve guest inquiries without switching systems.

**US-06** — As an Operations Director, I want the tool to carry STAYSelect's branding, so I can present it to the board as a proprietary solution — not a generic prototype.

---

## 7. Acceptance Criteria by Feature

### F1 — KPI Cards
- [ ] 4 cards shown: Total Bookings, Cancellation Rate, Avg Price, Est. Revenue
- [ ] Values are correct against the dataset
- [ ] Update when date filter is applied

### F2 — Bookings by month
- [ ] Chart shows all months in the dataset
- [ ] Visually differentiates canceled vs not canceled
- [ ] X axis shows readable month/year format

### F3 — Reservations table
- [ ] Shows the 8 specified columns
- [ ] Pagination works (20 per page)
- [ ] Status, channel, and room type filters work correctly
- [ ] Booking_ID search returns the correct result

### F4 — Reservation detail
- [ ] Accessible from row click in the table
- [ ] Shows all CSV fields
- [ ] "Back" button returns to the table with active filters intact

### F5 — STAYSelect branding
- [ ] Logo visible in the header
- [ ] Brand colors applied consistently
- [ ] Hotel selector shows "Sunset Hotel"

### F6/F7 — Distribution charts
- [ ] Channel donut chart shows correct percentages
- [ ] Room type bars ordered by volume

### F8 — Date filter
- [ ] Affects KPIs and all charts
- [ ] Defaults to showing the full dataset

---

## 8. Screens — Visual Summary

```
DASHBOARD                    RESERVATIONS               DETAIL
─────────────────────        ─────────────────────      ─────────────────────
[Logo] [Sunset Hotel▼]       [Logo] [Sunset Hotel▼]     [Logo] [Sunset Hotel▼]
──────────────────────       ──────────────────────      ──────────────────────
Dashboard | Reservations     Dashboard | Reservations   ← Back
──────────────────────       ──────────────────────      ──────────────────────
[KPI][KPI][KPI][KPI]        [Status▼][Channel▼][Type▼]  INN00001  ● Not Canceled
──────────────────────       [🔍 Search Booking ID  ]    ──────────────────────
[  Bookings / month  ]       ──────────────────────      Stay       │ Guest
[  Bar chart         ]       ID  │Arrival│Gst│...│⚡     Arrival:   │ Adults:
──────────────────────       ─────┼───────┼────┼───┼─    ...        │ ...
[Channel] │ [Room type]      ...  │  ...  │    │   │🔘
```

---

*Document prepared as part of the "Prototype with v0 — From 0 to Hero!" program | Wizeline — Product Discipline*
