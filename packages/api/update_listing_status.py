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

@app.route('/api/update_listing_status', methods=['POST'])
def update_listing_status():
    """
    API Endpoint to update listing status (approve/reject).
    POST request with JSON body: {"listing_id": "...", "status": "available|rejected"}
    """
    try:
        payload = request.get_json()
        if not payload:
            return Response("Invalid JSON payload.", status=400)

        listing_id = payload.get("listing_id")
        new_status = payload.get("status")

        if not listing_id or not new_status:
            return Response("Missing listing_id or status in payload.", status=400)

        if new_status not in ["available", "rejected"]:
            return Response("Status must be 'available' or 'rejected'.", status=400)

        supabase_client = get_supabase_client()
        
        # First check if listing exists and is in pending_review status
        response = supabase_client.table('listings').select('status').eq('id', listing_id).single().execute()
        
        if not response.data:
            return Response("Listing not found.", status=404)
            
        if response.data['status'] != "pending_review":
            return Response(f"Listing is not in pending_review status (current: {response.data['status']}).", status=400)

        # Update the status
        update_response = supabase_client.table('listings').update({'status': new_status}).eq('id', listing_id).execute()

        return Response(
            json.dumps({"message": f"Listing status updated to {new_status}", "listing_id": listing_id}),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Error in update_listing_status: {e}")
        return Response(f"Internal server error: {str(e)}", status=500)

# Vercel expects a handler variable
handler = app
