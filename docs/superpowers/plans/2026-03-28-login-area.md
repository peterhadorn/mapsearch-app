# Login Area Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add authenticated user navigation, account management pages (Account, Billing, History), and password reset flow to MapSearch.app.

**Architecture:** Jinja2 server-rendered pages extending `base.html` with page-specific JS via `{% block scripts %}`. New `account.py` router for page routes, new API endpoints in `auth.py` and `credits.py`. Junction table `search_result_ids` stores exact filtered results per search. SMTP-based password reset with hashed tokens.

**Tech Stack:** FastAPI, asyncpg, Jinja2, bcrypt/passlib, smtplib (stdlib), SHA-256 for reset tokens

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `app/database/schema.sql` | Modify | Add `deleted_at`, `password_reset_tokens`, `search_result_ids` |
| `app/database/queries.py` | Modify | Add `deleted_at IS NULL` guards, new queries for history/transactions/tokens |
| `app/config.py` | Modify | Add SMTP config vars |
| `app/models/request_models.py` | Modify | Add `ChangePasswordRequest`, `ForgotPasswordRequest`, `ResetPasswordRequest`, `force_refresh` |
| `app/routers/auth.py` | Modify | Add change-password, delete-account, forgot/reset-password endpoints |
| `app/routers/credits.py` | Modify | Add `GET /api/credits/transactions` endpoint |
| `app/routers/account.py` | Create | Page routes for `/account`, `/billing`, `/history`, `/history/{id}`, `/reset-password` |
| `app/services/search_service.py` | Modify | Store filtered result IDs, respect `force_refresh` flag |
| `app/services/email_service.py` | Create | SMTP email sending |
| `app/templates/base.html` | Modify | Move page-specific scripts to `{% block scripts %}` |
| `app/templates/app.html` | Modify | Add `{% block scripts %}`, update nav for logged-in state, add forgot-password link |
| `app/templates/account.html` | Create | Account settings page |
| `app/templates/billing.html` | Create | Credits & billing page |
| `app/templates/history.html` | Create | Search history list |
| `app/templates/history_detail.html` | Create | Single search results view |
| `app/templates/reset_password.html` | Create | Password reset form |
| `app/static/css/pages.css` | Create | Shared styles for account pages |
| `app/static/js/account.js` | Create | Client-side logic for account pages |
| `app/main.py` | Modify | Register account router, add startup purge task |
| `tests/conftest.py` | Modify | Add `deleted_at` field to `make_mock_user` |
| `tests/test_account.py` | Create | Tests for change-password, delete-account |
| `tests/test_password_reset.py` | Create | Tests for forgot/reset password flow |
| `tests/test_history.py` | Create | Tests for search history + transactions endpoints |
| `tests/test_search_result_ids.py` | Create | Tests for filtered result snapshot storage |
| `app/static/i18n/en.json` | Modify | Add i18n keys for account pages, nav dropdown, password reset |
| `app/static/i18n/fr.json` | Modify | Add French translations for new keys |
| `app/static/i18n/de.json` | Modify | Add German translations for new keys |
| `app/static/i18n/es.json` | Modify | Add Spanish translations for new keys |

---

### Task 1: Database Schema Changes

**Files:**
- Modify: `app/database/schema.sql`

- [ ] **Step 1: Add `deleted_at` column to users table**

Add after `last_login_at` line in `app/database/schema.sql`:

```sql
-- Add to users table definition, after last_login_at:
    deleted_at TIMESTAMP
```

- [ ] **Step 2: Add `password_reset_tokens` table**

Add after the `exports` table in `app/database/schema.sql`:

```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_reset_tokens_hash ON password_reset_tokens(token_hash);
CREATE INDEX idx_reset_tokens_user ON password_reset_tokens(user_id);
```

- [ ] **Step 3: Add `search_result_ids` junction table**

Add after `password_reset_tokens` in `app/database/schema.sql`:

```sql
CREATE TABLE search_result_ids (
    search_id UUID REFERENCES searches(id) ON DELETE CASCADE,
    search_result_id UUID REFERENCES search_results(id) ON DELETE CASCADE,
    PRIMARY KEY (search_id, search_result_id)
);
```

- [ ] **Step 4: Commit**

```bash
git add app/database/schema.sql
git commit -m "feat: add deleted_at, password_reset_tokens, search_result_ids to schema"
```

---

### Task 2: Soft-Delete Auth Guards in Queries

**Files:**
- Modify: `app/database/queries.py`
- Modify: `tests/conftest.py`
- Create: `tests/test_account.py`

- [ ] **Step 1: Write failing test for soft-delete guard**

Create `tests/test_account.py`:

```python
"""Tests for account management — soft delete, password change."""

from unittest.mock import AsyncMock, patch
from datetime import datetime

from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


def _make_deleted_user():
    user = make_mock_user()
    user["deleted_at"] = datetime(2026, 3, 1)
    return user


class TestSoftDeleteGuard:
    """Soft-deleted users must not be returned by user lookups."""

    @patch("app.database.queries.fetchrow", new_callable=AsyncMock)
    def test_get_user_by_email_excludes_deleted(self, mock_fetchrow, client):
        mock_fetchrow.return_value = None  # query with deleted_at IS NULL returns nothing
        response = client.post("/api/auth/login", json={
            "email": MOCK_USER_EMAIL,
            "password": "securepassword123"
        })
        assert response.status_code == 401

    @patch("app.database.queries.fetchrow", new_callable=AsyncMock)
    def test_get_user_by_id_excludes_deleted(self, mock_fetchrow, client):
        mock_fetchrow.return_value = None
        # Try to access /me with a cookie for a deleted user
        response = client.get("/api/auth/me")
        assert response.status_code == 401
```

- [ ] **Step 2: Run test to verify it passes (guards not yet added but mocks return None)**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_account.py::TestSoftDeleteGuard -v
```

- [ ] **Step 3: Add `deleted_at IS NULL` guards to queries**

Replace the two query functions in `app/database/queries.py`:

```python
async def get_user_by_email(email):
    return await fetchrow(
        "SELECT * FROM users WHERE email = $1 AND deleted_at IS NULL", email
    )


async def get_user_by_id(user_id):
    return await fetchrow(
        "SELECT * FROM users WHERE id = $1 AND deleted_at IS NULL", user_id
    )
```

- [ ] **Step 4: Update `make_mock_user` in conftest to include `deleted_at`**

In `tests/conftest.py`, add `deleted_at=None` to the `MockRecord` dict inside `make_mock_user`:

```python
    return MockRecord({
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "name": None,
        "google_id": None,
        "credits_remaining": credits,
        "locale": locale,
        "stripe_customer_id": None,
        "created_at": datetime(2026, 1, 1),
        "last_login_at": None,
        "deleted_at": None,
    })
```

- [ ] **Step 5: Run all existing tests to verify nothing breaks**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest -v
```

Expected: All pass.

- [ ] **Step 6: Commit**

```bash
git add app/database/queries.py tests/conftest.py tests/test_account.py
git commit -m "feat: add deleted_at IS NULL guard to all user queries"
```

---

### Task 3: Config + Request Models

**Files:**
- Modify: `app/config.py`
- Modify: `app/models/request_models.py`

- [ ] **Step 1: Add SMTP config to `app/config.py`**

Add after the `JWT_COOKIE_NAME` line:

```python
# SMTP for password reset emails
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "noreply@mapsearch.app")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "https://mapsearch.app")
```

- [ ] **Step 2: Add new request models to `app/models/request_models.py`**

Add after the existing `SearchRequest` class:

```python
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
```

- [ ] **Step 3: Add `force_refresh` to `SearchRequest`**

Update the `SearchRequest` class:

```python
class SearchRequest(BaseModel):
    keyword: str = Field(max_length=255)
    location: str = Field(max_length=255)
    zoom_level: int = Field(default=13, ge=11, le=14)
    near_me: bool = False
    filters: dict = {}
    force_refresh: bool = False
```

- [ ] **Step 4: Commit**

```bash
git add app/config.py app/models/request_models.py
git commit -m "feat: add SMTP config, password/reset request models, force_refresh flag"
```

---

### Task 4: Email Service

**Files:**
- Create: `app/services/email_service.py`
- Create: `tests/test_password_reset.py`

- [ ] **Step 1: Write failing test for email sending**

Create `tests/test_password_reset.py`:

```python
"""Tests for password reset flow — token generation, email, reset."""

import hashlib
import secrets
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


class TestEmailService:
    @patch("app.services.email_service.SMTP_HOST", "smtp.test.com")
    @patch("app.services.email_service.SMTP_PORT", 587)
    @patch("app.services.email_service.SMTP_USER", "testuser")
    @patch("app.services.email_service.SMTP_PASSWORD", "testpass")
    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_reset_email(self, mock_smtp_cls):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        from app.services.email_service import send_reset_email
        send_reset_email("test@example.com", "https://mapsearch.app/reset-password?token=abc123")

        mock_server.send_message.assert_called_once()

    @patch("app.services.email_service.SMTP_HOST", "")
    def test_send_reset_email_skips_when_no_smtp(self):
        """When SMTP_HOST is empty, email is silently skipped (dev/test mode)."""
        from app.services.email_service import send_reset_email
        # Should not raise — just logs a warning
        send_reset_email("test@example.com", "https://mapsearch.app/reset-password?token=abc123")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_password_reset.py::TestEmailService -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.email_service'`

- [ ] **Step 3: Implement email service**

Create `app/services/email_service.py`:

