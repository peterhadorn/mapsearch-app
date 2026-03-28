# Admin Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an internal admin panel at `/admin` for managing users, viewing searches, tracking revenue, and monitoring system stats.

**Architecture:** Single server-rendered Jinja2 page with admin-only access (hardcoded email check). New router with page route + 2 action endpoints. All data fetched via SQL queries, no client-side API calls.

**Tech Stack:** FastAPI, asyncpg, Jinja2, existing CSS design system

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `app/config.py` | Modify | Add `ADMIN_EMAIL` env var |
| `app/database/queries.py` | Modify | Add admin queries (stats, user list, searches, revenue) |
| `app/routers/admin.py` | Create | Admin page route + action endpoints |
| `app/templates/admin.html` | Create | Admin dashboard template |
| `app/main.py` | Modify | Register admin router |
| `tests/test_admin.py` | Create | Tests for admin access control + actions |

---

### Task 1: Config + Admin Queries

**Files:**
- Modify: `app/config.py`
- Modify: `app/database/queries.py`

- [ ] **Step 1: Add `ADMIN_EMAIL` to config**

In `app/config.py`, add after the `APP_BASE_URL` line:

```python
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
```

- [ ] **Step 2: Add admin queries to `app/database/queries.py`**

Add at the end of the file:

```python
# --- Admin queries ---

async def admin_get_stats():
    """Get system-wide stats for admin dashboard."""
    users = await fetchrow("SELECT COUNT(*) as total FROM users WHERE deleted_at IS NULL")
    searches = await fetchrow("SELECT COUNT(*) as total FROM searches")
    credits_sold = await fetchrow(
        "SELECT COALESCE(SUM(amount), 0) as total FROM credit_transactions WHERE type = 'purchase'"
    )
    # Derive revenue from credit pack pricing (credits → dollars)
    total_credits = credits_sold["total"]
    # Weighted average: most purchases are Starter ($1.50/1K), approximate at $1.40/1K
    estimated_revenue = round(total_credits * 1.40 / 1000, 2)
    return {
        "total_users": users["total"],
        "total_searches": searches["total"],
        "total_credits_sold": total_credits,
        "estimated_revenue": estimated_revenue,
    }


async def admin_get_users(limit=50, offset=0):
    return await fetch("""
        SELECT u.id, u.email, u.credits_remaining, u.created_at, u.last_login_at, u.deleted_at,
               COUNT(s.id) as search_count
        FROM users u
        LEFT JOIN searches s ON s.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)


async def admin_count_users():
    row = await fetchrow("SELECT COUNT(*) as total FROM users")
    return row["total"]


async def admin_get_searches(limit=50, offset=0):
    return await fetch("""
        SELECT s.id, s.filtered_result_count, s.credits_used, s.created_at,
               sc.keyword, sc.location,
               u.email as user_email
        FROM searches s
        JOIN scrape_cache sc ON s.scrape_cache_id = sc.id
        JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)


async def admin_count_searches():
    row = await fetchrow("SELECT COUNT(*) as total FROM searches")
    return row["total"]


async def admin_get_revenue(limit=50, offset=0):
    return await fetch("""
        SELECT ct.amount, ct.stripe_payment_id, ct.created_at,
               u.email as user_email
        FROM credit_transactions ct
        JOIN users u ON ct.user_id = u.id
        WHERE ct.type = 'purchase'
        ORDER BY ct.created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)


async def admin_count_revenue():
    row = await fetchrow("SELECT COUNT(*) as total FROM credit_transactions WHERE type = 'purchase'")
    return row["total"]


async def admin_adjust_credits(user_id, amount):
    """Add or subtract credits. Amount can be negative."""
    await execute(
        "UPDATE users SET credits_remaining = credits_remaining + $1 WHERE id = $2",
        amount, user_id
    )
    await execute("""
        INSERT INTO credit_transactions (user_id, amount, type)
        VALUES ($1, $2, $3)
    """, user_id, amount, "admin_adjustment")


async def admin_delete_user(user_id):
    """Soft delete a user (sets deleted_at, consistent with existing architecture)."""
    await execute("UPDATE users SET deleted_at = NOW() WHERE id = $1", user_id)
```

- [ ] **Step 3: Commit**

