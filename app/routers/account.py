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
