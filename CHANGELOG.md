# Changelog

## v0.3.0 — 2026-03-25

### Added
- Frontend: state.js pub/sub event bus
- Base template (Jinja2) + app.html ported from design prototype
- Theme toggle (light/dark/system) with localStorage persistence
- Pages router (GET /)
- App-specific CSS extracted from prototype
- Auth modal (signup/login with Google OAuth + email/password)
- Leaflet map module (CartoDB tiles, pins, popup, table interaction)
- Filter controls (tri-toggles, range sliders, search area, near me, category)
- Results table (sortable columns, pagination, column toggle, map sync)
- i18n module (EN/FR/DE/ES, browser detect, language selector)
- app.js search flow (auth gate → API → results → table + map)
- Toast notification system

## v0.2.0 — 2026-03-25

### Added
- Project scaffolding (FastAPI app, config, directory structure)
- Database schema (users, scrape_cache, searches, search_results, credit_transactions, exports)
- Async connection pool (asyncpg)
- Design assets copied to app/static/ (CSS + i18n)
- Email/password auth (signup, login, logout, me endpoints)
- JWT sessions in httpOnly cookies with bcrypt password hashing
- Rate limiting (5 signups/min, 10 logins/min)
- DataForSEO location resolver (country → location_code mapping)
- `require_current_user` FastAPI dependency for protected endpoints
- Google OAuth2 (signup/login via Google, state param CSRF protection)
- Nominatim geocoder service (location → lat/lng + country_code)
- Credit service (deduct, add, balance with transaction logging)
- Async DataForSEO Google Maps Live API client
- Search service (cache check → geocode → API → filter → credit deduction)
- POST /api/search endpoint with rate limiting (10/min)

## v0.1.0 — 2026-03-24

### Added
- Initial commit — design system, plans, competitor research
