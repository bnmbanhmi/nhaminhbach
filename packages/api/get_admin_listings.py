import os
import json
from decimal import Decimal
from typing import Any
from datetime import datetime
import uuid

from flask import Flask, Response, request
from supabase import create_client, Client
from dotenv import load_dotenv

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

@app.route('/api/get_admin_listings', methods=['GET'])
def get_admin_listings():
    """API Endpoint for admin dashboard to get listings with filtering by status."""
    try:
        # Get query parameters for filtering
        status = request.args.get("status")  # Can be 'pending_review', 'available', 'rejected', 'rented'
        district = request.args.get("district")
        limit = int(request.args.get("limit", "50"))  # Default to 50 listings
        offset = int(request.args.get("offset", "0"))  # For pagination

        supabase_client = get_supabase_client()
        
        query = supabase_client.table('listings').select('*, attributes:listing_attributes(*)', count='exact').order('created_at', desc=True).range(offset, offset + limit - 1)

        if status:
            query = query.eq('status', status)
        
        if district:
            query = query.ilike('address_district', f'%{district}%')

        response = query.execute()

        response_data = {
            "listings": response.data,
            "pagination": {
                "total": response.count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < response.count
            }
        }

        json_response = json.dumps(response_data, default=default_json_serializer)
        return Response(json_response, status=200, mimetype="application/json")

    except Exception as e:
        print(f"Error in get_admin_listings: {e}")
        return Response("An internal server error occurred.", status=500)

# Vercel expects a handler variable
handler = app
