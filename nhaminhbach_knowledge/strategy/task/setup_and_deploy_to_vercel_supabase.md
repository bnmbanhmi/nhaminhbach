---
tags: #task-ai
status: #ready
owner: [Human]
ai_agent: CTO Alex
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 1hr
complexity: Medium
---

# AI Task: Setup and Deploy to Vercel & Supabase Platforms

**Duration:** 1 hour
**Complexity:** Medium
**AI Agent:** CTO Alex

## 🎯 Objective (AI Context)
**What:** Provision the necessary infrastructure on the Vercel and Supabase platforms and link the local project.
**Why:** The application code for the Vercel/Supabase migration is complete, but the cloud environments have not been set up, which prevents actual deployment.
**Success:** The local project is successfully linked to live Vercel and Supabase projects, and all necessary environment variables are configured for a successful deployment.

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[CONTRIBUTING.md]] - To ensure secret management and environment setup protocols are followed.
- [[nhaminhbach_knowledge/system/infrastructure_constants.md]] - To check for any predefined constants or naming conventions.

**Technical Requirements:**
- Use Vercel CLI for Vercel operations.
- Use Supabase CLI for Supabase operations.
- All secrets must be set as environment variables in the Vercel dashboard/CLI, not in `.env` files.

**Integration Points:**
- The local monorepo needs to be linked to a Vercel project.
- The Vercel project needs to be configured with environment variables pointing to the Supabase instance.

## ✅ Acceptance Criteria (AI Verification)
- [ ] **Given** the Vercel and Supabase CLIs are installed, **when** the login and link commands are executed, **then** the local project is successfully connected to the remote platforms.
- [ ] **Given** the project is linked, **when** environment variables are set, **then** a subsequent deployment can successfully connect to the Supabase database.

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [ ] Confirm user has accounts for Vercel and Supabase.
- [ ] Read context files listed above.
- [ ] Prepare the sequence of CLI commands.

**Implementation Approach:**
- [ ] Step 1: Install CLIs and log in.
- [ ] Step 2: Link projects.
- [ ] Step 3: Configure environment variables.
- [ ] Step 4: Verify setup with a test deployment.

## 📋 Progress Tracking
**Status:** Ready
**Current Step:** Awaiting user approval of the plan.
**Next Action:** Begin Phase 1: Install Command-Line Tools.

## 🔗 Context & Dependencies
**Depends On:** [[migrate_to_vercel]], [[migrate_to_supabase]] (code completion).
**Enables:** [[deploy_web_to_custom_domain]], [[migrate_data_pipeline_to_vercel]].
**Reference:** Official Vercel and Supabase CLI documentation.

## 📝 AI Session Log
### **Session 1** (2025-11-18)
**AI Agent:** CTO Alex
**Progress:** Deconstructed user request, created this task file, and proposed a multi-phase deployment preparation plan.
**Decisions:** Decided to break down the process into CLI installation, authentication/linking, and environment configuration to ensure a structured and secure setup.
**Issues:** Initial user request was ambiguous; clarification was required to understand that platform setup, not code, was the objective.
**Handoff:** Awaiting user confirmation to proceed with the plan.
---
**Final Status:** [Pending] | **Quality:** [Production Ready]
