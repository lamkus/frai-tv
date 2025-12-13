# EVAL_RUBRICS.md – Bewertungskriterien

> Qualitätsbewertung für Code, Features und Releases.

---

## Bewertungsskala

| Score | Bedeutung |
|-------|-----------|
| 5 | Exzellent – Best Practice, vorbildlich |
| 4 | Gut – Erfüllt alle Anforderungen |
| 3 | Akzeptabel – Funktioniert, Verbesserungen möglich |
| 2 | Mangelhaft – Kritische Lücken |
| 1 | Ungenügend – Nicht nutzbar |

**Gate:** Minimum Score 3 für Release, Score 4 für kritische Komponenten.

---

## 1. Korrektheit (Funktionalität)

| Score | Kriterium |
|-------|-----------|
| 5 | Alle Anforderungen erfüllt, Edge Cases abgedeckt |
| 4 | Kernfunktionen vollständig, seltene Edge Cases offen |
| 3 | Hauptfunktion ok, bekannte Einschränkungen |
| 2 | Teilweise funktional, kritische Bugs |
| 1 | Nicht funktional |

---

## 2. Sicherheit (Security)

| Score | Kriterium |
|-------|-----------|
| 5 | OWASP Top 10 adressiert, Security Review bestanden |
| 4 | Keine bekannten Vulnerabilities, Input validiert |
| 3 | Basis-Security implementiert, Verbesserungen nötig |
| 2 | Bekannte Schwachstellen, unvalidierter Input |
| 1 | Kritische Sicherheitslücken |

### Checkpunkte
- [ ] SQL Injection geschützt
- [ ] XSS Prevention
- [ ] CSRF Tokens
- [ ] Auth/AuthZ implementiert
- [ ] Secrets nicht im Code

---

## 3. Performance

| Score | Kriterium |
|-------|-----------|
| 5 | Sub-100ms Response, optimierte Assets, Caching |
| 4 | <500ms Response, Assets komprimiert |
| 3 | <2s Response, akzeptable Ladezeiten |
| 2 | >2s Response, spürbare Verzögerungen |
| 1 | Timeouts, nicht nutzbar |

### Metriken
- Time to First Byte (TTFB)
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)

---

## 4. UX / Usability

| Score | Kriterium |
|-------|-----------|
| 5 | Intuitiv, konsistent, Delight-Faktoren |
| 4 | Klar verständlich, gute Flows |
| 3 | Nutzbar, kleine Usability-Issues |
| 2 | Verwirrend, inkonsistente Patterns |
| 1 | Nicht nutzbar ohne Anleitung |

---

## 5. Accessibility (A11y)

| Score | Kriterium |
|-------|-----------|
| 5 | WCAG AAA, alle Assistive Technologies |
| 4 | WCAG AA, Keyboard + Screen Reader |
| 3 | WCAG A, Basis-Accessibility |
| 2 | Teilweise accessible, Lücken |
| 1 | Nicht accessible |

### Checkpunkte
- [ ] Keyboard Navigation vollständig
- [ ] Focus-Indicator sichtbar
- [ ] Alt-Texte für Bilder
- [ ] Ausreichend Kontrast
- [ ] ARIA Labels wo nötig

---

## 6. Developer Experience (DX)

| Score | Kriterium |
|-------|-----------|
| 5 | Exzellente Docs, einfaches Setup, klare Patterns |
| 4 | Gute Docs, verständlicher Code |
| 3 | Basis-Docs, Code lesbar |
| 2 | Spärliche Docs, unklare Struktur |
| 1 | Keine Docs, unlesbarer Code |

---

## 7. Maintainability

| Score | Kriterium |
|-------|-----------|
| 5 | Modularer Code, hohe Test-Coverage, keine Tech Debt |
| 4 | Klare Struktur, gute Coverage |
| 3 | Wartbar, einige Verbesserungen nötig |
| 2 | Komplexer Code, niedrige Coverage |
| 1 | Spaghetti-Code, keine Tests |

### Metriken
- Test Coverage > 80%
- Cyclomatic Complexity < 10
- Keine Duplikation > 3%

---

## Feature Evaluation Template

```markdown
## Feature: [NAME]
**Evaluator:** [Name/Agent]
**Datum:** YYYY-MM-DD

| Kategorie | Score | Kommentar |
|-----------|-------|-----------|
| Korrektheit | /5 | |
| Sicherheit | /5 | |
| Performance | /5 | |
| UX | /5 | |
| A11y | /5 | |
| DX | /5 | |
| Maintainability | /5 | |

**Durchschnitt:** X.X / 5
**Gate bestanden:** ✅/❌
**Empfehlung:** [Release / Fix Required / Block]
```
