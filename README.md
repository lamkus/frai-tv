## Übersicht des Projekts

Dieses Repository dient als umfassendes Arbeitsverzeichnis für das Entwicklungsteam,
um eine professionelle, skalierbare Streaming‑Webseite für deinen YouTube‑Kanal
aufzubauen. Es enthält Lastenheft, Pflichtenheft, Installationsanleitungen,
Links zu relevanter Open‑Source‑Software und eine einfache Code‑Skeleton‑Struktur.

### Struktur

```
coding_team_workspace/
├── README.md               – Diese Übersicht
├── docs/
│   ├── Lastenheft.md       – Beschreibung der Anforderungen aus Kundensicht
│   ├── Pflichtenheft.md    – Technische Umsetzungsvorgaben und Spezifikation
│   ├── OpenSourceLibraries.md – Hinweise auf Open‑Source‑Projekte und Libraries
│   └── CITATIONS.md        – Quellenangaben
├── installation/
│   └── install_instructions.md – Installations- und Setupanleitungen
└── code/
    ├── backend/           – Basisstruktur für das Backend
    │   ├── package.json
    │   ├── README.md
    │   └── src/
    │       └── index.js    – Einstiegspunkt (Placeholder)
    └── frontend/          – Basisstruktur für das Frontend
        ├── package.json
        ├── README.md
        └── src/
            ├── main.jsx    – Einstiegspunkt (Placeholder)
            └── App.jsx     – Root-Komponente
```

Die Dokumente im Verzeichnis `docs/` sind miteinander verlinkt und enthalten
Verweise (Quellen) auf wissenschaftliche und technische Texte, die die
Entscheidungen für dieses Projekt belegen. Bitte lies zunächst das
Lastenheft, anschließend das Pflichtenheft und verweise auf die
Installationsanleitung, um die Entwicklungsumgebung aufzusetzen.

### Bereitstellung als ZIP

Um diesen Arbeitsbereich komfortabel an dein Entwicklungsteam weiterzugeben,
kannst du das gesamte Verzeichnis `coding_team_workspace` in eine ZIP‑Datei
packen. Die resultierende Datei enthält alle erforderlichen Dokumente und
Quellcodes, sodass die Teammitglieder direkt mit der Installation und
Weiterentwicklung beginnen können. Das Zippen erfolgt beispielsweise mit

```bash
zip -r coding_team_workspace.zip coding_team_workspace
```

oder über die grafische Benutzeroberfläche deines Betriebssystems. Stelle
sicher, dass die ZIP‑Datei die aktuelle Version sämtlicher Dateien enthält,
bevor du sie an dein Team weitergibst.

---

## Quickstart (Dev)

1) Backend starten

```powershell
cd code/backend
npm install
copy .env.example .env # set YOUTUBE_API_KEY and other values
npm run dev
```

2) Frontend starten (neues Terminal)

```powershell
cd code/frontend
npm install
copy .env.example .env # optionally set VITE_GOOGLE_CLIENT_ID
npm run dev
```

3) CI / Tests

The repo contains a GitHub Actions workflow at `.github/workflows/ci.yml` that runs frontend tests and a basic backend smoke check.