# Vercel Deployment

This document outlines the architecture and deployment process for this project on Vercel.

## Architecture

The project is a monorepo with a React frontend and a Python backend using serverless functions.

-   **Frontend:** The frontend is a standard Vite+React application located in the `packages/web` directory.
-   **Backend:** The backend consists of Python serverless functions located in the `api` directory. Each file in this directory corresponds to a serverless function endpoint. The functions use Flask to handle requests.

## Deployment

The project is deployed to Vercel. The `vercel.json` file at the root of the project contains the configuration for the deployment.

### Frontend

The frontend is deployed as a static site. Vercel automatically detects the Vite project in the `packages/web` directory and builds it.

### Backend

The backend is deployed as a set of serverless functions. Vercel automatically detects the Python files in the `api` directory and deploys them as serverless functions.

### Environment Variables

The following environment variables need to be set in the Vercel project settings:

-   `INSTANCE_CONNECTION_NAME`: The connection name of the Cloud SQL instance.
-   `DB_USER`: The username for the database.
-   `DB_NAME`: The name of the database.
-   `GCP_PROJECT`: The ID of the Google Cloud project.
-   `DB_PASS`: The password for the database. This should be stored as a Vercel secret.

## Local Development

For local development, you can run the frontend and backend separately.

### Frontend

To run the frontend, navigate to the `packages/web` directory and run:

```bash
npm install
npm run dev
```

You will also need to create a `.env.local` file in the `packages/web` directory with the following content:

```
VITE_API_BASE_URL=http://localhost:5000/api
```

### Backend

To run the backend, navigate to the `api` directory and run:

```bash
pip install -r requirements.txt
flask run
```

You will also need to set the environment variables listed above.