```bash
git add app/config.py app/database/queries.py
git commit -m "feat: add admin config and database queries"
```

---

### Task 2: Admin Router + Template

**Files:**
- Create: `app/routers/admin.py`
- Create: `app/templates/admin.html`
- Modify: `app/main.py`

- [ ] **Step 1: Create admin router**

Create `app/routers/admin.py`:

```python
"""Admin panel — user management, search stats, revenue tracking."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import ADMIN_EMAIL
from app.routers.auth import get_current_user, require_current_user
from app.database import queries

logger = logging.getLogger("mapsearch.admin")

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


async def require_admin(request: Request):
    """FastAPI dependency: require authenticated admin user. Raises 401/403."""
    user = await require_current_user(request)
    if user["email"] != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@router.get("")
async def admin_dashboard(
    request: Request,
    tab: str = "users",
    page: int = 1,
):
    # GET page: redirect unauthenticated users (nicer UX than 401 JSON)
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    if user["email"] != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Forbidden")

    limit = 50
    offset = (page - 1) * limit

    stats = await queries.admin_get_stats()

    users = []
    users_total = 0
    searches = []
    searches_total = 0
    revenue = []
    revenue_total = 0

    if tab == "users":
        users = await queries.admin_get_users(limit=limit, offset=offset)
        users_total = await queries.admin_count_users()
    elif tab == "searches":
        searches = await queries.admin_get_searches(limit=limit, offset=offset)
        searches_total = await queries.admin_count_searches()
    elif tab == "revenue":
        revenue = await queries.admin_get_revenue(limit=limit, offset=offset)
        revenue_total = await queries.admin_count_revenue()

    total_pages = 0
    total_items = {"users": users_total, "searches": searches_total, "revenue": revenue_total}.get(tab, 0)
    if total_items > 0:
        total_pages = (total_items + limit - 1) // limit

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "tab": tab,
        "page": page,
        "total_pages": total_pages,
        "users": users,
        "searches": searches,
        "revenue": revenue,
    })


@router.post("/api/adjust-credits")
async def adjust_credits(
    request: Request,
    user_id: str = Form(...),
    amount: int = Form(...),
    admin: dict = Depends(require_admin),
):
    if amount == 0:
        raise HTTPException(status_code=400, detail="Amount cannot be zero")
    await queries.admin_adjust_credits(UUID(user_id), amount)
    logger.info(f"Admin adjusted credits: user={user_id} amount={amount}")
    return RedirectResponse(url="/admin?tab=users", status_code=303)


@router.post("/api/delete-user")
async def delete_user(
    request: Request,
    user_id: str = Form(...),
    admin: dict = Depends(require_admin),
):
    if UUID(user_id) == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    await queries.admin_delete_user(UUID(user_id))
    logger.info(f"Admin deleted user: {user_id}")
    return RedirectResponse(url="/admin?tab=users", status_code=303)
```

- [ ] **Step 2: Create admin template**

Create `app/templates/admin.html`:

