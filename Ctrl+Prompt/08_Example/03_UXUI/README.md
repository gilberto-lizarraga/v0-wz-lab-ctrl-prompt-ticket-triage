# 03_UXUI — Design System

This folder contains the visual design references that guide the style of the prototype.

## Contents

- **design-system.md** — Full design system: color palette with hex tokens, typography scale, shadcn/ui component map per screen, Recharts color series, weather widget spec, and layout grid

## Quick Reference for v0

**Colors:**
- Primary: `#1A6FA8` (STAYSelect blue)
- Accent: `#E8622A` (logo orange/coral)
- Background: `#F8F9FA` (very light gray)
- Text: `#0F172A`

**General style:**
- Clean enterprise dashboard — inspiration: Vercel dashboard, Linear, Stripe
- Cards with subtle shadow, rounded borders
- Modern sans-serif typography (Inter)
- Brand-colored charts

**Component library:** shadcn/ui — natively compatible with v0, no extra setup needed

## Notes
- Always use hex codes, never color names — v0 has its own color defaults and will override if not explicitly set
- See design-system.md for the full component map per screen
