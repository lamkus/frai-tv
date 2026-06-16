# WochenschauTV — Render Server Info Package

> **Stand: 2026-02-26 | Komplett-Dokumentation für externen Renderserver**
> **Ziel: Der Renderserver bekommt ALLES was er braucht um Wochenschau-Videos perfekt zu preparen**

---

## 📋 ÜBERSICHT

Der Renderserver hat **2 Aufgaben**:
1. **8K-Quellen → 4K Pre-Render mit HUD-Overlay** (Upscaling + Watermarking)
2. **Pre-gerenderte Files → YouTube-Livestream** (optional, wenn er direkt streamen kann)

### Aktueller Stand
- **60 Episoden** im Render-Katalog (chronologisch 1939-1945)
- **39 Episoden** haben verifizierte 8K-Quellen auf V:\  
- **20 Episoden** existieren nur auf E:\ (als Strike-geschützte Versionen)
- **40 Episoden** auf D:\ als Rohquellen
- **3 Episoden** sind aktuell im Stream (471, 473, 491) — nur copyright-sichere

---

## 🗂️ 1. QUELL-DATEIEN (Source Files)

### Verzeichnisse

| Laufwerk | Pfad | Inhalt | Anzahl |
|----------|------|--------|--------|
| **V:\\** | `V:\MediaArchive\DeutscheWochenschau\` | 8K SLS Upscaled Originale (4-8 GB/Stück) | 39 verifiziert |
| **V:\\** | `V:\OriginalSources\` | Weitere 8K Quellen | einige |
| **V:\\** | `V:\TopazPipeline\` | Topaz-upscaled Quellen | einige |
| **D:\\** | `D:\remaike.TV\watch\wochenschau_stream\` | Roh-Quellen für Render | ~40 Episoden |
| **E:\\** | `E:\_OUTPUT\WochenschauStrike\` | Strike-geschützte Versionen (bereits mit Overlay/Wasserzeichen) | 20 Episoden |

### Dateinamen-Konvention Quellen

```
V:\ Quellen:
  Deutsche_Wochenschau_Nr459_sls_8K_HQ.mp4
  Deutsche_Wochenschau_Nr470_sls_8K_HQ.mp4
  (Muster: Deutsche_Wochenschau_Nr{NNN}_sls_8K_HQ.mp4)

D:\ Quellen:
  Wochenschau_Nr{NNN}_*.mp4  oder  *{NNN}*

E:\ Strike-Quellen:
  wochenschau_nr{NNN}_8K_HQ.mp4
  wochenschau_nr{NNN}_ARCHIVE_PROTECTED.mp4
