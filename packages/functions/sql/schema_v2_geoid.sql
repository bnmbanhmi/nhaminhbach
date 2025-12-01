-- =========================================================================
-- NHAMINHBACH GEOID DATABASE SCHEMA V2.0
-- =========================================================================
-- Purpose: Redesign from UUID-based to GeoID-based (29CG.HHHRR format)
-- Author: CTO Alex + AI Agent
-- Date: 2025-12-01
-- Status: DRAFT - Pending Review
-- =========================================================================

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

    -- 3. OFFICIAL ID (Số khung - Dùng cho Định danh Tài sản) -> THÊM MỚI
    -- Mapping theo chuẩn Tổng cục Thống kê & Bộ TNMT
    admin_city_code VARCHAR(10) DEFAULT '01',    -- Mã TP Hà Nội
    admin_district_code VARCHAR(10),             -- Mã Quận (005)
    admin_ward_code VARCHAR(10),                 -- Mã Phường (00169)
    
    -- CẤP ĐỘ SỔ ĐỎ (The Holy Grail of Asset ID)
    -- Dữ liệu này cực quý, ban đầu sẽ NULL, sau này verified sẽ điền vào
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(city_code, ward_code, geo_id),
    CHECK (LENGTH(geo_id) <= 5),
    CHECK (accuracy_level IN (1, 2))
);

-- Indexes for houses
CREATE INDEX idx_houses_full_geo_id ON houses(full_geo_id);
CREATE INDEX idx_houses_ward ON houses(ward_code);
CREATE INDEX idx_houses_coords ON houses(latitude, longitude);
CREATE INDEX idx_houses_address_hash ON houses(address_hash);
CREATE INDEX idx_houses_phone_hash ON houses(phone_hash);

-- Comments
COMMENT ON TABLE houses IS 'Static layer: Physical buildings/properties with stable geographic identity';
COMMENT ON COLUMN houses.geo_id IS 'House portion of GeoID (HHH): 3-char Base36, expandable with leading 0';
COMMENT ON COLUMN houses.full_geo_id IS 'Complete GeoID: 29CG.0AB format (city+ward+house)';
COMMENT ON COLUMN houses.accuracy_level IS '1=Verified address with exact coordinates, 2=Fuzzy location (street-level)';
COMMENT ON COLUMN houses.address_hash IS 'SHA256(city|ward|street|number) for deduplication';
COMMENT ON COLUMN houses.phone_hash IS 'SHA256(phone|street) for anonymous post deduplication';

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
    
    -- Full GeoID (Maintained by trigger; cannot reference other table in GENERATED column)
    full_geo_id VARCHAR(12),
    
    -- Current Status
    current_status VARCHAR(20) DEFAULT 'available',  -- available, rented, pending_review, rejected
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(house_id, room_id),
    CHECK (LENGTH(room_id) = 2),
    CHECK (current_status IN ('available', 'rented', 'pending_review', 'rejected'))
);

-- Trigger to populate rooms.full_geo_id based on parent house GeoID
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

-- Indexes for rooms
CREATE INDEX idx_rooms_full_geo_id ON rooms(full_geo_id);
CREATE INDEX idx_rooms_house_id ON rooms(house_id);
CREATE INDEX idx_rooms_status ON rooms(current_status);

-- Comments
COMMENT ON TABLE rooms IS 'Individual rental units within a house (can be whole house if room_id=00)';
COMMENT ON COLUMN rooms.room_id IS 'Room portion of GeoID (RR): 2-char Base36, 00=whole house/unknown';
COMMENT ON COLUMN rooms.full_geo_id IS 'Complete GeoID: 29CG.0AB01 format (city+district+house+room)';
COMMENT ON COLUMN rooms.current_status IS 'Latest status, synchronized from room_history is_current record';

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
    price_monthly_vnd INTEGER,
    area_m2 NUMERIC(6, 2),
    contact_phone TEXT,
    image_urls TEXT[],
    source_url TEXT,
    
    -- Attributes (Denormalized JSONB for performance)
    attributes JSONB DEFAULT '{}',
    
    -- SCD Type 2 Fields (Slowly Changing Dimension)
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,  -- NULL = current/active version
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Status at this point in time
    status VARCHAR(20) DEFAULT 'pending_review',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (status IN ('available', 'rented', 'pending_review', 'rejected')),
    CHECK ((is_current = TRUE AND valid_to IS NULL) OR (is_current = FALSE AND valid_to IS NOT NULL))
);

-- Indexes for room_history
CREATE INDEX idx_room_history_room_current ON room_history(room_id, is_current) WHERE is_current = TRUE;
CREATE INDEX idx_room_history_valid_period ON room_history(valid_from, valid_to);
CREATE INDEX idx_room_history_source_url ON room_history(source_url);
CREATE INDEX idx_room_history_status ON room_history(status);
CREATE INDEX idx_room_history_price ON room_history(price_monthly_vnd) WHERE is_current = TRUE;

