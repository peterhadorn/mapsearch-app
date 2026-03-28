"""Export router — CSV download for search results."""

import csv
import io
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.routers.auth import require_current_user
from app.database.connection import fetchrow, fetch, execute

logger = logging.getLogger("mapsearch.export")

router = APIRouter(prefix="/api", tags=["export"])

CSV_COLUMNS = [
    "business_name", "category", "address", "city", "state", "zip", "country",
    "phone", "email", "domain", "url", "rating", "reviews_count",
    "is_claimed", "verified", "photos_count", "latitude", "longitude",
    "google_maps_url", "price_level", "business_status",
]


@router.get("/export/{search_id}")
async def export_csv(search_id: str, user: dict = Depends(require_current_user)):
    """Export search results as CSV. Free — no additional credits."""

    # SECURITY: Ownership check — return 404 (not 403) to avoid confirming existence
    search = await fetchrow(
        "SELECT id, scrape_cache_id, filtered_result_count FROM searches WHERE id = $1 AND user_id = $2",
        UUID(search_id), user["id"]
    )
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    # Fetch exact filtered results via junction table
    results = await fetch("""
        SELECT sr.* FROM search_results sr
        JOIN search_result_ids sri ON sr.id = sri.search_result_id
        WHERE sri.search_id = $1
    """, search["id"])

    # Generate CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, extrasaction='ignore')
    writer.writeheader()
    for row in results:
        writer.writerow(dict(row))

    # Log export
    await execute("""
        INSERT INTO exports (user_id, search_id, row_count, filters_applied)
        VALUES ($1, $2, $3, $4)
    """, user["id"], search["id"], len(results), None)

    # Stream response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=mapsearch-{search_id}.csv"}
    )
