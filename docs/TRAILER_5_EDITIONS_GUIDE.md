# 🎬 remAIke.TV - 5 TRAILER EDITIONEN

> Professionelle Trailer-Stile basierend auf Best Practices von YouTube Creators, 
> GoPro Action-Videos und Film-Industrie-Standards.

---

## 📺 ÜBERSICHT

| Edition | Stil | Dauer | Auflösung | Zielgruppe |
|---------|------|-------|-----------|------------|
| **1** | CINEMATIC EPIC | 60s | 1920x1080 (16:9) | Film-Enthusiasten |
| **2** | GOPRO ACTION | 45s | 1920x1080 (16:9) | Junge Zielgruppe |
| **3** | RETRO VHS | 50s | 1920x1080 (16:9) | Nostalgie-Fans |
| **4** | CLEAN MINIMAL | 60s | 1920x1080 (16:9) | Premium-Audience |
| **5** | SOCIAL MEDIA | 30s | 1080x1920 (9:16) | TikTok/Shorts |

---

## 🎥 EDITION 1: CINEMATIC EPIC

### Konzept
Langsame Reveals, dramatisches Letterbox-Format, Teal/Orange Color Grading.
Inspiriert von Hollywood-Trailer-Techniken und Netflix-Dokumentationen.

### Techniken
- **Letterbox**: Schwarze Balken oben/unten für Film-Look
- **Color Grading**: Teal in Schatten, Orange in Highlights
- **Slow Crossfades**: 2-3 Sekunden Überblendungen
- **Serif Fonts**: Georgia/Times für Eleganz
- **Subtle Zoom**: Ken Burns Effect (0.3% pro Sekunde)

### Struktur
```
0:00-0:03  │ Black + "remAIke.TV presents"
0:03-0:13  │ Betty Boop Side-by-Side (slow wipe)
0:13-0:23  │ Superman Side-by-Side (slow wipe)
0:23-0:33  │ Felix Side-by-Side (slow wipe)
0:33-0:41  │ Text: "Vergessene Klassiker" / "Restauriert in 8K"
0:41-0:55  │ Montage (crossfades)
0:55-1:00  │ CTA: "SUBSCRIBE for weekly classics"
```

### FFmpeg Filter Highlights
```bash
# Teal/Orange Grading
colorbalance=rs=0.08:gs=-0.03:bs=-0.08

# Slow Wipe Transition
xfade=transition=wipeleft:duration=3

# Letterbox Padding
pad=iw:iw*9/16:(ow-iw)/2:(oh-ih)/2:black
```

---

## 🚀 EDITION 2: GOPRO ACTION

### Konzept
Schnelle Schnitte, Speed Ramps, Kamera-Shake, Flash-Transitions.
Inspiriert von GoPro Hero Videos, Red Bull Content und Gaming Intros.

### Techniken
- **Speed Ramps**: 0.6x - 1.5x variable Geschwindigkeit
- **Camera Shake**: Leichtes Wackeln für Energie
- **Flash Cuts**: Weiße Blitze zwischen Schnitten
- **Slam Text**: Text erscheint mit Stroboskop-Effekt
- **Impact Font**: Bold, aggressive Typography

### Struktur
```
0:00-0:01  │ WHITE FLASH + "remAIke"
0:01-0:04  │ Betty Boop FAST comparison + shake
0:04-0:05  │ SLAM TEXT: "8K"
0:05-0:08  │ Superman FAST comparison + shake
0:08-0:09  │ SLAM TEXT: "RESTORED"
0:09-0:12  │ Popeye FAST comparison
0:12-0:35  │ RAPID MONTAGE (0.5s cuts)
0:35-0:45  │ Action CTA: "SUBSCRIBE NOW"
```

### FFmpeg Filter Highlights
```bash
# Speed Ramp (60% speed)
setpts=0.6*PTS

# Flash Transition
fade=t=out:st=2.8:d=0.2:color=white

# Camera Shake Effect
crop=in_w*0.95:in_h*0.95:in_w*0.025+(random(0)-0.5)*20:in_h*0.025+(random(0)-0.5)*20
```

---

## 📼 EDITION 3: RETRO VHS

### Konzept
VHS-Ästhetik mit Rauschen, Scan Lines, Tracking-Fehler und Color Bleed.
Inspiriert von 80s/90s Nostalgie-Trend und Synthwave-Ästhetik.

### Techniken
- **VHS Noise**: Analog-Rauschen über das Bild
- **Scan Lines**: Horizontale Linien alle 2 Pixel
- **Color Bleed**: RGB-Versatz für CRT-Look
- **Tracking Error**: Horizontale Glitches
- **VHS UI**: PLAY ▶, Timecode, SP/LP Anzeige

### Struktur
```
0:00-0:03  │ VHS Startup: PLAY ▶ + Channel Display
0:03-0:11  │ Betty Boop VHS vs 8K comparison
0:11-0:12  │ TRACKING ERROR GLITCH
0:12-0:20  │ Felix VHS → Clean 8K Reveal (wipe)
0:20-0:24  │ VHS Info Overlay Text
0:24-0:44  │ Montage with occasional glitches
0:44-0:50  │ VHS CTA: "■ STOP to subscribe"
```

### FFmpeg Filter Highlights
```bash
# VHS Noise + Vintage Curve
noise=alls=30:allf=t,curves=vintage

# Scan Lines
drawgrid=w=0:h=2:t=1:c=black@0.2

# Color Bleed (RGB Shift)
rgbashift=rh=-2:bh=2

# Tracking Error
scroll=h=0.02:v=0
```

