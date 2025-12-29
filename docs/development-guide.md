# Development Guide

## Prerequisites

-   **Node.js**: v18+ (for Web)
-   **Python**: v3.10+ (for API/Functions)
-   **PostgreSQL**: Database (Supabase or Cloud SQL)
-   **Google Cloud SDK**: For deploying functions

## Project Setup

### 1. Web Frontend (`packages/web`)

```bash
cd packages/web
npm install
npm run dev
```

Runs on `http://localhost:5173`.

### 2. Backend API (`api` & `packages/functions`)

The project uses a shared Python environment logic.

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r packages/functions/requirements.txt
pip install -r api/requirements.txt

# Run local server (FastAPI)
cd packages/functions
python local_server.py
```

## Environment Variables

Create `.env` files in `packages/web` and `packages/functions`.
Refer to `.env.example` (if available) or `config` templates.

Key variables:
-   `DATABASE_URL`: Connection string for PostgreSQL.
-   `GCP_PROJECT`: Google Cloud Project ID.

## Testing

-   **Web**: `npm run test` (Vitest)
-   **Backend**: `pytest` (looks for `test_*.py` files in `packages/functions`)
