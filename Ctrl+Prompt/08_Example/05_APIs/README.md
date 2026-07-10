# 05_APIs

---

## API in use — Open-Meteo (Weather Widget)

The prototype consumes a **real weather API** to display current conditions at the location of Sunset Hotel.

### Open-Meteo
- **Base URL:** `https://api.open-meteo.com/v1/forecast`
- **Docs:** https://open-meteo.com/en/docs
- **Cost:** Free, no API key, no registration required
- **Format:** JSON
- **CORS:** Enabled — works directly from the browser

### Widget endpoint

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude=21.1619
  &longitude=-86.8515
  &current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m
  &timezone=America%2FCancun
  &forecast_days=1
```

**Coordinates:** Cancún, Quintana Roo, México
`latitude: 21.1619 | longitude: -86.8515`

### Relevant response

```json
{
  "current": {
    "temperature_2m": 31.2,        // °C — current temperature
    "weathercode": 1,               // WMO code — sky condition
    "windspeed_10m": 18.4,          // km/h — wind speed
    "relative_humidity_2m": 72      // % — relative humidity
  }
}
```

### WMO Weather Codes (most relevant for Cancún)

| Code | Condition | Suggested icon |
|---|---|---|
| 0 | Clear sky | ☀️ `Sun` |
| 1–3 | Partly cloudy | ⛅ `CloudSun` |
| 45–48 | Fog | 🌫️ `CloudFog` |
| 51–67 | Drizzle / rain | 🌧️ `CloudRain` |
| 80–82 | Showers | 🌦️ `CloudDrizzle` |
| 95–99 | Thunderstorm | ⛈️ `CloudLightning` |

Use icons from `lucide-react` for consistency with shadcn/ui.

---

## Implementation in the prototype

```typescript
// Fetch on header component mount — one call, no polling
const res = await fetch(
  'https://api.open-meteo.com/v1/forecast?latitude=21.1619&longitude=-86.8515&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m&timezone=America%2FCancun&forecast_days=1'
)
const data = await res.json()
const { temperature_2m, weathercode } = data.current
```

**Error handling:** 5-second timeout with silent fallback — widget disappears cleanly, app never breaks.

---

## Demo talking point

> "The prototype is also consuming a real weather API right now — see the widget showing current conditions in Cancún. This is an example of the architecture already being open to external integrations from day one."

---

## Future APIs (out of scope for the prototype)

If STAYSelect moves forward with Wizeline, the relevant proprietary endpoints would be:
- `GET /reservations` — paginated reservation list
- `GET /reservations/:id` — individual reservation detail
- `GET /dashboard/kpis` — aggregated metrics
- `GET /dashboard/trends` — chart data by time period
