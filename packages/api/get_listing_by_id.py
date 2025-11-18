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

@app.route('/api/get_listing_by_id', methods=['GET'])
def get_listing_by_id():
    """Get a specific listing by its ID (UUID)."""
    try:
        listing_id_str = request.args.get("id")
        if not listing_id_str:
            return Response("Missing 'id' query parameter.", status=400)

        try:
            listing_id = uuid.UUID(listing_id_str)
        except ValueError:
            return Response(f"Invalid 'id' format. Must be a valid UUID.", status=400)

        supabase_client = get_supabase_client()
        
        response = supabase_client.table('listings').select('*, attributes:listing_attributes(*)').eq('id', str(listing_id)).single().execute()

        if not response.data:
            return Response(f"Listing with ID {listing_id} not found.", status=404)

        listing_data = response.data
        json_response = json.dumps(listing_data, default=default_json_serializer)

        return Response(json_response, status=200, mimetype="application/json")

    except Exception as e:
        print(f"Error fetching listing ID {listing_id_str}: {e}")
        return Response("An internal server error occurred.", status=500)

# Vercel expects a handler variable
handler = app
