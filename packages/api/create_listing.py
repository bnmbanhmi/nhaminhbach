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

@app.route('/api/create_listing', methods=['POST'])
def create_listing():
    """
    API Endpoint to create a new listing with dynamic attributes.
    """
    try:
        data = request.get_json()
        if not data:
            return Response("Invalid JSON payload.", status=400)

        listing_data = data.get("listing")
        attributes_data = data.get("attributes")

        if not listing_data or not isinstance(attributes_data, list):
            return Response("Missing or malformed 'listing' or 'attributes' data.", status=400)

        supabase_client = get_supabase_client()

        # 1. Insert into 'listings' table
        listing_to_insert = {
            "title": listing_data.get("title"),
            "description": listing_data.get("description"),
            "price_monthly_vnd": int(listing_data.get("price_monthly_vnd", 0)),
            "area_m2": float(listing_data.get("area_m2", 0)),
            "address_ward": listing_data.get("address_ward"),
            "address_district": listing_data.get("address_district"),
            "source_url": f"qc-form-{uuid.uuid4()}" # Create a unique source_url
        }
        
        listing_response = supabase_client.table('listings').insert(listing_to_insert).execute()
        new_listing_id = listing_response.data[0]['id']

        # 2. Insert into 'listing_attributes' table
        if attributes_data:
            attrs_to_insert = []
            for attr in attributes_data:
                row = {
                    "listing_id": new_listing_id,
                    "attribute_id": attr.get("attribute_id"),
                    "value_boolean": None,
                    "value_integer": None,
                    "value_string": None,
                }
                
                value = attr.get("value")
                
                if isinstance(value, bool):
                    row["value_boolean"] = value
                elif isinstance(value, int):
                    row["value_integer"] = value
                else:
                    row["value_string"] = str(value)
                
                attrs_to_insert.append(row)
            
            if attrs_to_insert:
                supabase_client.table('listing_attributes').insert(attrs_to_insert).execute()

        return Response(
            json.dumps({"message": "Listing created successfully", "id": new_listing_id}, default=default_json_serializer),
            status=201,
            mimetype="application/json"
        )

    except Exception as e:
        print(f"Error in create_listing: {e}")
        return Response("An internal server error occurred.", status=500)

# Vercel expects a handler variable
handler = app
