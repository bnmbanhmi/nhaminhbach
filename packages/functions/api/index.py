import sys
import os
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict, Union
import json
import uuid
from datetime import datetime
from decimal import Decimal
import sqlalchemy
from sqlalchemy import text
# from google.cloud.sql.connector import Connector, IPTypes  <-- Removed for Supabase
from utils import get_secret, geocode_address
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================================================
#  GLOBAL SETUP & CONFIGURATION
# =================================================================================

db_engine: sqlalchemy.engine.Engine = None

def default_json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime, uuid.UUID)):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def get_db_engine() -> sqlalchemy.engine.Engine:
    global db_engine
    if db_engine is not None:
        return db_engine

    # 1. Check for Supabase/Standard PostgreSQL Connection String (Preferred)
    DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    
    if DATABASE_URL:
        # Handle "postgres://" vs "postgresql://" for SQLAlchemy
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            
        # Use standard SQLAlchemy engine creation
        # pool_pre_ping=True helps with connection drops in serverless environments
        db_engine = sqlalchemy.create_engine(DATABASE_URL, pool_pre_ping=True)
        logger.info("Database engine initialized using DATABASE_URL (Supabase).")
        return db_engine

    # 2. Fallback to Google Cloud SQL (Legacy) - Only if DATABASE_URL is missing
    logger.warning("DATABASE_URL not found. Falling back to Google Cloud SQL Connector.")
    
    try:
        from google.cloud.sql.connector import Connector, IPTypes
    except ImportError:
        raise RuntimeError("DATABASE_URL not set and google-cloud-sql-connector not installed.")

    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME", "omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db-prod")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_NAME = os.environ.get("DB_NAME", "postgres")
    
    # Get database password
    GCP_PROJECT = os.environ.get("GCP_PROJECT") or "omega-sorter-467514-q6"
    DB_PASS = os.environ.get("DB_PASS")
    if not DB_PASS:
        DB_PASS = get_secret(GCP_PROJECT, "db-password")

    def getconn() -> Any:
        conn = Connector().connect(
            INSTANCE_CONNECTION_NAME, "pg8000", user=DB_USER, password=DB_PASS,
            db=DB_NAME, ip_type=IPTypes.PUBLIC,
            enable_iam_auth=False
        )
        return conn

    db_engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
    logger.info("Database engine initialized (Cloud SQL).")
    return db_engine

# =================================================================================
#  PYDANTIC MODELS
# =================================================================================

class AttributeValue(BaseModel):
    attribute_id: int
    value: Union[bool, int, str]

class ListingCreate(BaseModel):
    listing: Dict[str, Any]
    attributes: Optional[List[AttributeValue]] = None

class ListingStatusUpdate(BaseModel):
    listing_id: str
    status: str

class ListingDataUpdate(BaseModel):
    listing_id: str
    listing: Optional[Dict[str, Any]] = None
    attributes: Optional[List[Any]] = None

# =================================================================================
#  API ENDPOINTS
# =================================================================================

@app.get("/api/get_listings")
def get_listings():
    """API Endpoint to get all 'available' listings."""
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
        # Use JSONResponse with custom encoder handling if needed, but FastAPI handles basic types.
        # For Decimal/UUID/Datetime, we might need to convert them first or use a custom encoder.
        # Let's convert them manually to be safe as per original code.
        return json.loads(json.dumps(listings_data, default=default_json_serializer))

    except Exception as e:
        logger.error(f"Error in get_listings: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/api/get_admin_listings")
