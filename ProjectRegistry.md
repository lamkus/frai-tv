# ProjectRegistry.md – Services & Packages

> Übersicht aller Komponenten im remAIke.TV Workspace.

---

## Services

| Service | Path | Status | Owner | Tech Stack | Entry Point | Port |
|---------|------|--------|-------|------------|-------------|------|
| **Backend API** | `code/backend/` | 🟡 MVP | TBD | Node.js 18+, Express, PostgreSQL | `src/index.js` | 4000 |
| **Frontend SPA** | `code/frontend/` | 🟡 MVP | TBD | React 18, Vite 4 | `src/main.jsx` | 5173 (dev) |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Production Ready |
| 🟡 | In Development / MVP |
| 🔴 | Broken / Blocked |
| ⚪ | Planned |

---

## Backend API (`code/backend/`)

### Tech Stack
- **Runtime:** Node.js 18+ (ES Modules)
- **Framework:** Express 4.18
- **Database:** PostgreSQL (pg 8.11)
- **Scheduler:** node-cron 3.0
- **HTTP Client:** axios 1.6

### Scripts
```bash
npm run dev    # Start development server
npm start      # Start production server
```

### API Endpoints (Current)
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/health` | Health check | ✅ |
| GET | `/api/videos` | List videos | ✅ (mock) |
| GET | `/api/videos/:id` | Get video by ID | ✅ (mock) |

### API Endpoints (Planned)
| Method | Endpoint | Description | Task ID |
|--------|----------|-------------|---------|
| GET | `/api/categories` | List categories | T-004 |
| GET | `/api/search` | Search videos | T-005 |
| POST | `/api/admin/login` | Admin login | T-006 |
| POST | `/api/admin/import` | Trigger import | T-002 |

### Configuration
- `.env.example` → Copy to `.env`
- Required: `DATABASE_URL`, `YOUTUBE_API_KEY`
- Optional: `REDIS_URL`, `PORT`

---

## Frontend SPA (`code/frontend/`)

### Tech Stack
- **Framework:** React 18.2
- **Build Tool:** Vite 4.x
- **Styling:** (Planned) Tailwind CSS
- **Routing:** (Planned) React Router

### Scripts
```bash
npm run dev    # Start dev server (HMR)
npm run build  # Production build → dist/
npm run serve  # Preview production build
```

### Pages (Planned)
| Route | Component | Status | Task ID |
|-------|-----------|--------|---------|
| `/` | HomePage | ⚪ Planned | T-008 |
| `/video/:id` | VideoDetail | ⚪ Planned | T-009 |
| `/search` | SearchPage | ⚪ Planned | T-010 |
| `/admin` | AdminPanel | ⚪ Planned | T-011 |
| `/live` | LivestreamPage | ⚪ Planned | T-013 |

### Configuration
- `.env.example` → Copy to `.env`
- `VITE_API_URL` for production API endpoint

---

## Infrastructure

| Component | Technology | Status | Config Location |
|-----------|------------|--------|-----------------|
| **Database** | PostgreSQL 14+ | ⚪ Setup needed | Docker / Strato |
| **Cache** | Redis (optional) | ⚪ Planned | Docker / Strato |
| **Reverse Proxy** | nginx | ✅ Config ready | `installation/nginx.conf` |
| **Process Manager** | PM2 | ✅ Config ready | `code/backend/ecosystem.config.cjs` |
| **Hosting** | Strato VPS + Plesk | ✅ Documented | `installation/strato_deployment.md` |

---

## Documentation

| Document | Path | Description |
|----------|------|-------------|
| Lastenheft | `docs/Lastenheft.md` | Requirements specification |
| Pflichtenheft | `docs/Pflichtenheft.md` | Technical specification |
| Deployment Guide | `installation/strato_deployment.md` | Strato VPS setup |
| Open Source Libs | `docs/OpenSourceLibraries.md` | Library references |
| Citations | `docs/CITATIONS.md` | Source citations |

---

## Dependencies Overview

### Backend
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| express | ^4.18.2 | Web framework | MIT |
| pg | ^8.11.2 | PostgreSQL client | MIT |
| axios | ^1.6.2 | HTTP client | MIT |
| cors | ^2.8.5 | CORS middleware | MIT |
| dotenv | ^16.3.1 | Env vars | BSD-2 |
| node-cron | ^3.0.2 | Scheduler | ISC |

### Frontend
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| react | ^18.2.0 | UI framework | MIT |
| react-dom | ^18.2.0 | React DOM | MIT |
| vite | ^4.0.0 | Build tool | MIT |
| @vitejs/plugin-react | ^3.0.0 | Vite React plugin | MIT |

---

*Last Updated: 2024-12-09 by CrossDomain Orchestrator v3*
