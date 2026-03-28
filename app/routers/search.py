"""Search router — POST /api/search endpoint."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from app.limiter import limiter
from app.routers.auth import require_current_user
from app.models.request_models import SearchRequest
from app.services.search_service import search, InsufficientCreditsError

logger = logging.getLogger("mapsearch.search")

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search")
@limiter.limit("10/minute")
async def search_endpoint(request: Request, body: SearchRequest, user: dict = Depends(require_current_user)):
    try:
        result = await search(
            user_id=user["id"],
            keyword=body.keyword,
            location=body.location,
            zoom_level=body.zoom_level,
            near_me=body.near_me,
            filters=body.filters,
            force_refresh=body.force_refresh,
        )
        return result
    except InsufficientCreditsError as e:
        return {
            "insufficient_credits": True,
            "needed": e.needed,
            "available": e.available,
            "results": [],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
