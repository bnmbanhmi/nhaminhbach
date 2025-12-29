# Backend Architecture

## Executive Summary
The Backend operates as a hybrid serverless architecture, leveraging Vercel for user-facing APIs and Google Cloud Platform (Cloud Run/Functions) for heavy background processing and data ingestion. It is unified by a shared Python codebase.

## Technology Stack
-   **Framework**: FastAPI
-   **Runtime**: Python 3.10+
-   **Database**: PostgreSQL (via SQLAlchemy & pg8000)
-   **Infrastructure**: Vercel (API), Google Cloud Run (Workers), Pub/Sub (Messaging)

## Architecture Pattern
**Service-Oriented / Hybrid Serverless**:
-   **API Layer**: Stateless HTTP handlers optimized for cold starts (Vercel).
-   **Core Logic**: Domain logic decoupled from the HTTP layer, residing in `packages/functions`.
-   **Event-Driven**: Asynchronous tasks handled via Pub/Sub to decouple ingestion from processing.

## Data Architecture
The system uses a Relational Database (PostgreSQL) with an **Entity-Attribute-Value (EAV)** model for flexibility.

### Key Models
-   **Listings**: Core entity (`id`, `title`, `price`, `address`).
-   **Attributes**: Definitions of features (`Air Conditioner`, `Balcony`).
-   **ListingAttributes**: Links listings to specific attribute values.

## Key Components
1.  **Ingestion Engine**: `ingest_scraped_data` endpoint handles raw data from scrapers.
2.  **Transformation Engine**: LLM-powered module (`transform_raw_post`) to structure unstructured text.
3.  **GeoID System**: Custom addressing logic (`29CG.AB1`) for unique, human-readable IDs.
