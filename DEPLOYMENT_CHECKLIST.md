# 🚀 FRai.TV DEPLOYMENT CHECKLIST

> Stand: 2. Januar 2026 | Status: **API BROKEN**

---

## 📊 AKTUELLER STATUS

| Komponente | URL | Status |
|------------|-----|--------|
| Frontend | https://frai.tv | ✅ Online (200 OK) |
| SSL | Let's Encrypt | ✅ Gültig |
| DNS | 185.3.235.231 | ✅ Korrekt |
| API /api/videos | https://frai.tv/api/videos | ❌ Returns HTML |
| API /api/health | https://frai.tv/api/health | ❌ Returns HTML |
| Backend (PHP) | /api/index.php | ❌ Nicht geroutet |

**Root Cause:** `.htaccess` SPA Fallback fängt `/api/*` ab, bevor PHP erreicht wird.

---

## 🔧 FIX-OPTIONEN

### Option A: .htaccess Fix (EMPFOHLEN)

**Problem:** SPA Fallback leitet auch API-Requests um.

**Lösung:** `.htaccess` im Document Root anpassen:

```apache
# API Requests NICHT umleiten
RewriteEngine On
RewriteBase /

# API Requests direkt an PHP
RewriteCond %{REQUEST_URI} ^/api/
RewriteRule ^api/(.*)$ /api/index.php [L,QSA]

# SPA Fallback für alle anderen Requests (außer existierende Dateien)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/
RewriteRule . /index.html [L]
```

**Deploy-Schritte:**
1. SSH: `ssh rnhszswb@host254.checkdomain.de`
2. `cd ~/frai.tv/` (oder Document Root)
3. `nano .htaccess`
4. Obigen Code einfügen
5. Testen: `curl https://frai.tv/api/health`

---

### Option B: Render.com Backend (Fallback)

Falls PHP nicht funktioniert:

1. https://render.com → New Web Service
2. Repo: `remaike.TV`, Root: `code/backend`
3. Build: `npm install`, Start: `npm start`
4. Environment Variables:
   ```
   YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
   PORT=10000
   ```
5. Frontend `.env.production` anpassen:
   ```
   VITE_API_URL=https://frai-tv-backend.onrender.com
   ```
6. Frontend neu builden und deployen

---

## 📦 FULL DEPLOYMENT PROCEDURE

### Pre-Flight Checks
- [ ] Git Status clean (`git status`)
- [ ] Keine offenen Errors (`npm run lint`)
- [ ] Build erfolgreich (`npm run build`)
- [ ] Credentials vorhanden (`.checkdomain_cred.xml`)

### Phase 1: Backend Fix
- [ ] .htaccess auf Server prüfen
- [ ] API-Routing korrigieren
- [ ] `/api/health` testen → muss JSON zurückgeben
- [ ] `/api/videos` testen → muss Video-Liste zurückgeben

### Phase 2: Frontend Deploy
- [ ] `cd code/frontend`
- [ ] `.env.production` prüfen
- [ ] `npm run build`
- [ ] `.\deploy.ps1` oder `.\deploy-full.ps1`

### Phase 3: Verification
- [ ] https://frai.tv → Lädt
- [ ] Videos werden angezeigt
- [ ] Player funktioniert
- [ ] Mobile Test (iOS Safari, Android Chrome)

### Phase 4: Post-Deploy
- [ ] Cache invalidieren (CloudFlare falls aktiv)
- [ ] Smoke Tests durchführen
- [ ] Analytics prüfen

---

## 🛠️ QUICK COMMANDS

```powershell
# Full Deploy (Frontend + Backend)
.\deploy-full.ps1

# Nur Frontend
cd code/frontend
.\deploy.ps1

# Build ohne Deploy
cd code/frontend
npm run build

# Lokaler Dev Server
cd code/frontend
npm run dev

# Backend lokal
cd code/backend
npm run dev
```

---

## 🔐 CREDENTIALS

**SFTP/SSH:**
- Host: `host254.checkdomain.de`
- User: `rnhszswb`
- Password: Gespeichert in `~/.checkdomain_cred.xml`

**YouTube API:**
- Key: `YOUR_YOUTUBE_API_KEY`
- Channel: `@remAIke_IT` (UCVFv6Egpl0LDvigpFbQXNeQ)

---

## 📁 SERVER STRUKTUR (Checkdomain)

```
/frai.tv/                    # Document Root
├── index.html               # SPA Entry
├── assets/                  # Vite Build Output
├── .htaccess                # Routing Rules ← FIX HERE
├── api/                     # PHP Backend
│   ├── index.php            # API Router
│   ├── analytics.php        # Tracking
│   └── .htaccess            # API-spezifische Rules
└── data/
    └── videos.json          # Cached Video Data
```

---

## 🚨 EMERGENCY PROCEDURES

### Site Down?
1. Check: `Test-NetConnection frai.tv -Port 443`
2. SSH Login: `ssh rnhszswb@host254.checkdomain.de`
3. Logs: `tail -f ~/logs/error.log`

### API Broken?
1. Direct Test: `curl https://frai.tv/api/index.php`
2. Check .htaccess
3. PHP Error Log: `tail -f ~/logs/php_error.log`

### SSL Issues?
1. Let's Encrypt auto-renew via Checkdomain Panel
2. Check: `openssl s_client -connect frai.tv:443`

---

## 📈 NEXT STEPS

1. **SOFORT:** .htaccess API-Routing fixen
2. **DANN:** Videos.json mit YouTube API befüllen
3. **OPTIONAL:** Matomo Analytics installieren
4. **FUTURE:** CDN (CloudFlare) für Performance
