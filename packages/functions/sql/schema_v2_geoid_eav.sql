-- =========================================================================
-- NHAMINHBACH GEOID DATABASE SCHEMA V2.2 (JSONB Attributes)
-- =========================================================================
-- Purpose: GeoID-based schema with JSONB flexible attributes
-- Author: CTO Alex + AI Agent
-- Date: 2025-12-02
-- Status: PRODUCTION READY
-- 
-- Architecture:
--   - Static Layer: houses (physical properties with GiST geo index)
--   - Room Layer: rooms (individual units)
--   - Dynamic Layer: room_history (SCD Type 2 + JSONB attributes)
--   - Dictionary Layer: attributes (metadata/schema for attributes)
--   - Routing Layer: geo_aliases (smart URLs)
--   - Migration Layer: uuid_to_geoid_mapping (backwards compatibility)
--
-- Key Design Decision:
--   Using JSONB for attributes in room_history instead of EAV junction table.
--   This reduces JOINs while maintaining queryability via GIN index.
--   The 'attributes' table serves as metadata dictionary (names, types, icons).
-- =========================================================================

-- =========================================================================
-- PART 0: EXTENSIONS & TYPES
-- =========================================================================

-- Enable UUID extension (for migration compatibility)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- NOTE: PostGIS must be enabled from Supabase Dashboard:
-- Database → Extensions → Search "postgis" → Enable
-- After enabling, uncomment the geo index in PART 1

-- Create ENUM types
CREATE TYPE listing_status AS ENUM ('available', 'rented', 'pending_review', 'rejected');
CREATE TYPE attribute_type AS ENUM ('boolean', 'string', 'integer', 'enum');

-- =========================================================================
-- PART 1: STATIC LAYER - Physical Assets (Bất biến)
-- =========================================================================

CREATE TABLE IF NOT EXISTS houses (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- GeoID Components
    geo_id VARCHAR(5) NOT NULL,  -- HHH portion (3 chars Base36: 000-ZZZ)
    city_code VARCHAR(2) NOT NULL DEFAULT '29',  -- Hà Nội
    ward_code VARCHAR(2) NOT NULL,  -- CG, ND, DD, etc. (123 wards in Hà Nội)

    -- Official ID (Số khung - Dùng cho Định danh Tài sản)
    -- Mapping theo chuẩn Tổng cục Thống kê & Bộ TNMT
    admin_city_code VARCHAR(10) DEFAULT '01',    -- Mã TP Hà Nội
    admin_district_code VARCHAR(10),             -- Mã Quận (005)
    admin_ward_code VARCHAR(10),                 -- Mã Phường (00169)
    
    -- Land Registry (Sổ đỏ - The Holy Grail)
    -- Initially NULL, populated when verified
    land_map_sheet_number VARCHAR(20),  -- Số Tờ bản đồ
    land_parcel_number VARCHAR(20),     -- Số Thửa đất
    land_certificate_id VARCHAR(50),    -- Số vào sổ (Sổ đỏ/hồng)
    
    -- Full GeoID (Computed, Indexed)
    full_geo_id VARCHAR(10) GENERATED ALWAYS AS (
        city_code || ward_code || '.' || geo_id
    ) STORED,
    
    -- Geographic Data (Immutable once verified)
    latitude NUMERIC(10, 8),  -- Precision: ~1.1mm
    longitude NUMERIC(11, 8),
    
    -- Address Components
    address_street TEXT,
    address_ward TEXT,
    address_district TEXT,
    
    -- Data Quality
    accuracy_level INTEGER DEFAULT 2,  -- 1=Verified (pin map), 2=Fuzzy (circle map)
    
    -- Deduplication Fingerprints
    address_hash VARCHAR(64),  -- SHA256 of normalized address
    phone_hash VARCHAR(64),    -- SHA256 of phone+street for anonymous posts
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(city_code, ward_code, geo_id),
    CHECK (LENGTH(geo_id) <= 5),
    CHECK (accuracy_level IN (1, 2))
);

