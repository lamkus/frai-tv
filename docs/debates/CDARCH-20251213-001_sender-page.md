## Debatte: FRai.TV Sender Page (Landing für YouTube Ads)
**ID:** CDARCH-20251213-001
**Datum:** 2025-12-13
**Status:** DECIDED

### Fragestellung
Welche Umsetzung liefert die beste, stabile und "Netflix-grade" Sender-Seite (FRai.TV) als Landing-Page für YouTube-Werbung, ohne unnötige Komplexität oder Risiko?

### Optionen
- **Option A:** Neue dedizierte Route `/sender` als Landing-Page: Live-Status + nächste geplante Streams + klare CTAs (Live ansehen / Mediathek / Subscribe). Nutzt Backend-Endpoint `/api/livestreams` (read-only via API key) mit Caching.
- **Option B:** Bestehende Route `/live` auf "Sender" umlabeln und nur diese Seite pflegen (keine zusätzliche Landing). Optional Alias `/sender` → `/live`.
- **Option C:** Kein Sender-Page: externer Redirect auf YouTube Channel.

### Argumente
| Rolle | Position | Argument |
|-------|----------|----------|
| Lead Architect (15) | Option A | Klare IA: Sender-Landing getrennt von Player-Detail; minimales Risiko, gut skalierbar. |
| Security (10) | Option A | Read-only Endpoint, kein neuer Auth-Fluss; geringe Angriffsfläche. |
| DevOps/Platform (9) | Option A | Ein zusätzlicher Endpoint + Route; kein Infra-Refactor nötig. |
| Backend (8) | Option A | `/api/livestreams` kann sauber gecached werden; YouTube API Quota wird geschützt. |
| Frontend (8) | Option A | Ads-Traffic braucht eine klare Landing mit CTAs; bestehende `/live` bleibt als Player-Seite. |
| Data Engineering/ETL (7) | Option A | Live/Upcoming kann separat gecached werden; Import-Pipeline bleibt unberührt. |
| QA/Testing (7) | Option A | Gut testbar: leere/fehlerhafte API → kontrollierte Fallback-UI. |
| SRE/Observability (5) | Option A | Endpoint kann über `/api/health`/`/api/metrics` überwacht werden; kurze TTL. |
| Performance Engineering (4) | Option A | Landing lädt klein; keine Full-Catalog Abhängigkeit. |
| UX Design (3) | Option A | "Sender" als mentaler Einstiegspunkt (On Air / Next) erhöht Conversion. |
| Accessibility (A11y) (2) | Option A | Klare Struktur: Headings + Buttons + ARIA; weniger kognitive Last. |
| Documentation/Tech Writing (3) | Option A | Einfach zu dokumentieren: URL + API + Content-Regeln. |
| Product Management (3) | Option A | Direkter Fit zu Ads: Message Match + CTA + Vertrauen. |
| Legal/Compliance (2) | Option A | DSGVO/Consent bleibt zentral; YouTube Embed erst nach Interaktion. |
| Privacy/Data Protection (2) | Option A | Kein zusätzlicher Tracker nötig; existing Consent Mechanik nutzbar. |
| i18n/Localization (2) | Option A | Sender-Strings können sauber in locales ergänzt werden. |
| Maintainability/Refactoring (3) | Option A | Keine Breaking Changes; additive Erweiterung. |
| Legacy Integration (3) | Option A | Kompatibel mit bestehender Router-Struktur. |
| Release Management (2) | Option A | Low-risk Release, leicht rollbackbar. |
| Ethics/Safety (2) | Option A | Transparente CTAs, keine Dark Patterns nötig. |

### Ergebnis
**Option A: 100 Punkte** ✓
Option B: 0 Punkte
Option C: 0 Punkte

### Mindermeinung
Keine.
