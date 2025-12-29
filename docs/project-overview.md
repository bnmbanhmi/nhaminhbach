# Project Overview: NhaMinhBach

## Mission
"The Cleanest Rental Platform" - Providing transparent, verified, and easily searchable rental listings for Vietnam.

## System Summary
NhaMinhBach is a modern rental platform featuring a **Hybrid Serverless Architecture**. It combines a fast, reactive frontend with a robust Python backend capable of complex data ingestion and LLM-based transformation.

## Key Highlights
-   **GeoID System**: A revolutionary addressing schema (`29CG.AB1`) for precise location tracking.
-   **AI-Powered**: Uses LLMs to transform unstructured rental posts into structured data.
-   **Monorepo**: Unified codebase for Web, API, and Cloud Functions.

## Architecture Type
**Hybrid Monolith/Microservices (Monorepo)**:
-   **Frontend**: SPA (React)
-   **Backend**: Split between API Gateway (Vercel) and Workers (Cloud Run).

## Repository Structure
-   `packages/web`: Frontend
-   `api`: Backend API Adapter
-   `packages/functions`: Backend Core & Workers
-   `packages/scraper`: Data Collection

## Documentation Index
-   [Web Architecture](./architecture-web.md)
-   [Backend Architecture](./architecture-backend.md)
-   [Integration Architecture](./integration-architecture.md)
-   [API Contracts](./api-contracts.md)
-   [Data Models](./data-models.md)
-   [Development Guide](./development-guide.md)
-   [Source Tree Analysis](./source-tree-analysis.md)
