"""Auth router — signup, login, logout, me, Google OAuth2 endpoints with JWT in httpOnly cookies."""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import (
    SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_COOKIE_NAME,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
)
from app.database import queries
from app.limiter import limiter
from app.models.request_models import SignupRequest, LoginRequest

logger = logging.getLogger("mapsearch.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

_secure = os.environ.get("MAPSEARCH_ENV", "production") != "test"


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=JWT_ALGORITHM)


def _set_session_cookie(response: Response, token: str):
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


@router.get("/google")
async def google_login(request: Request):
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": "https://mapsearch.app/api/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        "oauth_state", state, httponly=True, samesite="lax",
        secure=_secure, max_age=600,
    )
    return response


@router.get("/google/callback")
async def google_callback(request: Request, code: str, state: str):
    # Validate state matches cookie (CSRF prevention)
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": "https://mapsearch.app/api/auth/google/callback",
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")
        tokens = token_resp.json()

        # Get user info
        userinfo_resp = await client.get(GOOGLE_USERINFO_URL, headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        userinfo = userinfo_resp.json()

    email = userinfo["email"]
    name = userinfo.get("name", "")
    google_id = userinfo["sub"]

    # Find or create user
    user = await queries.get_user_by_google_id(google_id)
    if not user:
        user = await queries.get_user_by_email(email)
        if user:
            # Link Google to existing email account
            await queries.link_google_id(user["id"], google_id)
        else:
            # New user
            user = await queries.create_user(
                email=email, password_hash=None, name=name, google_id=google_id,
            )

    # Set session cookie and redirect to home
    token = _create_token(str(user["id"]))
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        JWT_COOKIE_NAME, token, httponly=True, samesite="lax",
        secure=_secure, max_age=JWT_EXPIRE_HOURS * 3600,
    )
    response.delete_cookie("oauth_state")
    return response
