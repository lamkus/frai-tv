# PR Review Checklist

> Für jeden Pull Request durchzugehen.

---

## Code Quality

- [ ] Code ist lesbar und selbsterklärend
- [ ] Keine unnötige Komplexität
- [ ] DRY-Prinzip beachtet
- [ ] Namenskonventionen eingehalten
- [ ] Keine auskommentierten Code-Blöcke

## Funktionalität

- [ ] Feature erfüllt Anforderungen
- [ ] Edge Cases berücksichtigt
- [ ] Error Handling implementiert
- [ ] Keine Breaking Changes (oder dokumentiert)

## Tests

- [ ] Unit Tests für neue Funktionen
- [ ] Bestehende Tests nicht gebrochen
- [ ] Test Coverage nicht gesunken

## Security

- [ ] Keine Secrets im Code
- [ ] Input Validation vorhanden
- [ ] Keine SQL Injection Risiken
- [ ] Keine XSS Risiken

## Performance

- [ ] Keine N+1 Queries
- [ ] Keine Memory Leaks
- [ ] Keine unnötigen Re-Renders (React)

## Documentation

- [ ] JSDoc/Kommentare wo nötig
- [ ] README aktualisiert (bei API-Änderungen)
- [ ] CHANGELOG Entry

## Accessibility

- [ ] Keyboard-navigierbar
- [ ] ARIA Labels wo nötig
- [ ] Kontrast ausreichend

---

## Review Decision

| Decision | Begründung |
|----------|------------|
| ✅ Approved | |
| 🔄 Request Changes | |
| ❌ Rejected | |

---

## Comments

```
[Reviewer-Kommentare hier]
```
