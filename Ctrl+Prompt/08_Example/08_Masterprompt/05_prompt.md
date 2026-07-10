# 05_Prompt — Weather Widget (Open-Meteo API)

## Context
The app is complete with all 3 functional screens. The header has a `<div id="weather-widget" />` placeholder on the right side, next to the hotel selector. It's time to replace it with the real widget.

## Objective
Build the WeatherWidget that consumes the Open-Meteo API in real time and displays the current weather for Cancún, Quintana Roo in the app header.

## Files to attach in v0
- `00_Inputs/05_APIs/README.md`

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

Replace the `<div id="weather-widget" />` placeholder in the header with the **WeatherWidget** component that consumes real weather data.

### Endpoint to use

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude=21.1619
  &longitude=-86.8515
  &current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m
  &timezone=America%2FCancun
  &forecast_days=1
```

### Component logic

```typescript
// On component mount, fetch the endpoint
// Extract from response: temperature_2m, weathercode
// Map weathercode to lucide-react icon (see table below)
// Display: [Icon] [temperature]°C  Cancún, MX
```

### Weathercode to lucide-react icon mapping

| Codes | Icon |
|---|---|
| 0 | `Sun` |
| 1, 2, 3 | `CloudSun` |
| 45, 48 | `CloudFog` |
| 51, 53, 55, 61, 63, 65, 66, 67 | `CloudDrizzle` |
| 71, 73, 75, 77 | `CloudSnow` |
| 80, 81, 82 | `CloudRain` |
| 95, 96, 99 | `CloudLightning` |

### Widget visual in the header

```
[Icon 16px]  31°C
             Cancún, MX
```

- No card or border — inline in the header, no visible container
- Temperature: `text-sm font-medium text-slate-700`
- City: `text-xs text-slate-400`
- Icon: `size-4 text-slate-600`
- Container: `flex items-center gap-2`

### Widget states

- **Loading:** Shadcn `Skeleton` — `w-16 h-4` — while fetching
- **Error / timeout:** Widget disappears silently — **the app must not break if the API fails**
- **Success:** Shows icon + temperature + city

### Important

- Fetch happens only once on component mount (no polling)
- 5-second timeout — if no response, activate the silent error state
- Do not show spinners or error messages to the user

─────────────────────────────────────────────────────────────────────────────

## Validation — Complete prototype ✓

- [ ] Widget shows current Cancún weather with real temperature
- [ ] Icon matches the current weather conditions
- [ ] Loading state shows a skeleton while fetching
- [ ] If the API fails, the header looks normal without the widget (no visible errors)
- [ ] Widget does not break the header layout in any case

### Final checklist — complete prototype

- [ ] Dashboard: 4 KPIs + 3 charts with real CSV data
- [ ] Reservations: filterable and paginated table
- [ ] Detail: all fields, frequent guest badge, conditional history
- [ ] Weather widget: real Cancún weather in the header
- [ ] STAYSelect branding consistent across all 3 screens
- [ ] Smooth navigation without full page reloads
- [ ] App loads in under 3 seconds

**🎉 Prototype ready for the demo.**