-- Indexes for houses
CREATE INDEX idx_houses_full_geo_id ON houses(full_geo_id);
CREATE INDEX idx_houses_ward ON houses(ward_code);
CREATE INDEX idx_houses_district ON houses(address_district);
CREATE INDEX idx_houses_address_hash ON houses(address_hash);
CREATE INDEX idx_houses_phone_hash ON houses(phone_hash);

-- Simple B-tree index on coordinates (works without PostGIS)
CREATE INDEX idx_houses_coords ON houses(latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- =========================================================================
-- OPTIONAL: GiST Geography Index (Requires PostGIS extension)
-- =========================================================================
-- Enable PostGIS from Supabase Dashboard first, then run this separately:
--
-- CREATE INDEX idx_houses_geo_point ON houses 
--     USING GIST (
--         ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
--     )
--     WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
--
-- This enables efficient radius search: "Tìm phòng quanh đây"
-- =========================================================================

-- Comments
COMMENT ON TABLE houses IS 'Static layer: Physical buildings/properties with stable geographic identity';
COMMENT ON COLUMN houses.geo_id IS 'House portion of GeoID (HHH): 3-char Base36, expandable with leading 0';
COMMENT ON COLUMN houses.full_geo_id IS 'Complete GeoID: 29CG.0AB format (city+ward+house)';
COMMENT ON COLUMN houses.accuracy_level IS '1=Verified address with exact coordinates, 2=Fuzzy location (street-level)';

-- =========================================================================
-- PART 2: ROOM LAYER - Individual Units
-- =========================================================================

CREATE TABLE IF NOT EXISTS rooms (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Foreign Key to House
    house_id INTEGER NOT NULL REFERENCES houses(id) ON DELETE CASCADE,
    
    -- Room ID Component
    room_id VARCHAR(2) NOT NULL DEFAULT '00',  -- RR portion (00-ZZ Base36)
    
    -- Full GeoID (Maintained by trigger)
    full_geo_id VARCHAR(12),
    
    -- Current Status
    current_status listing_status DEFAULT 'pending_review',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(house_id, room_id),
    CHECK (LENGTH(room_id) = 2)
);

-- Indexes for rooms
CREATE INDEX idx_rooms_full_geo_id ON rooms(full_geo_id);
CREATE INDEX idx_rooms_house_id ON rooms(house_id);
CREATE INDEX idx_rooms_status ON rooms(current_status);

-- Comments
COMMENT ON TABLE rooms IS 'Individual rental units within a house (room_id=00 means whole house or unknown)';
COMMENT ON COLUMN rooms.room_id IS 'Room portion of GeoID (RR): 2-char Base36, 00=whole house/unknown';
COMMENT ON COLUMN rooms.full_geo_id IS 'Complete GeoID: 29CG.0AB01 format (city+ward+house+room)';

-- =========================================================================
-- PART 3: DYNAMIC LAYER - Time Machine (SCD Type 2)
-- =========================================================================

CREATE TABLE IF NOT EXISTS room_history (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Foreign Key to Room
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    
    -- Listing Data Snapshot
    title TEXT,
    description TEXT,
    price_monthly_vnd BIGINT,
    area_m2 NUMERIC(6, 2),
    contact_phone TEXT,
    image_urls TEXT[],
    source_url TEXT,
    
    -- Flexible Attributes (JSONB - NoSQL power with SQL queryability)
    -- Example: {"air_conditioner": true, "water_heater": true, "furniture": "full", "floor_number": 3}
    -- Use 'attributes' table as dictionary for metadata (display names, types, icons)
    attributes JSONB DEFAULT '{}',
    
    -- SCD Type 2 Fields (Slowly Changing Dimension)
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE,  -- NULL = current/active version
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Status at this point in time
    status listing_status DEFAULT 'pending_review',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CHECK ((is_current = TRUE AND valid_to IS NULL) OR (is_current = FALSE AND valid_to IS NOT NULL))
);

-- Indexes for room_history
CREATE INDEX idx_room_history_room_current ON room_history(room_id, is_current) WHERE is_current = TRUE;
CREATE INDEX idx_room_history_valid_period ON room_history(valid_from, valid_to);
CREATE INDEX idx_room_history_source_url ON room_history(source_url);
CREATE INDEX idx_room_history_status ON room_history(status);
CREATE INDEX idx_room_history_price ON room_history(price_monthly_vnd) WHERE is_current = TRUE;

-- GIN index for JSONB attributes (fast @>, ?, ?& queries)
CREATE INDEX idx_room_history_attributes ON room_history USING GIN(attributes);

-- Comments
COMMENT ON TABLE room_history IS 'Time-series data for rooms: tracks all changes in price, attributes, status over time';
COMMENT ON COLUMN room_history.valid_from IS 'Start timestamp of this version';
COMMENT ON COLUMN room_history.valid_to IS 'End timestamp (NULL=current/active)';
COMMENT ON COLUMN room_history.is_current IS 'TRUE only for the latest active version';
COMMENT ON COLUMN room_history.attributes IS 'JSONB snapshot of amenities: {"air_conditioner": true, "furniture": "full"}';

-- =========================================================================
-- PART 4: ATTRIBUTE DICTIONARY - Metadata for JSONB attributes
-- =========================================================================
-- This table defines the "schema" of flexible attributes stored in room_history.attributes JSONB
-- It provides: display names, data types, validation rules, icons, display order
-- The actual values are stored in room_history.attributes JSONB column (no JOINs needed!)

-- Attributes Definition Table (The "Dictionary" of the system)
CREATE TABLE IF NOT EXISTS attributes (
    id SERIAL PRIMARY KEY,
    type attribute_type NOT NULL,
    name TEXT NOT NULL,              -- Vietnamese display name: "Điều hoà"
    slug TEXT NOT NULL,              -- Machine-readable JSONB key: "air_conditioner" (UNIQUE)
    icon TEXT,                       -- Icon name/class for UI: "snowflake", "thermometer"
    possible_values TEXT[],          -- For ENUM type: allowed values array
    description TEXT,                -- Help text for QC cockpit
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT uq_attributes_slug UNIQUE (slug)
);

-- Indexes for attributes
CREATE UNIQUE INDEX idx_attributes_slug ON attributes(slug);
CREATE INDEX idx_attributes_type ON attributes(type);
CREATE INDEX idx_attributes_active ON attributes(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_attributes_display_order ON attributes(display_order);

-- Comments
COMMENT ON TABLE attributes IS 'Dictionary/metadata for room_history.attributes JSONB keys';
COMMENT ON COLUMN attributes.type IS 'Data type for validation: boolean, string, integer, enum';
COMMENT ON COLUMN attributes.slug IS 'UNIQUE machine-readable key used in JSONB: air_conditioner, furniture, etc.';
COMMENT ON COLUMN attributes.icon IS 'Icon identifier for UI rendering';
COMMENT ON COLUMN attributes.possible_values IS 'For enum type: array of allowed values for validation';

-- =========================================================================
-- PART 5: ALIAS & ROUTING LAYER - Smart URLs
-- =========================================================================

CREATE TABLE IF NOT EXISTS geo_aliases (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Alias Slug
    alias VARCHAR(50) NOT NULL UNIQUE,  -- e.g., 'svbk', 'nhatrogiarecaugiay'
    
    -- Routing Configuration
    route_type VARCHAR(20) NOT NULL,  -- 'filter', 'room', 'house'
    target_geo_id VARCHAR(12),  -- For room/house type: 29CG.AB1
    filter_config JSONB,  -- For filter type: {"district": "CG", "radius_km": 2, "max_price": 4000000}
    
    -- Redirect Behavior
    redirect_type VARCHAR(10) DEFAULT '301',  -- 301 permanent, 302 temporary
    
    -- Analytics
    click_count INTEGER DEFAULT 0,
    last_clicked_at TIMESTAMP WITH TIME ZONE,
    
    -- Lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CHECK (route_type IN ('filter', 'room', 'house')),
    CHECK (redirect_type IN ('301', '302')),
    CHECK (
        (route_type IN ('room', 'house') AND target_geo_id IS NOT NULL) OR
        (route_type = 'filter' AND filter_config IS NOT NULL)
    )
);

-- Indexes for geo_aliases
CREATE INDEX idx_geo_aliases_alias ON geo_aliases(alias) WHERE is_active = TRUE;
CREATE INDEX idx_geo_aliases_route_type ON geo_aliases(route_type);
CREATE INDEX idx_geo_aliases_target ON geo_aliases(target_geo_id);

-- Comments
COMMENT ON TABLE geo_aliases IS 'Campaign URLs and smart aliases: svbk → filter students near BK';
COMMENT ON COLUMN geo_aliases.filter_config IS 'JSON filter params: {ward, radius_km, max_price, amenities}';

-- =========================================================================
-- PART 6: MIGRATION SUPPORT - Backwards Compatibility
-- =========================================================================

CREATE TABLE IF NOT EXISTS uuid_to_geoid_mapping (
    -- Old System
    old_uuid UUID PRIMARY KEY,
    old_source_url TEXT,
    
    -- New System
    new_room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    new_geo_id VARCHAR(12),
    new_house_id INTEGER REFERENCES houses(id) ON DELETE SET NULL,
    
    -- Migration Metadata
    migrated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    migration_batch INTEGER
);

-- Indexes for migration mapping
CREATE INDEX idx_uuid_mapping_geo_id ON uuid_to_geoid_mapping(new_geo_id);
CREATE INDEX idx_uuid_mapping_room_id ON uuid_to_geoid_mapping(new_room_id);

-- Comments
COMMENT ON TABLE uuid_to_geoid_mapping IS 'Temporary: UUID → GeoID migration tracking for backwards compatibility';

-- =========================================================================
-- PART 7: HELPER FUNCTIONS & TRIGGERS
-- =========================================================================

-- Function: Calculate room.full_geo_id from parent house
CREATE OR REPLACE FUNCTION calc_room_full_geoid()
RETURNS TRIGGER AS $$
DECLARE
    parent_geo_id VARCHAR(10);
BEGIN
    SELECT full_geo_id INTO parent_geo_id FROM houses WHERE id = NEW.house_id;
    NEW.full_geo_id := parent_geo_id || NEW.room_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rooms_calc_geoid
    BEFORE INSERT OR UPDATE OF house_id, room_id ON rooms
    FOR EACH ROW
    EXECUTE FUNCTION calc_room_full_geoid();

-- Function: Update room.current_status when room_history changes
CREATE OR REPLACE FUNCTION update_room_current_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_current = TRUE THEN
        UPDATE rooms 
        SET current_status = NEW.status,
            updated_at = NOW()
        WHERE id = NEW.room_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_room_history_update_status
    AFTER INSERT OR UPDATE OF is_current, status ON room_history
    FOR EACH ROW
    WHEN (NEW.is_current = TRUE)
    EXECUTE FUNCTION update_room_current_status();

-- Function: Close previous room_history version when new one is created
CREATE OR REPLACE FUNCTION close_previous_room_history()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_current = TRUE THEN
        UPDATE room_history
        SET is_current = FALSE,
            valid_to = NEW.valid_from
        WHERE room_id = NEW.room_id
          AND is_current = TRUE
          AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_room_history_close_previous
    AFTER INSERT ON room_history
    FOR EACH ROW
    WHEN (NEW.is_current = TRUE)
    EXECUTE FUNCTION close_previous_room_history();

-- Function: Auto-update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_houses_update_timestamp
    BEFORE UPDATE ON houses
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_rooms_update_timestamp
    BEFORE UPDATE ON rooms
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- =========================================================================
-- PART 8: SEED DATA - Default Attributes
-- =========================================================================

-- Seed the attributes dictionary with Vietnamese room attributes
-- These define metadata for room_history.attributes JSONB keys
INSERT INTO attributes (type, name, slug, icon, possible_values, description, display_order) VALUES
    -- Tiện ích chung (Boolean) - General Amenities
    ('boolean', 'Điều hoà', 'air_conditioner', 'snowflake', NULL, 'Phòng có điều hoà không?', 10),
    ('boolean', 'Nóng lạnh', 'water_heater', 'thermometer', NULL, 'Phòng có bình nóng lạnh không?', 20),
    ('boolean', 'Thang máy', 'elevator', 'arrow-up-down', NULL, 'Toà nhà có thang máy không?', 30),
    ('boolean', 'Khoá vân tay', 'fingerprint_lock', 'fingerprint', NULL, 'Cửa có khoá vân tay/thẻ từ không?', 40),
    ('boolean', 'Cho phép vật nuôi', 'allows_pets', 'paw-print', NULL, 'Có được nuôi chó mèo không?', 50),
    ('boolean', 'Chung chủ', 'owner_occupied', 'users', NULL, 'Chủ nhà có ở cùng không?', 60),
    ('boolean', 'Ban công', 'balcony', 'sun', NULL, 'Phòng có ban công không?', 70),
    ('boolean', 'Cửa sổ', 'window', 'square', NULL, 'Phòng có cửa sổ không?', 80),
    ('boolean', 'Tủ lạnh', 'refrigerator', 'refrigerator', NULL, 'Phòng có tủ lạnh không?', 90),
    ('boolean', 'Máy giặt', 'washing_machine', 'washing-machine', NULL, 'Có máy giặt không?', 100),
    ('boolean', 'Wifi', 'wifi', 'wifi', NULL, 'Có wifi miễn phí không?', 110),
    ('boolean', 'Giữ xe', 'parking', 'car', NULL, 'Có chỗ để xe không?', 120),

    -- Chính sách & Quy định (Enum) - Policies
    ('enum', 'Đối tượng cho thuê', 'guest_policy', 'user-check', ARRAY['female_only', 'male_only', 'any'], 'Cho nam/nữ/tất cả thuê?', 200),
    ('enum', 'Giờ giấc', 'access_hours', 'clock', ARRAY['free', 'restricted'], 'Có giờ giấc không?', 210),
    ('enum', 'Loại bếp', 'kitchen_type', 'utensils', ARRAY['private', 'shared', 'none'], 'Bếp riêng hay chung?', 220),
    ('enum', 'Loại vệ sinh', 'bathroom_type', 'bath', ARRAY['private', 'shared'], 'WC riêng hay chung?', 230),
    ('enum', 'Nội thất', 'furniture', 'sofa', ARRAY['none', 'basic', 'full'], 'Mức độ nội thất?', 240),
    ('enum', 'Loại phòng', 'room_type', 'home', ARRAY['single', 'shared', 'studio', 'apartment'], 'Loại hình phòng?', 250),

    -- Thông số số lượng (Integer) - Numeric specs
    ('integer', 'Số người chung bếp', 'kitchen_sharers_count', 'users', NULL, 'Bao nhiêu người dùng chung bếp?', 300),
    ('integer', 'Số người chung vệ sinh', 'bathroom_sharers_count', 'users', NULL, 'Bao nhiêu người dùng chung WC?', 310),
    ('integer', 'Số người hiện tại', 'current_occupants', 'user', NULL, 'Hiện có bao nhiêu người ở?', 320),
    ('integer', 'Cần tìm thêm người', 'needed_occupants', 'user-plus', NULL, 'Cần tìm thêm bao nhiêu người?', 330),
    ('integer', 'Ở tối đa', 'max_occupants', 'users', NULL, 'Tối đa bao nhiêu người?', 340),
    ('integer', 'Số xe tối đa', 'parking_limit', 'bike', NULL, 'Để được tối đa bao nhiêu xe?', 350),
    ('integer', 'Tầng', 'floor_number', 'layers', NULL, 'Phòng ở tầng mấy?', 360),
    ('integer', 'Tiền điện (đ/kWh)', 'electricity_price', 'zap', NULL, 'Giá điện bao nhiêu đ/kWh?', 370),
    ('integer', 'Tiền nước (đ/m³)', 'water_price', 'droplet', NULL, 'Giá nước bao nhiêu đ/m³?', 380),
    ('integer', 'Đặt cọc (tháng)', 'deposit_months', 'banknote', NULL, 'Đặt cọc bao nhiêu tháng?', 390)
ON CONFLICT (slug) DO NOTHING;

-- =========================================================================
-- PART 9: USEFUL VIEWS
-- =========================================================================

-- View: Current listings with full info (replaces legacy "listings" table usage)
CREATE OR REPLACE VIEW v_current_listings AS
SELECT 
    r.id AS room_id,
    r.full_geo_id,
    h.address_street,
    h.address_ward,
    h.address_district,
    h.latitude,
    h.longitude,
    h.accuracy_level,
    rh.id AS room_history_id,
    rh.title,
    rh.description,
    rh.price_monthly_vnd,
    rh.area_m2,
    rh.contact_phone,
    rh.image_urls,
    rh.source_url,
    rh.attributes,  -- JSONB attributes included
    rh.status,
    rh.valid_from,
    rh.created_at
FROM rooms r
JOIN houses h ON h.id = r.house_id
JOIN room_history rh ON rh.room_id = r.id AND rh.is_current = TRUE;

-- Comment
COMMENT ON VIEW v_current_listings IS 'Convenience view: Current active listings with all fields joined';

-- =========================================================================
-- PART 10: SAMPLE QUERIES (For Testing & Reference)
-- =========================================================================

-- Get current listing by GeoID
-- SELECT * FROM v_current_listings WHERE full_geo_id LIKE '29CG.0AB%';

-- Get JSONB attributes for a listing (no JOINs needed!)
-- SELECT 
--     full_geo_id,
--     title,
--     attributes->>'air_conditioner' AS has_ac,
--     attributes->>'furniture' AS furniture_level,
--     (attributes->>'floor_number')::int AS floor
-- FROM v_current_listings
-- WHERE room_history_id = 123;

-- Get price history for a room
-- SELECT valid_from, valid_to, price_monthly_vnd, status, attributes
-- FROM room_history
-- WHERE room_id = 123
-- ORDER BY valid_from DESC;

-- Search with JSONB attribute filter (e.g., has air conditioner)
-- SELECT * FROM v_current_listings
-- WHERE status = 'available'
--   AND (attributes->>'air_conditioner')::boolean = true;

-- Search with multiple JSONB filters
-- SELECT * FROM v_current_listings
-- WHERE status = 'available'
--   AND attributes @> '{"air_conditioner": true, "bathroom_type": "private"}';

-- Check if attribute exists
-- SELECT * FROM v_current_listings
-- WHERE attributes ? 'wifi';

-- =========================================================================
-- RADIUS SEARCH - "Tìm phòng quanh đây" (Find rooms nearby)
-- =========================================================================
-- Find all houses within 2km of a point (uses GiST index)
-- SELECT h.*, ST_Distance(
--     ST_SetSRID(ST_MakePoint(h.longitude, h.latitude), 4326)::geography,
--     ST_SetSRID(ST_MakePoint(105.8342, 21.0278), 4326)::geography  -- Center point
-- ) AS distance_meters
-- FROM houses h
-- WHERE ST_DWithin(
--     ST_SetSRID(ST_MakePoint(h.longitude, h.latitude), 4326)::geography,
--     ST_SetSRID(ST_MakePoint(105.8342, 21.0278), 4326)::geography,
--     2000  -- 2000 meters = 2km radius
-- )
-- ORDER BY distance_meters;

-- =========================================================================
-- CONFIRMATION
-- =========================================================================

-- =========================================================================
-- ✅ SCHEMA V2.2 (GeoID + JSONB Attributes) - READY TO DEPLOY
-- =========================================================================
-- Tables created:
--   - houses (static physical assets)
--   - rooms (individual units)
--   - room_history (SCD Type 2 + JSONB attributes column + GIN index)
--   - attributes (dictionary/metadata for JSONB keys)
--   - geo_aliases (smart URL routing)
--   - uuid_to_geoid_mapping (migration support)
--
-- Views created:
--   - v_current_listings (includes JSONB attributes)
--
-- Seed data:
--   - 26 attribute definitions with icons
--
-- Query examples:
--   - Filter by attribute: WHERE attributes @> '{"air_conditioner": true}'
--   - Check attribute exists: WHERE attributes ? 'wifi'
-- =========================================================================
