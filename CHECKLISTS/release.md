# Release Checklist

> Vor jedem Release durchzugehen.

---

## Pre-Release

- [ ] **Version**: Versionsnummer in `package.json` aktualisiert
- [ ] **Changelog**: `CHANGELOG.md` mit allen Änderungen
- [ ] **Dependencies**: Keine kritischen Vulnerabilities (`npm audit`)
- [ ] **Tests**: Alle Tests grün
- [ ] **Lint**: ESLint ohne Fehler
- [ ] **Build**: Frontend baut erfolgreich (`npm run build`)

## Code Quality

- [ ] **Code Review**: Mindestens 1 Review für kritische Changes
- [ ] **Tech Debt**: Keine neuen TODO-Kommentare ohne Ticket
- [ ] **Documentation**: README/Docs aktualisiert

## Security

- [ ] **Secrets**: Keine Credentials im Code
- [ ] **Dependencies**: `npm audit` clean oder Risiko dokumentiert
- [ ] **Environment**: `.env.example` aktuell

## Database

- [ ] **Migrations**: Alle Migrations ausgeführt
- [ ] **Rollback**: Rollback-Strategie dokumentiert
- [ ] **Backup**: Datenbank-Backup vor Release

## Deployment

- [ ] **Staging**: Auf Staging getestet
- [ ] **Smoke Test**: Kritische Pfade geprüft
- [ ] **Monitoring**: Alerts konfiguriert

## Post-Release

- [ ] **Git Tag**: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
- [ ] **Push**: `git push origin main --tags`
- [ ] **Verify**: Production Health-Check
- [ ] **Announce**: Team informiert

---

## Sign-Off

| Role | Name | Date | ✓ |
|------|------|------|---|
| Dev Lead | | | |
| QA | | | |
| DevOps | | | |
