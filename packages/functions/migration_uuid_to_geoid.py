"""
Migration Script: UUID to GeoID System
=======================================
Migrates existing listings from old schema (UUID-based) to new GeoID schema.

Steps:
1. Read all existing listings from `listings` table
2. Extract district codes from addresses
3. Create houses with fingerprinting (deduplicate)
4. Create rooms (all with room_id=00 initially)
5. Create room_history snapshots
6. Store UUID → GeoID mapping
7. Validate migration

Usage:
    python migration_uuid_to_geoid.py [--dry-run] [--batch-size 100]

Author: CTO Alex + AI Agent
Date: 2025-12-01
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

import argparse
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import sqlalchemy
from sqlalchemy import text, create_engine
from geoid_utils import (
    get_ward_code,
    find_or_create_house,
    create_room,
    create_room_history,
    WARD_CODES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationStats:
    """Track migration statistics."""
    
    def __init__(self):
        self.total_listings = 0
        self.migrated_listings = 0
        self.failed_listings = 0
        self.houses_created = 0
        self.houses_reused = 0
        self.rooms_created = 0
        self.errors: List[Dict] = []
    
    def log_summary(self):
        """Print migration summary."""
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total listings processed: {self.total_listings}")
        logger.info(f"Successfully migrated: {self.migrated_listings}")
        logger.info(f"Failed: {self.failed_listings}")
        logger.info(f"Houses created: {self.houses_created}")
        logger.info(f"Houses reused (deduplicated): {self.houses_reused}")
        logger.info(f"Rooms created: {self.rooms_created}")
        
        if self.errors:
            logger.error(f"\nErrors encountered: {len(self.errors)}")
            for i, error in enumerate(self.errors[:10], 1):  # Show first 10 errors
                logger.error(f"{i}. UUID={error['uuid']}: {error['error']}")


def get_database_connection():
    """
    Get Supabase database connection from environment.
    
    Required environment variables:
    - SUPABASE_DB_HOST: db.<project-ref>.supabase.co
    - SUPABASE_DB_PASSWORD: Your Supabase password
    - SUPABASE_DB_NAME: postgres (default)
    - SUPABASE_DB_USER: postgres (default)
    - SUPABASE_DB_PORT: 5432 (default)
    """
    host = os.environ.get("SUPABASE_DB_HOST")
    password = os.environ.get("SUPABASE_DB_PASSWORD")
    
    if not host or not password:
        raise ValueError(
            "Missing Supabase credentials. Set SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD"
        )
    
    user = os.environ.get("SUPABASE_DB_USER", "postgres")
    dbname = os.environ.get("SUPABASE_DB_NAME", "postgres")
    port = os.environ.get("SUPABASE_DB_PORT", "5432")
    
    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    logger.info(f"Connecting to Supabase: {host}")
    engine = create_engine(conn_str, pool_pre_ping=True)
    return engine


def fetch_old_listings(conn, limit: int = None, offset: int = 0):
    """
    Fetch listings from old schema.
    
    Args:
        conn: SQLAlchemy connection
        limit: Max number of listings to fetch
        offset: Offset for pagination
    
    Returns:
        List of listing dictionaries
    """
    query = text("""
        SELECT 
            id,
            status,
            source_url,
            title,
            description,
            price_monthly_vnd,
            area_m2,
            address_street,
            address_ward,
            address_district,
            latitude,
            longitude,
            contact_phone,
            image_urls
        FROM listings
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """)
    
    result = conn.execute(query, {"limit": limit or 999999, "offset": offset})
    
    listings = []
    for row in result:
        listings.append({
            "uuid": str(row[0]),
            "status": row[1],
            "source_url": row[2],
            "title": row[3],
            "description": row[4],
            "price_monthly_vnd": row[5],
            "area_m2": float(row[6]) if row[6] else None,
            "address_street": row[7],
            "address_ward": row[8],
            "address_district": row[9],
            "latitude": float(row[10]) if row[10] else None,
            "longitude": float(row[11]) if row[11] else None,
            "contact_phone": row[12],
            "image_urls": row[13] or []
        })
    
    return listings


def fetch_listing_attributes(conn, listing_uuid: str) -> Dict:
    """
    Fetch attributes for a listing from old schema.
    
    Args:
        conn: SQLAlchemy connection
        listing_uuid: UUID of listing
    
    Returns:
        Dict of attributes {slug: value}
    """
    query = text("""
        SELECT 
            a.slug,
            a.type,
            la.value_boolean,
            la.value_integer,
            la.value_string
        FROM listing_attributes la
        JOIN attributes a ON a.id = la.attribute_id
        WHERE la.listing_id = :uuid
    """)
    
    result = conn.execute(query, {"uuid": listing_uuid})
    
    attributes = {}
    for row in result:
        slug = row[0]
        attr_type = row[1]
        
        # Extract value based on type
        if attr_type == 'boolean':
            value = row[2]
        elif attr_type == 'integer':
            value = row[3]
        else:  # string or enum
            value = row[4]
        
        attributes[slug] = value
    
    return attributes


def migrate_listing(
    conn,
    listing: Dict,
    stats: MigrationStats,
    dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Migrate a single listing to new GeoID schema.
    
    Args:
        conn: SQLAlchemy connection
        listing: Listing dictionary
        stats: MigrationStats object
        dry_run: If True, don't commit changes
    
    Returns:
        Tuple of (success, geo_id or error_message)
    """
    try:
        uuid = listing["uuid"]
        logger.info(f"Migrating listing: UUID={uuid}")
        
        # Step 1: Extract ward code from address_ward or address_district
        ward_name = listing.get("address_ward") or listing.get("address_district")
        ward_code = get_ward_code(ward_name)
        
        if not ward_code:
            logger.warning(f"Unknown ward: '{ward_name}' for UUID={uuid}")
            # Default to first ward (Cầu Giấy) for now
            ward_code = "CG"
            logger.warning(f"Defaulting to ward code: {ward_code}")
        
        # Step 2: Determine accuracy level
        accuracy_level = 1 if listing.get("latitude") and listing.get("longitude") else 2
        
        # Step 3: Find or create house
        house_id, house_geo_id, created = find_or_create_house(
            conn=conn,
            ward_code=ward_code,
            latitude=listing.get("latitude"),
            longitude=listing.get("longitude"),
            address_street=listing.get("address_street"),
            address_ward=listing.get("address_ward"),
            address_district=listing.get("address_district"),
            contact_phone=listing.get("contact_phone"),
            accuracy_level=accuracy_level
        )
        
        if created:
            stats.houses_created += 1
        else:
            stats.houses_reused += 1
        
        logger.info(f"House: id={house_id}, geo_id={house_geo_id}, created={created}")
        
        # Step 4: Create room (default room_id=00 for whole house)
        room_id, room_geo_id = create_room(
            conn=conn,
            house_id=house_id,
            room_number=None,  # Default to 00
            status=listing.get("status", "available")
        )
        stats.rooms_created += 1
        
        logger.info(f"Room: id={room_id}, geo_id={room_geo_id}")
        
        # Step 5: Fetch attributes from old schema
        attributes = fetch_listing_attributes(conn, uuid)
        
        # Step 6: Create room_history snapshot
        history_id = create_room_history(
            conn=conn,
            room_id=room_id,
            title=listing.get("title"),
            description=listing.get("description"),
            price_monthly_vnd=listing.get("price_monthly_vnd"),
            area_m2=listing.get("area_m2"),
            contact_phone=listing.get("contact_phone"),
            image_urls=listing.get("image_urls"),
            source_url=listing.get("source_url"),
            attributes=attributes,
            status=listing.get("status", "available"),
            is_current=True
        )
        
        logger.info(f"Room history: id={history_id}")
        
        # Step 7: Store UUID → GeoID mapping
        conn.execute(
            text("""
                INSERT INTO uuid_to_geoid_mapping 
                (old_uuid, new_room_id, new_geo_id, new_house_id, old_source_url)
                VALUES (:uuid, :room_id, :geo_id, :house_id, :source_url)
            """),
            {
                "uuid": uuid,
                "room_id": room_id,
                "geo_id": room_geo_id,
                "house_id": house_id,
                "source_url": listing.get("source_url")
            }
        )
        
        logger.info(f"✓ Migrated: {uuid} → {room_geo_id}")
        stats.migrated_listings += 1
        
        return True, room_geo_id
        
    except Exception as e:
        logger.error(f"✗ Failed to migrate UUID={uuid}: {e}")
        stats.failed_listings += 1
        stats.errors.append({"uuid": uuid, "error": str(e)})
        return False, str(e)


