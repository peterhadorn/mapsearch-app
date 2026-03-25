# Changelog

## v0.3.0 — 2026-03-25

### Added
- Frontend: state.js pub/sub event bus

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