```html
{% extends "base.html" %}

{% block title %}Admin — MapSearch{% endblock %}

{% block head %}
<link rel="stylesheet" href="/static/css/pages.css?v=11">
<style>
  .admin-tabs { display: flex; gap: var(--space-2); margin-bottom: var(--space-6); }
  .admin-tab {
    padding: var(--space-2) var(--space-4); border-radius: var(--radius-md);
    text-decoration: none; color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500;
    border: 1px solid var(--border); background: transparent;
  }
  .admin-tab.active { background: var(--accent); color: white; border-color: var(--accent); }
  .admin-tab:hover:not(.active) { background: var(--bg-hover); }
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
  .stat-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4); text-align: center; }
  .stat-value { font-size: var(--text-2xl); font-weight: 700; color: var(--accent); }
  .stat-label { font-size: var(--text-sm); color: var(--text-secondary); margin-top: var(--space-1); }
  .admin-actions { display: flex; gap: var(--space-2); align-items: center; }
  .admin-actions input[type="number"] {
    width: 80px; padding: var(--space-1) var(--space-2); border: 1px solid var(--border);
    border-radius: var(--radius-sm); background: var(--bg-primary); color: var(--text-primary);
    font-size: var(--text-sm);
  }
  .admin-actions button {
    padding: var(--space-1) var(--space-2); border-radius: var(--radius-sm);
    font-size: var(--text-xs); cursor: pointer; border: none; font-weight: 600;
  }
  .btn-sm-primary { background: var(--accent); color: white; }
  .btn-sm-danger { background: var(--red); color: white; }
  .pagination-nav { display: flex; justify-content: center; gap: var(--space-2); margin-top: var(--space-4); }
  .pagination-nav a, .pagination-nav span {
    padding: var(--space-1) var(--space-3); border-radius: var(--radius-sm);
    font-size: var(--text-sm); text-decoration: none; border: 1px solid var(--border);
    color: var(--text-secondary);
  }
  .pagination-nav .active { background: var(--accent); color: white; border-color: var(--accent); }
  .pagination-nav a:hover:not(.active) { background: var(--bg-hover); }
  .badge-deleted { color: var(--red); font-size: var(--text-xs); }
  .badge-active { color: var(--green); font-size: var(--text-xs); }
</style>
{% endblock %}

{% block content %}

<header class="header--glass">
  <a href="/" class="header__logo">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    MapSearch Admin
  </a>
  <div class="header__actions">
    <a href="/" style="color: var(--text-secondary); font-size: var(--text-sm); text-decoration: none;">← Back to app</a>
    <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle theme" title="Toggle theme">
      <svg class="theme-icon--light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      <svg class="theme-icon--dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
  </div>
</header>

<div class="page-container" style="max-width: 1100px;">

  <!-- Stats -->
  <div class="stat-grid">
    <div class="stat-card">
      <div class="stat-value">{{ stats.total_users }}</div>
      <div class="stat-label">Users</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ stats.total_searches }}</div>
      <div class="stat-label">Searches</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ "{:,}".format(stats.total_credits_sold) }}</div>
      <div class="stat-label">Credits Sold</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${{ "%.2f"|format(stats.estimated_revenue) }}</div>
      <div class="stat-label">Est. Revenue</div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="admin-tabs">
    <a href="/admin?tab=users" class="admin-tab {% if tab == 'users' %}active{% endif %}">Users</a>
    <a href="/admin?tab=searches" class="admin-tab {% if tab == 'searches' %}active{% endif %}">Searches</a>
    <a href="/admin?tab=revenue" class="admin-tab {% if tab == 'revenue' %}active{% endif %}">Revenue</a>
  </div>

  <!-- Users Tab -->
  {% if tab == "users" %}
  <div class="card" style="overflow-x: auto;">
    <table class="data-table">
      <thead>
        <tr>
          <th>Email</th>
          <th>Credits</th>
          <th>Searches</th>
          <th>Signed up</th>
          <th>Last login</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for u in users %}
        <tr>
          <td>{{ u.email }}</td>
          <td>{{ u.credits_remaining }}</td>
          <td>{{ u.search_count }}</td>
          <td>{{ u.created_at.strftime('%Y-%m-%d') if u.created_at else '—' }}</td>
          <td>{{ u.last_login_at.strftime('%Y-%m-%d') if u.last_login_at else '—' }}</td>
          <td>
            {% if u.deleted_at %}<span class="badge-deleted">Deleted</span>
            {% else %}<span class="badge-active">Active</span>{% endif %}
          </td>
          <td>
            <div class="admin-actions">
              <form method="POST" action="/admin/api/adjust-credits" style="display:flex;gap:4px;align-items:center;">
                <input type="hidden" name="user_id" value="{{ u.id }}">
                <input type="number" name="amount" value="100" step="1">
                <button type="submit" class="btn-sm-primary">Adjust</button>
              </form>
              <form method="POST" action="/admin/api/delete-user" onsubmit="return confirm('Delete {{ u.email }}? This cannot be undone.')">
                <input type="hidden" name="user_id" value="{{ u.id }}">
                <button type="submit" class="btn-sm-danger">Delete</button>
              </form>
            </div>
          </td>
        </tr>
        {% endfor %}
        {% if not users %}
        <tr><td colspan="7" style="text-align:center;color:var(--text-secondary);">No users</td></tr>
        {% endif %}
      </tbody>
    </table>
  </div>
  {% endif %}

  <!-- Searches Tab -->
  {% if tab == "searches" %}
  <div class="card" style="overflow-x: auto;">
    <table class="data-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Keyword</th>
          <th>Location</th>
          <th>Results</th>
          <th>Credits</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {% for s in searches %}
        <tr>
          <td>{{ s.user_email }}</td>
          <td>{{ s.keyword }}</td>
          <td>{{ s.location }}</td>
          <td>{{ s.filtered_result_count }}</td>
          <td>{{ s.credits_used }}</td>
          <td>{{ s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else '—' }}</td>
        </tr>
        {% endfor %}
        {% if not searches %}
        <tr><td colspan="6" style="text-align:center;color:var(--text-secondary);">No searches yet</td></tr>
        {% endif %}
      </tbody>
    </table>
  </div>
  {% endif %}

  <!-- Revenue Tab -->
  {% if tab == "revenue" %}
  <div class="card" style="overflow-x: auto;">
    <table class="data-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Credits</th>
          <th>Stripe ID</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {% for r in revenue %}
        <tr>
          <td>{{ r.user_email }}</td>
          <td style="color: var(--green);">+{{ r.amount }}</td>
          <td style="font-size: var(--text-xs);">{{ r.stripe_payment_id or '—' }}</td>
          <td>{{ r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '—' }}</td>
        </tr>
        {% endfor %}
        {% if not revenue %}
        <tr><td colspan="4" style="text-align:center;color:var(--text-secondary);">No purchases yet</td></tr>
        {% endif %}
      </tbody>
    </table>
  </div>
  {% endif %}

  <!-- Pagination -->
  {% if total_pages > 1 %}
  <div class="pagination-nav">
    {% if page > 1 %}
    <a href="/admin?tab={{ tab }}&page={{ page - 1 }}">← Prev</a>
    {% endif %}
    {% for p in range(1, total_pages + 1) %}
      {% if p == page %}
      <span class="active">{{ p }}</span>
      {% else %}
      <a href="/admin?tab={{ tab }}&page={{ p }}">{{ p }}</a>
      {% endif %}
    {% endfor %}
    {% if page < total_pages %}
    <a href="/admin?tab={{ tab }}&page={{ page + 1 }}">Next →</a>
    {% endif %}
  </div>
  {% endif %}

</div>

{% endblock %}
```

