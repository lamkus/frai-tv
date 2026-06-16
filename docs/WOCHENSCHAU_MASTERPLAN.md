# 📺 WochenschauTV — MASTERPLAN & STATUS

> **Stand: 2026-02-28 | REAL FILESYSTEM SCAN + ffprobe Auflösungsanalyse**
> **Datenquelle:** `config/wochenschau_real_scan.json` (1752 Dateien, ffprobe-verifiziert)

---

## 📊 GESAMTÜBERSICHT

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WOCHENSCHAUTV — 258 EPISODEN GEFUNDEN (Nr. 459–755)                    │
│  1752 Video-Dateien auf 4 Laufwerken (V:\ D:\ E:\ Y:\)                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Auflösung → Pipeline-Status (BESTER Status pro Episode):              │
│                                                                         │
│  ✅ 4K RENDERED (3840×2160, HUD v3):     60 Episoden  (23.3%)          │
│  ⬆️  8K UPSCALED (7680×4320, Topaz):      16 Episoden  ( 6.2%)          │
│  🔶 QHD PARTIAL (2560-2880px):            22 Episoden  ( 8.5%)          │
│  🟡 FHD SOURCE (1920×1080):              16 Episoden  ( 6.2%)          │
│  🟠 HD SOURCE (1280-1440×1080):          25 Episoden  ( 9.7%)          │
│  🔴 SD ORIGINAL (320-854px):            119 Episoden  (46.1%)          │
│                                                                         │
│  KEIN Video hat KEINE Quelle!                                           │
│  ALLE 258 Episoden sind auf mindestens einem Laufwerk vorhanden!       │
│                                                                         │
│  ████████████████████████████████████████████████████  258/258 QUELLEN  │
│  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   60/258 FERTIG   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ QUELLENBESTAND — ALLE LAUFWERKE (ffprobe-verifiziert)

### V:\ — HAUPTARCHIV (10 TB, 1066 Videos)

| Verzeichnis | Dateien | Haupttyp | Zweck |
|-------------|---------|----------|-------|
| `V:\MediaArchive\DeutscheWochenschau` | 153 | 64×QHD, 40×8K, 24×HD, 12×FHD | Upscale-Archiv (SLS+Topaz) |
| `V:\OriginalSources\...\Wochenschau` | 251 | 246×SD, 5×QHD | Originalquellen (Archive.org etc) |
| `V:\OriginalSources\...\Wochenschau_Certified` | 285 | 256×SD, 13×FHD, 11×HD, 5×QHD | Verifizierte Quellen |
| `V:\OriginalSources\...\Wochenschau_Backup` | 67 | 67×SD | Backup-Kopien |
| `V:\OriginalSources\...\Wochenschau_WICHTIG` | 36 | 33×SD, 2×QHD, 1×HD | Prioritäts-Quellen |
| `V:\TopazPipeline\Input\Wochenschau` | 274 | 248×SD, 12×FHD, 9×HD, 5×QHD | Topaz-Warteschlange |

### D:\ — PROJEKT (40+40 Renders)

| Verzeichnis | Dateien | Typ | Zweck |
|-------------|---------|-----|-------|
| `D:\remaike.TV\wochenschau_rendered` | 40 | 40×4K | **HUD v3 Renders (aktuell)** |
| `D:\remaike.TV\watch\wochenschau_stream` | 40 | 40×4K | Stream-Kopien |
| `D:\remaike.TV\watch\wochenschau_rendered` | 31 | 29×4K, 1×FHD, 1×FAIL | Ältere Renders |
| `D:\remaike.TV\watch\wochenschau_rendered_v2` | 3 | 2×FAIL, 1×4K | Test-Renders |

### E:\ / Y:\ — OUTPUT (identische Spiegel!)

| Verzeichnis | Dateien | Typ | Zweck |
|-------------|---------|-----|-------|
| `E:\wochenschau_rendered` = `Y:\wochenschau_rendered` | 20 | 20×4K | **HUD v3 Renders (E-only)** |
| `E:\_OUTPUT\WochenschauStrike` = `Y:\_OUTPUT\WochenschauStrike` | 63 | 62×8K, 1×QHD | **8K Upscaled (Strike-Batch)** |
| `E:\_OUTPUT\wochenschaurest` = `Y:\_OUTPUT\wochenschaurest` | 203 | 150×SD, 23×QHD, 16×HD, 13×FHD, 1×4K | Restliche Quellen (gemischt) |

> **E:\ und Y:\ sind Spiegel** — identische Dateien, identische Größen.

---

## 📐 AUFLÖSUNGS-VERTEILUNG (alle 1752 Dateien)

