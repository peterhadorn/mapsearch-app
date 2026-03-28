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

    return templates.TemplateResponse(request, "admin.html", {
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