- [ ] **Step 3: Register admin router in `app/main.py`**

Add after the account router registration:

```python
from app.routers import admin
app.include_router(admin.router)
```

- [ ] **Step 4: Add `ADMIN_EMAIL` to `.env.example`**

Add to `.env.example`:
```
# Admin panel access (email of admin user)
ADMIN_EMAIL=peter@mapsearch.app
```

- [ ] **Step 5: Add `ADMIN_EMAIL` to test env in `tests/conftest.py`**

Add after the other `os.environ.setdefault` lines:
```python
os.environ.setdefault("ADMIN_EMAIL", "admin@test.com")
```

- [ ] **Step 6: Commit**

```bash
git add app/routers/admin.py app/templates/admin.html app/main.py .env.example tests/conftest.py
git commit -m "feat: add admin panel with user management, search stats, revenue tracking"
```

---

### Task 3: Admin Tests

**Files:**
- Create: `tests/test_admin.py`

- [ ] **Step 1: Write admin access control and action tests**

Create `tests/test_admin.py`:

```python
"""Tests for admin panel — access control and actions."""

from unittest.mock import AsyncMock, patch
from datetime import datetime
import uuid
import os

from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


def _make_auth_cookie(email=None):
    """Create a JWT cookie for a specific user."""
    from jose import jwt
    from app.config import SECRET_KEY, JWT_ALGORITHM
    user_id = str(MOCK_USER_ID)
    return {"mapsearch_session": jwt.encode(
        {"sub": user_id, "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM
    )}


def _make_admin_user():
    return make_mock_user(email=os.environ.get("ADMIN_EMAIL", "admin@test.com"))


def _make_regular_user():
    return make_mock_user(email="regular@example.com")


class TestAdminAccess:
    """Admin panel access control."""

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_admin_page_loads_for_admin(self, mock_get_user, client):
        mock_get_user.return_value = _make_admin_user()
        with patch("app.database.queries.admin_get_stats", new_callable=AsyncMock) as mock_stats, \
             patch("app.database.queries.admin_get_users", new_callable=AsyncMock) as mock_users, \
             patch("app.database.queries.admin_count_users", new_callable=AsyncMock) as mock_count:
            mock_stats.return_value = {"total_users": 5, "total_searches": 100, "total_credits_sold": 5000, "estimated_revenue": 7.00}
            mock_users.return_value = []
            mock_count.return_value = 0
            response = client.get("/admin", cookies=_make_auth_cookie())
        assert response.status_code == 200

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_admin_403_for_non_admin(self, mock_get_user, client):
        mock_get_user.return_value = _make_regular_user()
        response = client.get("/admin", cookies=_make_auth_cookie())
        assert response.status_code == 403

    def test_admin_redirects_unauthenticated(self, client):
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 302


class TestAdminActions:
    """Admin credit adjustment and user deletion."""

    @patch("app.database.queries.admin_adjust_credits", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_adjust_credits(self, mock_get_user, mock_adjust, client):
        mock_get_user.return_value = _make_admin_user()
        mock_adjust.return_value = None
        target_user = uuid.uuid4()
        response = client.post("/admin/api/adjust-credits",
            data={"user_id": str(target_user), "amount": "500"},
            cookies=_make_auth_cookie(),
            follow_redirects=False
        )
        assert response.status_code == 303
        mock_adjust.assert_called_once_with(target_user, 500)

    @patch("app.database.queries.admin_delete_user", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_delete_user(self, mock_get_user, mock_delete, client):
        mock_get_user.return_value = _make_admin_user()
        mock_delete.return_value = None
        target_user = uuid.uuid4()
        response = client.post("/admin/api/delete-user",
            data={"user_id": str(target_user)},
            cookies=_make_auth_cookie(),
            follow_redirects=False
        )
        assert response.status_code == 303
        mock_delete.assert_called_once_with(target_user)

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_delete_self_returns_400(self, mock_get_user, client):
        mock_get_user.return_value = _make_admin_user()
        response = client.post("/admin/api/delete-user",
            data={"user_id": str(MOCK_USER_ID)},
            cookies=_make_auth_cookie(),
        )
        assert response.status_code == 400

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_adjust_credits_403_for_non_admin(self, mock_get_user, client):
        mock_get_user.return_value = _make_regular_user()
        response = client.post("/admin/api/adjust-credits",
            data={"user_id": str(uuid.uuid4()), "amount": "100"},
            cookies=_make_auth_cookie(),
        )
        assert response.status_code == 403
```

