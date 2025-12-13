# Installationsanleitung

Diese Anleitung beschreibt die Einrichtung der Entwicklungsumgebung und
erläutert, wie das Projekt gestartet wird. Für alle Schritte wird
vorausgesetzt, dass ein aktuelles Betriebssystem (Linux, macOS oder
Windows mit WSL) vorhanden ist und dass grundlegende Befehle in der
Shell ausgeführt werden können.

## 1  Vorbereitungen

1. **Node.js installieren**: Es wird Node.js in Version 18 oder höher
   benötigt. Download von <https://nodejs.org>. Empfohlen wird die
   Installation mittels nvm (Node Version Manager).
2. **Git installieren:** Zum Klonen des Repositories und zur
   Versionsverwaltung (<https://git-scm.com/>).
3. **Datenbank und Cache:**
   - PostgreSQL (z. B. über Docker oder Paketmanager)
   - Redis (optional; über Docker oder Paketmanager)
4. **Docker (optional):** Für einen einfachen Entwicklungsstart kann
   Docker und docker‑compose verwendet werden. Installationsanleitung
   unter <https://docs.docker.com/get-docker/>.

## 2  Repository klonen

Öffnen Sie eine Konsole und führen Sie folgende Befehle aus:

```bash
git clone <REPOSITORY_URL> coding_team_workspace_project
cd coding_team_workspace_project/code
```

*(Hinweis: Ersetzen Sie `<REPOSITORY_URL>` durch die tatsächliche
Git‑Repository‑URL.)*

## 3  Backend einrichten

1. Wechseln Sie in das Backend‑Verzeichnis:

   ```bash
   cd backend
   ```

2. Installieren Sie Abhängigkeiten:

   ```bash
   npm install
   ```

3. Kopieren Sie die Umgebungsvariablen:

   ```bash
   cp .env.example .env
   ```
   Öffnen Sie `.env` und tragen Sie:
   - Ihre YouTube Data API‑Schlüssel ein.
   - Die Zugangsdaten für PostgreSQL.
   - Einen geheimen Schlüssel für JWT (bei Nutzung von Auth).

4. Datenbank vorbereiten:
   - Erstellen Sie eine Datenbank (z. B. `streaming_db`).
   - Führen Sie ggf. Migrationen aus (bei Nutzung von Prisma oder TypeORM).

5. Starten Sie den Backend‑Server im Entwicklungsmodus:

   ```bash
   npm run dev
   ```

   Der Server läuft standardmäßig auf Port 4000. Über `http://localhost:4000/api/videos` sollten Sie eine leere JSON‑Antwort erhalten.

## 4  Frontend einrichten

1. Wechseln Sie in das Frontend‑Verzeichnis:

   ```bash
   cd ../frontend
   ```

2. Installieren Sie Abhängigkeiten:

   ```bash
   npm install
   ```

3. Starten Sie das Frontend im Entwicklungsmodus:

   ```bash
   npm run dev
   ```

   Standardmäßig wird das Frontend auf Port 5173 gestartet. Rufen Sie im
   Browser `http://localhost:5173` auf. Die Seite sollte eine Liste der
   Videos anzeigen (aktuell mit Platzhalterdaten).

      Optional: Um die Google "Sign in" Funktion zu aktivieren, legen Sie `VITE_GOOGLE_CLIENT_ID` in `code/frontend/.env` fest (siehe `code/frontend/.env.example`).

## 5  Docker Compose (optional)

Zur Vereinfachung kann eine `docker-compose.yml` erstellt werden, die
Datenbank, Redis, Backend und Frontend gemeinsam startet. Ein Beispiel
könnte so aussehen:

```yaml
version: '3'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: streaming_db
      POSTGRES_USER: streaming_user
      POSTGRES_PASSWORD: streaming_pass
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgres://streaming_user:streaming_pass@db:5432/streaming_db
      YOUTUBE_API_KEY: <your_key>
    depends_on:
      - db
      - redis
    ports:
      - "4000:4000"

  frontend:
    build: ./frontend
    environment:
      VITE_API_URL: http://localhost:4000
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

Zum Starten aller Services:

```bash
docker-compose up --build
```

Die Container können anschließend mit `docker-compose down` wieder
gestoppt werden.

## 6  Cron‑Jobs für automatische Updates

Im Backend befindet sich ein Skript, das täglich neue Videos vom
YouTube‑Kanal abruft und in die Datenbank importiert. Dieser Cron kann
über `node-cron` oder über einen System‑Cron eingerichtet werden.
Ein Beispiel für `node-cron`:

```js
const cron = require('node-cron');
const { importVideos } = require('./services/videoService');

// täglich um 3:00 Uhr
cron.schedule('0 3 * * *', async () => {
  await importVideos();
});
```

## 7  Nächste Schritte

- Implementieren Sie die noch ausstehenden Module gemäß Pflichtenheft.
- Passen Sie das Theme‑System an die gewünschten Designs an.
- Richten Sie einen Consent‑Banner ein, bevor der YouTube‑Player
  geladen wird.
- Fügen Sie Tests und weitere Dokumentation hinzu.

Bei Fragen nutzen Sie bitte die README‑Dateien in `code/backend` und
`code/frontend` sowie die technischen Spezifikationen im Pflichtenheft.