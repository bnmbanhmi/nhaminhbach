# Local Demo Setup Guide
**NhaMinhBach.com - Rental Platform Demo**

## ✅ Setup Complete!

Your local demo is now running:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8080
- **API Docs:** http://localhost:8080/

## Quick Reference

### Current Running Services

```
✓ Backend Server (Flask)
  - Port: 8080
  - Status: Running in demo mode with mock data
  - Terminal ID: c2a596b4-0c29-4016-ab6e-c1b00803be15

✓ Frontend Server (Vite)
  - Port: 5173
  - Status: Running with hot reload
  - Terminal ID: 2ed8083c-c60c-44f4-bbbe-9041c6b7e0d0
```

### Stop Servers

Press `Ctrl+C` in each terminal where servers are running.

### Step 1: Install Frontend Dependencies
```bash
cd /Users/mac/nhaminhbach.com/nhaminhbach/packages/web
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

The app will be available at: **http://localhost:5173**

---

## What You'll See

### 🏠 Public Features
1. **Homepage** - Landing page with rental listings
2. **Search & Filter** - Filter by district, price range, and amenities
3. **Listing Details** - View detailed information about each property
4. **Responsive Design** - Works on mobile and desktop

### ⚙️ Admin Features (QC Cockpit)
- **Dashboard** - Review pending listings
- **Side-by-Side Review** - Compare raw vs structured data
- **Approve/Reject** - Quality control workflow

---

## Architecture Overview

```
┌─────────────────┐
│   Web Frontend  │  ← React + Vite + TypeScript + Tailwind
│  (localhost:5173)│
└────────┬────────┘
         │ API Calls
         ↓
┌─────────────────┐
│ Cloud Functions │  ← Python Backend (GCP)
│   (Production)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Cloud SQL DB   │  ← PostgreSQL (GCP)
│   (Production)  │
└─────────────────┘
```

**Note:** Frontend runs locally, but connects to production backend APIs for data.

---

## Available Commands

### Frontend (packages/web)
```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
npm run test     # Run tests
```

### Backend (packages/functions) - For Reference Only
```bash
# Backend is deployed on GCP Cloud Functions
# Local backend development requires:
cd /Users/mac/nhaminhbach.com/nhaminhbach/packages/functions
source .venv/bin/activate
pip install -r requirements.txt

# Then configure GCP credentials and Cloud SQL connection
```

---

## Configuration

### Frontend Environment
The frontend is configured to connect to production APIs via `packages/web/src/config.ts`:
- **API Base URL:** `https://asia-southeast1-omega-sorter-467514-q6.cloudfunctions.net`
- **CORS:** Enabled for localhost development

### No Local .env Required
All secrets are managed via Google Secret Manager. Frontend only needs the public API endpoints.

---

## Troubleshooting

### Port Already in Use
If port 5173 is busy:
```bash
# Kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or change port in vite.config.ts
```

### API Connection Issues
- Check internet connection (backend is cloud-hosted)
- Verify CORS settings in backend
- Check browser console for detailed errors

### Missing Dependencies
```bash
cd /Users/mac/nhaminhbach.com/nhaminhbach/packages/web
rm -rf node_modules package-lock.json
npm install
```

---

## Project Structure

```
packages/web/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route pages (Home, Details, Admin)
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript interfaces
│   ├── utils/          # Helper functions
│   ├── config.ts       # API configuration
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── package.json        # Dependencies
└── vite.config.ts      # Vite configuration
```

---

## Next Steps After Demo

1. **Explore the UI** - Browse listings, test filters
2. **Check Mobile View** - Resize browser or use mobile device
3. **Admin Cockpit** - Navigate to `/admin` for QC interface
4. **Read Documentation** - Check `/nhaminhbach_knowledge/` for architecture docs

---

## Tech Stack
- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS
- **Backend:** Python Cloud Functions + Flask
- **Database:** PostgreSQL (Cloud SQL)
- **LLM:** Google Vertex AI (Gemini 2.5 Flash Lite)
- **Infrastructure:** Google Cloud Platform

---

## Support
For issues or questions, check:
- `CONTRIBUTING.md` - Development guidelines
- `nhaminhbach_knowledge/system/` - Architecture documentation
- `nhaminhbach_knowledge/strategy/` - Product roadmap
