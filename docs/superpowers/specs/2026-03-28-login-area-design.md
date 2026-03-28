# Login Area — Design Spec

**Date:** 2026-03-28
**Status:** Approved (rev 2 — addressing code review findings)

## Overview

Add authenticated user navigation and account management pages to MapSearch.app. Auth stays as modal (signup/login). Post-login, users get a nav dropdown and three Jinja2 server-rendered pages: Account, Billing & Credits, Search History. Password reset via SMTP email.

## 1. Logged-in Nav

When authenticated, the header "Sign In" button is replaced by a user dropdown menu:
- Account
- Billing & Credits
- Search History
- Sign Out

Dropdown trigger: user's email (truncated) or a user icon. Works on both desktop and mobile (hamburger menu).

## 2. Account Page (`/account`)

Jinja2 server-rendered, extends `base.html`. Requires authentication.

**Sections:**
- **Email display** — read-only, shows current email
- **Change password** — current password + new password + confirm new password form
- **Delete account** — soft delete with confirmation modal. Marks account inactive, keeps data 30 days, then purges. Shows warning about data loss.

**Backend:**
- `PUT /api/auth/password` — change password (requires current password)
- `POST /api/auth/delete-account` — soft delete (sets `deleted_at` timestamp), **clears JWT cookie immediately**, returns 200 with redirect to `/`
- Database: add `deleted_at` column to `users` table
- **All auth queries must check `deleted_at IS NULL`:** `get_user_by_email`, `get_user_by_id`, and `require_current_user` dependency must reject soft-deleted users. A soft-deleted user cannot log in, and existing sessions are invalidated by the cookie clear + query guard.
- Cron/scheduled task (or on-login check): purge users where `deleted_at < NOW() - INTERVAL '30 days'` — cascading delete of searches, transactions, exports

## 3. Billing & Credits Page (`/billing`)

Jinja2 server-rendered, extends `base.html`. Requires authentication.

**Sections:**
- **Current balance** — credit count, prominently displayed
- **Transaction history** — table with columns: date, type (purchase/deduction), amount, description (pack name or search keyword+location), balance after. Paginated, newest first.
- **Buy credits** — 5 credit pack cards (Free excluded) with Stripe checkout buttons. Same design as pricing section.

**Backend:**
- `GET /api/credits/transactions` — paginated transaction history
- Existing `GET /api/credits/balance` and `POST /api/credits/checkout` endpoints reused

## 4. Search History Page (`/history`)

Jinja2 server-rendered, extends `base.html`. Requires authentication.

### Data model fix: filtered result snapshots

The current schema stores raw results in `search_results` (keyed by `scrape_cache_id`) and search metadata in `searches` (with `filters_applied` JSON). Multiple searches can share the same cache with different filters, so we cannot reliably reconstruct the exact filtered set from raw cache data alone.

**Solution: `search_result_ids` junction table.**

```sql
CREATE TABLE search_result_ids (
    search_id UUID REFERENCES searches(id) ON DELETE CASCADE,
    search_result_id UUID REFERENCES search_results(id) ON DELETE CASCADE,
    PRIMARY KEY (search_id, search_result_id)
);
```

At search time, after filtering, the search service stores the IDs of the filtered results in this table. This is the exact set the user saw and paid credits for.

**Sections:**
- **Search list** — table/cards with: keyword, location, date, result count, credits used. Paginated, newest first.
- **View results** — click a search → navigates to `/history/{search_id}` showing the **exact filtered results** (joined via `search_result_ids`) in table + map
- **Re-run button** — on the results view, button to re-run the same keyword+location search with fresh DataForSEO data

**Backend:**
- `GET /api/searches` — paginated search history for current user (joins `searches` → `scrape_cache` for keyword/location)
- `GET /api/searches/{search_id}` — returns results via `search_result_ids` join (not raw cache data)
- Search service modification: after filtering, `INSERT INTO search_result_ids` the IDs of matching results
- Results view page reuses `map.js` and `table.js` modules

### Re-run: cache bypass flag

