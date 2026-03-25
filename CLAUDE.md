# CLAUDE.md — MapSearch.app

## What This Is

MapSearch.app — a SaaS web app for searching Google Maps business data at scale. Users search by keyword + location, set filters, pay credits per filtered result, and get data as a live table + CSV export.

**Tagline:** "Search any area. Get every business."
**Domain:** mapsearch.app
**Positioning:** 2x cheaper than Outscraper, 10x prettier, 10x simpler, multilingual.

## Python Version

**Always use `python3`, never `python`.**

## Key Documents

| Document | Purpose |
|----------|---------|
| `plans/2026-03-24-MAPSEARCH-SAAS.md` | Master plan (product vision, pricing, positioning) |
| `plans/2026-03-24-mapsearch-mvp.md` | Implementation plan (22 tasks, reviewed 3x) |
| `docs/2026-03-24-mapsearch-*.md` | Competitor research |
| `design/` | CSS design system, HTML prototypes, i18n files |

## Tech Stack

- **Backend:** FastAPI (Python 3), asyncpg (PostgreSQL)
- **Frontend:** Vanilla JS, Leaflet.js, Jinja2 templates
- **Data source:** DataForSEO Google Maps Live API
- **Payments:** Stripe Checkout (one-time credit packs)
- **Auth:** Google OAuth2 + email/password, JWT in httpOnly cookies
- **Map:** Leaflet.js + OpenStreetMap (CartoDB Dark Matter tiles)
- **i18n:** EN/FR/ES/DE, JSON translation files, browser auto-detect
- **Deploy:** VPS (82.21.4.94) behind Caddy

## Architecture Notes

- **Standalone app** — NOT a subproject of leadgen monorepo. Clean break.
- **Async DataForSEO client** — new async client using httpx, NOT the shared sync scraper from leadgen. Reference: webevolve has an async client pattern.
- **Cache architecture:** `scrape_cache` (raw DataForSEO data, shared across users) + `searches` (per-user with filters). Filters applied post-cache.
- **Credit model:** 1 credit = 1 filtered result. Filters save users money.

## Pricing

| Pack | Credits | Price | Per 1,000 |
|------|---------|-------|-----------|
| Free (signup) | 99 | $0 | — |
| Starter | 1,000 | $1.50 | $1.50 |
| Growth | 5,000 | $7 | $1.40 |
| Pro | 25,000 | $32 | $1.28 |
| Agency | 100,000 | $120 | $1.20 |

Outscraper charges $3/1,000. We're 2x cheaper at every tier.

## Related Repos

- `leadgen` — Origin repo. Contains original exploration plans and shared scraper patterns for reference.
