# Product Roadmap
#core

### **The Battle-Tested Roadmap V2**

*This is our pragmatic, battle-tested plan. It prioritizes the creation of our core asset—clean, structured data—and the delivery of tangible user value at each stage. It is a living document, subject to change based on data and user feedback.*

---

### **Phase 1: Foundation & Data Factory**
-   **Theme:** Infrastructure & Asset Creation
-   **Objective:** To build a robust, scalable technical foundation and a semi-automated data acquisition pipeline, creating the company's core asset (clean data) before any public launch.
-   **Status:** **`DONE`**
-   **Associated Epic:** [[E1]] Foundation & Data Factory
-   **Key Outcomes:**
    -   A fully provisioned and secured GCP infrastructure.
    -   A complete set of backend APIs for managing listings and attributes.
    -   A powerful, local-first scraper for raw data acquisition.
    -   An intelligent internal QC Cockpit for data enrichment and approval.
    -   A secure Local-to-Cloud ingestion bridge.

---

### **Phase 2: Public MVP - The Cleanest Source of Truth**
-   **Theme:** Activation & Core Value Validation
-   **Objective:** To launch the first public version of the product, validating our core value proposition of saving users time and reducing risk through superior data quality.
-   **Status:** **`IN PROGRESS`**
-   **Associated Epic:** [[E2]] Public MVP - The Cleanest Source of Truth
-   **Key Features:**
    -   `[[✅ Done]]` Public List & Detail View UI
    -   `[[🎯 To Do]]` Minimalist Filtering System (District, Price Range, Key Amenities).
    -   `[[🎯 To Do]]` Source Post Link on the UI.
    -   `[[🎯 To Do]]` Full Responsive Design for mobile and desktop.
-   **Strategic Deferrals (Won't Build):**
    -   User Accounts (Login/Registration)
    -   Comments & Social Features
    -   AI Chatbots
    -   Direct Listing Submissions

---

### **Phase 3: Experience & Trust Optimization**
-   **Theme:** Retention & Trust Building
-   **Objective:** To evolve the product from a simple utility into an indispensable tool by enhancing its usability and building foundational layers of community trust, driven by early user feedback from the MVP.
-   **Status:** **`PLANNED`**
-   **Associated Epic:** [[E3]] Experience & Trust Optimization
-   **Potential Features (Prioritized):**
    1.  Performance Optimization (especially image loading).
    2.  Advanced Filtering & Keyword Search.
    3.  Community Reporting Feature ("Inaccurate" / "Rented" button).
    4.  Brand & Transparency Pages ("About Us", "Contact").
    5.  Local Storage Favorites (no account required).

---

### **Phase 4: The Future - The Trusted Transaction Platform**
-   **Theme:** Monetization & Platform Expansion
-   **Objective:** To transition from a pure information source to a trusted ecosystem where users can confidently make decisions and initiate transactions, solidifying our market leadership in reliability.
-   **Status:** **`PLANNED`**
-   **Associated Epic:** [[E4]] The Trusted Transaction Platform
-   **Potential Features:**
    1.  **Trust System:**
        -   "Verified Landlord" badges and verification process.
        -   Post-interaction review system.
    2.  **AI-Powered QC:**
        -   Train models on our QC data to automate classification, tagging, and entity extraction.
        -   *Alex's Note: The goal of AI here is not to replace the founder, but to act as a QC Assistant, handling 80% of the easy cases so you can focus on the 20% that require human judgment.*
    3.  **Direct Landlord Posting:**
        -   Open a high-quality ingestion channel for verified landlords to reduce dependency on scraping.
    4.  **Value-Added Services:**
        -   Standardized rental contracts, legal checks, professional photography services.