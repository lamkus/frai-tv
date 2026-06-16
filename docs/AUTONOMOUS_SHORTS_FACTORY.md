# 🏗️ AUTONOMOUS SHORTS FACTORY — Machbarkeitsanalyse & Implementierungsplan

> **Stand:** 2026-02-08  
> **Ziel:** Localhost soll ohne Copilot eigenständig Shorts generieren, optimieren und hochladen.  
> **Hardware-Angebot:** RTX 3090 steht zur Einbau bereit.

---

## 📊 IST-ZUSTAND: Was haben wir?

### Hardware (Localhost)

| Komponente | IST | Bewertung |
|------------|-----|-----------|
| **CPU** | i9-11900K (8C/16T, 3.5 GHz) | ✅ Stark für FFmpeg |
| **RAM** | 48 GB DDR4 | ✅ Reicht für 8K Decode |
| **GPU** | GeForce GT 710 (2 GB VRAM) | ❌ Unbrauchbar für Encoding |
| **Mainboard** | ASUS ROG Maximus XIII Hero (Z590) | ✅ PCIe 4.0 x16 Slot frei |
| **Storage** | C: 953GB (73 frei) / D: 1.8TB (137 frei) / E: 3.7TB (1.6TB frei) | ✅ Genug Platz |
| **OS** | Windows | ✅ |
| **FFmpeg** | Installiert, NVENC-fähig (h264/hevc/av1) | ✅ GPU-ready sobald 3090 drin |

### Software (bereits vorhanden)

| Komponente | Status | Pfad |
|------------|--------|------|
| **Shorts FFmpeg Pipeline** | ✅ 790 Zeilen, 5 Art-Modi | `scripts/shorts/create_art_shorts.py` |
| **YouTube Upload (resumable)** | ✅ Retry, Healthcheck | `code/backend/scripts/auto_upload.py` |
| **SEO Optimizer** | ✅ Category-Templates | `code/backend/scripts/perfect_upload.py` |
| **Admin Dashboard** | ✅ Express + WebSocket | `code/admin/` (Port 3333) |
| **Backend API** | ✅ Express + Prisma | `code/backend/` (Port 10000) |
| **Scheduler** | ⚠️ Fragmentiert (4 Systeme) | node-cron, Windows Task, PM2, manual |
| **File Watcher** | ✅ watchdog | `code/backend/scripts/auto_upload.py` |
| **Database** | ✅ Prisma + PostgreSQL | `code/backend/prisma/schema.prisma` |

### Fehlende Bausteine

| Gap | Kritikalität | Aufwand |
|-----|-------------|---------|
| **GPU für Encoding** | 🔴 Hoch | Hardware-Einbau (1h) |
| **Unified Orchestrator** | 🔴 Hoch | ~400 Zeilen Python |
| **Scene Detection (PySceneDetect)** | 🟡 Mittel | pip install + Config |
| **Shorts Queue + State Machine** | 🟡 Mittel | ~300 Zeilen + DB-Schema |
| **Dashboard Extension** | 🟢 Niedrig | React-Komponente |

---

## 🎯 RTX 3090 IMPACT-ANALYSE

### Vorher (GT 710) vs Nachher (RTX 3090)

| Operation | GT 710 (CPU-Only) | RTX 3090 | Speedup |
|-----------|-------------------|----------|---------|
| 8K→1080p Decode+Scale (13s Short) | ~45 Sek | ~3 Sek | **15x** |
| 8K→1080p Decode+Scale (60s Short) | ~3.5 Min | ~12 Sek | **17x** |
| Color Grading (filter_complex) | ~30 Sek | ~2 Sek (CUDA) | **15x** |
| HEVC Encode (CRF 18) | ~2 Min/Short | ~8 Sek (NVENC) | **15x** |
| **Batch 14 Shorts** | **~45 Min** | **~3 Min** | **15x** |
| ONNX AI Upscale (optional) | ❌ Unmöglich | ~30 Sek/Frame | ∞ |
| PySceneDetect (8K Source) | ~10 Min/Video | ~40 Sek/Video | **15x** |

