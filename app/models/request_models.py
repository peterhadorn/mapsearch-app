"""Pydantic request models for MapSearch API."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class SearchRequest(BaseModel):
    keyword: str = Field(max_length=255)
    location: str = Field(max_length=255)
    zoom_level: int = Field(default=13, ge=11, le=14)
    near_me: bool = False
    filters: dict = {}
