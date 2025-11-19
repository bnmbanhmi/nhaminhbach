// src/config.ts

/**
 * Centralized configuration for the application.
 * Using VITE_ environment variables allows us to set different values for
 * development and production builds.
 * Learn more: https://vitejs.dev/guide/env-and-mode.html
 */

// Production Cloud Functions base URL (asia-southeast1)
// const PROD_API_BASE_URL = 'https://asia-southeast1-omega-sorter-467514-q6.cloudfunctions.net';
// Migrated to Vercel Serverless Functions
const PROD_API_BASE_URL = '/api';

// The base URL for the API. It uses the VITE_API_BASE_URL from the .env file if it exists,
// otherwise it falls back to the production Cloud Functions URL.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || PROD_API_BASE_URL;