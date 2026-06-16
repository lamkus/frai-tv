# YouTube Knowledge Base - remAIke.TV

> **Stand: Januar 2026**
> Diese Datei enthält alle Best Practices, Learnings und Referenzen für YouTube-Operationen.

---

## 📊 YOUTUBE ALGORITHM 2025/2026

### Wichtigste Ranking-Faktoren

1. **Watch Time / Retention** - Wie lange schauen Zuschauer?
2. **Engagement** - Likes, Comments, Shares, Saves
3. **Click-Through Rate (CTR)** - Thumbnail + Titel Performance
4. **Session Time** - Hält das Video Zuschauer auf YouTube?
5. **Subscriber Growth** - Konvertiert das Video zu Abos?

### Shorts-spezifisch (2025/2026)

- **Views seit 31.03.2025**: Zählen ab Start/Replay (keine Mindest-Watchtime!)
- **"Engaged Views"**: Alte Metrik, weiterhin in Analytics verfügbar
- **Loop-Design**: Videos die zum erneuten Ansehen animieren performen besser
- **Erste 2-3 Sekunden**: Entscheidend für Retention
- **Max 3 Minuten**: Seit Oktober 2024
- **Musik nur <60 Sek**: Copyright-Einschränkung

---

## 🎯 SEO BEST PRACTICES

### Titel (max 100 Zeichen, 70 empfohlen)

```
RICHTIG:
- Keyword am ANFANG
- Jahr in Klammern: (1987)
- Qualität: 8K HQ / 4K UHD
- Brand: @remAIke_IT
- Bei Serien: (25/52) für Episode 25 von 52

FALSCH:
- Clickbait ohne Bezug zum Inhalt
- CAPS LOCK ÜBERALL
- Zu viele Emojis im Titel
```

### Description (erste 2 Zeilen KRITISCH!)

```
STRUKTUR:
1. Hook mit Keyword (erscheint in Suche!)
2. Kurze Inhaltsbeschreibung
3. ════════════════════════
4. Ausführliche Info
5. Timestamps/Chapters
6. Links (Playlist, Channel, Social)
7. Hashtags (2-3, NICHT mehr!)
```

### Tags (5-15 optimal)

```
REIHENFOLGE:
1. Exakter Titel-Match
2. Primäre Keywords
3. Serien-Name / Franchise
4. Genre
5. Qualität (8K, 4K, remastered)
6. Brand (remAIke)
7. Verwandte Begriffe
```

### Hashtags

```
2025/2026 REGEL:
- Max 2-3 Hashtags in Description
- Erscheinen ÜBER der Description
- Mehr = YouTube wertet als Spam
- #Shorts ist NICHT mehr nötig (automatische Erkennung)
```

---

## 📺 KATEGORIE-SPEZIFISCHE REGELN

### Zeichentrickserien (BraveStarr, Alfred J. Kwak)

```yaml
Category: Film & Animation
Playlist: Chronologisch nach Episodennummer
Titel-Format: "[Serie] (EP/TOTAL): [Titel] | 8K HQ | Deutsch | @remAIke_IT"
Tags: 
  - Serien-Name (alle Schreibweisen!)
  - Jahr
  - Studio (Filmation, etc.)
  - Charakternamen
  - "80er Zeichentrick" / "80s cartoon"
```

### Vintage Music (Soundies)

```yaml
Category: Music
Playlist: "Soundies - Vintage Music (1940s)"
Titel-Format: "Soundie: [Song] | [Artist wenn bekannt] | 8K HQ | @remAIke_IT"
Tags:
  - soundie, soundies
  - 1940s, vintage music
  - Jazz, swing, big band (je nach Genre)
  - Artist Name
  - Song Title
```

### Public Domain Filme

```yaml
Category: Film & Animation
Playlist: Nach Genre oder Jahrzehnt
Titel-Format: "[Film] ([Jahr]) | Full Movie | 8K HQ | @remAIke_IT"
Tags:
  - Film-Titel
  - Jahr
  - Regisseur
  - Hauptdarsteller
  - Genre
  - "public domain", "classic film"
```

---

## 🔧 TECHNISCHE SPECS

### Video Upload

| Eigenschaft | Empfehlung |
|-------------|------------|
| Resolution | 3840x2160 (4K) oder höher |
| Codec | H.264 / H.265 |
| Frame Rate | 24/25/30/60 fps |
| Bitrate | 35-85 Mbps für 4K |
| Audio | AAC, 320 kbps |

### Thumbnails

| Eigenschaft | Wert |
|-------------|------|
| Resolution | 1280x720 (min 640px Breite) |
| Format | JPG, PNG, GIF |
| Max Size | 2MB (Video), 10MB (Podcast) |
| Aspect Ratio | 16:9 |

### Shorts

| Eigenschaft | Wert |
|-------------|------|
| Aspect Ratio | 9:16 (vertikal) |
| Max Länge | 3 Minuten |
| Resolution | 1920x1080 empfohlen |
| Min Resolution | 600x1067 |
| Musik | Nur bei <60 Sek |

---

## 🚫 HÄUFIGE FEHLER (NICHT WIEDERHOLEN!)

### Episode-Mapping bei Serien

```
❌ FALSCH: Dateiname "e02" = Ausstrahlungs-Episode 2
✅ RICHTIG: Dateiname "e02" = PRODUKTIONS-Nummer 002

BraveStarr Beispiel:
- e01 = Prod 001 = "Das Musikfestival" (DE Ausstrahlung: #55!)
- e02 = Prod 002 = "Das Ungetüm aus der Wüste" (DE Ausstrahlung: #60!)
```

### Blind Batch-Updates

```
❌ FALSCH: Script das 100 Videos auf einmal ändert
✅ RICHTIG: Jede Änderung einzeln prüfen und bestätigen

VOR JEDER ÄNDERUNG:
1. Video-ID verifizieren
2. Aktuellen Titel/Desc via API holen
3. Thumbnail im Studio visuell prüfen
4. Änderung dem User ZEIGEN
5. User-Freigabe abwarten
```

### Keyword-Matching

```
❌ FALSCH: "Musikfestival" im Titel → muss Episode 55 sein!
✅ RICHTIG: Thumbnail + Dateiname + User-Bestätigung

Niemals blind auf Keywords vertrauen!
```

---

## 📚 REFERENZEN

### Offizielle Docs

- [YouTube Creator Academy](https://creatoracademy.youtube.com/)
- [YouTube Help - Shorts](https://support.google.com/youtube/answer/10059070)
- [YouTube API v3](https://developers.google.com/youtube/v3)

### Best Practice Guides (2025/2026)

- [Hootsuite YouTube Shorts Guide](https://blog.hootsuite.com/youtube-shorts/)
- [Hootsuite YouTube SEO](https://blog.hootsuite.com/youtube-seo/)

### Tools

- [TubeBuddy](https://www.tubebuddy.com/) - Browser Extension für YouTube SEO
- [VidIQ](https://vidiq.com/) - Keyword Research & Analytics
- [YouTube Analytics](https://studio.youtube.com/) - Native Insights

---

## 🔄 CHANGELOG

| Datum | Änderung |
|-------|----------|
| 2026-01-13 | Initiale Knowledge Base erstellt |
| 2026-01-13 | BraveStarr Episode-Mapping hinzugefügt |
| 2026-01-13 | Shorts Best Practices 2025/2026 dokumentiert |
| 2026-01-13 | Fehler-Learnings dokumentiert |