def validate_migration(conn, stats: MigrationStats):
    """
    Validate migration by comparing counts and sampling data.
    
    Args:
        conn: SQLAlchemy connection
        stats: MigrationStats object
    """
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION")
    logger.info("=" * 60)
    
    # Count old listings
    old_count = conn.execute(text("SELECT COUNT(*) FROM listings")).scalar()
    logger.info(f"Old listings table: {old_count} records")
    
    # Count new rooms
    new_count = conn.execute(text("SELECT COUNT(*) FROM rooms")).scalar()
    logger.info(f"New rooms table: {new_count} records")
    
    # Count room_history
    history_count = conn.execute(text("SELECT COUNT(*) FROM room_history WHERE is_current = TRUE")).scalar()
    logger.info(f"Current room_history: {history_count} records")
    
    # Count houses
    house_count = conn.execute(text("SELECT COUNT(*) FROM houses")).scalar()
    logger.info(f"Houses created: {house_count} records")
    
    # Check mapping
    mapping_count = conn.execute(text("SELECT COUNT(*) FROM uuid_to_geoid_mapping")).scalar()
    logger.info(f"UUID → GeoID mappings: {mapping_count} records")
    
    # Validation checks
    if new_count == old_count:
        logger.info("✓ Room count matches old listing count")
    else:
        logger.warning(f"✗ Mismatch: {new_count} rooms vs {old_count} old listings")
    
    if history_count == new_count:
        logger.info("✓ Room history count matches room count")
    else:
        logger.warning(f"✗ Mismatch: {history_count} history vs {new_count} rooms")
    
    # Sample comparison
    logger.info("\nSample GeoID mappings (first 5):")
    sample = conn.execute(text("""
        SELECT old_uuid, new_geo_id, old_source_url
        FROM uuid_to_geoid_mapping
        ORDER BY migrated_at
        LIMIT 5
    """))
    
    for row in sample:
        logger.info(f"  {row[0]} → {row[1]} ({row[2][:50]}...)")