```

### Episode-Nummern Katalog (60 Episoden, chronologisch)

```
459, 468, 470, 471, 473, 477, 480, 482, 483, 488,
491, 492, 493, 496, 502, 504, 505, 506, 508, 509,
512, 513, 514, 515, 518, 519, 520, 522, 523, 542,
543, 544, 545, 547, 548, 550, 552, 553, 554, 555,
556, 565, 567, 569, 573, 605, 606, 607, 652, 654,
720, 721, 722, 746, 749, 750, 751, 752, 753, 754
```

### Nur auf E:\ vorhandene Episoden (20 Stück)

```
491, 492, 493, 496, 504, 505, 506, 552, 553, 554,
555, 556, 565, 567, 569, 605, 606, 607, 749, 752
```

### Verifizierte 8K-Quellen (V:\, 39 Stück)

Siehe `config/wochenschau_8k_verified_sources.json` — enthält pro Episode:
- Voller Dateipfad auf V:\
- Dateigröße in Bytes
- Verifikationsstatus

**Fehlende 8K-Quellen:** 522, 524, 652, 654, 720, 721, 722, 746, 750

---

## 🎨 2. HUD OVERLAY SYSTEM (v3 — "Historical Documentary")

### Overlay-Architektur

Das HUD ist ein **linkes Panel** (240px breit @1080p, skaliert auf 480px @4K) mit:

```
┌────────────────────┐
│   remAIke.TV       │  Brand (30px @1080p)
│                    │
│   ── NOW PLAYING ──│  Red divider (#FF0000)
│                    │
│   INVASION OF      │  Era Label (18px, uppercase)
│   POLAND           │  → aus wochenschau_hud_context.json
│                    │
│   War Begins       │  Event Title (34px, bold)
│                    │  → aus hud_context oder events.json
│   FIRST WARTIME    │
│   NEWSREEL EVER    │  Context Block (18px, max 6 Zeilen)
│   PRODUCED.        │  → Englischer historischer Kontext
│   Germany invades  │  → DAS Alleinstellungsmerkmal!
│   Poland...        │
│                    │
│   ─────────────    │  Separator
│   Warsaw, Poland   │  Location (19px)
│   Sept 1, 1939     │  Exact Date (18px)
│                    │
│   ████████░░░░     │  War Timeline (1939—1945)
│   1939      1945   │  + Runtime Progress Bar
│     12 / 60        │  Episode Counter
└────────────────────┘
```

Zusätzlich gibt es ein **rechtes Panel** (gleiche Breite) mit:
- Rotem Top-Accent (3px)
- Roter Hairline am linken Rand

### Farbschema (YouTube-Brand)

```
YT_RED         = '#FF0000'
YT_RED_DARK    = '#CC0000'
YT_BG_DARK     = '#0D0D0D'
YT_TEXT_PRIMARY = '#FFFFFF'
YT_TEXT_SECONDARY = '#AAAAAA'
YT_TEXT_MUTED  = '#717171'

Panel Background: #0A0A0F @ 0.92 Opacity
```

### Fonts

```
Primary:   'Segoe UI'           (Windows = YouTube's Roboto equivalent)
Semibold:  'Segoe UI Semibold'  (für Brand, Era, Event Title)
```

### Skalierung

Alle Pixel-Werte sind für **1080p Basis** definiert. Bei 4K wird automatisch `×2` skaliert:
```python
scale = output_height / 1080  # 2.0 bei 4K, 1.0 bei 1080p
px(val) = max(1, int(val * scale))
```

### Dynamische Elemente

1. **Runtime Progress Bar** — zeigt aktuelle Wiedergabeposition im Video
   - Nutzt FFmpeg-Expression `t` (aktuelle Zeit) / `_duration`
   - Roter Balken wächst mit der Wiedergabe
   - ETA-Anzeige: "XX remaining" + Elapsed/Total

2. **War Timeline Bar** — zeigt Position im Krieg (1939-1945)
   - Berechnet aus Episoden-Datum
   - Roter Fortschrittsbalken
   - Jahres-Tick-Marks

3. **Episode Counter** — "12 / 60" (dynamisch pro Episode)

---

## 📊 3. METADATEN PRO EPISODE

### Datenquellen (3 JSON-Dateien)

#### A) `config/wochenschau_events.json`
Basis-Metadaten pro Episode:
```json
{
  "events": {
    "470": {
      "date": "1939-09-06",
      "event_de": "Kriegsausbruch",
      "event_en": "War Begins",
      "note": "ERSTE KRIEGSWOCHENSCHAU! Überfall auf Polen (01.09.1939)"
    }
  }
}
```

#### B) `config/wochenschau_complete_locations.json`
Geografische + erweiterte Metadaten:
```json
{
  "470": {
    "number": 470,
    "date": "1939-09-06",
    "event_en": "War Begins",
    "event_de": "Kriegsausbruch",
    "location": {
      "lat": 52.2297,
      "lng": 21.0122,
      "desc": "Warsaw, Poland"
    },
    "historical_note": "ERSTE KRIEGSWOCHENSCHAU! Überfall auf Polen (01.09.1939)"
  }
}
```

#### C) `config/wochenschau_hud_context.json` ⭐ WICHTIGSTE DATEI
Reichhaltiger englischer historischer Kontext für HUD v3:
```json
{
  "episodes": {
    "470": {
      "era": "INVASION OF POLAND",
      "title": "War Begins",
      "context": "FIRST WARTIME NEWSREEL EVER PRODUCED. Germany invades Poland on September 1, 1939. World War II begins.",
      "exact_date": "September 1, 1939",
      "location": "Warsaw, Poland"
    }
  }
}
```
**32 Episoden** haben reichen HUD-Kontext. Für die restlichen werden Fallbacks aus events.json/locations.json verwendet.

### Episode Dict (was der Renderer braucht)

Pro Episode muss folgender Dict aufgebaut werden:

```python
{
    'number': 470,                              # Episode-Nummer
    'date': '1939-09-06',                       # ISO-Datum
    'event_en': 'War Begins',                   # Englischer Event-Name
    'event_de': 'Kriegsausbruch',               # Deutscher Event-Name
    'location': {'lat': 52.23, 'lng': 21.01, 'desc': 'Warsaw, Poland'},
    'historical_note': 'ERSTE KRIEGSWOCHENSCHAU!...',
    'year': 1939,                               # Für Timeline-Berechnung
    '_index': 3,                                # Position in Playlist (1-based)
    '_total': 60,                               # Gesamt-Episoden
    '_duration': 480,                           # Video-Dauer in Sekunden (via ffprobe)
    'file_path': 'D:\\...\\source.mp4',          # Quell-Datei
}
```

Zusätzliche Felder aus `wochenschau_hud_context.json` (per Episode-Nr. gesucht):
```python
{
    'era': 'INVASION OF POLAND',                # Ära-Label (uppercase)
    'title': 'War Begins',                      # Event-Titel (überschreibt event_en)
    'context': 'FIRST WARTIME NEWSREEL...',     # Kontext-Block (richtext)
    'exact_date': 'September 1, 1939',          # Formatiertes Datum
    'location': 'Warsaw, Poland',               # Ort (String)
}
```

---

## ⚙️ 4. RENDER-EINSTELLUNGEN (FFmpeg)

### 4K Pre-Render (render_v3.py Einstellungen)

```
Auflösung:     3840×2160 (4K, als "8K HQ" gebranded)
Codec:         h264_nvenc (NVIDIA Hardware-Encoder)
Preset:        p5 (Qualitäts-Preset)
Bitrate:       20 Mbps VBR (maxrate 25 Mbps, bufsize 40 Mbps)
Pixel Format:  yuv420p
GOP:           60 Frames (2 Sekunden bei 30fps)
B-Frames:      2
FPS:           30
Audio Codec:   AAC
Audio Bitrate: 192 kbps
Audio Sample:  44100 Hz
Faststart:     Ja (+faststart, Web-optimiert)
A/V Sync:      -async 1
```

### FFmpeg Filter-Chain (Reihenfolge!)

```
1. scale=3840:2160:force_original_aspect_ratio=decrease
2. pad=3840:2160:(ow-iw)/2:(oh-ih)/2:black
3. fps=30
4. [HUD Overlay Filters — ca. 30-40 drawtext/drawbox Filter]
```

### Vollständiger FFmpeg-Befehl (Beispiel)

```bash
ffmpeg -y \
  -threads 0 \
  -i "D:\watch\wochenschau_stream\Wochenschau_Nr470_8K.mp4" \
  -vf "scale=3840:2160:force_original_aspect_ratio=decrease,\
       pad=3840:2160:(ow-iw)/2:(oh-ih)/2:black,\
       fps=30,\
       drawbox=x=0:y=0:w=480:h=ih:color=#0A0A0F@0.92:t=fill,\
       drawbox=x=0:y=0:w=480:h=6:color=#FF0000@0.95:t=fill,\
       drawbox=x=479:y=0:w=2:h=ih:color=#FF0000@0.20:t=fill,\
       drawbox=x=3360:y=0:w=480:h=6:color=#FF0000@0.95:t=fill,\
       drawbox=x=3360:y=0:w=2:h=ih:color=#FF0000@0.20:t=fill,\
       drawtext=text='remAIke.TV':fontsize=60:fontcolor=#FFFFFF@0.95:x=48:y=36:font='Segoe UI Semibold':shadowcolor=black@0.9:shadowx=6:shadowy=6,\
       drawtext=text='NOW PLAYING':fontsize=32:fontcolor=#FFFFFF@0.92:x=110:y=152:font='Segoe UI Semibold':shadowcolor=black@0.8:shadowx=4:shadowy=4,\
       drawtext=text='INVASION OF':fontsize=36:fontcolor=#FFFFFF@0.90:x=48:y=224:font='Segoe UI Semibold':shadowcolor=black@0.8:shadowx=4:shadowy=4,\
       drawtext=text='POLAND':fontsize=36:fontcolor=#FFFFFF@0.90:x=48:y=268:font='Segoe UI Semibold':shadowcolor=black@0.8:shadowx=4:shadowy=4,\
       drawtext=text='War Begins':fontsize=68:fontcolor=#FFFFFF@0.98:x=48:y=292:font='Segoe UI Semibold':shadowcolor=black@0.9:shadowx=6:shadowy=6,\
       [... weitere Context/Location/Date/Timeline Filter ...]" \
  -c:v h264_nvenc \
  -preset p5 \
  -b:v 20000k -maxrate 25000k -bufsize 40000k \
  -pix_fmt yuv420p \
  -g 60 -bf 2 \
  -c:a aac -b:a 192k -ar 44100 \
  -movflags +faststart \
  -async 1 \
  "D:\wochenschau_rendered\WochenschauTV_Nr470_8K_HQ.mp4"
```

### Output-Dateinamen

```
D:\remaike.TV\wochenschau_rendered\WochenschauTV_Nr{NNN}_8K_HQ.mp4  (D:\ Episoden)
E:\wochenschau_rendered\WochenschauTV_Nr{NNN}_8K_HQ.mp4              (E:\ Episoden)
```

### Render-Performance (Referenz RTX 3090)

| Schritt | Geschwindigkeit |
|---------|----------------|
| 8K AV1 Software-Decode (CPU) | ~30 fps (alle Kerne) |
| CPU Drawtext Filter | ~25 fps |
| h264_nvenc Encode (GPU) | >100 fps |
| **Gesamt-Pipeline** | **~20-25 fps (ca. 30 Min/Episode)** |

> **WICHTIG:** VP9/AV1 cuvid Hardware-Decode funktioniert NICHT mit drawtext-Filtern!
> Lösung: Software-Decode → CPU-Filter → NVENC GPU-Encode

---

## 📡 5. STREAMING-EINSTELLUNGEN (stream_4k.py)

### YouTube Live-Stream Specs (v7, YouTube-offiziell)

```
Auflösung:     3840×2160 (Native 4K)
Codec:         h264_nvenc (NVIDIA)
Preset:        p2 (schnell, ~2.5-3× Echtzeit)
Rate Control:  CBR (YouTube PFLICHT!)
Bitrate:       30 Mbps (YouTube-Empfehlung für H.264 4K@30fps)
Buffer:        60 MB (2× Bitrate)
Profil:        High (CABAC Entropy)
Level:         5.1
GOP:           60 (= 2 Sekunden Keyframe)
B-Frames:      2 + 1 Reference Frame
Farbraum:      bt709 SDR 8-bit yuv420p
Audio:         AAC 128 kbps stereo, 44.1 kHz (re-encoded!)
Protokoll:     RTMPS (verschlüsselt)
Container:     FLV (Streaming-Modus)
```

### Stream-Modus

```
Concat-Demuxer → EINZELNER FFmpeg-Prozess → RTMPS → YouTube Live
- -stream_loop -1 = Endlosschleife
- -re = Echtzeit-Pacing
- NVENC re-encode (NICHT -c copy!) wegen:
  1. YouTube verlangt CBR (Quellen sind VBR 20 Mbps)
  2. 30 Mbps > 20 Mbps (YouTube-Empfehlung)
  3. Audio re-encode = saubere Timestamps an Episode-Übergängen
```

### Stream Key
```
Datei: D:\remaike.TV\config\stream_key.txt
URL:   rtmps://a.rtmp.youtube.com/live2/{STREAM_KEY}
```

### Resume-Support
```bash
python stream_4k.py --resume 750 --inpoint 341.9
# → Startet bei Episode 750, Sekunde 341.9
# → Dann weiter: 751, 752, ..., 754, 459, 468, ... (Endlosschleife)
```

---

## 🔄 6. PIPELINE-ABLAUF (End-to-End)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  8K QUELLE      │     │  PRE-RENDER     │     │  LIVESTREAM     │
│  (V:\ oder D:\) │ ──> │  (render_v3.py) │ ──> │  (stream_4k.py) │
│                 │     │                 │     │                 │
│  AV1/VP9/H.264  │     │  + HUD Overlay  │     │  NVENC H.264    │
│  8K Upscaled    │     │  + Scale → 4K   │     │  CBR 30 Mbps    │
│  4-8 GB/Episode │     │  h264_nvenc     │     │  → YouTube RTMPS│
│                 │     │  20 Mbps VBR    │     │                 │
│                 │     │  Output: ~2 GB  │     │  Concat -c copy │
│                 │     │                 │     │  (aktuell re-enc)│
└─────────────────┘     └─────────────────┘     └─────────────────┘

Schritt 1: build_episode_dict()     → Metadaten aus 3 JSON-Dateien laden
Schritt 2: build_timeline_filters() → HUD-Overlay als FFmpeg-Filterkette generieren
Schritt 3: ffmpeg (NVENC)           → 8K → 4K mit HUD, Output als H.264 MP4
Schritt 4: stream_4k.py             → Concat aller gerenderter Files → YouTube
```

### Warum Pre-Render statt Echtzeit?

1. **8K AV1 Software-Decode** ist CPU-intensiv → kein Echtzeit möglich
2. **Drawtext-Filter** laufen nur auf CPU (nicht GPU-kompatibel mit cuvid)
3. **Lagfrei:** Pre-gerenderte Files = `-c copy` beim Streamen = 0% CPU
4. **Flexibel:** Render einmal, streame beliebig oft

---

## 🖥️ 7. RENDERSERVER-OPTIONEN

### Option A: Nur Render (wie bisher)

1. Renderserver rendert alle 60 Episoden mit HUD → 4K H.264
2. Gerenderte Files werden auf D:\ / E:\ gespeichert
3. Stream-PC spielt sie mit stream_4k.py ab

**Renderserver braucht:**
- FFmpeg mit NVENC (NVIDIA GPU)
- Python 3.10+ (für build_timeline_filters)
- Zugriff auf Quell-Dateien (V:\, D:\ oder E:\)
- Die 3 JSON-Config-Dateien
- wochenschautv.py (HUD-Modul)
- Segoe UI + Segoe UI Semibold Fonts

### Option B: Render + Stream (All-in-One)

1. Renderserver rendert UND streamt direkt
2. Braucht zusätzlich: `config/stream_key.txt`
3. Stabile Internetverbindung (min. 35 Mbps Upload für 30 Mbps CBR)
4. RTMPS-Zugang zu YouTube

**Zusätzlich nötig:**
- Stabile Uplink-Verbindung
- stream_4k.py Script
- psutil Python-Modul

### Option C: Echtzeit-Render + Stream (fortgeschritten)

Statt Pre-Render → direkt von 8K Quelle → HUD → Stream.
**NICHT EMPFOHLEN** weil:
- 8K AV1-Decode + CPU-Filter + NVENC = grenzwertig für Echtzeit
- Kein Fehlerpuffer (wenn GPU/CPU kurz lahmt = Lag im Stream)

---

## 📦 8. DATEIEN FÜR DEN RENDERSERVER

### Pflicht-Dateien

```
scripts/youtube/wochenschautv.py           # HUD-Modul (build_timeline_filters)
render_v3.py                                # Render-Script
config/wochenschau_events.json             # Basis-Metadaten (60+ Episoden)
config/wochenschau_complete_locations.json  # Geo + erweiterte Daten
config/wochenschau_hud_context.json        # Rich English Context (32 Episoden)
```

### Optional (für Streaming)

```
stream_4k.py                               # Stream-Script
config/stream_key.txt                       # YouTube RTMP Key (GEHEIM!)
config/wochenschautv_config.json           # Stream-Metadata
```

### Font-Abhängigkeiten

```
Segoe UI          → Standard Windows Font
Segoe UI Semibold → Standard Windows Font
(Auf Linux: ttf-ms-fonts oder manuell installieren)
```

### Python-Abhängigkeiten

```
Python 3.10+
psutil            (nur für stream_4k.py)
ffmpeg            (in PATH, mit NVENC-Support)
ffprobe           (in PATH)
```

---

## 🛡️ 9. YOUTUBE COMPLIANCE (PFLICHT!)

### Wochenschau = NS-Propaganda → Besondere Vorsicht!

Jedes Video MUSS enthalten:
1. **HUD-Overlay** (✅ via build_timeline_filters — "Historical Documentary" Design)
2. **Category 27** (Education) — NICHT News!
3. **"Made for Kids" = NEIN**
4. **Disclaimer in Description**

Das HUD v3 erfüllt alle YouTube-Anforderungen:
- "remAIke.TV" Brand → identifiziert Uploader
- "NOW PLAYING" + Era/Event/Context → bildet den historischen Rahmen
- Permanent sichtbar → Gemini-KI kann jeden Frame einordnen
- Englischsprachig → international verständlich

### Copyright-Filter (Stream)

Aktuell sind nur **3 Episoden** im Stream freigegeben (keine Copyright-Claims):
```
471, 473, 491
```

⚠️ Vor Freischaltung weiterer Episoden: Copyright-Status im YouTube Studio prüfen!

---

## 📊 10. EPISODEN-LISTE MIT METADATEN

| Nr. | Datum | Era | Event (EN) | Location | Quelle |
|-----|-------|-----|------------|----------|--------|
| 459 | 1939-06-21 | PRE-WAR EUROPE | Pre-War Era | Berlin, Germany | V:\ / D:\ |
| 468 | 1939-08-23 | ROAD TO WAR | Nazi-Soviet Pact | Moscow, Russia | V:\ / D:\ |
| 470 | 1939-09-06 | INVASION OF POLAND | War Begins | Warsaw, Poland | V:\ / D:\ |
| 471 | 1939-09-13 | INVASION OF POLAND | Poland Campaign | Poland | V:\ / D:\ |
| 473 | 1939-09-27 | INVASION OF POLAND | Fall of Warsaw | Warsaw, Poland | V:\ / D:\ |
| 477 | 1939-10-25 | OCCUPIED POLAND | Poland Occupied | Poland | V:\ / D:\ |
| 480 | 1939-11-08 | ASSASSINATION ATTEMPT | Bürgerbräu Bomb | Munich, Germany | V:\ / D:\ |
| 482 | 1939-11-30 | THE WINTER WAR | Winter War Begins | Finland | V:\ / D:\ |
| 483 | 1939-12-06 | THE WINTER WAR | Finnish Resistance | Finland | V:\ / D:\ |
| 488 | 1940-01-10 | THE PHONEY WAR | Phoney War | Germany | V:\ / D:\ |
| 491 | — | — | — | — | E:\ only |
| 492 | — | — | — | — | E:\ only |
| 493 | — | — | — | — | E:\ only |
| 496 | — | — | — | — | E:\ only |
| 502 | 1940-04-09 | SCANDINAVIA INVADED | Norway Invasion | Oslo, Norway | V:\ / D:\ |
| 504-506 | — | — | — | — | E:\ only |
| 508 | 1940-05-26 | FALL OF FRANCE | Dunkirk Pocket | Dunkirk, France | V:\ / D:\ |
| 509 | 1940-06-04 | FALL OF FRANCE | Dunkirk Evacuation | Dunkirk, France | V:\ / D:\ |
| 512 | 1940-06-22 | FALL OF FRANCE | French Armistice | Compiègne, France | V:\ / D:\ |
| 513 | 1940-07-03 | FORTRESS EUROPE | Channel Islands | Channel Islands | V:\ / D:\ |
| 514 | 1940-07-10 | FORTRESS EUROPE | Berlin Victory Parade | Berlin, Germany | V:\ / D:\ |
| 515 | 1940-07-10 | BATTLE OF BRITAIN | Battle of Britain | London, England | V:\ / D:\ |
| 518 | 1940-08-07 | BATTLE OF BRITAIN | Channel Battles | English Channel | V:\ / D:\ |
| 519 | 1940-08-13 | BATTLE OF BRITAIN | Eagle Day | England | V:\ / D:\ |
| 520 | 1940-08-21 | BATTLE OF BRITAIN | Battle at its Peak | London, England | V:\ / D:\ |
| 522 | 1940-09-04 | BATTLE OF BRITAIN | Berlin Retaliation | Berlin, Germany | V:\ / D:\ |
| 523 | 1940-09-07 | THE LONDON BLITZ | London Blitz | London, England | V:\ / D:\ |
| 542 | 1941-01-22 | NORTH AFRICA | Tobruk Falls | Tobruk, Libya | V:\ / D:\ |
| 543 | 1941-01-29 | NORTH AFRICA | Afrika Korps | North Africa | V:\ / D:\ |
| 544 | 1941-02-12 | NORTH AFRICA | Rommel Arrives | Tripoli, Libya | V:\ / D:\ |
| 545 | 1941-02-12 | NORTH AFRICA | Africa Offensive | North Africa | V:\ / D:\ |
| 547 | 1941-02-26 | NORTH AFRICA | Africa Campaign | North Africa | V:\ / D:\ |
| 548 | 1941-03-01 | AXIS EXPANSION | Bulgaria Joins Axis | Sofia, Bulgaria | V:\ / D:\ |
| 550 | 1941-03-25 | BALKANS CRISIS | Yugoslavia Crisis | Belgrade, Yugoslavia | V:\ / D:\ |
| 552-556 | — | — | — | — | E:\ only |
| 565, 567, 569 | — | — | — | — | E:\ only |
| 573 | 1941-08-27 | OPERATION BARBAROSSA | Battle of Kiev | Kyiv, Ukraine | V:\ / D:\ |
| 605-607 | — | — | — | — | E:\ only |
| 652 | 1943-03-03 | EASTERN FRONT | Third Battle of Kharkov | Kharkov, Ukraine | V:\ / D:\ |
| 654 | 1943-03-17 | NORTH AFRICA ENDGAME | Tunisia Battles | Tunisia | V:\ / D:\ |
| 720 | 1944-06-21 | VENGEANCE WEAPONS | V-1 Flying Bombs | London, England | V:\ / D:\ |
| 721 | 1944-06-28 | OPERATION BAGRATION | Bagration Begins | Belarus | V:\ / D:\ |
| 722 | 1944-07-05 | OPERATION BAGRATION | Army Group Center Destroyed | Minsk, Belarus | V:\ / D:\ |
| 746 | 1944-12-20 | LAST OFFENSIVE | Battle of the Bulge | Ardennes, Belgium | V:\ / D:\ |
| 749 | — | — | — | — | E:\ only |
| 750 | 1945-01-17 | THE FINAL COLLAPSE | Vistula-Oder Offensive | Vistula River, Poland | V:\ / D:\ |
| 751 | 1945-01-24 | THE FINAL COLLAPSE | Eastern Front Collapses | Poland | V:\ / D:\ |
| 752 | — | — | — | — | E:\ only |
| 753 | 1945-02-04 | ENDGAME | Yalta Conference | Yalta, Crimea | V:\ / D:\ |
| 754 | 1945-02-13 | ENDGAME | Dresden Bombed | Dresden, Germany | V:\ / D:\ |

---

## 🔧 11. SCHNELL-START FÜR RENDERSERVER

### Schritt 1: Dateien kopieren
```
render_v3.py
scripts/youtube/wochenschautv.py
config/wochenschau_events.json
config/wochenschau_complete_locations.json
config/wochenschau_hud_context.json
```

### Schritt 2: Pfade anpassen in render_v3.py
```python
SRC_DIR    = r'<PFAD_ZU_QUELLEN>'        # Wo die 8K Quellen liegen
OUT_DIR    = r'<PFAD_FÜR_OUTPUT>'         # Wo gerenderte Files hinkommen
EVENTS     = r'<PFAD>/wochenschau_events.json'
LOCATIONS  = r'<PFAD>/wochenschau_complete_locations.json'
```

### Schritt 3: Test-Render einer Episode
```bash
python render_v3.py --episode 470 --dry-run   # Zeigt was passieren würde
python render_v3.py --episode 470              # Rendert Episode 470
```

### Schritt 4: Alle Episoden rendern
```bash
python render_v3.py                            # Rendert alle, überspringt existierende
python render_v3.py --force                    # Erzwingt Re-Render aller
```

### Schritt 5 (optional): Direkt streamen
```bash
python stream_4k.py --list                     # Zeigt Episoden-Liste
python stream_4k.py                            # Startet Endlos-Stream
```

---

*Erstellt: 2026-02-26 | Quelle: render_v3.py, stream_4k.py, wochenschautv.py, 3 JSON-Configs*
