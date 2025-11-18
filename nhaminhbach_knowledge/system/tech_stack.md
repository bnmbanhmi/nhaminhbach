# Tech Stack
#system

**Always adhere to this tech stack. Do not suggest alternatives unless explicitly asked.**

- **Frontend:**
  - **Framework:** React (using Vite) with TypeScript.
  - **Styling:** Tailwind CSS. Prioritize utility-first classes.
  - **State Management:** For simple cases, use React's built-in hooks (`useState`, `useContext`). For complex global state, use Zustand.
  - **Deployment:** Vercel.

- **Backend:**
  - **Platform:** Vercel Serverless Functions.
  - **Language:** Python 3.11+.
  - **Architecture:** Serverless, stateless functions. Each function is a single, focused microservice in the `packages/api` directory.

- **LLM & AI Processing:**
  ### AI & Machine Learning Stack
- **LLM Provider:** Google Vertex AI
- **Model:** Gemini 2.5 Flash Lite (production-grade multilingual)
- **Integration:** google-cloud-aiplatform + Instructor (structured outputs)
- **Authentication:** Service Account via Google Secret Manager
  - **Structured Output:** Instructor library for LLM-to-Pydantic model validation
  - **Data Contracts:** Pydantic v2 models mirroring database schema
  - **Transformation Pipeline:** (On Hold - To be redesigned for Vercel)
  - **Secret Management:** Vercel Environment Variables (for Supabase keys) and Google Secret Manager (for GCP services).

- **Database:**
  - **Provider:** Supabase (PostgreSQL).
  - **Connector:** Use `supabase-py` for all database interactions.
  - **Schema:** The database schema is pre-defined and must be respected. The core tables are `listings`, `attributes`, and `listing_attributes`.

- **Infrastructure:**
  - **Primary Platform:** Vercel.
  - **Secret Management:** Vercel Environment Variables.
  - **CI/CD:** Vercel's automatic deployments from Git.
  - **Monitoring:** Vercel's built-in logging and monitoring.