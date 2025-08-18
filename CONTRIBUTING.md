# Contributing to NhaMinhBach

This document outlines the core principles, project structure, and development workflow required to contribute to the NhaMinhBach project. Adherence to these guidelines is mandatory.

## 1. Core Principles

This project is governed by a strict set of principles. Before writing any code, familiarize yourself with our [[engineering_principles]].

## 2. Project Structure (Monorepo)

This project is a monorepo containing multiple independent packages. Each package is a self-contained "kingdom".

-   `/packages/functions`: The Python backend (Cloud Functions/Services).
-   `/packages/scraper`: The Python local scraper tool.
-   `/packages/web`: The React frontend application.

## 3. Environment Setup Protocol (MANDATORY)

### 3.0. Secret Management Standard (MANDATORY)

**All secrets (API keys, database passwords, etc.) must be managed exclusively via Google Secret Manager.**

- Secrets are never stored in `.env` files, environment variables, or checked into source control.
- Only non-secret configuration (e.g., `GCP_PROJECT`, `INSTANCE_CONNECTION_NAME`, etc.) may be set via environment variables or config files.
- All Python code must use the provided utility function `get_secret(project_id, secret_id)` to fetch secrets at runtime.

**How to use secrets in code:**

```python
from utils import get_secret

GCP_PROJECT = os.environ.get("GCP_PROJECT")
DB_PASS = get_secret(GCP_PROJECT, "db-password")
INGEST_API_KEY = get_secret(GCP_PROJECT, "ingest-api-key")
```

**How to create and manage secrets:**

1. Create a secret in Google Secret Manager:
	```bash
	gcloud secrets create db-password --replication-policy="automatic" --project=$GCP_PROJECT
	gcloud secrets versions add db-password --data-file=- --project=$GCP_PROJECT <<< "your-db-password-here"
	```
2. Grant access to the service account running your code:
	```bash
	gcloud secrets add-iam-policy-binding db-password --member="serviceAccount:<YOUR_SA_EMAIL>" --role="roles/secretmanager.secretAccessor" --project=$GCP_PROJECT
	```

**Migration Note:**
- All legacy `.env` files containing secrets must be deleted. Only configuration variables may remain in `.env.yaml` or similar files.
- If you need to support local development, use Google Secret Manager with `gcloud auth application-default login`.

**Violations of this standard will be rejected in code review.**

### 3.1. GCP Region Standard (MANDATORY)

**All GCP services, deployments, and environment variables must use the region `asia-southeast1` unless explicitly required otherwise.**

- Set `GCP_REGION=asia-southeast1` in all config files and environment variables.
- When deploying services (Cloud SQL, Artifact Registry, Cloud Run, Cloud Functions, Pub/Sub, Cloud Scheduler, etc.), always specify `--region=asia-southeast1`.
- Example API endpoint URLs and resource names should use `asia-southeast1`.
- If you need to override the region for a specific service, document the reason in code comments and deployment scripts.

**Violations of this standard will be rejected in code review.**

Environment chaos is not tolerated. Each package manages its own isolated environment. **There is NO virtual environment at the project root.**

### 3.2. Setting up the Backend (`/packages/functions`)

**To be run once:**

```bash
# Navigate to the functions directory
cd packages/functions

# Create the virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**To start working:**

```bash
cd packages/functions
source .venv/bin/activate
# You are now ready to work on the backend.
```

### 3.3. Setting up the Scraper (`/packages/scraper`)

**To be run once:**

```bash
# Navigate to the scraper directory
cd packages/scraper

# Create the virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

**To start working:**

```bash
cd packages/scraper
source .venv/bin/activate
# You are now ready to work on the scraper.
```

### 3.4. Setting up the Frontend (`/packages/web`)

The frontend uses Node.js and `npm`.

**To be run once:**

```bash
# Navigate to the web directory
cd packages/web

# Install Node.js dependencies
npm install
```

**To start the development server:**

```bash
cd packages/web
npm run dev
```

## 4. Git & Commit Guidelines

-   The `.gitignore` file is configured to ignore all `.venv` directories.
-   Commit messages should be clear and concise.