| Auflösung | Dateien | Speicher | Bedeutung |
|-----------|---------|----------|-----------|
| **8K** (7680×4320) | 164 | 1.379 GB | Topaz/SLS Upscale → bereit für HUD-Render |
| **4K** (3840×2160) | 154 | 479 GB | HUD v3 gerendert → Stream/Upload-ready |
| **QHD** (2560-2880px) | 129 | 1.004 GB | Teilupscale (SLS ohne Topaz Enhance?) |
| **FHD** (1920×1080) | 64 | 90 GB | Full HD Quelle |
| **HD** (1280-1440×1080) | 77 | 89 GB | HD Quelle |
| **SD** (<1280px) | 1.152 | 128 GB | Original (unbearbeitet) |
| ffprobe failed | 12 | 34 GB | Korrupte/unlesbare Dateien |
| **GESAMT** | **1.752** | **3.203 GB** | |

---

## 📺 YOUTUBE STATUS (aus vorherigem API-Audit)

| Metrik | Wert |
|--------|------|
| **Gesamt auf YouTube** | 72 Episoden |
| Davon Public | 68 |
| Davon Private | 4 (Nr. 492, 493, 513, 524) |
| **Im 24/7 Stream** | 3 (Nr. 471, 473, 491) |
| **Category 27 (Education)** | ✅ 100% |
| **8K im Titel** | ✅ 100% |
| **4K im Titel** | ⚠️ 1 fehlt (Nr. 516) |

---

## 🎯 PIPELINE-STATUS PRO EPISODE

### ✅ 4K RENDERED — 60 Episoden (FERTIG für Stream/Upload)

```
459, 468, 470, 471, 473, 477, 480, 482, 483, 488, 491, 492, 493, 496,
502, 504, 505, 506, 508, 509, 512, 513, 514, 515, 518, 519, 520, 522,
523, 542, 543, 544, 545, 547, 548, 550, 552, 553, 554, 555, 556, 565,
567, 569, 573, 605, 606, 607, 652, 654, 720, 721, 722, 746, 749, 750,
751, 752, 753, 754
```

### ⬆️ 8K UPSCALED — 16 Episoden (braucht NUR HUD-Render)

```
511, 516, 521, 524, 697, 699, 700, 701, 703, 704, 705, 706, 707, 708, 709, 710
```
→ 1x `render_v3.py` Durchlauf = fertig!

### 🔶 QHD PARTIAL — 22 Episoden (Teilupscale, braucht Topaz Enhance + Render)

```
507, 525, 528, 530, 531, 533, 534, 536, 537, 538, 539, 564, 602, 690,
692, 698, 711, 712, 713, 715, 723, 755
```

### 🟡 FHD SOURCE — 16 Episoden (braucht Upscale + Render)

```
532, 549, 580, 581, 604, 608, 617, 629, 637, 650, 653, 657, 660, 665, 691, 693
```

### 🟠 HD SOURCE — 25 Episoden (braucht Upscale + Render)

```
472, 497, 499, 517, 526, 529, 546, 557, 562, 566, 568, 570, 574, 576,
610, 641, 645, 655, 677, 694, 702, 717, 725, 747, 748
```

### 🔴 SD ORIGINAL — 119 Episoden (braucht Upscale + Render)

```
474, 510, 527, 561, 571, 572, 575, 577, 578, 579, 582, 583, 584, 585,
586, 587, 588, 589, 590, 592, 593, 594, 595, 596, 598, 599, 600, 601,
609, 611, 612, 613, 614, 615, 616, 618, 619, 620, 621, 622, 623, 624,
625, 627, 628, 630, 631, 632, 633, 634, 635, 638, 639, 640, 642, 643,
644, 646, 647, 648, 649, 651, 656, 658, 659, 661, 662, 663, 664, 666,
667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 678, 679, 680, 681,
682, 683, 684, 685, 686, 687, 688, 689, 695, 696, 714, 716, 718, 719,
724, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738,
739, 740, 741, 742, 743, 744, 745
```

---

## 🎯 AKTIONSPLAN (nach Priorität)

### 🔴 P1: Stream erweitern — 3 → 60 Episoden!

**Problem:** Der 24/7 Stream hat NUR 3 Episoden. Es gibt **60 fertige 4K-Renders!**

**Aktion:**
1. Copyright-Claims für alle 60 gerenderten Episoden prüfen
2. Alle claim-freien Episoden in `stream_4k.py → ALL_EPISODES` aufnehmen
3. Stream neu starten

**Impact:** Von ~5 Min Schleife → ~100h Programm!

---

### 🔴 P2: 16 Episoden 8K→4K rendern (nur HUD-Overlay!)

Diese 16 Episoden haben bereits **8K Topaz Output** — brauchen NUR den HUD-Render:

```
511, 516, 521, 524, 697, 699, 700, 701, 703, 704, 705, 706, 707, 708, 709, 710
```

**Aktion:** In `render_v3.py → ALL_EPISODES` aufnehmen, Quellpfade prüfen, rendern.
**Ergebnis:** 60 + 16 = **76 fertige Episoden!**

---

### 🟡 P3: 22 QHD-Episoden durch Topaz Enhance auf 8K bringen

Die 22 QHD-Episoden (2560-2880px) sind **teilweise upscaled** (SLS-Output ohne Topaz Enhance):

```
507, 525, 528, 530, 531, 533, 534, 536, 537, 538, 539, 564, 602, 690,
692, 698, 711, 712, 713, 715, 723, 755
```

