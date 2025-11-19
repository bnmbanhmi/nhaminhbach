# Vercel Migration Guide

This project has been migrated to use Vercel for both Frontend and Backend (Serverless Functions).

## 1. Project Structure

- **Frontend**: `packages/web` (Vite + React)
- **Backend**: `packages/functions/api/index.py` (FastAPI)
- **Configuration**: `vercel.json` (Root)

## 2. Deployment Instructions

### Prerequisites
- Vercel CLI installed (`npm i -g vercel`)
- Google Cloud Service Account credentials (if using GCP services like Cloud SQL, Secret Manager)

### Steps

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Deploy:**
   Run the following command from the root of the repository:
   ```bash
   vercel
   ```

3. **Configure Project Settings (First Time):**
   - **Build Command:** `cd packages/web && npm install && npm run build`
   - **Output Directory:** `packages/web/dist`
   - **Install Command:** `echo "No install needed for root"` (or leave default)

4. **Environment Variables:**
   Go to the Vercel Project Settings > Environment Variables and add:
   
   - `DB_PASS`: Your PostgreSQL database password.
   - `DB_USER`: Database user (default: postgres).
   - `DB_NAME`: Database name (default: postgres).
   - `INSTANCE_CONNECTION_NAME`: GCP Cloud SQL Instance Connection Name.
   - `GCP_PROJECT`: Your GCP Project ID.
   - `GOOGLE_APPLICATION_CREDENTIALS`: (Optional) JSON content of your service account key if you need to access GCP APIs like Secret Manager or Geocoding from Vercel.

   *Note: The code is updated to look for `DB_PASS` in environment variables first, so you don't strictly need Secret Manager if you set it in Vercel.*

## 3. Local Development

To run locally with Vercel:

```bash
vercel dev
```

This will start the frontend and backend, handling the `/api` rewrites automatically.
