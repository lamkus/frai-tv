# TODO_MANIFEST.md – Backlog & Task Tracking

> CrossDomain Orchestrator v3: Zentrales Task-Management mit IDs, Status, Priorität und Risiko.
> **Last Updated: 2024-12-10 18:00**

---

## Status-Legende

| Status | Bedeutung |
|--------|-----------|
| `IDEA` | Konzeptphase, noch nicht analysiert |
| `DISCOVERY` | In Analyse/Recherche |
| `DESIGN` | Architektur/Design in Arbeit |
| `DRAFT` | Erster Entwurf erstellt |
| `IMPLEMENTING` | In aktiver Entwicklung |
| `REVIEW` | Code Review / QA |
| `TESTING` | In Test-Phase |
| `STAGING` | Auf Staging deployed |
| `DONE` | Abgeschlossen |
| `BLOCKED` | Blockiert (Abhängigkeit dokumentieren) |

## Priorität

| Prio | Bedeutung |
|------|-----------|
| P0 | Kritisch – Sofort |
| P1 | Hoch – Diese Iteration |
| P2 | Mittel – Nächste Iteration |
| P3 | Niedrig – Backlog |

---

## ✅ Completed (2024-12-11)

| ID | Title | Notes |
|----|-------|-------|
| T-097 | **Hero Billboard Cinematic** | Netflix/Disney+ full-bleed hero design |
| T-053 | **Skeleton Loaders** | MediathekSkeleton with HeroSkeleton, ContentRowSkeleton |
| T-054 | **Error States** | ErrorState component with NetworkError, ApiError, NotFound, Generic |
| T-055 | **Empty States** | EmptyState component integrated in Watchlist, History pages |
| T-056 | **404 Page Design** | Premium NotFoundPage with animations |
| T-057 | **Up Next / Autoplay** | UpNextOverlay mit Timer-Fallback für Video-Ende |
| T-058 | **Keyboard Navigation** | Escape, Space, K, M, F, Pfeiltasten im VideoPlayer |
| T-059 | **Still Watching Prompt** | Nach 4+ Stunden automatischer Prompt |
| T-060 | **Share Modal** | Social sharing mit X, Facebook, WhatsApp, Telegram, Reddit, Email |
| T-098 | **Category Detection** | Enhanced regex patterns + description fallback |
| T-096 | **Hero Carousel** | Top 5 Videos Slider in Mediathek |
| T-094 | **Remove External Links** | Removed "Watch on YouTube" from Modal/Detail |
| T-095 | **Mediathek Navigation** | Removed Sidebar, added Horizontal Filter |
| T-010 | **Search Filter** | Category/Decade Filter + History |
| T-051 | **Flaggen Sprachauswahl** | Emoji Flags in TopNav |
| T-092 | **MiniPlayer** | Picture-in-Picture, Unmuted |
| T-093 | **Global Theme Fix** | Gold Theme enforced |
| T-047 | **Doppelte Videos entfernt** | `dedupeVideos()` in MediathekPage |
| T-048 | **Clean Titles (4K/8K entfernt)** | `cleanTitle()` helper |
| T-049 | **Kategorie-Farben auf Thumbnails** | Farbige Badges oben links |
| T-070 | **AmbientPlayer Rewrite** | Kein muted autoplay, DSGVO Disclaimer |
| T-071 | **Watchlist Actions in VideoCard** | add/remove/isInWatchlist |
| T-072 | **Continue Watching Tracking** | VideoPlayer sendet Progress alle 5s |
| T-073 | **Backend API Endpoints** | /api/videos, /api/watch-progress |
| T-074 | **Prisma WatchProgress Model** | Server-seitige Progress-Speicherung |
| T-075 | **Admin Import mit maxResults** | 50/200/500/1000/5000 Selector |
| T-076 | **Full-Stack Deploy Script** | `deploy-full.ps1` für Frontend+Backend |
| T-077 | **Timeline 1900+ Jahr-Erkennung** | Strict filtering & 1900-2030 support |
| T-078 | **Mock Data Fallback** | AppContext lädt Fallback wenn API fails |
| T-099 | **Backend Taxonomy Sync** | Aligned `youtubeImporter.js` with new categories |
| T-100 | **Search Cleanup** | Removed "Retro Tech" trending searches |
| T-101 | **Data Integrity** | Added missing 1970s to `remaikeData.js` |
| T-102 | **Security Hardening** | Removed hardcoded secrets, sanitized deploy scripts |
| T-103 | **Infrastructure Rescue** | Fixed Nginx/HTTPS config via `fix_server.sh` |
| T-104 | **Unlimited Import** | Patched `youtubeImporter.js` to fetch ALL videos |

