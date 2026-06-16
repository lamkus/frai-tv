# 🎯 remAIke Channel Optimization Plan

> **Datum:** 27. Dezember 2025  
> **Quota Status:** FRISCH RESET ✅ (10.000 Units verfügbar)  
> **Priorität:** MAXIMALE SEO-Optimierung

---

## 📊 Kanal-Statistik

| Metrik | Wert |
|--------|------|
| **Total Videos** | 124 |
| **Cartoons** | 74 (60%) |
| **Classic Films** | 34 (27%) |
| **Christmas Specials** | 12 (10%) |
| **Comedy** | 4 (3%) |

### Serien-Verteilung
| Serie | Videos | Playlist Status |
|-------|--------|-----------------|
| Betty Boop | 25 | ❌ Fehlt |
| Felix the Cat | 12 | ❌ Fehlt |
| Superman | 9 | ❌ Fehlt |
| Casper | 8 | ❌ Fehlt |
| Popeye | 4 | ❌ Fehlt |
| Buster Keaton | 2 | ❌ Fehlt |
| Charlie Chaplin | 2 | ❌ Fehlt |

---

## 🔴 Identifizierte Probleme

### 1. TITEL-PROBLEME
- ❌ **5 Titel > 70 Zeichen** (werden abgeschnitten!)
- ❌ **120 Titel ohne Quality Tag** (8K/4K fehlt auf YouTube)
- ❌ **2 Titel ohne Jahr**
- ❌ **Inkonsistenz:** `originalTitle` (YouTube) ≠ `title` (Display)

### 2. FEHLENDE PLAYLISTS
- ❌ Keine YouTube Playlists erstellt
- ❌ Videos sind nicht gruppiert
- ❌ Serien-Folgen sind verstreut

### 3. SEO-DEFIZITE
- ❌ Tags nicht standardisiert
- ❌ Descriptions ohne Chapters
- ❌ Keine End Screens konfiguriert

---

## ✅ OPTIMIERUNGS-STRATEGIE

### PHASE 1: TITEL-OPTIMIERUNG (Priorität HOCH)

#### Standard-Titelformat (≤70 Zeichen):
```
[Serien-Name]: [Titel] (Jahr) | 8K Restored
```

#### Beispiele:
| Aktuell | Optimiert |
|---------|-----------|
| `Ha! Ha! Ha! (1934) \| Betty Boop` | `Betty Boop: Ha! Ha! Ha! (1934) \| 8K` |
| `The Fast and the Furious (1954)` | `The Fast and the Furious (1954) \| 8K` |
| `Superman: Japoteurs (1942)` | `Superman: Japoteurs (1942) \| 8K Fleischer` |

#### Regeln:
1. **Serien-Videos:** `[Serie]: [Episode] (Jahr) | 8K`
2. **Spielfilme:** `[Filmtitel] (Jahr) | 8K Restored`
3. **Kompilationen:** `[Titel] Marathon | 8K Collection`
4. **IMMER:** Jahr in Klammern + Quality Tag

### PHASE 2: PLAYLISTS ERSTELLEN

#### Prioritäts-Playlists (API: playlistItems.insert = 50 units/video)

| Playlist | Videos | Quota Kosten |
|----------|--------|--------------|
| 🔴 Betty Boop Collection (1930-1939) | 25 | 1.250 |
| 🟡 Felix the Cat Classics | 12 | 600 |
| 🟢 Superman - Fleischer Studios | 9 | 450 |
| 🔵 Casper the Friendly Ghost | 8 | 400 |
| 🟣 Popeye Cartoons | 4 | 200 |
| ⚫ Silent Comedy Gold | 4 | 200 |
| 🎄 Christmas Specials | 12 | 600 |
| **TOTAL** | 74 | **3.700 units** |

### PHASE 3: SEO-TAGS BULK UPDATE

#### Nutzung: `videos.update` = 50 units pro Video

| Task | Videos | Quota |
|------|--------|-------|
| Tags für alle Videos | 124 | 6.200 |

**Problem:** Quota reicht nicht für alles!

---

## 💡 QUOTA-OPTIMIERTE STRATEGIE

