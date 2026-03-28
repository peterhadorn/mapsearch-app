# Changelog

## v0.5.0 — 2026-03-28

### Added
- Admin panel (`/admin`) — user management, search stats, revenue tracking
- System stats: total users, searches, credits sold, estimated revenue
- User table: email, credits, search count, signup/login dates, adjust credits, delete
- Search history: all searches across users with keyword, location, results, credits
- Revenue: credit purchase transactions with Stripe payment IDs
- `ADMIN_EMAIL` env var for access control
- Self-delete prevention (admin cannot delete own account)

### Security
- Admin access via hardcoded email check (ADMIN_EMAIL env var)
- POST actions use `Depends(require_admin)` — raises 401/403, no redirect
- Soft delete for admin user deletion (consistent with existing architecture)

## v0.4.0 — 2026-03-28

### Added
- Logged-in user dropdown nav (Account, Billing, History, Sign Out)
- Account page (`/account`) — email display, change password, soft-delete account (30-day grace + auto-purge)
- Billing page (`/billing`) — credit balance, transaction history with pagination, buy credit packs
- Search history page (`/history`) — paginated list with keyword, location, results count
- History detail page (`/history/{id}`) — view exact filtered results on map + table, re-run with fresh API data
- Password reset flow — forgot password in modal, SMTP email with reset token (SHA-256, 1hr), reset page
- Credit transactions API endpoint with pagination (total, has_next)
- Search history API endpoints with pagination
- `search_result_ids` junction table — stores exact filtered result IDs per search
- `force_refresh` flag on search — bypass cache for fresh DataForSEO data
- i18n translations for all new pages (EN/FR/DE/ES)
- `APP_BASE_URL` config for canonical URLs in emails
- Startup purge of soft-deleted users older than 30 days
- Shared `pages.css` for account page styles

### Changed
- `base.html` now loads only shared scripts (state, i18n, theme); page-specific scripts via `{% block scripts %}`
- User queries now exclude soft-deleted accounts (`deleted_at IS NULL`)
- Export uses junction table for exact filtered results instead of raw cache
- Reset URLs use `APP_BASE_URL` config instead of Host header

### Security
- Password reset tokens: SHA-256 hashed, 1hr expiry, single-use
- Generic response on forgot-password (no email enumeration)
- Soft-deleted users cannot authenticate (query guard + cookie clear)
- Reset URLs from config, not Host header (prevents host-header poisoning)

## v0.3.1 — 2026-03-27

### Added
- Hamburger menu for mobile (nav links, language selector, theme toggle, sign in/logout)
- Logout button in desktop header and mobile menu
- Compact credits pill on mobile (number only, always visible)

### Fixed
- Credits pill hidden on mobile — now always visible across all viewports
- Pricing grid orphaned 5th card on tablet — changed to 3-col layout
- Mobile menu stacking context — moved outside header to avoid backdrop-filter z-index trap

### Changed
- Cache bust v6 → v8
- Theme toggle and Sign In button hidden on mobile (accessible via hamburger menu)

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
- Stripe credit purchase (checkout session, webhook, balance endpoint)
- Credits UI (purchase modal with 4 packs, Stripe redirect)
- CSV export (GET /api/export/{search_id} with ownership check)
- Deploy script (setup, app, db-setup, service-install, caddy-add, status, logs)
- Systemd service config (port 8200)
- Caddy reverse proxy for mapsearch.allwk.com
- .env.example with all required variables
- Dynamic host detection for Stripe URLs
- Deploy fixes: Caddy at /root/caddy/, Docker bridge IP 172.18.0.1, uvicorn bind 0.0.0.0

### Added (Page Sections)
- Hero viewport restructure (fixed → absolute for scrollable sections)
- Header nav: Features, Pricing, How it works links with smooth scroll
- Features section: 6 capability cards, 27 data field pills, 4 comparison cards
- Pricing section: 5 credit packs with auth-gated buy buttons
- How it works: 3-step flow (Search → Filter → Export)
- CTA section with signup button
- Footer

### Fixed
- Map overlay too dark — boosted colorful radial gradients, removed dark edge vignette
- Search card rainbow gradient more visible (thicker border, higher opacity, added rose)
- Filters panel open by default
- Map zoomed into Manhattan (zoom 14) instead of wide NYC view
- User location shown as pulsing emerald dot when geolocation allowed

### Removed
- Google OAuth2 (unnecessary for B2B data tool — email/password auth only)

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