### 3090 Specs die relevant sind:
- **24 GB VRAM** → Kann 8K Frames im VRAM halten
- **NVENC** → Hardware-Encoding H.264/HEVC/AV1
- **NVDEC** → Hardware-Decoding HEVC (8K Sources)
- **10496 CUDA Cores** → FFmpeg CUDA-Filter, PySceneDetect
- **PCIe 4.0 x16** → Passt ins Maximus XIII Hero
- **350W TDP** → PSU muss min. 750W haben (prüfen!)

### ⚠️ VOR EINBAU PRÜFEN:
1. **Netzteil:** Mindestens 750W? (i9-11900K = 125W + 3090 = 350W + Rest)
2. **PCIe Slot:** x16 Slot frei? (GT 710 raus, 3090 rein)
3. **Gehäuse:** 3090 ist 313mm lang — passt das?
4. **Stromkabel:** 2x 8-Pin PCIe Power vorhanden?

---

## 🏭 ARCHITEKTUR: Autonomous Shorts Factory

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHORTS FACTORY (Localhost)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  📁 SOURCE    │    │  🧠 BRAIN     │    │  📤 UPLOAD    │      │
│  │  SCANNER     │───▶│  ORCHESTRATOR│───▶│  PIPELINE    │      │
│  │              │    │              │    │              │      │
│  │  • V:\ Scan  │    │  • Queue     │    │  • OAuth     │      │
│  │  • ffprobe   │    │  • State     │    │  • Resumable │      │
│  │  • Duration  │    │  • Schedule  │    │  • SEO Auto  │      │
│  │  • Resolution│    │  • Decisions │    │  • Quota Mgmt│      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                             │                                   │
│  ┌──────────────┐    ┌──────▼───────┐    ┌──────────────┐      │
│  │  🔍 SCENE     │    │  🎬 RENDER    │    │  📊 DASHBOARD │      │
│  │  DETECTOR    │◀──▶│  ENGINE      │    │  (Admin UI)  │      │
│  │              │    │              │    │              │      │
│  │  • PySceD    │    │  • FFmpeg    │    │  • Queue View│      │
│  │  • Adaptive  │    │  • NVENC 3090│    │  • Status    │      │
│  │  • Best Shots│    │  • 5 Art Modi│    │  • History   │      │
│  │  • Thumbnails│    │  • 9:16 Crop │    │  • Manual    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  💾 DATABASE (Prisma/PostgreSQL)                          │   │
│  │  • shorts_queue (state machine)                          │   │
│  │  • scene_cache (detected best scenes per source)         │   │
│  │  • upload_history (what was published when)              │   │
│  │  • quota_tracker (daily API usage)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 WORKFLOW: Fully Autonomous

```
Täglich um 03:00 Uhr:

1. SOURCE SCANNER
   ├─ Scannt V:\OriginalSources\Final\nyx8kexportupscale\
   ├─ Vergleicht mit DB → findet NEUE oder UNBEARBEITETE Sources
   ├─ ffprobe: Resolution, Duration, Codec
   └─ Markiert als "scan_complete"

2. SCENE DETECTOR (GPU-beschleunigt)
   ├─ PySceneDetect mit AdaptiveDetector (luma_only für B&W)
   ├─ Findet Top-10 visuell stärkste Szenen pro Source
   ├─ Exportiert Thumbnail-Frames als JPG
   ├─ Bewertet: Motion Energy, Kontrast, Komposition
   └─ Speichert in scene_cache DB

3. ORCHESTRATOR (Entscheidungen)
   ├─ Wählt beste Szenen basierend auf:
   │   ├─ Visuelle Qualität (Scene Score)
   │   ├─ Diversität (nicht 5x Skeleton Dance)
   │   ├─ Content-Mix (Animation/Doku/Horror)
   │   └─ Upload-Historie (was kam schon?)
   ├─ Erstellt Shorts-Definition (Art-Typ, Start/End, Grade)
   ├─ Generiert SEO-Metadaten automatisch
   └─ Schiebt in render_queue

4. RENDER ENGINE (RTX 3090)
   ├─ FFmpeg mit NVDEC (Decode) + CUDA (Filter) + NVENC (Encode)
   ├─ 8K → 1080x1920 (9:16)
   ├─ Color Grade, Text, Watermark
   ├─ ~3 Sek pro 13s Short / ~12 Sek pro 60s Short
   └─ Output → D:\remaike.TV\output\shorts\

5. UPLOAD PIPELINE (nach Quota-Reset 09:15 MEZ)
   ├─ Prüft Quota-Budget (max 5 uploads/Tag = 250 Units)
   ├─ Upload als PRIVATE (nie public!)
   ├─ Setzt SEO-Metadaten
   └─ Speichert Video-ID in DB

6. NOTIFICATION
   ├─ Dashboard zeigt: "5 neue Shorts ready for review"
   └─ User prüft im YouTube Studio → setzt auf PUBLIC
```

