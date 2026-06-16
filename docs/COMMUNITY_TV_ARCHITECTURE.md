# 📺 frai.tv CommunityTV — Architecture & Research

> **Stand: 2026-02-19 | Version 1.0**
> **Ziel:** Interaktives Community-Dashboard auf frai.tv das YouTube-Livestreams mit Echtzeit-Voting & Playlist-Steuerung verbindet.

---

## 🔬 INTERNET-ANALYSE: State of the Art

### Existierende Plattformen (analysiert)

| Plattform | Konzept | Stärken | Schwächen | Relevanz |
|-----------|---------|---------|-----------|----------|
| **CyTube** (cytu.be) | Sync-Watch Räume mit Playlist-Queue + Chat | Open-Source (MIT), Voting, User-Queues, 1.6k⭐ | Veraltet (CoffeeScript), kein modernes UI, kein YouTube Live Integration | ⭐⭐⭐⭐ Kernkonzept! |
| **WatchParty** | Browser-sync für YouTube/Files + Chat + Video-Chat | Playlists, Sync-Play, Discord-Bot, Open-Source | Nur Watch-Together, kein Voting, kein Live-Stream-Control | ⭐⭐⭐ UI-Inspiration |
| **Watch2Gether** (w2g.tv) | Sync-Watch Rooms mit YouTube | Einfaches UX, mobil-freundlich | Closed-Source, kein Community-Voting | ⭐⭐ Nur UX-Referenz |
| **Hyperbeam** | Virtual Browser Embed (API) | Multi-User Control, 10k participants | Teuer ($0.007/min), Overkill für unser Use-Case | ⭐ Nicht relevant |
| **Stremio** | Media Center mit Addon-System | 30M Users, Plugin-Architektur | Desktop-App, kein Web-Community-Feature | ⭐ Addon-Konzept interessant |
| **Agora.io** | Real-time Video SDK | Ultra-low-latency, global CDN | Teuer, für Video-Calls gedacht | ❌ Nicht passend |

### YouTube Live API — Schlüssel-Features

| Feature | API | Quota | Nutzen für uns |
|---------|-----|-------|----------------|
| **Live Chat lesen** | `liveChatMessages.list` | 5 Units/call | Chat-Commands für Voting ("!vote 1") |
| **Live Chat schreiben** | `liveChatMessages.insert` | 50 Units | Bot-Antworten, Abstimmungs-Ergebnisse |
| **Live Chat streamen** | `liveChatMessages.streamList` | Low-latency SSE | ⭐ Echtzeit-Chat-Monitor! |
| **Polls (nativ)** | `liveChatMessages.insert` (pollEvent) | 50 Units | YouTube-native Umfragen im Chat |
| **Broadcast Info** | `liveBroadcasts.list` | 1 Unit | Stream-Status, Viewer-Count |
| **Live Chat ID** | `snippet.liveChatId` | via Broadcast | Verknüpfung Stream ↔ Chat |

### 🆕 Was KEINER macht (unsere Innovation)

```
┌─────────────────────────────────────────────────────────────┐
│  💡 DIE INNOVATION: "Second Screen Control"                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PROBLEM: YouTube Live hat Chat, aber keine Steuerung.      │
│  CyTube hat Steuerung, aber keinen YouTube Live Stream.     │
│                                                             │
│  UNSERE LÖSUNG: frai.tv als "Second Screen" Dashboard       │
│                                                             │
│  📺 YouTube = Video-Output (der Stream läuft dort)          │
│  🖥️ frai.tv  = Control Panel (Community steuert dort)       │
│                                                             │
│  → Voting auf frai.tv bestimmt was als NÄCHSTES läuft       │
│  → StreamPilot liest Votes und wechselt Episode             │
│  → YouTube-Chat-Commands als Fallback ("!vote 3")           │
│  → Dashboard zeigt: Timeline, Infos, nächste Episoden       │
│                                                             │
│  = WELTWEIT EINZIGARTIG für Public Domain Content!          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ ARCHITEKTUR: CommunityTV

### Übersicht

```
┌──────────────────────────────────────────────────────────────────┐
│                        frai.tv ECOSYSTEM                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    WebSocket     ┌──────────────────┐          │
│  │  frai.tv     │◄──────────────►│  CommunityTV     │          │
│  │  Dashboard   │   (Socket.IO)   │  Backend         │          │
│  │  (React)     │                 │  (Node/Express)  │          │
│  └──────┬──────┘                 └────────┬─────────┘          │
│         │                                  │                     │
│         │ YouTube Embed                    │ REST API            │
│         ▼                                  ▼                     │
│  ┌─────────────┐                 ┌──────────────────┐          │
│  │  YouTube     │                 │  StreamPilot     │          │
│  │  Live Player │                 │  (FFmpeg Engine)  │          │
│  │  (iframe)    │                 │  wochenschautv.py │          │
│  └─────────────┘                 └────────┬─────────┘          │
│                                           │                     │
│                                           ▼                     │
│                                  ┌──────────────────┐          │
│                                  │  YouTube RTMP     │          │
│                                  │  Live Ingest      │          │
│                                  └──────────────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Daten-Flow: Voting → Stream-Steuerung

