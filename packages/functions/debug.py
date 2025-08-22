import os
import json
from firebase_functions import https_fn, options
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from sqlalchemy import text
from utils import get_secret

# Configure CORS for testing
CORS_CONFIG = options.CorsOptions(
    cors_origins=["*"],
    cors_methods=["get", "post"]
)

# Database connection function (copied from main.py)
def get_test_db_engine() -> sqlalchemy.engine.Engine:
    GCP_PROJECT = os.environ.get("GCP_PROJECT", "omega-sorter-467514-q6")
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME", "omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db")
    DB_USER = os.environ.get("DB_USER", "nhaminhbach_user")
    DB_NAME = os.environ.get("DB_NAME", "nhaminhbach_db")
    
    DB_PASS = get_secret(GCP_PROJECT, "db-password")
    
    connector = Connector()
    
    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            ip_type=IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC,
        )
        return conn
    
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine

@https_fn.on_request(
    cors=CORS_CONFIG,
    region="asia-southeast1"
)
def debug_listing_update(req: https_fn.Request) -> https_fn.Response:
    """
    Debug function to test database operations and column existence
    """
    if req.method != "POST":
        return https_fn.Response(f"Method {req.method} not allowed.", status=405)

    try:
        # First, let's see what columns exist in the listings table
        engine = get_test_db_engine()
        
        with engine.connect() as conn:
            # Check table structure
            structure_query = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'listings'
                ORDER BY ordinal_position
            """)
            columns = conn.execute(structure_query).fetchall()
            
            # Get a sample listing
            sample_query = text("SELECT * FROM listings WHERE status = 'pending_review' LIMIT 1")
            sample = conn.execute(sample_query).fetchone()
            
            # Try a simple status update
            test_listing_id = "3d55f7c2-cc27-4b33-8c6e-97af26b54f05"
            check_query = text("SELECT id, status FROM listings WHERE id = :listing_id")
            listing_check = conn.execute(check_query, {"listing_id": test_listing_id}).fetchone()
            
            result = {
                "columns": [{"name": col[0], "type": col[1]} for col in columns],
                "sample_listing": dict(sample._mapping) if sample else None,
                "test_listing": dict(listing_check._mapping) if listing_check else None,
                "debug": "Database connection successful"
            }
            
        return https_fn.Response(
            json.dumps(result, default=str),
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }
        return https_fn.Response(
            json.dumps(error_details),
            status=500,
            headers={"Content-Type": "application/json"}
        )
