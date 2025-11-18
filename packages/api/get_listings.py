import os
import json
from decimal import Decimal
from typing import Any
from datetime import datetime
import uuid

from flask import Flask, Response
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

@app.route('/api/get_listings', methods=['GET'])
def get_listings():
    """API Endpoint to get all available listings."""
    try:
        supabase_client = get_supabase_client()
        response = supabase_client.table('listings').select('*, attributes:listing_attributes(*)').eq('status', 'available').execute()
        
        listings_data = response.data
        json_response = json.dumps(listings_data, default=default_json_serializer)

        return Response(json_response, status=200, mimetype="application/json")

    except Exception as e:
        print(f"Error in get_listings: {e}")
        return Response("An internal server error occurred.", status=500)

# Vercel expects a handler variable
handler = app
