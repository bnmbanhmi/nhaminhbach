# Deployment Guide

## Infrastructure

The project uses a dual-cloud strategy:

1.  **Vercel**: Hosts the Frontend (Web) and the lightweight API Gateway.
2.  **Google Cloud Platform (GCP)**: Hosts the heavy-lifting logic (Cloud Functions/Run), Database (Cloud SQL), and Pub/Sub.

## Configuration Files

-   `vercel.json`: Configures routes and rewrites for the Vercel deployment.
-   `cloudbuild.yaml`: Google Cloud Build configuration for deploying the `functions` package to Cloud Run.
-   `packages/functions/Dockerfile`: Container definition for the backend worker.

## Deploying Web & API (Vercel)

The Vercel deployment is likely triggered via Git push to `main`.
Manual deployment:

```bash
vercel deploy
```

## Deploying Backend Workers (GCP)

To deploy the Cloud Run services:

```bash
gcloud builds submit --config cloudbuild.yaml
```

Or manually deploy specific functions:

```bash
cd packages/functions
gcloud functions deploy ...
```

## Environment Variables

Ensure the following are set in Vercel and GCP Secret Manager:
-   `DATABASE_URL`
-   `GCP_PROJECT`
-   `INGEST_API_KEY`
