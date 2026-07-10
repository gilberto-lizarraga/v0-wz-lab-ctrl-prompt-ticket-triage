# 02_Prompt — Dashboard: KPI Cards + Charts

## Context
The base layout is built. The DataProvider loads the CSV correctly and exposes `reservations` and `loading` to the entire app. Pages exist as placeholders.

## Objective
Build the complete Dashboard screen: 4 KPI cards and 3 charts using real data from the CSV.

## Files to attach in v0
- `00_Inputs/06_Features/features-prototipo.md`
- `00_Inputs/03_UXUI/design-system.md`

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

Build the **Dashboard** screen (`app/page.tsx`) using data from `useData()` in the DataProvider. Replace the placeholder with the full content.

### Dashboard Layout

```
Page: max-w-7xl mx-auto px-6 py-6

Row 1: grid grid-cols-4 gap-4
  → 4 KPI Cards

Row 2: grid grid-cols-3 gap-4
  → col-span-2: Bookings by month (BarChart)
  → col-span-1: Channel distribution (PieChart donut)

Row 3: grid grid-cols-1
  → Bookings by room type (horizontal BarChart)
```

### KPI Cards — exact calculations

Use shadcn's `Card` component for each:

| Card | Calculation | Format |
|---|---|---|
| Total Bookings | `reservations.length` | Integer with thousands separator |
| Cancellation Rate | `(canceled / total * 100).toFixed(1) + '%'` | "XX.X%" |
| Avg Price / Night | `(sum of avg_price_per_room / total).toFixed(2)` | "$XXX.XX" |
| Est. Revenue | `sum of (avg_price_per_room * (no_of_weekend_nights + no_of_week_nights))` | "$X.XM" or "$XXX,XXX" |

Each card has: lucide-react icon, label in `text-xs text-slate-500`, value in `text-2xl font-bold`, and a descriptive subtext in `text-xs text-slate-400`.

### Chart 1 — Bookings by month (Recharts BarChart)

- Group by `arrival_year + arrival_month` — label format: "Jan 2017", "Feb 2017"...
- Two bars per month: `Not_Canceled` (`#1A6FA8`) and `Canceled` (`#E8622A`)
- Stacked: `stackId="a"`
- X axis: month/year labels rotated 45°
- Tooltip showing both values and total

### Chart 2 — Channel distribution (Recharts PieChart donut)

- Group by `market_segment_type`
- Donut: `innerRadius={60} outerRadius={90}`
- Colors: `["#1A6FA8", "#E8622A", "#1B8FA8", "#64748B", "#2563EB"]`
- Legend below with name and percentage
- Tooltip with count and percentage

### Chart 3 — Bookings by room type (horizontal BarChart)

- Group by `room_type_reserved`
- Horizontal bars sorted largest to smallest
- Single color: `#1A6FA8`
- Labels with count at the end of each bar

### Loading state

While `loading === true`, show shadcn `Skeleton` components in place of each card and chart.

─────────────────────────────────────────────────────────────────────────────

## Validation before advancing to 03_prompt

- [ ] All 4 KPI cards show correct numeric values (verify against the CSV)
- [ ] The monthly bar chart shows all time periods in the dataset
- [ ] The donut chart shows all channels with percentages summing to 100%
- [ ] Horizontal bars are sorted largest to smallest
- [ ] Loading state shows skeletons while data loads
- [ ] Design looks correct with STAYSelect brand colors
