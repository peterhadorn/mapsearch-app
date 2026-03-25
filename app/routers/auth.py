"""Auth router — signup, login, logout, me endpoints with JWT in httpOnly cookies."""

import logging
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_COOKIE_NAME
from app.database import queries
from app.limiter import limiter
from app.models.request_models import SignupRequest, LoginRequest

logger = logging.getLogger("mapsearch.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=JWT_ALGORITHM)


def _set_session_cookie(response: Response, token: str):
    secure = os.environ.get("MAPSEARCH_ENV", "production") != "test"
    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=secure,
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
