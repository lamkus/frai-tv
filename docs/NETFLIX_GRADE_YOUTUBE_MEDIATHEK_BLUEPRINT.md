# Netflix-grade Mediathek on top of YouTube (Blueprint)

**Goal:** A Netflix/Disney+/Joyn-like browsing experience while **YouTube stays the hosting layer** (player, CDN, video storage).

This blueprint is tailored to this repo:
- Frontend: React/Vite SPA with TV-style navigation
- Backend: Express + optional Prisma/Postgres
- YouTube: Data API read + OAuth write (admin automation)

---

## 1) What “Netflix-grade” means here (realistic scope)

### We can make AAA
- Fast browse UX: hero + rails, instant search, snappy detail pages, smooth TV navigation.
- Strong library organization: series/seasons/episodes vs compilations, consistent titles/thumbnails, chapters.
- Personalization layer: continue-watching, history-based rails, diversity/exploration.
- Operational automation: playlist management, metadata pushes, consistency checks.

### YouTube will still constrain us
- Playback is an embedded YouTube player; true DRM/offline control is not achievable like Netflix.
- Some videos may be age-restricted / region-restricted and behave differently when embedded.
- API quotas and write limits require batching, caching, and scheduled jobs.

---

## 2) Information Architecture (IA) for 5,000 videos

### Canonical entities (DB-first model)
- **Video**: ytId, title/desc, duration, publishDate, thumbnail, view/like counts, tags.
- **Series**: id, title, synopsis, poster, sortOrder.
- **Season** (optional but recommended for pro optics): seriesId, number, title.
- **Collections / Compilations**: a curated “long-form” grouping (marathons, 4K/8K collections).
- **Playlist mapping**: YouTube playlist id ↔ internal collection/series rail.

### Practical mapping to YouTube
- **Series Episodes** ⇒ playlist `SERIES — Episodes`
- **Series Compilations** ⇒ playlist `SERIES — Compilations`
- Editorial rails (e.g. “Silent Comedy Classics”) ⇒ playlists or internal “virtual rails” built from tags.

You already have the automation path for this in:
- Backend series split/sync: [code/backend/src/services/youtubeAdminSync.js](../code/backend/src/services/youtubeAdminSync.js)

---

## 3) Product UX: Rails that feel like Netflix

Minimum set of rails that scales well to 5k:
- **Continue Watching** (personal)
- **New Releases** (global)
- **Trending / Most Watched** (global; needs stats)
- **Because you watched X** (personal; series/tag similarity)
- **Series Hubs** (rows of series posters)
- **Collections** (compilations/marathons)

Key UX rules:
- Never block home UI on loading the full catalog.
- Search must be instant and tolerate typos (DB-backed search).
- Avoid showing 5,000 items in one DOM list; use pagination/virtualization.

---

## 4) Data strategy for 100 → 5,000 videos

### Phase A (now): Stable catalog with pagination
- Move “load everything” to **API paging**.
- Backend should support:
  - `GET /api/videos?limit=...&cursor=...`
  - `GET /api/videos?q=...` (basic search)

This is now supported in the backend route:
- [code/backend/src/index.js](../code/backend/src/index.js)

### Phase B: DB becomes the source of truth
- Nightly import already exists (cron) if Prisma is enabled.
- Expand import to persist: duration, viewCount, tags (where quota allows).
- Add “denormalized” fields used by rails:
  - `popularityScore`, `freshnessScore`, `longTailScore`, `seriesId` (or derived key)

### Phase C: Fast search and fast home
- Indexing:
  - Postgres indexes on `publishDate`, `featured`, `hidden` already exist.
  - Add trigram / full-text for title/description (optional).
- Cache:
  - If Redis is not available on Strato, use in-process + file cache.

---

## 5) Recommendation & ranking (lightweight but powerful)

You already have a strong research-backed approach in:
- [docs/RECOMMENDATION_ALGORITHM.md](RECOMMENDATION_ALGORITHM.md)

For “AAA optics” the key is not perfect ML, it’s:
- **Good rails** + **good metadata** + **diverse ranking**.

Suggested scoring (simple, stable):
- $score = 0.45\cdot popularity + 0.35\cdot freshness + 0.20\cdot personalization$
- Add a diversity rerank pass (MMR) per rail.

Personalization signals you already capture:
- Watch progress / continue-watching via `WatchProgress`.

---

## 6) YouTube operations: “pro channel” at scale

### Metadata hygiene (must-have)
- Titles: consistent series prefix + episode numbering (if episodes exist).
- Descriptions: structured template + chapters (for compilations).
- Thumbnails: consistent style per series.

### Automation loop (weekly)
1) Import new uploads
2) Detect series + classification (episode vs compilation)
3) Sync playlists (create missing, add missing videos)
4) Generate “needs attention” report:
   - missing chapters, missing thumbnail standard, inconsistent titles

You already have step (3) implemented; step (4) is the next big leverage point.

---

## 7) Performance targets (what to measure)

For a Netflix-like feel, set measurable budgets:
- Home API: p95 < 200ms (cached)
- Search API: p95 < 300ms
- Time-to-first-meaningful-UI (TV): < 2.0s on mid devices
- Avoid loading > 200 videos per request by default

---

## 8) Execution roadmap (recommended)

### Milestone 1: “5k-ready backend” (1–2 days)
- Paginated `/api/videos` (done)
- Paginated/complete `/api/series` (done: clamp to 5k)
- Add a dedicated `/api/search` endpoint (optional; can reuse `/api/videos?q=`)

### Milestone 2: “DB-first catalog” (2–4 days)
- Ensure Prisma migrations + stable import job
- Store duration/stats if available
- Add admin report endpoint for inconsistencies

### Milestone 3: “AAA home rails” (frontend) (3–7 days)
- Home loads rails progressively, each rail paged
- Virtualize big lists
- Tune ranking + diversity

---

## 9) Open questions (need your decision)

1) Should “Series” be sourced from YouTube playlists (authoritative), or from detection rules (derived)?
2) Do you want seasons (S01/E01) for Popeye/Superman, or keep it flat?
3) Is Postgres always available in production, or do we need a no-DB fallback for the 5k catalog?
