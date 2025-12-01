"""
GeoID API - Transaction-safe listing creation for NhaMinhBach
==============================================================
Supabase-based API endpoints with full transaction safety.

Author: CTO Alex + AI Agent
Date: 2025-12-01
"""

import os
import logging
from typing import Optional, Dict, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import BaseModel, Field

from geoid_utils import (
    find_or_create_house,
    create_room,
    create_room_history,
    format_geoid_display,
    get_ward_code,
)

logger = logging.getLogger(__name__)

# =========================================================================
# DATABASE CONNECTION (Supabase PostgreSQL)
# =========================================================================

def get_supabase_connection_string() -> str:
    """
    Build Supabase connection string from environment variables.
    
    Required env vars:
    - SUPABASE_DB_HOST (e.g., db.<project-ref>.supabase.co)
    - SUPABASE_DB_NAME (default: postgres)
    - SUPABASE_DB_USER (default: postgres)
    - SUPABASE_DB_PASSWORD
    - SUPABASE_DB_PORT (default: 5432)
    """
    host = os.environ.get("SUPABASE_DB_HOST")
    port = os.environ.get("SUPABASE_DB_PORT", "5432")
    db_name = os.environ.get("SUPABASE_DB_NAME", "postgres")
    user = os.environ.get("SUPABASE_DB_USER", "postgres")
    password = os.environ.get("SUPABASE_DB_PASSWORD")
    
    if not all([host, password]):
        raise ValueError(
            "Missing required Supabase credentials. Set SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD"
        )
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


@contextmanager
def get_db_connection():
    """
    Context manager for Supabase database connection with automatic cleanup.
    
    Usage:
        with get_db_connection() as conn:
            result = conn.execute(...)
    """
    connection_string = get_supabase_connection_string()
    engine = create_engine(connection_string, pool_pre_ping=True)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()


# =========================================================================
# PYDANTIC MODELS (Request/Response Validation)
# =========================================================================

class CreateListingRequest(BaseModel):
    """Request model for creating a new listing."""
    
    # Location
    ward: str = Field(..., description="Ward name (e.g., 'Cầu Giấy')")
    address_street: Optional[str] = Field(None, description="Street address")
    address_ward: Optional[str] = Field(None, description="Ward name (verbose form)")
    address_district: Optional[str] = Field(None, description="District name (optional, for reference)")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Listing details
    title: str = Field(..., min_length=10, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    price_monthly_vnd: int = Field(..., gt=0, description="Monthly rent in VND")
    area_m2: Optional[float] = Field(None, gt=0)
    
    # Contact
    contact_phone: Optional[str] = Field(None, max_length=20)
    
    # Media
    image_urls: Optional[List[str]] = Field(default_factory=list)
    source_url: Optional[str] = Field(None, description="Original post URL")
    
    # Attributes (amenities)
    attributes: Optional[Dict] = Field(default_factory=dict)
    
    # Room info
    room_number: Optional[str] = Field(None, description="Room number (e.g., '301', 'A12')")
    
    # Quality
    accuracy_level: int = Field(2, ge=1, le=2, description="1=Verified, 2=Fuzzy")
    status: str = Field("pending_review", description="Initial status")


class ListingResponse(BaseModel):
    """Response model after creating a listing."""
    
    success: bool
    geo_id: str = Field(..., description="Full GeoID (29CG.AB1)")
    display_id: str = Field(..., description="Display format (29CGAB1)")
    house_id: int
    room_id: int
    history_id: int
    house_created: bool = Field(..., description="True if new house was created")
    url: str = Field(..., description="Public URL to listing")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict] = None


# =========================================================================
# TRANSACTION-SAFE LISTING CREATION
# =========================================================================

def create_listing_atomic(request: CreateListingRequest) -> ListingResponse:
    """
    Create a complete listing in a single atomic transaction.
    
    This function ensures that:
    1. House creation/lookup
    2. Room creation
    3. Room history creation
    
    ALL succeed together or ALL fail together (no partial state).
    
    Args:
        request: Validated CreateListingRequest
    
    Returns:
        ListingResponse with GeoID and IDs
    
    Raises:
        ValueError: Invalid input data
        IntegrityError: Database constraint violation
        SQLAlchemyError: Database error
    """
    ward_code = get_ward_code(request.ward)
    if not ward_code:
        raise ValueError(f"Unknown ward: {request.ward}")
    
    with get_db_connection() as conn:
        # Start explicit transaction
        trans = conn.begin()
        
        try:
            # Step 1: Find or create house (with deduplication)
            logger.info(f"Creating listing for ward={request.ward}, street={request.address_street}")
            
            house_id, house_geo_id, house_created = find_or_create_house(
                conn=conn,
                ward_code=ward_code,
                latitude=request.latitude,
                longitude=request.longitude,
                address_street=request.address_street,
                address_ward=request.address_ward,
                address_district=request.address_district,
                contact_phone=request.contact_phone,
                accuracy_level=request.accuracy_level
            )
            
            # Step 2: Create room
            room_db_id, room_geo_id = create_room(
                conn=conn,
                house_id=house_id,
                room_number=request.room_number,
                status=request.status
            )
            
            # Step 3: Create room history snapshot
            history_id = create_room_history(
                conn=conn,
                room_id=room_db_id,
                title=request.title,
                description=request.description,
                price_monthly_vnd=request.price_monthly_vnd,
                area_m2=request.area_m2,
                contact_phone=request.contact_phone,
                image_urls=request.image_urls,
                source_url=request.source_url,
                attributes=request.attributes,
                status=request.status,
                is_current=True
            )
            
            # Commit transaction - all or nothing
            trans.commit()
            
            # Success - format response
            display_id = format_geoid_display(room_geo_id)
            
            logger.info(
                f"✅ Listing created: geo_id={room_geo_id}, display={display_id}, "
                f"house_id={house_id}, room_id={room_db_id}, history_id={history_id}"
            )
            
            return ListingResponse(
                success=True,
                geo_id=room_geo_id,
                display_id=display_id,
                house_id=house_id,
                room_id=room_db_id,
                history_id=history_id,
                house_created=house_created,
                url=f"/{display_id}"
            )
            
        except Exception as e:
            # Rollback on ANY error
            trans.rollback()
            logger.error(f"❌ Transaction rolled back: {e.__class__.__name__}: {e}")
            raise


# =========================================================================
# FASTAPI ENDPOINT EXAMPLE
# =========================================================================

"""
FastAPI integration example:

```python
from fastapi import FastAPI, HTTPException
from geoid_api import create_listing_atomic, CreateListingRequest, ListingResponse, ErrorResponse

app = FastAPI()

@app.post("/api/listings", response_model=ListingResponse, responses={400: {"model": ErrorResponse}})
async def create_listing_endpoint(request: CreateListingRequest):
    '''
    Create a new rental listing with transaction safety.
    
    Example request:
    {
        "ward": "Cầu Giấy",
        "address_street": "Phạm Hùng",
        "address_ward": "Dịch Vọng",
        "title": "Phòng trọ giá rẻ gần ĐH Bách Khoa",
        "price_monthly_vnd": 3500000,
        "area_m2": 25,
        "contact_phone": "0987654321",
        "latitude": 21.0278,
        "longitude": 105.7850
    }
    '''
    try:
        result = create_listing_atomic(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Conflict: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error creating listing")
        raise HTTPException(status_code=500, detail="Internal server error")
```
"""
