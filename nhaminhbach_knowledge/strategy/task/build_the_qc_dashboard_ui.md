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

# AI Task: Build the QC Dashboard UI

**Duration:** 16hr  
**Complexity:** Complex  
**AI Agent:** Frontend Agent

## 🎯 Objective (AI Context)
**What:** Build a comprehensive admin dashboard interface that allows human reviewers to view, filter, and manage pending rental listings from our transformation pipeline  
**Why:** Essential for data quality control - humans need to review and approve AI-generated structured data before it goes live to users  
**Success:** A functional admin dashboard where the founder can efficiently browse pending listings and navigate to detailed review interfaces

## 🤖 AI Agent Instructions
**Context Files to Read:**
- [[database_schema_and_model]] - Listings table structure and status states
- [[transformation_engine_results]] - S7 output format that QC interface will display
- [[ui_component_library]] - Existing design system and responsive patterns
- [[user_experience_requirements]] - Admin interface usability standards
- [[tech_stack]] - Frontend framework and styling approach

**Technical Requirements:**
- React.js with TypeScript for component development
- TailwindCSS for styling (consistent with existing design system)
- Responsive design patterns for tablet/desktop admin use
- Integration with PostgreSQL backend via REST API
- Real-time status updates using polling or WebSocket connections

**Integration Points:**
- REST API endpoints for listings with status="pending_review"
- Database queries filtered by listing status
- Navigation to detailed review interfaces (future tasks)
- Authentication system for admin access control

## ✅ Acceptance Criteria (AI Verification)
- [ ] **Given** the founder logs into the admin dashboard, **when** they view the main interface, **then** they see a list of all listings with status="pending_review"
- [ ] **Given** there are pending listings, **when** the founder uses filters, **then** they can filter by source_url, district, price range, and date created
- [ ] **Given** the founder clicks on a listing, **when** they navigate to detail view, **then** they can see the full listing data in a structured format
- [ ] **Given** the interface is responsive, **when** viewed on different screen sizes, **then** the layout adapts appropriately for admin workflow
- [ ] **Given** multiple listing statuses exist, **when** the founder selects different status filters, **then** they can view approved, rejected, and pending listings separately

## 🧭 AI Agent Preparation Checklist
**Before Starting:**
- [ ] Read context files listed above
- [ ] Understand current database schema for listings and attributes
- [ ] Verify React development environment is ready
- [ ] Confirm API endpoints exist for listing queries
- [ ] Review existing UI components and patterns

**Implementation Approach:**
- [ ] Create main dashboard layout with header, sidebar, and content area
- [ ] Implement listing table/card view with sortable columns
- [ ] Build filtering interface for status, location, price, and date
- [ ] Add pagination for large datasets
- [ ] Integrate real-time updates for status changes
- [ ] Ensure mobile-responsive design for tablet admin use

## 📋 Steps & Progress
- [ ] **Environment Setup** - Verify React/TypeScript environment and dependencies
- [ ] **API Integration** - Connect to backend listing endpoints with proper filtering
- [ ] **Main Layout** - Create responsive admin dashboard shell
- [ ] **Listing Table** - Build sortable, filterable table of pending listings
- [ ] **Filtering System** - Implement multi-criteria filtering for efficient review
- [ ] **Status Management** - Add status indicators and real-time updates
- [ ] **Responsive Design** - Ensure optimal tablet/desktop experience
- [ ] **Testing & Validation** - Verify all acceptance criteria are met

## 🔗 Related Tasks
**Dependencies:**
- [[migrate_llm_to_gemini_vertex_ai]] - ✅ COMPLETED (provides listing data structure)

**Leads to:**
- [[implement_the_side_by_side_review_ui]] - Detailed review interface for individual listings
- [[develop_approve_edit_reject_functionality]] - Action buttons and state management

## 🎯 Business Impact
**Efficiency:** Enables the founder to process 10+ listings in under 15 minutes  
**Quality Control:** Provides structured oversight of AI-generated data before public visibility  
**Workflow:** Establishes the foundation for scalable human-in-the-loop data processing

## 📝 Final Retrospective
_To be completed when task finishes_

### 📊 Task Results
**Planned Duration:** 16hr | **Actual Duration:** [To be filled]  
**Complexity Assessment:** [Simple/Medium/Complex - actual vs estimated]

### 🤖 AI Agent Performance
**Most Effective:** [What AI interaction patterns worked best for this UI work]  
**Challenging Areas:** [Where AI struggled with complex UI logic]  
**Context Loading:** [How well context files supported the implementation]

### 🔄 Process Improvements
**AI Instructions:** [How to improve AI agent briefings for complex UI tasks]  
**Context Management:** [Better ways to provide UI/UX guidance to AI]  
**Task Breakdown:** [How to better structure complex frontend work]

### 📚 Knowledge Captured
**Technical Patterns:** [Reusable admin interface patterns discovered]  
**Integration Insights:** [API integration and data flow optimizations]  
**UI/UX Learnings:** [Effective admin dashboard design principles]
