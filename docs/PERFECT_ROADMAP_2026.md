# 🎯 PERFEKTE ROADMAP - remAIke_IT Channel Finale

> **Datum:** 2026-02-03
> **Ziel:** 100% YouTube 2026 Algo Compliance
> **Videos:** 308 public + 9 private/drafts = 317 total

---

## 📊 AKTUELLER STATUS

| Bereich | Status | Offen |
|---------|--------|-------|
| CTAs in Description | ✅ 100% | 0 |
| Tags vorhanden | ✅ 100% | 0 |
| Hashtags | ⚠️ 99% | 3 Videos |
| Titel <70 chars | ❌ 67% | **102 Videos** |
| Recording Locations | ❌ ~30% | ~200+ Videos |
| Recording Dates | ❌ 0% | 308 Videos |
| Channel Keywords | ❌ | Manuell |
| Channel Trailer | ❌ | Manuell |
| Auto-Chapters | ❌ | Manuell |

---

## 🔴 PHASE 1: KRITISCH - TITEL KÜRZEN (102 Videos)

### 1.1 Betty Boop (56 Videos) - HÖCHSTE PRIORITÄT!

**Problem:** Fast alle Betty Boop Titel sind zu lang
**Ursache:** Format `Betty Boop: [Episodentitel] ([Jahr]) | 8K HQ | @remAIke_IT`

**Lösung:** Kürzen auf max 70 chars
```
ALT:  Betty Boop: Minnie the Moocher (1932) | 8K HQ | @remAIke_IT (65 chars) ✅
ALT:  Betty Boop: Snow-White (1933) | Fleischer Studios | 8K | @remAIke_IT (73 chars) ❌

NEU:  Betty Boop: Snow-White (1933) | 8K | @remAIke_IT (52 chars) ✅
```

**Script benötigt:** `fix_betty_boop_titles.py`

### 1.2 Alfred J. Kwak (12 Videos)

**Problem:** Episode + Deutscher Titel zu lang
**Format aktuell:** `Alfred Jodokus Quack (14/52): Skrupellose Geschäfte | Deutsch | 8K HQ (...)`

**Lösung:**
```
NEU: Alfred J. Kwak E14: Skrupellose Geschäfte | 8K | @remAIke_IT (55 chars)
```

### 1.3 Felix the Cat (5 Videos)

**Problem:** Titel mit zu viel Detail
**Lösung:** Standardformat anwenden

### 1.4 Soundies (5 Videos)

**Problem:** Artist + Song + "Soundie (1940s)" + 8K + @remAIke_IT zu lang
**Lösung:**
```
NEU: Louis Armstrong: Musical Review | Soundie | 8K | @remAIke_IT (55 chars)
```

### 1.5 Other (24 Videos)

Individuelle Prüfung und Kürzung

---

## 🟡 PHASE 2: DESCRIPTIONS - Hashtags (3 Videos)

### Videos ohne Hashtags:
1. `EZxg1D958mo` - A Corny Concerto (1943)
2. `2nT_DjkOWn8` - Pigs In A Polka (1943)
3. `0ZT_5BmyixM` - A Tale Of Two Kitties (1942)

**Lösung:** Hashtag-Block am Ende hinzufügen:
```
#LooneyTunes #WB #VintageCartoons #8K #PublicDomain #remAIke
```

---

## 🟢 PHASE 3: RECORDING DETAILS (Nach Quota Reset)

### 3.1 Recording Locations

**Priorität nach Content:**

| Serie | Videos | Location-Typ |
|-------|--------|--------------|
| Wochenschau | ~25 online + 252 DB | Historische Orte ✅ FERTIG |
| Soundies | 48 | New York, USA |
| Betty Boop | 67 | New York, USA (Fleischer Studios) |
| Alfred J. Kwak | 36 | Amsterdam, NL (TELESCREEN) |
| Felix the Cat | 13 | New York, USA |
| Superman | ? | New York, USA (Fleischer) |
| Maulwurf | 7 | Prague, CZ |
| Other | ~100 | Individuell |

**Script:** `set_recording_locations.py` (bereits erstellt, ~90 Videos done)

### 3.2 Recording Dates

**Priorität nach Content:**

| Serie | Recording Date |
|-------|---------------|
| Betty Boop | 1930-1939 (aus Titel) |
| Wochenschau | 1939-1945 (aus DB) ✅ |
| Soundies | 1940-1947 |
| Alfred J. Kwak | 1989-1991 |
| Felix | 1919-1930 |
| Maulwurf | 1957-2002 |

---

## 🔵 PHASE 4: MANUELLE AKTIONEN (YouTube Studio)

### 4.1 Channel Keywords setzen
**Wo:** YouTube Studio → Customization → Basic Info → Keywords

**Empfohlene Keywords:**
```
"8K" "AI Upscaling" "Public Domain" "Vintage Animation" "Classic Cartoons" 
"Betty Boop" "Wochenschau" "WWII" "1930s" "1940s" "remAIke" "Soundies" 
"Felix the Cat" "Alfred Jodokus Kwak" "8K Restaurierung"
```

### 4.2 Channel Trailer setzen
**Empfehlung:** Bestes/populärstes Video als Trailer
- Option A: Betty Boop "Minnie the Moocher" (bekannt)
- Option B: Boxing Cats (viral-potenzial)
- Option C: Neues Intro-Video erstellen (60-90 Sek)