## ✅ Completed (2024-12-09)

| ID | Title | Notes |
|----|-------|-------|
| T-025 | **FRai.TV Branding** | Logo, Footer, Header |
| T-026 | **Social Media Buttons** | YouTube, Instagram, TikTok, X |
| T-027 | **Legal Pages** | Impressum, Datenschutz |
| T-028 | **Category Colors** | getCategoryColor() helper |
| T-029 | **Modal Styling** | Gold/Red Akzente |
| T-030 | **Video Fallback Data** | Echte YouTube IDs |
| T-031 | **Feature Flags** | VITE_EXPERIMENTAL_FEATURES |
| T-032 | **Experimental Hidden** | TV Guide/Mindmap hinter Flag |
| T-036 | **VideoInfoModal** | Play/Watchlist/Share Popup |
| T-037 | **Info-Button auf Cards** | Alle VideoCards |
| T-038 | **Dashboard Toggle entfernt** | Ein View |
| T-039 | **Social Buttons Style** | Clean white/gray |

---

## 🔧 In Progress

| ID | Title | Status | Prio | Owner |
|----|-------|--------|------|-------|
| T-086 | **Bubblewrap Setup** | TODO | P1 | - |

---

## 📋 Backlog (Priorisiert)

### P0 - Für v1.0 Release

✅ **All P0 tasks completed!** (T-053, T-054, T-055, T-056)

### P1 - Nach v1.0

✅ **All P1 core tasks completed!** (T-057, T-058, T-059, T-060)

| ID | Title | Aufwand | Status |
|----|-------|---------|--------|
| T-050 | **i18n Vollständig** | 4h | ✅ DONE |
| T-019 | **Accessibility Audit** | 4h | ✅ DONE |

### P2 - v1.1

| ID | Title | Aufwand | Status |
|----|-------|---------|--------|
| T-061 | **Personalisierte Empfehlungen** | 8h | ✅ EXISTS |
| T-062 | **Admin: Video Editor** | 6h | ✅ DONE |
| T-063 | **Admin: Analytics** | 8h | ✅ EXISTS |
| T-064 | **Livestream Integration** | 8h | ✅ DONE |

### P3 - Backlog

| ID | Title | Aufwand | Status |
|----|-------|---------|--------|
| T-065 | **TV Guide Fix** | 16h | ✅ DONE |
| T-066 | **Mindmap Fix** | 16h | ✅ DONE |
| T-067 | **User Accounts** | 24h | IDEA |
| T-068 | **Playlists API** | 8h | ✅ DONE |
| T-069 | **Comments** | 16h | IDEA |

---

## 📺 YouTube Kanal Optimierung (NEW - 2024-12-12)

> Siehe detaillierte Anleitung: `docs/YOUTUBE_CHANNEL_OPTIMIZATION.md`

| ID | Title | Aufwand | Status | Prio |
|----|-------|---------|--------|------|
| T-110 | **YouTube Playlisten erstellen** | 2h | IN_PROGRESS | P0 |
| T-111 | **Serien-Playlisten (Superman, Popeye, etc.)** | 1h | DONE | P0 |
| T-112 | **Thematische Playlisten (Horror, Christmas)** | 1h | TODO | P0 |
| T-113 | **Kapitelmarker für Kompilationen** | 2h | IN_PROGRESS | P1 |
| T-114 | **Channel-Startseite Sections** | 1h | TODO | P1 |
| T-115 | **Thumbnail-Standardisierung** | 4h | TODO | P2 |
| T-116 | **Video-Titel Konventionen** | 2h | TODO | P2 |
| T-117 | **Serien-Seite im Frontend** | 4h | DONE | P2 |
| T-118 | **Playlist-Sync (YT → App)** | 4h | TODO | P2 |