**Aktion:** Topaz Video AI → 8K Enhance → HUD Render
**Ergebnis:** 76 + 22 = **98 Episoden!**

---

### 🟡 P4: 41 HD/FHD-Episoden upscalen

16 FHD + 25 HD = 41 Episoden mit brauchbarer Ausgangsqualität:

**Aktion:** Topaz Pipeline (FHD/HD → 8K) → HUD Render
**Ergebnis:** 98 + 41 = **139 Episoden!**

---

### 🟡 P5: 20 HUD-Kontexte erstellen

20 Episoden in der Render-Pipeline haben nur generischen Fallback-Overlay:

```
491, 492, 493, 496, 504, 505, 506, 552, 553, 554, 555, 556, 565, 567,
569, 605, 606, 607, 749, 752
```

**Aktion:** `config/wochenschau_hud_context.json` erweitern (era, title, context, exact_date, location)

---

### 🟢 P6: 119 SD-Episoden upscalen (Langfrist-Bulk)

Alle 119 SD-Originalquellen durch die volle Pipeline:
SD (320-854px) → Topaz 8K → HUD Render

**Ergebnis:** 139 + 119 = **258 Episoden KOMPLETT!**

---

### 🟢 P7: YouTube SEO & Compliance

| Nr | Problem | Fix |
|----|---------|-----|
| 516 | Kein "4K" im Titel | `8K HQ (4K UHD)` ergänzen |
| 492, 493, 513 | Private (haben Render) | Public setzen? |
| 524 | Private (8K vorhanden) | Public nach Render? |

---

## 📋 QUICK WINS (heute machbar)

| # | Aktion | Aufwand | Impact |
|---|--------|---------|--------|
| 1 | **Stream**: 60 Episoden in stream_4k.py | 15 Min | ×20 Programmlänge |
| 2 | **Render**: 16× 8K→4K (nur HUD) | 1 Render-Session | +16 Episoden |
| 3 | **SEO**: Nr. 516 Titel fixen | 2 Min | 100% Compliance |
| 4 | **HUD**: 20 Kontexte schreiben | 1-2 Std | Overlay-Qualität ↑ |

---

## 🏗️ TV-CHANNEL AUFBAUPLAN (Roadmap)

### Phase 1: SOFORT (diese Woche) → 76 Episoden
- [ ] Stream auf 60 Episoden erweitern
- [ ] 16 × 8K→4K HUD-Render (Topaz OUTPUT liegt bereit!)
- [ ] Nr. 516 Titel fixen
- [ ] RTX 3090 installieren

### Phase 2: KURZFRISTIG (2-4 Wochen) → 98 Episoden
- [ ] 22 × QHD → Topaz Enhance → 8K → HUD Render
- [ ] 20 HUD-Kontexte erstellen
- [ ] 4 Private Videos entscheiden

### Phase 3: MITTELFRISTIG (1-3 Monate) → 139 Episoden
- [ ] 41 × HD/FHD → Topaz 8K → HUD Render
- [ ] HUD-Kontexte für ALLE neuen Episoden
- [ ] YouTube-Uploads der neuen Renders

### Phase 4: LANGFRISTIG (3-6 Monate) → 258 Episoden KOMPLETT
- [ ] 119 × SD → Topaz 8K → HUD Render
- [ ] 24/7 Stream mit 258 × ~15 Min = ~65h Programm
- [ ] Monetarisierung (YPP bei 4.000h Watch Time)

---

## ⚠️ DUPLIKATE & SPEICHER

- **258 Episoden haben im Schnitt 6-7 Kopien** (Original, Backup, Certified, Pipeline, Rendered...)
- **E:\ und Y:\ sind identisch** — 286 doppelte Dateien!
- **105 Dateien ohne Episodennummer** (Archiv-Footage: D-Day, Eva Braun, Apollo etc.)
- **12 Dateien ffprobe-Fehler** (korrupt oder unvollständig)

---

## 📁 REFERENZ-DATEIEN

| Datei | Inhalt |
|-------|--------|
| `config/wochenschau_real_scan.json` | **REAL Filesystem Scan (1752 Dateien, ffprobe)** |
| `config/wochenschau_mega_audit.json` | YouTube API + Config Cross-Reference |
| `config/wochenschau_complete_upload_database.json` | Upload-Metadaten (252 Episoden, 14 Sprachen) |
| `config/wochenschau_events.json` | Events + Daten (252 Episoden) |
| `config/wochenschau_complete_locations.json` | Orte + Koordinaten (252 Episoden) |
| `config/wochenschau_hud_context.json` | Reicher HUD-Overlay-Kontext (40 Episoden) |
| `render_v3.py` | HUD v3 Render-Pipeline (60 Episoden → erweitern!) |
| `stream_4k.py` | 24/7 Stream Engine (3 Episoden → erweitern!) |
| `scripts/youtube/wochenschautv.py` | Core Engine (1695 Zeilen, build_timeline_filters) |
| `docs/RENDER_SERVER_PACKAGE.md` | Render-Server Dokumentation |
