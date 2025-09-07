# Software Requirements Specification (SRS)

## nhaminhbach.com - The Cleanest Rental Platform

**Document Version:** 1.0  
**Date:** September 2, 2025  
**Project:** nhaminhbach.com Rental Platform  
**Document Owner:** Founder/Product Owner  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Technical Architecture](#6-technical-architecture)
7. [Data Requirements](#7-data-requirements)
8. [System Constraints](#8-system-constraints)
9. [Acceptance Criteria](#9-acceptance-criteria)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document defines the functional and non-functional requirements for nhaminhbach.com, a rental property aggregation and quality control platform targeting the Vietnamese rental market, specifically Hanoi.

### 1.2 Product Scope
nhaminhbach.com is a web-based platform that aggregates rental property listings from multiple sources (primarily Facebook groups), applies AI-powered data cleaning and quality control, and presents users with a curated, reliable source of rental properties. The platform aims to solve the problem of noisy, unstructured, and unreliable rental information in the Vietnamese market.

### 1.3 Intended Audience
- **Primary Users:** Students and young professionals (18-25 years old) in Hanoi
- **Secondary Users:** Property seekers with budget constraints (under 5 million VND)
- **Stakeholders:** Platform owner, potential landlords, property management companies

### 1.4 Document Conventions
- **Must/Shall:** Mandatory requirements
- **Should:** High priority but not mandatory
- **May/Could:** Optional or future considerations
- **Epic Codes:** E1, E2, E3, E4 refer to development phases

---

## 2. Overall Description

### 2.1 Product Perspective
The platform serves as an intermediary layer between chaotic rental data sources and end users, providing value through data curation, quality control, and user experience optimization.

### 2.2 Product Functions
#### Phase 1: Foundation & Data Factory ✅ COMPLETED
- Raw data scraping from Facebook groups and other sources
- AI-powered data transformation and standardization
- Internal Quality Control (QC) dashboard for manual verification
- Secure data ingestion pipeline from local to cloud

#### Phase 2: Public MVP - The Cleanest Source of Truth 🎯 IN PROGRESS
- Public-facing property listing interface
- Basic search and filtering capabilities
- Mobile-responsive design
- Source attribution and transparency

#### Phase 3: Experience & Trust Optimization 📋 PLANNED
- Advanced filtering and search functionality
- Community reporting features
- Performance optimization
- Brand and trust-building features

#### Phase 4: Trusted Transaction Platform 🔮 FUTURE
- Landlord verification system
- Direct listing submission
- Value-added services
- Monetization features

### 2.3 User Classes and Characteristics
#### Primary Users: Property Seekers
- **Demographics:** 18-25 years old, tech-savvy
- **Budget:** Under 5 million VND monthly rent
- **Pain Points:** Time-consuming searches, unreliable information, scams
- **Technical Proficiency:** High smartphone usage, comfortable with web interfaces

#### Secondary Users: Platform Administrators
- **Role:** Content moderation, quality control, system monitoring
- **Access Level:** Backend administrative tools
- **Responsibilities:** Data verification, user support, system maintenance

### 2.4 Operating Environment
- **Client Side:** Web browsers (Chrome, Safari, Firefox, Edge)
- **Server Side:** Google Cloud Platform (GCP)
- **Database:** PostgreSQL on Google Cloud SQL
- **CDN:** Firebase Hosting
- **Mobile:** Progressive Web App (PWA) capabilities

---

## 3. System Features

### 3.1 Data Acquisition and Processing

#### 3.1.1 Automated Data Scraping
**Priority:** High  
**Description:** System shall automatically collect rental listings from designated sources.

**Functional Requirements:**
- FR-DA-001: System must scrape data from Facebook rental groups on a scheduled basis
- FR-DA-002: System must handle rate limiting and API restrictions gracefully
- FR-DA-003: System must detect and avoid duplicate listings across sources
- FR-DA-004: System must capture metadata including source, timestamp, and original URL

#### 3.1.2 AI-Powered Data Transformation
**Priority:** High  
**Description:** System shall process raw data through AI transformation pipeline.

**Functional Requirements:**
- FR-DT-001: System must use Google Vertex AI (Gemini 2.5 Flash Lite) for data processing
- FR-DT-002: System must extract structured data from unstructured text using Instructor library
- FR-DT-003: System must classify listings by property type, location, and key attributes
- FR-DT-004: System must validate and standardize pricing information
- FR-DT-005: System must detect and flag potential spam or fraudulent listings

### 3.2 User Interface and Experience

#### 3.2.1 Property Listing Display
**Priority:** High  
**Description:** Users shall be able to view clean, organized property listings.

**Functional Requirements:**
- FR-UI-001: System must display property listings in a card-based grid layout
- FR-UI-002: Each listing must show: title, price, location, key amenities, images
- FR-UI-003: System must provide detailed view for each property
- FR-UI-004: System must include direct link to original source post
- FR-UI-005: System must be fully responsive across desktop, tablet, and mobile

#### 3.2.2 Search and Filtering
**Priority:** Medium  
**Description:** Users shall be able to filter listings based on their criteria.

**Functional Requirements:**
- FR-SF-001: System must provide filtering by district/location
- FR-SF-002: System must provide price range filtering
- FR-SF-003: System must provide filtering by key amenities (WiFi, parking, etc.)
- FR-SF-004: System must support keyword search across listing descriptions
- FR-SF-005: System must remember filter preferences during session

### 3.3 Quality Control and Trust

#### 3.3.1 Internal QC Dashboard
**Priority:** High  
**Description:** Administrators shall have tools to review and approve listings.

**Functional Requirements:**
- FR-QC-001: System must provide admin interface for reviewing pending listings
- FR-QC-002: System must allow manual approval/rejection of listings
- FR-QC-003: System must track approval status and reviewer information
- FR-QC-004: System must provide bulk operations for efficient review

#### 3.3.2 Community Reporting
**Priority:** Medium (Phase 3)  
**Description:** Users shall be able to report inaccurate or outdated listings.

**Functional Requirements:**
- FR-CR-001: System must provide "Report Inaccurate" button on listings
- FR-CR-002: System must provide "Already Rented" reporting option
- FR-CR-003: System must track reporting frequency for listing quality scoring

### 3.4 Data Management

#### 3.4.1 Database Operations
**Priority:** High  
**Description:** System shall efficiently store and retrieve property data.

**Functional Requirements:**
- FR-DB-001: System must use PostgreSQL with SQLAlchemy Core
- FR-DB-002: System must maintain core tables: listings, attributes, listing_attributes
- FR-DB-003: System must implement proper indexing for search performance
- FR-DB-004: System must handle concurrent read/write operations safely

---

## 4. External Interface Requirements

### 4.1 User Interfaces
- **Web Interface:** React-based responsive web application
- **Mobile Interface:** Progressive Web App (PWA) optimized for mobile devices
- **Admin Interface:** Dedicated dashboard for quality control operations

### 4.2 Hardware Interfaces
- **Client Devices:** Smartphones, tablets, desktop computers
- **Server Infrastructure:** Google Cloud Platform virtual machines
- **Storage:** Google Cloud SQL for structured data, Cloud Storage for media

### 4.3 Software Interfaces
- **Frontend Framework:** React 19+ with TypeScript, Vite build system
- **Styling:** Tailwind CSS for utility-first styling
- **Backend:** Python 3.13+ Cloud Functions
- **Database:** PostgreSQL with SQLAlchemy Core ORM
- **AI/ML:** Google Vertex AI with Instructor for structured outputs

### 4.4 Communication Interfaces
- **HTTP/HTTPS:** RESTful API communication
- **WebSocket:** Real-time updates (future consideration)
- **External APIs:** Facebook Graph API, Google Maps API

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **Response Time:** Page load time < 3 seconds on 3G connection
- **Throughput:** Support 1000+ concurrent users during peak hours
- **Data Processing:** Process and transform 500+ listings per hour
- **Search Performance:** Return search results within 1 second

### 5.2 Security Requirements
- **Data Encryption:** All data transmission must use HTTPS/TLS 1.3
- **Authentication:** Secure admin access with multi-factor authentication
- **API Security:** Rate limiting and input validation on all endpoints
- **Secret Management:** All credentials stored in Google Secret Manager

### 5.3 Reliability Requirements
- **Availability:** 99.5% uptime target
- **Data Integrity:** Zero data loss policy for approved listings
- **Backup:** Daily automated backups with point-in-time recovery
- **Monitoring:** Real-time system health monitoring and alerting

### 5.4 Scalability Requirements
- **Horizontal Scaling:** Cloud Functions auto-scaling based on demand
- **Database Scaling:** Read replicas for improved query performance
- **CDN:** Global content delivery for static assets
- **Caching:** Redis caching for frequently accessed data

### 5.5 Usability Requirements
- **Accessibility:** WCAG 2.1 AA compliance
- **Internationalization:** Vietnamese language primary, English fallback
- **Mobile-First:** Touch-optimized interface with gesture support
- **Loading States:** Clear feedback for all user actions

---

## 6. Technical Architecture

### 6.1 System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Firebase       │    │  Cloud Functions│
│   (React/Vite)  │◄──►│   Hosting        │◄──►│   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
                       ┌──────────────────┐              │
                       │   Google Cloud   │              │
                       │   SQL            │◄─────────────┘
                       │   (PostgreSQL)   │
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │   Vertex AI      │
                       │   (Gemini 2.5)   │
                       └──────────────────┘
```

### 6.2 Data Flow Architecture
1. **Data Ingestion:** Scrapers collect raw data from sources
2. **AI Processing:** Vertex AI transforms unstructured to structured data
3. **Quality Control:** Manual review and approval process
4. **Publication:** Approved listings served to public interface
5. **User Interaction:** Search, filter, and view operations

### 6.3 Security Architecture
- **Authentication:** Google Identity and Access Management (IAM)
- **Authorization:** Role-based access control (RBAC)
- **Data Protection:** Encryption at rest and in transit
- **Network Security:** VPC with firewall rules and private networking

---

## 7. Data Requirements

### 7.1 Core Data Entities

#### 7.1.1 Listings Table
- **listing_id:** Primary key (UUID)
- **title:** Property title (VARCHAR 500)
- **description:** Full description (TEXT)
- **price:** Monthly rent (INTEGER)
- **location:** Address/area (VARCHAR 255)
- **district:** Administrative district (VARCHAR 100)
- **source_url:** Original post URL (VARCHAR 1000)
- **created_at:** Timestamp (DATETIME)
- **status:** Approval status (ENUM: pending, approved, rejected)

#### 7.1.2 Attributes Table
- **attribute_id:** Primary key (UUID)
- **name:** Attribute name (VARCHAR 100)
- **category:** Attribute category (VARCHAR 50)
- **data_type:** Value type (ENUM: boolean, integer, string)

#### 7.1.3 Listing_Attributes Table
- **listing_id:** Foreign key to listings
- **attribute_id:** Foreign key to attributes
- **value:** Attribute value (TEXT)

### 7.2 Data Quality Standards
- **Completeness:** All required fields must be populated
- **Accuracy:** Price information must be validated and standardized
- **Consistency:** Location data must follow standard format
- **Timeliness:** Listings older than 30 days flagged for review

### 7.3 Data Retention Policy
- **Active Listings:** Retained indefinitely while active
- **Expired Listings:** Archived after 90 days of inactivity
- **User Data:** Minimal data collection, retained per privacy policy
- **Logs:** System logs retained for 30 days

---

## 8. System Constraints

### 8.1 Technical Constraints
- **Cloud Platform:** Must use Google Cloud Platform exclusively
- **Database:** PostgreSQL only, no NoSQL alternatives
- **Frontend:** React with TypeScript, no other frameworks
- **Backend:** Python Cloud Functions, serverless architecture only

### 8.2 Business Constraints
- **Budget:** Zero initial marketing budget (organic growth only)
- **Resources:** Single founder development model
- **Market:** Vietnamese market focus, Hanoi specifically
- **Compliance:** Must comply with Vietnamese data protection laws

### 8.3 Regulatory Constraints
- **Data Privacy:** Compliance with Vietnamese Personal Data Protection regulations
- **Content Liability:** Disclaimer requirements for aggregated content
- **Business Registration:** Proper business entity registration required for monetization

---

## 9. Acceptance Criteria

### 9.1 Phase 2 (Current) Acceptance Criteria
- ✅ **AC-P2-001:** Public listing interface displays minimum 100 verified listings
- 🎯 **AC-P2-002:** Basic filtering (district, price range) functions correctly
- 🎯 **AC-P2-003:** Mobile responsive design works on iOS and Android devices
- 🎯 **AC-P2-004:** Each listing shows original source link
- 🎯 **AC-P2-005:** Page load time under 3 seconds on 3G connection

### 9.2 Phase 3 Acceptance Criteria
- **AC-P3-001:** Advanced search returns relevant results within 1 second
- **AC-P3-002:** Community reporting system processes 95% of reports within 24 hours
- **AC-P3-003:** Site performance scores 90+ on Google PageSpeed Insights
- **AC-P3-004:** Local storage favorites persist across browser sessions

### 9.3 System Quality Acceptance Criteria
- **AC-SQ-001:** System maintains 99.5% uptime over 30-day periods
- **AC-SQ-002:** Data processing pipeline handles 500+ listings per hour
- **AC-SQ-003:** No critical security vulnerabilities in security audits
- **AC-SQ-004:** Database queries return results within 100ms average

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | [Founder Name] | ________________ | _________ |
| Technical Lead | [CTO Alex] | ________________ | _________ |
| Strategic Advisor | [Coach Martin] | ________________ | _________ |

---

**Document History:**
- Version 1.0 (September 2, 2025): Initial SRS creation based on project knowledge base

**Next Review Date:** October 2, 2025
