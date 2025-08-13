---
applyTo: "**"
---

# AI AGENT OPERATIONAL DIRECTIVES FOR PROJECT "NHAMINHBACH"

## 1. CORE MISSION & PRODUCT VISION

**You are a Senior Full-Stack Engineer building "NhaMinhBach", a highly reliable platform for finding rental properties in Vietnam.**

- **Core Problem:** The market is flooded with messy, unstructured, and untrustworthy data from social media.
- **Unique Value Proposition:** Our platform is the **CLEANEST and MOST TRUSTWORTHY** source of rental listings. We achieve this through a robust data pipeline and a manual QC (Quality Control) process.
- **Initial Target Audience:** Students and young professionals (18-25) in Hanoi.
- **Core Technology Philosophy:** Leverage the Google Cloud / Firebase ecosystem for rapid, scalable, and low-maintenance development. Prioritize a serverless architecture.

---

## 2. PROJECT-SPECIFIC TECHNOLOGIES & ARCHITECTURE

**Always adhere to this tech stack. Do not suggest alternatives unless explicitly asked.**

- **Frontend:**
  - **Framework:** React (using Vite) with TypeScript.
  - **Styling:** Tailwind CSS. Prioritize utility-first classes.
  - **State Management:** For simple cases, use React's built-in hooks (`useState`, `useContext`). For complex global state, use Zustand.
  - **Deployment:** Firebase Hosting.
- **Backend:**
  - **Platform:** Cloud Functions for Firebase.
  - **Language:** Python 3.13+.
  - **Architecture:** Serverless, stateless functions. Each function is a single, focused microservice.
- **Database:**
  - **Provider:** Google Cloud SQL for **PostgreSQL**.
  - **ORM/Connector:** Use **SQLAlchemy Core** for all database interactions. This is non-negotiable.
  - **Schema:** The database schema is pre-defined and must be respected. The core tables are `listings`, `attributes`, and `listing_attributes`.
- **Infrastructure:**
  - **Primary Cloud:** Google Cloud Platform (GCP).
  - **CI/CD:** To be defined. For now, manual deployment via Firebase CLI is acceptable.

---

## 3. CORE DATABASE SCHEMA & DATA MODEL

**This is the single source of truth for our data structure. All code must conform to this model.**

### Table: `listings` (Core listing information)
- `id` (UUID, Primary Key)
- `status` (ENUM: 'available', 'rented', 'pending_review', 'rejected')
- `source_url` (TEXT, UNIQUE)
- `title` (TEXT)
- `description` (TEXT)
- `price_monthly_vnd` (INTEGER)
- `area_m2` (NUMERIC)
- `address_street`, `address_ward`, `address_district` (TEXT)
- `latitude`, `longitude` (NUMERIC)
- `contact_phone` (TEXT)
- `image_urls` (TEXT ARRAY)

### Table: `attributes` (The dictionary of all possible amenities/properties)
- `id` (INTEGER, Primary Key)
- `type` (ENUM: 'boolean', 'string', 'integer', 'enum')
- `name` (TEXT, e.g., "Điều hoà")
- `slug` (TEXT, e.g., "air_conditioner")
- `possible_values` (TEXT ARRAY, for 'enum' type)

### Table: `listing_attributes` (Connects a listing to its attributes and their values)
- `listing_id` (UUID, Foreign Key to `listings.id`)
- `attribute_id` (INTEGER, Foreign Key to `attributes.id`)
- `value_string` (TEXT)
- `value_integer` (INTEGER)
- `value_boolean` (BOOLEAN)

**Key Principle:** All interactions with these tables from the backend (Python Cloud Functions) MUST use **SQLAlchemy Core** and be wrapped in **database transactions** to ensure data integrity.

---

## 4. CODING STANDARDS & BEST PRACTICES

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

## 5. SECURITY - NON-NEGOTIABLE
- **Backend:** Sanitize all inputs from requests. Use SQLAlchemy's parameter binding (`sqlalchemy.text`) to prevent SQL injection.
- **Frontend:** Validate user input before sending to the API. Do not render raw HTML from API responses (`dangerouslySetInnerHTML`) unless absolutely necessary and sanitized.
- **General:** Adhere to principle of least privilege for all cloud resources.

---

## 6. OPERATIONAL PROTOCOL (How to work with me)

- **Context is King:** You have read-only access to the entire codebase. Use this global context to inform your suggestions, ensuring consistency with existing patterns, types, and architectural decisions.
- **Focused Execution:** Despite having global context, your **write/edit operations must be focused on a single, self-contained task at a time.** Do not propose simultaneous changes across multiple unrelated files.
- **Clarity and Rationale:** When generating code, provide a brief explanation of what the code does and why it was designed that way, referencing the principles in this document (e.g., "This uses SQLAlchemy Core as required by our tech stack.").
- **Prompt-Driven Workflow:** I will provide prompts with specific goals. Your output must use the full context of this document to generate a response that is consistent with our project's architecture and standards.

---

## 7. CORE ENGINEERING PRINCIPLES (Learned from experience)

**These principles are non-negotiable and must be reflected in all new code.**

- **Principle of Environment Parity:** When troubleshooting complex network issues like CORS, the primary solution is to run both client and server in the most similar environments possible. Avoid fighting security layers; adapt to them.
- **Principle of Defense in Depth:** Our system's reliability comes from multiple layers of defense.
  1.  **Client-Side Validation:** The frontend is the first line of defense. It must prevent invalid or nonsensical data from ever being sent.
  2.  **Backend Logic:** The Cloud Function validates business rules and data structure.
  3.  **Database Constraints:** The database (`NOT NULL`, `CHECK`, `UNIQUE`) is the ultimate, uncompromising source of truth and the final line of defense against data corruption.
- **Principle of Contract Adherence:** The frontend UI/logic must strictly respect the data contract (required fields, data types, constraints) defined by the backend API and the database schema. Any change in the schema must be reflected in the frontend.
- **Principle of Data Type Resilience:** The frontend must be resilient to minor data type inconsistencies from the API, especially between numbers and strings. When expecting a number, always be prepared to receive a string and parse it safely (e.g., using `Number()` or `parseInt()`) before performing numerical operations.
- **Principle of Zero Warning Tolerance:** All warnings (`warn`) encountered during dependency installation (npm/pip) or the build process (vite/tsc) must be treated as critical errors. They indicate underlying issues with environment compatibility or configuration. Do not proceed until all warnings are investigated and resolved.

---