# 🎬 Shorts Upload Guide — remAIke.TV

> **Stand:** 2026-02-09
> **Status:** 14 Shorts upload-ready, 5 bereits hochgeladen
> **Metadata:** `config/shorts_upload_metadata.json` (14/14 validiert, 0 Fehler)

---

## 📊 Übersicht

| Status | Anzahl | Typ |
|--------|--------|-----|
| ✅ Bereits hochgeladen | 5 | Art Shorts (SEO fixed) |
| 📦 Upload-ready | 9 | Art Shorts |
| 📦 Upload-ready | 5 | Showcase Shorts |
| **Gesamt** | **19** | |

### Bereits auf YouTube (5)
| Video ID | Short | Typ |
|----------|-------|-----|
| `3v9UcdpzljE` | Skeleton Dance Full | CINEMA 60s |
| `SgZMhKpnrEw` | Skeleton Rib Solo | IMPACT 13s |
| `DiTBoIhQxio` | Frankenstein Creation | CINEMA 60s |
| `fW1ezUhg5-8` | Duck and Cover Loop | HYPNO 13s |
| `vN9da73UhOI` | Betty Cab Calloway | CINEMA 60s |

---

## 📋 Upload-Reihenfolge (empfohlen)

### Welle 1 — Maximum Impact (Tag 1-3)
> Die stärksten Hooks zuerst — Algorithmus testen

| # | Datei | Titel | Dauer | Prio |
|---|-------|-------|-------|------|
| 1 | `SHORT_frankenstein_face_IMPACT.mp4` | Frankenstein's Monster — First Face Reveal (1910) \| 8K | 13s | 🔴 |
| 2 | `SHORT_superman_beam_IMPACT.mp4` | Superman vs Death Ray — Fleischer (1941) \| 8K | 13s | 🔴 |
| 3 | `SHORT_superman_flying_CINEMA.mp4` | Superman Flying Through Metropolis (1941) \| 8K | 60s | 🔴 |
| 4 | `SHOWCASE_01_impossible_upscale.mp4` | 176p → 8K: The Impossible Upscale \| remAIke | 18s | 🔴 |
| 5 | `SHOWCASE_02_faces_reborn.mp4` | Faces Reborn in 8K — 100+ Years Later \| remAIke | 20s | 🔴 |
| 6 | `SHOWCASE_05_best_of_remaike.mp4` | Best of remAIke — 8K Restorations in 25 Seconds | 26s | 🔴 |

### Welle 2 — Diversifizierung (Tag 4-7)
> Verschiedene Genres/Themen testen

| # | Datei | Titel | Dauer | Prio |
|---|-------|-------|-------|------|
| 7 | `SHORT_atom_detonation_IMPACT.mp4` | Nuclear Blast — Yucca Flat (1953) ☢️ \| 8K | 13s | 🟡 |
| 8 | `SHORT_betty_skeleton_army_IMPACT.mp4` | Betty Boop: Skeleton Army March 💀 (1932) \| 8K | 13s | 🟡 |
| 9 | `SHORT_melies_moon_loop_HYPNO.mp4` | Moon Eats the Astronomer — Méliès Loop (1898) \| 8K | 13s | 🟡 |
| 10 | `SHOWCASE_03_animation_restored.mp4` | Classic Cartoons Restored to 8K \| remAIke | 20s | 🟡 |
| 11 | `SHOWCASE_04_history_in_8k.mp4` | History in 8K — Documentary Restoration \| remAIke | 20s | 🟡 |

### Welle 3 — Loops & Filler (Tag 8-10)
> Ergänzende Loops für Engagement

| # | Datei | Titel | Dauer | Prio |
|---|-------|-------|-------|------|
| 12 | `SHORT_atom_mushroom_CINEMA.mp4` | Mushroom Cloud Formation — Full Sequence (1953) \| 8K | 60s | 🟢 |
| 13 | `SHORT_skeleton_xylophone_loop_HYPNO.mp4` | Skeleton Xylophone Loop 🦴🎵 (1929) \| 8K | 13s | 🟢 |
| 14 | `SHORT_betty_rotoscope_loop_HYPNO.mp4` | Cab Calloway Rotoscope Ghost Dance (1932) \| 8K | 13s | 🟢 |