---

## 📋 IMPLEMENTIERUNGSPLAN (Phasen)

### Phase 1: Hardware (1 Tag)
- [ ] PSU prüfen (750W+?)
- [ ] GT 710 ausbauen
- [ ] RTX 3090 einbauen
- [ ] Treiber installieren (Studio Driver)
- [ ] FFmpeg GPU-Test: `ffmpeg -hwaccel cuda -i test.mp4 -c:v hevc_nvenc test_out.mp4`
- [ ] CUDA Toolkit installieren

### Phase 2: Shorts Factory Core (2-3 Tage)
```
scripts/shorts/
├── create_art_shorts.py      ← EXISTIERT (erweitern für GPU)
├── scene_detector.py         ← NEU: PySceneDetect Wrapper
├── source_scanner.py         ← NEU: V:\ Scanner mit DB
├── orchestrator.py           ← NEU: Queue + State Machine
├── seo_generator.py          ← NEU: Auto-SEO aus Templates
└── factory_config.json       ← NEU: Konfiguration
```

**Datei 1: `source_scanner.py`** (~120 Zeilen)
- Scannt V:\ nach neuen/geänderten MP4s
- ffprobe für Metadaten
- Schreibt in JSON-DB (oder Prisma wenn gewünscht)

**Datei 2: `scene_detector.py`** (~200 Zeilen)
- PySceneDetect mit GPU-beschleunigtem OpenCV
- AdaptiveDetector für B&W, ContentDetector für Farbe
- Exportiert Top-Scenes als `{source_id}_scenes.json`
- Generiert Thumbnail-Frames

**Datei 3: `orchestrator.py`** (~300 Zeilen)
- Zentrale State Machine:
  ```
  NEW → SCANNED → SCENES_DETECTED → QUEUED → RENDERING → RENDERED → UPLOADING → UPLOADED → DONE
  ```
- Täglicher Cron (03:00): Scan → Detect → Queue
- Täglicher Cron (09:15): Upload Queue abarbeiten
- Diversitäts-Algorithmus für Content-Mix
- Quota-Tracking

**Datei 4: `factory_config.json`**
```json
{
  "daily_shorts_target": 5,
  "max_daily_uploads": 5,
  "max_quota_per_day": 250,
  "art_type_weights": {
    "IMPACT": 0.35,
    "CINEMA": 0.30,
    "HYPNO": 0.25,
    "TIMETRAVEL": 0.05,
    "ARTPIECE": 0.05
  },
  "source_scan_dirs": [
    "V:\\OriginalSources\\Final\\nyx8kexportupscale",
    "V:\\MediaArchive"
  ],
  "gpu_encoding": {
    "decoder": "hevc_cuvid",
    "encoder": "hevc_nvenc",
    "preset": "p7",
    "cq": 20
  },
  "schedule": {
    "scan_cron": "0 3 * * *",
    "upload_cron": "15 9 * * *"
  }
}
```

### Phase 3: GPU-Beschleunigung (1 Tag)
- [ ] `create_art_shorts.py` erweitern:
  ```python
  # VORHER (CPU):
  cmd = ["ffmpeg", "-i", src, "-vf", filters, "-c:v", "libx264", ...]
  
  # NACHHER (GPU):
  cmd = ["ffmpeg", 
      "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
      "-c:v", "hevc_cuvid",  # GPU Decode
      "-i", src,
      "-vf", f"scale_cuda=1080:1920,hwdownload,format=nv12,{color_grade_filters}",
      "-c:v", "hevc_nvenc", "-preset", "p7", "-cq", "20",
      ...]
  ```
