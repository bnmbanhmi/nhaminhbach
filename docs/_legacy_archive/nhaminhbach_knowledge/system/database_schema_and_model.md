# Database Schema and Model
#system

**This is the single source of truth for our data structure. All code must conform to this model.**

---

## 🆕 NEW SCHEMA V2 (GeoID System) - ACTIVE

### GeoID Format: `29CG.HHHRR`
- **29**: City Code (Hà Nội)
- **CG**: Ward Code (Cầu Giấy, Nghĩa Đô, etc. - 123 wards in Hà Nội)
- **HHH**: House ID (3-char Base36: 000-ZZZ)
- **RR**: Room ID (2-char Base36: 00-ZZ, 00 = whole house)

**Example:** `29CG.AB1` (Display: `29CGAB1`)

---

### Table: `houses` (Static Layer - Physical Buildings)
**Purpose:** Permanent physical properties with stable geo-identity

- `id` (SERIAL, Primary Key)
- `geo_id` (VARCHAR(5), UNIQUE) - House portion (HHH)
- `city_code` (VARCHAR(2), DEFAULT '29') - Hà Nội
- `ward_code` (VARCHAR(2)) - CG, ND, DD, etc. (123 wards)
- `full_geo_id` (VARCHAR(10), GENERATED, INDEXED) - Computed: `29CG.0AB`
- `latitude`, `longitude` (NUMERIC) - Geographic coordinates
- `address_street`, `address_ward`, `address_district` (TEXT)
- `accuracy_level` (INTEGER) - 1=Verified (pin), 2=Fuzzy (circle)
- `address_hash` (VARCHAR(64)) - SHA256 for deduplication
- `phone_hash` (VARCHAR(64)) - SHA256 for anonymous posts
- `created_at`, `updated_at` (TIMESTAMP)

**Indexes:** full_geo_id, ward_code, coords, address_hash, phone_hash

---

### Table: `rooms` (Individual Rental Units)
**Purpose:** Specific rooms/units within a house

- `id` (SERIAL, Primary Key)
- `house_id` (INTEGER, FK to houses.id)
- `room_id` (VARCHAR(2)) - RR portion (00-ZZ)
- `full_geo_id` (VARCHAR(12), INDEXED) - Maintained by trigger `calc_room_full_geoid`: `houses.full_geo_id || room_id`
- `current_status` (VARCHAR(20)) - available, rented, pending_review, rejected
- `created_at`, `updated_at` (TIMESTAMP)

**Unique Constraint:** (house_id, room_id)  
**Indexes:** full_geo_id, house_id, status

---

### Table: `room_history` (Time Machine - SCD Type 2)
**Purpose:** Track all changes in price, attributes, status over time

- `id` (SERIAL, Primary Key)
- `room_id` (INTEGER, FK to rooms.id)
- `title`, `description` (TEXT) - Listing data snapshot
- `price_monthly_vnd` (INTEGER)
- `area_m2` (NUMERIC)
- `contact_phone` (TEXT)
- `image_urls` (TEXT[])
- `source_url` (TEXT)
- `attributes` (JSONB) - Denormalized amenities: `{air_conditioner: true, ...}`
- `valid_from`, `valid_to` (TIMESTAMP) - SCD Type 2 fields
- `is_current` (BOOLEAN) - TRUE only for active version
- `status` (VARCHAR(20))
- `created_at` (TIMESTAMP)

**Indexes:** (room_id, is_current), valid_period, source_url, attributes (GIN)  
**Constraint:** Only one is_current=TRUE per room_id

---

### Table: `geo_aliases` (Campaign URLs & Smart Routing)
**Purpose:** Short memorable URLs for marketing campaigns

- `id` (SERIAL, Primary Key)
- `alias` (VARCHAR(50), UNIQUE) - e.g., "svbk", "nhatrogiarecaugiay"
- `route_type` (VARCHAR(20)) - 'filter', 'room', 'house'
- `target_geo_id` (VARCHAR(12)) - For room/house types
- `filter_config` (JSONB) - For filter type: `{ward: 'CG', max_price: 4000000}`
- `redirect_type` (VARCHAR(10)) - '301' or '302'
- `click_count` (INTEGER) - Analytics
- `created_at`, `expires_at` (TIMESTAMP)
- `is_active` (BOOLEAN)

**Examples:**
- `/svbk` → Filter students near Bách Khoa
- `/29CG.AB1` → Direct room link

