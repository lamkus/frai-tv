# YouTube Algo 2026 – Creator Playbook (remAIke)

**Ziel:** Maximale Watchtime (Binge/Playlists) + solide Discovery (Search/Recommend), ohne Quota zu verbrennen.

## 1) Was YouTube offiziell sagt (Stand: Help Center ©2026)

### 1.1 Empfehlungen sind personalisiert (nicht „globaler Algo“)
YouTube vergleicht individuelle Sehgewohnheiten mit ähnlichen Nutzern und nutzt sehr viele Signale.
Wichtige, explizit genannte Signale:
- Watch History
- Search History
- Subscriptions
- Likes/Dislikes
- „Not interested“ / „Don’t recommend channel“ Feedback
- **Satisfaction surveys** (Zufriedenheits-Umfragen) – ausdrücklich *nicht nur Watchtime*

Quelle: https://support.google.com/youtube/answer/16089387

### 1.2 Unterschiedliche Flächen = unterschiedliche Prioritäten
- **Home** hängt stark an Watch History.
- **Up Next** hängt stark an „was du gerade schaust“.
- **Shorts Feed** ist personalisiert (eigene Feed-Logik).

Quelle: https://support.google.com/youtube/answer/16089387

### 1.3 Search-Ranking: Relevance + Engagement + Quality
YouTube nennt drei Kernelemente:
- **Relevance**: Match zwischen Query und Titel/Tags/Description/Video-Inhalt
- **Engagement**: u.a. Watchtime *für diese Query* als Relevanz-Indikator
- **Quality**: Signale, die Expertise/Authoritativeness/Trustworthiness unterstützen (topic-dependent)

Quelle: https://support.google.com/youtube/answer/16090438

### 1.4 Shorts-Metrik wurde geändert (2025 → wirkt 2026 weiter)
Ab 31.03.2025 zählen Shorts-Views als Starts/Replays ohne Mindestwatchtime; „Engaged views“ bleibt in Analytics.

Quelle: https://support.google.com/youtube/answer/10059070

## 2) Was Creator 2026 daraus praktisch ableiten (ohne Mythen)

### 2.1 „Long-term satisfaction“ ist das Fundament
Wenn Zufriedenheits-Surveys explizit ein Kernsignal sind, ist *Clickbait ohne Deliver* strukturell toxisch:
- kurzfristig CTR ↑
- mittelfristig „Not interested“ / „Don’t recommend“ / schlechte Satisfaction → Distribution ↓

### 2.2 Watchtime ist wichtig – aber nicht als reines „Minutes Farming“
Auf Home/Up Next zählt, ob der Viewer *weiterklickt/weiterguckt* und ob das Erlebnis zufriedenstellt.
Für euren Kanal heißt das: **Binge-konsistente Serienführung** + **Up Next Relevanz**.

### 2.3 Search ist ein anderes Spiel als Browse
Search kann über Relevance/Tags/Description profitieren, aber Engagement für die Query entscheidet mit.
Heißt: „SEO reinballern“ ohne gutes Video-Query-Fit bringt wenig.

## 3) Team-Entscheidung (Agents.md Debatte, kompakt)

**Fragestellung:** Für remAIke 2026: Priorität auf Watchtime/Playlists oder auf Search-SEO?

| Rolle (Gewicht) | Position | Begründung (1 Satz) |
|---|---|---|
| Lead Architect (15) | Watchtime-first | Playlists/Serien sind euer stärkster Hebel für Session-Time & Up Next-Fit. |
| Data Engineering (7) | Watchtime-first | Wir können binge-fähige Ordnung offline planen, quota-schonend ausspielen. |
| Frontend (8) | Balanced | Search/Discover braucht saubere Titel/Descriptions; UI kann Playlist-Entrypoints pushen. |
| Backend (8) | Balanced | Metadaten-Pipeline (Tags/Descriptions) muss robust sein, aber nicht overfitten. |
| Performance (4) | Watchtime-first | Höherer Session-Value pro Viewer ist effizienter als teure Broad-SEO-Experimente. |
| Legal/Privacy (je 2) | Neutral | Keine Änderung, nur darauf achten: keine Secrets, keine riskanten Scrapes. |

**Ergebnis:** Watchtime-first mit sauberer Search-Basis.

## 4) Konkrete Umsetzung im Repo (quota-safe)

### 4.1 Playlists
- **Ziel:** Up Next Relevanz + chronologische Serien = Binge.
- **Status:** Playlist-Optimierung existiert; Apply muss quota-sicher passieren (keine Deletes via API).

### 4.2 Chapters/Timestamps
- **Ziel:** bessere Navigation, höhere Zufriedenheit, bessere Session-Führung.
- **Regel:** Chapters nicht raten; nur echte Kapitel aus Quellen/Material.

### 4.3 Tags (Search-Relevance, nicht „Magic“)
- **Ziel:** max 15 Tags, max 500 Zeichen total, keine Spam-Duplikate. (YouTube: "Tags play a MINIMAL role")
- **Status:** Offline Tag-Plan wird generiert und kann später per OAuth angewendet werden.

## 5) Messplan (was ihr in Studio beobachten solltet)

- Browse/Home: Impressions → CTR → Average View Duration / Watchtime
- Suggested/Up Next: „Traffic source: Suggested“ + Session-Continuation
- Search: Queries, die wirklich Watchtime liefern (nicht nur Views)
- Satisfaction-Proxies: Kommentare, Likes/Dislikes, „Not interested“ (indirekt über Drops)

## 6) Limitierungen dieser Research-Runde

- Reddit/Foren-Inhalte konnten automatisiert nicht zuverlässig extrahiert werden (Cookie/Login-Walls).
- Daher basiert dieser Playbook-Teil bewusst auf offiziellen YouTube Help Center Aussagen + Ableitung.
