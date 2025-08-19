---
tags: #task
status: #active
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

- [ ] **Research Instructor Library:** Understand how to integrate Instructor with Gemini API for structured output
- [ ] **Design Prompt Engineering Strategy:** Create effective zero-shot prompts that guide the LLM to extract structured data
- [ ] **Implement Core Transform Function:** Build the main `transform_raw_post()` function using Instructor + Gemini
- [ ] **Create Attribute Mapping System:** Implement logic to map extracted attributes to database attribute IDs
- [ ] **Add Error Handling & Retry Logic:** Implement robust error handling for LLM API failures and validation errors
- [ ] **Test with Real Scraped Data:** Validate the transformation logic with actual Facebook post data
- [ ] **Performance Optimization:** Optimize for processing speed and cost efficiency
- [ ] **Integration Documentation:** Document the API and usage patterns for the transformation service

## Issues Encountered & Resolved
- [Track issues here with status indicators]

## Current Status
- **Phase:** Design & Implementation
- **Progress:** Starting - Instructor library installed, ready to build transformation logic
- **Blockers:** None

## Next Actions
- Research Instructor library documentation and Gemini integration patterns
- Design prompt templates for rental property data extraction
- Implement the core transformation function

## Links
- [Instructor Library Documentation](https://python.useinstructor.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Data Contracts Module](/packages/functions/data_contracts.py)
- [Sprint S7 Plan](/nhaminhbach_knowledge/strategy/sprint/S7.md)

## Decision Chronicle & Work Log
_Document key conversations, decisions, and turning points_

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