---

### Table: `uuid_to_geoid_mapping` (Migration Support)
**Purpose:** Backwards compatibility during transition from UUID to GeoID

- `old_uuid` (UUID, Primary Key)
- `old_source_url` (TEXT)
- `new_room_id` (INTEGER, FK to rooms.id)
- `new_geo_id` (VARCHAR(12))
- `new_house_id` (INTEGER, FK to houses.id)
- `migrated_at` (TIMESTAMP)
- `migration_batch` (INTEGER)

**Purpose:** Enable 301 redirects from old `/listings/{uuid}` to new `/{geoid}`

---

## 🔧 Key Principles

1. **GeoID as Primary Identifier:** All public URLs use GeoID format (`29CG.AB1`)
2. **Time Machine:** Never delete room_history - close old versions with `valid_to`
3. **Deduplication:** Use fingerprints (address_hash, phone_hash) before creating houses
4. **Transaction Safety (CRITICAL):** All listing creation (house + room + history) MUST execute in a single atomic transaction to prevent partial state (zombie houses/rooms)
5. **JSONB for Attributes:** Denormalized in room_history for performance
6. **Database:** Supabase PostgreSQL - no GCP dependencies

---

## 📌 GeoID Quick Reference

### Format
```
29CG.HHHRR
│ │  │  └─ RR: Room ID (2 chars Base36, 00-ZZ)
│ │  └──── HHH: House ID (3 chars Base36, 000-ZZZ)
│ └─────── CG: Ward Code (2 chars)
└───────── 29: City Code (Hà Nội)
```

Examples:
- Internal: `29CG.0AB01`
- Display: `29CGAB1` (elastic padding)
- Whole house: `29CG.W8K00` → display `29CGW8K`

### Ward Codes (Hà Nội)
- Cầu Giấy: `CG`, Nghĩa Đô: `ND`, Dân Hòa: `DH`, Mỹ Đức: `MD`, Đống Đa: `DD`, Ba Đình: `BD`, Hoàn Kiếm: `HK`, etc.
- **Full list:** 123 wards mapped in `geoid_utils.py::WARD_CODES`

### URL Routing
- `/{geoid}` → Direct room (e.g., `/29CGAB1`)
- `/{alias}` → Campaign (e.g., `/svbk`)
- `/listings/{uuid}` → Legacy; 301 redirect to GeoID

---

## 📚 Query Examples

### Get current listing by GeoID
```sql
SELECT h.full_geo_id, r.room_id, rh.*
FROM houses h
JOIN rooms r ON r.house_id = h.id
JOIN room_history rh ON rh.room_id = r.id
WHERE h.full_geo_id = '29CG.0AB'
  AND r.room_id = '01'
  AND rh.is_current = TRUE;
```

### Get price history for a room
```sql
SELECT valid_from, valid_to, price_monthly_vnd, status
FROM room_history
WHERE room_id = 123
ORDER BY valid_from DESC;
```

### Search with filters
```sql
SELECT h.full_geo_id, r.room_id, rh.price_monthly_vnd
FROM houses h
JOIN rooms r ON r.house_id = h.id
JOIN room_history rh ON rh.room_id = r.id
WHERE h.ward_code = 'CG'
  AND rh.is_current = TRUE
  AND rh.price_monthly_vnd BETWEEN 2000000 AND 5000000;
```

---

## 🗂️ DEPRECATED SCHEMA V1 (Will be removed after migration)

### Table: `listings` (DEPRECATED)
- `id` (UUID) → Replaced by GeoID
- `status`, `source_url`, `title`, `description`
- `price_monthly_vnd`, `area_m2`
- `address_*`, `latitude`, `longitude`
- `contact_phone`, `image_urls`

### Table: `attributes` (KEPT - Metadata only)
- `id`, `type`, `name`, `slug`, `possible_values`
- **Note:** Still used for UI filters, but values moved to JSONB in room_history

### Table: `listing_attributes` (DEPRECATED)
- `listing_id`, `attribute_id`, `value_*`
- Replaced by JSONB in room_history

---

**Migration Status:** ✅ Schema ready, migration script ready  
**Database:** Supabase PostgreSQL  
**Next Step:** Execute migration (see `nhaminhbach_knowledge/process/geoid_migration_and_deployment.md`)  
**API:** Use `geoid_api.create_listing_atomic()` for transaction-safe listing creation