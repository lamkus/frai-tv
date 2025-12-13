# Agents.md – 20-Rollen-Debatte

> CrossDomain Orchestrator v3: Multidisziplinäre Rollen für gewichtete Entscheidungsfindung.

---

## Rollen-Set (20 Rollen, Summe = 100 Punkte)

| # | Rolle | Gewicht | Fokus |
|---|-------|---------|-------|
| 1 | **Lead Architect** | 15 | Systemdesign, Skalierbarkeit, Patterns |
| 2 | **Security (AppSec)** | 10 | Threat Modeling, OWASP, Auth |
| 3 | **DevOps/Platform** | 9 | CI/CD, Infra, Deployment |
| 4 | **Backend** | 8 | APIs, Services, DB |
| 5 | **Frontend** | 8 | UI, UX, SPA, Performance |
| 6 | **Data Engineering/ETL** | 7 | Pipelines, YouTube API Import |
| 7 | **QA/Testing** | 7 | Tests, Coverage, Qualität |
| 8 | **SRE/Observability** | 5 | Monitoring, Logging, Alerts |
| 9 | **Performance Engineering** | 4 | Latenz, Caching, Optimierung |
| 10 | **UX Design** | 3 | Usability, Flows, Wireframes |
| 11 | **Accessibility (A11y)** | 2 | WCAG, Keyboard Nav, Screen Readers |
| 12 | **Documentation/Tech Writing** | 3 | Docs, Readme, API Specs |
| 13 | **Product Management** | 3 | Features, Priorisierung, Roadmap |
| 14 | **Legal/Compliance** | 2 | YouTube ToS, DSGVO, Lizenzen |
| 15 | **Privacy/Data Protection** | 2 | PII, Consent, Cookies |
| 16 | **i18n/Localization** | 2 | Mehrsprachigkeit, RTL |
| 17 | **Maintainability/Refactoring** | 3 | Code Quality, Tech Debt |
| 18 | **Legacy Integration** | 3 | Migration, Kompatibilität |
| 19 | **Release Management** | 2 | Versioning, Rollouts |
| 20 | **Ethics/Safety** | 2 | Bias, Content Moderation |

---

## Debatten-Prozess

### 1. Trigger
Debatte wird ausgelöst bei:
- Architekturentscheidungen
- Technologiewahl
- Sicherheitsrelevanten Änderungen
- Breaking Changes
- Kostenrelevanten Entscheidungen

### 2. Ablauf
```
1. FRAGESTELLUNG definieren
2. Jede relevante Rolle liefert 1-2 knappe Argumente
3. Gewichtetes Voting (Summe der Gewichte pro Option)
4. Mehrheitsentscheidung dokumentieren
5. Mindermeinung (1 Satz) festhalten
```

### 3. Dokumentation
```markdown
## Debatte: [THEMA]
**ID:** CDARCH-YYYYMMDD-###
**Datum:** YYYY-MM-DD
**Status:** DECIDED

### Fragestellung
[Konkrete Frage]

### Argumente
| Rolle | Position | Argument |
|-------|----------|----------|
| Lead Architect (15) | Option A | ... |
| Security (10) | Option B | ... |
| ... | ... | ... |

### Ergebnis
**Option A: 58 Punkte** ✓
Option B: 42 Punkte

### Mindermeinung
[Security, Privacy]: Option B hätte langfristig bessere Audit-Fähigkeiten geboten.
```

---

## Beispiel-Debatte: Framework-Wahl Frontend

**Fragestellung:** React/Vite beibehalten oder zu Next.js migrieren?

| Rolle | Position | Argument |
|-------|----------|----------|
| Lead Architect (15) | Next.js | SSR für SEO, API Routes |
| DevOps (9) | React/Vite | Einfacherer Deploy als Static |
| Frontend (8) | Next.js | Built-in Routing, Image Opt |
| Performance (4) | Next.js | Automatic Code Splitting |
| Maintainability (3) | React/Vite | Weniger Komplexität |

**Ergebnis:** Next.js (36) vs React/Vite (22) → **Next.js empfohlen**

**Mindermeinung:** Für MVP reicht React/Vite; Migration erhöht Komplexität.

---

## Integration in Workflow

1. Debatten werden in `.tempilot/log.json` protokolliert
2. Entscheidungen fließen in `TODO_MANIFEST.md`
3. Bei STOP-GATE: Debatte pausiert, User wird informiert