- [ ] **Step 2: Run tests**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_admin.py -v
```

Expected: All 7 pass.

- [ ] **Step 3: Run full test suite**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest -v
```

Expected: All pass (74 existing + 7 new = 81).

- [ ] **Step 4: Commit**

```bash
git add tests/test_admin.py
git commit -m "test: add admin panel access control and action tests"
```

---

### Task 4: Deploy + CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Set ADMIN_EMAIL on VPS**

```bash
ssh root@82.21.4.94 "echo 'ADMIN_EMAIL=peter@mapsearch.app' >> /var/www/mapsearch/.env"
```

(Replace with your actual admin email.)

- [ ] **Step 2: Update CHANGELOG**

Add at the top of CHANGELOG.md:

```markdown
## v0.5.0 — 2026-03-28

### Added
- Admin panel (`/admin`) — user management, search stats, revenue tracking
- System stats: total users, searches, credits sold
- User table: email, credits, search count, signup/login dates, adjust credits, delete
- Search history: all searches across users with keyword, location, results, credits
- Revenue: credit purchase transactions with Stripe payment IDs
- `ADMIN_EMAIL` env var for access control
```

- [ ] **Step 3: Commit and deploy**

```bash
git add CHANGELOG.md
git commit -m "docs: changelog for v0.5.0 — admin panel"
git push origin main
bash deploy.sh app
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Config + admin queries | config.py, queries.py |
| 2 | Router + template + registration | admin.py, admin.html, main.py, .env.example, conftest.py |
| 3 | Tests | test_admin.py |
| 4 | Deploy + changelog | CHANGELOG.md, VPS .env |
