# RUNBOOK – remAIke.TV

> Kurzleitfaden für Entwicklung, Build, Test, Release und Incident Response.

---

## 🚨 SOFORT-FIX: DNS ÄNDERN!

**Problem:** `frai.tv` zeigt auf toten Server (88.99.101.251). Muss auf Strato zeigen!

### DNS bei Strato ändern:
1. Login: https://www.strato.de/apps/CustomerService
2. Domains → frai.tv → DNS-Einstellungen
3. Ändere die A-Records:

| Typ | Host | Wert (ALT) | Wert (NEU) |
|-----|------|------------|------------|
| A | @ | 88.99.101.251 | **81.169.145.180** |
| A | www | 88.99.101.251 | **81.169.145.180** |

4. Speichern → Warten (5-30 Min)

---

## 🚀 Backend auf Render.com deployen

1. Gehe zu https://render.com → Sign up mit GitHub
2. New → Web Service → Connect Repo `remaike.TV`
3. Root Directory: `code/backend`
4. Build: `npm install` | Start: `npm start`
5. Env Vars: `YOUTUBE_API_KEY=AIzaSyBbM2BQflcIsduF9cioo79TDd7SZ5F83m8`
6. Deploy → URL kopieren (z.B. `https://frai-tv-backend.onrender.com`)
7. Falls URL anders: `code/frontend/.env.production` anpassen und neu deployen!

---

## 1. Quickstart (Entwicklung)

### Prerequisites
- Node.js 18+ (via nvm empfohlen)
- PostgreSQL 14+
- Git

### Backend starten
```bash
cd code/backend
cp .env.example .env  # Anpassen!
npm install
npm run dev
# → http://localhost:4000/api/health
```

### Frontend starten
```bash
cd code/frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## 2. Build

### Frontend Production Build
```bash
cd code/frontend
npm run build
# Output: dist/
```

### Backend (kein separater Build nötig)
ES Modules werden direkt ausgeführt.

---

## 3. Test

### Backend Tests
```bash
cd code/backend
npm test              # Unit Tests
npm run test:e2e      # E2E Tests (wenn konfiguriert)
```

### Frontend Tests
```bash
cd code/frontend
npm test              # Vitest/Jest
npm run test:coverage # Coverage Report
```

### Lint / Format
```bash
npm run lint          # ESLint
npm run format        # Prettier
```

---

## 4. Release

1. **Version bumpen**: `npm version patch|minor|major`
2. **Changelog**: `CHANGELOG.md` aktualisieren
3. **Tests**: Alle Tests grün
4. **Build**: Frontend bauen
5. **Tag**: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
6. **Push**: `git push origin main --tags`
7. **Deploy**: Siehe `installation/strato_deployment.md`

---

## 5. Incident Playbook

### P1: Service Down
1. Check PM2 Status: `pm2 status`
2. Check Logs: `pm2 logs remaike-backend --lines 100`
3. Restart: `pm2 restart remaike-backend`
4. Check DB: `systemctl status postgresql`
5. Check nginx: `systemctl status nginx`

### P2: Performance Degradation
1. Check Memory: `htop` / `pm2 monit`
2. Check DB Connections: `SELECT count(*) FROM pg_stat_activity;`
3. Check Redis (wenn aktiv): `redis-cli ping`

### P3: API Errors
1. Review Logs: `pm2 logs remaike-backend`
2. Check Health: `curl http://localhost:4000/api/health`
3. Check ENV vars: `.env` Datei prüfen

---

## 6. Contacts

| Role | Contact |
|------|---------|
| Project Lead | TBD |
| DevOps | TBD |
| On-Call | TBD |

---

## 7. Links

- [Strato Deployment Guide](installation/strato_deployment.md)
- [Pflichtenheft](docs/Pflichtenheft.md)
- [Lastenheft](docs/Lastenheft.md)
- [TODO Manifest](TODO_MANIFEST.md)

---

## Quick deploy checklist for analytics

1. If using Matomo, ensure env vars are set in the frontend build environment:
	- `VITE_MATOMO_URL=https://stats.YOUR_DOMAIN.de`
	- `VITE_MATOMO_SITE_ID=1`
2. If using GTM for YouTube triggers, set `VITE_GTM_ID` accordingly and ensure GTM scripts are added to Plesk/nginx if necessary.
3. Rebuild the frontend: `npm run build` and deploy the `dist/` folder.
4. Confirm the GDPR consent modal in the UI (decline / accept paths) — analytics should only run after accept.
5. Spot-check Admin Analytics dashboard for local events and confirm Matomo receives events when active.


---

## Matomo Health Checks (if installed)

1. **Site reachable**
	```bash
	curl -I https://stats.YOUR_DOMAIN.de
	```
	-> Should return HTTP 200/301/302 depending on configuration.

2. **Manual archiving test**
	```bash
	php /var/www/matomo/console core:archive --url=https://stats.YOUR_DOMAIN.de
	```
	-> Should complete without errors. Cron should run this hourly for production.

3. **DB connection**
	```bash
	mysql -u matomo -p -e "show databases;"
	```
	-> `matomo` database should be listed and accessible.

4. **Log inspection**
	```bash
	tail -n 200 /var/www/matomo/tmp/logs/*
	```
	-> Look for errors or permission problems.

