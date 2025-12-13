# Pflichtenheft

Das Pflichtenheft leitet aus dem Lastenheft konkrete technische
Umsetzungsvorgaben ab. Es definiert Architektur, Technologien, Schnittstellen
und Testkriterien. Alle Angaben sind bindend für das Entwicklerteam.

## 1  Architekturübersicht

Die Lösung besteht aus drei Hauptkomponenten:

1. **Frontend (Client)**: Eine Single‑Page‑Application (SPA) basierend auf
   React (Next.js). Diese Anwendung kümmert sich um die Darstellung,
   Routing, Theming (Netflix‑/Waipu‑/Apple‑Style) und kommuniziert über
   REST‑Endpoints mit dem Backend. Das Frontend nutzt Tailwind CSS für
   flexible Layouts und anpassbares Design.
2. **Backend (API‑Server)**: Ein Node.js‑Server mit Express oder Nest.js.
   Er stellt REST‑Endpoints bereit, die Videos, Kategorien und
   Suchergebnisse liefern. Zudem importiert er regelmäßig neue Videos via
   YouTube Data API【391388008267651†L498-L537】 und speichert Metadaten in der
   Datenbank. Das Backend übernimmt Authentifizierung für das Admin‑Panel.
3. **Datenhaltung**: Eine relationale Datenbank (PostgreSQL) speichert
   Video‑Metadaten, Kategorien, Nutzerinformationen (falls implementiert)
   und Import‑Status. Redis dient als Cache, um häufig abgerufene
   Daten (Startseite, „Beliebteste Videos“) schnell bereitzustellen.

Für Inspiration bezüglich Architektur und Code können vorhandene
Open‑Source‑Projekte herangezogen werden:

- **Streama**: Demonstriert ein Netflix‑ähnliches Dashboard mit
  Fortschrittsanzeige und Episode‑Browser【613967695887634†L418-L444】 sowie
  einem Admin‑Panel zur Metadatenpflege【613967695887634†L452-L456】.
- **Nextflix**: Ein modernes Next.js‑Projekt, das bis zu vier Profile pro
  Nutzer, Suchfunktion, SaaS‑Abrechnung und unendliches Scrollen
  implementiert【832452663600043†screenshot】.

## 2  Modulübersicht

### 2.1  Frontend

**Technologien:** React / Next.js (v13+), Tailwind CSS, Vite (Build Tool),
React Router (falls nicht Next.js), Axios oder SWR für API‑Requests.

**Module:**

| Modul            | Beschreibung |
|------------------|-------------|
| **Layout & Theme** | Basiskomponente, die Header, Footer, Navigation
enthält und ein Theme‑System bereitstellt (wechselbar zwischen
Netflix‑, Waipu‑ und Apple‑Look). |
| **Startseite**    | Präsentiert Slider‑Sektionen (Kategorien,
„Continue Watching“, „Neu“, „Beliebt“). Diese Komponenten laden ihre
Daten asynchron vom Backend. |
| **Video‑Detail**  | Seite/Modal, die den YouTube‑Player per iFrame
einbettet, Metadaten anzeigt und zum nächsten Video navigiert. |
| **Suchseite**     | Zeigt Ergebnisse für Suchbegriffe und Filter
(Kategorie, Jahr, Dauer). |
| **Admin‑Panel**   | Geschützte Oberfläche, um Kategorien zu erstellen,
Metadaten zu bearbeiten und Import‑Prozesse zu überwachen. |
| **Livestream‑Sektion** | Bereich, der den laufenden Livestream via
YouTube‑Live‑URL einbettet oder für kommende Termine einen Hinweis
anzeigt. |

**Spezielle Anforderungen:**

- Das Theme‑System muss dynamisch Farben, Fonts und Layouts ändern
  können. Für Netflix‑ähnliche Slider empfiehlt sich horizontales
  Scrollen und Auto‑Preview.
- Die App soll LocalStorage nutzen, um Positionen für „Continue
  Watching“ zu merken. Für spätere Multi‑User‑Profile kann die
  Position auch serverseitig gespeichert werden.
- Das Frontend ist über CI/CD automatisiert baubar und als statische
  Assets über ein CDN lieferbar.

### 2.2  Backend

**Technologien:** Node.js (18+), Express oder Nest.js, PostgreSQL,
TypeORM/Prisma, Redis, cron‑Scheduler (node‑cron), dotenv für
Konfiguration.

**Module:**

| Modul             | Beschreibung |
|-------------------|-------------|
| **Video Service** | Importiert Videos über die YouTube API. Dazu wird
die Upload‑Playlist des Kanals via `playlistItems.list` ausgelesen und die
Resultate paginiert in die Datenbank gespeichert【391388008267651†L498-L537】. |
| **Category Service** | Generiert Kategorien basierend auf Metadaten
(Jahr, Schlagwort) und speichert sie; bietet API zur Bearbeitung. |
| **Search Service**| Durchsucht Videos nach Titel oder anderen
Attributen. Nutzt DB‑Volltextsuche oder ElasticSearch. |
| **Recommendation Engine (optional)** | Berechnet
empfohlene Videos (z. B. meistgesehene, neueste) und
füllt die entsprechenden Sektionen. |
| **Auth Service**   | Verwaltet Admin‑Accounts via JWT; ermöglicht
Login, Logout und Rechteprüfung. |
| **Live Service**   | Prüft, ob gerade ein Livestream läuft und
liefert den entsprechenden Embed‑Link; sonst gibt es die nächsten
geplanten Streams zurück. |

**Schnittstellen:**

