# Project Knowledge Base

## Project Overview

-   **Project**: NhaMinhBach
-   **Type**: Monorepo (Web + Backend + Scraper)
-   **Architecture**: Hybrid Serverless (Vercel + Google Cloud)

## Quick Reference

-   **Frontend**: React 19, Vite, Tailwind (`packages/web`)
-   **Backend**: Python, FastAPI, Vercel (`api`, `packages/functions`)
-   **Database**: PostgreSQL (EAV Schema)
-   **Docs Source**: `docs/` and `docs/_legacy_archive/`

## Generated Documentation

### Architecture & System Design
-   [Project Overview](./project-overview.md)
-   [Web Frontend Architecture](./architecture-web.md)
-   [Backend Architecture](./architecture-backend.md)
-   [Integration Architecture](./integration-architecture.md)
-   [Source Tree Analysis](./source-tree-analysis.md)

### Technical References
-   [API Contracts](./api-contracts.md)
-   [Data Models](./data-models.md)
-   [Web Component Inventory](./component-inventory-web.md)

### Guides
-   [Development Guide](./development-guide.md)
-   [Deployment Guide](./deployment-guide.md)
-   [Legacy Knowledge Archive](./_legacy_archive/nhaminhbach_knowledge/index.md) _(Reference Only)_

## Getting Started

1.  **Install**: Follow [Development Guide](./development-guide.md).
2.  **Run Web**: `cd packages/web && npm run dev`.
3.  **Run Backend**: `cd packages/functions && python local_server.py`.
