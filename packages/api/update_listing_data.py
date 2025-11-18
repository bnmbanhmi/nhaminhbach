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

@app.route('/api/update_listing_data', methods=['POST'])
def update_listing_data():
    """
    API Endpoint to update listing data and approve it.
    POST request with JSON body containing listing fields and optional attributes.
    """
    try:
        payload = request.get_json()
        if not payload:
            return Response("Invalid JSON payload.", status=400)

        listing_id = payload.get("listing_id")
        listing_data = payload.get("listing", {})
        attributes_data = payload.get("attributes", [])

        if not listing_id:
            return Response("Missing listing_id in payload.", status=400)

        supabase_client = get_supabase_client()
        
        # First check if listing exists and is in pending_review status
        response = supabase_client.table('listings').select('status, address_street, address_ward, address_district').eq('id', listing_id).single().execute()
        
        if not response.data:
            return Response("Listing not found.", status=404)
            
        if response.data['status'] != "pending_review":
            return Response(f"Listing is not in pending_review status (current: {response.data['status']}).", status=400)

        # Update listing core fields
        update_payload = {}
        
        allowed_fields = ["title", "description", "price_monthly_vnd", "area_m2", 
                        "address_street", "address_ward", "address_district", "contact_phone"]
        
        for field in allowed_fields:
            if field in listing_data and listing_data[field] is not None:
                update_payload[field] = listing_data[field]
        
        # Check if any address fields were updated and perform geocoding
        address_fields = ["address_street", "address_ward", "address_district"]
        if any(field in listing_data for field in address_fields):
            street = listing_data.get("address_street") or response.data.get("address_street") or ""
            ward = listing_data.get("address_ward") or response.data.get("address_ward") or ""
            district = listing_data.get("address_district") or response.data.get("address_district") or ""
            
            address_parts = [part for part in [street, ward, district] if part and part.strip()]
            if address_parts:
                full_address = ", ".join(address_parts) + ", Hà Nội, Vietnam"
                
                GCP_PROJECT = os.environ.get("GCP_PROJECT", "omega-sorter-467514-q6")
                coords = geocode_address(GCP_PROJECT, full_address)
                
                if coords:
                    lat, lng = coords
                    update_payload["latitude"] = lat
                    update_payload["longitude"] = lng

        if update_payload:
            update_payload["status"] = "available"
            supabase_client.table('listings').update(update_payload).eq('id', listing_id).execute()
        else:
            # Just update status to available if no fields to update
            supabase_client.table('listings').update({"status": "available"}).eq('id', listing_id).execute()

        # TODO: Implement attribute updates if needed

        return Response(
            json.dumps({"message": "Listing updated and approved", "listing_id": listing_id}),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Error in update_listing_data: {e}")
        return Response(f"Internal server error: {str(e)}", status=500)

# Vercel expects a handler variable
handler = app
