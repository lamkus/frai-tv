# YouTube Studio Runbook (remAIke_IT)

Ziel: Alles, was ich _automatisieren kann_, ist im Repo vorbereitet (Titel/Description/Hashtags + Kapitel-Skeleton pro Compilation). Das **einzige**, was ich nicht direkt erledigen kann, sind Änderungen **im YouTube Studio** selbst (ohne deine Login-/OAuth-Freigabe).

## 1) Auto-generierter „Optimization Pack“ (fertig)
Im Repo liegt ein kompletter Satz „Copy/Paste“-Dateien:
- `docs/youtube/INDEX.md` (Übersicht)
- `docs/youtube/3gzbxznJ_PM_popeye-marathon-8k.md`
- `docs/youtube/FG-vqRH5Cg4_chaplin-film-fest.md`
- `docs/youtube/Qm3K0-XL46Q_kirby-abridged.md`

Neu generieren (falls sich `remaikeData.js` ändert):
- In `code/frontend`: `npm run yt:pack`

## 2) YouTube Studio – pro Compilation (5–12 Minuten)
Für jedes Video aus `docs/youtube/*.md`:

1. YouTube Studio → **Content** → Video öffnen
2. **Title**: aus `## Title (Optimized)` kopieren
3. **Description**: alles aus dem Code-Block unter `## Description (Paste into YouTube)` kopieren
4. **Kapitel aktivieren**:
   - Video öffnen (YouTube Watch Page)
   - Pausieren → mit `,` und `.` frameweise springen (präziser als „Millisekunden raten“)
   - Startpunkte notieren
   - In der Description die `00:00` Platzhalter durch echte Zeiten ersetzen
   - Wichtig: **erste Marke muss `00:00` sein**
5. **Playlists** setzen:
   - Popeye → Popeye Playlist
   - Chaplin → Chaplin Playlist
   - Kirby → Kirby Collection Playlist
6. **Details** (Quick Wins):
   - Video language: passend setzen (meist English)
   - Category: Film & Animation / Education je nach Inhalt
   - Tags: optional (YouTube nutzt primär Title/Description, Tags sind sekundär)
7. **End Screen** (20s): Subscribe + nächstes Video
8. Speichern

## 2.5) Kapitel automatisch scannen (präzise, technisch)
Wenn du die Videodatei lokal hast (empfohlen), kannst du Kapitel-Startzeiten automatisiert extrahieren.

Voraussetzungen:
- `ffmpeg` muss installiert sein und im PATH liegen (`ffmpeg` + `ffprobe`)
- Video-Datei lokal (z.B. Export aus deinem Editor)

Popeye (Beispiel):
1) In `code/frontend`:
   - `npm run yt:scan-chapters -- --video "D:\\path\\to\\popeye_marathon.mp4" --titles "..\\..\\docs\\METADATA_POPEYE_MARATHON_3gzbxznJ_PM.txt" --out "..\\..\\docs\\youtube\\3gzbxznJ_PM_chapters.generated.txt"`
2) Output-Datei öffnen und in die YouTube-Beschreibung kopieren.

Batch (alle Kompilationen nachträglich):
1) Lege deine lokalen Videodateien in einen Ordner und benenne sie so, dass die YouTube-ID im Dateinamen enthalten ist (z.B. `3gzbxznJ_PM_popeye.mp4`).
2) In `code/frontend`:
   - `npm run yt:scan-chapters:batch -- --videosDir "D:\\Your\\Exports"`
   - Output landet in `docs/youtube/chapters/<ytId>.txt`
3) Danach: `npm run yt:pack` (regeneriert `docs/youtube/*.md` und nimmt die Kapitel automatisch mit, wenn vorhanden)

Tuning (falls Cuts nicht perfekt erkannt werden):
- `--minGapSec 240` (min. Abstand zwischen Episoden-Starts)
- `--targetGapSec 405` (typische Episode-Länge ~6:45)
- `--episodes N` (falls du kein `--titles` File verwendest)

## 3) Warum ich nicht „alles“ direkt auf YouTube fertig machen kann
- Ohne Zugriff auf dein YouTube Studio / OAuth Token kann ich keine Titel/Beschreibungen/Playlist-Zuordnung/Chapters live ändern.
- „Millisekundengenau scannen“ geht nur mit Zugriff auf die Videodatei oder einem Analyse-Workflow (z.B. Download/Local File + Scene-Detect). Das ist aktuell nicht Teil dieses Workspaces.

## 4) Wenn du willst, dass ich wirklich 100% automatisch veröffentliche
Dann brauche ich **eine von zwei Optionen**:
1) **YouTube Data API OAuth** (Channel Owner) + Freigabe, damit der Backend-Service Updates schreiben darf (Title/Description/Playlists).
2) Oder die **Videodatei lokal** (oder exportiertes Kapitel-EDL), damit ich Cutpoints automatisch detecten kann.

Sobald du eine Option freigibst, kann ich die Kapitel und Metadaten „end-to-end“ automatisch pushen.
