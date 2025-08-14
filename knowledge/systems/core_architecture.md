### General
- **Clarity and Simplicity:** Write code that is easy to read and understand. Prefer simple, explicit solutions over complex, clever ones.
- **Comments:** Explain the "why", not the "what". Document complex logic, business rules, and API contracts.

### Python (Backend - Cloud Functions)
- **Style:** Follow PEP 8 strictly. Use a tool like Black for auto-formatting.
- **Typing:** Use Python's type hints (`typing` module) for all function signatures and complex variables.
- **Error Handling:**
  - Use specific exceptions where possible.
  - All public-facing API functions must have a top-level `try...except` block to catch unexpected errors and return a generic 500 Internal Server Error, while logging the specific error for debugging.
- **Dependencies:** Manage all dependencies in `requirements.txt`.
- **Environment Variables:** Use a `.env.yaml` file for local development with Firebase Emulators. **Never hardcode secrets** like API keys or connection strings.

### TypeScript/React (Frontend)
- **Style:** Follow a standard style guide (e.g., Airbnb) enforced by ESLint and Prettier.
- **Component Structure:**
  - Break down UI into small, reusable components.
  - Separate logic (hooks) from presentation (JSX).
  - Create a `/components` directory with subdirectories for major features or UI elements (e.g., `/components/common`, `/components/listing`).
- **API Calls:**
  - Centralize API calling logic in a dedicated service/hook (e.g., `services/api.ts` or `hooks/useApi.ts`).
  - Use `fetch()` or a lightweight wrapper like `ky`. Do not add heavy libraries like Axios.
  - Always handle loading, success, and error states explicitly in the UI.

- **Database Interaction:** Always use **named parameters** (e.g., `sqlalchemy.text("... VALUES (:key)")`) instead of positional parameters (e.g., `VALUES (%s)`) for all SQL queries. This prevents data type mismatch errors caused by incorrect parameter order.

- **Link Styling:** When styling links (e.g., the `<Link>` component from `react-router-dom`), always explicitly apply the desired text color class (e.g., `text-text-primary`) and use `no-underline` unless a visual underline is explicitly desired. Always prioritize our defined design tokens.

- **Folder Structure (for `packages/web`):**
  /src/
    ├── assets/
    ├── components/       # Reusable UI components
    ├── hooks/            # Custom React hooks
    ├── pages/            # Top-level page components corresponding to routes
    ├── services/         # API clients, utility functions
    ├── state/            # State management (Zustand stores)
    ├── types/            # TypeScript type definitions
    └── App.tsx


