import os
import json
from decimal import Decimal
from typing import Any
from datetime import datetime
import uuid

from flask import Flask, Response, request
from dotenv import load_dotenv

from utils import geocode_address

load_dotenv()

app = Flask(__name__)

# =================================================================================
#  1. UTILITY FUNCTIONS
# =================================================================================

def default_json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime, uuid.UUID)):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# =================================================================================
#  2. API ENDPOINTS
# =================================================================================

@app.route('/api/test_geocoding', methods=['POST'])
def test_geocoding():
    """
    Test endpoint to verify geocoding is working with a sample address.
    POST request with JSON body: {"address": "123 Some Street, Ward, District"}
    """
    try:
        payload = request.get_json()
        if not payload or "address" not in payload:
            return Response("Missing 'address' field in JSON body.", status=400)

        address = payload["address"]
        
        GCP_PROJECT = os.environ.get("GCP_PROJECT", "omega-sorter-467514-q6")
        coords = geocode_address(GCP_PROJECT, address)
        
        if coords:
            lat, lng = coords
            result = {
                "success": True,
                "address": address,
                "coordinates": {"latitude": lat, "longitude": lng}
            }
        else:
            result = {
                "success": False,
                "address": address,
                "error": "Geocoding failed"
            }
        
        return Response(
            json.dumps(result),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Error in test_geocoding: {e}")
        return Response(f"Internal server error: {str(e)}", status=500)

# Vercel expects a handler variable
handler = app
