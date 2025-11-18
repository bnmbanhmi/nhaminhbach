"""
Utility functions for the NhaMinhBach backend.
"""

import logging
import os
from typing import Optional
import time
import hashlib
import requests
from typing import Tuple, Dict, Any
import threading

# Use standard Python logging instead of firebase_functions logger
logger = logging.getLogger(__name__)


# Simple in-memory cache for geocoding results to reduce external API calls.
# This is process-local and suitable for short-lived caching in Cloud Functions.
_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}
_GEOCODE_TTL_SECONDS = 60 * 60 * 24  # 24 hours

# Nominatim rate limiting (1 request per second) - process local
_NOMINATIM_LAST_CALL = 0.0
_NOMINATIM_LOCK = threading.Lock()


def _cache_get(key: str):
    rec = _GEOCODE_CACHE.get(key)
    if not rec:
        return None
    if time.time() - rec["ts"] > _GEOCODE_TTL_SECONDS:
        del _GEOCODE_CACHE[key]
        return None
    return rec["value"]


def _cache_set(key: str, value: Any):
    _GEOCODE_CACHE[key] = {"ts": time.time(), "value": value}


def geocode_address(project_id: str, address: str) -> Optional[Tuple[float, float]]:
    """Geocode the given address string using Google Maps first, then OSM Nominatim as fallback.

    Returns (lat, lng) on success, or None on failure. Uses Secret Manager to fetch the
    'google-maps-api-key' secret when available. Caches successful responses for a TTL
    to limit external calls. Logs which provider returned the result.
    """
    global _NOMINATIM_LAST_CALL

    if not address or not address.strip():
        return None

    # Use a normalized cache key
    key = hashlib.sha256(address.strip().lower().encode("utf-8")).hexdigest()
    cached = _cache_get(key)
    if cached:
        logger.debug(f"Geocode cache hit for address: {address}")
        return cached

    # First attempt: Google Maps (if API key available)
    # In a Supabase environment, the API key should be an environment variable
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

    if api_key:
        params = {"address": address, "key": api_key}
        try:
            resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                lat = float(loc.get("lat"))
                lng = float(loc.get("lng"))
                _cache_set(key, (lat, lng))
                logger.info(f"Geocoded address with Google Maps: {address} -> ({lat}, {lng})")
                return (lat, lng)
            else:
                logger.info(f"Google Maps geocoding returned status {data.get('status')} for '{address}'")
        except Exception as e:
            logger.warning(f"Google Maps geocoding exception for '{address}': {e}")

    # Fallback: OSM Nominatim
    # Respect Nominatim usage policy: max 1 request per second per process and polite User-Agent
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": f"nhaminhbach/{project_id} (+https://nhaminhbach.com)"
    }
    params = {"q": address, "format": "json", "limit": 1, "addressdetails": 0}

    # Exponential backoff attempts
    backoff_seconds = [1, 2, 4]
    for attempt, backoff in enumerate(backoff_seconds, start=1):
        # Rate limiting: ensure at least 1s since last call
        with _NOMINATIM_LOCK:
            elapsed = time.time() - _NOMINATIM_LAST_CALL
            if elapsed < 1.0:
                to_sleep = 1.0 - elapsed
                logger.debug(f"Sleeping {to_sleep:.2f}s to respect Nominatim rate limit")
                time.sleep(to_sleep)
            _NOMINATIM_LAST_CALL = time.time()

        try:
            resp = requests.get(nominatim_url, params=params, headers=headers, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                item = data[0]
                lat = float(item.get("lat"))
                lng = float(item.get("lon"))
                _cache_set(key, (lat, lng))
                logger.info(f"Geocoded address with Nominatim: {address} -> ({lat}, {lng}) [attempt {attempt}]")
                return (lat, lng)
            else:
                logger.info(f"Nominatim returned no results for '{address}' on attempt {attempt}")
        except requests.HTTPError as e:
            # If we got a 429 or other server-side error, backoff and retry
            logger.warning(f"Nominatim HTTP error for '{address}' on attempt {attempt}: {e}")
        except Exception as e:
            logger.warning(f"Nominatim exception for '{address}' on attempt {attempt}: {e}")

        # Backoff before next attempt
        logger.debug(f"Backing off for {backoff}s before Nominatim retry")
        time.sleep(backoff)

    # If we get here, all providers failed
    logger.error(f"Failed to geocode address with both Google Maps and Nominatim: '{address}'")
    return None
