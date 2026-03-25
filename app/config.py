"""MapSearch configuration — all settings from environment variables."""

import os

DATAFORSEO_LOGIN = os.environ["DATAFORSEO_LOGIN"]
DATAFORSEO_PASSWORD = os.environ["DATAFORSEO_PASSWORD"]
DATABASE_URL = os.environ["MAPSEARCH_DATABASE_URL"]
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
SECRET_KEY = os.environ["MAPSEARCH_SECRET_KEY"]

SIGNUP_BONUS_CREDITS = 99
CACHE_DURATION_HOURS = 72
DATAFORSEO_MAX_DEPTH = 700

ZOOM_LEVELS = {
    14: {"label": "Neighborhood", "miles": "~3 mi", "km": "~5 km"},
    13: {"label": "District", "miles": "~6 mi", "km": "~10 km"},
    12: {"label": "City", "miles": "~12 mi", "km": "~20 km"},
    11: {"label": "Metro", "miles": "~25 mi", "km": "~40 km"},
}

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 168  # 7 days
JWT_COOKIE_NAME = "mapsearch_session"
