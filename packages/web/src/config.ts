// src/config.ts

/**
 * Centralized configuration for the application.
 * Using VITE_ environment variables allows us to set different values for
 * development and production builds.
 * Learn more: https://vitejs.dev/guide/env-and-mode.html
 */

// The base URL for the API. In production, this will be a relative path
// so that requests are proxied to the Vercel serverless functions.
// In development, this can be overridden by a .env file.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';