# LLM Transformation Process
#process

## Overview
The LLM transformation process converts unstructured Vietnamese rental property text into structured, validated data ready for database storage. This process is the core of our data quality advantage.

## Pipeline Architecture

### Input Processing
- **Source:** Raw text from Vietnamese rental property posts
- **Format:** Unstructured text with prices, addresses, amenities in Vietnamese
- **Challenges:** Inconsistent formatting, abbreviations, regional variations

### LLM Transformation
- **Model:** Gemini 2.5 Flash Lite via Google Vertex AI
- **Library:** Instructor for structured output generation
- **Prompt Engineering:** Vietnamese-optimized prompts for rental property extraction
- **Output:** Structured JSON matching Pydantic data contracts

### Validation & Storage
- **Validation:** Pydantic models ensure database schema compliance
- **Status:** All new listings set to 'pending_review' for QC workflow
- **Database:** PostgreSQL storage via SQLAlchemy Core transactions
- **Error Handling:** Comprehensive logging and retry logic

## Technical Implementation

### Cloud Function Architecture
- **Endpoint:** `POST /transform_listing`
- **Runtime:** Python 3.13+ on Google Cloud Functions
- **Dependencies:** Instructor, Pydantic, Google Generative AI, SQLAlchemy
- **Deployment:** Firebase Functions with proper environment configuration

### Key Components
1. **Prompt Templates:** Vietnamese-specific prompts for property data extraction
2. **Attribute Mapping:** Dynamic system linking extracted features to database attributes
3. **Batch Processing:** Parallel processing capabilities for multiple listings
4. **Error Recovery:** Robust error handling with detailed logging

## Quality Assurance

### Success Metrics
- **Accuracy Target:** >95% successful transformation rate
- **Current Performance:** 100% success on Vietnamese test dataset
- **Validation:** Zero database constraint violations
- **Processing Speed:** <30 seconds per listing

### Monitoring & Alerts
- **Cloud Functions Monitoring:** Automatic error detection and logging
- **Schema Compliance:** Validation prevents any database mismatches
- **Performance Tracking:** Response time and success rate monitoring

## Integration Points

### Event-Driven Processing
- **Trigger:** Database events when new raw listings are ingested
- **Processing:** Automatic transformation of pending listings
- **Status Updates:** Automatic progression from 'raw' to 'pending_review'

### QC Workflow Integration
- **Review Interface:** Transformed data flows to QC cockpit for human review
- **Side-by-Side Comparison:** Original text vs. structured data display
- **Approval Workflow:** Human-in-the-loop validation before public display

## Vietnamese Language Optimization

### Specialized Handling
- **Address Parsing:** Vietnamese address format recognition (Street/Ward/District)
- **Price Extraction:** Multiple Vietnamese currency formats and abbreviations
- **Amenity Recognition:** Comprehensive Vietnamese amenity terminology
- **Regional Variations:** Support for Ho Chi Minh City and Hanoi terminology

### Continuous Improvement
- **Feedback Loop:** QC corrections improve future prompt engineering
- **Model Updates:** Regular evaluation of model performance on Vietnamese text
- **Dictionary Expansion:** Ongoing expansion of Vietnamese property terminology
