# Security Checklist

> Sicherheitsprüfung vor jedem größeren Release.

---

## Authentication & Authorization

- [ ] JWT Tokens haben Expiry
- [ ] Passwords sind gehasht (bcrypt, Argon2)
- [ ] Rate Limiting auf Login-Endpoint
- [ ] Session Invalidation bei Logout
- [ ] Admin-Routen geschützt

## Input Validation

- [ ] Alle User-Inputs validiert
- [ ] SQL Injection: Parameterized Queries
- [ ] XSS: Output Encoding
- [ ] Command Injection: Keine Shell-Ausführung mit User-Input

## Data Protection

- [ ] Keine Secrets im Code/Logs
- [ ] `.env` in `.gitignore`
- [ ] HTTPS erzwungen
- [ ] Cookie Flags: `HttpOnly`, `Secure`, `SameSite`

## DSGVO / Privacy (remAIke.TV spezifisch)

- [ ] Cookie-Consent implementiert
- [ ] YouTube NoCookie Domain verwendet
- [ ] Datenschutzerklärung verlinkt
- [ ] Keine unnötige Datenspeicherung

## Dependencies

- [ ] `npm audit` ausgeführt
- [ ] Kritische CVEs behoben
- [ ] Keine bekannten Vulnerabilities

## Infrastructure

- [ ] Firewall konfiguriert
- [ ] SSH Key-only (kein Passwort-Login)
- [ ] Automatic Security Updates aktiviert
- [ ] Backup-Strategie dokumentiert

## API Security

- [ ] CORS korrekt konfiguriert
- [ ] Rate Limiting auf APIs
- [ ] Keine sensiblen Daten in URLs
- [ ] Error Messages leaken keine Interna

---

## Vulnerability Report

| CVE/Issue | Severity | Status | Mitigation |
|-----------|----------|--------|------------|
| | | | |

---

## Sign-Off

| Role | Name | Date | ✓ |
|------|------|------|---|
| Security Lead | | | |
| Dev Lead | | | |
