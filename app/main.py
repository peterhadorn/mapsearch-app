"""MapSearch.app — main FastAPI application."""

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("mapsearch")

app = FastAPI(title="MapSearch", docs_url=None, redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(CORSMiddleware, allow_origins=["https://mapsearch.app", "https://mapsearch.allwk.com"], allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

from app.routers import auth
app.include_router(auth.router)

from app.routers import search
app.include_router(search.router)

from app.routers import credits
app.include_router(credits.router)

from app.routers import pages
app.include_router(pages.router)

from app.routers import export
app.include_router(export.router)


@app.on_event("startup")
async def startup_purge():
    """Purge users who were soft-deleted more than 30 days ago."""
    from app.database import queries
    await queries.purge_deleted_users()


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
