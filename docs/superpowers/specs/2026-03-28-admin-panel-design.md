# Admin Panel — Design Spec

**Date:** 2026-03-28
**Status:** Approved

## Overview

Internal admin panel at `/admin` for managing users, viewing searches, tracking revenue, and monitoring system stats. Single page, server-rendered, protected by hardcoded admin email check.

## Access Control

- Route: `GET /admin`
- Auth: requires authenticated user AND email matches `ADMIN_EMAIL` env var
- Returns 403 for non-admin users, redirects to `/` for unauthenticated
- Config: `ADMIN_EMAIL` in `app/config.py` (from env var)

## Page Sections

### 1. System Stats (top)
Cards showing:
- Total users (excluding soft-deleted)
- Total searches
- Total credits sold (sum of positive credit transactions)
- Total revenue (derived from credit pack prices)

All computed server-side via SQL COUNT/SUM queries.

### 2. Users Table
Columns: email, credits remaining, signup date, last login, search count, status (active/deleted).
Actions per row:
- Adjust credits: +/- input with submit button (POST `/admin/api/adjust-credits`)
- Delete user: button with confirm (POST `/admin/api/delete-user`)

Paginated, 50 per page, newest first.

### 3. Recent Searches
Columns: user email, keyword, location, result count, credits used, date.
Read-only. Paginated, 50 per page, newest first.

### 4. Revenue
Credit purchase transactions only (type='purchase'). Columns: user email, amount, stripe payment ID, date.
Summary at top: total revenue, total credits sold.
Paginated, 50 per page, newest first.

## Implementation

- **Router:** `app/routers/admin.py` — page route + 2 action endpoints
- **Template:** `app/templates/admin.html` — extends `base.html`, uses `pages.css`
- **Queries:** `app/database/queries.py` — admin-specific queries
- **Config:** `ADMIN_EMAIL` env var in `app/config.py`
- **No new JS** — server-side rendered, forms use standard POST
- **i18n:** Not needed (internal tool, English only)