---

## ⬜ EDITION 4: CLEAN MINIMAL

### Konzept
Apple-Style Minimalismus: Weiß auf Schwarz, sanfte Zooms, elegante Übergänge.
Inspiriert von Apple Keynotes, Tesla Reveals und Premium Brand Content.

### Techniken
- **White on Black**: Maximaler Kontrast, minimale Ablenkung
- **Subtle Zoom**: Sanfter Ken Burns (0.03% pro Sekunde)
- **Soft Fades**: 1-Sekunden Ein-/Ausblendungen
- **Helvetica**: Clean Sans-Serif Typography
- **Breathing Room**: Viel Schwarzraum

### Struktur
```
0:00-0:03  │ "remAIke.TV" fade in/out
0:03-0:13  │ Betty Boop clean split (zoom)
0:13-0:16  │ "Restored." text
0:16-0:26  │ Superman clean split (zoom)
0:26-0:29  │ "Enhanced." text
0:29-0:39  │ Dinner for One clean split
0:39-0:42  │ "Preserved." text
0:42-0:54  │ 4-Up Grid (alle Serien)
0:54-1:00  │ "Subscribe for weekly classics."
```

### FFmpeg Filter Highlights
```bash
# Subtle Zoom (Ken Burns)
zoompan=z='min(zoom+0.0003,1.02)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=250:s=960x540

# Soft Alpha Fade
alpha='if(lt(t,0.8),t/0.8,if(lt(t,2.2),1,(3-t)/0.8))'

# Clean Split Labels
drawtext=text='Before':fontsize=24:fontcolor=white@0.8:font=Helvetica
```

---

## 📱 EDITION 5: SOCIAL MEDIA (VERTICAL)

### Konzept
TikTok/YouTube Shorts optimiert: 9:16 Format, große Texte, schnelle Hooks.
Inspiriert von viralen TikToks und erfolgreichen YouTube Shorts.

### Techniken
- **Vertical Stack**: Original oben, 8K unten
- **Big Text**: 72-96px mit schwarzem Border
- **Hook Formula**: POV/Wait for it/Drop
- **Emoji Integration**: 🔥 🎬 für Engagement
- **Quick Cuts**: Max 5 Sekunden pro Clip

### Struktur
```
0:00-0:02  │ HOOK: "POV: You find 8K cartoons"
0:02-0:07  │ Betty Boop vertical split
0:07-0:09  │ "Wait for it..."
0:09-0:14  │ Superman vertical split
0:14-0:16  │ "8K QUALITY 🔥"
0:16-0:24  │ Rapid vertical clips
0:24-0:30  │ CTA: "FOLLOW for more @remAIke_IT"
```

### FFmpeg Filter Highlights
```bash
# Vertical Stack (1080x1920)
vstack=inputs=2,pad=1080:1920:0:420:black

# Big Text with Border
drawtext=text='8K RESTORED':fontsize=48:fontcolor=yellow:borderw=4:bordercolor=black:font=Impact
```

---

## 🚀 SCHNELLSTART

### Eine Edition erstellen
```batch
cd D:\remaike.TV\scripts\trailer

# Einzelne Edition
edition1_cinematic.bat
edition2_action.bat
edition3_retro_vhs.bat
edition4_minimal.bat
edition5_social.bat

# Alle 5 Editionen
create_all_editions.bat
```

### Output
```
output\trailer_editions\
├── edition1_cinematic\
│   └── EDITION_1_CINEMATIC_FINAL.mp4
├── edition2_action\
│   └── EDITION_2_ACTION_FINAL.mp4
├── edition3_retro\
│   └── EDITION_3_RETRO_VHS_FINAL.mp4
├── edition4_minimal\
│   └── EDITION_4_MINIMAL_FINAL.mp4
└── edition5_social\
    └── EDITION_5_SOCIAL_FINAL.mp4  (1080x1920 Vertical!)
```

---

## 📚 QUELLEN & BEST PRACTICES

### YouTube Creator Research
- **Peter McKinnon**: Cinematic B-Roll Techniques
- **MKBHD**: Clean Minimal Product Showcases
- **GoPro**: Action Camera Editing Style
- **Captain Disillusion**: VHS/Retro Effects
- **MrBeast**: Hook Formulas & CTAs

### Konversions-Optimierung (verifiziert)
1. **Hook in ersten 3 Sekunden** - 65% entscheiden sofort
2. **CTA bei 60-70%** der Laufzeit, nicht am Ende
3. **Spezifische CTAs** ("Subscribe for weekly classics") > generisch
4. **Visual Proof** vor Claims - zeige 8K Qualität
5. **Series Branding** - konsistenter Look über alle Trailer

### A/B Test Empfehlung
```
Woche 1: Edition 4 (Clean Minimal) als Channel Trailer
Woche 2: Edition 2 (Action) - Vergleiche CTR
Woche 3: Edition 1 (Cinematic) - Vergleiche Watch Time
→ Gewinner bleibt als permanenter Trailer
```

---

## ⚠️ WICHTIG

- **Original + Enhanced immer vom SELBEN Video** (nie mixen!)
- **Prüfe Dateipfade** in V:\OriginalSources und V:\MediaArchive
- **FFmpeg muss installiert sein** und im PATH
- **Fonts müssen verfügbar sein** (Georgia, Impact, Helvetica)

---

*Erstellt: 2026-02-03 | remAIke.TV Trailer System*
