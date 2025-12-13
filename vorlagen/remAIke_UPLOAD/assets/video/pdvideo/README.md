# pdvideo - Public Domain Test Videos

Ordner für 3-Minuten Test-Video Compilations aus Public Domain Quellen.

## Struktur

```
pdvideo/
├── enhanced/
│   └── demo-3min.mp4    (Enhanced AI restoration compilation)
└── original/
    └── demo-3min.mp4    (Original source compilation)
```

## Video erstellen

### Empfohlene Quellen (alle im Y: Laufwerk):

**Enhanced (nyx3 restorations):**
- `Y:/Final/nyx8kexportupscale/Dinner_for_One_(1963)_sls_nyx3.mp4`
- `Y:/Final/nyx8kexportupscale/FrankensteinfullMovie_Frankenstein1910_512kb_sls_nyx3.mp4`
- `Y:/Final/nyx8kexportupscale/Gertie the Dinosaur (1914)..._sls_nyx3.mp4`
- `Y:/Final/nyx8kexportupscale/BettyBoopInAHuntingWeWillGo_sls_nyx3.mp4`
- `Y:/Final/nyx8kexportupscale/1920_Convict_13_Buster_Keaton_58_sls_1_starlight_mini_nyx3.mp4`

**Original (sls public domain):**
- `Y:/Final/nyx8kexportupscale/Dinner_for_One_(1963)_sls.mp4`
- `Y:/Final/sls/FrankensteinfullMovie_Frankenstein1910_512kb_sls.mp4`
- `Y:/Final/sls/4k/Gertie the Dinosaur..._sls.mp4`
- `Y:/Final/sls/4k/BettyBoopInAHuntingWeWillGo_sls.mp4`
- `Y:/Final/sls/1920_Convict_13_Buster_Keaton_58_sls.mp4`

### FFmpeg Compilation Command

```bash
# Enhanced compilation (30s from each, total ~3min)
ffmpeg -i "clip1.mp4" -i "clip2.mp4" -i "clip3.mp4" -i "clip4.mp4" -i "clip5.mp4" -i "clip6.mp4" \
  -filter_complex "[0:v]trim=0:30,setpts=PTS-STARTPTS[v0];[1:v]trim=0:30,setpts=PTS-STARTPTS[v1];[2:v]trim=0:30,setpts=PTS-STARTPTS[v2];[3:v]trim=0:30,setpts=PTS-STARTPTS[v3];[4:v]trim=0:30,setpts=PTS-STARTPTS[v4];[5:v]trim=0:30,setpts=PTS-STARTPTS[v5];[v0][v1][v2][v3][v4][v5]concat=n=6:v=1:a=0[out]" \
  -map "[out]" -c:v libx264 -preset slow -crf 18 demo-3min.mp4
```

## Verwendung

Diese Videos werden als Standard-Demo auf der Website verwendet, wenn kein spezifischer Vergleich ausgewählt ist.
