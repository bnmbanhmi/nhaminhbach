---
tags: #task-ai
status: #todo
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
created_date: 2025-11-19
owner: Minh
---

# Task: Migrate to Supabase

## 1. Context & Objective
Following the migration to Vercel and FastAPI, the next step in our infrastructure pivot is to replace Google Cloud SQL with Supabase. This will simplify our database management, provide a better developer experience, and align with our new Vercel-based stack.

## 2. Scope of Work
- [x] **Database Provisioning:** Create a new Supabase project.
- [x] **Schema Migration:** Export the current PostgreSQL schema from Cloud SQL and import it into Supabase.
- [ ] **Data Migration:** Migrate existing data (listings, attributes, etc.) to Supabase.
- [x] **Backend Configuration:** Update the FastAPI backend to connect to the Supabase PostgreSQL instance.
- [x] **Environment Variables:** Update Vercel environment variables with Supabase credentials.
- [ ] **Verification:** Test all API endpoints to ensure data integrity and connectivity.

## 3. Technical Details
- **Source:** Google Cloud SQL (PostgreSQL)
- **Destination:** Supabase (PostgreSQL)
- **Connection:** Use standard PostgreSQL connection string (SQLAlchemy compatible).

## 4. Success Criteria
- [ ] All tables and data are successfully replicated in Supabase.
- [ ] The Vercel-deployed application connects to Supabase without errors.
- [ ] `get_listings` and `create_listing` endpoints function correctly.
- [ ] Cloud SQL instance can be shut down.