```python
"""SMTP email service for password reset and transactional emails."""

import logging
import smtplib
from email.message import EmailMessage

from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

logger = logging.getLogger("mapsearch.email")


def send_reset_email(to_email: str, reset_url: str):
    """Send a password reset email via SMTP.

    Args:
        to_email: Recipient email address.
        reset_url: Full URL with token for password reset.
    """
    msg = EmailMessage()
    msg["Subject"] = "Reset your MapSearch password"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"You requested a password reset for your MapSearch account.\n\n"
        f"Click here to reset your password:\n{reset_url}\n\n"
        f"This link expires in 1 hour.\n\n"
        f"If you didn't request this, ignore this email."
    )

    if not SMTP_HOST:
        logger.warning("SMTP not configured — skipping email to %s", to_email)
        return

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    logger.info("Reset email sent to %s", to_email)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_password_reset.py::TestEmailService -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/email_service.py tests/test_password_reset.py
git commit -m "feat: add SMTP email service for password reset"
```

---

### Task 5: Password Reset Queries + Auth Endpoints

**Files:**
- Modify: `app/database/queries.py`
- Modify: `app/routers/auth.py`
- Modify: `tests/test_password_reset.py`

- [ ] **Step 1: Add reset token queries to `app/database/queries.py`**

Add at the end of the file:

```python
async def create_reset_token(user_id, token_hash, expires_at):
    return await execute("""
        INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3)
    """, user_id, token_hash, expires_at)


async def get_valid_reset_token(token_hash):
    return await fetchrow("""
        SELECT * FROM password_reset_tokens
        WHERE token_hash = $1
        AND expires_at > NOW()
        AND used_at IS NULL
    """, token_hash)


async def mark_token_used(token_id):
    return await execute(
        "UPDATE password_reset_tokens SET used_at = NOW() WHERE id = $1",
        token_id
    )


async def update_user_password(user_id, password_hash):
    return await execute(
        "UPDATE users SET password_hash = $1 WHERE id = $2",
        password_hash, user_id
    )


async def soft_delete_user(user_id):
    return await execute(
        "UPDATE users SET deleted_at = NOW() WHERE id = $1",
        user_id
    )


async def purge_deleted_users():
    """Permanently delete users whose deleted_at is older than 30 days.
    Cascading FKs handle searches, transactions, exports, tokens."""
    return await execute("""
        DELETE FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
    """)
```

- [ ] **Step 2: Write failing tests for forgot-password and reset-password endpoints**

Add to `tests/test_password_reset.py`:

```python
class TestForgotPassword:
    @patch("app.routers.auth.queries.get_user_by_email", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.create_reset_token", new_callable=AsyncMock)
    @patch("app.routers.auth.send_reset_email")
    def test_forgot_password_sends_email(self, mock_send, mock_create_token, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        mock_create_token.return_value = None

        response = client.post("/api/auth/forgot-password", json={"email": MOCK_USER_EMAIL})
        assert response.status_code == 200
        assert response.json()["message"] == "If that email exists, a reset link has been sent"
        mock_send.assert_called_once()

    @patch("app.routers.auth.queries.get_user_by_email", new_callable=AsyncMock)
    def test_forgot_password_unknown_email_still_200(self, mock_get_user, client):
        mock_get_user.return_value = None
        response = client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
        assert response.status_code == 200
        assert response.json()["message"] == "If that email exists, a reset link has been sent"


class TestResetPassword:
    @patch("app.routers.auth.queries.get_valid_reset_token", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.update_user_password", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.mark_token_used", new_callable=AsyncMock)
    def test_reset_password_success(self, mock_mark, mock_update, mock_get_token, client):
        mock_get_token.return_value = {
            "id": MOCK_USER_ID,
            "user_id": MOCK_USER_ID,
            "token_hash": "fakehash",
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "used_at": None,
        }
        mock_update.return_value = None
        mock_mark.return_value = None

        response = client.post("/api/auth/reset-password", json={
            "token": "valid-token",
            "new_password": "newpassword123"
        })
        assert response.status_code == 200
        mock_update.assert_called_once()
        mock_mark.assert_called_once()

    @patch("app.routers.auth.queries.get_valid_reset_token", new_callable=AsyncMock)
    def test_reset_password_invalid_token(self, mock_get_token, client):
        mock_get_token.return_value = None
        response = client.post("/api/auth/reset-password", json={
            "token": "invalid-token",
            "new_password": "newpassword123"
        })
        assert response.status_code == 400
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_password_reset.py::TestForgotPassword tests/test_password_reset.py::TestResetPassword -v
```

Expected: FAIL — endpoints don't exist yet.

- [ ] **Step 4: Add forgot-password and reset-password endpoints to `app/routers/auth.py`**

Add these imports at the top of `app/routers/auth.py`:

```python
import hashlib
import secrets
from app.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_COOKIE_NAME, APP_BASE_URL
from app.models.request_models import SignupRequest, LoginRequest, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.services.email_service import send_reset_email
```

Replace the existing import lines:
```python
from app.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_COOKIE_NAME
```
with:
```python
from app.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_COOKIE_NAME, APP_BASE_URL
```

And replace:
```python
from app.models.request_models import SignupRequest, LoginRequest
```
with:
```python
from app.models.request_models import SignupRequest, LoginRequest, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.services.email_service import send_reset_email
```

Add these endpoints after the `me` endpoint:

```python
@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, body: ForgotPasswordRequest):
    user = await queries.get_user_by_email(body.email)
    if user:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await queries.create_reset_token(user["id"], token_hash, expires_at)

        reset_url = f"{APP_BASE_URL}/reset-password?token={token}"
        send_reset_email(body.email, reset_url)

    # Always return same response to avoid email enumeration
    return {"message": "If that email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    token_hash = hashlib.sha256(body.token.encode()).hexdigest()
    token_row = await queries.get_valid_reset_token(token_hash)
    if not token_row:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    new_hash = pwd_context.hash(body.new_password)
    await queries.update_user_password(token_row["user_id"], new_hash)
    await queries.mark_token_used(token_row["id"])

    return {"message": "Password reset successful"}


@router.put("/password")
async def change_password(body: ChangePasswordRequest, user: dict = Depends(require_current_user)):
    if not pwd_context.verify(body.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    new_hash = pwd_context.hash(body.new_password)
    await queries.update_user_password(user["id"], new_hash)
    return {"message": "Password changed"}


@router.post("/delete-account")
async def delete_account(response: Response, user: dict = Depends(require_current_user)):
    await queries.soft_delete_user(user["id"])
    response.delete_cookie(key=JWT_COOKIE_NAME)
    return {"message": "Account scheduled for deletion in 30 days"}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_password_reset.py -v
```

Expected: All PASS.

- [ ] **Step 6: Add startup purge task to `app/main.py`**

Add a startup event that purges expired soft-deleted users on each app boot (simple, no cron needed):

```python
@app.on_event("startup")
async def startup_purge():
    """Purge users who were soft-deleted more than 30 days ago."""
    from app.database import queries
    await queries.purge_deleted_users()
```

- [ ] **Step 7: Commit**

```bash
git add app/database/queries.py app/routers/auth.py app/main.py tests/test_password_reset.py
git commit -m "feat: add password reset, change password, soft-delete account endpoints with 30-day purge"
```

---

### Task 6: Change Password + Delete Account Tests

**Files:**
- Modify: `tests/test_account.py`

- [ ] **Step 1: Add change-password and delete-account tests**

Add to `tests/test_account.py`:

```python
from unittest.mock import patch, AsyncMock
from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


class TestChangePassword:
    @patch("app.database.queries.execute", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_change_password_success(self, mock_get_user, mock_execute, client):
        mock_get_user.return_value = make_mock_user()

        from jose import jwt
        from app.config import SECRET_KEY, JWT_ALGORITHM
        token = jwt.encode({"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.put("/api/auth/password",
            json={"current_password": "securepassword123", "new_password": "newpassword456"},
            cookies={"mapsearch_session": token}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed"

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_change_password_wrong_current(self, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()

        from jose import jwt
        from app.config import SECRET_KEY, JWT_ALGORITHM
        token = jwt.encode({"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.put("/api/auth/password",
            json={"current_password": "wrongpassword", "new_password": "newpassword456"},
            cookies={"mapsearch_session": token}
        )
        assert response.status_code == 400


class TestDeleteAccount:
    @patch("app.database.queries.execute", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_delete_account_success(self, mock_get_user, mock_execute, client):
        mock_get_user.return_value = make_mock_user()

        from jose import jwt
        from app.config import SECRET_KEY, JWT_ALGORITHM
        token = jwt.encode({"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.post("/api/auth/delete-account",
            cookies={"mapsearch_session": token}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Account scheduled for deletion in 30 days"

    def test_delete_account_unauthenticated(self, client):
        response = client.post("/api/auth/delete-account")
        assert response.status_code == 401
```

- [ ] **Step 2: Run tests**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_account.py -v
```

Expected: All PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_account.py
git commit -m "test: add change-password and delete-account tests"
```

---

### Task 7: Credit Transactions Endpoint

**Files:**
- Modify: `app/database/queries.py`
- Modify: `app/routers/credits.py`
- Create: `tests/test_history.py`

- [ ] **Step 1: Add transaction query to `app/database/queries.py`**

Add at the end:

```python
async def get_credit_transactions(user_id, limit=50, offset=0):
    return await fetch("""
        SELECT id, amount, type, reference_id, stripe_payment_id, created_at
        FROM credit_transactions
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """, user_id, limit, offset)


async def count_credit_transactions(user_id):
    row = await fetchrow(
        "SELECT COUNT(*) as total FROM credit_transactions WHERE user_id = $1",
        user_id
    )
    return row["total"]
```

- [ ] **Step 2: Write failing test for transactions endpoint**

Create `tests/test_history.py`:

```python
"""Tests for search history and credit transaction endpoints."""

from unittest.mock import AsyncMock, patch
from datetime import datetime
import uuid

from tests.conftest import make_mock_user, MOCK_USER_ID


def _make_auth_cookie():
    from jose import jwt
    from app.config import SECRET_KEY, JWT_ALGORITHM
    return {"mapsearch_session": jwt.encode(
        {"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM
    )}


class TestCreditTransactions:
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    @patch("app.database.queries.get_credit_transactions", new_callable=AsyncMock)
    def test_list_transactions(self, mock_txns, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        mock_txns.return_value = [
            {"id": uuid.uuid4(), "amount": -10, "type": "search", "reference_id": None,
             "stripe_payment_id": None, "created_at": datetime(2026, 3, 28)},
            {"id": uuid.uuid4(), "amount": 1000, "type": "purchase", "reference_id": None,
             "stripe_payment_id": "pi_test", "created_at": datetime(2026, 3, 27)},
        ]

        response = client.get("/api/credits/transactions", cookies=_make_auth_cookie())
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 2

    def test_transactions_unauthenticated(self, client):
        response = client.get("/api/credits/transactions")
        assert response.status_code == 401
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_history.py::TestCreditTransactions -v
```

Expected: FAIL — endpoint doesn't exist.

- [ ] **Step 4: Add transactions endpoint to `app/routers/credits.py`**

Add after the `credit_balance` endpoint:

```python
@router.get("/transactions")
async def credit_transactions(
    page: int = 1,
    user: dict = Depends(require_current_user),
):
    from app.database import queries as q
    limit = 50
    offset = (page - 1) * limit
    txns = await q.get_credit_transactions(user["id"], limit=limit, offset=offset)
    total = await q.count_credit_transactions(user["id"])
    return {
        "transactions": [
            {
                "id": str(t["id"]),
                "amount": t["amount"],
                "type": t["type"],
                "stripe_payment_id": t["stripe_payment_id"],
                "created_at": t["created_at"].isoformat() if t["created_at"] else None,
            }
            for t in txns
        ],
        "page": page,
        "total": total,
        "has_next": offset + limit < total,
    }
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_history.py::TestCreditTransactions -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app/database/queries.py app/routers/credits.py tests/test_history.py
git commit -m "feat: add credit transactions endpoint with pagination"
```

---

### Task 8: Search History Queries + Endpoints

**Files:**
- Modify: `app/database/queries.py`
- Modify: `app/routers/auth.py` (reuse `require_current_user`)
- Create: `app/routers/search_history.py`
- Modify: `app/main.py`
- Modify: `tests/test_history.py`

- [ ] **Step 1: Add search history queries to `app/database/queries.py`**

Add at the end:

```python
async def get_user_searches(user_id, limit=50, offset=0):
    return await fetch("""
        SELECT s.id, s.filters_applied, s.filtered_result_count, s.credits_used, s.created_at,
               sc.keyword, sc.location
        FROM searches s
        JOIN scrape_cache sc ON s.scrape_cache_id = sc.id
        WHERE s.user_id = $1
        ORDER BY s.created_at DESC
        LIMIT $2 OFFSET $3
    """, user_id, limit, offset)


async def count_user_searches(user_id):
    row = await fetchrow(
        "SELECT COUNT(*) as total FROM searches WHERE user_id = $1",
        user_id
    )
    return row["total"]


async def get_search_with_results(search_id, user_id):
    """Get a single search and its filtered results via the junction table."""
    search = await fetchrow("""
        SELECT s.id, s.filters_applied, s.filtered_result_count, s.credits_used, s.created_at,
               sc.keyword, sc.location, sc.latitude, sc.longitude, sc.zoom_level
        FROM searches s
        JOIN scrape_cache sc ON s.scrape_cache_id = sc.id
        WHERE s.id = $1 AND s.user_id = $2
    """, search_id, user_id)
    if not search:
        return None, None

    results = await fetch("""
        SELECT sr.* FROM search_results sr
        JOIN search_result_ids sri ON sr.id = sri.search_result_id
        WHERE sri.search_id = $1
    """, search_id)
    return search, results
```

- [ ] **Step 2: Write failing tests for search history API**

Add to `tests/test_history.py`:

```python
class TestSearchHistory:
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    @patch("app.database.queries.get_user_searches", new_callable=AsyncMock)
    def test_list_searches(self, mock_searches, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        mock_searches.return_value = [
            {"id": uuid.uuid4(), "keyword": "plumber", "location": "NYC",
             "filtered_result_count": 50, "credits_used": 50,
             "filters_applied": "{}", "created_at": datetime(2026, 3, 28)},
        ]

        response = client.get("/api/searches", cookies=_make_auth_cookie())
        assert response.status_code == 200
        assert len(response.json()["searches"]) == 1

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    @patch("app.database.queries.get_search_with_results", new_callable=AsyncMock)
    def test_get_search_detail(self, mock_detail, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        search_id = uuid.uuid4()
        mock_detail.return_value = (
            {"id": search_id, "keyword": "plumber", "location": "NYC",
             "filtered_result_count": 2, "credits_used": 2, "filters_applied": "{}",
             "created_at": datetime(2026, 3, 28), "latitude": 40.7, "longitude": -74.0,
             "zoom_level": 13},
            [
                {"id": uuid.uuid4(), "business_name": "Joe's Plumbing", "latitude": 40.71, "longitude": -74.01,
                 "domain": "joesplumbing.com", "phone": "555-0001", "email": None,
                 "rating": 4.5, "reviews_count": 100, "category": "Plumber"},
            ]
        )

        response = client.get(f"/api/searches/{search_id}", cookies=_make_auth_cookie())
        assert response.status_code == 200
        data = response.json()
        assert data["search"]["keyword"] == "plumber"
        assert len(data["results"]) == 1

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    @patch("app.database.queries.get_search_with_results", new_callable=AsyncMock)
    def test_get_search_detail_not_found(self, mock_detail, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        mock_detail.return_value = (None, None)

        response = client.get(f"/api/searches/{uuid.uuid4()}", cookies=_make_auth_cookie())
        assert response.status_code == 404
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_history.py::TestSearchHistory -v
```

Expected: FAIL — endpoints don't exist.

- [ ] **Step 4: Create search history API router**

Create `app/routers/search_history.py`:

```python
"""Search history API — list past searches, view results."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.routers.auth import require_current_user
from app.database import queries

router = APIRouter(prefix="/api/searches", tags=["search-history"])


@router.get("")
async def list_searches(page: int = 1, user: dict = Depends(require_current_user)):
    limit = 50
    offset = (page - 1) * limit
    rows = await queries.get_user_searches(user["id"], limit=limit, offset=offset)
    total = await queries.count_user_searches(user["id"])
    return {
        "searches": [
            {
                "id": str(r["id"]),
                "keyword": r["keyword"],
                "location": r["location"],
                "result_count": r["filtered_result_count"],
                "credits_used": r["credits_used"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ],
        "page": page,
        "total": total,
        "has_next": offset + limit < total,
    }


@router.get("/{search_id}")
async def get_search_detail(search_id: str, user: dict = Depends(require_current_user)):
    search, results = await queries.get_search_with_results(UUID(search_id), user["id"])
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    return {
        "search": {
            "id": str(search["id"]),
            "keyword": search["keyword"],
            "location": search["location"],
            "result_count": search["filtered_result_count"],
            "credits_used": search["credits_used"],
            "filters_applied": search["filters_applied"],
            "latitude": float(search["latitude"]) if search["latitude"] else None,
            "longitude": float(search["longitude"]) if search["longitude"] else None,
            "zoom_level": search["zoom_level"],
            "created_at": search["created_at"].isoformat() if search["created_at"] else None,
        },
        "results": [dict(r) for r in results],
    }
```

- [ ] **Step 5: Register router in `app/main.py`**

Add after the export router registration:

```python
from app.routers import search_history
app.include_router(search_history.router)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_history.py -v
```

Expected: All PASS.

- [ ] **Step 7: Commit**

```bash
git add app/database/queries.py app/routers/search_history.py app/main.py tests/test_history.py
git commit -m "feat: add search history API with filtered result snapshots"
```

---

### Task 9: Store Filtered Result IDs in Search Service

**Files:**
- Modify: `app/services/search_service.py`
- Create: `tests/test_search_result_ids.py`

- [ ] **Step 1: Write failing test for result ID storage**

Create `tests/test_search_result_ids.py`:

