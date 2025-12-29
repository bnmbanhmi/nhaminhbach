---
tags: #task-ai
status: #in-progress
owner: Minh
ai_agent: CTO Alex
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 16hr
complexity: Complex
priority: CRITICAL
---

# AI Task: Database Redesign with GeoID System

**Duration:** 16 hours  
**Complexity:** Complex  
**AI Agent:** CTO Alex  
**Priority:** CRITICAL - Core differentiator

## 🎯 Objective (AI Context)
**What:** Redesign database schema từ UUID-based sang GeoID-based (29CG.HHHRR format), implement ID generation algorithm, và migration strategy từ hệ thống hiện tại

**Why:** 
- GeoID là core differentiator của vision - semantic, hierarchical, human-friendly
- Enable campaign aliases, QR stickers, instant gratification UX
- Foundation cho time machine (price history) và scale strategy

**Success:** 
- New schema với `houses`, `rooms`, `room_history` tables deployed
- ID generation algorithm working (Base36, elastic padding)
- Migration script chạy thành công từ UUID → GeoID
- All existing data preserved với GeoID mới
- Public URLs chuyển từ `/listings/{uuid}` → `/{geoid}`

## 🏗️ Technical Design

### **A. GeoID Structure: `29CG.HHHRR`**

**Format:**
- `29`: City Code (Hà Nội - fixed)
- `CG`: District Code (2 chars, ví dụ: CG=Cầu Giấy, DD=Đống Đa, HD=Hoàn Kiếm)
- `HHH`: House ID (3 chars Base36, expandable với leading 0)
- `RR`: Room ID (2 chars Base36, `00` = whole house/unknown)

**Display Logic (ElasticID):**
- `29CG0AB01` → Display as `29CGAB1` (remove leading zeros khi có thể)
- `29CG00A0R` → Display as `29CGA.R` (optimize readability)
- Algorithm ưu tiên tránh collision toàn thành phố trước khi tạo ID dài

**Examples:**
```
29CG.AB1   → Cầu Giấy, House 0AB, Room 01 (compact)
29CG.W8K00 → Cầu Giấy, House W8K, Whole house
29DD.5M2   → Đống Đa, House 05M, Room 02
```

### **B. New Database Schema**

```sql
-- ===== STATIC LAYER (Bất biến) =====

CREATE TABLE houses (
    id SERIAL PRIMARY KEY,
    geo_id VARCHAR(5) NOT NULL UNIQUE,  -- HHH portion (3 chars Base36)
    city_code VARCHAR(2) NOT NULL DEFAULT '29',
    district_code VARCHAR(2) NOT NULL,  -- CG, DD, HD, etc.
    full_geo_id VARCHAR(10) GENERATED ALWAYS AS (city_code || district_code || '.' || geo_id) STORED,
    
    -- Geographic data (immutable once verified)
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    address_street TEXT,
    address_ward TEXT,
    address_district TEXT,
    accuracy_level INTEGER DEFAULT 2,  -- 1=Verified (pin), 2=Fuzzy (circle)
    
    -- Fingerprinting for deduplication
    address_hash VARCHAR(64),  -- Hash(City+Ward+Street+Number)
    phone_hash VARCHAR(64),    -- Hash(Phone+Street) for anonymous posts
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_full_geo_id (full_geo_id),
    INDEX idx_district (district_code),
    INDEX idx_coords (latitude, longitude),
    INDEX idx_address_hash (address_hash),
    INDEX idx_phone_hash (phone_hash)
);

CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    house_id INTEGER NOT NULL REFERENCES houses(id) ON DELETE CASCADE,
    room_id VARCHAR(2) NOT NULL DEFAULT '00',  -- RR portion (00-ZZ Base36)
    full_geo_id VARCHAR(12) GENERATED ALWAYS AS (
        (SELECT full_geo_id FROM houses WHERE id = house_id) || room_id
    ) STORED,
    
    current_status VARCHAR(20) DEFAULT 'available',  -- available, rented, pending_review, rejected
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(house_id, room_id),
    INDEX idx_full_geo_id (full_geo_id),
    INDEX idx_status (current_status)
);

-- ===== DYNAMIC LAYER (SCD Type 2 - Time Machine) =====

CREATE TABLE room_history (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    
    -- Listing data (snapshot at this point in time)
    title TEXT,
    description TEXT,
    price_monthly_vnd INTEGER,
    area_m2 NUMERIC,
    contact_phone TEXT,
    image_urls TEXT[],
    source_url TEXT,
    
    -- Attributes as JSON (denormalized for performance)
    attributes JSONB,
    
    -- SCD Type 2 fields
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,  -- NULL = current version
    is_current BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_room_current (room_id, is_current),
    INDEX idx_valid_period (valid_from, valid_to),
    INDEX idx_source_url (source_url)
);

-- ===== ALIAS & ROUTING LAYER =====

CREATE TABLE geo_aliases (
    id SERIAL PRIMARY KEY,
    alias VARCHAR(50) NOT NULL UNIQUE,  -- e.g., 'svbk', 'nhatrogiarecaugiay'
    
    -- Routing logic (can point to filter query OR specific room)
    route_type VARCHAR(20) NOT NULL,  -- 'filter', 'room', 'house'
    target_geo_id VARCHAR(12),  -- For room/house type
    filter_config JSONB,  -- For filter type: {district: 'CG', radius_km: 2, max_price: 4000000}
    
    redirect_type VARCHAR(10) DEFAULT '301',  -- 301 permanent, 302 temporary
    click_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    
    INDEX idx_alias (alias),
    INDEX idx_route_type (route_type)
);

-- ===== MIGRATION MAPPING TABLE (Temporary) =====

CREATE TABLE uuid_to_geoid_mapping (
    old_uuid UUID PRIMARY KEY,
    new_room_id INTEGER REFERENCES rooms(id),
    new_geo_id VARCHAR(12),
    migrated_at TIMESTAMP DEFAULT NOW()
);
```