```
User klickt "Vote" auf frai.tv
        │
        ▼
[1] WebSocket → CommunityTV Backend
        │
        ▼
[2] Backend speichert Vote (SQLite/JSON)
    + broadcastet Live-Ergebnis an alle Clients
        │
        ▼
[3] Voting-Timer läuft ab (z.B. 60 Sek vor Episode-Ende)
        │
        ▼
[4] Backend sendet Gewinner-Episode an StreamPilot API
        │
        ▼
[5] StreamPilot queued nächste Episode in FFmpeg-Pipeline
        │
        ▼
[6] YouTube-Stream zeigt neue Episode
    + Bot postet Ergebnis im YouTube Live Chat
        │
        ▼
[7] frai.tv Dashboard aktualisiert:
    - "Now Playing" Info
    - Timeline-Position
    - Nächste Voting-Runde startet
```

---

## 📋 FEATURE-MATRIX

### Phase 1: MVP (2-3 Wochen)

| Feature | Beschreibung | Tech |
|---------|-------------|------|
| **Live Embed** | YouTube-Stream eingebettet auf frai.tv | YouTube IFrame API |
| **Now Playing** | Aktuelle Episode, Datum, Event, Timeline | WebSocket from StreamPilot |
| **Episode Queue** | Nächste 5-10 Episoden anzeigen | REST API |
| **Voting** | 3 Episoden zur Wahl, 60-Sek Timer | WebSocket + React State |
| **Viewer Count** | Aktive User auf frai.tv | Socket.IO `connected` |
| **Chat Mirror** | YouTube Live Chat neben dem Player | YouTube Live Chat Embed |

### Phase 2: Community (4-6 Wochen)

| Feature | Beschreibung | Tech |
|---------|-------------|------|
| **User Accounts** | Login via YouTube OAuth (optional) | OAuth 2.0 |
| **Playlist Builder** | User erstellen eigene Playlists aus 252 Episoden | React DnD + SQLite |
| **Episode-Wiki** | Historischer Kontext pro Episode | Markdown + MDX |
| **Chat Commands** | `!vote 1`, `!skip`, `!queue` im YouTube Chat | Live Chat API Polling |
| **Reactions** | Emoji-Reactions in Echtzeit (🔥 ❤️ 😮) | WebSocket Broadcast |
| **Schedule** | Wochenprogramm: Mo=Wochenschau, Di=Betty Boop... | Cron Config |

### Phase 3: Social (8-12 Wochen)

| Feature | Beschreibung | Tech |
|---------|-------------|------|
| **Leaderboard** | Top-Voter, aktivste Community-Members | Points System |
| **Theme Nights** | "D-Day Spezial", "1943 Rückblick" | Curated Playlists |
| **Multi-Channel** | Wechsel zwischen WochenschauTV / CartoonTV | StreamPilot Channels |
| **Mobile App** | PWA für unterwegs | Service Worker + Manifest |
| **Clips** | User markieren Highlights → Shorts-Kandidaten | Timestamp Bookmarks |

---

## 🛠️ TECH-STACK ENTSCHEIDUNG

### Frontend: React + Vite (bestehendes frai.tv!)

```
Begründung:
✅ frai.tv existiert bereits als React/Vite App
✅ framer-motion schon installiert (Animationen)
✅ Nur neue Pages/Components hinzufügen
✅ Kein Framework-Wechsel nötig!

Neue Dependencies:
+ socket.io-client     → WebSocket-Kommunikation
+ @tanstack/react-query → Server State Management
+ react-router-dom     → Routing (Projector + CommunityTV)
```

### Backend: Express + Socket.IO (bestehendes Backend erweitern!)

```
Begründung:
✅ Express-Backend existiert bereits (code/backend/)
✅ YouTube OAuth bereits implementiert
✅ YouTube Live Service existiert (youtubeLive.js)
✅ Prisma/DB-Anbindung existiert

Neue Dependencies:
+ socket.io            → WebSocket Server
+ better-sqlite3       → Leichtgewichtige Voting-DB (Alternative zu Prisma)
```