-- GIN index for JSONB attributes
CREATE INDEX idx_room_history_attributes ON room_history USING GIN(attributes);

-- Comments
COMMENT ON TABLE room_history IS 'Time-series data for rooms: tracks all changes in price, attributes, status over time';
COMMENT ON COLUMN room_history.valid_from IS 'Start timestamp of this version';
COMMENT ON COLUMN room_history.valid_to IS 'End timestamp (NULL=current/active)';
COMMENT ON COLUMN room_history.is_current IS 'TRUE only for the latest active version';
COMMENT ON COLUMN room_history.attributes IS 'JSONB snapshot of amenities at this point in time: {air_conditioner: true, furniture: "full"}';

-- =========================================================================
-- PART 4: ALIAS & ROUTING LAYER - Smart URLs
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
    last_clicked_at TIMESTAMP,
    
    -- Lifecycle
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
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
COMMENT ON TABLE geo_aliases IS 'Campaign URLs and smart aliases: svbk → filter students near BK, 29CGAB1 → specific room';
COMMENT ON COLUMN geo_aliases.alias IS 'Short memorable slug: svbk, nhatrogiarecaugiay, etc.';
COMMENT ON COLUMN geo_aliases.route_type IS 'filter=dynamic search, room=specific unit, house=all rooms in building';
COMMENT ON COLUMN geo_aliases.filter_config IS 'JSON filter params: {district, radius_km, max_price, amenities, etc.}';

-- =========================================================================
-- PART 5: MIGRATION SUPPORT - Temporary Mapping Table
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
    migrated_at TIMESTAMP DEFAULT NOW(),
    migration_batch INTEGER,
    
    -- Constraints
    CHECK (new_room_id IS NOT NULL OR new_geo_id IS NOT NULL)
);

-- Indexes for migration mapping
CREATE INDEX idx_uuid_mapping_geo_id ON uuid_to_geoid_mapping(new_geo_id);
CREATE INDEX idx_uuid_mapping_room_id ON uuid_to_geoid_mapping(new_room_id);

-- Comments
COMMENT ON TABLE uuid_to_geoid_mapping IS 'Temporary table for UUID → GeoID migration tracking and backwards compatibility';

-- =========================================================================
-- PART 6: HELPER FUNCTIONS & TRIGGERS
-- =========================================================================

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

-- Trigger: Auto-update room status
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

-- Trigger: Auto-close previous versions
CREATE TRIGGER trg_room_history_close_previous
    AFTER INSERT ON room_history
    FOR EACH ROW
    WHEN (NEW.is_current = TRUE)
    EXECUTE FUNCTION close_previous_room_history();

-- Function: Update houses.updated_at timestamp
CREATE OR REPLACE FUNCTION update_houses_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update houses timestamp
CREATE TRIGGER trg_houses_update_timestamp
    BEFORE UPDATE ON houses
    FOR EACH ROW
    EXECUTE FUNCTION update_houses_timestamp();

-- Function: Update rooms.updated_at timestamp
CREATE OR REPLACE FUNCTION update_rooms_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update rooms timestamp
CREATE TRIGGER trg_rooms_update_timestamp
    BEFORE UPDATE ON rooms
    FOR EACH ROW
    EXECUTE FUNCTION update_rooms_timestamp();

-- =========================================================================
-- PART 7: SAMPLE QUERIES (For Testing & Reference)
-- =========================================================================

-- Get current listing by GeoID
-- SELECT 
--     h.full_geo_id,
--     r.room_id,
--     rh.*
-- FROM houses h
-- JOIN rooms r ON r.house_id = h.id
-- JOIN room_history rh ON rh.room_id = r.id
-- WHERE h.full_geo_id = '29CG.0AB'
--   AND r.room_id = '01'
--   AND rh.is_current = TRUE;

-- Get price history for a room
-- SELECT 
--     valid_from,
--     valid_to,
--     price_monthly_vnd,
--     status
-- FROM room_history
-- WHERE room_id = 123
-- ORDER BY valid_from DESC;

-- Find all rooms in a house
-- SELECT 
--     r.full_geo_id,
--     r.current_status,
--     rh.price_monthly_vnd,
--     rh.area_m2
-- FROM rooms r
-- JOIN room_history rh ON rh.room_id = r.id
-- WHERE r.house_id = 456
--   AND rh.is_current = TRUE;

-- Search with filter
-- SELECT 
--     h.full_geo_id,
--     r.room_id,
--     rh.price_monthly_vnd,
--     rh.title
-- FROM houses h
-- JOIN rooms r ON r.house_id = h.id
-- JOIN room_history rh ON rh.room_id = r.id
-- WHERE h.ward_code = 'CG'
--   AND rh.is_current = TRUE
--   AND rh.status = 'available'
--   AND rh.price_monthly_vnd <= 5000000
-- ORDER BY rh.price_monthly_vnd ASC;

-- =========================================================================
-- END OF SCHEMA DEFINITION
-- =========================================================================