### **C. ID Generation Algorithm**

```python
import hashlib
import string
from typing import Tuple, Optional

BASE36 = string.digits + string.ascii_uppercase  # 0-9, A-Z

def to_base36(num: int, width: int) -> str:
    """Convert integer to Base36 string with padding."""
    if num == 0:
        return '0' * width
    
    result = ''
    while num:
        result = BASE36[num % 36] + result
        num //= 36
    
    return result.zfill(width)

def from_base36(s: str) -> int:
    """Convert Base36 string to integer."""
    return int(s, 36)

def generate_house_fingerprint(
    city: str,
    ward: str,
    street: str,
    house_number: str = None,
    phone: str = None
) -> Tuple[str, str]:
    """Generate fingerprints for deduplication.
    
    Returns: (address_hash, phone_hash)
    """
    # Priority 1: Full address hash
    if all([city, ward, street, house_number]):
        addr_str = f"{city}|{ward}|{street}|{house_number}".lower().strip()
        address_hash = hashlib.sha256(addr_str.encode()).hexdigest()
    else:
        address_hash = None
    
    # Priority 2: Phone + Street hash (for anonymous posts)
    if phone and street:
        phone_str = f"{phone}|{street}".lower().strip()
        phone_hash = hashlib.sha256(phone_str.encode()).hexdigest()
    else:
        phone_hash = None
    
    return address_hash, phone_hash

def find_or_create_house(
    conn,
    district_code: str,
    latitude: float,
    longitude: float,
    address_street: str,
    address_ward: str,
    address_district: str,
    contact_phone: str = None
) -> int:
    """Find existing house or create new one.
    
    Returns: house_id (integer)
    """
    # Generate fingerprints
    addr_hash, phone_hash = generate_house_fingerprint(
        city="Hà Nội",
        ward=address_ward,
        street=address_street,
        house_number=None,  # Extract from street if available
        phone=contact_phone
    )
    
    # Check for existing house
    if addr_hash:
        existing = conn.execute(
            text("SELECT id FROM houses WHERE address_hash = :hash"),
            {"hash": addr_hash}
        ).fetchone()
        if existing:
            return existing[0]
    
    if phone_hash:
        existing = conn.execute(
            text("SELECT id FROM houses WHERE phone_hash = :hash"),
            {"hash": phone_hash}
        ).fetchone()
        if existing:
            return existing[0]
    
    # Create new house with next available HHH
    next_num = conn.execute(
        text("SELECT COUNT(*) FROM houses WHERE district_code = :district"),
        {"district": district_code}
    ).scalar()
    
    geo_id = to_base36(next_num, 3)
    
    result = conn.execute(
        text("""
            INSERT INTO houses 
            (geo_id, district_code, latitude, longitude, 
             address_street, address_ward, address_district,
             address_hash, phone_hash)
            VALUES (:geo_id, :district, :lat, :lng, :street, :ward, :district_name, :addr_hash, :phone_hash)
            RETURNING id
        """),
        {
            "geo_id": geo_id,
            "district": district_code,
            "lat": latitude,
            "lng": longitude,
            "street": address_street,
            "ward": address_ward,
            "district_name": address_district,
            "addr_hash": addr_hash,
            "phone_hash": phone_hash
        }
    )
    
    return result.scalar()

def create_room(conn, house_id: int, room_number: str = None) -> int:
    """Create new room under a house.
    
    Args:
        house_id: Parent house ID
        room_number: Optional room number (e.g., "301", "A12")
    
    Returns: room_id (integer)
    """
    # Count existing rooms for this house
    room_count = conn.execute(
        text("SELECT COUNT(*) FROM rooms WHERE house_id = :house_id"),
        {"house_id": house_id}
    ).scalar()
    
    if room_number:
        # Try to parse room number into Base36
        # Simple logic: use last 2 chars or convert number
        room_id = to_base36(int(room_number) if room_number.isdigit() else room_count + 1, 2)
    else:
        # Default: 00 for whole house, or next number
        room_id = "00" if room_count == 0 else to_base36(room_count, 2)
    
    result = conn.execute(
        text("""
            INSERT INTO rooms (house_id, room_id)
            VALUES (:house_id, :room_id)
            RETURNING id
        """),
        {"house_id": house_id, "room_id": room_id}
    )
    
    return result.scalar()
```

