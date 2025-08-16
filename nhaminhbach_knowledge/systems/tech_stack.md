# Tech Stack
#system

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