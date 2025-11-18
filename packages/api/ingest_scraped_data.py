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

@app.route('/api/ingest_scraped_data', methods=['POST'])
def ingest_scraped_data():
    """
    Secure endpoint for local scraper to submit scraped posts into the listings table.
    - Auth: X-API-Key header must match INGEST_API_KEY env var.
    - Dedup: Check listings by source_url (permalink). Skip existing.
    - Insert: New rows into listings with status='pending_review' and placeholder values.
    Payloads supported:
      - { "posts": [ {content, image_urls[], permalink}, ... ] }
      - [ {content, image_urls[], permalink}, ... ]
      - {content, image_urls[], permalink} (single)
    """
    # API Key check
    api_key_header = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if not api_key_header or api_key_header != os.environ.get("INGEST_API_KEY"):
        return Response("Unauthorized", status=401)

    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return Response("Invalid JSON payload.", status=400)

        # Normalize posts array from supported payload shapes
        posts = []
        if isinstance(payload, dict) and isinstance(payload.get("posts"), list):
            posts = payload.get("posts", [])
        elif isinstance(payload, list):
            posts = payload
        elif isinstance(payload, dict) and ("permalink" in payload or "content" in payload):
            posts = [payload]
        else:
            return Response("Unsupported payload shape. Provide {posts: [...]}, an array, or a single post object.", status=400)

        new_count = 0
        dup_count = 0

        supabase_client = get_supabase_client()

        for p in posts:
            permalink = (p.get("permalink") if isinstance(p, dict) else None) or ""
            if not isinstance(permalink, str) or not permalink:
                dup_count += 1
                continue

            # Duplicate check
            response = supabase_client.table('listings').select('id').eq('source_url', permalink).execute()
            if response.data:
                dup_count += 1
                continue

            content = p.get("content") if isinstance(p, dict) else None
            image_urls = p.get("image_urls") if isinstance(p, dict) else None
            if not isinstance(image_urls, list):
                image_urls = []

            # Insert with placeholders for NOT NULL fields
            listing_to_insert = {
                "status": "pending_review",
                "title": "Pending QC",
                "description": content or "Pending QC",
                "price_monthly_vnd": 1000000,
                "area_m2": 1.0,
                "ward": "Unknown",
                "district": "Unknown",
                "source_url": permalink,
                "image_urls": image_urls,
            }
            
            supabase_client.table('listings').insert(listing_to_insert).execute()
            new_count += 1

        return Response(
            json.dumps({
                "message": "Ingestion complete",
                "new_listings_created": new_count,
                "skipped_duplicates": dup_count
            }),
            status=200,
            mimetype="application/json",
        )

    except Exception as e:
        print(f"Error in ingest_scraped_data: {e}")
        return Response("An internal server error occurred.", status=500)

# Vercel expects a handler variable
handler = app
