---
tags: #sprint-ai
status: #in-progress
timeframe: 2025-12-02 to 2025-12-15
epic: [[E2]]
owner: Minh
estimated_duration: 40 hours
---

# Sprint S9: GeoID Instant Access Sprint

**Duration:** 2025-12-02 to 2025-12-15 (2 weeks)  
**Epic:** [[E2]] Public MVP - The Cleanest Source of Truth  
**Sprint Type:** Core Feature / UX Revolution

---

## 🎯 Sprint Objective

**Mission:** Transform NhaMinhBach from UUID-based to GeoID-based platform with **Instant Gratification UX**.

**The "Google Moment":** User types `AB1` → instantly sees the listing. No friction. No confusion.

**User Value:** 
- Access any listing via short URL: `nhaminhbach.com/AB1`
- Search bar = navigation: type GeoID → direct to listing
- Every listing has a memorable, copyable ID

**Technical Value:**
- GeoID format: `29CG.HHHRR` (e.g., `29CG.0AB01`)
- Display format: `AB1` (elastic, human-friendly)
- URL format: `/AB1` or `/29CGAB1` (both work)

---

## 📋 Sprint Backlog

### **Part 1: Database Infrastructure** ✅ COMPLETE

| # | Task | Status | Completed |
|---|------|--------|-----------|
| 1 | Database Redesign GeoID System | ✅ DONE | 2025-12-01 |
| 2 | Ward Migration (123 wards) | ✅ DONE | 2025-12-02 |

**Deliverables:**
- ✅ GeoID format: `29{WARD}.HHHRR` (123 wards mapped)
- ✅ Base36 encoding utilities
- ✅ Address/phone fingerprinting for deduplication
- ✅ SCD Type 2 room_history table
- ✅ Transaction-safe API (`create_listing_atomic`)
- ✅ SQL schema DDL (`schema_v2_geoid.sql`)
- ✅ All tests passing

---

### **Part 2: Instant Access Layer** ✅ COMPLETE

| # | Task | Est. | Status | Notes |
|---|------|------|--------|-------|
| 3 | GeoID Short URL Routing | 1hr | ✅ DONE | `/AB1` → listing detail |
| 4 | GeoID Search Bar | 2hr | ✅ DONE | Central search, instant navigation |
| 5 | Display GeoID on Cards & Detail | 1hr | ✅ DONE | Big, copyable ID badge |
| 6 | Temporary UUID-to-GeoID Bridge | 1hr | ✅ DONE | Generate displayID from UUID hash |

**Deliverables:**
- ✅ URL `/AB1` shows listing with matching display ID
- ✅ Search bar: type `AB1` → navigate to listing
- ✅ GeoID visible on all listing cards (big, prominent)
- ✅ Copy button for GeoID sharing
- ✅ Central search bar with Google-style UX

---

### **Part 3: Legacy Cleanup & Schema Deployment** (After Part 2)

| # | Task | Est. | Status | Notes |
|---|------|------|--------|-------|
| 7 | Create Cleanup SQL Script | 0.5hr | ✅ DONE | `000_cleanup_all.sql` with safety checks |
| 8 | Create Schema V2.2 (GeoID + JSONB) | 1hr | ✅ DONE | `schema_v2_geoid_eav.sql` - JSONB attributes |
| 9 | Run Cleanup on Empty Supabase | 0.5hr | 📅 PLANNED | Execute `000_cleanup_all.sql` |
| 10 | Deploy V2.2 Schema to Supabase | 1hr | 📅 PLANNED | Execute `schema_v2_geoid_eav.sql` |
| 11 | Verify Schema & Seed Data | 0.5hr | 📅 PLANNED | Check tables, triggers, 26 attributes |

**Key Files Created:**
- `sql/000_cleanup_all.sql` - Safe database reset (aborts if data exists)
- `sql/schema_v2_geoid_eav.sql` - Full V2.2 schema with JSONB attributes

**Schema V2.2 Architecture (Optimized):**
- `houses` → Static physical properties (GeoID: 29CG.HHH) + **GiST geo index for radius search**
- `rooms` → Individual units (GeoID: 29CG.HHHRR)  
- `room_history` → SCD Type 2 history + **JSONB `attributes` column** + GIN index
- `attributes` → Dictionary/metadata only (names, types, icons, validation) - **NOT a junction table**
- `geo_aliases` → Smart URL routing (campaigns)
- `uuid_to_geoid_mapping` → Migration backwards compatibility
- `v_current_listings` → Convenience view with JSONB attributes included

**Key Design Decisions (V2.2):**
1. **JSONB over EAV:** Removed `room_attributes` junction table → attributes stored directly in `room_history.attributes` JSONB
2. **GiST Geography Index:** `idx_houses_geo_point` for efficient radius search ("Tìm phòng quanh đây")
3. **GIN Index on JSONB:** Fast `@>`, `?`, `?&` queries on attributes
4. **UNIQUE slug constraint:** Enforced on `attributes.slug` to prevent duplicates
5. **Icon field added:** `attributes.icon` for UI rendering

