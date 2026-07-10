# 03_Prompt — Reservations: Table + Filters + Pagination

## Context
The Dashboard is complete with KPI cards and the 3 charts. The DataProvider works correctly. Navigation between Dashboard and Reservations already exists in the header.

## Objective
Build the complete Reservations screen: filter bar, paginated table with status and channel badges, and navigation to the detail view of each reservation.

## Files to attach in v0
- `00_Inputs/06_Features/features-prototipo.md`
- `00_Inputs/02_BRD_PRD_Specs/PRD.md`

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

Build the **Reservations** screen (`app/reservations/page.tsx`) replacing the placeholder. Use data from `useData()`.

### Filter bar

Four controls in a row using shadcn components:

| Control | Type | Options |
|---|---|---|
| Status | `Select` | All / Not_Canceled / Canceled |
| Channel | `Select` | All + unique values from `market_segment_type` |
| Room type | `Select` | All + unique values from `room_type_reserved` |
| Search | `Input` with `Search` icon (lucide) | Searches by `Booking_ID` (case insensitive) |

- `outline` button "Clear filters" — visible only when at least one filter is active
- Results counter below the filters: `"Showing X of Y reservations"` in `text-sm text-slate-500`

### Reservations table

Use shadcn's `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell`.

Columns:

| Column | Field | Detail |
|---|---|---|
| Booking ID | `Booking_ID` | `font-mono text-sm` |
| Arrival | `arrival_date/month/year` | Format: "Oct 2, 2017" |
| Guests | `no_of_adults` + `no_of_children` | "2 adults" or "2 adults, 1 child" |
| Room | `room_type_reserved` | Clean: "Room_Type 1" → "Type 1" |
| Nights | `no_of_weekend_nights + no_of_week_nights` | "X nights" |
| Price/night | `avg_price_per_room` | "$XXX.XX" |
| Channel | `market_segment_type` | Colored badge (see design-system.md) |
| Status | `booking_status` | Badge: green Not_Canceled / red Canceled |

- `hover:bg-slate-50` on each row
- Entire row is clickable → navigates to `/reservations/[Booking_ID]`
- Cursor `pointer` on rows

### Pagination

- 20 reservations per page
- Shadcn `Pagination` component
- Show: previous / page numbers / next
- Pagination resets to page 1 when any filter changes

### Filtering logic

Filters are applied in this order and are cumulative:
1. Filter by `booking_status` if not "All"
2. Filter by `market_segment_type` if not "All"
3. Filter by `room_type_reserved` if not "All"
4. Filter by `Booking_ID` if there is text in the search box

─────────────────────────────────────────────────────────────────────────────

## Validation before advancing to 04_prompt

- [ ] Filters work individually and in combination
- [ ] Results counter updates when filtering
- [ ] "Clear filters" button appears only when filters are active and clears them all
- [ ] Pagination works and shows 20 records per page
- [ ] Status badges have the correct colors (green / red)
- [ ] Clicking any row navigates to `/reservations/[Booking_ID]`
- [ ] Pagination resets to page 1 when filters change
