---
tags: #task
status: #active
id: 25081920_build_core_transformation_logic
owner: mac@bnms-Laptop
epic: [[E1]]
sprint: [[S7]]
---

# Task: Build Core Transformation Logic

**Owner:** mac@bnms-Laptop
**Date Started:** 2025-08-19

## Objective
Develop the central Python function that transforms raw scraped text into structured, validated data entities. This function will accept raw text from scraped posts as input, construct detailed prompts for the Gemma LLM, and use the Instructor library to enforce the Pydantic data contracts we created in the previous task, ensuring the output is a validated, structured Python object ready for database insertion.

## Steps & Progress

- [ ] **Research and Install Instructor Library:** Install the Instructor library and understand its integration patterns with Pydantic models
- [ ] **Design LLM Prompt Template:** Create a comprehensive, zero-shot prompt template that guides the LLM to extract structured data from Vietnamese rental posts
- [ ] **Implement Core Transformation Function:** Build the main `transform_raw_post()` function that orchestrates the entire transformation pipeline
- [ ] **Configure LLM Client:** Set up the Gemma API client with proper authentication and error handling
- [ ] **Add Retry Logic:** Implement robust retry mechanisms for LLM API failures and malformed outputs
- [ ] **Build Validation Pipeline:** Create post-processing validation to ensure LLM output meets our business rules
- [ ] **Create Test Suite:** Build comprehensive tests with real Vietnamese rental post examples
- [ ] **Performance Optimization:** Optimize prompt engineering and response parsing for speed and accuracy

## Issues Encountered & Resolved
- [Track issues here with status indicators]

## Current Status
- **Phase:** Planning & Setup
- **Progress:** Starting - need to research Instructor library and LLM integration patterns
- **Blockers:** None

## Next Actions
- Install and explore Instructor library
- Research best practices for prompt engineering with structured output
- Design the transformation function architecture

## Links
- [Instructor Library Documentation](https://python.useinstructor.com/)
- [Pydantic Data Contracts](/packages/functions/data_contracts.py)
- [Sprint S7 Plan](/nhaminhbach_knowledge/strategy/sprint/S7.md)
- [Previous Task - Data Contracts](/nhaminhbach_knowledge/strategy/task/25081919_define_pydantic_data_contracts.md)

## Decision Chronicle & Work Log
_Document key conversations, decisions, and turning points_

### **Initial Analysis**
> **Context:** Need to build the core transformation engine that converts unstructured Vietnamese rental posts into our structured Pydantic models. This is the "brain" of our data factory.
> **Approach:** Use Instructor library to enforce Pydantic schema on LLM outputs, ensuring type safety and validation. Focus on prompt engineering for Vietnamese real estate domain.

### **Key Decisions**
- **Decision:** Use Instructor library for structured LLM outputs
- **Rationale:** Provides automatic validation, retry logic, and seamless Pydantic integration
- **Reference:** Engineering Principle of Defense in Depth - validation at LLM output level

### **Technical Architecture**
The transformation function will follow this pipeline:
1. **Input Validation:** Ensure raw text meets minimum requirements
2. **Prompt Construction:** Build context-rich prompts with examples
3. **LLM Invocation:** Call Gemma API via Instructor with Pydantic schema
4. **Output Validation:** Additional business logic validation
5. **Error Handling:** Graceful failures with retry mechanisms
6. **Response Formatting:** Convert to database-ready payload

## Final Retrospective
_Complete when task is done - distill key learnings_

- **Trigger:** [What originally caused this need]
- **Final Outcome:** [What was actually delivered]
- **The "Aha!" Moment:** [Key insight or realization]
- **Core Principle Learned:** [Link to principle reinforced or discovered]
- **Knowledge Captured:** [What documentation was updated]

---
**Status:** Active
