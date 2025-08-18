---
tags: #process
created: 2025-08-19
priority: high
trigger: infrastructure deployment failures in S6
---

# Infrastructure Configuration Management Process

## Problem Statement
During Sprint S6, we encountered repeated deployment failures due to scattered infrastructure constants and configuration drift:
- Database credentials inconsistent across deployment commands
- Secret names mismatched (ingestion-api-key vs ingest-api-key)
- Database names confused (nhaminhbach vs postgres)
- User names incorrect (nhaminhbach vs postgres)
- No single source of truth for infrastructure constants

**Impact:** Multiple deployment cycles, trial-and-error debugging, wasted development time.

## Solution: Centralized Infrastructure Configuration

### 1. Infrastructure Constants Registry

Create `/nhaminhbach_knowledge/system/infrastructure_constants.md` as the single source of truth:

```markdown
# Infrastructure Constants Registry

## GCP Project
- **Project ID:** omega-sorter-467514-q6
- **Project Number:** 967311112997
- **Default Region:** asia-southeast1

## Cloud SQL Database
- **Instance ID:** nhaminhbach-db-prod
- **Connection Name:** omega-sorter-467514-q6:asia-southeast1:nhaminhbach-db-prod
- **Database Name:** postgres
- **Primary User:** postgres
- **Password Secret:** db-password (Google Secret Manager)

## Cloud Functions
- **Ingestion API:** ingest_scraped_data
- **API Key Secret:** ingest-api-key (Google Secret Manager)
- **Endpoint:** https://asia-southeast1-omega-sorter-467514-q6.cloudfunctions.net/ingest_scraped_data

## Secret Manager Secrets
- **Database Password:** projects/omega-sorter-467514-q6/secrets/db-password/versions/latest
- **Ingestion API Key:** projects/omega-sorter-467514-q6/secrets/ingest-api-key/versions/latest
```

### 2. Pre-Deployment Configuration Verification

Before any infrastructure deployment, MUST run verification checklist:

#### Database Configuration Check
```bash
# Verify database exists
gcloud sql databases list --instance=nhaminhbach-db-prod --project=omega-sorter-467514-q6

# Verify user exists  
gcloud sql users list --instance=nhaminhbach-db-prod --project=omega-sorter-467514-q6

# Test password secret access
gcloud secrets versions access latest --secret=db-password --project=omega-sorter-467514-q6
```

#### Secret Manager Verification
```bash
# List all secrets
gcloud secrets list --project=omega-sorter-467514-q6

# Verify specific secrets exist
gcloud secrets versions list db-password --project=omega-sorter-467514-q6
gcloud secrets versions list ingest-api-key --project=omega-sorter-467514-q6
```

### 3. Deployment Command Templates

#### Cloud Function Deployment Template
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

### 4. Configuration Drift Prevention

#### Mandatory Process Steps:
1. **Reference Registry First:** Always check infrastructure_constants.md before deployment
2. **Verify Before Deploy:** Run pre-deployment verification checklist  
3. **Update Registry:** If any constants change, update the registry FIRST
4. **Test After Deploy:** Verify deployment with actual API call

#### Configuration Change Protocol:
1. Identify need for configuration change
2. Update infrastructure_constants.md with new values
3. Update all affected deployment scripts/commands
4. Test in development environment first
5. Deploy to production with verification
6. Document change in decision log

### 5. Error Prevention Rules

#### NEVER:
- ❌ Use hardcoded constants in deployment commands
- ❌ Deploy without checking the infrastructure registry
- ❌ Assume database names/users from memory
- ❌ Skip pre-deployment verification

#### ALWAYS:
- ✅ Reference infrastructure_constants.md as source of truth
- ✅ Run verification checklist before deployment
- ✅ Test configuration with actual API calls after deployment
- ✅ Update registry when any constants change

## Implementation Priority
**IMMEDIATE:** This process addresses critical technical debt identified in S6 and must be implemented before next infrastructure deployment.

## Success Metrics
- Zero deployment failures due to configuration issues
- Single-command deployment success rate: 100%
- Infrastructure constant consistency across all services
- Reduced debugging time for deployment issues