### 4.3 Auto-Chapters aktivieren
**Wo:** YouTube Studio → Settings → Upload Defaults → Advanced
**Aktion:** "Allow automatic chapters" aktivieren

### 4.4 Stichproben-Verifizierung
- [ ] 5 random Videos prüfen
- [ ] Recording Location angezeigt?
- [ ] Alle Metadaten korrekt?

---

## 📋 VOLLSTÄNDIGE TODO-LISTE

### SCRIPTS ZU ERSTELLEN

| # | Script | Zweck | Prio |
|---|--------|-------|------|
| 1 | `fix_betty_boop_titles.py` | 56 Titel kürzen | 🔴 |
| 2 | `fix_alfred_titles.py` | 12 Titel kürzen | 🔴 |
| 3 | `fix_felix_titles.py` | 5 Titel kürzen | 🟡 |
| 4 | `fix_soundies_titles.py` | 5 Titel kürzen | 🟡 |
| 5 | `fix_other_titles.py` | 24 Titel kürzen | 🟡 |
| 6 | `add_hashtags_3videos.py` | 3 Hashtags hinzufügen | 🟢 |
| 7 | `set_recording_dates.py` | Dates setzen | 🟢 |

### SCRIPTS BEREITS VORHANDEN

| Script | Status |
|--------|--------|
| `set_recording_locations.py` | ✅ ~90 Videos done |
| `set_wochenschau_recording_details.py` | ✅ Ready |
| `wochenschau_final_locations.py` | ✅ 252 Locations |
| `full_channel_audit_2026.py` | ✅ Audit-Tool |

### MANUELLE AUFGABEN

| # | Aufgabe | Wo | Zeit |
|---|---------|-----|------|
| M1 | Channel Keywords | Studio | 5 min |
| M2 | Channel Trailer | Studio | 5 min |
| M3 | Auto-Chapters | Studio | 2 min |
| M4 | Stichproben-Check | Studio | 15 min |

---

## ⏱️ ZEITPLAN

### Tag 1 (HEUTE)
- [x] Vollständiges Audit ✅
- [x] Roadmap erstellen ✅
- [ ] Script: fix_betty_boop_titles.py erstellen
- [ ] Betty Boop Titel fixen (DRY RUN)

### Tag 2
- [ ] Betty Boop Titel fixen (LIVE)
- [ ] Alfred J. Kwak Titel fixen
- [ ] Felix/Soundies/Other Titel fixen
- [ ] 3 Hashtags hinzufügen

### Tag 3 (Nach Quota Reset)
- [ ] Recording Locations (Batch 1: 100 Videos)
- [ ] Recording Dates (Batch 1: 100 Videos)

### Tag 4
- [ ] Recording Locations (Batch 2: 100 Videos)
- [ ] Recording Dates (Batch 2: 100 Videos)

### Tag 5
- [ ] Restliche Recording Details
- [ ] Manuelle Studio-Aufgaben
- [ ] Final Verification

---

## 🎯 ERFOLGS-KRITERIEN

### Minimum (Must-Have)
- [ ] Alle Titel <70 chars (0/102 done)
- [ ] Alle Videos mit Hashtags (305/308 done)
- [ ] Channel Keywords gesetzt
- [ ] Auto-Chapters aktiviert

### Optimal (Nice-to-Have)
- [ ] Recording Locations 100%
- [ ] Recording Dates 100%
- [ ] Channel Trailer gesetzt
- [ ] Video Localizations (API)

### Perfekt (Future)
- [ ] Chapters für alle Videos >5 min
- [ ] End Screens konfiguriert
- [ ] Cards zwischen Videos
- [ ] Community Posts

---

## 📊 CONTENT-VERTEILUNG NACH SERIE

| Serie | Videos | Status |
|-------|--------|--------|
| Betty Boop | 67 | ❌ 56 Titel zu lang |
| Soundies | 48 | ⚠️ 5 Titel zu lang |
| Alfred J. Kwak | 36 | ⚠️ 12 Titel zu lang |
| Felix the Cat | 13 | ⚠️ 5 Titel zu lang |
| Wochenschau | 9-25 | ✅ SEO perfekt |
| Christmas | 7 | ✅ |
| Maulwurf | 7 | ✅ Titel gefixt |
| Looney Tunes | 3 | ⚠️ 3 ohne Hashtags |
| Documentary | 2 | ✅ |
| Other/Misc | 123 | ⚠️ 24 Titel zu lang |

---

## 🔧 QUOTA-MANAGEMENT

**Daily Quota:** 10.000 Units
**Reset:** 08:00 UTC (09:00 MEZ)

| Operation | Units | Max/Tag |
|-----------|-------|---------|
| videos.list | 1 | 10.000 |
| videos.update | 50 | 200 |
| search.list | 100 | 100 |

**Strategie:**
- Titel-Updates: 50 Units × 102 = 5.100 Units (1 Tag)
- Location-Updates: 50 Units × 300 = 15.000 Units (2 Tage)
- Date-Updates: parallel mit Location möglich

---

*Roadmap erstellt: 2026-02-03 | remAIke.TV*
