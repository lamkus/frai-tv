# YouTube Execution Backlog (2026 Q1) – remAIke_IT

Ziel: **Watchtime-first** (Binge/Playlists/Session Flow) + solide **Search-Basis** (Relevance/Quality), strikt quota-sicher.

## Guardrails (nicht verhandelbar)
- READ immer **Public API** (`YOUTUBE_API_KEY`), OAuth nur für WRITE.
- **Keine Deletes per API** (PlaylistItems.delete etc.). Wenn nötig: manuell in YouTube Studio.
- Bei `quotaExceeded`: **sofort stoppen**, nichts „weiter probieren“.

## 0) Reset-Ready Setup (1x)
- [ ] `YOUTUBE_API_KEY` als Env Var setzen (lokal + Deploy).
- [ ] Sicherstellen, dass keine Keys im Repo sind (ist aktuell clean).

## 1) Watchtime-Repair: Alfred Playlist wieder korrekt (P0)
**Warum:** Broken Playlist killt Up Next/Session.

**Vorgehen (quota-sicher):**
1. Studio: Playlist öffnen → wenn falsch/teilkaputt → manuell bereinigen (0 Quota).
2. Offline: `config/watchtime_playlists.json` prüfen (Reihenfolge Episode 1..52).
3. Apply: Nur Inserts (OAuth, 50 Units/Video) – in kleinen Batches, mit Stop bei Quota.

**Definition of Done:** Playlist hat alle 52 Folgen in korrekter Reihenfolge.

## 2) Tag Upgrade rollout (P1)
**Warum:** Search-Relevance ist 1/3 Search-Ranking (offiziell) und hilft auch bei Klarheit.

**Status:** Offline Plan existiert.
- Input: `config/videos.json`
- Output: `config/tags_plan.json`, `config/tags_plan_report.json`

**Nächster Schritt:** Apply-Script (OAuth) bauen, das:
- pro Video `tags_csv` aus Plan setzt,
- 500-Zeichen Limit garantiert,
- `--dry-run` kann,
- optional `--limit N` für Quota-Schutz.

## 3) Chapters/Timestamps (P1)
**Warum:** Satisfaction/Navigation; hilft Binge-Führung.

**Regel:** Keine geschätzten Chapters. Nur echte Kapitel (lokal via Datei/ffmpeg oder verifizierte Quellen).

**Workflow:**
- Für Compilations: lokale File + ffmpeg Cut/Scene Detect → `docs/youtube/chapters/<ytId>.txt`.
- Für Serien-Episoden: minimalistische Chapters (Intro/Outro) nur wenn wahr und konsistent.

## 4) Titles/Descriptions Konsistenz (P2)
**Ziel:** Relevance + klare Erwartung (Satisfaction).
- Format stabilisieren: Serie (x/y) + Jahr + 8K + Brand.
- Description: erster Absatz keywords + Playlist-Link + Subscribe CTA + Hashtags.

## 5) Metrics & Feedback Loop (P2)
**Was messen (Studio):**
- Browse/Home: Impressions → CTR → Avg View Duration
- Suggested: Anteil Suggested + Session-Continuation
- Search: Queries mit echter Watchtime (nicht nur Views)

## 6) Risk Register
- Quota: Inserts/Updates sind teuer (50 Units). Always batch.
- Over-automation: falsche Änderungen skalieren negativ. Erst offline planen, dann schreiben.
