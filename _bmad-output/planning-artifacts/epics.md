---
stepsCompleted: [1, 2, 3, 4]
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
FR24: The System can identify and auto-ban non-human scraping agents via invisible "Honeypot" links.
FR25: The System can rate-limit the viewing of sensitive contact information per user.
FR26: The System can enforce a "Login Wall" for accessing owner/admin contact details.
FR27: Admins can manually input new listings (individually or in bulk) via the admin interface, reusing the manual edit components.

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
- **Starter Template:** Use the Custom Turborepo Construction with pnpm workspaces for React (Vite), FastAPI, and Docker (Scraper).
- **Data Modeling:** Use JSONB for property attributes in PostgreSQL, validated by Pydantic v2.
- **Migrations:** Use Alembic (v1.18.2) for schema evolution.
- **Identity & Auth:** Use Supabase Auth for user-facing services and Shared API Secret (X-NHB-SECRET) for Scraper-to-API communication.
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

FR1: Epic 2 - Seekers can navigate directly via GeoID.
FR2: Epic 2 - Seekers can build queries with chips.
FR3: Epic 1 - Seekers can perform keyword searches.
FR4: Epic 1 - Seekers can filter by Price, Ward, District.
FR5: Epic 2 - Seekers can view property map.
FR6: Epic 2 - Seekers can toggle search modes.
FR7: Epic 4 - Seekers can view historical price timeline.
FR8: Epic 1 - Seekers can view 'Real View' and 'Cons'.
FR9: Epic 2 - Seekers can initiate Zalo chat with Admin.
FR10: Epic 1 - Landlords can share via human-readable URLs.
FR11: Epic 2 - Users must pass a Login Wall for contact info.
FR12: Epic 2 - Users can trigger pre-filled Zalo messages with GeoID.
FR13: Epic 3 - System autonomously ingests social posts.
FR14: Epic 3 - System transforms unstructured text to structured data.
FR15: Epic 3 - System identifies unique properties via fingerprinting.
FR16: Epic 1 - System generates unique, hierarchical GeoIDs.
FR17: Epic 3 - System geocodes addresses with fallback logic.
FR18: Epic 3 - System rewrites descriptions using AI.
FR19: Epic 3 - Admins can review data side-by-side.
FR20: Epic 1 - Admins can manually override and edit attributes.
FR21: Epic 3 - Admins can approve or reject pending listings.
FR22: Epic 3 - Admins can view fingerprint collision alerts.
FR23: Epic 1 - Admins can manage available/rented status.
FR24: Epic 3 - System can auto-ban non-human scrapers via Honeypots.
FR25: Epic 2 - System rate-limits contact information views.
FR26: Epic 2 - System enforces login wall for owner details.
FR27: Epic 1 - Admins can manually input listings (individually or in bulk).

## Epic List

### Epic 1: The Manual MVP (Core Listing & Viewing)
Build the essential manual platform where Admins can create listings by hand and Seekers can discover and view them. Validates the core data model and user experience.
**FRs covered:** FR3, FR4, FR8, FR10, FR16, FR20, FR23, FR27.

### Epic 2: The "Smart" Search & Interaction
Enhance the seeker experience with the innovative "Smart Waterfall Search" (GeoID jumps, Guided Chips) and secure contact flows.
**FRs covered:** FR1, FR2, FR5, FR6, FR9, FR11, FR12, FR25, FR26.

### Epic 3: Automated Data Refinery & Geocoding
Introduce the high-throughput automation layer and cloud-based geocoding services to scale listing acquisition.
**FRs covered:** FR13, FR14, FR15, FR17, FR18, FR19, FR21, FR22, FR24.

### Epic 4: The Time Machine (Transparency & History)
Implement SCD Type 2 tracking to visualize historical price trends for properties.
**FRs covered:** FR7.

## Epic 1: The Manual MVP (Core Listing & Viewing)

Build the essential manual platform where Admins can create listings by hand and Seekers can discover and view them. Validates the core data model and user experience.

### Story 1.1: Project Scaffolding & Database Foundation

As a Developer,
I want to set up the monorepo and core database schema,
So that I have a solid foundation for implementing features.

**Acceptance Criteria:**

**Given** a clean project directory
**When** I run the initialization commands
**Then** a Turborepo monorepo is created with apps/web (Vite/React), apps/api (FastAPI), and packages/scraper
**And** pnpm and uv are configured for dependency management
**And** the project directory structure matches the architectural design document

