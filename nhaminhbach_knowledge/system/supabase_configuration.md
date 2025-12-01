# GeoID System - Supabase Configuration Guide
#process

This guide covers connecting the GeoID system to Supabase PostgreSQL.

---

## 🔐 Environment Variables (Required)

All code now uses Supabase exclusively. Set these environment variables:

```bash
# Supabase PostgreSQL Connection
export SUPABASE_DB_HOST="db.<your-project-ref>.supabase.co"
export SUPABASE_DB_PASSWORD="<your-supabase-password>"
export SUPABASE_DB_NAME="postgres"  # default
export SUPABASE_DB_USER="postgres"  # default
export SUPABASE_DB_PORT="5432"      # default
```

### How to Get Credentials

1. Go to Supabase Dashboard → Project Settings → Database
2. Copy **Connection String** (Transaction mode preferred)
3. Extract components:
   - Host: `db.<project-ref>.supabase.co`
   - Password: Your database password
   - Port: `5432`
   - Database: `postgres`
   - User: `postgres`

---

## 📦 Python Dependencies

Update `requirements.txt` to remove GCP dependencies:

```txt
# Database (Supabase PostgreSQL)
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.0  # or pg8000

# API Framework
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0

# LLM (if needed)
instructor>=1.0.0

# Utilities
python-dotenv>=1.0.0  # for local .env files
```

**Remove these GCP packages:**
- ~~google-cloud-secret-manager~~
- ~~cloud-sql-python-connector~~
- ~~google-cloud-pubsub~~
- ~~google-cloud-run~~
- ~~google-cloud-aiplatform~~

---

## 🚀 Usage Examples

### Migration Script
```bash
export SUPABASE_DB_HOST="db.abc123xyz.supabase.co"
export SUPABASE_DB_PASSWORD="your-password-here"

python3 migration_uuid_to_geoid.py --dry-run --limit 100
```

### API Server
```python
# In your FastAPI app
from geoid_api import create_listing_atomic, CreateListingRequest

# Env vars are read automatically by get_supabase_connection_string()

@app.post("/api/listings")
async def create_listing(request: CreateListingRequest):
    result = create_listing_atomic(request)
    return result
```

---

## 🧪 Testing Connection

```python
python3 -c "
import os
os.environ['SUPABASE_DB_HOST'] = 'db.abc123.supabase.co'
os.environ['SUPABASE_DB_PASSWORD'] = 'your-password'

from geoid_api import get_supabase_connection_string, get_db_connection

print('Connection string:', get_supabase_connection_string().replace(os.environ['SUPABASE_DB_PASSWORD'], '***'))

with get_db_connection() as conn:
    result = conn.execute('SELECT version();')
    print('PostgreSQL version:', result.scalar())
print('✅ Connection successful!')
"
```

---

## 🔒 Security Notes

1. **Never commit credentials to git**
   - Use `.env` files locally (add to `.gitignore`)
   - Use environment secrets in production (Vercel, Railway, etc.)

2. **Use Row-Level Security (RLS)** in Supabase for public APIs
   - Enable RLS on tables if exposing direct Supabase APIs
   - Our backend wraps all DB access, so RLS is optional for internal use

3. **Connection pooling**
   - SQLAlchemy engine uses connection pooling by default
   - For serverless (Vercel), use `pool_pre_ping=True` to verify connections

---

## 📎 Files Updated

- `geoid_api.py`: New transaction-safe API with Supabase connection
- `migration_uuid_to_geoid.py`: Updated to use `SUPABASE_DB_*` env vars
- `geoid_utils.py`: Core utilities (unchanged, DB-agnostic)

---

## 🆘 Troubleshooting

### "Missing Supabase credentials"
- Ensure `SUPABASE_DB_HOST` and `SUPABASE_DB_PASSWORD` are set
- Check with: `echo $SUPABASE_DB_HOST`

### "Connection refused"
- Verify host format: `db.<project-ref>.supabase.co` (no `https://`)
- Check Supabase project is not paused
- Verify IP not blocked (Supabase allows all IPs by default)

### "SSL required"
- Supabase requires SSL. SQLAlchemy uses SSL by default for `postgresql://` URLs
- If issues, add `?sslmode=require` to connection string

---

**Status:** ✅ Supabase migration complete, GCP dependencies removed
