---
stepsCompleted: [1]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
---

# nhaminhbach - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for nhaminhbach, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Seekers can navigate directly to a specific property using a unique GeoID.
FR2: Seekers can build logical queries using a guided token-based interface (chips).
FR3: Seekers can perform standard keyword searches across property descriptions.
FR4: Seekers can filter property results by Price Range, Ward, and District.
FR5: Seekers can view a map representation of property locations (pin or circle based on accuracy).
FR6: Seekers can toggle between a "Guided Query" mode and standard keyword search.
FR7: Seekers can view a historical price timeline for a specific room (The "Time Machine").
FR8: Seekers can view "Góc nhìn thật" (Real view) and "Điểm trừ" (Cons) metadata for any listing.
FR9: Seekers can initiate a direct Zalo chat with the Platform Admin (Minh) regarding a specific property.
FR10: Landlords can share their specific property or portfolio via a human-readable alias URL.
FR11: Users can view property contact information only after passing a "Login Wall" or verification gate.
FR12: Users can trigger a pre-filled Zalo message template containing the property's GeoID.
FR13: The System can autonomously ingest raw rental posts from social media sources.
FR14: The System can transform unstructured Vietnamese text into structured property data.
FR15: The System can identify unique physical properties across multiple social posts using address/phone fingerprinting.
FR16: The System can automatically generate unique, hierarchical GeoIDs for new properties.
FR17: The System can geocode structured addresses into geographic coordinates using a fallback sequence.
FR18: The System can rewrite social media descriptions into unique platform content using AI.
FR19: Admins can review ingested data in a side-by-side comparison interface (Raw vs. Refined).
FR20: Admins can manually override and edit any attribute of a listing before approval.
FR21: Admins can approve or reject pending listings with a single action.
FR22: Admins can view fingerprint collision alerts for properties that have appeared historically.
FR23: Admins can manage the "Available/Rented" status of any room in the system.
FR27: Admins can manually input new listings (individually or in bulk) via the admin interface, reusing the manual edit components.
FR24: The System can identify and auto-ban non-human scraping agents via invisible "Honeypot" links.
FR25: The System can rate-limit the viewing of sensitive contact information per user.
FR26: The System can enforce a "Login Wall" for accessing owner/admin contact details.

### NonFunctional Requirements

NFR1: Short ID Resolution: Entering a GeoID in the search bar must resolve to the property page in < 300ms (network excluding).
NFR2: Search Intent Latency: Transforming natural language to a logical query and returning results must complete in < 800ms.
NFR3: First Contentful Paint (FCP): The public landing page must load in < 1.5s on a standard 4G connection in Hanoi.
NFR4: Mobile Smoothness: Touch interactions (scrolling, chip selection) must maintain 60fps to ensure a "Zalo-like" responsive feel.
NFR5: Data Protection (Smart Gating): Owner contact information must be protected behind a rate-limiting gate (e.g., maximum 5 contact views per day per user).
NFR6: Competitor Defense: Implement Honeypot link detection that automatically blacklists IPs demonstrating bulk-scraping behavior within < 10 seconds of detection.
NFR7: Data Integrity: All LLM-generated data must pass Pydantic schema validation before being committed to Supabase to prevent data corruption.
NFR8: Admin Security: Minh's access to the QC Cockpit must be secured via Multi-Factor Authentication (MFA) or Zalo Social Login.
NFR9: Horizontal Scraping: The GCP pipeline must support scaling to 50+ concurrent Cloud Run instances to handle regional expansion without architectural changes.
NFR10: Storage Strategy: Supabase storage must handle up to 100,000 active listings with price history without query performance degradation (using proper indexing on full_geo_id and address_hash).
NFR11: Refinery Throughput: The transformation engine must be capable of processing 1,000+ social media posts daily without human intervention bottlenecking the pipeline.
NFR12: SLA Freshness: Data ingested from social media must be processed and ready for verification in < 24 hours.
NFR13: Transactional Consistency: 100% of listing creations must be Atomic (House + Room + History) to prevent partial data states.

### Additional Requirements

**From Architecture:**
- **Starter Template:** Use the Custom Turborepo Construction with `pnpm` workspaces for React (Vite), FastAPI, and Docker (Scraper).
- **Data Modeling:** Use JSONB for property attributes in PostgreSQL, validated by Pydantic v2.
- **Migrations:** Use Alembic (v1.18.2) for schema evolution.
- **Identity & Auth:** Use Supabase Auth for user-facing services and Shared API Secret (`X-NHB-SECRET`) for Scraper-to-API communication.
- **Frontend State:** Use TanStack Query (v5.x) for server state and Zustand (v5.x) for client state (Search Bar).
- **Deployment:** Docker-First for Scraper, Vercel for App Tier.
- **Naming Conventions:** Strict adherence to defined naming (camelCase JSON, snake_case DB/Python) and structure patterns.
- **Error Handling:** Standardized Error Objects for API responses.

**From UX Design:**
- **Responsive Design:** Mobile-First SPA optimized for 360px-420px viewports.
- **Interaction:** "Smart Waterfall Search Bar" logic (GeoID -> Chips -> Keyword).
- **Touch Targets:** Minimum 44px hit area for all interactive elements.
- **Aesthetic:** "Future Warmth" palette (Coral/Cream) and "Her" aesthetic (soft rounded corners).
- **Component Strategy:** Use Headless UI wrapped in Tailwind CSS.
- **Navigation:** Bottom Sheets for detail views on mobile; Gestures for closing.
- **Accessibility:** Keyboard sovereignty for Search Bar; WCAG 2.1 AA contrast compliance.

### FR Coverage Map

{{requirements_coverage_map}}

## Epic List

{{epics_list}}
