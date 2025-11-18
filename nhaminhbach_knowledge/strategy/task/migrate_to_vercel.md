---
tags: #task-ai
status: #complete
owner: Gemini
ai_agent: Gemini
epic: [[E4]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 2hr
complexity: Complex
---

# AI Task: Migrate Project to Vercel

**Duration:** 2hr
**Complexity:** Complex
**AI Agent:** Gemini

## 🎯 Objective (AI Context)
**What:** Migrate the project's frontend and backend from Firebase/Google Cloud to Vercel.
**Why:** To streamline deployment, simplify infrastructure, and leverage Vercel's platform features for a better developer experience.
**Success:** Frontend and backend are successfully deployed on Vercel, and all core API endpoints function correctly.

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[vercel.json]] - Vercel deployment configuration.
- [[packages/web/src/config.ts]] - Frontend API base URL configuration.
- [[README.vercel.md]] - Documentation for Vercel deployment and local development.
- [[packages/api/]] - Directory containing the new Vercel Serverless Functions.

**Technical Requirements:**
- Ensure `vercel.json` correctly routes API requests to `packages/api`.
- Update `README.vercel.md` to reflect the new directory structure and local development instructions.
- Maintain existing functionality of migrated API endpoints.

**Integration Points:**
- Vercel platform for deployment.
- Frontend (React/Vite) making API calls to Vercel Serverless Functions.

## ✅ Acceptance Criteria (AI Verification)
- [x] **Given** the project is deployed on Vercel, **when** the frontend loads, **then** it successfully fetches data from the Vercel Serverless Functions.
- [x] **Given** a request to an API endpoint (e.g., `/api/get_listings`), **when** the request is made, **then** the corresponding Vercel Serverless Function in `packages/api` is invoked and returns the correct response.
- [x] **Given** the `README.vercel.md` file, **when** a developer reads it, **then** they can understand the Vercel architecture and set up local development correctly.

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [x] Read context files listed above
- [x] Understand current system state (Firebase/GCP to Vercel)
- [x] Verify development environment ready
- [x] Confirm integration points exist

**Implementation Approach:**
- [x] Move the `api` directory to `packages/api`.
- [x] Update `vercel.json` to reflect the new API path.
- [x] Verify `packages/web/src/config.ts` for correct API base URL.
- [x] Update `README.vercel.md` with new API path and local development instructions.
- [x] Commit all changes.

## 📋 Progress Tracking
**Status:** Complete
**Current Step:** Documentation
**Next Action:** Create documentation for Supabase migration.

## 🔗 Context & Dependencies
**Depends On:** Initial migration of individual API endpoints to Vercel Serverless Functions.
**Enables:** Full project deployment on Vercel.
**Reference:** Vercel documentation, existing project structure.

## 📝 AI Session Log

### **Session 1** (2025-11-18)
**AI Agent:** Gemini
**Progress:** Identified the incorrect location of the `api` folder. Moved `api` to `packages/api`. Updated `vercel.json` and `README.vercel.md`.
**Decisions:** Moved `api` to `packages/api` to maintain monorepo structure. Updated `vercel.json` destination for API rewrites. Updated `README.vercel.md` to reflect new paths.
**Issues:** Initial oversight in placing the `api` folder.
**Handoff:** Commit changes and create documentation.

## 🎉 Completion Summary
**Delivered:** Project successfully configured for Vercel deployment, with API functions correctly located within `packages/api` and `vercel.json` and `README.vercel.md` updated accordingly.
**Variance:** Corrected initial structural oversight of `api` folder placement.
**AI Learning:** Emphasized the importance of adhering to monorepo conventions and thorough verification of pathing in configuration files.
**Next Recommended:** Document the Supabase migration.
