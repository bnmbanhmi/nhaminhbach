"""
Utility functions for the NhaMinhBach backend.
"""

import logging
from typing import Optional
import time
import hashlib
import requests
from typing import Tuple, Dict, Any

from google.cloud import secretmanager
from google.api_core import exceptions as gcp_exceptions

logger = logging.getLogger(__name__)


def get_secret(project_id: str, secret_id: str) -> str:
    """
    Fetch the latest version of a secret from Google Secret Manager.
    
    Args:
        project_id: The GCP project ID where the secret is stored.
        secret_id: The ID/name of the secret to retrieve.
    
    Returns:
        The secret value as a UTF-8 decoded string.
    
    Raises:
        ValueError: If project_id or secret_id is empty.
        RuntimeError: If the secret cannot be accessed due to permissions, 
                     not found, or other GCP errors.
    """
    if not project_id or not project_id.strip():
        raise ValueError("project_id cannot be empty")
    
    if not secret_id or not secret_id.strip():
        raise ValueError("secret_id cannot be empty")
    
    try:
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name for the latest version of the secret
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        logger.debug(f"Accessing secret: {name}")
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Decode the secret payload from bytes to UTF-8 string
        secret_value = response.payload.data.decode("utf-8")
        
        logger.debug(f"Successfully retrieved secret: {secret_id}")
        return secret_value
        
    except gcp_exceptions.NotFound as e:
        error_msg = f"Secret '{secret_id}' not found in project '{project_id}'"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    except gcp_exceptions.PermissionDenied as e:
        error_msg = f"Permission denied accessing secret '{secret_id}' in project '{project_id}'"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    except gcp_exceptions.Unauthenticated as e:
        error_msg = f"Authentication failed when accessing secret '{secret_id}'"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    except Exception as e:
        error_msg = f"Unexpected error accessing secret '{secret_id}': {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_secret_or_env(project_id: str, secret_id: str, env_var_name: Optional[str] = None) -> str:
    """
    Convenience function that tries to get a secret from Secret Manager first,
    and falls back to an environment variable if specified.
    
    Args:
        project_id: The GCP project ID where the secret is stored.
        secret_id: The ID/name of the secret to retrieve.
        env_var_name: Optional environment variable name to fall back to.
    
    Returns:
        The secret value as a string.
    
    Raises:
        RuntimeError: If neither the secret nor the environment variable is available.
    """
    import os
    
    try:
        return get_secret(project_id, secret_id)
    except RuntimeError as e:
        if env_var_name:
            env_value = os.environ.get(env_var_name)
            if env_value:
                logger.warning(f"Using environment variable '{env_var_name}' as fallback for secret '{secret_id}'")
                return env_value
        
        # If we get here, neither secret nor env var worked
        raise RuntimeError(f"Could not retrieve secret '{secret_id}' from Secret Manager and no fallback available") from e


# Simple in-memory cache for geocoding results to reduce external API calls.
# This is process-local and suitable for short-lived caching in Cloud Functions.
_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}
_GEOCODE_TTL_SECONDS = 60 * 60 * 24  # 24 hours


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
    """Geocode the given address string using Google Maps Geocoding API.

    Returns (lat, lng) on success, or None on failure. Uses Secret Manager to fetch the
    'google-maps-api-key' secret. Caches responses for a TTL to limit external calls.
    """
    if not address or not address.strip():
        return None

    # Use a normalized cache key
    key = hashlib.sha256(address.strip().lower().encode("utf-8")).hexdigest()
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        api_key = get_secret_or_env(project_id, "google-maps-api-key", env_var_name="GOOGLE_MAPS_API_KEY")
    except RuntimeError:
        logger.warning("Google Maps API key not available; skipping geocoding")
        return None

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
            return (lat, lng)
        else:
            logger.warning(f"Geocoding failed for address '{address}': {data.get('status')} - {data.get('error_message')}")
            return None
    except Exception as e:
        logger.error(f"Exception during geocoding for '{address}': {e}")
        return None