### Kommunikation: StreamPilot ↔ Backend

```python
# StreamPilot REST API (neu zu bauen)
GET  /api/stream/status      → {playing: "Ep.491", progress: 0.65, viewers: 12}
GET  /api/stream/queue        → [{ep: 492, title: "..."}, ...]
POST /api/stream/next         → {episode: 495}  (Voting-Gewinner)
POST /api/stream/skip         → Skip aktuelle Episode
GET  /api/episodes            → Alle 252 Episoden mit Metadata
GET  /api/episodes/:nr/wiki   → Historischer Kontext
```

---

## 📐 UI/UX DESIGN

### Dashboard Layout (Desktop)

```
┌──────────────────────────────────────────────────────────┐
│  🎬 frai.tv Community TV                    👥 47 Online │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────┐  ┌───────────────────┐ │
│  │                             │  │ 💬 LIVE CHAT      │ │
│  │     YouTube Live Stream     │  │                   │ │
│  │        (Embed 16:9)         │  │ User1: Wow, 1943! │ │
│  │                             │  │ User2: !vote 2    │ │
│  │                             │  │ Bot: Voting open! │ │
│  └─────────────────────────────┘  │                   │ │
│                                    │                   │ │
│  ┌─────────────────────────────┐  └───────────────────┘ │
│  │ 📺 NOW PLAYING                                       │
│  │ Wochenschau Nr. 491 | 12.10.1939                    │
│  │ Event: Poland Campaign                               │
│  │ ██████████░░░░░░░░░░ 48% (1939────────────1945)     │
│  └──────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 🗳️ VOTE FOR NEXT EPISODE          ⏱️ 0:47 remaining │ │
│  │                                                      │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │ Nr. 495  │  │ Nr. 512  │  │ Nr. 530  │          │ │
│  │  │ Oct 1939 │  │ Mar 1940 │  │ Aug 1940 │          │ │
│  │  │ Warsaw   │  │ Norway   │  │ Britain  │          │ │
│  │  │  ██ 34%  │  │ ████ 58% │  │  █ 8%    │          │ │
│  │  │ [VOTE]   │  │ [VOTE]✓  │  │ [VOTE]   │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘          │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 📋 COMING UP (Queue)                                 │ │
│  │  1. Nr. 512 — Norway Campaign (Voting Winner!)       │ │
│  │  2. Nr. 513 — Western Front                          │ │
│  │  3. Nr. 514 — Home Front                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                          │
│  1939 ●━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1945  │
│       ▲ Now                                              │
└──────────────────────────────────────────────────────────┘
```

### Dashboard Layout (Mobile)

```
┌────────────────────────┐
│ 🎬 frai.tv   👥 47     │
├────────────────────────┤
│ ┌────────────────────┐ │
│ │  YouTube Embed     │ │
│ │     (16:9)         │ │
│ └────────────────────┘ │
│                        │
│ 📺 Nr.491 | 12.10.39  │
│ Poland Campaign        │
│ ████████░░░░ 48%       │
│                        │
│ 🗳️ VOTE    ⏱️ 0:47    │
│ ┌────┐┌────┐┌────┐    │
│ │ 495││ 512││ 530│    │
│ │34% ││58% ││ 8% │    │
│ └────┘└────┘└────┘    │
│                        │
│ 💬 Chat ──────────     │
│ [Expandable Panel]     │
└────────────────────────┘
```

---

## 🔗 INTEGRATION MIT BESTEHENDER INFRASTRUKTUR

### Was schon existiert (WIEDERVERWENDEN!)

| Komponente | Pfad | Status |
|-----------|------|--------|
| React Frontend | `code/frai-tv/` | ✅ Vite + React 18, Projector-Page |
| Express Backend | `code/backend/` | ✅ Express + YouTube OAuth + Live API |
| StreamPilot | `tools/streampilot/` | ✅ Multi-Channel Manager |
| WochenschauTV | `scripts/youtube/wochenschautv.py` | ✅ 4K Stream Engine |
| Episode DB | `config/wochenschau_complete_upload_database.json` | ✅ 252 Episoden |
| Events | `config/wochenschau_events.json` | ✅ DE/EN Events |
| Locations | `config/wochenschau_complete_locations.json` | ✅ GPS Koordinaten |
| YouTube OAuth | `code/backend/src/services/youtubeOAuth.js` | ✅ Token-Flow |
| YouTube Live | `code/backend/src/services/youtubeLive.js` | ✅ Live-Stream-Scan |