**Given** a Supabase project
**When** I apply the initial Alembic migrations
**Then** the houses and rooms tables are created with support for JSONB attributes
**And** the schema supports SCD Type 2 history (tracking changes via valid_from/valid_to)

### Story 1.2: Admin Manual Listing Creation

As an Admin (Minh),
I want to manually input a new property listing,
So that I can start building the platform's data without automation.

**Acceptance Criteria:**

**Given** I am logged into the Admin interface
**When** I enter a property address and details (Price, Ward, District, Specs) and submit
**Then** the system checks for address fingerprint collisions
**And** generates a unique hierarchical GeoID (e.g., 29CG.W8K01)
**And** creates a new House and Room record in the database
**And** the new listing is saved with status "Available"

### Story 1.3: Seeker Discovery Grid & Keyword Search

As a Seeker (Hương),
I want to browse available listings and search by keywords,
So that I can find properties that match my basic criteria.

**Acceptance Criteria:**

**Given** I am on the home page
**When** I enter a keyword (e.g., "bancony") or select basic filters (Price Range, Ward)
**Then** the grid updates to show matching "Available" listings
**And** each card displays the Price, Location, and key specs
**And** the response time is responsive (< 1.5s FCP)

### Story 1.4: Property Detail View & Metadata

As a Seeker (Hương),
I want to view the full details of a property, including honest "Cons" and "Real View" images,
So that I can make an informed decision without visiting.

**Acceptance Criteria:**

**Given** I click on a listing card
**When** the detail page loads
**Then** I see the full address, structured specs, "Real View" images, and "Cons" list
**And** the URL is human-readable (e.g., /listing/29CG.W8K01) and shareable

### Story 1.5: Admin Listing Management

As an Admin (Minh),
I want to edit existing listing attributes and manage their status,
So that I can keep the platform data accurate and up-to-date.

**Acceptance Criteria:**

**Given** I am viewing a listing in the Admin interface
**When** I update a field (e.g., Price) or toggle status to "Rented"
**Then** the change is saved immediately to the database
**And** if the status is "Rented", the listing disappears from the public search grid

## Epic 2: The "Smart" Search & Interaction

Enhance the seeker experience with the innovative "Smart Waterfall Search" (GeoID jumps, Guided Chips) and secure contact flows.

### Story 2.1: Smart Search Bar State Machine

As a Seeker (Hương),
I want a search bar that understands different types of inputs,
So that I can navigate quickly without using complex filters.

**Acceptance Criteria:**

**Given** I focus on the search bar
**When** I type a GeoID regex (e.g., "29CG.W8"), a keyword, or a price shorthand (e.g., "3tr")
**Then** the Zustand state manager updates the search mode (Jump vs. Filter vs. Keyword)
**And** the UI provides visual feedback for the detected mode

### Story 2.2: Guided Query Chips

As a Seeker (Hương),
I want the search bar to suggest filter chips as I type,
So that I can build structured queries with minimal typing.

**Acceptance Criteria:**

**Given** I type an ambiguous term (e.g., "3") in the search bar
**When** the suggestion dropdown appears
**Then** I see structured chips like "[Price < 3m]" or "[Floor: 3]"
**And** tapping a chip adds it to the active filter set and updates the listing grid

### Story 2.3: GeoID "Teleport" Navigation

As a Seeker (Hương),
I want to jump directly to a property page when I enter its ID,
So that I can skip the search results list entirely.

**Acceptance Criteria:**

**Given** I enter a complete GeoID (e.g., "29CG.W8K01")
**When** the system matches the regex
**Then** the right-action button in the search bar pulses
**And** tapping it (or Enter) triggers an instant < 300ms transition to the detail page

### Story 2.4: Secure Contact & Login Wall

As an Admin (Minh),
I want to protect sensitive owner data behind a verification wall,
So that I can prevent bots from bulk-scraping contact information.

**Acceptance Criteria:**

**Given** I am on a property detail page
**When** I attempt to view the contact information
**Then** I am presented with a "Login Wall" (Supabase Auth) or verification gate
**And** access is granted only after successful authentication

### Story 2.5: Zalo Integration & Rate Limiting

As a Seeker (Hương),
I want to contact the admin via Zalo with property context,
So that I can inquire about a specific room efficiently.

**Acceptance Criteria:**

**Given** I have passed the verification wall
**When** I click the "Contact via Zalo" button
**Then** a pre-filled Zalo message is generated (e.g., "Hello, is listing 29CG.W8K01 still available?")
**And** the system increments my daily contact view count
**And** I am blocked after 5 views per day (NFR5)

