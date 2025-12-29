# Source Tree Analysis

## Project Structure Overview

The project is a **Monorepo** organized into four main parts:

1.  **Web Frontend** (`packages/web`): React 19 application using Vite and TailwindCSS.
2.  **API Backend** (`api`): Python/FastAPI backend (Vercel-ready).
3.  **Cloud Functions** (`packages/functions`): Google Cloud Functions/Run services for core logic and processing.
4.  **Scraper** (`packages/scraper`): Data ingestion service.

## Annotated Directory Tree

```
nhaminhbach/
├── api/                     # [Part: api] Vercel Serverless Function entry point
│   ├── index.py             # Main FastAPI app entry point
│   └── requirements.txt     # Python dependencies
├── packages/
│   ├── functions/           # [Part: functions] Core logic & Cloud Services
│   │   ├── api/             # API definition module
│   │   ├── sql/             # SQL schema migrations & scripts
│   │   ├── main.py          # Cloud Functions entry point (all endpoints)
│   │   ├── data_contracts.py # Pydantic data models (Data Contracts)
│   │   └── geoid_api.py     # GeoID logic
│   ├── scraper/             # [Part: scraper] Data ingestion
│   │   ├── main.py
│   │   └── requirements.txt
│   └── web/                 # [Part: web] Frontend Application
│       ├── src/
│       │   ├── components/  # React components
│       │   │   ├── ui/      # Reusable UI elements (SearchBar, etc.)
│       │   │   └── layout/  # Layout components (MainLayout, Navbar)
│       │   ├── pages/       # Route pages
│       │   └── utils/       # Helper functions (GeoID utils)
│       ├── vite.config.ts   # Vite configuration
│       └── package.json     # Frontend dependencies
├── docs/
│   ├── _legacy_archive/     # Archived legacy knowledge base
│   └── ...                  # Generated documentation (this folder)
├── firebase.json            # Firebase configuration
├── vercel.json              # Vercel configuration
└── cloudbuild.yaml          # Google Cloud Build config
```

## Critical Folders & Entry Points

| Part | Path | Entry Point | Purpose |
|------|------|-------------|---------|
| **Web** | `packages/web` | `src/main.tsx` (inferred) | User interface and client-side logic |
| **API** | `api` | `index.py` | Vercel serverless function handler |
| **Functions** | `packages/functions` | `main.py` | Core backend business logic and event handlers |
| **Scraper** | `packages/scraper` | `main.py` | Data collection and ingestion |

## Integration Points

-   **Web -> API**: The frontend calls the API endpoints (likely proxied or direct).
-   **API -> Functions**: The Vercel API likely imports or calls logic from `packages/functions` (shared code).
-   **Scraper -> Functions**: Scraper ingests data via `ingest_scraped_data` endpoint in Functions.
-   **Functions -> Database**: Direct SQLAlchemy connection to PostgreSQL.
