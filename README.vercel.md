# Vercel Deployment

This document outlines the architecture and deployment process for this project on Vercel.

## Architecture

The project is a monorepo with a React frontend and a Python backend using serverless functions.

-   **Frontend:** The frontend is a standard Vite+React application located in the `packages/web` directory.
-   **Backend:** The backend consists of Python serverless functions located in the `packages/api` directory. Each file in this directory corresponds to a serverless function endpoint. The functions use Flask to handle requests.

## Deployment

The project is deployed to Vercel. The `vercel.json` file at the root of the project contains the configuration for the deployment.

### Frontend

The frontend is deployed as a static site. Vercel automatically detects the Vite project in the `packages/web` directory and builds it.

### Backend

The backend is deployed as a set of serverless functions. Vercel automatically detects the Python files in the `packages/api` directory and deploys them as serverless functions.

### Environment Variables

The following environment variables need to be set in the Vercel project settings:

-   `SUPABASE_URL`: The URL of your Supabase project.
-   `SUPABASE_KEY`: The `anon` key for your Supabase project.
-   `GOOGLE_MAPS_API_KEY`: Your Google Maps API key for geocoding.

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

To run the backend, navigate to the `packages/api` directory and create a `.env` file with the following content:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

Then, run the following commands:

```bash
pip install -r requirements.txt
flask run
```