### **D. Migration Strategy**

**Phase 1: Schema Creation (No Downtime)**
1. Create new tables alongside existing `listings` table
2. No code changes yet

**Phase 2: Data Migration**
1. Script to migrate all existing listings:
   - Extract district from `address_district`
   - Map to district code (Cầu Giấy → CG)
   - Create house entries with fingerprinting
   - Create room entries (all with room_id=00 for now)
   - Create room_history entries from current listing data
   - Store UUID → GeoID mapping

**Phase 3: Dual Write (Transition Period)**
1. Update backend to write to BOTH old and new schema
2. Read from new schema, fallback to old
3. Test thoroughly

**Phase 4: Cut Over**
1. Update all URLs to use GeoID
2. Remove old schema writes
3. Drop `listings` table after grace period

## 🤖 AI Agent Instructions

**Context Files to Read:**
- [[database_schema_and_model]] - Current schema to understand migration
- [[core_architecture]] - SQLAlchemy patterns
- [[system_design_current_vs_target]] - Full vision context

**Technical Requirements:**
- PostgreSQL 13+ (Cloud SQL)
- SQLAlchemy Core for all DB operations
- Python 3.13+ for migration scripts
- Transaction safety - ROLLBACK on any error

**Integration Points:**
- Backend API endpoints need GeoID lookup
- Frontend URLs need redirect from UUID → GeoID
- QC Dashboard needs GeoID display
- Scraper ingestion needs fingerprinting logic

## ✅ Acceptance Criteria (AI Verification)

- [ ] **Schema:** All new tables created in Cloud SQL
- [ ] **Algorithm:** ID generation functions tested with 1000+ samples, no collisions
- [ ] **Fingerprinting:** Deduplication working for same address different posts
- [ ] **Migration:** All existing listings migrated with preserved data
- [ ] **URLs:** New endpoints working with GeoID format (e.g., `/29CG.AB1`)
- [ ] **Backwards Compat:** Old UUID URLs redirect 301 to GeoID
- [ ] **Performance:** GeoID lookup < 50ms
- [ ] **Data Integrity:** Zero data loss, all relationships preserved

## 🧭 Implementation Steps

### Step 1: Schema Design & Review (2hr)
- [ ] Write complete SQL DDL for new tables
- [ ] Review indexes for query performance
- [ ] Validate constraints and foreign keys
- [ ] Get human approval before execution