---

### **Part 4: Legacy Supabase Schema Archived**

| # | Task | Est. | Status | Notes |
|---|------|------|--------|-------|
| 12 | Archive Legacy `supabase_schema.sql` | - | ✅ DONE | Kept as reference, superseded by V2.1 |
| 13 | Archive Legacy `attributes.sql` | - | ✅ DONE | Attributes now seeded in V2.1 schema |

**Legacy Files (Kept for Reference):**
- `sql/supabase_schema.sql` - Original UUID-based 3-table schema
- `sql/attributes.sql` - Original attribute seed data

---

### **Part 5: API Integration** (After Part 3)

| # | Task | Est. | Status | Notes |
|---|------|------|--------|-------|
| 14 | Update Backend for GeoID Lookup | 4hr | 📅 PLANNED | `/api/listings/{geoid}` |
| 15 | Add Ward-based Filtering | 2hr | 📅 PLANNED | Filter by ward code |
| 16 | 301 Redirects for Old UUIDs | 1hr | 📅 PLANNED | Backwards compatibility |
| 17 | Update API to Use `v_current_listings` View | 2hr | 📅 PLANNED | Replace legacy listing queries |
| 18 | Add Attribute CRUD Endpoints | 2hr | 📅 PLANNED | For QC Cockpit attribute editing |

---

## 📊 Progress Dashboard

| Phase | Tasks | Done | Progress |
|-------|-------|------|----------|
| 1. Database Infrastructure | 2 | 2 | ✅ 100% |
| 2. Instant Access Layer | 4 | 4 | ✅ 100% |
| 3. Legacy Cleanup & Schema Deployment | 5 | 2 | 🔄 40% |
| 4. Legacy Schema Archived | 2 | 2 | ✅ 100% |
| 5. API Integration | 5 | 0 | 📅 0% |
| **TOTAL** | **18** | **10** | **56%** |

---

## 🔥 Critical Path (TODAY)

### Priority 1: Make GeoID URLs Work NOW

**Problem:** Users should access listings via `/AB1` not `/listings/uuid`

**Solution (Temporary):**
1. Add frontend route that catches short IDs
2. Generate display GeoID from UUID hash (temporary until DB migration)
3. Store mapping in localStorage for consistency

**Implementation:**
```
URL: /AB1 or /CG.AB1 or /29CGAB1
↓
Parse → detect if GeoID pattern
↓
If GeoID → lookup listing by display_id
If UUID → lookup listing by UUID (legacy)
↓
Show listing detail
```

### Priority 2: Central Search Bar

**From new_core.md:**
> **Search Bar:** Đặt chính giữa, to rõ ràng như Google. Nhập đúng ID phòng là đến thẳng phòng đó.

**Implementation:**
- Big search bar at top of homepage
- Placeholder: "Nhập mã phòng (VD: AB1) hoặc tìm kiếm..."
- On Enter: if matches GeoID pattern → navigate directly
- Auto-suggest from known listings

### Priority 3: GeoID Display on Cards

**From new_core.md:**
> **Feed Experience:** Card listing thiết kế dọc. Thông tin rõ ràng: giá, địa chỉ, **ID**

**Implementation:**
- Badge at top-right of card: `#AB1`
- Big, high-contrast, touchable
- On detail page: large ID with copy button

---

## 🛠 Technical Approach

### Temporary GeoID Generation (Until DB Migration)

Since we haven't migrated the database yet, we'll generate a **temporary display ID** from UUID:

```typescript
// Generate stable 3-5 char display ID from UUID
function generateDisplayId(uuid: string): string {
  // Take first 8 hex chars of UUID, convert to Base36
  const hex = uuid.replace(/-/g, '').slice(0, 8);
  const num = parseInt(hex, 16) % (36 * 36 * 36); // Max 3 chars
  return toBase36(num).toUpperCase();
}
// Example: "a1b2c3d4-..." → "K7M"
```

This gives us:
- Stable: same UUID always → same display ID
- Short: 2-3 characters
- Reversible: can lookup UUID from display ID

### URL Routing Strategy

```
/AB1           → Parse as GeoID → lookup listing
/CG.AB1        → Parse as GeoID with ward → lookup
/29CGAB1       → Parse as full GeoID → lookup  
/listings/:id  → Legacy UUID route → lookup
```

---

## 📚 Key Files