- [ ] Benchmark: CPU vs GPU Encoding-Speed
- [ ] Fallback: Auto-Detect ob GPU vorhanden

### Phase 4: Dashboard Extension (1 Tag)
- [ ] Admin Dashboard (`code/admin/`) erweitern:
  - Shorts Queue View (pending/rendering/uploaded)
  - Manual Scene Selection (Thumbnail-Grid)
  - Override: Art-Typ, Start/End manuell setzen
  - Upload-History Timeline
- [ ] WebSocket: Live Render-Progress

### Phase 5: Auto-Pilot (1 Tag)
- [ ] Windows Task Scheduler oder PM2:
  - `03:00` → `orchestrator.py --scan --detect --queue`
  - `09:15` → `orchestrator.py --upload`
- [ ] Health Monitoring:
  - GPU Temperatur / Auslastung
  - Disk Space Check (min 50GB frei)
  - Quota Remaining
  - Error Count / Auto-Pause bei >3 Fehlern

---

## ⏱️ GESCHÄTZTER ZEITPLAN

| Phase | Aufwand | Abhängigkeit |
|-------|---------|-------------|
| Phase 1: Hardware | 2-4h | 3090 + ggf. PSU kaufen |
| Phase 2: Factory Core | 8-12h | Phase 1 |
| Phase 3: GPU-Beschl. | 4-6h | Phase 1 |
| Phase 4: Dashboard | 4-6h | Phase 2 |
| Phase 5: Auto-Pilot | 2-4h | Phase 2+3 |
| **TOTAL** | **~20-32h** | **1-2 Wochen** |

---

## 💰 KOSTEN

| Position | Kosten | Einmalig/Laufend |
|----------|--------|------------------|
| RTX 3090 (gebraucht) | ~450-600€ | Einmalig |
| PSU Upgrade (falls nötig) | ~80-120€ | Einmalig |
| Strom (3090 @ 350W, 8h/Tag) | ~25€/Monat | Laufend |
| YouTube API Quota | 0€ (10k/Tag reicht) | — |
| **TOTAL** | **~530-720€ + 25€/m** | |

---

## 🎯 OUTPUT NACH FERTIGSTELLUNG

| Metrik | Wert |
|--------|------|
| **Shorts pro Tag (automatisch)** | 5 |
| **Shorts pro Woche** | 35 |
| **Shorts pro Monat** | ~150 |
| **Rendering-Zeit pro Batch** | ~3 Min (14 Shorts) |
| **Menschlicher Aufwand** | 5 Min/Tag (Review im Studio) |
| **Zeit bis 200 Shorts** | ~6 Wochen |
| **Erwartete View-Steigerung** | 10-30x (Shorts Algo Push für neue Channels) |

---

## ⚠️ RISIKEN & MITIGATIONEN

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Monotone Shorts (gleiche Szenen) | 🟡 Mittel | Diversitäts-Algo + Manual Review |
| YouTube Community Strike | 🟡 Mittel | Nur Public Domain, kein NS-Material in Shorts |
| GPU Überhitzung (24/7) | 🟢 Niedrig | Nur 3 Min Batch/Tag, Rest idle |
| Quota-Limit | 🟢 Niedrig | 5 uploads = 250 von 10.000 Units |
| Falsche Szenen-Auswahl | 🟡 Mittel | Thumbnail-Preview vor Upload |

---

## 🏁 EMPFEHLUNG: SOFORT-AKTION

```
1. ✅ Netzteil prüfen (Label auf PSU lesen → Watt?)
2. ✅ RTX 3090 bestellen/einbauen  
3. ✅ Phase 2 starten: orchestrator.py ist der Kern
4. ✅ Erste Woche: Semi-Auto (Render auto, Upload manuell)
5. ✅ Zweite Woche: Full Auto + Dashboard
```

**Nächster konkreter Schritt:** `nvidia-smi` nach Einbau → dann baue ich `orchestrator.py`.