### Step 2: ID Algorithm Implementation (3hr)
- [ ] Implement Base36 conversion utilities
- [ ] Build fingerprinting system
- [ ] Write house creation logic with deduplication
- [ ] Write room creation logic
- [ ] Unit tests for all functions

### Step 3: Migration Script (4hr)
- [ ] Script to read all existing listings
- [ ] District code mapping (Cầu Giấy → CG, etc.)
- [ ] Batch migration with transaction safety
- [ ] Validation script to compare before/after
- [ ] Dry run on staging database

### Step 4: Backend Integration (4hr)
- [ ] Update `ingest_scraped_data` to use new schema
- [ ] Update `get_listings` to read from `room_history`
- [ ] Update `get_listing_by_id` to support GeoID
- [ ] Add redirect endpoint for old UUID URLs
- [ ] Update QC endpoints

### Step 5: Frontend Updates (2hr)
- [ ] Update routing to handle GeoID format
- [ ] Add GeoID display on cards
- [ ] Add copy GeoID button
- [ ] Update detail page URLs

### Step 6: Testing & Deployment (1hr)
- [ ] Integration tests with new schema
- [ ] Load testing GeoID lookups
- [ ] Deploy to staging
- [ ] Manual QA
- [ ] Production deployment

## 📋 Progress Tracking

**Status:** In Progress  
**Current Step:** Step 1 - Schema Design  
**Next Action:** Create SQL DDL and review

## 🔗 District Code Mapping (Reference)

```python
DISTRICT_CODES = {
    "Cầu Giấy": "CG",
    "Đống Đa": "DD",
    "Ba Đình": "BD",
    "Hoàn Kiếm": "HK",
    "Hai Bà Trưng": "HB",
    "Thanh Xuân": "TX",
    "Tây Hồ": "TH",
    "Long Biên": "LB",
    "Hoàng Mai": "HM",
    "Hà Đông": "HD",
    "Nam Từ Liêm": "NL",
    "Bắc Từ Liêm": "BL",
}
```

## 🚨 Risk Management

**Critical Risks:**
1. **Data Loss During Migration** → Mitigation: Extensive testing, backup before migration
2. **Performance Degradation** → Mitigation: Proper indexing, query optimization
3. **Breaking Existing Integrations** → Mitigation: Backwards compatibility layer
4. **GeoID Collisions** → Mitigation: Robust fingerprinting algorithm

## 📝 AI Session Log

### **Session 1** (2025-12-01 - Implementation Complete)
**AI Agent:** CTO Alex  
**Progress:** 
- ✅ Task created with full specification
- ✅ SQL schema designed (schema_v2_geoid.sql)
- ✅ Python utilities implemented (geoid_utils.py)
- ✅ Migration script created (migration_uuid_to_geoid.py)
- ✅ Deployment guide written (GEOID_DEPLOYMENT.md)
- ✅ Database schema documentation updated

**Key Design Decisions:**
1. **SCD Type 2 for Time Machine:** Use valid_from/valid_to instead of hard updates
2. **JSONB for Attributes:** Denormalize in room_history for query performance
3. **Dual Fingerprinting:** address_hash (priority 1) + phone_hash (priority 2)
4. **Elastic Display:** Remove leading zeros for UX (29CG.0AB01 → 29CGAB1)
5. **Base36 Encoding:** Maximum density with alphanumeric (0-9, A-Z)

**Deliverables:**
1. `/packages/functions/sql/schema_v2_geoid.sql` - Complete DDL with triggers
2. `/packages/functions/geoid_utils.py` - ID generation & house/room management
3. `/packages/functions/migration_uuid_to_geoid.py` - Migration script with validation
4. `/packages/functions/GEOID_DEPLOYMENT.md` - Step-by-step deployment guide
5. `/nhaminhbach_knowledge/system/database_schema_and_model.md` - Updated docs

**Testing Status:** Ready for dry-run testing

**Next Actions:**
1. Review SQL schema for approval
2. Test migration on local/staging database
3. Execute production migration
4. Update backend API endpoints
5. Update frontend routing

**Blockers:** None - awaiting human approval to proceed with testing
