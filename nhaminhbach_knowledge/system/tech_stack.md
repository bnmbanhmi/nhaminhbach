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

- **LLM & AI Processing:**
  ### AI & Machine Learning Stack
- **LLM Provider:** Google Vertex AI
- **Model:** Gemini 2.5 Flash Lite (production-grade multilingual)
- **Integration:** google-cloud-aiplatform + Instructor (structured outputs)
- **Authentication:** Service Account via Google Secret Manager
  - **Structured Output:** Instructor library for LLM-to-Pydantic model validation
  - **Data Contracts:** Pydantic v2 models mirroring database schema
  - **Transformation Pipeline:** Cloud Functions with event-driven processing
  - **Secret Management:** Google Secret Manager for API keys and credentials

- **Database:**
  - **Provider:** Google Cloud SQL for **PostgreSQL**.
  - **ORM/Connector:** Use **SQLAlchemy Core** for all database interactions. This is non-negotiable.
  - **Schema:** The database schema is pre-defined and must be respected. The core tables are `listings`, `attributes`, and `listing_attributes`.
  - **Data Flow:** Raw scraped data → LLM transformation → Structured data → Database storage

- **Infrastructure:**
  - **Primary Cloud:** Google Cloud Platform (GCP).
  - **Secret Management:** Google Secret Manager (mandatory for all secrets, API keys, credentials).
  - **Environment Variables:** Only for non-secret configuration (project IDs, regions, etc.).
  - **CI/CD:** Manual deployment via Firebase CLI and gcloud CLI.
  - **Monitoring:** Google Cloud Functions logging and monitoring.