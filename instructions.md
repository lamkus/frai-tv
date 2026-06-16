# instructions.md – remAIke.TV (YouTube Ops + Dev)

**Purpose:** Wenn du morgen zurückkommst, weiß jeder genau was zu tun ist.

**Stand:** 2026-01-13

---

## 🚨 NON-NEGOTIABLE RULES

> Diese Regeln sind NICHT verhandelbar. Bei Verstoß: STOP + User fragen.

### YouTube API
- **Public API FIRST** für READ (videos/channels/playlists) via `YOUTUBE_API_KEY`
- **OAuth NUR für WRITE** (playlist inserts, videos.update, uploads)
- **NIEMALS via API löschen** → Manuell im YouTube Studio (0 Quota)
- Bei `quotaExceeded`: **SOFORT STOPPEN**
- **Keine Secrets im Repo** (Keys, Tokens, Refresh Tokens)

### Video-Änderungen
- **NIEMALS blind batch-updaten**
- **VOR jeder Änderung**: Video-ID, Thumbnail, Dateiname prüfen
- **Änderungen zeigen** → User-Freigabe abwarten → DANN erst ändern
- Bei Serien: **Produktions-Nr ≠ Ausstrahlungs-Nr** beachten!

---

## 📚 AUTHORITATIVE DOCS (IMMER LADEN!)

| Datei | Beschreibung | Priorität |
|-------|--------------|-----------|
| `.github/copilot-instructions.md` | Wird bei JEDEM Prompt geladen | 🔴 KRITISCH |
| `MANA_RULES.md` | Arbeitsregeln, Stop-Gates | 🔴 KRITISCH |
| `docs/YOUTUBE_KNOWLEDGE_BASE.md` | YouTube Best Practices 2025/2026 | 🟡 WICHTIG |
| `config/bravestarr_episodes.json` | Episode-Mapping (Prod-Nr → DE Titel) | 🟡 WICHTIG |
| `config/soundie_catalog.json` | Soundie Template | 🟡 WICHTIG |

---

## 📺 CHANNEL INFO

```
Channel ID:     UCVFv6Egpl0LDvigpFbQXNeQ
Channel Name:   remAIke_IT
Videos Total:   ~285 (Jan 2026)
  - Public:     ~252
  - Private:    ~30 (Drafts)
```

### Content-Status

| Kategorie | Status |
|-----------|--------|
| Alfred J. Kwak (52) | ✅ Komplett |
| BraveStarr (65) | 🔄 4 online, Rest in Produktion |
| Soundies (~40) | 📋 Drafts (SEO optimieren!) |
| Filme (Public Domain) | ✅ Online |

---

## ⚠️ AKTUELLE PROBLEME (2026-01-13)

### BraveStarr Drafts - FALSCH BENANNT

| Video-ID | Aktuell (FALSCH) | Korrekt | Status |
|----------|------------------|---------|--------|
| `EaOwzIJuQJU` | "Fallen Idol" | "Das Ungetüm aus der Wüste" (Prod 002) | 🔴 FIX NEEDED |
| `W_VhuNn-5nY` | "Skuzz and Fuzz" | Prüfen gegen Prod-Nr! | ⚠️ PRÜFEN |

### Soundies - NICHT GEÄNDERT

Trotz Script-Output wurden die Soundie-Drafts NICHT umbenannt. Status im YouTube Studio prüfen!

---

## 🎯 NÄCHSTE SCHRITTE (Priority Order)

### P0 - BraveStarr Korrektur
1. Video-IDs der Drafts holen
2. Thumbnail im Studio prüfen → richtigen DE Titel bestätigen
3. `config/bravestarr_episodes.json` konsultieren
4. User-Freigabe für Änderung holen
5. Einzeln korrigieren (NICHT batch!)

### P1 - Soundies aufbereiten
1. Alle Soundie-Draft Video-IDs auflisten
2. SEO-Template aus `config/soundie_catalog.json` anwenden
3. Musik-Playlist erstellen
4. User-Review vor Publish

### P2 - Playlist-Struktur
- BraveStarr Playlist erstellen (chronologisch nach Episoden-Nr)
- Soundies Playlist erstellen

---

## 🔧 ENVIRONMENT

```powershell
# API Key setzen (NIE committen!)
$env:YOUTUBE_API_KEY = "AIzaSy..."

# Python venv aktivieren
.\.venv\Scripts\Activate.ps1

# OAuth Token prüfen
Get-Content config/youtube_oauth.json | ConvertFrom-Json | Select-Object expiry
```

---

## 📁 WICHTIGE PFADE

```
config/
├── youtube_oauth.json          # OAuth Token (NICHT committen!)
├── bravestarr_episodes.json    # Episode-Mapping
├── soundie_catalog.json        # Soundie Template
├── full_channel_scan.json      # Alle Videos mit IDs
└── watchtime_playlists.json    # Playlist-Config

scripts/youtube/
├── full_channel_scan.py        # Channel-Inventory
└── [andere Scripts]            # Mit Vorsicht verwenden!

docs/
├── YOUTUBE_KNOWLEDGE_BASE.md   # Ausführliche Best Practices
└── [weitere Docs]
```

---

## 🛡️ BEI PROBLEMEN

1. **Quota erschöpft?** → Warte bis 08:00 UTC (09:00 MEZ)
2. **Falsche Änderung gemacht?** → Im YouTube Studio manuell korrigieren
3. **Unsicher?** → STOP + User fragen, nicht raten!
4. **Script funktioniert nicht?** → API-Response prüfen, nicht blind wiederholen

---

## 📖 CHANGELOG

| Datum | Änderung |
|-------|----------|
| 2026-01-13 | BraveStarr Episode-Mapping erstellt |
| 2026-01-13 | Soundie-Katalog Template erstellt |
| 2026-01-13 | YouTube Knowledge Base erstellt |
| 2026-01-13 | copilot-instructions.md erweitert |
| 2026-01-13 | MANA_RULES.md mit Learnings ergänzt |