| Purpose | Path |
|---------|------|
| GeoID Utilities | `/packages/functions/geoid_utils.py` |
| GeoID API | `/packages/functions/geoid_api.py` |
| **SQL: Cleanup Script** | `/packages/functions/sql/000_cleanup_all.sql` |
| **SQL: Schema V2.2 (GeoID+JSONB)** | `/packages/functions/sql/schema_v2_geoid_eav.sql` |
| SQL: Schema V2.0 (Legacy) | `/packages/functions/sql/schema_v2_geoid.sql` |
| SQL: Legacy Schema V1 | `/packages/functions/sql/supabase_schema.sql` |
| SQL: Legacy Attributes Seed | `/packages/functions/sql/attributes.sql` |
| Frontend App | `/packages/web/src/App.tsx` |
| Listing Card | `/packages/web/src/components/listings/ListingCard.tsx` |
| Homepage | `/packages/web/src/pages/HomePage.tsx` |

---

## 🎯 Definition of Done

### MVP (End of This Sprint)
- [x] GeoID system designed and tested
- [ ] Short URL access working (`/AB1` → listing)
- [ ] Search bar with ID navigation
- [ ] GeoID displayed on all cards
- [ ] Copy ID button functional

### Full Completion
- [ ] Database schema deployed to Supabase
- [ ] All listings migrated to GeoID
- [ ] API returning GeoID-formatted data
- [ ] Ward-based filtering
- [ ] Old UUIDs redirecting to new URLs

---

## 📝 Session Log

### Session 1: 2025-12-01 (Database Redesign)
**Agent:** CTO Alex  
**Duration:** 16 hours  
**Completed:** Full GeoID schema design, Base36 utilities, fingerprinting, SCD Type 2

### Session 2: 2025-12-02 (Ward Migration)
**Agent:** CTO Alex  
**Duration:** 45 minutes  
**Completed:** District → Ward migration (12 → 123 codes)

### Session 3: 2025-12-02 (Instant Access Layer)
**Agent:** CTO Alex  
**Status:** ✅ COMPLETE  
**Duration:** ~2 hours  
**Focus:** Short URL routing, Search bar, GeoID display

**Files Created:**
- `/packages/web/src/utils/geoid.ts` - GeoID utilities (Base36, display formatting)
- `/packages/web/src/components/ui/SearchBar.tsx` - Central search component
- `/packages/web/src/pages/GeoIdLookupPage.tsx` - Short URL routing handler

**Files Modified:**
- `/packages/web/src/App.tsx` - Added GeoID route
- `/packages/web/src/pages/HomePage.tsx` - Added central search bar
- `/packages/web/src/pages/ListingDetailPage.tsx` - Added GeoID header with copy
- `/packages/web/src/components/listings/ListingCard.tsx` - Added GeoID badge

**Key Features Implemented:**
1. Short URL: `/AB1` redirects to listing
2. Search bar with GeoID detection and hints
3. Copy ID button on cards and detail page
4. Temporary UUID→DisplayID generation (hash-based)

**Next Session:** Deploy GeoID schema to Supabase, run migration

### Session 4: 2025-12-02 (Legacy Cleanup & Schema V2.1)
**Agent:** CTO Alex  
**Status:** ✅ COMPLETE  
**Duration:** ~30 minutes  
**Focus:** Create cleanup script, integrate EAV attributes into GeoID schema

**Files Created:**
- `/packages/functions/sql/000_cleanup_all.sql` - Safe database reset script
  - Safety check: aborts if any table has data
  - Drops all V1 and V2 tables, triggers, functions, types
  - Provides clear confirmation message
  
- `/packages/functions/sql/schema_v2_geoid_eav.sql` - Complete V2.1 schema
  - GeoID architecture (houses → rooms → room_history)
  - EAV pattern preserved (attributes + room_attributes tables)
  - 26 default attributes seeded (amenities, policies, specs)
  - Convenience view `v_current_listings` for backward compatibility
  - All triggers and functions for auto-updates

**Legacy Files Archived (Kept for Reference):**
- `sql/supabase_schema.sql` - Original UUID-based schema
- `sql/attributes.sql` - Original attribute seed data
- `sql/schema_v2_geoid.sql` - Previous V2.0 without EAV

**Key Design Decisions:**
1. **EAV over JSONB:** Preserved flexible attributes table instead of JSONB column
2. **room_attributes links to room_history:** Attributes snapshot at each history point
3. **Added more attributes:** Extended from 16 to 26 (balcony, wifi, parking, etc.)
4. **v_current_listings view:** Drop-in replacement for legacy listing queries

**Next Session:** Execute cleanup + schema on Supabase, verify deployment

### Session 5: 2025-12-02 (Schema V2.2 - JSONB Optimization)
**Agent:** CTO Alex  
**Status:** ✅ COMPLETE  
**Duration:** ~15 minutes  
**Focus:** Upgrade to JSONB attributes, add GiST geo index, enforce UNIQUE slug

**Changes Made:**

