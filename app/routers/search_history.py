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