- **GET /api/videos** – Liefert paginierte Listen von Videos,
  filterbar nach Kategorie, Jahr und Dauer.
- **GET /api/videos/:id** – Liefert Details eines Videos inkl.
  Embed‑URL und verwandter Videos.
- **GET /api/categories** – Listet verfügbare Kategorien.
- **GET /api/search?q=...** – Sucht Videos nach Title oder Tags.
- **POST /api/admin/categories** – Admin‑Endpoint zum Erstellen
  eigener Kategorien (Authentifizierung erforderlich).
- **POST /api/admin/import** – Trigger für manuellen API‑Import.

**Datenmodell (vereinfacht):**

- **Video**: id (UUID), ytId (string), title, description,
  categoryIds (array), publishDate, duration, thumbnailUrl,
  viewCount, tags, createdAt, updatedAt.
- **Category**: id, name, description, sortOrder, createdAt.
- **User** (optional): id, email, passwordHash, roles.

### 2.3  Installation / Betrieb

Die Installation wird im Dokument
`installation/install_instructions.md` detailliert beschrieben. Kurzfassung:

1. Node.js und npm/pnpm installieren.
2. Repository klonen, `cd code/backend && npm install`,
   `cd code/frontend && npm install`.
3. `.env`‑Dateien aus den Vorlagen erstellen und API‑Keys eintragen.
4. Datenbank (PostgreSQL) und Redis starten (z. B. via Docker Compose).
5. Backend mit `npm run dev` starten, Frontend mit `npm run dev` starten.
6. Optional: Docker Compose nutzen, um Services gemeinsam zu
   orchestrieren.

## 3  Open‑Source‑Referenzen und Bibliotheken

Das Projekt profitiert von bestehender Software. Das Team sollte die
folgenden Projekte studieren und bei Bedarf Code oder Konzepte
adaptieren:

| Projekt | Quelle | Nutzen | Zitat |
|--------|-------|-------|------|
| **Streama** | [GitHub – streamaserver/streama](https://github.com/streamaserver/streama) | Inspiration für die Episode‑Browser und das Admin‑Panel. Streama zeigt „Continue Watching“ und greift auf die MovieDB‑API zu, um Metadaten automatisch anzureichern【613967695887634†L418-L444】【613967695887634†L452-L456】. | 【613967695887634†L418-L444】 |
| **Nextflix** | [GitHub – Apestein/nextflix](https://github.com/Apestein/nextflix) | Modernes Netflix‑Klonprojekt mit Next.js 13, Server Actions, mehreren Profilen und unendlichem Scrollen【832452663600043†screenshot】. | 【832452663600043†screenshot】 |
| **WordPress YouTube Plugin** | [Embed Plus for YouTube](https://wordpress.org/plugins/youtube-embed-plus/) | Falls eine Low‑Code‑Lösung benötigt wird, ermöglicht das Plugin das Einbetten ganzer Kanäle und Playlists inklusive Live‑Streams. |  |

## 4  Testkriterien und Abnahmebedingungen

1. **Vollständigkeit:** Alle im Lastenheft beschriebenen Funktionen sind
   implementiert oder durch Tickets für zukünftige Releases dokumentiert.
2. **Performance:** Beim Laden der Startseite mit 1 000 Videos darf
   die Ladezeit 2 Sekunden nicht überschreiten (auf durchschnittlicher
   Desktop‑Hardware). Lazy‑Loading und Caching werden eingesetzt.
3. **Responsiveness:** Das Frontend funktioniert auf Desktop (≥ 1280 px),
   Tablet (≥ 768 px) und Smartphone (≥ 375 px) fehlerfrei. Layouts
   passen sich entsprechend an.
4. **Barrierefreiheit:** Die Seite erfüllt die WCAG‑AA‑Kriterien für
   Kontrast und ist mit Tastatur bedienbar【33158469727155†L123-L167】.
5. **Datenschutz:** Beim ersten Laden wird der YouTube‑iFrame nur nach
   Zustimmung geladen; die Seite enthält eine Datenschutzerklärung.
6. **Fehlerfreiheit:** 0 kritische Bugs in Tests; weniger als 5 
   bekannte kleinere Bugs, die dokumentiert werden.
7. **Dokumentation:** Code ist dokumentiert; Readmes, Pflichten- und
   Lastenheft sind aktuell und in das Repository eingebunden.

## 5  Projektablauf / Zeitplan

1. **Analyse & Planung:** 1–2 Wochen. Lasten- und Pflichtenheft
   finalisieren, Architektur entwerfen.
2. **Prototyping:** 2 Wochen. Minimaler Prototyp (Video‑Liste,
   Einbettung eines YouTube‑Videos) zur UI‑Evaluation.
3. **Backend‑Grundlage:** 3 Wochen. Datenmodelle, YouTube‑Import,
   grundlegende API.
4. **Frontend‑Grundlage:** 3 Wochen. Layouts, erste Komponenten,
   Datenabruf.
5. **Admin‑Panel & Automatisierung:** 3 Wochen. Verwaltung, Cron‑Jobs.
6. **Feinschliff & Themes:** 2 Wochen. Theme‑Wechsel,
   Responsiveness, Barrierefreiheit.
7. **Testing & Deployment:** 2 Wochen. Tests, Bugfixes,
   CI/CD einrichten, erste Live‑Veröffentlichung.

Der Zeitplan ist beispielhaft; reale Ressourcen und externe Faktoren
können die Dauer beeinflussen. Iterative Releases sind empfehlenswert.

---

*Dieses Pflichtenheft basiert auf dem Lastenheft und enthält alle
technischen Spezifikationen, die für die Umsetzung benötigt werden.*