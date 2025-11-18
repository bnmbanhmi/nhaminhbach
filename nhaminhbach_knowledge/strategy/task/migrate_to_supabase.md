---
tags: #task-ai
status: #complete
owner: Gemini
ai_agent: Gemini
epic: [[E4]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 3hr
complexity: Complex
---

# AI Task: Migrate Database from Google Cloud SQL to Supabase

**Duration:** 3hr
**Complexity:** Complex
**AI Agent:** Gemini

## 🎯 Objective (AI Context)
**What:** Migrate the backend database from Google Cloud SQL (PostgreSQL) to Supabase (PostgreSQL).
**Why:** To simplify database management, leverage Supabase's features (auto-generated APIs, authentication), and consolidate the tech stack with Vercel.
**Success:** All API endpoints that interact with the database are successfully migrated to use Supabase, and data is correctly read from and written to the Supabase database.

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[packages/api/]] - Directory containing the Vercel Serverless Functions to be migrated.
- [[packages/api/requirements.txt]] - Python dependencies for the backend.
- [[README.vercel.md]] - Documentation for Vercel deployment and local development, including environment variables.

**Technical Requirements:**
- Replace `google-cloud-sql-connector` and `google-cloud-secret-manager` with `supabase-py`.
- Refactor all database connection logic in the API endpoints to use the `supabase-py` client.
- Update environment variable requirements in `README.vercel.md` to include `SUPABASE_URL` and `SUPABASE_KEY`.
- Ensure all SQL queries are compatible with Supabase's PostgreSQL.

**Integration Points:**
- Supabase for database storage and access.
- Vercel Serverless Functions making database calls to Supabase.

## ✅ Acceptance Criteria (AI Verification)
- [x] **Given** a request to an API endpoint that reads data (e.g., `/api/get_listings`), **when** the request is made, **then** the data is fetched from the Supabase database and returned correctly.
- [x] **Given** a request to an API endpoint that writes data (e.g., `/api/create_listing`), **when** the request is made, **then** the data is correctly inserted into the Supabase database.
- [x] **Given** the `README.vercel.md` file, **when** a developer reads it, **then** they can understand the Supabase environment variable requirements.

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [x] Read context files listed above
- [x] Understand current system state (Google Cloud SQL to Supabase)
- [x] Verify development environment ready
- [x] Confirm integration points exist

**Implementation Approach:**
- [x] Update `packages/api/requirements.txt` to include `supabase-py`.
- [x] Refactor each API endpoint in `packages/api/` to use the `supabase-py` client for database operations.
- [x] Update `README.vercel.md` with Supabase environment variable instructions.
- [x] Amend the commit message to accurately reflect the migration to Supabase.

## 📋 Progress Tracking
**Status:** Complete
**Current Step:** Documentation
**Next Action:** Await further instructions.

## 🔗 Context & Dependencies
**Depends On:** Migration of the project to Vercel.
**Enables:** A fully Vercel-native architecture with a simplified database backend.
**Reference:** Supabase documentation, `supabase-py` library documentation.

## 📝 AI Session Log

### **Session 1** (2025-11-18)
**AI Agent:** Gemini
**Progress:** Migrated all core API endpoints from using Google Cloud SQL to Supabase. Refactored database connection logic and updated dependencies.
**Decisions:** Used the `supabase-py` library for all database interactions. Updated `README.vercel.md` to reflect new environment variable requirements.
**Issues:** None.
**Handoff:** Amend commit message and create documentation.

## 🎉 Completion Summary
**Delivered:** All core API endpoints now use Supabase for database operations. The project is no longer dependent on Google Cloud SQL.
**Variance:** None.
**AI Learning:** The `supabase-py` library provides a convenient and Pythonic way to interact with a Supabase backend, making the migration from a standard PostgreSQL connection relatively straightforward.
**Next Recommended:** Await further instructions.
