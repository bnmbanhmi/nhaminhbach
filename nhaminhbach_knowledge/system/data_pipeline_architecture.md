# Data Pipeline Architecture
#system

## Overview
The data pipeline transforms raw Vietnamese rental property posts into clean, structured data ready for public consumption. This end-to-end flow is the core of our competitive advantage.

## Pipeline Stages

### 1. Data Ingestion
- **Source:** Local scraper targeting Vietnamese rental platforms
- **Method:** Playwright-based scraping with configurable scheduling
- **Storage:** Raw text data ingested via secure Cloud Functions API
- **Security:** API key authentication with Google Secret Manager
- **Status:** Raw listings marked as 'raw' in database

### 2. LLM Transformation  
- **Trigger:** Event-driven processing when new raw listings detected
- **Model:** Gemini 2.5 Flash Lite optimized for Vietnamese text processing
- **Framework:** Instructor + Pydantic for structured output generation
- **Validation:** Multi-layer validation (LLM → Pydantic → Database schema)
- **Status:** Successfully transformed listings marked as 'pending_review'

### 3. Quality Control
- **Interface:** Human-in-the-loop QC cockpit for review and validation
- **Workflow:** Side-by-side original text vs. structured data comparison
- **Actions:** Approve, Edit & Approve, or Reject with detailed reasons
- **Learning:** QC corrections feed back into LLM prompt optimization
- **Status:** Approved listings marked as 'available' for public display

### 4. Public Display
- **API:** RESTful endpoints serving validated listing data
- **Frontend:** React-based public interface with search and filtering
- **Performance:** Optimized queries and caching for fast user experience
- **SEO:** Search engine optimized for rental property discovery

## Technical Architecture

### Data Flow
```
Raw Scraping → Cloud Function Ingestion → PostgreSQL (raw)
     ↓
LLM Transformation → Pydantic Validation → PostgreSQL (pending_review)
     ↓
Human QC Review → Approval/Edit/Reject → PostgreSQL (available/rejected)
     ↓
Public API → React Frontend → User Search & Discovery
```

### Infrastructure Components
- **Database:** PostgreSQL on Google Cloud SQL
- **Processing:** Google Cloud Functions (Python 3.13+)
- **LLM Service:** Google Vertex AI with Gemini 2.5 Flash Lite model
- **Frontend:** React/Vite hosted on Firebase Hosting
- **Security:** Google Secret Manager for all credentials
- **Monitoring:** Cloud Functions logging and error tracking

## Quality Assurance

### Data Quality Metrics
- **Transformation Accuracy:** >95% successful LLM processing
- **Schema Compliance:** 100% database constraint adherence
- **Review Efficiency:** <2 minutes average QC review time
- **Publication Quality:** >98% approved listings require no corrections

### Performance Targets
- **Ingestion Latency:** <10 seconds from scraper to database
- **Transformation Speed:** <30 seconds per listing processing
- **API Response Time:** <500ms for listing queries
- **Frontend Load Time:** <2 seconds for search results

## Competitive Advantages

### Data Quality
- **Human-AI Collaboration:** Combines AI efficiency with human quality control
- **Vietnamese Optimization:** Specialized processing for Vietnamese rental terminology
- **Structured Data:** Clean, searchable data vs. unstructured competitors
- **Real-time Updates:** Fresh data pipeline maintains listing currency

### Technical Excellence
- **Scalable Architecture:** Cloud-native design handles growth automatically
- **Type Safety:** End-to-end type checking prevents data corruption
- **Event-Driven Processing:** Efficient resource utilization and cost optimization
- **Comprehensive Monitoring:** Proactive issue detection and resolution

## Future Enhancements

### Automation Opportunities
- **Smart QC:** ML models to pre-approve high-confidence transformations
- **Duplicate Detection:** Automated identification of duplicate listings
- **Price Validation:** Market analysis for price reasonableness checks
- **Image Analysis:** Automated image quality and relevance assessment

### Scaling Considerations
- **Batch Processing:** Parallel processing for high-volume ingestion
- **Regional Expansion:** Multi-city support with location-specific optimization
- **Multi-Platform Integration:** Additional data sources beyond current platforms
- **Real-time Processing:** Streaming data pipeline for immediate updates
