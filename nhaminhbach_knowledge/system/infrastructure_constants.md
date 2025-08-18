---
tags: #system #infrastructure
created: 2025-08-19
last_updated: 2025-08-19
status: active
---

# Infrastructure Constants Registry
**Single Source of Truth for All Infrastructure Configuration**

⚠️ **CRITICAL:** All deployment commands and configuration MUST reference this document. Never use hardcoded values.

## GCP Project Configuration
- **Project ID:** `omega-sorter-467514-q6`
- **Project Number:** `967311112997`
- **Default Region:** `asia-southeast1`
- **Default Zone:** `asia-southeast1-a`

## Cloud SQL Database
- **Instance ID:** `nhaminhbach-db-prod`
- **Connection Name:** `omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db-prod`
- **Database Name:** `postgres`
- **Primary User:** `postgres`
- **Password Secret:** `db-password` (Google Secret Manager)
- **Instance IP:** `34.87.38.127` (external)
- **Database Version:** PostgreSQL 15

## Cloud Functions
- **Ingestion API Function:** `ingest_scraped_data`
- **API Key Secret:** `ingest-api-key` (Google Secret Manager)
- **Function URL:** `https://asia-southeast1-omega-sorter-467514-q6.cloudfunctions.net/ingest_scraped_data`
- **Runtime:** `python311`
- **Memory:** `512MB`
- **Timeout:** `540s`
- **Region:** `asia-southeast1`

## Google Secret Manager Secrets
| Secret Name | Purpose | Full Path |
|-------------|---------|-----------|
| `db-password` | PostgreSQL database password | `projects/omega-sorter-467514-q6/secrets/db-password/versions/latest` |
| `ingest-api-key` | Cloud Function API authentication | `projects/omega-sorter-467514-q6/secrets/ingest-api-key/versions/latest` |
| `orchestrator-secret-key` | System orchestration key | `projects/omega-sorter-467514-q6/secrets/orchestrator-secret-key/versions/latest` |

## Environment Variables for Cloud Functions
Standard environment variables for function deployment:
```bash
INSTANCE_CONNECTION_NAME=omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db-prod
DB_USER=postgres
DB_NAME=postgres
GCP_PROJECT=omega-sorter-467514-q6
```

## Database Schema Information
- **Primary Database:** `postgres`
- **Main Tables:** `listings`, `attributes`, `listing_attributes`
- **Connection Method:** Cloud SQL Python Connector with pg8000
- **Authentication:** Username/password via Secret Manager

## Deployment Command Templates

### Cloud Function Deployment
```bash
cd /Users/mac/nhaminhbach.com/nhaminhbach/packages/functions

gcloud functions deploy ingest_scraped_data \
  --gen2 \
  --runtime=python311 \
  --region=asia-southeast1 \
  --source=. \
  --entry-point=ingest_scraped_data \
  --memory=512MB \
  --timeout=540s \
  --set-env-vars="INSTANCE_CONNECTION_NAME=omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db-prod,DB_USER=postgres,DB_NAME=postgres,GCP_PROJECT=omega-sorter-467514-q6" \
  --project=omega-sorter-467514-q6
```

### Database Connection Test
```bash
gcloud sql connect nhaminhbach-db-prod --project=omega-sorter-467514-q6 --user=postgres
```

### Secret Access Test
```bash
# Database password
gcloud secrets versions access latest --secret=db-password --project=omega-sorter-467514-q6

# API key
gcloud secrets versions access latest --secret=ingest-api-key --project=omega-sorter-467514-q6
```

## Local Development Configuration

### Scraper Environment (.env)
```properties
# GCP Project Configuration
GCP_PROJECT=omega-sorter-467514-q6

# Ingest API Configuration  
INGEST_API_URL=https://asia-southeast1-omega-sorter-467514-q6.cloudfunctions.net/ingest_scraped_data

# Note: INGEST_API_KEY is fetched from Google Secret Manager using the GCP_PROJECT setting above
```

## Change History
| Date | Change | Updated By | Reason |
|------|--------|------------|---------|
| 2025-08-19 | Initial creation | CTO Alex | Address S6 infrastructure config chaos |
| 2025-08-19 | Added deployment templates | CTO Alex | Standardize deployment commands |

## Verification Checklist
Before any deployment, verify:
- [ ] Database instance exists and is accessible
- [ ] Database user 'postgres' exists
- [ ] Required secrets exist in Secret Manager
- [ ] Function deployment uses exact constants from this registry
- [ ] Environment variables match this documentation

**Last Verified:** 2025-08-19
**Next Verification Due:** Before next infrastructure deployment
