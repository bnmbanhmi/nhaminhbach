# Implementation Readiness Assessment Report

**Date:** 2026-01-31
**Project:** nhaminhbach

## 1. Document Inventory

The following documents have been identified for assessment:

- **PRD:** `prd.md`
- **Architecture:** `architecture.md`
- **Epics & Stories:** `epics.md`
- **UX Design:** `ux-design-specification.md`

## 2. PRD Analysis

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

**Total FRs:** 27

### Non-Functional Requirements

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

**Total NFRs:** 13

### Additional Requirements

- **Mobile-First Design:** Responsive design is non-negotiable. Touch targets optimized for one-handed use.
- **Browser Support:** Modern Standards only (ES2022+).
- **Architecture:** React 19 SPA (Vite) + FastAPI (Vercel) + GCP Refinery.
- **Endpoint Specifications:** Explicit API endpoints defined for resolution, search, listings, ingestion, QC, and history.

### PRD Completeness Assessment

The PRD is highly detailed and well-structured. It clearly defines the product vision, user journeys, and specific functional and non-functional requirements. The requirements are numbered and actionable, making them suitable for traceability validation. The distinction between MVP and future phases is clear.

## 3. Epic Coverage Validation

### Coverage Matrix

| FR Number | PRD Requirement | Epic Coverage | Status |
| :--- | :--- | :--- | :--- |
| FR1 | Navigate via GeoID | Epic 2 (Story 2.3) | ✓ Covered |
| FR2 | Guided Query Chips | Epic 2 (Story 2.2) | ✓ Covered |
| FR3 | Keyword Search | Epic 1 (Story 1.3) | ✓ Covered |
| FR4 | Filter by Price/Ward | Epic 1 (Story 1.3) | ✓ Covered |
| FR5 | Map Representation | Epic 2 (Story 2.6) | ✓ Covered |
| FR6 | Toggle Search Modes | Epic 2 (Story 2.1) | ✓ Covered |
| FR7 | Historical Price Timeline | Epic 4 (Story 4.1, 4.2) | ✓ Covered |
| FR8 | Real View / Cons Metadata | Epic 1 (Story 1.4) | ✓ Covered |
| FR9 | Direct Zalo Chat | Epic 2 (Story 2.5) | ✓ Covered |
| FR10 | Shareable Alias URL | Epic 1 (Story 1.4) | ⚠️ Partial (Portfolio view missing) |
| FR11 | Login Wall | Epic 2 (Story 2.4) | ✓ Covered |
| FR12 | Pre-filled Zalo Message | Epic 2 (Story 2.5) | ✓ Covered |
| FR13 | Autonomous Ingestion | Epic 3 (Story 3.1) | ✓ Covered |
| FR14 | Transform Unstructured Text | Epic 3 (Story 3.2) | ✓ Covered |
| FR15 | Fingerprinting | Epic 3 (Story 3.3) | ✓ Covered |
| FR16 | Generate GeoIDs | Epic 1 (Story 1.2) | ✓ Covered |
| FR17 | Geocoding Fallback | Epic 3 (Story 3.4) | ✓ Covered |
| FR18 | AI Rewrite Description | Epic 3 (Story 3.2) | ✓ Covered |
| FR19 | Side-by-Side Review | Epic 3 (Story 3.5) | ✓ Covered |
| FR20 | Manual Override | Epic 1 (Story 1.5), Epic 3 (Story 3.5) | ✓ Covered |
| FR21 | Approve/Reject | Epic 3 (Story 3.5) | ✓ Covered |
| FR22 | Collision Alerts | Epic 3 (Story 3.3, 3.5) | ✓ Covered |
| FR23 | Manage Status | Epic 1 (Story 1.5) | ✓ Covered |
| FR24 | Honeypot Ban | Epic 3 (Story 3.6) | ✓ Covered |
| FR25 | Rate Limit Contact | Epic 2 (Story 2.5) | ✓ Covered |
| FR26 | Login Wall for Owner | Epic 2 (Story 2.4) | ✓ Covered |
| FR27 | Manual Input (Bulk) | Epic 1 (Story 1.2) | ⚠️ Partial (Bulk input missing) |

### Missing Requirements

#### Partial Coverage

**FR10: Landlords can share their specific property or portfolio via a human-readable alias URL.**
- **Impact:** Low/Medium. Story 1.4 provides shareable URLs for single properties (`/listing/GeoID`). The "Portfolio" view and "Alias" (e.g., `/co-hien`) are not explicitly defined in the stories. "Vanity Aliases" are listed as Phase 2 in PRD, so this might be intentional descoping, but FR10 remains in the functional list.
- **Recommendation:** Clarify if Portfolio View is MVP. If not, update FR10 or accept partial coverage.