def main():
    """Main migration execution."""
    parser = argparse.ArgumentParser(description='Migrate from UUID to GeoID system')
    parser.add_argument('--dry-run', action='store_true', help='Run without committing changes')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of listings per batch')
    parser.add_argument('--limit', type=int, help='Limit total number of listings to migrate')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("NHAMINHBACH UUID → GEOID MIGRATION")
    logger.info("=" * 60)
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Limit: {args.limit or 'None (all listings)'}")
    logger.info("=" * 60)
    
    # Get database connection
    engine = get_database_connection()
    stats = MigrationStats()
    
    try:
        with engine.begin() as conn:
            # Fetch total count
            total = conn.execute(text("SELECT COUNT(*) FROM listings")).scalar()
            stats.total_listings = min(total, args.limit) if args.limit else total
            logger.info(f"Total listings to migrate: {stats.total_listings}")
            
            # Process in batches
            offset = 0
            batch_num = 1
            
            while offset < stats.total_listings:
                current_batch_size = min(args.batch_size, stats.total_listings - offset)
                logger.info(f"\n--- Batch {batch_num} (offset={offset}, size={current_batch_size}) ---")
                
                # Fetch batch
                listings = fetch_old_listings(conn, limit=current_batch_size, offset=offset)
                
                # Migrate each listing
                for listing in listings:
                    success, result = migrate_listing(conn, listing, stats, dry_run=args.dry_run)
                
                offset += current_batch_size
                batch_num += 1
                
                # Commit batch (unless dry run)
                if not args.dry_run:
                    conn.commit()
                    logger.info(f"✓ Batch {batch_num - 1} committed")
                else:
                    logger.info(f"(Dry run - changes not committed)")
            
            # Validation
            validate_migration(conn, stats)
            
            # Rollback if dry run
            if args.dry_run:
                logger.info("\nDRY RUN - Rolling back all changes")
                conn.rollback()
            else:
                logger.info("\nCommitting final changes")
                conn.commit()
        
        # Print summary
        stats.log_summary()
        
        if stats.failed_listings > 0:
            logger.error(f"\n⚠️  Migration completed with {stats.failed_listings} errors")
            sys.exit(1)
        else:
            logger.info("\n✅ Migration completed successfully!")
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error during migration: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
