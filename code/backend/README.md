# Backend – Streaming‑Plattform

Dieses Verzeichnis enthält den Ausgangspunkt für den Backend‑Server der
Streaming‑Plattform. Der Server basiert auf **Express** und ist als
REST‑API konzipiert. Aktuell sind nur Platzhalter implementiert – die
komplette Logik (Import der YouTube‑Videos, Datenbankanbindung, Admin‑API)
muss gemäß dem Pflichtenheft umgesetzt werden.

## Einrichtung

1. Abhängigkeiten installieren:
   ```bash
   npm install
   ```
2. Datei `.env.example` kopieren und `.env` nennen. Tragen Sie Ihre
   Zugangsdaten ein (YouTube API‑Key, DB‑URL etc.).
3. Server starten:
   ```bash
   npm run dev
   ```

## Endpunkte (Platzhalter)

- **GET /api/health** – Gibt `{ status: "ok" }` zurück.
- **GET /api/videos** – Gibt ein Array von Beispielvideos zurück.
- **GET /api/videos/:id** – Gibt ein einzelnes Beispielvideo zurück.

- **POST /api/refresh-channel** – Importiert Uploads eines Channels (admin/dev use). Unterstützt großes Importieren via `maxResults` (z. B. 5000) und führt Upserts in die Datenbank aus, wenn `DATABASE_URL` konfiguriert ist.
- **POST /api/watch-progress** – Persistiert Watch‑Fortschritt (JSON body: `{ userId?, ytId, progress, duration }`) in DB oder in Cache als Fallback.
- **GET /api/watch-progress?userId=** – Liefert gespeicherten Watch‑Fortschritt für einen User.
- **GET /api/metrics** – Einfache Telemetrie (uptime, memory, requestCount) für smoke checks.

## Weiterentwicklung

Folgende Schritte sind geplant:

1. **Import‑Service**: Anbindung an die YouTube Data API, um die
   Upload‑Playlist des Kanals abzurufen und in die Datenbank zu
   importieren【391388008267651†L498-L537】.
2. **Datenbank**: PostgreSQL‑Tabellen für Videos, Kategorien und Nutzer
   definieren; Zugriff per ORM (Prisma oder TypeORM).
3. **Admin‑Routen**: Endpunkte zum Bearbeiten von Kategorien,
   Metadaten, Cron‑Triggern usw.
4. **Caching**: Redis zur Beschleunigung von häufigen Anfragen.
5. **Authentifizierung**: JWT‑basierte Authentifizierung für den
   Admin‑Bereich implementieren.

Bitte orientieren Sie sich an `docs/Pflichtenheft.md` für detaillierte
Anforderungen.

## Umgebung

Setzen Sie in `.env` mindestens folgendes:

```env
YOUTUBE_API_KEY=your_youtube_data_api_key_here
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

Nach Änderungen am Prisma‑Schema: Client generieren und Migrationen ausführen

```bash
npm install
npx prisma generate
npx prisma migrate dev --name add-watchprogress
```

Hinweis: Für die Google‑Sign‑in Überprüfung verwendet das Frontend (if configured) die Google ID token verification endpoint. Setzen Sie `VITE_GOOGLE_CLIENT_ID` in `code/frontend/.env` für client‑side sign-in.