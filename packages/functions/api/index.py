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
            
        # Log masked URL for debugging
        try:
            from sqlalchemy.engine.url import make_url
            u = make_url(DATABASE_URL)
            logger.info(f"Connecting to DB: Host={u.host}, Port={u.port}, User={u.username}, DB={u.database}")
        except Exception as e:
            logger.error(f"Failed to parse DATABASE_URL for logging: {e}")

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
    # Query the v2 GeoID schema: use room_history (current versions) joined to rooms and houses
    sql_query = sqlalchemy.text("""
        SELECT
            rh.id::text AS id,
            rh.status,
            rh.source_url,
            rh.title,
            rh.description,
            rh.price_monthly_vnd,
            rh.area_m2,
            h.address_street,
            h.address_ward,
            h.address_district,
            h.latitude,
            h.longitude,
            rh.contact_phone,
            rh.image_urls,
            rh.created_at,
            (
                SELECT json_agg(json_build_object(
                    'name', a.name,
                    'slug', a.slug,
                    'value', COALESCE(
                        NULLIF((rh.attributes ->> a.slug), '')::boolean::text,
                        NULLIF((rh.attributes ->> a.slug), '')::integer::text,
                        rh.attributes ->> a.slug
                    )
                ))
                FROM jsonb_each_text(rh.attributes) kv(key, value)
                JOIN attributes a ON a.slug = kv.key
            ) as attributes
        FROM room_history rh
        JOIN rooms r ON rh.room_id = r.id
        JOIN houses h ON r.house_id = h.id
        WHERE rh.is_current = TRUE AND rh.status = 'available'
    """)

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()

        listings_data = [dict(row._mapping) for row in result]
        return json.loads(json.dumps(listings_data, default=default_json_serializer))

    except Exception as e:
        logger.error(f"Error in get_listings: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.get("/api/get_admin_listings")
def get_admin_listings(
    status: Optional[str] = None,
    district: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """API Endpoint for admin dashboard to get listings with filtering by status."""
    
    # Build dynamic WHERE conditions against room_history/houses
    where_conditions = []
    params = {}

    if status:
        where_conditions.append("rh.status = :status")
        params["status"] = status

    if district:
        where_conditions.append("h.address_district ILIKE :district")
        params["district"] = f"%{district}%"

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

    sql_query = sqlalchemy.text(f"""
        SELECT
            rh.id::text AS id,
            rh.status,
            rh.source_url,
            rh.title,
            rh.description,
            rh.price_monthly_vnd,
            rh.area_m2,
            h.address_street,
            h.address_ward,
            h.address_district,
            h.latitude,
            h.longitude,
            rh.contact_phone,
            rh.image_urls,
            rh.created_at,
            (
                SELECT json_agg(json_build_object(
                    'name', a.name,
                    'slug', a.slug,
                    'value', COALESCE(
                        NULLIF((rh.attributes ->> a.slug), '')::boolean::text,
                        NULLIF((rh.attributes ->> a.slug), '')::integer::text,
                        rh.attributes ->> a.slug
                    )
                ))
                FROM jsonb_each_text(rh.attributes) kv(key, value)
                JOIN attributes a ON a.slug = kv.key
            ) as attributes
        FROM room_history rh
        JOIN rooms r ON rh.room_id = r.id
        JOIN houses h ON r.house_id = h.id
        WHERE rh.is_current = TRUE AND {where_clause}
        ORDER BY rh.created_at DESC
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
            FROM room_history rh
            JOIN rooms r ON rh.room_id = r.id
            JOIN houses h ON r.house_id = h.id
            WHERE rh.is_current = TRUE AND {where_clause}
        """)

        with engine.connect() as conn:
            count_result = conn.execute(count_query, {k: v for k, v in params.items() if k not in ['limit', 'offset']}).fetchone()
            total_count = int(count_result.total)

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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.get("/api/get_listing_by_id")
def get_listing_by_id(id: str):
    """Get a specific listing by ID (UUID)."""
    # Accept either numeric room_history.id or legacy UUID mapped in uuid_to_geoid_mapping
    engine = get_db_engine()
    try:
        with engine.connect() as conn:
            rh_id = None

            # First, is it an integer id (room_history.id)
            if id.isdigit():
                rh_id = int(id)
            else:
                # Try to parse as UUID and lookup mapping
                try:
                    old_uuid = uuid.UUID(id)
                    mapping_q = text("SELECT new_room_id FROM uuid_to_geoid_mapping WHERE old_uuid = :old_uuid LIMIT 1")
                    mapping = conn.execute(mapping_q, {"old_uuid": str(old_uuid)}).fetchone()
                    if mapping and mapping.new_room_id:
                        # Find current room_history for that room
                        rh_q = text("SELECT id FROM room_history WHERE room_id = :room_id AND is_current = TRUE LIMIT 1")
                        rh_row = conn.execute(rh_q, {"room_id": mapping.new_room_id}).fetchone()
                        if rh_row:
                            rh_id = int(rh_row.id)
                except ValueError:
                    pass

            if rh_id is None:
                raise HTTPException(status_code=400, detail="Invalid 'id' format or mapping not found.")

            sql_query = text("""
                SELECT
                    rh.id::text AS id,
                    rh.status,
                    rh.source_url,
                    rh.title,
                    rh.description,
                    rh.price_monthly_vnd,
                    rh.area_m2,
                    h.address_street,
                    h.address_ward,
                    h.address_district,
                    h.latitude,
                    h.longitude,
                    rh.contact_phone,
                    rh.image_urls,
                    rh.created_at,
                    rh.attributes,
                    (
                        SELECT json_agg(json_build_object(
                            'name', a.name,
                            'slug', a.slug,
                            'value', COALESCE(
                                NULLIF((rh.attributes ->> a.slug), '')::boolean::text,
                                NULLIF((rh.attributes ->> a.slug), '')::integer::text,
                                rh.attributes ->> a.slug
                            )
                        ))
                        FROM jsonb_each_text(rh.attributes) kv(key, value)
                        JOIN attributes a ON a.slug = kv.key
                    ) as attributes_list
                FROM room_history rh
                JOIN rooms r ON rh.room_id = r.id
                JOIN houses h ON r.house_id = h.id
                WHERE rh.id = :rh_id AND rh.is_current = TRUE
            """)

            result = conn.execute(sql_query, {"rh_id": rh_id}).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail=f"Listing with ID {id} not found.")

            listing_data = dict(result._mapping)
            return json.loads(json.dumps(listing_data, default=default_json_serializer))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching listing ID {id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.get("/api/get_all_attributes")
def get_all_attributes():
    """API Endpoint to get all possible attributes for a listing."""
    sql_query = sqlalchemy.text("SELECT id, type, name, slug, possible_values FROM attributes ORDER BY type, id;")

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sql_query).fetchall()

        attributes_data = [dict(row._mapping) for row in result]
        return json.loads(json.dumps(attributes_data, default=default_json_serializer))

    except Exception as e:
        logger.error(f"Error in get_all_attributes: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.post("/api/create_listing")
def create_listing(payload: ListingCreate):
    """API Endpoint to create a new listing with dynamic attributes."""
    listing_data = payload.listing
    attributes_data = payload.attributes

    try:
        engine = get_db_engine()
        new_rh_id = None

        # Build attributes JSONB from provided attributes list (mapping attribute_id -> slug)
        with engine.connect() as conn:
            # Fetch attribute id -> slug map
            attr_map = {row.id: row.slug for row in conn.execute(text("SELECT id, slug FROM attributes")).fetchall()}

        attributes_json = {}
        if attributes_data:
            for attr in attributes_data:
                slug = attr_map.get(attr.attribute_id)
                if slug:
                    attributes_json[slug] = attr.value

        with engine.connect() as conn:
            with conn.begin() as tx:
                try:
                    # 1. Create a house (minimal required fields). Generate geo_id using md5(random()) to avoid collisions.
                    create_house = text("""
                        INSERT INTO houses (city_code, ward_code, geo_id, address_street, address_ward, address_district, latitude, longitude, created_at, updated_at)
                        VALUES (:city_code, :ward_code, :geo_id, :street, :ward, :district, :latitude, :longitude, NOW(), NOW())
                        RETURNING id
                    """)

                    gen_geo = str(uuid.uuid4()).replace('-', '')[:5]
                    house_res = conn.execute(create_house, {
                        "city_code": "29",
                        "ward_code": listing_data.get("address_ward") or "00",
                        "geo_id": gen_geo,
                        "street": listing_data.get("address_street"),
                        "ward": listing_data.get("address_ward"),
                        "district": listing_data.get("address_district"),
                        "latitude": listing_data.get("latitude"),
                        "longitude": listing_data.get("longitude")
                    })
                    house_id = house_res.scalar_one()

                    # 2. Create a room (room_id '00' by default)
                    create_room = text("""
                        INSERT INTO rooms (house_id, room_id, created_at, updated_at)
                        VALUES (:house_id, :room_id, NOW(), NOW())
                        RETURNING id
                    """)
                    room_res = conn.execute(create_room, {"house_id": house_id, "room_id": "00"})
                    room_id = room_res.scalar_one()

                    # 3. Insert into room_history as the current version
                    insert_rh = text("""
                        INSERT INTO room_history (room_id, title, description, price_monthly_vnd, area_m2, contact_phone, image_urls, source_url, attributes, status, valid_from, is_current, created_at)
                        VALUES (:room_id, :title, :description, :price, :area, :contact_phone, :image_urls, :source_url, :attributes::jsonb, :status, NOW(), TRUE, NOW())
                        RETURNING id
                    """)

                    rh_res = conn.execute(insert_rh, {
                        "room_id": room_id,
                        "title": listing_data.get("title"),
                        "description": listing_data.get("description"),
                        "price": int(listing_data.get("price_monthly_vnd", 0)),
                        "area": float(listing_data.get("area_m2", 0)),
                        "contact_phone": listing_data.get("contact_phone"),
                        "image_urls": listing_data.get("image_urls"),
                        "source_url": f"qc-form-{uuid.uuid4()}",
                        "attributes": json.dumps(attributes_json),
                        "status": "pending_review"
                    })

                    new_rh_id = rh_res.scalar_one()
                    tx.commit()
                except Exception as e:
                    logger.error(f"Transaction failed creating v2 listing: {e}")
                    tx.rollback()
                    raise

        return JSONResponse(
            content=json.loads(json.dumps({"message": "Listing created successfully", "id": str(new_rh_id)}, default=default_json_serializer)),
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
            # Determine room_history id from provided listing_id (accept numeric rh.id or legacy UUID mapping)
            rh_id = None
            if listing_id.isdigit():
                rh_id = int(listing_id)
            else:
                try:
                    old_uuid = uuid.UUID(listing_id)
                    mapping = conn.execute(text("SELECT new_room_id FROM uuid_to_geoid_mapping WHERE old_uuid = :old_uuid LIMIT 1"), {"old_uuid": str(old_uuid)}).fetchone()
                    if mapping and mapping.new_room_id:
                        rh_row = conn.execute(text("SELECT id FROM room_history WHERE room_id = :room_id AND is_current = TRUE LIMIT 1"), {"room_id": mapping.new_room_id}).fetchone()
                        if rh_row:
                            rh_id = int(rh_row.id)
                except ValueError:
                    pass

            if rh_id is None:
                raise HTTPException(status_code=404, detail="Listing not found or invalid id.")

            # Fetch current room_history row
            current = conn.execute(text("SELECT * FROM room_history WHERE id = :rh_id AND is_current = TRUE"), {"rh_id": rh_id}).fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Listing not found or not current.")

            if current.status != 'pending_review':
                raise HTTPException(status_code=400, detail=f"Listing is not in pending_review status (current: {current.status}).")

            # Insert a new room_history row copying existing fields but with updated status (triggers will close previous)
            insert_q = text("""
                INSERT INTO room_history (room_id, title, description, price_monthly_vnd, area_m2, contact_phone, image_urls, source_url, attributes, status, valid_from, is_current, created_at)
                VALUES (:room_id, :title, :description, :price, :area, :contact_phone, :image_urls, :source_url, :attributes, :status, NOW(), TRUE, NOW())
                RETURNING id
            """)

            new_rh = conn.execute(insert_q, {
                "room_id": current.room_id,
                "title": current.title,
                "description": current.description,
                "price": current.price_monthly_vnd,
                "area": current.area_m2,
                "contact_phone": current.contact_phone,
                "image_urls": current.image_urls,
                "source_url": current.source_url,
                "attributes": json.dumps(current.attributes) if current.attributes is not None else '{}',
                "status": new_status
            }).scalar_one()

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
            # Resolve rh_id similar to update_listing_status
            rh_id = None
            if listing_id.isdigit():
                rh_id = int(listing_id)
            else:
                try:
                    old_uuid = uuid.UUID(listing_id)
                    mapping = conn.execute(text("SELECT new_room_id FROM uuid_to_geoid_mapping WHERE old_uuid = :old_uuid LIMIT 1"), {"old_uuid": str(old_uuid)}).fetchone()
                    if mapping and mapping.new_room_id:
                        rh_row = conn.execute(text("SELECT id FROM room_history WHERE room_id = :room_id AND is_current = TRUE LIMIT 1"), {"room_id": mapping.new_room_id}).fetchone()
                        if rh_row:
                            rh_id = int(rh_row.id)
                except ValueError:
                    pass

            if rh_id is None:
                raise HTTPException(status_code=404, detail="Listing not found or invalid id.")

            # Fetch current
            current = conn.execute(text("SELECT * FROM room_history WHERE id = :rh_id AND is_current = TRUE"), {"rh_id": rh_id}).fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Listing not found or not current.")

            # Build new values
            new_title = listing_data.get("title", current.title)
            new_description = listing_data.get("description", current.description)
            new_price = int(listing_data.get("price_monthly_vnd", current.price_monthly_vnd or 0))
            new_area = float(listing_data.get("area_m2", current.area_m2 or 0))
            new_contact = listing_data.get("contact_phone", current.contact_phone)

            # Merge attributes if provided
            existing_attrs = current.attributes or {}
            new_attrs = existing_attrs.copy()
            if payload.attributes:
                # attributes is expected to be list of AttributeValue-like dicts
                # fetch attribute id -> slug map
                attr_map = {row.id: row.slug for row in conn.execute(text("SELECT id, slug FROM attributes")).fetchall()}
                for a in payload.attributes:
                    slug = attr_map.get(a.get('attribute_id') if isinstance(a, dict) else getattr(a, 'attribute_id', None))
                    val = a.get('value') if isinstance(a, dict) else getattr(a, 'value', None)
                    if slug:
                        new_attrs[slug] = val

            # If address changed, update houses table
            address_changed = any(field in listing_data for field in ["address_street", "address_ward", "address_district"])
            if address_changed:
                # get room -> house
                room_row = conn.execute(text("SELECT room_id FROM room_history WHERE id = :rh_id"), {"rh_id": rh_id}).fetchone()
                room_row_id = room_row.room_id
                house_row = conn.execute(text("SELECT house_id FROM rooms WHERE id = :room_row_id"), {"room_row_id": room_row_id}).fetchone()
                if house_row:
                    update_house = text("""
                        UPDATE houses SET address_street = COALESCE(:street, address_street), address_ward = COALESCE(:ward, address_ward), address_district = COALESCE(:district, address_district), updated_at = NOW()
                        WHERE id = :house_id
                    """)
                    conn.execute(update_house, {"street": listing_data.get("address_street"), "ward": listing_data.get("address_ward"), "district": listing_data.get("address_district"), "house_id": house_row.house_id})

            # Insert a new room_history record with updated values and mark available
            insert_q = text("""
                INSERT INTO room_history (room_id, title, description, price_monthly_vnd, area_m2, contact_phone, image_urls, source_url, attributes, status, valid_from, is_current, created_at)
                VALUES (:room_id, :title, :description, :price, :area, :contact_phone, :image_urls, :source_url, :attributes::jsonb, :status, NOW(), TRUE, NOW())
                RETURNING id
            """)

            new_rh = conn.execute(insert_q, {
                "room_id": current.room_id,
                "title": new_title,
                "description": new_description,
                "price": new_price,
                "area": new_area,
                "contact_phone": new_contact,
                "image_urls": listing_data.get("image_urls") or current.image_urls,
                "source_url": current.source_url,
                "attributes": json.dumps(new_attrs),
                "status": "available"
            }).scalar_one()

        return {"message": "Listing updated and approved successfully", "listing_id": listing_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_listing_data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
