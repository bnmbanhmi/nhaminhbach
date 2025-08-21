---
tags: #task-ai
status: #ready
owner: Minh
ai_agent: Frontend Agent
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: 16hr
complexity: Complex
---

# AI Task: Develop Approve/Edit/Reject Functionality

**Duration:** 16hr  
**Complexity:** Complex  
**AI Agent:** Frontend Agent

## 🎯 Objective (AI Context)
**What:** Build functional approve, edit, and reject buttons for the side-by-side review UI with full state management and API integration  
**Why:** Complete the QC workflow by enabling human reviewers to take action on pending listings - approve for publication, reject permanently, or edit before approval  
**Success:** Fully functional QC workflow where reviewers can approve listings (change status to 'available'), reject listings (change status to 'rejected'), or edit data inline before approval

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[implement_the_side_by_side_review_ui]] - Completed task showing current review page structure
- [[database_schema_and_model]] - Listing status enum values and update patterns
- [[QcCreatePage]] and [[ListingForm]] - Existing form components to reuse for edit functionality
- [[useListingForm]] - Form management hook to reuse/adapt for editing
- [[tech_stack]] - API patterns and state management approach

**Technical Requirements:**
- Reuse existing ListingForm component from QC Create page for edit mode
- Maintain side-by-side layout when in edit mode (raw text left, form right)
- Use React state management for edit/view mode switching
- Integrate with Cloud Functions API for status updates
- Implement optimistic UI updates with error handling
- Follow existing design system and component patterns

**Integration Points:**
- Update existing QcReviewPage to support edit mode toggle
- Create new API endpoints or extend existing ones for listing updates
- Integrate with existing useAdminListings hook for data refresh
- Maintain navigation flow back to QC Dashboard after actions

## ✅ Acceptance Criteria (AI Verification)
- [ ] **Given** a reviewer on side-by-side page, **when** clicking "Approve", **then** listing status changes to 'available' and success feedback is shown
- [ ] **Given** a reviewer on side-by-side page, **when** clicking "Reject", **then** listing status changes to 'rejected' with confirmation dialog
- [ ] **Given** a reviewer on side-by-side page, **when** clicking "Edit", **then** right side switches to editable form using ListingForm component
- [ ] **Given** edit mode is active, **when** making changes and clicking "Save & Approve", **then** listing data updates and status changes to 'available'
- [ ] **Given** any action is taken, **when** operation completes, **then** user is navigated back to QC Dashboard with updated listing state
- [ ] **Given** API errors occur, **when** operations fail, **then** clear error messages are displayed without breaking UI state

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [ ] Analyze current QcReviewPage structure and button placement
- [ ] Study ListingForm component and useListingForm hook patterns
- [ ] Understand existing API patterns from useAdminListings
- [ ] Design edit mode layout that maintains side-by-side comparison
- [ ] Plan API endpoints needed for listing status updates

**Implementation Approach:**
- [ ] Add edit mode state management to QcReviewPage
- [ ] Create reusable EditableListingForm component based on existing ListingForm
- [ ] Implement API functions for approve/reject/update operations
- [ ] Add confirmation dialogs and loading states for all actions
- [ ] Integrate optimistic updates and error handling
- [ ] Test complete workflow end-to-end

## 📋 Progress Tracking
**Status:** Ready  
**Current Step:** Awaiting AI agent pickup  
**Next Action:** Begin implementation with edit mode design and component reuse

## 🔗 Context & Dependencies
**Depends On:** [[implement_the_side_by_side_review_ui]] (completed - provides foundation UI)  
**Enables:** Complete QC workflow and public listing publication  
**Reference:** QC Create page ListingForm component for edit functionality patterns

## 📝 AI Session Log
_Track decisions and discoveries across AI handoffs_

### **Session 1** (Pending)
**AI Agent:** [Agent name]  
**Progress:** [What was accomplished]  
**Decisions:** [Key technical/design decisions made]  
**Issues:** [Problems encountered]  
**Handoff:** [State for next AI agent]

## 🎉 Completion Summary
**Delivered:** [What was actually built]  
**Variance:** [Any scope changes during implementation]  
**AI Learning:** [Technical insights for future similar tasks]  
**Next Recommended:** Proceed to public launch tasks (filtering, responsive design, source links)

---
**Final Status:** [Complete/Partial] | **Quality:** [Production Ready/Needs Review/Prototype]
