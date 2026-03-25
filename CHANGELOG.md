# Changelog

## v0.1.0 — 2026-03-25

### Added
- Task 1: Project scaffolding — FastAPI app structure
  - `app/` package with `main.py`, `config.py`, and empty `__init__.py` files for `routers`, `services`, `database`, `models`
  - `app/static/{css,js,i18n}/` and `app/templates/partials/` directories
  - `tests/` package with `fixtures/` directory
  - `requirements.txt` with all pinned dependencies (FastAPI, asyncpg, slowapi, Stripe, etc.)
  - `config.py` — all settings loaded from environment variables, no defaults for secrets
  - `main.py` — FastAPI app with slowapi rate limiting, CORS, static files, and `/health` endpoint
