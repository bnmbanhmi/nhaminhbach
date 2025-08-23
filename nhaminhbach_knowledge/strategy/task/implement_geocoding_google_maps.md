---
tags: #task-ai
status: #ready
owner: Minh
ai_agent: Frontend Agent
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 4hr
complexity: Medium
---

# AI Task: Implement Geocoding with Google Maps API for Addresses

**Duration:** 4hr  
**Complexity:** Medium  
**AI Agent:** Frontend Agent / Backend Agent

## 🎯 Objective (AI Context)
**What:** Add geocoding to transform structured address fields (address_street, address_ward, address_district) into latitude and longitude using the Google Maps Geocoding API. Ensure geocoding runs both when (a) a listing is created/edited via the QC workflow and (b) when the LLM transformation pipeline produces structured address data.
**Why:** Geocoded coordinates enable map display, radius searches, and more accurate location-based filtering for the public MVP.
**Success:** Listings include `latitude` and `longitude` populated when address fields are available; geocoding errors are logged and do not block listing approval.

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[database_schema_and_model]] - confirm latitude/longitude field names and constraints
- `packages/functions` transformation and ingestion code - to run geocoding server-side when transformation output is written
- `packages/web` ListingForm / EditableListingForm - to optionally trigger client-side geocoding in the QC flow

**Technical Requirements:**
- Prefer server-side geocoding inside the ingestion/transformation flow (Cloud Functions) to avoid leaking API keys and to centralize rate-limiting retries
- Use Google Secret Manager to store the Maps API key; do NOT use .env for secrets (CONTRIBUTING.md)
- Implement an idempotent geocoding function that checks for existing lat/lng and only calls the API when necessary
- Add retry/backoff and a simple caching layer (in-process cache keyed by normalized address) to reduce quota usage
- Log geocoding results and failures; do not prevent listing creation or approval on geocoding failure

**Integration Points:**
- Transformation service: after structured address is produced, call geocoding function and attach lat/lng before saving to DB
- QC Update API (`update_listing_data`): when a user edits address fields and saves, trigger geocoding server-side
- Optionally: expose a test-only endpoint to geocode a single address for QA

## ✅ Acceptance Criteria (AI Verification)
- [ ] Given a transformed listing with address fields, when transformation completes, then listing saved with valid `latitude` and `longitude` (or clear log entry on failure)
- [ ] Given an edit to address in QC workflow, when Save & Approve is clicked, then server runs geocoding and returns lat/lng in the updated listing
- [ ] Given repeated geocoding requests for the same normalized address, then cache prevents extra external API calls within reasonable TTL (e.g., 24h)
- [ ] Given an invalid address, then the system logs the failure and the listing is still processed with `latitude`/`longitude` null

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [ ] Confirm DB schema allows nullable latitude/longitude and review constraints
- [ ] Add Maps API key to Google Secret Manager and document secret id
- [ ] Identify where transformation service writes listings and add geocoding hook

**Implementation Approach:**
- [ ] Implement `geocode_address(address: str) -> {lat: float, lng: float} | None` in `packages/functions/utils.py` (or existing utils)
- [ ] Integrate geocode call into transformation flow where structured address is available
- [ ] Update `update_listing_data` Cloud Function to call geocode before saving
- [ ] Add unit tests for geocoding function (mocking external API)

## 📋 Progress Tracking
**Status:** Ready  
**Current Step:** Waiting for approval to start  
**Next Action:** Implement server-side geocoding in `packages/functions` once approved

---

**Notes & Assumptions:**
- We will store the Maps API key in Google Secret Manager and retrieve it server-side via `get_secret()` utility.
- If you prefer client-side geocoding for interactive QA, we'll implement it as an optional enhancement; server-side is the priority to protect API key.
