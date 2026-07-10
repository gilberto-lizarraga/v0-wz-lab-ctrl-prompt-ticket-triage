# 00_Masterprompt — Project Rector Prompt

## Files to attach in v0 before sending this prompt

- `00_Inputs/01_Context/stayselect-context.md`
- `00_Inputs/03_UXUI/design-system.md`

---

## Prompt

─────────────────────────────────────────────────────────────────────────────

We're going to build together a web application prototype called **STAYSelect Operations Dashboard**.

Before writing a single line of code, I need you to carefully read the two files I'm attaching:
- `stayselect-context.md` — the business context: who the client is, what their problem is, and what we want to demonstrate to them
- `design-system.md` — the design system: color palette, typography, shadcn/ui components and visual rules

This is the project we will build step by step in separate prompts. This first prompt establishes the ground rules — I'm not asking you to generate any code yet.

---

### Project stack (do not change)

- **Framework:** Next.js with App Router
- **Components:** shadcn/ui exclusively — do not use other component libraries
- **Styles:** Tailwind CSS following the tokens from design-system.md
- **Charts:** Recharts
- **Icons:** lucide-react
- **Data parsing:** PapaParse with `dynamicTyping: true`
- **Deploy target:** Vercel

---

### Visual identity (apply throughout the entire app without exception)

- **Primary color:** `#1A6FA8` — buttons, active nav, main elements
- **Accent color:** `#E8622A` — alert badges, accents, secondary CTAs
- **Background:** `bg-gray-50` (page) and `bg-white` (cards)
- **Typography:** Inter — import from Google Fonts
- **Logo:** styled text — `STAY` in `font-bold text-[#1A6FA8]` + `Select` in `font-normal text-[#1A6FA8]`
- **Active hotel:** "Sunset Hotel" — always visible in the header

The design should look **enterprise but human** — clean, professional, with STAYSelect's colors on every screen. I don't want a generic dashboard — I want the client to see themselves in the product from the very first glance.

---

### Collaboration rules for this project

1. **If you have any doubts about a design decision, functionality, or data — ask before executing.** Don't assume, don't invent. I'd rather answer a question than fix 3 screens.

2. **Follow design-system.md to the letter.** If something isn't in the design system, let me know before making a visual decision on your own.

3. **Each prompt you receive is autonomous** — it will explain what already exists, what you must build, and what additional files you'll receive as context. Always read the full context before generating.

4. **Do not build functionality I haven't asked for.** If you see an improvement opportunity, mention it — but don't implement it without confirmation.

5. **Maintain visual consistency across screens.** The header, navigation, and colors must be identical on Dashboard, Reservations, and Reservation Detail.

---

### Prototype overview (so you have the complete map)

The dashboard has 3 screens:

1. **Dashboard** — KPI cards + charts for reservations, channels, and room types
2. **Reservations** — paginated table with filters by status, channel, and room type
3. **Reservation Detail** — full view of an individual booking

Data comes from a CSV (`Hotel Reservations.csv`) loaded with PapaParse when the app starts. All data corresponds to **Sunset Hotel, Cancún, México**.

The global header will include a real-time Cancún weather widget (Open-Meteo API) — we'll build that in a dedicated prompt.

---

### What I need from you now

Confirm that:
1. You read and understood the STAYSelect context and the design system
2. You're clear on the stack and collaboration rules
3. You have any questions or clarifications before we start building

If everything is clear, respond with a 5-point summary of what you're going to build and how you'll approach it — so I can validate we're aligned before the first code prompt.

─────────────────────────────────────────────────────────────────────────────

---

## Validation before advancing to 01_prompt

- [ ] v0 confirms it read the STAYSelect context
- [ ] v0 confirms the stack (Next.js, shadcn, Recharts, PapaParse)
- [ ] v0 confirms the exact colors (#1A6FA8, #E8622A)
- [ ] v0 has no blocking questions, or you resolved them
- [ ] v0's summary correctly reflects the 3 screens and the CSV data flow

**Only advance to `01_prompt.md` when this checklist is complete.**
