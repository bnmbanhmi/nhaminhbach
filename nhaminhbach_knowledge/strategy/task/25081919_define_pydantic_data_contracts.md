---
tags: #task
status: #active
id: 25081919_define_pydantic_data_contracts
owner: mac@bnms-Laptop
epic: [[E1]]
sprint: [[S7]]
---

# Task: Define Pydantic Data Contracts for LLM Transformation

**Owner:** mac@bnms-Laptop
**Date Started:** 2025-08-19

## Objective
Create a comprehensive set of Pydantic models in Python that serve as the strict, non-negotiable schema for our data transformation pipeline. These models must mirror the structure of the `listings` and `attributes` tables in our PostgreSQL database exactly, providing the blueprint for LLM output validation and ensuring data integrity throughout the transformation process.

## Steps & Progress

- [x] **Analyze Current Database Schema:** Review the exact structure of `listings`, `attributes`, and `listing_attributes` tables from our PostgreSQL database
- [x] **Create Base Pydantic Models:** Define core models for `Listing`, `Attribute`, and `ListingAttribute` entities
- [x] **Implement Field Validation:** Add proper data type validation, constraints, and custom validators to match database constraints
- [x] **Define Transformation Response Model:** Create a comprehensive model that represents the complete output structure the LLM must produce
- [x] **Add Enum Definitions:** Define all status enums and attribute types that match database constraints
- [x] **Implement Cross-Field Validation:** Add validators that ensure data consistency across related fields (e.g., attribute values match their types)
- [x] **Create Test Cases:** Build comprehensive test suite to validate model behavior with edge cases
- [x] **Documentation:** Document usage patterns and integration points for the transformation pipeline

## Issues Encountered & Resolved
- ✅ **Pydantic v2 Migration** - Updated from deprecated `@validator` and `@root_validator` to `@field_validator` and `@model_validator` - RESOLVED
- ✅ **Configuration Schema** - Updated `schema_extra` to `json_schema_extra` for Pydantic v2 compatibility - RESOLVED
- ✅ **Type Annotations** - Fixed type hint issues in database payload conversion functions - RESOLVED

## Current Status
- **Phase:** COMPLETED
- **Progress:** All Pydantic models created, validated, and tested successfully
- **Blockers:** None

## Next Actions
- Ready for integration with LLM transformation logic
- Models are prepared for Instructor library usage
- Database insertion patterns are established

## Links
- [Database Schema Documentation](/nhaminhbach_knowledge/system/database_schema_and_model.md)
- [Engineering Principles](/nhaminhbach_knowledge/principle/engineering_principles.md)
- [Sprint S7 Plan](/nhaminhbach_knowledge/strategy/sprint/S7.md)

## Decision Chronicle & Work Log
_Document key conversations, decisions, and turning points_

### **Initial Analysis**
> **Context:** Sprint S7 requires building automated data transformation pipeline to convert raw scraped text into structured data. Pydantic models serve as the contract between LLM output and our database.
> **Approach:** Mirror database schema exactly in Pydantic to ensure type safety and data integrity. Use Instructor library pattern for LLM integration.

### **Key Decisions**
- **Decision:** Use Pydantic models as single source of truth for transformation output validation
- **Rationale:** Ensures data integrity, provides clear contract for LLM, enables type-safe development
- **Reference:** Engineering Principle of Defense in Depth - multiple validation layers

### **Strategic Context**
This task is foundational for the entire S7 sprint. All subsequent transformation logic depends on these data contracts being correct and comprehensive. The models will serve as:
1. **LLM Output Schema:** What the AI must produce
2. **Validation Layer:** Ensuring data integrity before database insertion  
3. **API Contract:** Clear interface for transformation service
4. **Documentation:** Self-documenting code that reflects our data model

## Final Retrospective
_Complete when task is done - distill key learnings_

- **Trigger:** S7 sprint requires automated data transformation from raw scraped text to structured database entities
- **Final Outcome:** Comprehensive Pydantic data contract system that mirrors database schema exactly, with robust validation and LLM integration patterns
- **The "Aha!" Moment:** Separating transformation pipeline models from database insertion models creates clean abstraction layers and enables flexible LLM integration via Instructor library
- **Core Principle Learned:** Defense in Depth - Multiple validation layers (Pydantic models, field validators, cross-field validation) prevent data corruption at the contract level
- **Knowledge Captured:** Complete data contract specification in `/packages/functions/data_contracts.py` with comprehensive validation patterns for future transformation services

---
**Status:** DONE
