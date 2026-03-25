"""Pydantic request models for MapSearch API."""

from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str  # min 8 chars validated in endpoint


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
