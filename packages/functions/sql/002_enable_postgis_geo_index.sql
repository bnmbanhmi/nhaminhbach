-- =========================================================================
-- NHAMINHBACH - POSTGIS GEO INDEX
-- =========================================================================
-- Purpose: Create GiST geography index for radius search
-- Prerequisite: Enable PostGIS from Supabase Dashboard first!
--   Database → Extensions → Search "postgis" → Enable
-- 
-- Run this AFTER schema_v2_geoid_eav.sql and AFTER enabling PostGIS
-- =========================================================================

-- Verify PostGIS is enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
        RAISE EXCEPTION '
========================================================================
⛔ POSTGIS NOT ENABLED!
========================================================================
Please enable PostGIS from Supabase Dashboard first:
  1. Go to Database → Extensions
  2. Search for "postgis"
  3. Click Enable
  4. Wait for it to complete
  5. Run this script again
========================================================================';
    END IF;
    
    RAISE NOTICE '✅ PostGIS is enabled. Creating geography index...';
END $$;

-- Drop existing index if any (from previous attempts)
DROP INDEX IF EXISTS idx_houses_geo_point;

-- Create GiST geography index for efficient radius search
-- This enables: "Tìm phòng quanh đây" (Find rooms nearby)
CREATE INDEX idx_houses_geo_point ON houses 
    USING GIST (
        geography(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326))
    )
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Confirmation
DO $$
BEGIN
    RAISE NOTICE '
========================================================================
✅ GIST GEOGRAPHY INDEX CREATED SUCCESSFULLY
========================================================================
Index name: idx_houses_geo_point
Type: GiST on geography(Point)

You can now use radius search queries:

-- Find houses within 2km of a point
SELECT h.*, 
    ST_Distance(
        geography(ST_SetSRID(ST_MakePoint(h.longitude, h.latitude), 4326)),
        geography(ST_SetSRID(ST_MakePoint(105.8342, 21.0278), 4326))
    ) AS distance_meters
FROM houses h
WHERE ST_DWithin(
    geography(ST_SetSRID(ST_MakePoint(h.longitude, h.latitude), 4326)),
    geography(ST_SetSRID(ST_MakePoint(105.8342, 21.0278), 4326)),
    2000  -- 2km radius in meters
)
ORDER BY distance_meters;
========================================================================';
END $$;
