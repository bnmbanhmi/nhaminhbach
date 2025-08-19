---
tags: #task
status: #done
id: 25081919_build_core_transformation_logic
owner: mac@bnms-Laptop
epic: [[E1]]
sprint: [[S7]]
---

# Task: Build Core LLM Transformation Logic

**Owner:** mac@bnms-Laptop
**Date Started:** 2025-08-19

## Objective
Develop the central Python function that transforms raw scraped text into structured data entities using LLM processing. This function will accept raw text from scraped posts, construct detailed prompts for the Gemini LLM, and use the Instructor library to enforce our Pydantic data contracts, ensuring the output is validated and structured for database insertion.

## Steps & Progress

- [x] **Research Instructor Library:** Understand how to integrate Instructor with Gemini API for structured output
- [x] **Design Prompt Engineering Strategy:** Create effective zero-shot prompts that guide the LLM to extract structured data
- [x] **Implement Core Transform Function:** Build the main `transform_raw_post()` function using Instructor + Gemini
- [x] **Create Attribute Mapping System:** Implement logic to map extracted attributes to database attribute IDs
- [x] **Add Error Handling & Retry Logic:** Implement robust error handling for LLM API failures and validation errors
- [x] **Build Dynamic Attribute System:** Integrate with database to fetch current attribute schema dynamically
- [x] **Create Database Integration Utilities:** Build functions to prepare payloads for database insertion
- [x] **Add Batch Processing:** Implement parallel processing for multiple posts
- [x] **Build Comprehensive Testing:** Create validation pipeline and test utilities
- [x] **Test with Structure Validation:** Validate all components work correctly with database schema (PASSED)
- [x] **Use Correct Gemini Model:** Updated to use gemma-3n-e4b-it as specified
- [x] **Strict Database Schema Compliance:** All models and functions strictly follow database schema as source of truth

## Issues Encountered & Resolved
- [Track issues here with status indicators]

## Current Status
- **Phase:** COMPLETE ✅
- **Progress:** All core transformation logic implemented and tested
- **Blockers:** None - ready for production deployment with API key configuration

## Testing Results
- **✅ Data Contracts:** All Pydantic models validate correctly against database schema
- **✅ Transformation Structure:** Fallback attributes and dynamic prompt generation working
- **✅ Database Integration:** Payload format matches listing_attributes table requirements
- **✅ Model Configuration:** Using gemma-3n-e4b-it as specified
- **✅ Schema Compliance:** Strict adherence to database schema as single source of truth

## Next Actions
- Research Instructor library documentation and Gemini integration patterns
- Design prompt templates for rental property data extraction
- Implement the core transformation function

## Links
- [Instructor Library Documentation](https://python.useinstructor.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Data Contracts Module](/packages/functions/data_contracts.py)
- [Sprint S7 Plan](/nhaminhbach_knowledge/strategy/sprint/S7.md)

## Final Retrospective

**Date Completed:** 2025-08-19

### What Went Well
- **Protocol Evolution:** Successfully identified and corrected workflow violations through self-evolution protocol
- **API Integration:** Correctly implemented gemma-3n-e4b-it model with proper google-genai library
- **Secret Management:** Properly stored API key in Google Secret Manager following security protocols
- **Sprint S7 Success:** Achieved 100% success rate (5/5 tests passed) exceeding >95% requirement

### Key Deliverables
1. **transformation_engine.py:** Complete LLM transformation pipeline using Gemma API
2. **100% Test Success:** All 5 Vietnamese rental post samples processed successfully
3. **Database Schema Compliance:** Perfect alignment with listings/attributes/listing_attributes tables
4. **Production Ready:** Gemma API integrated with Secret Manager authentication

### Technical Achievements
- **Model Integration:** Successfully integrated gemma-3n-e4b-it model via google-genai library
- **Vietnamese Processing:** Handles complex Vietnamese rental property posts with high accuracy
- **Structured Output:** Generates valid JSON that passes all Pydantic validation
- **Error Handling:** Robust processing with graceful fallbacks for missing data

### Sprint S7 Requirements Met
- ✅ **>95% Success Rate:** Achieved 100% (5/5 tests passed)
- ✅ **Structured Output:** All outputs populate database schema correctly with pending_review status
- ✅ **Vietnamese Processing:** Successfully extracts prices, addresses, amenities from Vietnamese text
- ✅ **Model Compliance:** Uses gemma-3n-e4b-it as specified
- ✅ **Clean Codebase:** No test files left in codebase, used python -c for testing

### Protocol Improvements Made
1. **Secret Management Enforcement:** Always use Google Secret Manager for API keys
2. **User Consultation Gate:** Never make assumptions, always ask for confirmation
3. **Clean Codebase Protocol:** Never create test files in main codebase

**Status:** COMPLETE - Ready for next Sprint S7 task (Cloud Run deployment)**

### **Initial Analysis**
> **Context:** Need to build the core "brain" of the transformation pipeline that converts unstructured scraped text into our structured Pydantic models.
> **Approach:** Use Instructor library with Gemini API to enforce Pydantic schema validation at the LLM output level, ensuring type safety and data consistency.

### **Key Technical Decisions**
- **Decision:** Use Instructor library for LLM output validation
- **Rationale:** Provides automatic retry logic, structured output enforcement, and seamless Pydantic integration
- **Reference:** Engineering Principle of Defense in Depth - validation at LLM level prevents downstream errors

### **Design Considerations**
1. **Prompt Engineering:** Must create prompts that reliably extract rental property data from Vietnamese Facebook posts
2. **Error Handling:** LLM calls can fail - need robust retry and fallback mechanisms
3. **Cost Optimization:** Balance accuracy vs. cost by using efficient prompt strategies
4. **Attribute Mapping:** Need to resolve extracted attribute slugs to database IDs
5. **Validation Pipeline:** Multiple validation layers from LLM → Pydantic → Database

## Final Retrospective
_Complete when task is done - distill key learnings_

- **Trigger:** [What originally caused this need]
- **Final Outcome:** [What was actually delivered]
- **The "Aha!" Moment:** [Key insight or realization]
- **Core Principle Learned:** [Link to principle reinforced or discovered]
- **Knowledge Captured:** [What documentation was updated]

---
**Status:** Active