### Option A: API-Priorisierung
```
Verfügbar: 10.000 units
- Playlists erstellen: ~500 (nur Playlist-Container)
- Videos zu Playlists: 3.700 (74 wichtigste)
- SEO Updates: 5.000 (100 Videos)
  TOTAL: ~9.200 units ✅
```

### Option B: YouTube Studio Bot (KEIN QUOTA!)
```
✅ Titel ändern: Browser-Automation
✅ Tags hinzufügen: Browser-Automation  
✅ Descriptions: Browser-Automation
❌ Playlists: Komplexe UI, API besser
```

### 🎯 EMPFEHLUNG: HYBRID-ANSATZ

1. **API für Playlists** (zuverlässiger)
2. **Bot für SEO-Updates** (quota-frei)

---

## 🚀 AKTIONS-PLAN (27.12.2025)

### MORGEN (09:00-12:00)

#### Schritt 1: Playlists via API erstellen
```bash
node scripts/youtube_playlist_creator.mjs
```
- playlists.insert: 50 units × 7 Playlists = 350 units
- playlistItems.insert: 50 units × 74 Videos = 3.700 units
- **Total: ~4.050 units**

#### Schritt 2: SEO-Bulk via YouTube Studio Bot
```bash
node scripts/youtube_studio_bot.mjs seo --force
```
- Titel optimieren
- Tags hinzufügen (min 20 pro Video)
- **Quota: 0 units** ✅

#### Schritt 3: Titel-Korrektur für 5 lange Titel
```bash
# Via API oder manuell in Studio
videos.update für 5 Videos = 250 units
```

### NACHMITTAG (14:00-18:00)

#### Schritt 4: Descriptions mit Chapters
- Nur für Kompilationen (Marathon-Videos)
- Via YouTube Studio Bot

#### Schritt 5: Audit & Verification
```bash
python scripts/youtube_full_audit.py
```

---

## 📝 VIDEO-NAMING-CONVENTION

### Format A: Serien (Cartoons)
```
[Serie]: [Episode-Titel] (Jahr) | 8K
```
**Max 70 Zeichen**

Beispiele:
- `Betty Boop: Snow White (1933) | 8K`
- `Superman: Japoteurs (1942) | 8K`
- `Felix: Oceantics (1930) | 8K`
- `Popeye: Ancient Fistory (1953) | 8K`

### Format B: Spielfilme
```
[Filmtitel] (Jahr) | 8K [Restored/Full Film]
```

Beispiele:
- `Nosferatu (1922) | 8K Restored`
- `Metropolis (1927) | 8K Full Film`
- `Great Expectations (1946) | 8K`

### Format C: Dokumentationen/Specials
```
[Titel] (Jahr) | 8K [Typ]
```

Beispiele:
- `Duck and Cover (1951) | 8K Documentary`
- `Berlin Symphony (1927) | 8K Documentary`

### Format D: Kompilationen
```
[Titel] Marathon | 8K Collection
```

Beispiele:
- `Charlie Chaplin Marathon | 8K Collection`
- `Betty Boop Marathon | 8K Collection`

---

## 🛠️ TOOLS & SCRIPTS

| Tool | Zweck | Quota |
|------|-------|-------|
| `youtube_studio_bot.mjs seo` | Bulk SEO Updates | 0 |
| `youtube_studio_bot.mjs playlists` | Playlist-Management | 0 |
| `youtube_playlist_creator.mjs` | Playlists via API | ~4.000 |
| `batch_seo_fix_all_videos.py` | Python SEO Batch | ~6.200 |
| `generate-youtube-metadata.mjs` | Metadata Templates | 0 |

---

## ✅ CHECKLISTE

### Heute erledigen:
- [ ] Playlists via API erstellen (7 Playlists)
- [ ] Videos in Playlists einsortieren
- [ ] 5 zu lange Titel kürzen
- [ ] SEO-Bot für Tags starten

### Diese Woche:
- [ ] Alle 124 Videos SEO-optimiert
- [ ] Chapters für Kompilationen
- [ ] Channel Sections einrichten
- [ ] Thumbnail-Audit

---

*Erstellt von Claude am 27.12.2025*
