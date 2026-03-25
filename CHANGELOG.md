# Changelog

## 0.2.0 (2026-03-25)

### Added
- Email/password auth system: signup, login, logout, me endpoints
- JWT sessions in httpOnly cookies (HS256, 7-day expiry)
- bcrypt password hashing via passlib
- Rate limiting: 5 signups/min, 10 logins/min per IP (slowapi)
- Pydantic request models for signup/login
- Database queries module (asyncpg parameterized queries)
- 10 auth tests with mocked DB layer

## 0.1.0 (2026-03-24)

### Added
- Initial project scaffolding, design system, plans, competitor research
