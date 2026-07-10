# UX/UI Design System — STAYSelect Operations Dashboard
**Version:** 1.0  
**Component stack:** shadcn/ui + Tailwind CSS  
**Built for:** v0 by Vercel

---

## 1. Design Principles

| Principle | Description |
|---|---|
| **Clarity first** | The most important data is always the most visible. No unnecessary decoration. |
| **Enterprise but human** | Clean and professional, not cold or robotic. The operations team uses this every day. |
| **Action at a glance** | The manager should be able to read the hotel's status in under 5 seconds. |
| **Own brand** | STAYSelect should look like theirs — not a generic third-party dashboard. |

---

## 2. Color Palette

### STAYSelect brand colors

```
Primary Blue:     #1A6FA8   → Main elements, buttons, links, active nav
Teal Blue:        #1B8FA8   → Hover states, active card borders
Coral Orange:     #E8622A   → Accents, alert badges, secondary CTAs
```

### System colors (Tailwind / shadcn tokens)

```
Background:       #F8F9FA   → bg-gray-50      → App general background
Surface:          #FFFFFF   → bg-white         → Cards, panels, modals
Border:           #E2E8F0   → border-slate-200 → Card and table borders
Text Primary:     #0F172A   → text-slate-900   → Titles and primary data
Text Secondary:   #64748B   → text-slate-500   → Labels, metadata, placeholders
```

### Semantic colors

```
Success (Not_Canceled):   #16A34A   → green-600   → Green chip
Danger  (Canceled):       #DC2626   → red-600     → Red chip
Info    (Online):         #2563EB   → blue-600    → Channel badge
Neutral (Offline):        #6B7280   → gray-500    → Channel badge
Warning (Corporate):      #D97706   → amber-600   → Channel badge
```

---

## 3. Typography

```
Font family:    Inter (via Google Fonts or system)
Fallback:       ui-sans-serif, system-ui, sans-serif

Scale:
- Display:      text-2xl  (24px)  font-bold     → Large KPI numbers
- H1:           text-xl   (20px)  font-semibold → Section titles
- H2:           text-lg   (18px)  font-semibold → Card subtitles
- Body:         text-sm   (14px)  font-normal   → Table and content text
- Label:        text-xs   (12px)  font-medium   → Labels, badges, captions
```

---

## 4. shadcn/ui Components — Usage Map

### Layout and navigation

| shadcn component | Where it's used |
|---|---|
| `Sidebar` or `NavigationMenu` | Side or top nav: Dashboard / Reservations |
| `Select` | Hotel selector (Sunset Hotel ▼) in the header |
| `Separator` | Dividers between sections |

### Weather Widget — Header (right)

```
┌──────────────────────────────────────────────────────────┐
│ 🏠 STAYSelect     [Sunset Hotel ▼]       ⛅ 31°C Cancún │
└──────────────────────────────────────────────────────────┘
```

| Element | Detail |
|---|---|
| Weather icon | `lucide-react` mapped from WMO weathercode |
| Temperature | `{temperature_2m}°C` in `text-sm font-medium` |
| City | `"Cancún, MX"` in `text-xs text-slate-500` |
| Container | `flex items-center gap-1.5` — no card, inline in header |
| Loading | shadcn `Skeleton` — `w-20 h-4` while loading |
| Error | Silent — if the API fails, the widget simply does not appear |

**lucide-react icons by weathercode:**
```
0        → Sun
1, 2, 3  → CloudSun
45, 48   → CloudFog
51–67    → CloudDrizzle
71–77    → CloudSnow (unlikely in Cancún but handled robustly)
80–82    → CloudRain
95–99    → CloudLightning
```

### Dashboard — KPI Cards

| shadcn component | Where it's used |
|---|---|
| `Card`, `CardHeader`, `CardContent` | Container for each KPI (Total Bookings, etc.) |
| `Badge` | Variation indicator (↑ +12% vs previous month) |

