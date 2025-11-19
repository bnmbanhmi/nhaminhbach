# Supabase Migration Guide

This guide outlines the steps to migrate the NhaMinhBach database from Google Cloud SQL to Supabase.

## 1. Create Supabase Project
1.  Go to [Supabase Dashboard](https://supabase.com/dashboard).
2.  Click **"New Project"**.
3.  Select an organization and enter a name (e.g., `nhaminhbach-db`).
4.  Set a strong database password (save this!).
5.  Choose a region close to your users (e.g., Singapore `sin1` or Tokyo `tky1`).
6.  Click **"Create new project"**.

## 2. Initialize Database Schema
1.  Once the project is created, go to the **SQL Editor** in the left sidebar.
2.  Click **"New query"**.
3.  Copy the content of `packages/functions/sql/supabase_schema.sql` from this repository.
4.  Paste it into the SQL Editor and click **"Run"**.
    *   *Note: This will create the `listings`, `attributes`, and `listing_attributes` tables.*

## 3. Configure Vercel Environment Variables
1.  Go to your [Vercel Project Settings](https://vercel.com/dashboard).
2.  Navigate to **Settings** > **Environment Variables**.
3.  Add the following variable:
    *   **Key:** `DATABASE_URL`
    *   **Value:** Your Supabase Connection String.
        *   Find this in Supabase: **Project Settings** > **Database** > **Connection string** > **URI**.
        *   Make sure to replace `[YOUR-PASSWORD]` with the password you set in Step 1.
        *   *Tip: Use the "Session" mode (port 5432) for migration, but "Transaction" mode (port 6543) is often better for Serverless functions if you have high concurrency.*

## 4. Data Migration (Optional / Manual)
If you need to migrate existing data from Cloud SQL:
1.  Export data from Cloud SQL using `pg_dump`.
2.  Import into Supabase using `psql`.
    ```bash
    # Example Import Command
    psql -h aws-0-ap-southeast-1.pooler.supabase.com -p 6543 -U postgres.[your-project-ref] -d postgres -f dump_file.sql
    ```

## 5. Verify
1.  Redeploy your Vercel application (or wait for the next push).
2.  Check the logs in Vercel to ensure the database connection is successful.
