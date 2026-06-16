# 🏗️ System Architecture (v1.0)

## Current Production Architecture (Checkdomain-Only)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER DEVICES                               │
│  Desktop (Chrome/Firefox) • Mobile (iOS/Android) • Tablet           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CHECKDOMAIN HOSTING                            │
│  Domain: frai.tv • Static Site + PHP                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  index.html     │  │   api.php        │  │  data/           │  │
│  │  + React SPA    │◄─┤   (API Router)   │◄─┤  videos.json     │  │
│  │  + Vite Bundle  │  │                  │  │  analytics.ndjson│  │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘  │
│         │                     │                      ▲               │
│         │ Fetch               │ Read/Write           │               │
│         ▼                     ▼                      │               │
│  ┌─────────────────────────────────────────────────┐│              │
│  │  Endpoints:                                      ││              │
│  │  • GET  /api.php?path=health                    ││              │
│  │  • GET  /api.php?path=videos                    ││              │
│  │  • POST /api.php?path=analytics/event           ││              │
│  │  • GET  /api.php?path=analytics/summary         ││              │
│  │  • GET  /api.php?path=analytics/backup&key=...  ││              │
│  └─────────────────────────────────────────────────┘│              │
│                                                       │              │
└───────────────────────────────────────────────────────┼──────────────┘
                                                        │
                                                        │ Updated by
                                                        │ GitHub Actions
                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AI VIDEO SYNC (GitHub Actions)                 │
│  Cron: Daily 3 AM UTC • Manual Trigger                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────┐       ┌──────────────────┐                  │
│  │ sync-youtube-ai   │──────►│  YouTube Data    │                  │
│  │     .mjs          │       │  API v3          │                  │
│  │                   │       └──────────────────┘                  │
│  │  1. Fetch videos  │              ▼                               │
│  │  2. AI categorize │       ┌──────────────────┐                  │
│  │  3. Update JSON   │──────►│  OpenAI GPT-4    │                  │
│  │  4. Commit + Push │       │  (Categorization)│                  │
│  │  5. Build + Deploy│       └──────────────────┘                  │
│  └───────────────────┘              │                               │
│         │                            │                               │
│         ▼                            ▼                               │
│  public/data/videos.json  (AI-enriched metadata)                    │
│  • ytId, title, thumbnail                                            │
│  • category (Film, Music, Tutorial, etc.)                           │
│  • tags (AI-generated)                                               │
│  • enhanced description                                              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Video Discovery (Automated)
```
YouTube Channel
    ↓ (YouTube Data API)
GitHub Actions Workflow
    ↓ (OpenAI GPT-4)
videos.json (AI-categorized)
    ↓ (FTP Deploy)
Checkdomain Hosting
    ↓ (api.php)
React SPA
    ↓
User Browser
```

### 2. Video Playback
```
User clicks Play
    ↓
React Router → /video/:ytId
    ↓
VideoPlayerPage loads
    ↓
YouTube IFrame API embeds player
    ↓
Double-tap gestures handle seek
    ↓
Analytics event logged
```

### 3. Analytics Pipeline
```
User interaction (play, pause, seek)
    ↓
POST /api.php?path=analytics/event
    ↓
Append to data/analytics_events.ndjson
    ↓
GET /api.php?path=analytics/summary
    ↓
Aggregate events (last N days)
    ↓
Return JSON summary
```

---

## Technology Stack

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.4.21
- **Router**: React Router 6.20.0
- **Styling**: Tailwind CSS + Custom Design Tokens
- **Icons**: Lucide React
- **i18n**: i18next
- **State**: Context API (AppContext)

### Backend (API)
- **Language**: PHP 8.x
- **Endpoints**: `api.php` (routing + JSON responses)
- **Data Storage**: 
  - Videos: `data/videos.json` (static)
  - Analytics: `data/analytics_events.ndjson` (append-only log)

### Backend (Node - Optional, Not Deployed Yet)
- **Runtime**: Node.js 20.x
- **Framework**: Express 4.18.2
- **ORM**: Prisma 7.1.0
- **Database**: MySQL 8.0 (db-host254.checkdomain.de)
- **Status**: ⚠️ Not currently deployed; PHP api.php sufficient for MVP

