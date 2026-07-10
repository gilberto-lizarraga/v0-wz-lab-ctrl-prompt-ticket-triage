# 04_Prompt — Reservation Detail

## Context
The Dashboard and the Reservations screen are complete. The table navigates to `/reservations/[id]` when a row is clicked. That page is still a placeholder.

## Objective
Build the individual reservation detail view showing all CSV fields in a two-column layout, with navigation back to the table.

## Files to attach in v0
- `00_Inputs/02_BRD_PRD_Specs/PRD.md`

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

Build the **Reservation Detail** page (`app/reservations/[id]/page.tsx`) replacing the placeholder.

### Data logic

- The `id` from the URL corresponds to the `Booking_ID` in the CSV
- Find the reservation: `reservations.find(r => r.Booking_ID === id)`
- If not found: show an error state with message "Reservation not found" and a button to go back

### Page header

```
← Back to Reservations          [Booking_ID]  ● Not_Canceled / ● Canceled
```

- "← Back" button with `variant="ghost"` — returns to `/reservations` (use `router.back()` to preserve filters)
- `Booking_ID` in `text-xl font-bold`
- Status badge: green for Not_Canceled, red for Canceled

### Data layout — two columns

Two shadcn `Card` components side by side (`grid grid-cols-2 gap-6`):

**Left card — Stay information**

| Label | Field | Format |
|---|---|---|
| Arrival date | `arrival_date/month/year` | "October 2, 2017" |
| Weeknights | `no_of_week_nights` | "X nights" |
| Weekend nights | `no_of_weekend_nights` | "X nights" |
| Total nights | sum of both | "X nights" |
| Room type | `room_type_reserved` | "Type 1" |
| Meal plan | `type_of_meal_plan` | Direct CSV value |
| Parking | `required_car_parking_space` | "Yes" / "No" |

**Right card — Guest and booking information**

| Label | Field | Format |
|---|---|---|
| Adults | `no_of_adults` | Number |
| Children | `no_of_children` | Number (hide if 0) |
| Booking channel | `market_segment_type` | Colored badge |
| Lead time | `lead_time` | "X days in advance" |
| Returning guest | `repeated_guest` | Special gold badge if 1: "⭐ Frequent Guest" |
| Special requests | `no_of_special_requests` | "X requests" (hide if 0) |
| Price per night | `avg_price_per_room` | "$XXX.XX" in `text-lg font-semibold` |

### Guest history (separate section below)

Only show if `no_of_previous_cancellations > 0` or `no_of_previous_bookings_not_canceled > 0`:

A full-width `Card` with:
- Previous cancellations: `no_of_previous_cancellations`
- Previous completed bookings: `no_of_previous_bookings_not_canceled`

─────────────────────────────────────────────────────────────────────────────

## Validation before advancing to 05_prompt

- [ ] The page loads the correct detail for any Booking_ID
- [ ] The "← Back" button returns to the table with filters intact
- [ ] The status badge has the correct color
- [ ] The "Frequent Guest" badge appears only when `repeated_guest === 1`
- [ ] The history section hides when both values are 0
- [ ] The error state shows if the Booking_ID doesn't exist
