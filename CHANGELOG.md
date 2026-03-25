# Changelog

## [0.2.0] - 2026-03-25

### Added
- Database schema (`app/database/schema.sql`): tables for users, scrape_cache, searches, search_results, credit_transactions, exports with appropriate indexes and generated columns
- Async database connection pool (`app/database/connection.py`): asyncpg-based pool with `execute`, `fetchrow`, and `fetch` helpers

## [0.1.0] - 2026-03-24

### Added
- Initial commit: design system, plans, competitor research
