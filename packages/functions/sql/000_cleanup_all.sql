-- =========================================================================
-- NHAMINHBACH DATABASE CLEANUP SCRIPT (Supabase Compatible)
-- =========================================================================
-- Purpose: Drop all existing tables and reset database to clean state
-- Author: CTO Alex + AI Agent
-- Date: 2025-12-02
-- 
-- ⚠️  WARNING: THIS SCRIPT WILL DELETE ALL DATA!
-- ⚠️  ONLY RUN ON EMPTY/NEW DATABASES OR WHEN YOU WANT TO RESET EVERYTHING
-- =========================================================================

-- =========================================================================
-- DROP VIEW FIRST (depends on tables)
-- =========================================================================

DROP VIEW IF EXISTS v_current_listings CASCADE;

-- =========================================================================
-- DROP TRIGGERS (Must drop before functions)
-- =========================================================================

DROP TRIGGER IF EXISTS trg_rooms_calc_geoid ON rooms;
DROP TRIGGER IF EXISTS trg_room_history_update_status ON room_history;
DROP TRIGGER IF EXISTS trg_room_history_close_previous ON room_history;
DROP TRIGGER IF EXISTS trg_houses_update_timestamp ON houses;
DROP TRIGGER IF EXISTS trg_rooms_update_timestamp ON rooms;

-- =========================================================================
-- DROP FUNCTIONS
-- =========================================================================

DROP FUNCTION IF EXISTS calc_room_full_geoid();
DROP FUNCTION IF EXISTS update_room_current_status();
DROP FUNCTION IF EXISTS close_previous_room_history();
DROP FUNCTION IF EXISTS update_houses_timestamp();
DROP FUNCTION IF EXISTS update_rooms_timestamp();
DROP FUNCTION IF EXISTS update_timestamp();

-- =========================================================================
-- DROP TABLES (Order matters due to foreign keys)
-- =========================================================================

-- V2 Tables (GeoID system)
DROP TABLE IF EXISTS uuid_to_geoid_mapping CASCADE;
DROP TABLE IF EXISTS geo_aliases CASCADE;
DROP TABLE IF EXISTS room_attributes CASCADE;
DROP TABLE IF EXISTS room_history CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS houses CASCADE;

-- V1 Tables (Legacy UUID system)
DROP TABLE IF EXISTS listing_attributes CASCADE;
DROP TABLE IF EXISTS listings CASCADE;

-- Shared Tables
DROP TABLE IF EXISTS attributes CASCADE;

-- Raw data staging table
DROP TABLE IF EXISTS raw_scraped_data CASCADE;

-- =========================================================================
-- DROP ENUM TYPES
-- =========================================================================

DROP TYPE IF EXISTS listing_status CASCADE;
DROP TYPE IF EXISTS attribute_type CASCADE;

-- =========================================================================
-- DONE - Database is now clean and ready for fresh schema
-- Next step: Run schema_v2_geoid_eav.sql
-- =========================================================================