1. **JSONB Attributes (Removed EAV Junction):**
   - ❌ Deleted `room_attributes` table (no more JOINs!)
   - ✅ Added `attributes JSONB` column to `room_history`
   - ✅ Added GIN index `idx_room_history_attributes` for fast `@>`, `?` queries
   - Example: `{"air_conditioner": true, "furniture": "full", "floor_number": 3}`

2. **GiST Geography Index for Radius Search:**
   - ✅ Added PostGIS extension
   - ✅ Created `idx_houses_geo_point` using `ST_MakePoint(longitude, latitude)::geography`
   - Enables: `ST_DWithin(..., 2000)` for 2km radius search

3. **Attributes Dictionary Enhanced:**
   - ✅ Added `CONSTRAINT uq_attributes_slug UNIQUE (slug)`
   - ✅ Added `icon TEXT` column for UI rendering
   - ✅ Added `idx_attributes_display_order` index
   - Table now serves as metadata dictionary, not junction table

4. **Sample Queries Added:**
   - JSONB filter: `WHERE attributes @> '{"air_conditioner": true}'`
   - Radius search: `ST_DWithin(..., 2000)` with distance calculation

**Query Performance Improvement:**
```sql
-- OLD (V2.1 EAV): 3 JOINs needed
SELECT v.*, a.name FROM v_current_listings v
JOIN room_attributes ra ON ra.room_history_id = v.room_history_id
JOIN attributes a ON a.id = ra.attribute_id
WHERE a.slug = 'air_conditioner' AND ra.value_boolean = TRUE;

-- NEW (V2.2 JSONB): No JOINs!
SELECT * FROM v_current_listings
WHERE (attributes->>'air_conditioner')::boolean = true;
```

**Next Session:** Deploy to Supabase

### Session 6: 2025-12-02 (GeoID Instant Access — Backend + Frontend Integration)
**Agent:** CTO Alex + AI Agent
**Duration:** 1.5 hours
**Completed:** Implemented server-side GeoID lookup, wired frontend short-route handler, added local mock server and unit tests

**Details:**
- **Backend:** Added `get_listing_by_geoid` endpoint and `lookup_listing_by_geoid(conn, input_raw)` helper in `packages/functions/main.py`. Endpoint supports queries like `?geoid=AB1`, `?geoid=29CG.AB1`, `?geoid=29CGAB1` and queries `v_current_listings` for exact and loose matches.
- **Frontend:** Updated `packages/web/src/pages/GeoIdLookupPage.tsx` to call the backend endpoint first and fall back to the existing fetch-all approach when the endpoint returns 404.
- **Testing:** Added `packages/functions/test_get_listing_by_geoid.py` (mock DB connection) and ran tests locally — all passed.
- **Local Dev:** Added `packages/functions/mock_server.py` to simulate API endpoints for local frontend dev. Verified `GET /get_listing_by_geoid?geoid=29CG.0AB01` returns sample listing JSON.

**Files Modified / Added:**
- `packages/functions/main.py` — added endpoint + helper
- `packages/web/src/pages/GeoIdLookupPage.tsx` — call backend endpoint first
- `packages/functions/test_get_listing_by_geoid.py` — unit test (mocked)
- `packages/functions/mock_server.py` — lightweight local API mock for dev

**Impact / Next Steps:**
- Short URL lookup is now supported server-side; frontend uses it for instant navigation. Switch production routing to this endpoint once Supabase view `v_current_listings` is available in the production DB.
- Deploy endpoint to serverless environment and update production `API_BASE_URL`/proxy accordingly.

### Session 7: 2025-12-02 (CI/CD Decision)
**Agent:** CTO Alex + AI Agent
**Duration:** 30 minutes
**Decision:** Use Vercel Git Integration for automatic deployments; keep GitHub Actions as a tests-only CI.

**Rationale:**
- Vercel already supports Git integration and will create preview deployments for PRs and production deployments for commits to `main`.
- Using Vercel's native deploy pipeline avoids duplicate deployments and keeps the process simple and reliable.
- GitHub Actions will run tests (backend + frontend) on `pull_request` and `push` to provide CI feedback and protect `main` via branch protection rules.

**Actions Taken:**
- Replaced the previous CI deploy workflow with a `tests-only` workflow at `.github/workflows/deploy-vercel.yml` that runs on PRs and pushes.
- Removed CI-initiated `npx vercel` deploy step to avoid duplication with Vercel Git integration.
- Added local mock server + unit tests for GeoID endpoint (dev/test support).

**Follow-up / Recommendations:**
- Enable GitHub branch protection for `main` and require the `tests-only` workflow to pass before merging.
- Ensure the Vercel project is linked to this repository in the Vercel dashboard (Git integration enabled).
- If you want CI to perform deploys instead of Vercel's integration, we can reintroduce a gated `npx vercel` step that uses `VERCEL_TOKEN` (stored as GitHub secret).