Add `force_refresh: bool = False` to `SearchRequest` model. When true, the search service skips cache lookup and calls DataForSEO directly. The re-run button on `/history/{search_id}` sends a search request with `force_refresh=true` + the original keyword/location/filters.

Modified files:
- `app/models/request_models.py` — add `force_refresh` field
- `app/services/search_service.py` — respect `force_refresh` flag in cache check logic

## 5. Password Reset Flow

SMTP-based email delivery.

**Flow:**
1. User clicks "Forgot password?" in login modal
2. Modal shows email input form
3. `POST /api/auth/forgot-password` — generates reset token (random, hashed in DB), sends email with reset link
4. Email contains link to `/reset-password?token=<token>`
5. `/reset-password` page: new password + confirm form
6. `POST /api/auth/reset-password` — validates token (1hr expiry), updates password, invalidates token

**Backend:**
- `POST /api/auth/forgot-password` — rate limited (3/min)
- `POST /api/auth/reset-password` — validates token + sets new password
- Database: `password_reset_tokens` table (user_id, token_hash, expires_at, used_at)
- SMTP config: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` env vars

**Security:**
- Token is random 32 bytes, URL-safe base64 encoded
- Only hash stored in DB (SHA-256 — fast enough for single-use tokens, no bcrypt needed)
- 1 hour expiry
- Single use (marked used after reset)
- Generic response on forgot-password (don't reveal if email exists)
- Rate limited

## Routing & Auth

**Protected pages** (require authentication, redirect to `/` with login modal if not logged in):
- `/account`
- `/billing`
- `/history`
- `/history/{search_id}`

**Public pages** (no auth required):
- `/reset-password` — must be accessible by unauthenticated users arriving from email link

## Template Architecture Fix: base.html script loading

Current `base.html` loads ALL JS modules (map, filters, table, auth, credits, app) on every page. These scripts bind to landing-page-specific DOM nodes on `DOMContentLoaded` and will throw on pages without those nodes.

**Solution: split base template scripts into blocks.**

`base.html` will load only shared/safe scripts (state, i18n, theme). Page-specific scripts move to `{% block scripts %}`:
- `app.html` → loads auth, map, filters, table, app, credits via `{% block scripts %}`
- Account pages → load only `account.js` via `{% block scripts %}`
- `history_detail.html` → loads map, table (reused) via `{% block scripts %}`

This is a **breaking change to base.html** — `app.html` must be updated simultaneously to add its own script block.

## New & Modified Files

**New files:**
- `app/routers/account.py` — page routes (`/account`, `/billing`, `/history`, `/history/{search_id}`)
- `app/templates/account.html`
- `app/templates/billing.html`
- `app/templates/history.html`
- `app/templates/history_detail.html`
- `app/templates/reset_password.html`
- `app/services/email_service.py` — SMTP email sending
- `app/static/js/account.js` — client-side logic for account pages (change password, delete account, buy credits)
- `app/static/css/pages.css` — shared styles for account pages

**Modified files:**
- `app/templates/base.html` — move page-specific scripts to `{% block scripts %}`, keep only shared scripts in base
- `app/templates/app.html` — add `{% block scripts %}` with all current JS modules, update nav for logged-in state, add forgot password link to modal
- `app/routers/auth.py` — add password change, delete account, forgot/reset password endpoints
- `app/database/schema.sql` — add `deleted_at` to users, add `password_reset_tokens` table, add `search_result_ids` table
- `app/database/queries.py` — new queries for history, transactions, tokens; add `deleted_at IS NULL` guard to all user lookups
- `app/services/search_service.py` — store filtered result IDs after search, respect `force_refresh` flag
- `app/models/request_models.py` — add `force_refresh` field to `SearchRequest`
- `app/config.py` — SMTP config vars
- `requirements.txt` — no new deps (stdlib `smtplib` + `email`)

## Design Consistency

All new pages follow existing design system:
- Extend `base.html` template (with page-specific script blocks)
- Use CSS variables from `design-system.css`
- Dark/light theme support via existing `theme.js`
- i18n support — add translation keys to all 4 language files
- Mobile responsive using existing breakpoints from `layout.css`