```python
"""Tests for search_result_ids junction table population during search."""

import json
import uuid
from unittest.mock import AsyncMock, patch, call

import pytest

from tests.conftest import MOCK_USER_ID


def _make_raw_result(result_id, has_website=True, has_email=True, rating=4.5, reviews=100):
    return {
        "id": result_id,
        "scrape_cache_id": uuid.uuid4(),
        "business_name": "Test Biz",
        "has_website": has_website,
        "has_email": has_email,
        "has_phone": True,
        "rating": rating,
        "reviews_count": reviews,
        "is_claimed": True,
        "photos_count": 5,
        "category": "Plumber",
        "domain": "test.com" if has_website else None,
        "email": "a@b.com" if has_email else None,
        "phone": "555-0001",
    }


class TestSearchResultIdsStorage:
    @patch("app.services.search_service.execute", new_callable=AsyncMock)
    @patch("app.services.search_service.fetchrow", new_callable=AsyncMock)
    @patch("app.services.search_service.fetch", new_callable=AsyncMock)
    @patch("app.services.search_service.deduct_credits", new_callable=AsyncMock)
    @patch("app.services.search_service.get_balance", new_callable=AsyncMock)
    @patch("app.services.search_service.geocode", new_callable=AsyncMock)
    @patch("app.services.search_service.resolve_location")
    def test_search_stores_filtered_result_ids(
        self, mock_resolve, mock_geocode, mock_balance, mock_deduct,
        mock_fetch, mock_fetchrow, mock_execute
    ):
        cache_id = uuid.uuid4()
        search_id = uuid.uuid4()
        result_id_1 = uuid.uuid4()
        result_id_2 = uuid.uuid4()
        result_id_3 = uuid.uuid4()

        mock_geocode.return_value = {"lat": 40.7, "lng": -74.0, "country_code": "US"}
        mock_resolve.return_value = {"location_code": 2840, "language_code": "en"}
        # find_cached_scrape returns a cached scrape
        mock_fetchrow.side_effect = [
            {"id": cache_id, "raw_result_count": 3},  # find_cached_scrape
            {"id": search_id},  # INSERT INTO searches RETURNING id
        ]
        # get_cached_results returns 3 results, filter will keep 2
        mock_fetch.return_value = [
            _make_raw_result(result_id_1, has_website=True),
            _make_raw_result(result_id_2, has_website=True),
            _make_raw_result(result_id_3, has_website=False),
        ]
        mock_balance.return_value = 99
        mock_deduct.return_value = 97

        import asyncio
        from app.services.search_service import search

        result = asyncio.get_event_loop().run_until_complete(
            search(MOCK_USER_ID, "plumber", "NYC", filters={"has_website": "yes"})
        )

        # Verify search_result_ids INSERT was called for each filtered result
        execute_calls = [str(c) for c in mock_execute.call_args_list]
        junction_calls = [c for c in execute_calls if "search_result_ids" in c]
        assert len(junction_calls) == 2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_search_result_ids.py -v
```

Expected: FAIL — no `search_result_ids` INSERT in search service yet.

- [ ] **Step 3: Modify search service to store filtered result IDs and respect `force_refresh`**

In `app/services/search_service.py`, update the `search` function signature to accept `force_refresh`:

```python
async def search(user_id, keyword, location, zoom_level=13, near_me=False, filters=None, force_refresh=False):
```

Replace the cache check block (lines 137-138) with:

```python
    cache_key = build_cache_key(keyword, location, zoom_level, near_me, country_code)
    cached = None if force_refresh else await find_cached_scrape(cache_key, CACHE_DURATION_HOURS)
```

After the search record INSERT (after line 181), add the junction table population:

```python
    # 9. Store filtered result IDs for history
    for r in filtered_results:
        await execute("""
            INSERT INTO search_result_ids (search_id, search_result_id)
            VALUES ($1, $2)
        """, search_row["id"], r["id"])
```

- [ ] **Step 4: Update search router to pass `force_refresh`**

In `app/routers/search.py`, update the search call to pass through `force_refresh`:

Read `app/routers/search.py` first, then add `force_refresh=body.force_refresh` to the `search_service.search()` call.

- [ ] **Step 5: Run test to verify it passes**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_search_result_ids.py -v
```

Expected: PASS.

- [ ] **Step 6: Run all tests**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest -v
```

Expected: All PASS.

- [ ] **Step 7: Commit**

```bash
git add app/services/search_service.py app/routers/search.py tests/test_search_result_ids.py
git commit -m "feat: store filtered result IDs in junction table, add force_refresh flag"
```

---

### Task 10: Fix base.html Script Loading

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/templates/app.html`

- [ ] **Step 1: Update `app/templates/base.html` — keep only shared scripts**

Replace the JS modules section (lines 37-48) with:

```html
  <!-- Shared JS modules (safe on all pages) -->
  <script src="/static/js/state.js?v=9"></script>
  <script src="/static/js/i18n.js?v=9"></script>
  <script src="/static/js/theme.js?v=9"></script>

  {% block scripts %}{% endblock %}
```

- [ ] **Step 2: Update `app/templates/app.html` — add page-specific scripts in block**

In `app/templates/app.html`, find the `{% endblock %}` that closes the content block (the last one before `</body>` or end of file), and add a scripts block after it:

```html
{% block scripts %}
  <script src="/static/js/auth.js?v=9"></script>
  <script src="/static/js/map.js?v=9"></script>
  <script src="/static/js/filters.js?v=9"></script>
  <script src="/static/js/table.js?v=9"></script>
  <script src="/static/js/app.js?v=9"></script>
  <script src="/static/js/credits.js?v=9"></script>
{% endblock %}
```

- [ ] **Step 3: Bump cache version across all CSS links in `base.html`**

Update `v=8` to `v=9` in the CSS links in `base.html`.

- [ ] **Step 4: Run existing tests to verify nothing breaks**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest -v
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/base.html app/templates/app.html
git commit -m "refactor: move page-specific scripts to block, keep only shared in base.html"
```

---

### Task 11: Account Page Router + Templates

**Files:**
- Create: `app/routers/account.py`
- Modify: `app/main.py`
- Create: `app/static/css/pages.css`

- [ ] **Step 1: Create account page router**

Create `app/routers/account.py`:

```python
"""Account page routes — serves HTML pages for authenticated users."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.routers.auth import get_current_user, require_current_user

router = APIRouter(tags=["account-pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/account")
async def account_page(request: Request, user: dict = Depends(require_current_user)):
    return templates.TemplateResponse("account.html", {"request": request, "user": user})


@router.get("/billing")
async def billing_page(request: Request, user: dict = Depends(require_current_user)):
    return templates.TemplateResponse("billing.html", {"request": request, "user": user})


@router.get("/history")
async def history_page(request: Request, user: dict = Depends(require_current_user)):
    return templates.TemplateResponse("history.html", {"request": request, "user": user})


@router.get("/history/{search_id}")
async def history_detail_page(request: Request, search_id: str, user: dict = Depends(require_current_user)):
    return templates.TemplateResponse("history_detail.html", {
        "request": request, "user": user, "search_id": search_id,
    })


@router.get("/reset-password")
async def reset_password_page(request: Request):
    """Public page — no auth required. User arrives from email link."""
    return templates.TemplateResponse("reset_password.html", {"request": request})
```

- [ ] **Step 2: Register account router in `app/main.py`**

Add after the search_history router registration:

```python
from app.routers import account
app.include_router(account.router)
```

- [ ] **Step 3: Create shared page styles**

Create `app/static/css/pages.css`:

```css
/* Account pages — shared styles */

.page-container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
    min-height: 100vh;
}

.page-header {
    margin-bottom: var(--space-8);
}

.page-header h1 {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 var(--space-2) 0;
}

.page-header p {
    color: var(--text-secondary);
    margin: 0;
}

.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    margin-bottom: var(--space-6);
}

.card h2 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 var(--space-4) 0;
}

.form-group {
    margin-bottom: var(--space-4);
}

.form-group label {
    display: block;
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: var(--space-1);
}

.form-group input {
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-base);
}

.form-group input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-alpha);
}

.btn-primary {
    background: var(--accent);
    color: white;
    border: none;
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    font-size: var(--text-sm);
}

.btn-primary:hover {
    opacity: 0.9;
}

.btn-danger {
    background: var(--red);
    color: white;
    border: none;
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    font-size: var(--text-sm);
}

.btn-danger:hover {
    opacity: 0.9;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: var(--space-3);
    text-align: left;
    border-bottom: 1px solid var(--border);
    font-size: var(--text-sm);
}

.data-table th {
    font-weight: 600;
    color: var(--text-secondary);
}

.data-table td {
    color: var(--text-primary);
}

.data-table tr:hover td {
    background: var(--bg-hover);
}

.credit-balance {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--accent);
    margin: var(--space-2) 0;
}

.credit-packs {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: var(--space-4);
    margin-top: var(--space-4);
}

.pack-card {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    text-align: center;
}

.pack-card .pack-credits {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--text-primary);
}

.pack-card .pack-price {
    color: var(--accent);
    font-weight: 600;
    margin: var(--space-1) 0;
}

.alert {
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-4);
    font-size: var(--text-sm);
}

.alert-success {
    background: var(--green-alpha);
    color: var(--green);
    border: 1px solid var(--green);
}

.alert-error {
    background: var(--red-alpha);
    color: var(--red);
    border: 1px solid var(--red);
}

.back-link {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    color: var(--text-secondary);
    text-decoration: none;
    font-size: var(--text-sm);
    margin-bottom: var(--space-4);
}

.back-link:hover {
    color: var(--text-primary);
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    gap: var(--space-2);
    margin-top: var(--space-6);
}

.pagination a, .pagination span {
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    text-decoration: none;
}

.pagination a {
    color: var(--text-secondary);
    border: 1px solid var(--border);
}

.pagination a:hover {
    background: var(--bg-hover);
}

.pagination .active {
    background: var(--accent);
    color: white;
    border: 1px solid var(--accent);
}

/* Mobile */
@media (max-width: 640px) {
    .page-container {
        padding: var(--space-4) var(--space-3);
    }

    .credit-packs {
        grid-template-columns: 1fr 1fr;
    }

    .data-table {
        font-size: var(--text-xs);
    }

    .data-table th, .data-table td {
        padding: var(--space-2);
    }
}
```

- [ ] **Step 4: Commit**

```bash
git add app/routers/account.py app/main.py app/static/css/pages.css
git commit -m "feat: add account page router and shared page styles"
```

---

### Task 12: Account Page Template

**Files:**
- Create: `app/templates/account.html`
- Create: `app/static/js/account.js`

- [ ] **Step 1: Create account template**

Create `app/templates/account.html`:

```html
{% extends "base.html" %}

{% block title %}Account — MapSearch{% endblock %}

{% block head %}
<link rel="stylesheet" href="/static/css/pages.css?v=9">
{% endblock %}

{% block content %}
<div class="page-container">
    <a href="/" class="back-link">&larr; Back to MapSearch</a>

    <div class="page-header">
        <h1>Account Settings</h1>
        <p>Manage your account and security</p>
    </div>

    <div id="alert-container"></div>

    <!-- Email -->
    <div class="card">
        <h2>Email</h2>
        <p style="color: var(--text-primary);">{{ user.email }}</p>
    </div>

    <!-- Change Password -->
    <div class="card">
        <h2>Change Password</h2>
        <form id="change-password-form">
            <div class="form-group">
                <label for="current-password">Current Password</label>
                <input type="password" id="current-password" name="current_password" required>
            </div>
            <div class="form-group">
                <label for="new-password">New Password</label>
                <input type="password" id="new-password" name="new_password" minlength="8" required>
            </div>
            <div class="form-group">
                <label for="confirm-password">Confirm New Password</label>
                <input type="password" id="confirm-password" required>
            </div>
            <button type="submit" class="btn-primary">Change Password</button>
        </form>
    </div>

    <!-- Delete Account -->
    <div class="card">
        <h2>Delete Account</h2>
        <p style="color: var(--text-secondary); margin-bottom: var(--space-4);">
            Your account will be deactivated immediately and permanently deleted after 30 days.
            All your search history, credits, and data will be lost.
        </p>
        <button id="delete-account-btn" class="btn-danger">Delete My Account</button>
    </div>

    <!-- Delete Confirmation Modal -->
    <div id="delete-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:1000; display:none; align-items:center; justify-content:center;">
        <div class="card" style="max-width:400px; margin:auto; margin-top:20vh;">
            <h2>Are you sure?</h2>
            <p style="color: var(--text-secondary); margin-bottom: var(--space-4);">
                This action cannot be undone. Your account will be permanently deleted in 30 days.
            </p>
            <div style="display:flex; gap: var(--space-3); justify-content:flex-end;">
                <button id="delete-cancel" class="btn-primary" style="background: var(--bg-tertiary); color: var(--text-primary);">Cancel</button>
                <button id="delete-confirm" class="btn-danger">Yes, Delete My Account</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="/static/js/account.js?v=9"></script>
{% endblock %}
```

- [ ] **Step 2: Create account.js**

Create `app/static/js/account.js`:

```javascript
/* Account page — change password, delete account */

(function () {
  // Change password
  const form = document.getElementById('change-password-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const currentPw = document.getElementById('current-password').value;
      const newPw = document.getElementById('new-password').value;
      const confirmPw = document.getElementById('confirm-password').value;

      if (newPw !== confirmPw) {
        showAlert('Passwords do not match', 'error');
        return;
      }

      try {
        const res = await fetch('/api/auth/password', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('Password changed successfully', 'success');
          form.reset();
        } else {
          showAlert(data.detail || 'Failed to change password', 'error');
        }
      } catch (err) {
        showAlert('Network error', 'error');
      }
    });
  }

  // Delete account
  const deleteBtn = document.getElementById('delete-account-btn');
  const deleteModal = document.getElementById('delete-modal');
  const deleteCancel = document.getElementById('delete-cancel');
  const deleteConfirm = document.getElementById('delete-confirm');

  if (deleteBtn) {
    deleteBtn.addEventListener('click', () => {
      deleteModal.style.display = 'flex';
    });
  }

  if (deleteCancel) {
    deleteCancel.addEventListener('click', () => {
      deleteModal.style.display = 'none';
    });
  }

  if (deleteConfirm) {
    deleteConfirm.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/auth/delete-account', { method: 'POST' });
        if (res.ok) {
          window.location.href = '/';
        } else {
          const data = await res.json();
          showAlert(data.detail || 'Failed to delete account', 'error');
          deleteModal.style.display = 'none';
        }
      } catch (err) {
        showAlert('Network error', 'error');
        deleteModal.style.display = 'none';
      }
    });
  }

  function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    if (!container) return;
    container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => { container.innerHTML = ''; }, 5000);
  }
})();
```

- [ ] **Step 3: Commit**

```bash
git add app/templates/account.html app/static/js/account.js
git commit -m "feat: add account page template with change password and delete account"
```

---

### Task 13: Billing Page Template

**Files:**
- Create: `app/templates/billing.html`

- [ ] **Step 1: Create billing template**

Create `app/templates/billing.html`:

```html
{% extends "base.html" %}

{% block title %}Billing & Credits — MapSearch{% endblock %}

{% block head %}
<link rel="stylesheet" href="/static/css/pages.css?v=9">
{% endblock %}

{% block content %}
<div class="page-container">
    <a href="/" class="back-link">&larr; Back to MapSearch</a>

    <div class="page-header">
        <h1>Billing & Credits</h1>
        <p>Your credit balance and purchase history</p>
    </div>

    <!-- Balance -->
    <div class="card">
        <h2>Credit Balance</h2>
        <div class="credit-balance" id="credit-balance">{{ user.credits_remaining }}</div>
        <p style="color: var(--text-secondary);">credits remaining</p>
    </div>

    <!-- Buy More -->
    <div class="card">
        <h2>Buy Credits</h2>
        <div class="credit-packs">
            <div class="pack-card">
                <div class="pack-credits">1,000</div>
                <div class="pack-price">$1.50</div>
                <button class="btn-primary buy-pack-btn" data-pack="starter">Buy</button>
            </div>
            <div class="pack-card">
                <div class="pack-credits">5,000</div>
                <div class="pack-price">$7.00</div>
                <button class="btn-primary buy-pack-btn" data-pack="growth">Buy</button>
            </div>
            <div class="pack-card">
                <div class="pack-credits">25,000</div>
                <div class="pack-price">$32.00</div>
                <button class="btn-primary buy-pack-btn" data-pack="pro">Buy</button>
            </div>
            <div class="pack-card">
                <div class="pack-credits">100,000</div>
                <div class="pack-price">$120.00</div>
                <button class="btn-primary buy-pack-btn" data-pack="agency">Buy</button>
            </div>
        </div>
    </div>

    <!-- Transaction History -->
    <div class="card">
        <h2>Transaction History</h2>
        <table class="data-table" id="transactions-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Credits</th>
                </tr>
            </thead>
            <tbody id="transactions-body">
                <tr><td colspan="3" style="text-align:center; color: var(--text-secondary);">Loading...</td></tr>
            </tbody>
        </table>
        <div class="pagination" id="txn-pagination"></div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
(function () {
  function renderPagination(containerId, currentPage, total, perPage, loadFn) {
    const container = document.getElementById(containerId);
    const totalPages = Math.ceil(total / perPage);
    if (totalPages <= 1) { container.innerHTML = ''; return; }
    let html = '';
    if (currentPage > 1) html += `<a href="#" data-page="${currentPage - 1}">&laquo; Prev</a>`;
    for (let i = 1; i <= totalPages; i++) {
      if (i === currentPage) html += `<span class="active">${i}</span>`;
      else html += `<a href="#" data-page="${i}">${i}</a>`;
    }
    if (currentPage < totalPages) html += `<a href="#" data-page="${currentPage + 1}">Next &raquo;</a>`;
    container.innerHTML = html;
    container.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', (e) => { e.preventDefault(); loadFn(parseInt(a.dataset.page)); });
    });
  }

  let currentPage = 1;

  async function loadTransactions(page) {
    try {
      const res = await fetch(`/api/credits/transactions?page=${page}`);
      if (!res.ok) return;
      const data = await res.json();
      const tbody = document.getElementById('transactions-body');

      if (data.transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color: var(--text-secondary);">No transactions yet</td></tr>';
        return;
      }

      tbody.innerHTML = data.transactions.map(t => {
        const date = new Date(t.created_at).toLocaleDateString();
        const type = t.type === 'purchase' ? 'Purchase' : 'Search';
        const cls = t.amount > 0 ? 'color: var(--green)' : 'color: var(--red)';
        const sign = t.amount > 0 ? '+' : '';
        return `<tr><td>${date}</td><td>${type}</td><td style="${cls}">${sign}${t.amount}</td></tr>`;
      }).join('');

      currentPage = data.page;
      renderPagination('txn-pagination', data.page, data.total, 50, loadTransactions);
    } catch (err) {
      console.error('Failed to load transactions', err);
    }
  }

  // Buy pack buttons
  document.querySelectorAll('.buy-pack-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const packId = btn.dataset.pack;
      try {
        const res = await fetch('/api/credits/checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pack_id: packId }),
        });
        const data = await res.json();
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } catch (err) {
        console.error('Checkout failed', err);
      }
    });
  });

  loadTransactions(1);
})();
</script>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add app/templates/billing.html
git commit -m "feat: add billing page with credit balance, buy packs, transaction history"
```

---

### Task 14: History Page Template

**Files:**
- Create: `app/templates/history.html`

- [ ] **Step 1: Create history template**

Create `app/templates/history.html`:

```html
{% extends "base.html" %}

{% block title %}Search History — MapSearch{% endblock %}

{% block head %}
<link rel="stylesheet" href="/static/css/pages.css?v=9">
{% endblock %}

{% block content %}
<div class="page-container">
    <a href="/" class="back-link">&larr; Back to MapSearch</a>

    <div class="page-header">
        <h1>Search History</h1>
        <p>Your past searches and results</p>
    </div>

    <div class="card">
        <table class="data-table" id="history-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Keyword</th>
                    <th>Location</th>
                    <th>Results</th>
                    <th>Credits</th>
                    <th></th>
                </tr>
            </thead>
            <tbody id="history-body">
                <tr><td colspan="6" style="text-align:center; color: var(--text-secondary);">Loading...</td></tr>
            </tbody>
        </table>
        <div class="pagination" id="history-pagination"></div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
(function () {
  function renderPagination(containerId, currentPage, total, perPage, loadFn) {
    const container = document.getElementById(containerId);
    const totalPages = Math.ceil(total / perPage);
    if (totalPages <= 1) { container.innerHTML = ''; return; }
    let html = '';
    if (currentPage > 1) html += `<a href="#" data-page="${currentPage - 1}">&laquo; Prev</a>`;
    for (let i = 1; i <= totalPages; i++) {
      if (i === currentPage) html += `<span class="active">${i}</span>`;
      else html += `<a href="#" data-page="${i}">${i}</a>`;
    }
    if (currentPage < totalPages) html += `<a href="#" data-page="${currentPage + 1}">Next &raquo;</a>`;
    container.innerHTML = html;
    container.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', (e) => { e.preventDefault(); loadFn(parseInt(a.dataset.page)); });
    });
  }

  async function loadHistory(page) {
    try {
      const res = await fetch(`/api/searches?page=${page}`);
      if (!res.ok) return;
      const data = await res.json();
      const tbody = document.getElementById('history-body');

      if (data.searches.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-secondary);">No searches yet. Start by searching on the main page!</td></tr>';
        return;
      }

      tbody.innerHTML = data.searches.map(s => {
        const date = new Date(s.created_at).toLocaleDateString();
        return `<tr>
          <td>${date}</td>
          <td>${s.keyword}</td>
          <td>${s.location}</td>
          <td>${s.result_count}</td>
          <td>${s.credits_used}</td>
          <td><a href="/history/${s.id}" style="color: var(--accent);">View</a></td>
        </tr>`;
      }).join('');

      renderPagination('history-pagination', data.page, data.total, 50, loadHistory);
    } catch (err) {
      console.error('Failed to load history', err);
    }
  }

  loadHistory(1);
})();
</script>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add app/templates/history.html
git commit -m "feat: add search history page with keyword, location, result counts"
```

---

### Task 15: History Detail Page Template

**Files:**
- Create: `app/templates/history_detail.html`

- [ ] **Step 1: Create history detail template**

Create `app/templates/history_detail.html`:

```html
{% extends "base.html" %}

{% block title %}Search Results — MapSearch{% endblock %}

{% block head %}
<link rel="stylesheet" href="/static/css/pages.css?v=9">
<link rel="stylesheet" href="/static/css/components.css?v=9">
{% endblock %}

{% block content %}
<div class="page-container" style="max-width: 1200px;">
    <a href="/history" class="back-link">&larr; Back to History</a>

    <div class="page-header" id="search-header">
        <h1>Loading...</h1>
    </div>

    <div style="display: flex; gap: var(--space-3); margin-bottom: var(--space-4);">
        <button id="rerun-btn" class="btn-primary">Re-run Search (Fresh Data)</button>
        <a id="export-link" class="btn-primary" style="background: var(--bg-tertiary); color: var(--text-primary); text-decoration: none;">Export CSV</a>
    </div>

    <!-- Map -->
    <div id="history-map" style="height: 300px; border-radius: var(--radius-lg); margin-bottom: var(--space-4); border: 1px solid var(--border);"></div>

    <!-- Results table -->
    <div class="card" style="overflow-x: auto;">
        <table class="data-table" id="results-table">
            <thead>
                <tr>
                    <th>Business</th>
                    <th>Category</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th>Rating</th>
                    <th>Reviews</th>
                    <th>City</th>
                </tr>
            </thead>
            <tbody id="results-body">
                <tr><td colspan="7" style="text-align:center; color: var(--text-secondary);">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block scripts %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
(function () {
  const searchId = '{{ search_id }}';
  let mapInstance = null;

  async function loadSearchDetail() {
    try {
      const res = await fetch(`/api/searches/${searchId}`);
      if (!res.ok) {
        document.getElementById('search-header').innerHTML = '<h1>Search not found</h1>';
        return;
      }
      const data = await res.json();
      const s = data.search;
      const results = data.results;

      // Header
      document.getElementById('search-header').innerHTML =
        `<h1>"${s.keyword}" in ${s.location}</h1>
         <p>${s.result_count} results &middot; ${s.credits_used} credits &middot; ${new Date(s.created_at).toLocaleDateString()}</p>`;

      // Export link
      document.getElementById('export-link').href = `/api/export/${searchId}`;

      // Re-run button — POST directly to search API with force_refresh
      document.getElementById('rerun-btn').addEventListener('click', async () => {
        const btn = document.getElementById('rerun-btn');
        btn.disabled = true;
        btn.textContent = 'Searching...';
        try {
          const res = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              keyword: s.keyword,
              location: s.location,
              zoom_level: s.zoom_level || 13,
              filters: JSON.parse(s.filters_applied || '{}'),
              force_refresh: true,
            }),
          });
          if (!res.ok) {
            const err = await res.json();
            alert(err.detail || 'Search failed');
            return;
          }
          const newData = await res.json();
          // Redirect to the new search's history detail page
          window.location.href = `/history/${newData.search_id}`;
        } catch (err) {
          alert('Network error');
        } finally {
          btn.disabled = false;
          btn.textContent = 'Re-run Search (Fresh Data)';
        }
      });

      // Map
      if (s.latitude && s.longitude) {
        mapInstance = L.map('history-map').setView([s.latitude, s.longitude], s.zoom_level || 13);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
          attribution: '&copy; OpenStreetMap &copy; CartoDB',
        }).addTo(mapInstance);

        results.forEach(r => {
          if (r.latitude && r.longitude) {
            L.circleMarker([parseFloat(r.latitude), parseFloat(r.longitude)], {
              radius: 5, fillColor: '#10b981', fillOpacity: 0.8, color: '#10b981', weight: 1,
            }).addTo(mapInstance)
              .bindPopup(`<b>${r.business_name || 'Unknown'}</b><br>${r.category || ''}`);
          }
        });
      }

      // Table
      const tbody = document.getElementById('results-body');
      if (results.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No results</td></tr>';
        return;
      }

      tbody.innerHTML = results.map(r => `<tr>
        <td>${r.business_name || '—'}</td>
        <td>${r.category || '—'}</td>
        <td>${r.phone || '—'}</td>
        <td>${r.email || '—'}</td>
        <td>${r.rating || '—'}</td>
        <td>${r.reviews_count || '—'}</td>
        <td>${r.city || '—'}</td>
      </tr>`).join('');

    } catch (err) {
      console.error('Failed to load search detail', err);
    }
  }

  loadSearchDetail();
})();
</script>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add app/templates/history_detail.html
git commit -m "feat: add history detail page with map, results table, re-run button"
```

---

### Task 16: Reset Password Page Template

**Files:**
- Create: `app/templates/reset_password.html`

- [ ] **Step 1: Create reset password template**

Create `app/templates/reset_password.html`:

```html
{% extends "base.html" %}

{% block title %}Reset Password — MapSearch{% endblock %}

{% block head %}
<link rel="stylesheet" href="/static/css/pages.css?v=9">
{% endblock %}

{% block content %}
<div class="page-container" style="max-width: 400px;">
    <div class="page-header" style="text-align: center;">
        <h1>Reset Password</h1>
        <p>Enter your new password</p>
    </div>

    <div id="alert-container"></div>

    <div class="card">
        <form id="reset-password-form">
            <div class="form-group">
                <label for="new-password">New Password</label>
                <input type="password" id="new-password" name="new_password" minlength="8" required>
            </div>
            <div class="form-group">
                <label for="confirm-password">Confirm Password</label>
                <input type="password" id="confirm-password" required>
            </div>
            <button type="submit" class="btn-primary" style="width: 100%;">Reset Password</button>
        </form>
    </div>

    <p style="text-align: center; margin-top: var(--space-4);">
        <a href="/" style="color: var(--accent);">Back to MapSearch</a>
    </p>
</div>
{% endblock %}

{% block scripts %}
<script>
(function () {
  const form = document.getElementById('reset-password-form');
  const alertContainer = document.getElementById('alert-container');

  function showAlert(message, type) {
    alertContainer.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  }

  // Get token from URL
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');

  if (!token) {
    showAlert('Invalid reset link. No token found.', 'error');
    form.style.display = 'none';
    return;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const newPw = document.getElementById('new-password').value;
    const confirmPw = document.getElementById('confirm-password').value;

    if (newPw !== confirmPw) {
      showAlert('Passwords do not match', 'error');
      return;
    }

    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token, new_password: newPw }),
      });
      const data = await res.json();
      if (res.ok) {
        showAlert('Password reset successfully! You can now log in.', 'success');
        form.style.display = 'none';
      } else {
        showAlert(data.detail || 'Reset failed. The link may have expired.', 'error');
      }
    } catch (err) {
      showAlert('Network error', 'error');
    }
  });
})();
</script>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add app/templates/reset_password.html
git commit -m "feat: add reset password page template"
```

---

### Task 17: Update Nav for Logged-in State + Forgot Password Link

**Files:**
- Modify: `app/templates/app.html`

This task requires reading the current `app.html` to find the exact nav HTML and auth modal HTML to modify. The changes are:

- [ ] **Step 1: Read `app/templates/app.html` to find nav and modal sections**

Read the file to identify:
1. The header nav area where "Sign In" button lives
2. The auth modal where "Forgot password?" link should be added
3. The hamburger menu items

- [ ] **Step 2: Add user dropdown to desktop nav**

In the header, after the existing Sign In button, add a user dropdown that's shown when authenticated (JS will toggle visibility):

```html
<!-- User dropdown (shown when logged in) -->
<div id="user-menu" class="user-dropdown" style="display:none;">
    <button id="user-menu-trigger" class="user-menu-btn">
        <span id="user-email-display">Account</span>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M2 4l4 4 4-4"/></svg>
    </button>
    <div id="user-menu-items" class="user-menu-items" style="display:none;">
        <a href="/account">Account</a>
        <a href="/billing">Billing & Credits</a>
        <a href="/history">Search History</a>
        <button id="nav-logout-btn">Sign Out</button>
    </div>
</div>
```