### Was NEU gebaut werden muss

| Komponente | Beschreibung | Aufwand |
|-----------|-------------|---------|
| **CommunityTV Page** | React-Page mit Player, Voting, Queue | 3-4h |
| **WebSocket Server** | Socket.IO Integration ins Backend | 2h |
| **Voting Engine** | Vote-Logik, Timer, Auswertung | 2-3h |
| **StreamPilot API** | REST-Endpoints für Stream-Steuerung | 2h |
| **Stream State Bridge** | Python → Node Status-Sync | 1-2h |
| **Episode API** | Episoden-Daten als REST-Service | 1h |

**Total Initial: ~12-15h für MVP**

---

## 📁 DATEI-STRUKTUR (geplant)

```
code/frai-tv/src/
├── App.jsx                          # + React Router
├── pages/
│   ├── ProjectorPage.jsx            # Bestehendes Kino (unverändert)
│   └── CommunityTV.jsx              # ⭐ NEU: Live-Dashboard
├── components/
│   └── community/
│       ├── LivePlayer.jsx           # YouTube Embed + Status
│       ├── VotingPanel.jsx          # Episode-Voting mit Timer
│       ├── NowPlaying.jsx           # Aktuelle Episode + Timeline
│       ├── ChatPanel.jsx            # YouTube Chat Embed
│       ├── EpisodeQueue.jsx         # Kommende Episoden
│       ├── ViewerCounter.jsx        # Online-User Anzeige
│       ├── ReactionBar.jsx          # Emoji-Reactions
│       └── TimelineBar.jsx          # 1939━━━━━━1945 Visualisierung
├── hooks/
│   └── useSocket.js                 # Socket.IO Hook
├── data/
│   └── projectorData.js             # Bestehendes Video-Data
└── styles/
    ├── projector.css                # Bestehendes Styling
    └── community.css                # ⭐ NEU: CommunityTV Styling

code/backend/src/
├── index.js                         # + Socket.IO Setup + neue Routes
├── services/
│   ├── youtubeImporter.js           # Bestehend
│   ├── youtubeOAuth.js              # Bestehend
│   ├── youtubeLive.js               # Bestehend
│   ├── dbClient.js                  # Bestehend
│   ├── youtubeAdminSync.js          # Bestehend
│   ├── votingEngine.js              # ⭐ NEU: Voting-Logik
│   ├── streamBridge.js              # ⭐ NEU: StreamPilot ↔ Backend
│   └── episodeService.js            # ⭐ NEU: Episode-Daten-Service
└── data/
    └── episodes.json                # Symlink → config/wochenschau_complete_upload_database.json

tools/streampilot/
├── __main__.py                      # + REST API Server Mode
└── api.py                           # ⭐ NEU: Flask/FastAPI Mini-Server
```

---

## 🔐 SICHERHEIT & REGELN

### YouTube ToS Compliance

```
✅ Stream-Embed erlaubt (enableEmbed = true)
✅ YouTube Live Chat Embed ist offiziell supportet
✅ Voting ist USER-initiated (kein Bot-Spam)
✅ Keine View-Manipulation (User sehen echten YouTube-Stream)
⚠️ Chat-Bot muss Rate-Limits beachten (max 1 msg / 5 Sek)
⚠️ Kein automatisches privacyStatus-Ändern (SG-7!)
```

### Rate Limits

| Aktion | Limit | Unsere Nutzung |
|--------|-------|----------------|
| Chat lesen (polling) | 5 Units / call, 10k/Tag | 1 call / 10 Sek = 8.640/Tag ✅ |
| Chat lesen (streaming) | 1 connection | Ideal! Spart Quota |
| Chat schreiben | 50 Units / msg | Max 20 Bot-msgs/Tag = 1.000 Units |
| Broadcast status | 1 Unit / call | 1 call / 30 Sek = 2.880/Tag ✅ |

### Privacy

