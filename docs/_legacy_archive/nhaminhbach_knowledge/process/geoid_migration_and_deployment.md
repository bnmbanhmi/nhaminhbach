# GeoID Migration & Deployment Guide
#process

This is the canonical playbook to migrate from UUID-based listings to the GeoID system (29CG.HHHRR) and deploy across backend and frontend.

---

## 🔑 Key Facts
- **Database:** Supabase PostgreSQL (no GCP dependencies)
- **Transaction Safety:** All listing creation (house + room + history) MUST use single transaction to avoid partial state
- `houses.full_geo_id` is a PostgreSQL GENERATED column (same-row concat)
- `rooms.full_geo_id` is maintained by trigger `calc_room_full_geoid` because generated columns cannot reference other tables
- House GeoID allocation uses retry-on-conflict to avoid race collisions; for high scale consider per-district sequences or advisory locks

---

## 🚀 Deployment Steps

### 1) Backup
```bash
pg_dump -U postgres -d nhaminhbach > backup_before_geoid_$(date +%Y%m%d).sql
ls -lh backup_before_geoid_*.sql
```

### 2) Apply Schema (Supabase)
```bash
cd /Users/mac/nhaminhbach.com/nhaminhbach/packages/functions

# Connect to Supabase PostgreSQL
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" -f sql/schema_v2_geoid.sql

# Verify tables
psql -U postgres -d nhaminhbach -c "\\dt"
# Verify trigger exists
psql -U postgres -d nhaminhbach -c "\\dS+ rooms" | grep -i calc_room_full_geoid || echo "Trigger not found!"
```

### 3) Local Utilities Test (Optional)
```bash
python3 test_geoid_utils.py
```

### 4) Dry-Run Migration
```bash
# Set Supabase credentials
export SUPABASE_DB_HOST="db.[PROJECT-REF].supabase.co"
export SUPABASE_DB_PASSWORD="[YOUR-PASSWORD]"
export SUPABASE_DB_NAME="postgres"
export SUPABASE_DB_USER="postgres"

python3 migration_uuid_to_geoid.py --dry-run --batch-size 50 --limit 100
```

### 5) Full Migration
```bash
python3 migration_uuid_to_geoid.py --batch-size 100
```

---

## ✅ Validation Queries
```sql
-- Counts
SELECT 'Old listings' as table_name, COUNT(*) FROM listings
UNION ALL
SELECT 'New rooms', COUNT(*) FROM rooms
UNION ALL
SELECT 'Houses', COUNT(*) FROM houses
UNION ALL
SELECT 'Room history', COUNT(*) FROM room_history WHERE is_current = TRUE
UNION ALL
SELECT 'UUID mappings', COUNT(*) FROM uuid_to_geoid_mapping;

-- Sample mappings
SELECT old_uuid, new_geo_id, h.full_geo_id AS house_geo_id, r.room_id
FROM uuid_to_geoid_mapping m
JOIN rooms r ON r.id = m.new_room_id
JOIN houses h ON h.id = r.house_id
LIMIT 10;

-- Duplicate protection (should be 0)
SELECT full_geo_id, COUNT(*)
FROM rooms
GROUP BY full_geo_id
HAVING COUNT(*) > 1;

-- Price preservation
SELECT l.id as old_uuid, l.price_monthly_vnd as old_price, rh.price_monthly_vnd as new_price, m.new_geo_id
FROM listings l
JOIN uuid_to_geoid_mapping m ON m.old_uuid = l.id
JOIN room_history rh ON rh.room_id = m.new_room_id AND rh.is_current = TRUE
LIMIT 10;
```

---

## 🧩 API & Frontend Updates (Summary)
- **Critical:** Use `geoid_api.create_listing_atomic()` for all new listings - ensures transaction safety
- Backend: add `/api/listing/{geoid}`, `/api/search`, and legacy redirect via mapping table
- Frontend: support direct `/{geoid}` route, legacy `/listings/{uuid}` → redirect to GeoID
- Example FastAPI endpoint in `packages/functions/geoid_api.py`

---

## 🧪 Testing Checklist
- [ ] Schema tables and indexes created
- [ ] GeoID utilities and display format correct
- [ ] Dry-run completes without errors
- [ ] Full migration completes; counts match
- [ ] API endpoints resolve GeoID and legacy URLs
- [ ] Frontend routes render GeoID links correctly
- [ ] Performance: GeoID lookup < 50ms under expected load

---

## 🆘 Rollback
```bash
# Restore
psql -U postgres -d nhaminhbach < backup_before_geoid_YYYYMMDD.sql
# Drop new tables if necessary
psql -U postgres -d nhaminhbach -c "
DROP TABLE IF EXISTS uuid_to_geoid_mapping CASCADE;
DROP TABLE IF EXISTS geo_aliases CASCADE;
DROP TABLE IF EXISTS room_history CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS houses CASCADE;
"
```

---

## 📎 References
- Schema SQL: `/packages/functions/sql/schema_v2_geoid.sql`
- GeoID Utilities: `/packages/functions/geoid_utils.py`
- Migration Script: `/packages/functions/migration_uuid_to_geoid.py`
- Data Model: `/nhaminhbach_knowledge/system/database_schema_and_model.md`