```
Card anatomy:
┌─────────────────────────┐
│ CardHeader              │
│   Icon  Label (text-xs) │
├─────────────────────────┤
│ CardContent             │
│   Large value (text-2xl │
│   font-bold)            │
│   Subtext (text-xs      │
│   text-slate-500)       │
└─────────────────────────┘
```

### Charts

| Library | Component | Use |
|---|---|---|
| Recharts | `BarChart` + `Bar` | Bookings by month |
| Recharts | `PieChart` + `Pie` (donut) | Distribution by channel |
| Recharts | Horizontal `BarChart` | Reservations by room type |

Chart colors:
```
Not_Canceled:   #1A6FA8  (Primary Blue)
Canceled:       #E8622A  (Coral Orange)
Series 1:       #1A6FA8
Series 2:       #1B8FA8
Series 3:       #E8622A
Series 4:       #64748B
Series 5:       #2563EB
```

### Filters and search

| shadcn component | Where it's used |
|---|---|
| `Select` | Status, channel, room type filters |
| `Input` with `Search` icon | Search by Booking_ID |
| `DatePickerWithRange` | Date range filter |
| `Button` variant `outline` | "Clear filters" button |

### Reservations table

| shadcn component | Where it's used |
|---|---|
| `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell` | Main reservations table |
| `Badge` | Status (Not_Canceled / Canceled) and channel |
| `Button` variant `ghost` size `sm` | "View detail" button per row |
| `Pagination` | Table pagination |

Badge variants for status:
```
Not_Canceled  → variant="outline"  className="border-green-600 text-green-600"
Canceled      → variant="outline"  className="border-red-600 text-red-600"
```

Badge variants for channel:
```
Online        → className="bg-blue-100 text-blue-700"
Offline       → className="bg-gray-100 text-gray-600"
Corporate     → className="bg-amber-100 text-amber-700"
Aviation      → className="bg-purple-100 text-purple-700"
Complementary → className="bg-teal-100 text-teal-700"
```

### Detail view

| shadcn component | Where it's used |
|---|---|
| `Card` | Container for data groups |
| `Separator` | Divider between sections |
| `Button` variant `ghost` | "← Back to Reservations" button |
| `Badge` | Reservation status in the header |

---

## 5. General Layout

### Page structure

```
┌──────────────────────────────────────────────────────┐  h-16
│  HEADER                                              │
│  [🏠 STAYSelect logo]        [Sunset Hotel ▼]        │
├──────────────────────────────────────────────────────┤
│  NAV (top tabs or sidebar)                           │
│  [Dashboard]  [Reservations]                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  CONTENT AREA                                        │  flex-1
│  max-w-7xl  mx-auto  px-6  py-6                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Dashboard grid

```
Row 1: KPI Cards
grid grid-cols-4 gap-4

Row 2: Main charts
grid grid-cols-3 gap-4
└── col-span-2: Bookings by month (bar chart)
└── col-span-1: Distribution by channel (donut)

Row 3: Secondary chart
grid grid-cols-1
└── Reservations by room type (horizontal bars)
```

---

## 6. Micro-interactions and UX Details

- **Table row hover:** `hover:bg-slate-50` — subtle feedback on cursor over
- **Row click:** cursor pointer, navigates without a visible button (entire row is clickable)
- **Loading state:** Skeleton cards while CSV data loads
- **Empty state:** If filters return no results: illustration + "No reservations found matching these filters"
- **Active filters:** Counter badge above the table "3 active filters" with X button to clear
- **KPI number:** Count-up animation on load — visual impact in the demo

---

## 7. Instructions for v0

When generating the prototype with this design system, use these instructions:

```
- Use shadcn/ui for all UI components
- Use Recharts for all charts
- Apply the STAYSelect palette (primary: #1A6FA8, accent: #E8622A)
- Font: Inter
- General background: bg-gray-50, cards: bg-white with shadow-sm
- Logo can be styled text: "STAY" in font-bold text-[#1A6FA8] + "Select" in font-normal
- All navigation must be client-side, no full page reloads
- CSV is parsed on app load with PapaParse
```

---

*Document prepared as part of the "Prototype with v0 — From 0 to Hero!" program | Wizeline — Product Discipline*
