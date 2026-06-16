# Copilot Instructions - remAIke.TV / frai.tv

> Read **MASTER_PROMPT.md** for the full Copybox v2026.09 process framework.

═════════��═══════════════════════���═════════════════════════════════════════════

## Domain Context

- **YouTube Channel**: @remAIke_IT
  - 8K AI-restored classic films, newsreels, documentaries, cartoons
  - 440+ videos, 22.4k subscribers
  - Categories: cartoons, documentaries, classic-films, newsreels, christmas, comedy, commercials, propaganda

- **Platform**: frai.tv
  - React 18 + Vite 5 + Tailwind CSS single-page application
  - Hosted on Checkdomain shared hosting (static SPA, no SSR)
  - No backend database - all data in static JS/JSON files

## Languages

- Primary: DE (German)
- Supported: EN, FR, JA, KO, PT-BR, HI, ES
- i18n: react-i18next with HTTP backend

## Tech Stack

- Frontend: React 18, Vite 5, Tailwind CSS 3, React Router v6
- Scripts: Python 3.11+, Node.js 22
- Testing: Vitest (unit), Playwright (E2E)
- Linting: ESLint (zero warnings policy)
- CI/CD: GitHub Actions (ci.yml, deploy.yml)
- Deploy: WinSCP FTP/TLS via deploy-checkdomain.ps1 or deploy-frai.ps1

## Key Rules

- No secrets in code, use .env files
- All user-facing strings via i18n (never hardcode text)
- Functional React components with hooks only
- ESLint must pass with zero warnings
- Conventional commits: feat:, fix:, docs:, chore:
- Squash merge to master branch

## Video Categories

cartoons, documentaries, classic-films, newsreels, christmas, comedy, commercials, propaganda

═════════���═══════════════════════���═════════════════════════════════════════════

## STOP-GATES

| ID | Trigger | Aktion |
|----|---------|--------|
| SG-1 | Destructive commands (rm, del, DROP, API delete) | HALT + User fragen |
| SG-2 | Extension install outside approved list | HALT + User fragen |
| SG-3 | Secrets/Tokens/PII | NEVER log or output |
| SG-4 | Public API breaks | HALT + User fragen |
| SG-5 | Cost-relevant cloud ops | HALT + User fragen |
| SG-6 | YouTube API quota-critical | Public API first, track quota |
| SG-7 | Video PUBLISH | NEVER auto-publish, user does it manually |

══════════════════════════════���════════════════════════════════════════════════

## YouTube API Rules

- READ operations: ALWAYS use Public API with API Key ($env:YOUTUBE_API_KEY)
- WRITE operations: OAuth token only
- DELETE operations: MANUAL in YouTube Studio only (never via API)
- Quota reset: 08:00 UTC daily
- On quota error: STOP immediately

### Quota Costs
| Method | Units | Type |
|--------|-------|------|
| videos.list | 1 | READ |
| channels.list | 1 | READ |
| playlists.list | 1 | READ |
| playlistItems.list | 1 | READ |
| search.list | 100 | READ |
| playlistItems.insert | 50 | WRITE |
| videos.update | 50 | WRITE |

═════════════════════════════════════��═════════════════════════════════════════

## Video SEO Rules

### Title (max 70 chars)
- Primary keyword at START
- Year: (1933) or date: (10.07.1940)
- Quality suffix: **8K HQ (4K UHD)** - mandatory, both keywords
- NO @remAIke_IT in title
- For Alfred: both "Kwak" AND "Quack" spellings

### Description
- First 2 lines visible in search - use HIGH-VALUE KEYWORDS (not title repeat)
- Chapters: 0:00 Intro format
- Mandatory links: www.remaike.IT + YouTube channel link
- Subscribe CTA block
- Max 5 hashtags

### Tags
- Max 15 tags (YouTube: "MINIMAL role")
- Focus: series name, year, "8K", "public domain"

═════���══════════════════════════��══════════════════════════════════════════════

## Wochenschau Compliance

- Category: Education (27) for Wochenschau content
- MANDATORY: Visual disclaimer IN VIDEO (intro screen + watermark)
- YouTube/Gemini scans pixels for context
- Without in-video disclaimer: NO UPLOAD (strike risk)
- Individual location from config/wochenschau_complete_locations.json

═══════════════════════════════════════════════════════════════════════════════

## Important Paths

```
MASTER_PROMPT.md                    # Copybox v2026.09 framework
AGENTS.md                           # 22-agent council
PLAN.md                             # Active sprint
TRACE.md                            # Requirements trace (R-IDs)
CONVENTIONS.md                      # Coding standards
CHANGELOG.md                        # Change history
config/youtube_oauth.json           # OAuth (NEVER commit)
config/wochenschau_complete_locations.json  # 252 episodes with locations
scripts/youtube/                    # YouTube automation scripts
code/frontend/                      # frai.tv React SPA
.github/workflows/                  # CI/CD pipelines
```

════���════════════════════════════════════════════════════���═════════════════════

## Channel Info

```
Channel ID:      UCVFv6Egpl0LDvigpFbQXNeQ
Handle:          @remAIke_IT
Upload-Playlist: UUVFv6Egpl0LDvigpFbQXNeQ
Subscribers:     22,400+
Videos:          440+
Country:         DE
```

════════════��═══════════════════════���══════════════════════════════════════════
