# Strato VPS Deployment Guide for remAIke.TV

Dieses Dokument beschreibt die Bereitstellung (Deployment) der remAIke.TV Streaming-Plattform auf einem Strato VPS mit Plesk.

## Inhaltsverzeichnis

1. [Voraussetzungen](#1-voraussetzungen)
2. [Server-Vorbereitung](#2-server-vorbereitung)
3. [Node.js Installation](#3-nodejs-installation)
4. [PostgreSQL Setup](#4-postgresql-setup)
5. [Backend Deployment](#5-backend-deployment)
6. [Frontend Deployment](#6-frontend-deployment)
7. [Reverse Proxy Konfiguration](#7-reverse-proxy-konfiguration)
8. [SSL/TLS Zertifikat](#8-ssltls-zertifikat)
9. [Prozessmanagement mit PM2](#9-prozessmanagement-mit-pm2)
10. [Fehlerbehebung](#10-fehlerbehebung)

---

## 1. Voraussetzungen

### Strato-Produkt

| Anforderung | Minimum | Empfohlen |
|-------------|---------|-----------|
| Hosting-Typ | **VPS** (kein Shared Webspace!) | V-Server Linux Level 2+ |
| RAM | 2 GB | 4 GB |
| CPU | 1 vCore | 2 vCores |
| Speicher | 20 GB SSD | 40 GB SSD |
| OS | Debian 11 / Ubuntu 20.04 | Debian 12 / Ubuntu 22.04 |

> ⚠️ **Wichtig**: Node.js läuft **nicht** auf Strato Shared-Webspace! Nur VPS oder dedizierte Server unterstützen dauerhafte Node-Prozesse.

### Software-Anforderungen

- Node.js 18.x LTS (oder 16.x bei älterem glibc)
- PostgreSQL 14+
- PM2 (Prozessmanager)
- nginx (als Reverse Proxy, via Plesk)

---

## 2. Server-Vorbereitung

### 2.1 SSH-Zugang einrichten

```bash
# Verbindung zum Server
ssh root@your-server-ip

# System aktualisieren
apt update && apt upgrade -y
```

### 2.2 Logs-Verzeichnis erstellen

```bash
mkdir -p /var/www/remaike/code/backend/logs
```

### 2.3 Firewall konfigurieren

```bash
# UFW aktivieren (falls nicht vorhanden)
apt install ufw -y
ufw allow ssh
ufw allow http
ufw allow https
ufw enable
```

---

## 3. Node.js Installation

### Option A: Installation via nvm (Empfohlen)

nvm erlaubt die Verwaltung mehrerer Node-Versionen und umgeht glibc-Probleme.

```bash
# nvm installieren
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Shell neu laden
source ~/.bashrc

# Node.js 18 LTS installieren
nvm install 18

# Als Standard setzen
nvm alias default 18

# Verifizieren
node --version  # v18.x.x
npm --version
```

### Option B: Installation via apt

```bash
# NodeSource Repository hinzufügen
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Node.js installieren
apt install nodejs -y

# Verifizieren
node --version
npm --version
```

### Bekanntes Problem: glibc-Fehler

Falls Sie folgenden Fehler sehen:
```
node: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.28' not found
```

**Lösung**: Verwenden Sie Node.js 16.x:
```bash
nvm install 16.20.2
nvm use 16.20.2
nvm alias default 16.20.2
```

---

## 4. PostgreSQL Setup

### 4.1 Installation

```bash
# PostgreSQL installieren
apt install postgresql postgresql-contrib -y

# Service starten
systemctl start postgresql
systemctl enable postgresql
```

### 4.2 Datenbank erstellen

```bash
# Als postgres-User einloggen
sudo -u postgres psql

# In der PostgreSQL-Shell:
CREATE USER remaike WITH PASSWORD 'your_secure_password';
CREATE DATABASE remaike_db OWNER remaike;
GRANT ALL PRIVILEGES ON DATABASE remaike_db TO remaike;
\q
```

### 4.3 Connection String

Notieren Sie sich den Connection String für die `.env` Datei:
```
DATABASE_URL=postgres://remaike:your_secure_password@localhost:5432/remaike_db
```

---

## 5. Backend Deployment

### 5.1 Projektstruktur auf dem Server

```
/var/www/remaike/
├── code/
│   ├── backend/           # Node.js Backend
│   │   ├── src/
│   │   ├── package.json
│   │   ├── ecosystem.config.cjs
│   │   ├── start.js
│   │   ├── .env           # Produktions-Umgebungsvariablen
│   │   └── logs/
│   └── frontend/
│       └── dist/          # Gebaute Frontend-Dateien
└── httpdocs/              # Symlink oder Kopie von frontend/dist
```

### 5.2 Dateien hochladen

**Via SFTP:**
```
Host: ftp.strato.com (oder Ihre Server-IP)
User: Ihre Domain oder root
Port: 22 (SFTP) oder 21 (FTP)
```

**Via Git (empfohlen):**
```bash
cd /var/www
git clone https://github.com/your-username/remAIke.TV.git remaike
cd remaike
```

### 5.3 Backend konfigurieren

```bash
cd /var/www/remaike/code/backend

# Abhängigkeiten installieren
npm install --production

# Umgebungsvariablen einrichten
cp .env.example .env
nano .env
```

**.env Datei anpassen:**
```dotenv
NODE_ENV=production
PORT=4000
DATABASE_URL=postgres://remaike:your_secure_password@localhost:5432/remaike_db
YOUTUBE_API_KEY=your_youtube_api_key
```

### 5.4 Backend testen

```bash
# Manueller Start zum Testen
node start.js

# Sollte ausgeben:
# [start.js] Starting remAIke.TV Backend...
# Backend server listening on port 4000
```

---

## 6. Frontend Deployment

### 6.1 Lokal bauen (empfohlen)

Auf Ihrer Entwicklungsmaschine:

```bash
cd code/frontend

# Produktions-Build erstellen
npm run build

# Ergebnis: dist/ Ordner mit statischen Dateien
```

### 6.2 Auf Server bauen

```bash
cd /var/www/remaike/code/frontend

# Abhängigkeiten installieren
npm install

# Produktions-Build
npm run build
```

### 6.3 Frontend-Dateien bereitstellen

```bash
# Symlink zu httpdocs erstellen (Plesk-Standard)
ln -s /var/www/remaike/code/frontend/dist /var/www/vhosts/your-domain.de/httpdocs

# ODER: Dateien kopieren
cp -r /var/www/remaike/code/frontend/dist/* /var/www/vhosts/your-domain.de/httpdocs/
```

---

## 7. Reverse Proxy Konfiguration

### 7.1 Via Plesk (GUI)

1. Einloggen in Plesk
2. **Websites & Domains** → Ihre Domain auswählen
3. **Apache & nginx Einstellungen** öffnen
4. Bei **Zusätzliche nginx-Anweisungen** einfügen:

```nginx
# API Reverse Proxy zu Node.js Backend
location /api/ {
    proxy_pass http://127.0.0.1:4000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    proxy_read_timeout 86400;
}

# SPA Fallback für React Router
location / {
    try_files $uri $uri/ /index.html;
}
```

5. **OK** klicken und Änderungen übernehmen

### 7.2 Vollständige nginx.conf (falls manuell)

Erstellen Sie `/etc/nginx/sites-available/remaike.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.de www.your-domain.de;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.de www.your-domain.de;
    
    # SSL Zertifikate (Let's Encrypt via Plesk)
    ssl_certificate /etc/letsencrypt/live/your-domain.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.de/privkey.pem;
    
    # Frontend Static Files
    root /var/www/remaike/code/frontend/dist;
    index index.html;
    
    # Gzip Kompression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # SPA Routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Static Asset Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Aktivieren:
```bash
ln -s /etc/nginx/sites-available/remaike.conf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## 8. SSL/TLS Zertifikat

### Via Plesk (Let's Encrypt)

1. **Websites & Domains** → Ihre Domain
2. **SSL/TLS-Zertifikate** → **Let's Encrypt**
3. E-Mail-Adresse eingeben
4. **Installieren** klicken
5. **HTTPS umleiten** aktivieren

### Via Certbot (manuell)

```bash
# Certbot installieren
apt install certbot python3-certbot-nginx -y

# Zertifikat anfordern
certbot --nginx -d your-domain.de -d www.your-domain.de

# Auto-Renewal testen
certbot renew --dry-run
```

---

## 9. Prozessmanagement mit PM2

### 9.1 PM2 installieren

```bash
npm install -g pm2
```

### 9.2 Backend mit PM2 starten

```bash
cd /var/www/remaike/code/backend

# Mit ecosystem.config.cjs starten
pm2 start ecosystem.config.cjs --env production

# Status prüfen
pm2 status

# Logs anzeigen
pm2 logs remaike-backend
```

### 9.3 Autostart bei Systemstart

```bash
# Startup-Script generieren
pm2 startup systemd

# Den ausgegebenen Befehl ausführen (als root)
# Beispiel: sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u root --hp /root

# Aktuelle Prozesse speichern
pm2 save
```

### 9.4 Nützliche PM2-Befehle

```bash
pm2 restart remaike-backend    # Neustart
pm2 stop remaike-backend       # Stoppen
pm2 delete remaike-backend     # Entfernen
pm2 monit                      # Echtzeit-Monitor
pm2 logs --lines 100           # Letzte 100 Log-Zeilen
```

---

## Optional: Matomo On-Premise (Privacy-first analytics)

If you want to run first-party analytics, Matomo is recommended. The steps below assume you have a subdomain such as `stats.YOUR_DOMAIN.de` pointing to the server.

### Matomo quick installation steps
1. Create a site/subdomain `stats.YOUR_DOMAIN.de` in Plesk and use `/var/www/matomo` as the document root.
2. Ensure PHP + required extensions are installed (mbstring, json, pdo_mysql, curl, gd, zip, openssl).
3. Create a MySQL database + user (example):
    ```bash
    sudo -u postgres psql
    CREATE DATABASE matomo;
    CREATE USER matomo WITH PASSWORD 'your_secure_password';
    GRANT ALL PRIVILEGES ON DATABASE matomo TO matomo;
    \q
    ```
4. Download Matomo and extract to `/var/www/matomo`:
    ```bash
    cd /tmp
    wget https://builds.matomo.org/matomo.zip
    unzip matomo.zip
    sudo mv matomo /var/www/matomo
    sudo chown -R www-data:www-data /var/www/matomo
    ```
5. Configure the vhost in Plesk (or place manual nginx config), enable php-fpm for the site and request an SSL certificate.
6. Run the Matomo installer at `https://stats.YOUR_DOMAIN.de` and provide DB credentials.
7. Optional (recommended): Set up archiving cron (hourly):
    ```bash
    crontab -e
    # run hourly archiving
    0 * * * * /usr/bin/php /var/www/matomo/console core:archive --url=https://stats.YOUR_DOMAIN.de > /dev/null 2>&1
    ```

### Integrate Matomo with the frontend
1. Add the environment variables in `code/frontend/.env.production`:
    ```env
    VITE_MATOMO_URL=https://stats.YOUR_DOMAIN.de
    VITE_MATOMO_SITE_ID=1
    ```
2. Rebuild the frontend and redeploy.
3. You can keep AWStats/Webalizer enabled for log verification, but Matomo provides richer session & event analytics.

### Limitations
- Matomo will track player events forwarded by the frontend (Start/Progress/Complete) but does not replace YouTube Studio watch metrics. For absolute watch time, check YouTube Studio as well.


---

## 10. Fehlerbehebung

### Problem: App startet nicht (DefaultTasksMax)

**Symptom**: Node.js App startet nicht, systemd meldet Ressourcenlimit.

**Lösung**:
```bash
# /etc/systemd/system.conf bearbeiten
nano /etc/systemd/system.conf

# Zeile ändern oder hinzufügen:
DefaultTasksMax=300

# Systemd neu laden
systemctl daemon-reload
```

### Problem: 502 Bad Gateway

**Ursachen & Lösungen**:

1. Backend läuft nicht:
   ```bash
   pm2 status
   pm2 restart remaike-backend
   ```

2. Falscher Port in nginx:
   ```bash
   # Prüfen welchen Port das Backend nutzt
   pm2 logs remaike-backend | grep "listening on port"
   ```

3. Firewall blockiert:
   ```bash
   # Lokale Verbindung testen
   curl http://127.0.0.1:4000/api/health
   ```

### Problem: CORS-Fehler

Wenn das Frontend Fehler wie `Access-Control-Allow-Origin` meldet:

```javascript
// In src/index.js, CORS-Optionen anpassen:
app.use(cors({
  origin: ['https://your-domain.de', 'https://www.your-domain.de'],
  credentials: true
}));
```

### Problem: Datenbank-Verbindungsfehler

```bash
# PostgreSQL Status prüfen
systemctl status postgresql

# Verbindung testen
psql -U remaike -h localhost -d remaike_db

# Logs prüfen
tail -f /var/log/postgresql/postgresql-14-main.log
```

### Problem: Node.js Version inkompatibel

```bash
# Aktuelle Version prüfen
node --version

# Mit nvm wechseln
nvm install 16.20.2
nvm use 16.20.2

# PM2 mit neuer Version neu starten
pm2 kill
pm2 start ecosystem.config.cjs --env production
```

---

## Checkliste für Produktiv-Deployment

- [ ] VPS bei Strato gebucht (kein Shared Webspace)
- [ ] SSH-Zugang funktioniert
- [ ] Node.js 18.x (oder 16.x) installiert
- [ ] PostgreSQL installiert und Datenbank erstellt
- [ ] Backend-Code hochgeladen
- [ ] `.env` mit Produktionswerten konfiguriert
- [ ] Frontend gebaut und hochgeladen
- [ ] nginx Reverse Proxy konfiguriert
- [ ] SSL-Zertifikat installiert
- [ ] PM2 konfiguriert und Autostart aktiviert
- [ ] Health-Check funktioniert: `https://your-domain.de/api/health`
- [ ] Frontend erreichbar: `https://your-domain.de`

---

## Referenzen

- [Strato Node.js Tutorial](https://www.strato.nl/faq/hosting/hoe-installeer-ik-nodejs/)
- [Plesk Node.js Documentation](https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/nodejs-support.html)
- [PM2 Process Manager](https://pm2.keymetrics.io/docs/usage/quick-start/)
- [Let's Encrypt via Plesk](https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/ssl-tls-certificates.html)