---

## 🔧 Upload-Anleitung (YouTube Studio)

### Schritt für Schritt

1. **YouTube Studio öffnen:** https://studio.youtube.com
2. **Erstellen → Video hochladen**
3. **Datei auswählen** aus `D:\remaike.TV\output\shorts\` bzw. `...\showcase\`
4. **Titel** aus `config/shorts_upload_metadata.json` kopieren
5. **Beschreibung** aus JSON kopieren
6. **Tags** aus JSON kopieren (kommagetrennt einfügen)
7. **Kategorie** setzen:
   - `1` = Film & Animation (Cartoons)
   - `27` = Education (Atom/Wochenschau)
   - `28` = Science & Technology (Showcase/Technik)
8. **Nicht für Kinder** = Ja (madeForKids = false)
9. **Sichtbarkeit** = Öffentlich (oder Geplant)

### ⚠️ Shorts-Erkennung
- YouTube erkennt Shorts automatisch an **9:16 Aspect Ratio**
- `#Shorts` Hashtag ist **NICHT nötig** (seit 2025)
- Max Duration: 3 Minuten (alle unsere sind ≤60s ✅)

### 📅 Upload-Timing (Best Practices 2026)
- **Optimal:** 2-3 Shorts pro Tag, über mehrere Tage verteilt
- **Beste Zeiten:** 14:00-16:00 MEZ (US wacht auf + EU nachmittags)
- **NICHT:** Alle 14 auf einmal hochladen (Algorithmus bevorzugt Konsistenz!)
- **Frequenz:** Mind. 200 Shorts für konsistentes Wachstum (siehe copilot-instructions)

---

## 📁 Dateipfade

```
Quellen:
  D:\remaike.TV\output\shorts\SHORT_*.mp4          (9 Art Shorts)
  D:\remaike.TV\output\shorts\showcase\SHOWCASE_*.mp4  (5 Showcase Shorts)

Metadata:
  D:\remaike.TV\config\shorts_upload_metadata.json  (14 Shorts, validiert)

Referenz (bereits uploaded):
  D:\remaike.TV\scripts\shorts\fix_shorts_seo.py    (5 uploaded Shorts + IDs)
```

---

## 📈 Erwartete Performance

| Typ | Anzahl | Loop-Potential | Viral-Chance |
|-----|--------|---------------|--------------|
| IMPACT (13s) | 5 | ★★★★★ (auto-loop!) | Hoch |
| CINEMA (60s) | 2 | ★★★ | Mittel-Hoch |
| HYPNO (13s) | 3 | ★★★★★ (designed for loops) | Mittel |
| SHOWCASE (18-26s) | 5 | ★★★★ | Hoch (Before/After!) |

### Warum diese Shorts funktionieren werden:
1. **13s IMPACT/HYPNO** = Auto-Loop → Views multiplizieren sich
2. **Before/After SHOWCASE** = Hochgrades Engagement-Format auf Shorts
3. **Superman/Frankenstein/Betty Boop** = Bekannte IP mit Suchvolumen
4. **Atomtests** = Trending Content (History-Nische boomt)
5. **Méliès 1898** = "Ältester Film ever" Click-Magnet

---

## ✅ Checkliste pro Upload

- [ ] Datei hochgeladen (9:16 vertical)
- [ ] Titel aus JSON kopiert (≤70 Zeichen, 8K enthalten)
- [ ] Beschreibung aus JSON kopiert (CTA + Links vorhanden)
- [ ] Tags eingefügt (≤15 Tags)
- [ ] Kategorie korrekt gesetzt
- [ ] madeForKids = Nein
- [ ] Thumbnail: Standard (YouTube generiert bei Shorts)