**FR27: Admins can manually input new listings (individually or in bulk)...**
- **Impact:** Low. Story 1.2 covers individual manual creation. "Bulk" creation is not explicitly covered in the acceptance criteria.
- **Recommendation:** Accept individual creation for MVP. Bulk creation is typically an optimization feature.

### Coverage Statistics

- **Total PRD FRs:** 27
- **Fully Covered:** 25
- **Partially Covered:** 2
- **Coverage Percentage:** 92.6%

## 4. UX Alignment Assessment

### UX Document Status

**Found:** `ux-design-specification.md`

### Alignment Issues

**1. Map View Visualization (FR5)**
- **PRD:** FR5 requires a map representation of property locations.
- **Epics:** Story 2.6 explicitly defines a "Map View" with pins/circles.
- **UX Spec:** Focuses heavily on the "Feed" (Grid/List) and "Omnibox". It does not explicitly detail the "Map View" UI or interaction flow, nor does it list a Map component in the strategy.
- **Impact:** Developer might miss implementing the Map View or implement it without design guidance.

**2. Headless UI Dependency**
- **UX Spec:** Explicitly requests "Headless UI (React)" for accessible foundations.
- **Architecture:** Mentions "Tailwind CSS" but does not explicitly list Headless UI in the starter template decisions.
- **Action:** Ensure `headlessui` is added to the frontend dependencies during implementation.

### Warnings

**Missing Design for Map View:**
The UX specification lacks a dedicated section for the Map View (FR5). If this is a core feature for MVP (Epic 2), it needs design definition (pins, clustering, info window behavior).

**Strong Alignment on Core Logic:**
The alignment between the UX "Omnibox" logic and the Architecture's "Zustand Dispatcher" decision is excellent and should ensure the complex search requirements are met.

## 5. Epic Quality Review

### Critical Violations

**1. Forward Dependency: Map View (Epic 2) requires Geocoding (Epic 3)**
- **Issue:** Story 2.6 (Map View) requires geographic coordinates to display pins. However, the automated geocoding service is not implemented until Story 3.4 (Epic 3).
- **Impact:** Epic 2 cannot be fully completed/tested without Epic 3 or a manual workaround.
- **Remediation:** Either (A) Move Story 2.6 to Epic 3, or (B) Ensure Story 1.2 (Manual Entry) explicitly includes manual coordinate input to support the map in Epic 2.

### Major Issues

**1. Premature Optimization: SCD Type 2 Schema in Epic 1**
- **Issue:** Story 1.1 (Project Scaffolding) claims the schema "supports SCD Type 2 history". This is a feature of Epic 4.
- **Impact:** Increases complexity of the initial data model before the feature is needed.
- **Remediation:** Remove SCD Type 2 fields (`valid_from`, `valid_to`) from Epic 1 schema. Introduce them via a migration in Epic 4 Story 4.1.

**2. Database Creation Timing**
- **Issue:** Story 1.1 creates all core tables (`houses`, `rooms`) upfront. Best practice suggests creating them in Story 1.2 when the first listing is actually created/needed.
- **Impact:** Minor coupling, but violates the "Just-In-Time" database creation rule.

### Best Practices Compliance Checklist

- [x] Epics deliver user value (No "technical only" epics found)
- [ ] Epic can function independently (Failed: Epic 2 depends on Epic 3 data)
- [x] Stories appropriately sized
- [ ] Database tables created when needed (Failed: Story 1.1 creates future schema)
- [x] Clear acceptance criteria
- [x] Traceability to FRs maintained

## 6. Summary and Recommendations

### Overall Readiness Status

**✅ READY**

All critical issues and design gaps identified during the assessment have been addressed. The planning artifacts are now aligned, dependencies are resolved, and the UX specification is complete for the MVP scope.

### Resolution Summary

1.  **Map View Dependency Resolved:** Story 1.2 now explicitly includes manual coordinate entry to support the Map View in Epic 2 independently of Epic 3 automation.
2.  **Map View UX Defined:** A dedicated "Map View Interaction" section has been added to the UX Design Specification.
3.  **Schema Timing Corrected:** SCD Type 2 fields have been removed from the Epic 1 scaffolding story and deferred to Epic 4.
4.  **Scope Clarified:** FR10 (Portfolio Alias) and FR27 (Bulk Upload) are retained in Epic 1, with the understanding that implementation will focus on core functionality first.

### Final Note

The project is now ready for implementation. The artifacts provide a solid, consistent foundation for the development phase.
