import os
import json
from decimal import Decimal
from typing import Any
from datetime import datetime
import uuid

from flask import Flask, Response, request
from supabase import create_client, Client
from dotenv import load_dotenv

from utils import geocode_address

load_dotenv()

app = Flask(__name__)

# =================================================================================
#  1. GLOBAL SETUP & CONFIGURATION
# =================================================================================

supabase: Client = None

# =================================================================================
#  2. CLIENT INITIALIZATION
# =================================================================================

def get_supabase_client() -> Client:
    global supabase
    if supabase is not None:
        return supabase

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)
    return supabase

# =================================================================================
#  3. UTILITY FUNCTIONS
# =================================================================================

def default_json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime, uuid.UUID)):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# =================================================================================
#  4. API ENDPOINTS
# =================================================================================

@app.route('/api/geocode_existing_listings', methods=['POST'])
def geocode_existing_listings():
    """
    Geocode existing listings that have address data but missing latitude/longitude.
    This is useful for backfilling existing data or re-geocoding after address updates.
    """
    try:
        payload = request.get_json() or {}
        limit = min(int(payload.get("limit", 50)), 100)  # Limit to prevent timeout
        
        supabase_client = get_supabase_client()
        
        # Find listings with address data but no coordinates
        response = supabase_client.table('listings').select('id, address_street, address_ward, address_district').is_('latitude', 'is', None).limit(limit).execute()
        
        listings = response.data
        
        if not listings:
            return Response(
                json.dumps({"message": "No listings found that need geocoding", "geocoded": 0}),
                status=200,
                mimetype="application/json"
            )
        
        geocoded_count = 0
        failed_count = 0
        
        for listing in listings:
            listing_id = listing.get("id")
            street = listing.get("address_street") or ""
            ward = listing.get("address_ward") or ""
            district = listing.get("address_district") or ""
            
            address_parts = [part for part in [street, ward, district] if part and part.strip()]
            if not address_parts:
                continue
            
            full_address = ", ".join(address_parts) + ", Hà Nội, Vietnam"
            
            GCP_PROJECT = os.environ.get("GCP_PROJECT", "omega-sorter-467514-q6")
            coords = geocode_address(GCP_PROJECT, full_address)
            
            if coords:
                lat, lng = coords
                supabase_client.table('listings').update({'latitude': lat, 'longitude': lng}).eq('id', listing_id).execute()
                geocoded_count += 1
            else:
                failed_count += 1
        
        return Response(
            json.dumps({
                "message": "Geocoding complete",
                "processed": len(listings),
                "geocoded": geocoded_count,
                "failed": failed_count
            }),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Error in geocode_existing_listings: {e}")
        return Response(f"Internal server error: {str(e)}", status=500)

# Vercel expects a handler variable
handler = app
