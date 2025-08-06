// src/config.ts

/**
 * Centralized configuration for the application.
 * Using VITE_ environment variables allows us to set different values for
 * development and production builds.
 * Learn more: https://vitejs.dev/guide/env-and-mode.html
 */

// For local development with Firebase Emulators
const LOCAL_API_BASE_URL = 'http://127.0.0.1:5001/omega-sorter-467514-q6/asia-southeast1';

// The base URL for the API. It uses the VITE_API_BASE_URL from the .env file if it exists,
// otherwise it falls back to the local emulator URL.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || LOCAL_API_BASE_URL;