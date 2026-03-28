"""Auth router — signup, login, logout, me endpoints with JWT in httpOnly cookies."""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_COOKIE_NAME, APP_BASE_URL
from app.database import queries
from app.limiter import limiter
from app.models.request_models import SignupRequest, LoginRequest, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.services.email_service import send_reset_email

logger = logging.getLogger("mapsearch.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_secure = os.environ.get("MAPSEARCH_ENV", "production") != "test"


def _create_token(user_id: str) -> str:
    """Create a signed JWT for the authenticated user.

    Args:
        user_id: Authenticated user identifier.

    Returns:
        str: Encoded JWT session token.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=JWT_ALGORITHM)


def _set_session_cookie(response: Response, token: str):
    """Attach the session cookie to an HTTP response.

    Args:
        response: Response object to mutate.
        token: Encoded JWT session token.

    Returns:
        None
    """
    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=_secure,
        samesite="lax",
        max_age=JWT_EXPIRE_HOURS * 3600,
    )


async def get_current_user(request: Request):
    """Read JWT from cookie, decode, fetch user from DB. Returns user dict or None."""
    token = request.cookies.get(JWT_COOKIE_NAME)
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    user = await queries.get_user_by_id(UUID(user_id))
    if user is None:
        return None
    return dict(user)


async def require_current_user(request: Request):
    """FastAPI dependency — returns current user or raises 401."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.post("/signup", status_code=201)
@limiter.limit("5/minute")
async def signup(request: Request, body: SignupRequest, response: Response):
    existing = await queries.get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = pwd_context.hash(body.password)
    user = await queries.create_user(email=body.email, password_hash=password_hash)

    token = _create_token(str(user["id"]))
    _set_session_cookie(response, token)

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "credits_remaining": user["credits_remaining"],
        "locale": user["locale"],
    }


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, response: Response):
    user = await queries.get_user_by_email(body.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_token(str(user["id"]))
    _set_session_cookie(response, token)

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "credits_remaining": user["credits_remaining"],
        "locale": user["locale"],
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=JWT_COOKIE_NAME)
    return {"message": "Logged out"}


@router.get("/me")
async def me(user: dict = Depends(require_current_user)):
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "credits_remaining": user["credits_remaining"],
        "locale": user["locale"],
    }


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
