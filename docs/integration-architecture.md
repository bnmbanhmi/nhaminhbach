# Integration Architecture

## System Overview

The system follows a **Modern Monorepo** pattern with a clear separation of concerns between the React frontend, Vercel-hosted API layer, and heavy-lifting Cloud Functions.

## Component Interactions

### 1. Web to Backend
-   **Protocol**: REST API (HTTPS)
-   **Flow**: The React frontend (`packages/web`) makes HTTP requests to the Vercel API endpoints (`api/index.py`).
-   **Data**: JSON payloads for Listings and Search queries.

### 2. API to Core Logic
-   **Pattern**: Direct Module Import / Shared Code
-   **Flow**: The `api/index.py` imports core logic and database connections from `packages/functions`.
-   **Benefit**: Allows sharing the same business logic between Vercel Serverless Functions and Google Cloud Run.

### 3. Data Ingestion (Scraper)
-   **Component**: `packages/scraper`
-   **Target**: `packages/functions/main.py` (Endpoint: `/ingest_scraped_data`)
-   **Auth**: API Key (`X-API-Key`)
-   **Flow**: Scraper collects data -> POSTs to Ingest Endpoint -> Database.

### 4. Asynchronous Processing
-   **Mechanism**: Google Cloud Pub/Sub
-   **Use Case**: Scraping Orchestration, Transformation Jobs.
-   **Flow**:
    1.  `orchestrate_scrapes` (Scheduled) -> Publishes messages to `scrape-requests`.
    2.  `execute_scrape_job` (Trigger) -> Consumes message -> Runs Cloud Run job.

## Data Flow Diagram

```mermaid
graph TD
    User[User / Browser] -->|HTTPS| Web[Web Frontend]
    Web -->|REST API| API[Vercel API]
    API -->|Import| Core[Core Logic (functions)]
    Core -->|SQLAlchemy| DB[(PostgreSQL)]
    
    Scraper[Scraper Service] -->|POST| Ingest[Ingest Endpoint]
    Ingest -->|SQLAlchemy| DB
    
    Scheduler[Cloud Scheduler] -->|Trigger| Orchestrator[Orchestrate Scrapes]
    Orchestrator -->|Pub/Sub| Topic[scrape-requests]
    Topic -->|Trigger| Worker[Scrape Job Worker]
```
