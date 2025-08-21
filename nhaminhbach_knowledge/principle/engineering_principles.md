# Engineering Principles
#principle

**These principles are non-negotiable and must be reflected in all new code.**

- **Principle of Environment Parity:** When troubleshooting complex network issues like CORS, the primary solution is to run both client and server in the most similar environments possible. Avoid fighting security layers; adapt to them.

- **Principle of Defense in Depth:** Our system's reliability comes from multiple layers of defense.
  1.  **Client-Side Validation:** The frontend is the first line of defense. It must prevent invalid or nonsensical data from ever being sent.
  2.  **Backend Logic:** The Cloud Function validates business rules and data structure.
  3.  **Database Constraints:** The database (`NOT NULL`, `CHECK`, `UNIQUE`) is the ultimate, uncompromising source of truth and the final line of defense against data corruption.

- **Principle of Contract Adherence:** The frontend UI/logic must strictly respect the data contract (required fields, data types, constraints) defined by the backend API and the database schema. Any change in the schema must be reflected in the frontend.

- **Principle of Data Type Resilience:** The frontend must be resilient to minor data type inconsistencies from the API, especially between numbers and strings. When expecting a number, always be prepared to receive a string and parse it safely (e.g., using `Number()` or `parseInt()`) before performing numerical operations.

- **Principle of Zero Warning Tolerance:** All warnings (`warn`) encountered during dependency installation (npm/pip) or the build process (vite/tsc) must be treated as critical errors. They indicate underlying issues with environment compatibility or configuration. Do not proceed until all warnings are investigated and resolved.

- **Principle of LLM Data Integrity:** All LLM-generated data must pass through Pydantic validation before database storage. The database schema is the single source of truth - LLM outputs must conform exactly to database constraints.

- **Principle of Vietnamese Language Optimization:** All LLM prompts and processing must be specifically optimized for Vietnamese rental property terminology. Generic English prompts are insufficient for accurate Vietnamese text extraction.

- **Principle of Human-in-the-Loop Quality:** LLM transformations produce 'pending_review' status data that requires human QC validation before public display. AI efficiency combined with human quality control ensures data excellence.

- **Principle of Secret Management Compliance:** All API keys, credentials, and sensitive data must use Google Secret Manager. Environment variables are only for non-secret configuration. This principle is non-negotiable for production security.