### AI/Automation
- **YouTube API**: googleapis package (YouTube Data API v3)
- **AI**: OpenAI GPT-4 (categorization, tagging, descriptions)
- **Orchestration**: GitHub Actions (daily cron + manual triggers)

### Testing
- **Unit**: Vitest
- **E2E**: Playwright + @axe-core (accessibility)
- **Visual**: Playwright snapshots
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)

### Deployment
- **Method**: FTP (WinSCP via PowerShell + GitHub Actions)
- **Target**: Checkdomain shared hosting
- **Domain**: https://frai.tv
- **Automation**: `.github/workflows/deploy-release.yml` (on Git tag)

---

## Key Architectural Decisions

### 1. Why PHP `api.php` instead of Node backend?
**Problem**: Checkdomain SPA rewrite swallows `/api/*` URLs → returns `index.html` instead of JSON.

**Solution**: PHP entrypoint (`api.php`) bypasses rewrite rules.
- ✅ Works with Checkdomain shared hosting (no custom nginx config needed)
- ✅ No reverse proxy required
- ✅ Fast deployment (just FTP upload)
- ⚠️ Limited scalability compared to Node + DB

**Future**: Migrate to Node + Prisma when traffic scales (requires Plesk/Node.js hosting).

### 2. Why static `videos.json` instead of DB queries?
**Problem**: Real-time YouTube API calls are slow and rate-limited.

**Solution**: Pre-fetch videos via GitHub Actions, store as static JSON.
- ✅ Fast page loads (no external API calls)
- ✅ AI-enriched metadata (categories, tags)
- ✅ Cacheable by CDN
- ⚠️ Requires daily sync to stay updated

**Future**: Store videos in MySQL (Prisma) when backend is deployed.

### 3. Why AI categorization instead of manual?
**Problem**: User complained "new videos aren't recognized and kategorized" → manual curation is slow.

**Solution**: OpenAI GPT-4 analyzes video titles/descriptions → auto-generates categories/tags.
- ✅ Automatic video discovery
- ✅ High-quality categorization
- ✅ Scales with channel growth
- ⚠️ Requires API keys (costs money)

**Future**: Train custom ML model for categorization (reduce costs).

### 4. Why NDJSON for analytics instead of DB?
**Problem**: No Node backend deployed yet; need analytics NOW.

**Solution**: Append-only NDJSON log with PHP.
- ✅ Simple to implement
- ✅ No DB setup required
- ✅ Backup rotation prevents bloat
- ⚠️ Limited querying capabilities

**Future**: Import NDJSON into Prisma (MySQL) when backend is deployed.

---

## Security Considerations

### Current Protections
- ✅ HTTPS enforced (Checkdomain SSL)
- ✅ Analytics backup endpoint requires admin key
- ✅ CSP headers (example config provided)
- ✅ No sensitive data in client-side code
- ✅ API keys stored in GitHub Secrets

### Pending Improvements
- [ ] Rate limiting on API endpoints
- [ ] CORS headers on api.php
- [ ] Input validation on analytics events
- [ ] Honeypot/CAPTCHA for abuse prevention

---

## Performance Targets

### Lighthouse Scores (Target)
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90

### Core Web Vitals (Target)
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Load Times (Target)
- **Time to First Byte**: < 600ms
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s

---

## Scalability Plan

### Current Capacity
- **Videos**: 92 (static JSON)
- **Concurrent Users**: ~100 (Checkdomain shared hosting)
- **Analytics**: Append-only NDJSON (rotated daily)

### Scale Triggers
- **>500 videos**: Migrate to DB (Prisma + MySQL)
- **>1000 concurrent users**: Upgrade to VPS/dedicated server
- **>10GB analytics**: Import to DB, add aggregation

### Migration Path
```
Phase 1: PHP API + Static JSON (CURRENT)
    ↓
Phase 2: Node + Prisma + MySQL (videos + analytics)
    ↓
Phase 3: Redis cache + CDN (static assets)
    ↓
Phase 4: Microservices (separate video/analytics/auth services)
```

---

## Monitoring & Observability

### Current
- ✅ Deployment verification script (`verify-deployment.mjs`)
- ✅ Analytics summary endpoint
- ⚠️ Manual log inspection (Checkdomain/Plesk)

### Future
- [ ] Matomo analytics integration
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Performance monitoring (SpeedCurve)

---

**Last Updated**: 2024-01-XX  
**Version**: 1.0.0