```
✅ Kein User-Tracking auf frai.tv
✅ Voting ist anonym (Session-based, kein Login nötig)
✅ Optional: YouTube OAuth für personalisierte Features
✅ Keine Cookies außer Session-Cookie
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Sprint 1: Skeleton (Tag 1-2)
- [ ] React Router in frai.tv (Projector + /live)
- [ ] CommunityTV Page Layout (responsive)
- [ ] YouTube IFrame Embed
- [ ] Socket.IO Setup (Frontend + Backend)
- [ ] Viewer Counter (verbundene Clients)

### Sprint 2: Core Voting (Tag 3-5)
- [ ] Voting Engine Backend (3 Kandidaten, Timer, Auswertung)
- [ ] VotingPanel Component mit Countdown
- [ ] NowPlaying Component mit Episode-Info
- [ ] Episode API (252 Wochenschau-Episoden)
- [ ] WebSocket-Events: vote, result, nowPlaying, queue

### Sprint 3: Stream Integration (Tag 6-8)
- [ ] StreamPilot REST API (Python FastAPI)
- [ ] Stream State Bridge (Python → Node)
- [ ] "Next Episode" Command → StreamPilot
- [ ] Timeline-Visualisierung (1939-1945)
- [ ] Queue-Anzeige

### Sprint 4: Polish & Launch (Tag 9-12)
- [ ] YouTube Live Chat Embed
- [ ] Emoji Reactions (🔥 ❤️ 😮)
- [ ] Mobile-responsive Design
- [ ] Deploy auf frai.tv (Vercel/Netlify für Frontend)
- [ ] Backend auf eigenem Server (PM2)

---

## 💡 INNOVATIVE FEATURES (USPs)

### 1. "Time Machine" Navigation
```
Statt langweiliger Episode-Liste:
Timeline-Slider 1939━━━━━━━━━━━━━━━━━━━━1945
User "reist" durch die Zeit, sieht Events auf einer Karte.
Voting bestimmt, wohin die Zeitreise als nächstes geht.
```

### 2. "War Map" Live-Overlay
```
Interaktive Karte (Leaflet.js) zeigt:
- 📍 Aktueller Schauplatz der Episode (aus GPS-Daten!)
- 🔴 Frontverläufe (animiert über die Zeit)
- 📌 Alle 252 Episoden als Pins
User können auf Pins klicken → Episode in Queue
```

### 3. "Historian Mode"
```
Toggle für historischen Kontext:
- Hintergrund-Info zu jedem Event
- Wikipedia-Links
- Zeitgenössische Fotos
- "Was geschah noch an diesem Tag?"
```

### 4. "Community Playlist" Builder
```
User erstellen eigene Themen-Playlists:
- "Die Ostfront" (nur Russland-Episoden)
- "Homefront Deutschland" 
- "D-Day bis Kriegsende"
Community voted für beste Playlists → werden gestreamt!
```

### 5. "Chat Commands" (YouTube ↔ frai.tv Bridge)
```
YouTube Chat:           frai.tv Dashboard:
!vote 1/2/3      ↔     Click "Vote" Button
!skip             ↔     Click "Skip" Button  
!queue            ↔     Shows Queue
!info             ↔     Shows Episode Info
!time             ↔     Shows Timeline Position
```

---

## 📊 DEBATTE: TECH-ENTSCHEIDUNGEN

### Debatte: WebSocket-Provider

| Rolle | Position | Argument |
|-------|----------|----------|
| Lead Architect (15) | Socket.IO | Rooms, Reconnect, Fallback — alles built-in |
| Backend (8) | Socket.IO | Express-Integration trivial, Python-Client existiert |
| Frontend (8) | Socket.IO | React-Hook-Pattern etabliert, `socket.io-client` nur 10.4kB |
| Performance (4) | Raw WS | Weniger Overhead (4 Bytes vs ~20 Bytes) |
| DevOps (9) | Socket.IO | Einfacher zu deployen, CDN-freundlich (HTTP fallback) |

**Ergebnis: Socket.IO (40) vs Raw WS (4) → Socket.IO ✓**

### Debatte: Voting-Persistenz

| Rolle | Position | Argument |
|-------|----------|----------|
| Lead Architect (15) | In-Memory + File | Voting ist ephemeral, kein DB nötig |
| Data Engineering (7) | SQLite | Statistiken, History, Analytics |
| Backend (8) | In-Memory | Schnellster Path, < 100 concurrent users |
| QA (7) | SQLite | Testbar, reproduzierbar |

**Ergebnis: In-Memory MVP (23) + SQLite Phase 2 (14) → In-Memory zuerst ✓**

---

## 🎯 NEXT STEPS

1. **JETZT:** React Router + CommunityTV-Skeleton in `code/frai-tv/`
2. **JETZT:** Socket.IO ins Backend integrieren
3. **JETZT:** VotingPanel + NowPlaying Components bauen
4. **DANN:** StreamPilot REST API
5. **DANN:** Deploy + Testen mit echtem Livestream