- [ ] **Step 3: Add "Forgot password?" link to auth modal**

In the login form inside the auth modal, add after the password field:

```html
<a href="#" id="forgot-password-link" style="font-size: var(--text-sm); color: var(--accent); display: block; margin-top: var(--space-2);">Forgot password?</a>
```

And add a forgot password form view that's hidden by default:

```html
<div id="forgot-password-view" style="display:none;">
    <h3 style="margin-bottom: var(--space-4);">Reset Password</h3>
    <p style="color: var(--text-secondary); margin-bottom: var(--space-4); font-size: var(--text-sm);">
        Enter your email and we'll send you a reset link.
    </p>
    <div class="form-group">
        <input type="email" id="forgot-email" placeholder="Email" required>
    </div>
    <button id="forgot-submit-btn" class="btn-primary" style="width:100%;">Send Reset Link</button>
    <p id="forgot-message" style="margin-top: var(--space-3); font-size: var(--text-sm);"></p>
    <a href="#" id="back-to-login-link" style="font-size: var(--text-sm); color: var(--accent); display: block; margin-top: var(--space-3);">Back to login</a>
</div>
```

- [ ] **Step 4: Add dropdown styles to `app/static/css/app.css`**

Append to `app/static/css/app.css`:

```css
/* User dropdown */
.user-dropdown {
    position: relative;
}

.user-menu-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    background: transparent;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-1) var(--space-3);
    color: var(--text-primary);
    cursor: pointer;
    font-size: var(--text-sm);
}

.user-menu-items {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: var(--space-1);
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    min-width: 180px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 100;
}

.user-menu-items a,
.user-menu-items button {
    display: block;
    width: 100%;
    padding: var(--space-2) var(--space-3);
    color: var(--text-primary);
    text-decoration: none;
    font-size: var(--text-sm);
    text-align: left;
    background: transparent;
    border: none;
    cursor: pointer;
}

.user-menu-items a:hover,
.user-menu-items button:hover {
    background: var(--bg-hover);
}
```

- [ ] **Step 5: Update `app/static/js/auth.js` for dropdown + forgot password**

Add to `auth.js` — the exact code depends on reading the current file, but the key additions are:

1. On page load, check `/api/auth/me`. If authenticated, hide "Sign In", show user dropdown with email.
2. User dropdown toggle: click trigger → show/hide items. Click outside → close.
3. Forgot password link: hide login form, show forgot-password view.
4. Forgot password submit: POST to `/api/auth/forgot-password`, show success message.
5. Nav logout button: POST to `/api/auth/logout`, reload page.
6. Mobile hamburger menu: add Account/Billing/History links when authenticated.

- [ ] **Step 6: Run all tests**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest -v
```

Expected: All PASS.

- [ ] **Step 7: Commit**

```bash
git add app/templates/app.html app/static/css/app.css app/static/js/auth.js
git commit -m "feat: add logged-in nav dropdown, forgot password link, mobile menu items"
```

---

### Task 18: Update Export Router to Use Junction Table

**Files:**
- Modify: `app/routers/export.py`

- [ ] **Step 1: Update export query to use `search_result_ids` junction table**

In `app/routers/export.py`, replace the results fetch query (lines 39-42):

Old:
```python
    results = await fetch(
        "SELECT * FROM search_results WHERE scrape_cache_id = $1",
        search["scrape_cache_id"]
    )
```

New:
```python
    results = await fetch("""
        SELECT sr.* FROM search_results sr
        JOIN search_result_ids sri ON sr.id = sri.search_result_id
        WHERE sri.search_id = $1
    """, search["id"])
```

- [ ] **Step 2: Run export tests**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest tests/test_export.py -v
```

Expected: PASS (tests mock the fetch call).

- [ ] **Step 3: Commit**

```bash
git add app/routers/export.py
git commit -m "fix: export uses search_result_ids junction table for exact filtered results"
```

---

### Task 19: i18n — Add Translation Keys for All New UI

**Files:**
- Modify: `app/static/i18n/en.json`
- Modify: `app/static/i18n/fr.json`
- Modify: `app/static/i18n/de.json`
- Modify: `app/static/i18n/es.json`

All new templates must use `data-i18n` attributes consistent with the existing i18n system. This task adds the translation keys and updates templates to reference them.

- [ ] **Step 1: Add new keys to `app/static/i18n/en.json`**

Add a new `"account"` section:

```json
"account": {
    "title": "Account Settings",
    "subtitle": "Manage your account and security",
    "email": "Email",
    "changePassword": "Change Password",
    "currentPassword": "Current Password",
    "newPassword": "New Password",
    "confirmPassword": "Confirm New Password",
    "changePasswordBtn": "Change Password",
    "passwordChanged": "Password changed successfully",
    "passwordMismatch": "Passwords do not match",
    "wrongPassword": "Current password is incorrect",
    "deleteAccount": "Delete Account",
    "deleteWarning": "Your account will be deactivated immediately and permanently deleted after 30 days. All your search history, credits, and data will be lost.",
    "deleteConfirmTitle": "Are you sure?",
    "deleteConfirmText": "This action cannot be undone. Your account will be permanently deleted in 30 days.",
    "deleteConfirmBtn": "Yes, Delete My Account",
    "deleteScheduled": "Account scheduled for deletion in 30 days",
    "cancel": "Cancel",
    "backToSearch": "Back to MapSearch"
},
"billing": {
    "title": "Billing & Credits",
    "subtitle": "Your credit balance and purchase history",
    "balance": "Credit Balance",
    "creditsRemaining": "credits remaining",
    "buyCredits": "Buy Credits",
    "transactionHistory": "Transaction History",
    "date": "Date",
    "type": "Type",
    "credits": "Credits",
    "purchase": "Purchase",
    "search": "Search",
    "noTransactions": "No transactions yet"
},
"history": {
    "title": "Search History",
    "subtitle": "Your past searches and results",
    "date": "Date",
    "keyword": "Keyword",
    "location": "Location",
    "results": "Results",
    "credits": "Credits",
    "view": "View",
    "noSearches": "No searches yet. Start by searching on the main page!",
    "rerun": "Re-run Search (Fresh Data)",
    "exportCsv": "Export CSV",
    "backToHistory": "Back to History",
    "searchNotFound": "Search not found",
    "searching": "Searching...",
    "noResults": "No results"
},
"resetPassword": {
    "title": "Reset Password",
    "subtitle": "Enter your new password",
    "newPassword": "New Password",
    "confirmPassword": "Confirm Password",
    "submitBtn": "Reset Password",
    "success": "Password reset successfully! You can now log in.",
    "invalidLink": "Invalid reset link. No token found.",
    "expired": "Reset failed. The link may have expired.",
    "backToHome": "Back to MapSearch"
},
"userMenu": {
    "account": "Account",
    "billing": "Billing & Credits",
    "history": "Search History",
    "signOut": "Sign Out"
}
```

- [ ] **Step 2: Add French translations to `app/static/i18n/fr.json`**

Add the same structure with French values:

```json
"account": {
    "title": "Paramètres du compte",
    "subtitle": "Gérez votre compte et votre sécurité",
    "email": "E-mail",
    "changePassword": "Changer le mot de passe",
    "currentPassword": "Mot de passe actuel",
    "newPassword": "Nouveau mot de passe",
    "confirmPassword": "Confirmer le nouveau mot de passe",
    "changePasswordBtn": "Changer le mot de passe",
    "passwordChanged": "Mot de passe changé avec succès",
    "passwordMismatch": "Les mots de passe ne correspondent pas",
    "wrongPassword": "Le mot de passe actuel est incorrect",
    "deleteAccount": "Supprimer le compte",
    "deleteWarning": "Votre compte sera désactivé immédiatement et définitivement supprimé après 30 jours. Tout votre historique de recherche, vos crédits et vos données seront perdus.",
    "deleteConfirmTitle": "Êtes-vous sûr ?",
    "deleteConfirmText": "Cette action est irréversible. Votre compte sera définitivement supprimé dans 30 jours.",
    "deleteConfirmBtn": "Oui, supprimer mon compte",
    "deleteScheduled": "Compte programmé pour suppression dans 30 jours",
    "cancel": "Annuler",
    "backToSearch": "Retour à MapSearch"
},
"billing": {
    "title": "Facturation et crédits",
    "subtitle": "Votre solde de crédits et historique d'achats",
    "balance": "Solde de crédits",
    "creditsRemaining": "crédits restants",
    "buyCredits": "Acheter des crédits",
    "transactionHistory": "Historique des transactions",
    "date": "Date",
    "type": "Type",
    "credits": "Crédits",
    "purchase": "Achat",
    "search": "Recherche",
    "noTransactions": "Aucune transaction"
},
"history": {
    "title": "Historique des recherches",
    "subtitle": "Vos recherches et résultats passés",
    "date": "Date",
    "keyword": "Mot-clé",
    "location": "Lieu",
    "results": "Résultats",
    "credits": "Crédits",
    "view": "Voir",
    "noSearches": "Aucune recherche. Commencez par chercher sur la page principale !",
    "rerun": "Relancer la recherche (données fraîches)",
    "exportCsv": "Exporter CSV",
    "backToHistory": "Retour à l'historique",
    "searchNotFound": "Recherche introuvable",
    "searching": "Recherche en cours...",
    "noResults": "Aucun résultat"
},
"resetPassword": {
    "title": "Réinitialiser le mot de passe",
    "subtitle": "Entrez votre nouveau mot de passe",
    "newPassword": "Nouveau mot de passe",
    "confirmPassword": "Confirmer le mot de passe",
    "submitBtn": "Réinitialiser le mot de passe",
    "success": "Mot de passe réinitialisé ! Vous pouvez maintenant vous connecter.",
    "invalidLink": "Lien invalide. Aucun jeton trouvé.",
    "expired": "Échec. Le lien a peut-être expiré.",
    "backToHome": "Retour à MapSearch"
},
"userMenu": {
    "account": "Compte",
    "billing": "Facturation et crédits",
    "history": "Historique des recherches",
    "signOut": "Déconnexion"
}
```

