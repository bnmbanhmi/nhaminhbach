# GeoID System Implementation Guide

## 📋 Overview

Hệ thống GeoID mới thay thế UUID-based system với semantic, hierarchical IDs theo format `29CG.HHHRR`:

- **29**: City Code (Hà Nội)
- **CG**: Ward Code (Cầu Giấy, Đống Đa, etc.)
- **HHH**: House ID (Base36, 3 chars)
- **RR**: Room ID (Base36, 2 chars, 00 = whole house)

**Example URLs:**
- Old: `/listings/123e4567-e89b-12d3-a456-426614174000`
- New: `/29CG.AB1` (compact display: 29CGAB1)

---

## 🗄️ Database Schema Changes

### New Tables

1. **houses** - Static layer (physical buildings)
   - Geo-location, address, fingerprints
   - Deduplication via address_hash & phone_hash

2. **rooms** - Individual units
   - Many-to-one with houses
   - Each room has unique GeoID

3. **room_history** - Time machine (SCD Type 2)
   - Tracks all changes: price, attributes, status
   - Enables price history charts

4. **geo_aliases** - Campaign URLs
# Moved

This guide has moved to the canonical knowledge base:

`/nhaminhbach_knowledge/process/geoid_migration_and_deployment.md`
   - 301 redirects from old UUIDs
