# REFERENCES.md – Quellen & Dokumentation

> CrossDomain Orchestrator v3: Verifizierte Quellen für alle technischen Entscheidungen.

---

## Primärquellen (Hersteller-Dokumentation)

### Node.js / JavaScript Runtime
| Quelle | Version | Bezug |
|--------|---------|-------|
| [Node.js Docs](https://nodejs.org/docs/latest-v18.x/api/) | 18.x LTS | Backend Runtime |
| [ES Modules](https://nodejs.org/api/esm.html) | 18+ | Module System |
| [npm Docs](https://docs.npmjs.com/) | 10.x | Package Management |

### Express.js
| Quelle | Version | Bezug |
|--------|---------|-------|
| [Express.js Guide](https://expressjs.com/en/guide/routing.html) | 4.x | Backend Framework |
| [Express API Reference](https://expressjs.com/en/4x/api.html) | 4.18 | API Routes |

### React / Frontend
| Quelle | Version | Bezug |
|--------|---------|-------|
| [React Docs](https://react.dev/) | 18.x | Frontend Framework |
| [Vite Guide](https://vitejs.dev/guide/) | 4.x | Build Tool |
| [Vite Config](https://vitejs.dev/config/) | 4.x | vite.config.js |

### YouTube API
| Quelle | Version | Bezug |
|--------|---------|-------|
| [YouTube Data API v3](https://developers.google.com/youtube/v3/docs) | v3 | Video Import |
| [PlaylistItems.list](https://developers.google.com/youtube/v3/docs/playlistItems/list) | v3 | Channel Uploads |
| [Embed Parameters](https://developers.google.com/youtube/player_parameters) | - | iFrame Player |
| [YouTube ToS](https://www.youtube.com/t/terms) | 2024 | Legal Compliance |

### PostgreSQL
| Quelle | Version | Bezug |
|--------|---------|-------|
| [PostgreSQL Docs](https://www.postgresql.org/docs/14/) | 14 | Database |
| [node-postgres (pg)](https://node-postgres.com/) | 8.x | DB Client |

### Deployment / Infrastructure
| Quelle | Version | Bezug |
|--------|---------|-------|
| [PM2 Docs](https://pm2.keymetrics.io/docs/usage/quick-start/) | 5.x | Process Manager |
| [nginx Docs](https://nginx.org/en/docs/) | 1.24 | Reverse Proxy |
| [Plesk Node.js](https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/nodejs-support.html) | Obsidian | VPS Hosting |
| [Let's Encrypt](https://letsencrypt.org/docs/) | - | SSL Certificates |

### Strato-Spezifisch
| Quelle | Version | Bezug |
|--------|---------|-------|
| [Strato Node.js Tutorial](https://www.strato.nl/faq/hosting/hoe-installeer-ik-nodejs/) | 2024 | VPS Setup |
| [Strato FTP FAQ](https://www.strato-hosting.co.uk/faq/hosting/how-to-upload-files/) | 2024 | File Upload |

---

## Standards & Specifications

| Standard | Bezug |
|----------|-------|
| [WCAG 2.1 AA](https://www.w3.org/WAI/WCAG21/quickref/) | Accessibility |
| [OWASP Top 10](https://owasp.org/Top10/) | Security |
| [DSGVO/GDPR](https://gdpr.eu/) | Privacy |
| [Semantic Versioning](https://semver.org/) | Versioning |

---

## Open Source Referenzprojekte

| Projekt | Repository | Bezug |
|---------|------------|-------|
| Streama | [streamaserver/streama](https://github.com/streamaserver/streama) | Netflix-ähnliches UI, Admin Panel |
| Nextflix | [Apestein/nextflix](https://github.com/Apestein/nextflix) | Next.js Netflix Clone |
| Invidious | [iv-org/invidious](https://github.com/iv-org/invidious) | YouTube Alternative Frontend |

---

## VS Code / Tooling

| Quelle | Bezug |
|--------|-------|
| [VS Code Docs](https://code.visualstudio.com/docs) | Editor |
| [ESLint Rules](https://eslint.org/docs/rules/) | Linting |
| [Prettier Options](https://prettier.io/docs/en/options.html) | Formatting |
| [Tailwind CSS](https://tailwindcss.com/docs) | Styling (planned) |

---

## Projektinterne Dokumente

| Dokument | Pfad | Beschreibung |
|----------|------|--------------|
| Lastenheft | `docs/Lastenheft.md` | Anforderungsspezifikation |
| Pflichtenheft | `docs/Pflichtenheft.md` | Technische Spezifikation |
| OpenSourceLibraries | `docs/OpenSourceLibraries.md` | Bibliotheken-Referenz |
| Citations | `docs/CITATIONS.md` | Quellenverweise |
| Deployment Guide | `installation/strato_deployment.md` | Strato VPS Anleitung |

---

## WEB-CHECK Log

> Dokumentation aller Online-Verifizierungen.

| Datum | Thema | Quelle | Ergebnis |
|-------|-------|--------|----------|
| 2024-12-09 | PM2 ecosystem.config.cjs | [PM2 Docs](https://pm2.keymetrics.io/docs/usage/application-declaration/) | ✅ Syntax verified |
| 2024-12-09 | Plesk Node.js Extension | [Plesk Docs](https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/nodejs-support.html) | ✅ start.js wrapper approach valid |
| 2024-12-09 | nginx proxy_pass | [nginx Docs](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) | ✅ Config syntax correct |
| 2024-12-09 | Vite env variables | [Vite Env](https://vitejs.dev/guide/env-and-mode.html) | ✅ VITE_ prefix required |

---

*Last Updated: 2024-12-09 by CrossDomain Orchestrator v3*