def get_admin_listings(
    status: Optional[str] = None,
    district: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """API Endpoint for admin dashboard to get listings with filtering by status."""
    
    # Build dynamic WHERE conditions
    where_conditions = []
    params = {}

    if status:
        where_conditions.append("l.status = :status")
        params["status"] = status
    
    if district:
        where_conditions.append("l.address_district ILIKE :district")
        params["district"] = f"%{district}%"

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

    sql_query = sqlalchemy.text(f"""
        SELECT l.*, (
            SELECT json_agg(json_build_object(
                'name', a.name,
                'slug', a.slug,
                'value', COALESCE(la.value_boolean::text, la.value_integer::text, la.value_string)
            ))
            FROM listing_attributes la JOIN attributes a ON la.attribute_id = a.id
            WHERE la.listing_id = l.id
        ) as attributes
        FROM listings l 
        WHERE {where_clause}
        ORDER BY l.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    params["limit"] = limit
    params["offset"] = offset

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query, params).fetchall()
        
        listings_data = [dict(row._mapping) for row in result]
        
        # Also get total count for pagination
        count_query = sqlalchemy.text(f"""
            SELECT COUNT(*) as total
            FROM listings l 
            WHERE {where_clause}
        """)
        
        with engine.connect() as conn:
            count_result = conn.execute(count_query, {k: v for k, v in params.items() if k not in ['limit', 'offset']}).fetchone()
            total_count = count_result.total

        response_data = {
            "listings": listings_data,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }

        return json.loads(json.dumps(response_data, default=default_json_serializer))

    except Exception as e:
        logger.error(f"Error in get_admin_listings: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/api/get_listing_by_id")
def get_listing_by_id(id: str):
    """Get a specific listing by ID (UUID)."""
    try:
        listing_id = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid 'id' format. Must be a valid UUID.")

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
        FROM listings l WHERE l.id = :listing_id
    """)

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query, {"listing_id": listing_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found.")

        listing_data = dict(result._mapping)
        return json.loads(json.dumps(listing_data, default=default_json_serializer))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching listing ID {listing_id}: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/api/get_all_attributes")
def get_all_attributes():
    """API Endpoint to get all possible attributes for a listing."""
    sql_query = sqlalchemy.text("SELECT * FROM attributes ORDER BY type, id;")

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()
        
        attributes_data = [dict(row._mapping) for row in result]
        return json.loads(json.dumps(attributes_data, default=default_json_serializer))

    except Exception as e:
        logger.error(f"Error in get_all_attributes: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.post("/api/create_listing")
def create_listing(payload: ListingCreate):
    """API Endpoint to create a new listing with dynamic attributes."""
    listing_data = payload.listing
    attributes_data = payload.attributes

    try:
        engine = get_db_engine()
        new_listing_id = None

        with engine.connect() as conn:
            with conn.begin() as tx:
                try:
                    # 1. Insert into 'listings'
                    insert_listing_stmt = sqlalchemy.text("""
                        INSERT INTO listings (title, description, price_monthly_vnd, area_m2, address_ward, address_district, source_url)
                        VALUES (:title, :description, :price, :area, :ward, :district, :source)
                        RETURNING id
                    """)
                    result = conn.execute(
                        insert_listing_stmt,
                        {
                            "title": listing_data.get("title"),
                            "description": listing_data.get("description"),
                            "price": int(listing_data.get("price_monthly_vnd", 0)),
                            "area": float(listing_data.get("area_m2", 0)),
                            "ward": listing_data.get("address_ward"),
                            "district": listing_data.get("address_district"),
                            "source": f"qc-form-{uuid.uuid4()}"
                        }
                    )
                    new_listing_id = result.scalar_one()

                    # 2. Insert into 'listing_attributes'
                    if attributes_data:
                        attrs_to_insert = []
                        for attr in attributes_data:
                            row = {
                                "listing_id": new_listing_id,
                                "attribute_id": attr.attribute_id,
                                "value_boolean": None,
                                "value_integer": None,
                                "value_string": None,
                            }
                            
                            value = attr.value
                            
                            if isinstance(value, bool):
                                row["value_boolean"] = value
                            elif isinstance(value, int):
                                row["value_integer"] = value
                            else:
                                row["value_string"] = str(value)
                            
                            attrs_to_insert.append(row)
                        
                        if attrs_to_insert:
                            insert_attrs_stmt = sqlalchemy.text("""
                                INSERT INTO listing_attributes (listing_id, attribute_id, value_boolean, value_integer, value_string)
                                VALUES (:listing_id, :attribute_id, :value_boolean, :value_integer, :value_string)
                            """)
                            conn.execute(insert_attrs_stmt, attrs_to_insert)
                    
                    tx.commit()
                except Exception as e:
                    logger.error(f"Transaction failed, rolling back. Error: {e}")
                    tx.rollback()
                    raise

        return JSONResponse(
            content=json.loads(json.dumps({"message": "Listing created successfully", "id": new_listing_id}, default=default_json_serializer)),
            status_code=201
        )

    except Exception as e:
        logger.error(f"Error in create_listing: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.post("/api/update_listing_status")
def update_listing_status(payload: ListingStatusUpdate):
    """API Endpoint to update listing status (approve/reject)."""
    listing_id = payload.listing_id
    new_status = payload.status

    if new_status not in ["available", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'available' or 'rejected'.")

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            check_query = text("SELECT status FROM listings WHERE id = :listing_id")
            result = conn.execute(check_query, {"listing_id": listing_id}).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Listing not found.")
            
            if result[0] != "pending_review":
                raise HTTPException(status_code=400, detail=f"Listing is not in pending_review status (current: {result[0]}).")

            update_query = text("UPDATE listings SET status = :status WHERE id = :listing_id")
            conn.execute(update_query, {"status": new_status, "listing_id": listing_id})
            conn.commit()

        return {"message": f"Listing status updated to {new_status}", "listing_id": listing_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_listing_status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/update_listing_data")
def update_listing_data(payload: ListingDataUpdate):
    """API Endpoint to update listing data and approve it."""
    listing_id = payload.listing_id
    listing_data = payload.listing or {}
    
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            check_query = text("SELECT status FROM listings WHERE id = :listing_id")
            result = conn.execute(check_query, {"listing_id": listing_id}).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Listing not found.")
            
            if result[0] != "pending_review":
                raise HTTPException(status_code=400, detail=f"Listing is not in pending_review status (current: {result[0]}).")

            update_fields = []
            update_params = {"listing_id": listing_id}
            
            allowed_fields = ["title", "description", "price_monthly_vnd", "area_m2", 
                            "address_street", "address_ward", "address_district", "contact_phone"]
            
            for field in allowed_fields:
                if field in listing_data and listing_data[field] is not None:
                    update_fields.append(f"{field} = :{field}")
                    update_params[field] = listing_data[field]
            
            # Geocoding logic
            address_fields = ["address_street", "address_ward", "address_district"]
            if any(field in listing_data for field in address_fields):
                current_query = text("SELECT address_street, address_ward, address_district FROM listings WHERE id = :listing_id")
                current_result = conn.execute(current_query, {"listing_id": listing_id}).fetchone()
                
                if current_result:
                    street = listing_data.get("address_street") or current_result[0] or ""
                    ward = listing_data.get("address_ward") or current_result[1] or ""
                    district = listing_data.get("address_district") or current_result[2] or ""
                    
                    address_parts = [part for part in [street, ward, district] if part and part.strip()]
                    if address_parts:
                        full_address = ", ".join(address_parts) + ", Hà Nội, Vietnam"
                        
                        GCP_PROJECT = os.environ.get("GCP_PROJECT", "omega-sorter-467514-q6")
                        coords = geocode_address(GCP_PROJECT, full_address)
                        
                        if coords:
                            lat, lng = coords
                            update_fields.extend(["latitude = :latitude", "longitude = :longitude"])
                            update_params.update({"latitude": lat, "longitude": lng})
            
            if update_fields:
                update_fields.append("status = :status")
                update_params["status"] = "available"
                
                update_query = text(f"""
                    UPDATE listings SET {', '.join(update_fields)}
                    WHERE id = :listing_id
                """)
                conn.execute(update_query, update_params)
                conn.commit()
            else:
                status_query = text("UPDATE listings SET status = 'available' WHERE id = :listing_id")
                conn.execute(status_query, {"listing_id": listing_id})
                conn.commit()

        return {"message": "Listing updated and approved successfully", "listing_id": listing_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_listing_data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
