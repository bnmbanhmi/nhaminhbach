---
tags: #process #infrastructure #security
created: 2025-08-19
last_updated: 2025-08-19
status: active
---

# Infrastructure Permissions Management Process

## Overview
This process ensures systematic and secure management of IAM permissions, Secret Manager access, and database connectivity for all Cloud Functions and services in our infrastructure.

## Core Principles

### 1. Least Privilege Access
- Grant only the minimum permissions required for functionality
- Regular audit and removal of unused permissions
- Service-specific IAM roles rather than broad permissions

### 2. Secret Manager as Single Source of Truth
- All sensitive data (API keys, passwords, tokens) MUST be stored in Google Secret Manager
- Never use environment variables for secrets
- Standardized secret naming convention: `service-purpose` (e.g., `gemini-api-key`, `db-password`)

### 3. Systematic Permission Verification
- Every Cloud Function deployment MUST include permission verification step
- Document service account used by each function
- Test secret access before declaring deployment complete

## Common Permission Patterns

### Cloud Functions Service Account Access
**Default Service Account:** `{PROJECT_NUMBER}-compute@developer.gserviceaccount.com`

**Standard Permissions Needed:**
```bash
# Secret Manager access for API keys
gcloud secrets add-iam-policy-binding {SECRET_NAME} \
  --member="serviceAccount:{PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project={PROJECT_ID}

# Cloud SQL access (if using Cloud SQL Connector)
gcloud projects add-iam-policy-binding {PROJECT_ID} \
  --member="serviceAccount:{PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

## Secret Manager Management

### 1. Secret Creation Standard
```bash
# Create secret
gcloud secrets create {SECRET_NAME} --project={PROJECT_ID}

# Add secret value
echo "{SECRET_VALUE}" | gcloud secrets versions add {SECRET_NAME} --data-file=- --project={PROJECT_ID}

# Grant access to Cloud Functions
gcloud secrets add-iam-policy-binding {SECRET_NAME} \
  --member="serviceAccount:{PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project={PROJECT_ID}
```

### 2. Current Project Secrets Registry
| Secret Name | Purpose | Access Pattern | Functions Using |
|-------------|---------|----------------|-----------------|
| `db-password` | PostgreSQL database password | `get_secret(project_id, "db-password")` | All DB functions |
| `ingest-api-key` | Cloud Function API authentication | `get_secret(project_id, "ingest-api-key")` | `ingest_scraped_data` |
| `orchestrator-secret-key` | System orchestration key | `get_secret(project_id, "orchestrator-secret-key")` | Orchestration functions |
| `gemini-api-key` | Gemini LLM API authentication | `get_secret(project_id, "gemini-api-key")` | `transform_property_post` |

## Database Access Management

### Cloud SQL Connection Permissions
```bash
# Grant Cloud SQL client role
gcloud projects add-iam-policy-binding {PROJECT_ID} \
  --member="serviceAccount:{PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# For Cloud SQL Proxy (if used)
gcloud projects add-iam-policy-binding {PROJECT_ID} \
  --member="serviceAccount:{PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.instanceUser"
```

### Database Connection Verification
```python
# Standard verification pattern in functions
def verify_db_connection():
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            return result == 1
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
```

## Deployment Permission Checklist

### Pre-Deployment Verification
- [ ] Identify all secrets the function will access
- [ ] Verify secrets exist in Secret Manager
- [ ] Grant secretAccessor role to function's service account
- [ ] Test secret access in local environment (if possible)
- [ ] Document all permissions granted

### Post-Deployment Verification
- [ ] Test function with real requests
- [ ] Verify all secret access works end-to-end
- [ ] Check function logs for permission errors
- [ ] Document any additional permissions needed
- [ ] Update this registry with new patterns

## Troubleshooting Common Issues

### "Permission denied accessing secret"
**Root Cause:** Service account lacks `secretmanager.secretAccessor` role
**Solution:**
```bash
gcloud secrets add-iam-policy-binding {SECRET_NAME} \
  --member="serviceAccount:{SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project={PROJECT_ID}
```

### "Could not connect to Cloud SQL"
**Root Cause:** Service account lacks `cloudsql.client` role
**Solution:**
```bash
gcloud projects add-iam-policy-binding {PROJECT_ID} \
  --member="serviceAccount:{SERVICE_ACCOUNT}" \
  --role="roles/cloudsql.client"
```

### "Environment variable not found"
**Root Cause:** Using environment variables for secrets (violation of our principles)
**Solution:** Migrate to Secret Manager using `get_secret()` utility

## Permission Audit Process

### Monthly Security Review
1. List all secrets and their IAM bindings
2. Verify each service account has minimum required permissions
3. Remove permissions for deprecated/unused functions
4. Update secret values if compromised or expired

### Commands for Audit
```bash
# List all secrets
gcloud secrets list --project={PROJECT_ID}

# Check secret permissions
gcloud secrets get-iam-policy {SECRET_NAME} --project={PROJECT_ID}

# List service accounts
gcloud iam service-accounts list --project={PROJECT_ID}

# Check service account permissions
gcloud projects get-iam-policy {PROJECT_ID} --filter="bindings.members:{SERVICE_ACCOUNT}"
```

## Emergency Procedures

### Immediate Secret Rotation
1. Create new secret version: `gcloud secrets versions add {SECRET_NAME} --data-file=-`
2. Test new version with affected functions
3. Disable old version: `gcloud secrets versions disable {VERSION} --secret={SECRET_NAME}`

### Permission Revocation
1. Remove IAM binding: `gcloud secrets remove-iam-policy-binding`
2. Verify function stops working (confirms permission removal)
3. Document incident and update procedures

## Integration with Development Workflow

### For New Cloud Functions
1. **Design Phase:** Document all secrets and permissions needed
2. **Development Phase:** Test with local service account keys (development only)
3. **Deployment Phase:** Grant production permissions following this process
4. **Validation Phase:** Verify all permissions work end-to-end
5. **Documentation Phase:** Update infrastructure constants and this registry

### For Existing Function Updates
1. **Change Analysis:** Identify new permission requirements
2. **Permission Updates:** Apply changes following this process
3. **Testing:** Verify both old and new functionality works
4. **Rollback Plan:** Document how to revert permissions if needed

---

## Process Maintenance

**Owner:** CTO Alex
**Review Frequency:** Monthly or after any permission-related incident
**Update Triggers:** New service deployment, security incident, audit findings
**Related Documents:** 
- [[infrastructure_constants.md]]
- [[security_principles.md]]
- [[deployment_procedures.md]]
