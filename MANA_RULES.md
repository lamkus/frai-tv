# MANA_RULES.md – Verbindliche Arbeitsregeln

> CrossDomain Orchestrator v3: Diese Regeln gelten dauerhaft für alle Aktionen.

---

## 1. Quellenpriorität

```
1. Primärquellen (Hersteller-Doku, Standards, RFCs)
2. Offizielle Release Notes / Changelogs
3. Stack Overflow (verifizierte Antworten)
4. Blog-Artikel (nur mit Vorsicht)
```

**Regel:** Vor jedem Befehl/Config → WEB-CHECK gegen Primärquellen.

---

## 2. Keine Halluzinationen

- ❌ Keine erfundenen CLI-Flags
- ❌ Keine Pseudo-Pfade
- ❌ Keine angenommenen API-Optionen
- ✅ Bei Unsicherheit → WEB-CHECK oder Nachfrage

---

## 3. Minimalinvasiv

- Bevorzuge PR/Patch-Ansatz über Direktänderungen
- Kleine, atomare Commits
- Jede Änderung begründen (WHY + Trade-offs)

---

## 4. Idempotenz & Wiederholbarkeit

- Skripte sollen mehrfach ausführbar sein
- Keine Side Effects bei read-only Operationen
- Setup-Skripte mit Existenzprüfungen

---

## 5. Sicherheit > Geschwindigkeit

- Keine Secrets im Klartext (Logs, Code, Chat)
- Keine Credentials anfordern
- Sensitive Daten → STOP-GATE

---

## 6. Stop-Gates (SG)

| ID | Trigger | Aktion |
|----|---------|--------|
| SG-1 | Destruktive Befehle (rm, del, DROP) | HALT + User fragen |
| SG-2 | Extension-Install außerhalb Liste | HALT + User fragen |
| SG-3 | Secrets/Tokens/PII | NIEMALS loggen/anfordern |
| SG-4 | Public API Breaks | HALT + User fragen |
| SG-5 | Kostenrelevante Cloud-Ops | HALT + User fragen |

---

## 7. Auto-Approve Regeln

### ✅ Erlaubt (read-only)
```
git status, git log, git show, git diff
ls, dir, cat, type, head, tail
npm list, npm outdated
```

### ❌ Nicht erlaubt (destruktiv)
```
rm, del, rmdir
git push --force, git reset --hard
DROP TABLE, DELETE FROM
npm publish, deploy
sudo *
```

---

## 8. Accessibility & i18n

- A11y ist **keine Kür**, sondern Pflicht
- Alle UI-Komponenten: Keyboard-navigierbar
- Alle Texte: i18n-fähig strukturieren
- Farben: Kontrastverhältnis prüfen (WCAG AA)

---

## 9. Dokumentationspflicht

- Jede Architekturentscheidung dokumentieren
- Jeder Task mit ID und Status
- Logs in `.tempilot/log.json`
- Updates in `TODO_MANIFEST.md`

---

## 10. Code-Qualität

- Lint vor Commit (ESLint)
- Format vor Commit (Prettier)
- Tests vor Merge
- Code Review bei kritischen Änderungen

---

## 11. Projektspezifische Regeln (remAIke.TV)

### YouTube API
- API-Key niemals committen
- Rate Limits beachten (10.000 Quota/Tag)
- Embed nur für eigene, öffentliche Videos

### DSGVO
- Cookie-Consent vor YouTube-Embed
- `youtube-nocookie.com` Domain verwenden
- Datenschutzerklärung pflegen

### Lizenzen
- Nur MIT/Apache/BSD-kompatible Pakete
- GPL-Pakete nur mit Bedacht (Copyleft!)
- License-Check vor neuen Dependencies

---

## 12. Definition of Done (DoD)

Ein Task ist DONE wenn:
- [ ] Build grün
- [ ] Tests grün
- [ ] Lint/Format sauber
- [ ] Security-Checks ok
- [ ] Docs aktualisiert
- [ ] TODO_MANIFEST.md Status = DONE
- [ ] RUNBOOK.md konsistent
- [ ] ProjectRegistry.md aktuell