- [ ] **Step 3: Add German translations to `app/static/i18n/de.json`**

```json
"account": {
    "title": "Kontoeinstellungen",
    "subtitle": "Verwalten Sie Ihr Konto und Ihre Sicherheit",
    "email": "E-Mail",
    "changePassword": "Passwort ändern",
    "currentPassword": "Aktuelles Passwort",
    "newPassword": "Neues Passwort",
    "confirmPassword": "Neues Passwort bestätigen",
    "changePasswordBtn": "Passwort ändern",
    "passwordChanged": "Passwort erfolgreich geändert",
    "passwordMismatch": "Passwörter stimmen nicht überein",
    "wrongPassword": "Aktuelles Passwort ist falsch",
    "deleteAccount": "Konto löschen",
    "deleteWarning": "Ihr Konto wird sofort deaktiviert und nach 30 Tagen endgültig gelöscht. Ihr gesamter Suchverlauf, Ihre Guthaben und Daten gehen verloren.",
    "deleteConfirmTitle": "Sind Sie sicher?",
    "deleteConfirmText": "Diese Aktion kann nicht rückgängig gemacht werden. Ihr Konto wird in 30 Tagen endgültig gelöscht.",
    "deleteConfirmBtn": "Ja, mein Konto löschen",
    "deleteScheduled": "Konto zur Löschung in 30 Tagen vorgemerkt",
    "cancel": "Abbrechen",
    "backToSearch": "Zurück zu MapSearch"
},
"billing": {
    "title": "Abrechnung & Guthaben",
    "subtitle": "Ihr Guthaben und Kaufhistorie",
    "balance": "Guthaben",
    "creditsRemaining": "Guthaben verbleibend",
    "buyCredits": "Guthaben kaufen",
    "transactionHistory": "Transaktionshistorie",
    "date": "Datum",
    "type": "Typ",
    "credits": "Guthaben",
    "purchase": "Kauf",
    "search": "Suche",
    "noTransactions": "Noch keine Transaktionen"
},
"history": {
    "title": "Suchverlauf",
    "subtitle": "Ihre bisherigen Suchen und Ergebnisse",
    "date": "Datum",
    "keyword": "Suchbegriff",
    "location": "Ort",
    "results": "Ergebnisse",
    "credits": "Guthaben",
    "view": "Anzeigen",
    "noSearches": "Noch keine Suchen. Starten Sie eine Suche auf der Hauptseite!",
    "rerun": "Suche wiederholen (neue Daten)",
    "exportCsv": "CSV exportieren",
    "backToHistory": "Zurück zum Verlauf",
    "searchNotFound": "Suche nicht gefunden",
    "searching": "Suche läuft...",
    "noResults": "Keine Ergebnisse"
},
"resetPassword": {
    "title": "Passwort zurücksetzen",
    "subtitle": "Geben Sie Ihr neues Passwort ein",
    "newPassword": "Neues Passwort",
    "confirmPassword": "Passwort bestätigen",
    "submitBtn": "Passwort zurücksetzen",
    "success": "Passwort zurückgesetzt! Sie können sich jetzt anmelden.",
    "invalidLink": "Ungültiger Link. Kein Token gefunden.",
    "expired": "Fehlgeschlagen. Der Link ist möglicherweise abgelaufen.",
    "backToHome": "Zurück zu MapSearch"
},
"userMenu": {
    "account": "Konto",
    "billing": "Abrechnung & Guthaben",
    "history": "Suchverlauf",
    "signOut": "Abmelden"
}
```

- [ ] **Step 4: Add Spanish translations to `app/static/i18n/es.json`**

```json
"account": {
    "title": "Configuración de cuenta",
    "subtitle": "Administra tu cuenta y seguridad",
    "email": "Correo electrónico",
    "changePassword": "Cambiar contraseña",
    "currentPassword": "Contraseña actual",
    "newPassword": "Nueva contraseña",
    "confirmPassword": "Confirmar nueva contraseña",
    "changePasswordBtn": "Cambiar contraseña",
    "passwordChanged": "Contraseña cambiada exitosamente",
    "passwordMismatch": "Las contraseñas no coinciden",
    "wrongPassword": "La contraseña actual es incorrecta",
    "deleteAccount": "Eliminar cuenta",
    "deleteWarning": "Tu cuenta será desactivada inmediatamente y eliminada permanentemente después de 30 días. Todo tu historial de búsqueda, créditos y datos se perderán.",
    "deleteConfirmTitle": "¿Estás seguro?",
    "deleteConfirmText": "Esta acción no se puede deshacer. Tu cuenta será eliminada permanentemente en 30 días.",
    "deleteConfirmBtn": "Sí, eliminar mi cuenta",
    "deleteScheduled": "Cuenta programada para eliminación en 30 días",
    "cancel": "Cancelar",
    "backToSearch": "Volver a MapSearch"
},
"billing": {
    "title": "Facturación y créditos",
    "subtitle": "Tu saldo de créditos e historial de compras",
    "balance": "Saldo de créditos",
    "creditsRemaining": "créditos restantes",
    "buyCredits": "Comprar créditos",
    "transactionHistory": "Historial de transacciones",
    "date": "Fecha",
    "type": "Tipo",
    "credits": "Créditos",
    "purchase": "Compra",
    "search": "Búsqueda",
    "noTransactions": "Sin transacciones aún"
},
"history": {
    "title": "Historial de búsquedas",
    "subtitle": "Tus búsquedas y resultados anteriores",
    "date": "Fecha",
    "keyword": "Palabra clave",
    "location": "Ubicación",
    "results": "Resultados",
    "credits": "Créditos",
    "view": "Ver",
    "noSearches": "Sin búsquedas aún. ¡Empieza buscando en la página principal!",
    "rerun": "Repetir búsqueda (datos frescos)",
    "exportCsv": "Exportar CSV",
    "backToHistory": "Volver al historial",
    "searchNotFound": "Búsqueda no encontrada",
    "searching": "Buscando...",
    "noResults": "Sin resultados"
},
"resetPassword": {
    "title": "Restablecer contraseña",
    "subtitle": "Ingresa tu nueva contraseña",
    "newPassword": "Nueva contraseña",
    "confirmPassword": "Confirmar contraseña",
    "submitBtn": "Restablecer contraseña",
    "success": "¡Contraseña restablecida! Ya puedes iniciar sesión.",
    "invalidLink": "Enlace inválido. No se encontró token.",
    "expired": "Falló. El enlace puede haber expirado.",
    "backToHome": "Volver a MapSearch"
},
"userMenu": {
    "account": "Cuenta",
    "billing": "Facturación y créditos",
    "history": "Historial de búsquedas",
    "signOut": "Cerrar sesión"
}
```

- [ ] **Step 5: Update all templates to use `data-i18n` attributes**

In each new template, replace hard-coded strings with `data-i18n` attributes. Example for `account.html`:
- `<h1>Account Settings</h1>` → `<h1 data-i18n="account.title">Account Settings</h1>`
- `<p>Manage your account and security</p>` → `<p data-i18n="account.subtitle">Manage your account and security</p>`
- Labels, buttons, warnings all get `data-i18n` attributes with English as fallback text content.

Apply the same pattern to `billing.html`, `history.html`, `history_detail.html`, `reset_password.html`, and the nav dropdown in `app.html`.

- [ ] **Step 6: Commit**

```bash
git add app/static/i18n/ app/templates/
git commit -m "feat: add i18n translations for account pages, nav, password reset (EN/FR/DE/ES)"
```

---

### Task 20: Final Integration Test

**Files:** None new — verification only.

- [ ] **Step 1: Run full test suite**

```bash
cd /Users/peterhadorn/Documents/GitHub/mapsearch-app && python3 -m pytest -v
```

Expected: All tests PASS.

- [ ] **Step 2: Update CHANGELOG.md**

Add at the top of CHANGELOG.md:

```markdown
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
```

- [ ] **Step 3: Add `APP_BASE_URL` to `.env.example`**

Add to `.env.example`:
```
APP_BASE_URL=https://mapsearch.app
```

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md .env.example
git commit -m "docs: update changelog for v0.4.0 — login area, account pages, password reset"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Database schema changes | schema.sql |
| 2 | Soft-delete auth guards | queries.py, conftest.py, test_account.py |
| 3 | Config + request models | config.py, request_models.py |
| 4 | Email service | email_service.py, test_password_reset.py |
| 5 | Password reset endpoints | queries.py, auth.py, test_password_reset.py |
| 6 | Change password + delete tests | test_account.py |
| 7 | Credit transactions endpoint | queries.py, credits.py, test_history.py |
| 8 | Search history API | queries.py, search_history.py, main.py, test_history.py |
| 9 | Store filtered result IDs | search_service.py, search.py, test_search_result_ids.py |
| 10 | Fix base.html scripts | base.html, app.html |
| 11 | Account router + page CSS | account.py, main.py, pages.css |
| 12 | Account page template | account.html, account.js |
| 13 | Billing page template | billing.html |
| 14 | History page template | history.html |
| 15 | History detail template | history_detail.html |
| 16 | Reset password template | reset_password.html |
| 17 | Nav dropdown + forgot password | app.html, app.css, auth.js |
| 18 | Export uses junction table | export.py |
| 19 | i18n translations for new UI | en/fr/de/es.json, all templates |
| 20 | Final integration + changelog | CHANGELOG.md |
