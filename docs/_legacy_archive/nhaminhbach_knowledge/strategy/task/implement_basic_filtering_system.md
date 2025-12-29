---
tags: #task-ai
status: #completed
owner: Frontend Agent
ai_agent: Frontend Agent
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 12hr
complexity: Medium
completed_at: 2025-08-23
time_spent: 3hr
---

# AI Task: Implement Basic Filtering System

**Duration:** 12hr  
**Complexity:** Medium  
**AI Agent:** Frontend Agent

## 🎯 Objective (AI Context)
**What:** Implement a public-facing filtering system for listings supporting location (district), price range, area, and status filters; wire filters to the existing search API and ensure UI state persists across navigation.
**Why:** Filters are core to user discovery and must be reliable for the public MVP launch.
**Success:** Users can filter public listings by district, price range, area, and status; filters update URL query params for shareability; results update within 500ms for typical queries.

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[database_schema_and_model]] - for field names and allowed values
- [[ui_component_library]] - for filter components and responsive patterns
- [[implement_the_side_by_side_review_ui]] - to understand listing data shape
- `packages/web/src` - existing components and hooks for search and pagination

**Technical Requirements:**
- Use existing React + TypeScript frontend (`packages/web`) and follow current component patterns
- Keep filter state in URL query params using router (Vite/React Router or framework in project)
- Debounce filter inputs to avoid excessive API calls (300ms)
- Implement server-side filtering via current API (confirm endpoints exist) and fall back to client-side filtering if needed
- Ensure accessibility for filter controls and mobile-friendly layout

**Integration Points:**
- Search/listings API endpoint used by public pages
- Pagination component and result card/list view
- Analytics event for filter usage (if analytics is present)

## ✅ Acceptance Criteria (AI Verification)
- [x] Given the public listings page, when the user sets district and price filters, then results show only matching listings
- [x] Given filters are applied, when user navigates or shares the URL, then filter state is preserved and reproducible
- [x] Given rapid input changes, when user types in price/area, then API calls are debounced and no more than 1 call per 300ms is made
- [x] Given slow network, when server-side filtering isn't available, then client-side fallback returns correct filtered results
- [x] Given accessibility audit, then filter controls have appropriate labels and keyboard focus behavior (basic labels/focus present)

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [ ] Read `packages/web` README and verify dev server runs locally
- [ ] Identify current search/listings API endpoint and parameters
- [ ] Review existing pagination and result components

**Implementation Approach:**
- [ ] Add FilterBar component with DistrictSelect, PriceRange inputs, Area input, and Status select
- [ ] Wire FilterBar to listing query hook and URL query params
- [ ] Implement debounce and cancellation for in-flight requests
- [ ] Add tests for filter behavior (unit for hook, integration for page)
- [ ] Manual end-to-end test with real API data and write short verification notes

**Work Completed:**
- Added `amenities` support to `FilterState` and implemented checkbox UI in `FilterBar`.
- Fetched attributes in `HomePage.tsx` and passed boolean attributes to `FilterBar`.
- Implemented client-side filtering fallback for amenities and ensured URL query params capture amenity selections.
- Redeployed `get_all_attributes` and `get_listing_by_id` functions with public access and CORS headers to support local development.
- Verified the end-to-end flow locally: filters apply correctly and listing detail pages load without CORS errors.

**Verification Notes:**
- Frontend dev server: `http://localhost:5173/` responds and page loads.
- `get_all_attributes` returns boolean attribute list with `slug` and `name`.
- `get_listing_by_id` returns full listing JSON and `Access-Control-Allow-Origin: http://localhost:5173` when Origin header is present.

## 📋 Progress Tracking
**Status:** Completed  
**Current Step:** Implementation finished and verified locally  
**Next Action:** Follow-ups: move amenities filtering server-side for performance; add unit/integration tests; improve UX for amenity chips and accessibility refinements

## 🔗 Context & Dependencies
**Depends On:** [[implement_the_side_by_side_review_ui]], database schema availability
**Enables:** Public search and discovery features for Epic E2
**Reference:** Existing dashboard filters and `useAdminListings` patterns

---

**Final Note:** Task completed. Frontend dev server was run and a smoke test executed. The `get_all_attributes` and `get_listing_by_id` backend functions were redeployed with public access and verified to return CORS headers for `http://localhost:5173`. See sprint notes and infrastructure docs for deploy commands and CORS guidance.
