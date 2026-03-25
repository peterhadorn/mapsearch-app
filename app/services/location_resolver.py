"""Map country codes to DataForSEO location_codes and language_codes."""

# Top 20 countries — extend from DataForSEO /v3/serp/google/locations/ (free endpoint)
LOCATION_CODES = {
    "US": 2840, "GB": 2826, "DE": 2276, "FR": 2250, "CH": 2756,
    "AT": 2040, "IT": 2380, "ES": 2724, "NL": 2528, "BE": 2056,
    "CA": 2124, "AU": 2036, "BR": 2076, "MX": 2484, "IN": 2356,
    "JP": 2392, "KR": 2410, "SE": 2752, "NO": 2578, "DK": 2208,
}

LANGUAGE_CODES = {
    "US": "en", "GB": "en", "DE": "de", "FR": "fr", "CH": "de",
    "AT": "de", "IT": "it", "ES": "es", "NL": "nl", "BE": "fr",
    "CA": "en", "AU": "en", "BR": "pt", "MX": "es", "IN": "en",
    "JP": "ja", "KR": "ko", "SE": "sv", "NO": "no", "DK": "da",
}


def resolve_location(country_code: str) -> dict:
    """Return DataForSEO location_code and language_code for a country."""
    code = country_code.upper()
    return {
        "location_code": LOCATION_CODES.get(code, 2840),
        "language_code": LANGUAGE_CODES.get(code, "en"),
    }