## 🎬 AAA / Netflix-Grade Mediathek (5.000 Videos)

> Blueprint: `docs/NETFLIX_GRADE_YOUTUBE_MEDIATHEK_BLUEPRINT.md`

| ID | Title | Aufwand | Status | Prio |
|----|-------|---------|--------|------|
| T-119 | **5k Catalog: API Pagination/Search** | 4h | DONE | P0 |
| T-120 | **DB-first Catalog Import (nightly)** | 6h | IN_PROGRESS | P0 |
| T-121 | **Admin: Library QA Report** | 6h | TODO | P1 |
| T-122 | **Home Rails: Progressive Loading** | 8h | TODO | P1 |
| T-123 | **Virtualized Lists for 5k** | 6h | TODO | P1 |

### YouTube Playlisten Checkliste:

- [ ] 🦸 Superman - Fleischer Studios Collection (1941-1943)
- [ ] ⚓ Popeye - Classic Cartoons (1930s-1950s)
- [ ] 💋 Betty Boop - Fleischer Collection (1930s)
- [ ] 🎩 Charlie Chaplin - Silent Comedy Classics
- [ ] 😐 Buster Keaton - Silent Comedy Genius
- [ ] 🎄 Weihnachts-Specials / Christmas Classics
- [ ] 👻 Horror-Klassiker / Classic Horror
- [ ] 🎬 Fritz Lang Collection
- [ ] 📽️ Stummfilm-Meisterwerke
- [ ] ☢️ Cold War Archives
- [ ] 🎖️ WWII Dokumentationen
- [ ] 🎨 Early Animation Pioneers (1900-1920)
- [ ] 🌟 Neu hier? Start Here! / Best of remAIke

---

## 📱 App Store Publishing (NEW)

| ID | Title | Aufwand | Status | Prio |
|----|-------|---------|--------|------|
| T-080 | **PWA Icons erstellen** | 2h | ✅ DONE | P0 |
| T-081 | **manifest.json** | 30min | ✅ DONE | P0 |
| T-082 | **Service Worker** | 30min | ✅ DONE | P0 |
| T-083 | **InstallPrompt Component** | 30min | ✅ DONE | P0 |
| T-084 | **Lighthouse PWA Audit** | 1h | ✅ DONE | P0 |
| T-085 | **assetlinks.json (TWA)** | 30min | ✅ DONE | P1 |
| T-086 | **Bubblewrap Setup** | 2h | TODO | P1 |
| T-087 | **Google Play Console** | 2h | TODO | P1 |
| T-088 | **Store Screenshots** | 4h | TODO | P1 |
| T-089 | **Capacitor iOS Setup** | 4h | TODO | P2 |
| T-090 | **Apple Developer Account** | 2h | TODO | P2 |
| T-091 | **Push Notifications** | 8h | TODO | P2 |

---

## 🏗️ Technical Debt

| Item | Prio | Status |
|------|------|--------|
| Vite Dynamic Import Warnings | P2 | TODO |
| ESLint Warnings | P2 | TODO |
| Test Coverage > 50% | P1 | TODO |
| Lighthouse > 90 | P1 | TODO |
| Bundle Size Optimize | P2 | TODO |

---

## 🔴 Blocked

| ID | Blocked By | Action |
|----|------------|--------|
| Backend Live | Strato Hosting Setup | User kümmert sich |

---

## Feature Flags

```env
# Production
VITE_EXPERIMENTAL_FEATURES=false
VITE_ENABLE_ADMIN=false

# Development  
VITE_EXPERIMENTAL_FEATURES=true
VITE_ENABLE_ADMIN=true
```

---

*Last Updated: 2024-12-10 18:00*
