import os
import json
from decimal import Decimal
from typing import Any
from datetime import datetime
import uuid

from flask import Flask, Response, request
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from sqlalchemy import text


from utils import get_secret

app = Flask(__name__)

# =================================================================================
#  1. GLOBAL SETUP & CONFIGURATION
# =================================================================================

# Biến toàn cục cho SQLAlchemy Engine, được khởi tạo một cách "lười biếng"
db_engine: sqlalchemy.engine.Engine = None

# =================================================================================
#  2. CLIENT INITIALIZATION (Refactored into helper functions)
# =================================================================================

def get_db_engine() -> sqlalchemy.engine.Engine:
    global db_engine
    if db_engine is not None:
        return db_engine

    # Các biến môi trường này sẽ được cung cấp bởi cấu hình `run_with`
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME", "omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db-prod")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_NAME = os.environ.get("DB_NAME", "postgres")
    
    # Get database password from Secret Manager
    GCP_PROJECT = os.environ.get("GCP_PROJECT")
    if not GCP_PROJECT:
        # Set the project ID for Cloud Functions environment
        os.environ["GCP_PROJECT"] = "omega-sorter-467514-q6"
        GCP_PROJECT = "omega-sorter-467514-q6"
    DB_PASS = get_secret(GCP_PROJECT, "db-password")

    def getconn() -> Any:
        # Sử dụng IS_EMULATOR đã được định nghĩa ở global
        enable_iam_auth = os.environ.get("FUNCTIONS_EMULATOR") != "true"
        conn = Connector().connect(
            INSTANCE_CONNECTION_NAME, "pg8000", user=DB_USER, password=DB_PASS,
            db=DB_NAME, ip_type=IPTypes.PUBLIC,
            enable_iam_auth=False
        )
        return conn

    db_engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
    print("Database engine initialized.")
    return db_engine

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
    """API Endpoint để lấy tất cả các tin đăng 'available'."""
    sql_query = sqlalchemy.text("""
        SELECT l.*, (
            SELECT json_agg(json_build_object(
                'name', a.name,
                'slug', a.slug,
                'value', COALESCE(la.value_boolean::text, la.value_integer::text, la.value_string)
            ))
            FROM listing_attributes la JOIN attributes a ON la.attribute_id = a.id
            WHERE la.listing_id = l.id
        ) as attributes
        FROM listings l WHERE l.status = 'available'
    """)

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()
        
        listings_data = [dict(row._mapping) for row in result]
        json_response = json.dumps(listings_data, default=default_json_serializer)

        return Response(json_response, status=200, mimetype="application/json")

    except Exception as e:
        print(f"Error in get_listings: {e}")
        return Response("An internal server error occurred.", status=500)

# Vercel expects a handler variable
handler = app
