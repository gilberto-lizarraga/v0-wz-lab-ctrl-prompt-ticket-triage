# 01_Prompt — Foundation: Base Layout + DataProvider

## Context
The masterprompt was sent and v0 confirmed the stack, branding, and rules. The project is ready to receive code.

## Objective
Build the app skeleton: global layout with header, navigation, hotel selector, and the DataProvider that loads the CSV with PapaParse and exposes it to the entire app via Context.

## Files to attach in v0
- `00_Inputs/04_Data_Sources/Hotel Reservations.csv`
- `00_Inputs/02_BRD_PRD_Specs/PRD.md`

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

Let's start. This first prompt builds the **app foundation** — the global layout and data loading. Don't build the content of any screen yet, only the base structure.

### 1. DataProvider — CSV Loading

Create a `DataProvider` (React Context) that:
- Loads `Hotel Reservations.csv` when the app mounts using PapaParse with `dynamicTyping: true`
- Exposes the reservations array as `reservations` to the entire app
- Exposes a `loading` state (boolean) while parsing
- The CSV is located at `public/Hotel Reservations.csv`

CSV fields we'll use (reference for TypeScript typing):
```
Booking_ID, no_of_adults, no_of_children, no_of_weekend_nights, no_of_week_nights,
type_of_meal_plan, required_car_parking_space, room_type_reserved, lead_time,
arrival_year, arrival_month, arrival_date, market_segment_type, repeated_guest,
no_of_previous_cancellations, no_of_previous_bookings_not_canceled,
avg_price_per_room, no_of_special_requests, booking_status
```

### 2. Global layout — app/layout.tsx

Fixed header with:
- **Left:** STAYSelect logo (text: `STAY` bold + `Select` normal, color `#1A6FA8`)
- **Center:** Navigation — two tabs: `Dashboard` and `Reservations`
- **Right:** Hotel selector — shadcn `Select` with "Sunset Hotel" selected (UI only, not functional yet) + reserved space for the weather widget (a placeholder `<div id="weather-widget" />` for now)

Header styles:
- `bg-white border-b border-slate-200 h-16`
- `max-w-7xl mx-auto px-6` for internal content
- Active tab uses color `#1A6FA8` with `border-b-2`

### 3. Placeholder pages

Create pages with placeholder content (just a centered title):
- `app/page.tsx` → "Dashboard — coming next"
- `app/reservations/page.tsx` → "Reservations — coming next"
- `app/reservations/[id]/page.tsx` → "Detail — coming next"

The `DataProvider` must wrap the entire app from `layout.tsx`.

---

Do not build screen content yet. Only the layout, navigation, and data loading.

─────────────────────────────────────────────────────────────────────────────

## Validation before advancing to 02_prompt

- [ ] Header renders correctly with logo, nav, and hotel selector
- [ ] Navigation switches between Dashboard and Reservations without full page reload
- [ ] CSV loads without errors (verify in console that `reservations.length > 0`)
- [ ] Numeric CSV fields are numbers, not strings (verify `avg_price_per_room`)
- [ ] Layout looks correct at 1440px