### Story 2.6: Map View of Listings

As a Seeker (Hương),
I want to see properties on a map,
So that I can understand their location in relation to landmarks or my school.

**Acceptance Criteria:**

**Given** I toggle to "Map View"
**When** the map loads
**Then** I see property pins or circles based on their coordinate accuracy
**And** tapping a pin shows a mini-card preview with a link to details

## Epic 3: Automated Data Refinery & Geocoding

Introduce the high-throughput automation layer and cloud-based geocoding services to scale listing acquisition.

### Story 3.1: Stateless Facebook Scraper

As an Admin (Minh),
I want an automated scraper to capture rental leads from social media,
So that I don't have to manually browse Facebook groups for data.

**Acceptance Criteria:**

**Given** the scraper is deployed in a Docker container
**When** the scheduler triggers a shallow-scrape of targeted Facebook Groups
**Then** Playwright captures raw post text and images without requiring a logged-in account
**And** the raw data is sent to the `/api/v1/ingest` endpoint with the correct shared secret

### Story 3.2: Gemini AI Transformation Engine

As an Admin (Minh),
I want the system to automatically structure and rewrite raw social media posts,
So that I have clean, searchable data and unique content that prevents "search-back" to the original post.

**Acceptance Criteria:**

**Given** raw post data has been ingested
**When** the Gemini Flash transformation engine processes the text
**Then** it extracts structured attributes (Price, Ward, District, Amenities) into a Pydantic-validated JSON
**And** it generates a unique, rewritten description that maintains the original facts but uses different phrasing

### Story 3.3: Automated Geo-Identity & Fingerprinting

As a System,
I want to identify if a social media post refers to a property already in our database,
So that I can maintain a single source of truth for physical properties.

**Acceptance Criteria:**

**Given** structured data from the AI engine
**When** the system hashes the address and owner phone number
**Then** it checks for existing "fingerprint" collisions in Supabase
**And** it flags the refinery item as "Duplicate" or "Update" if a match is found, preserving the Geo-Identity

### Story 3.4: Geocoding Fallback Service

As a System,
I want to automatically map property addresses to geographic coordinates,
So that I can display them accurately on the seeker's map.

**Acceptance Criteria:**

**Given** a structured address
**When** the geocoding service is triggered
**Then** it attempts to resolve coordinates via the Google Maps API
**And** if Google fails, it automatically falls back to OSM Nominatim
**And** the final coordinates are saved with the listing

### Story 3.5: Side-by-Side QC Cockpit

As an Admin (Minh),
I want a high-throughput interface to verify AI-processed data,
So that I can maintain 100% data accuracy with minimal effort.

**Acceptance Criteria:**

**Given** items are pending in the refinery queue
**When** I open the QC Cockpit
**Then** I see a side-by-side comparison of the raw Facebook post and the AI-refined data
**And** I can edit any field and approve or reject the listing with a single click (or hotkey)
**And** approval instantly publishes the listing to the public feed

### Story 3.6: Bot Defense & Honeypots

As an Admin (Minh),
I want to protect my refined data from being stolen by competitor scrapers,
So that I maintain my competitive advantage as the "Clean Source of Truth."

**Acceptance Criteria:**

**Given** a non-human agent attempts to scrape the site
**When** it triggers an invisible "Honeypot" link
**Then** the system identifies the IP and automatically blacklists it within < 10 seconds
**And** the agent can no longer access sensitive contact or listing data

## Epic 4: The Time Machine (Transparency & History)

Implement SCD Type 2 tracking to visualize historical price trends for properties.

### Story 4.1: Historical Price Tracking

As a System,
I want to automatically snapshot price changes,
So that I can preserve a historical record of property valuation.

**Acceptance Criteria:**

**Given** an existing listing is being updated with a new price
**When** the update is committed
**Then** the current record is versioned (valid_to is set)
**And** a new record with the updated price is created (valid_from is set)
**And** the entire change is wrapped in a single database transaction

### Story 4.2: Price Timeline Visualization

As a Seeker (Hương),
I want to see a history of price changes for a property,
So that I can understand its market trend and build trust in the listing.

**Acceptance Criteria:**

**Given** I am on a property detail page
**When** I scroll to the "Price History" section
**Then** I see a visual timeline or chart showing historical price points
**And** the data is fetched accurately from the SCD Type 2 history records
