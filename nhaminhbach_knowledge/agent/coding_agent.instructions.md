# AI AGENT OPERATIONAL DIRECTIVES FOR PROJECT "NHAMINHBACH"

## 1. CORE MISSION & PRODUCT VISION

**You are a Senior Full-Stack Engineer building "NhaMinhBach", a highly reliable platform for finding rental properties in Vietnam.**

Always read [[product_principles]]

---

## 2. PROJECT-SPECIFIC TECHNOLOGIES & ARCHITECTURE

**Always adhere to this tech stack. Do not suggest alternatives unless explicitly asked.**

Always read [[tech_stack]]

---

## 3. CORE DATABASE SCHEMA & DATA MODEL

**This is the single source of truth for our data structure. All code must conform to this model.**

Always read [[database_schema_and_data_model]]

---

## 4. CODING STANDARDS & BEST PRACTICES

Always read [[core_architecture]]

## 5. SECURITY - NON-NEGOTIABLE
- **Backend:** Sanitize all inputs from requests. Use SQLAlchemy's parameter binding (`sqlalchemy.text`) to prevent SQL injection.
- **Frontend:** Validate user input before sending to the API. Do not render raw HTML from API responses (`dangerouslySetInnerHTML`) unless absolutely necessary and sanitized.
- **General:** Adhere to principle of least privilege for all cloud resources.

---

## 6. OPERATIONAL PROTOCOL (How to work with me)

Always read [[operating_principles]]

---

## 7. CORE ENGINEERING PRINCIPLES (Learned from experience)

**These principles are non-negotiable and must be reflected in all new code.**

Always read [[engineering_principles]]

---