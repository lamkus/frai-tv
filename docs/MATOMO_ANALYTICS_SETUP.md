# Matomo Analytics Setup für FRai.TV (Checkdomain)

> Stand: 2024-12-16 | Hosting: Checkdomain (Shared Hosting)

## Übersicht

Matomo ist eine DSGVO-konforme Analytics-Lösung. Da Checkdomain Shared Hosting ist, nutzen wir die **Matomo Cloud** oder eine **Subdomain Installation**.

---

## Option A: Matomo Cloud (Empfohlen für Shared Hosting)

1. **Account erstellen:** https://matomo.org/start-free-analytics-trial/
2. **Site hinzufügen:** frai.tv als Website
3. **Tracking Code:** Wird automatisch generiert
4. **In .env.production eintragen:**

```env
VITE_MATOMO_URL=https://DEIN_ACCOUNT.matomo.cloud
VITE_MATOMO_SITE_ID=1
```

5. **Rebuild & Deploy:**
```powershell
cd code/frontend
npm run build
./deploy.ps1
```

---

## Option B: Self-Hosted auf Subdomain (stats.frai.tv)

### Voraussetzungen bei Checkdomain:
- Subdomain `stats.frai.tv` anlegen
- PHP 7.4+ aktiviert
- MySQL-Datenbank erstellen

### Installation:

1. **Subdomain erstellen** im Checkdomain Panel
   - Ziel: `stats.frai.tv`
   - Document Root: `/stats` oder eigenes Verzeichnis

2. **Matomo herunterladen:**
   - Download: https://matomo.org/download/
   - Per FTP in das Subdomain-Verzeichnis hochladen
   - Entpacken

3. **Datenbank erstellen:**
   - Checkdomain Panel → Datenbanken → Neue DB
   - Name: `matomo`
   - Notiere: Host, User, Passwort

4. **Web-Installer:**
   - Öffne `https://stats.frai.tv`
   - Folge dem Installer
   - Datenbank-Zugangsdaten eingeben

5. **Frontend konfigurieren:**

```env
# code/frontend/.env.production
VITE_MATOMO_URL=https://stats.frai.tv
VITE_MATOMO_SITE_ID=1
```

6. **Archivierung (Cron):**
   - Checkdomain Panel → Cronjobs
   - Befehl: `php /pfad/zu/matomo/console core:archive`
   - Intervall: Stündlich

---

## Frontend Integration

Die Integration ist bereits vorbereitet in:
- [externalAnalytics.js](../code/frontend/src/lib/externalAnalytics.js)

### Funktionen:
- `initMatomo()` - Initialisiert Tracking
- `trackPageView(path, title)` - Seitenaufruf tracken
- `trackEvent(category, action, name, value)` - Events tracken
- `trackVideoPlay(videoId, title)` - Video-Wiedergabe tracken

### Automatisches Tracking:
- Seitenaufrufe bei Route-Wechsel
- Video-Starts
- Suchen
- Watchlist-Aktionen

---

## Datenschutz

Die Matomo-Integration respektiert:
- ✅ Cookie-Consent (nur mit Zustimmung)
- ✅ DoNotTrack Browser-Einstellung
- ✅ IP-Anonymisierung (letzte 2 Bytes)
- ✅ Keine Daten an Dritte

Siehe auch: [Datenschutzerklärung](https://frai.tv/datenschutz)

---

## Verifizierung

Nach Aktivierung testen:
1. Seite aufrufen
2. In Matomo Dashboard → Echtzeit prüfen
3. Browser Console: Keine Matomo-Fehler

---

## Checkliste

- [ ] Matomo Account/Installation erstellt
- [ ] VITE_MATOMO_URL gesetzt
- [ ] VITE_MATOMO_SITE_ID gesetzt
- [ ] Frontend neu gebaut
- [ ] Deployed
- [ ] Tracking verifiziert
