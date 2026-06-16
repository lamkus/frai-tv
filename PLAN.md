# PLAN.md - Active Roadmap

> Copybox v2026.09 - remAIke.TV / frai.tv Sprint Plan

═══════════════════════════════════════════════════════════════════════════════

## Current Sprint

| # | Item | Status | Agents | R-ID |
|---|------|--------|--------|------|
| 1 | Sidebar i18n completion (all languages) | ► in_progress | Elena, Felix | R-011 |
| 2 | Matomo analytics integration on frai.tv | ░ planned | Jakob, Quinn | R-012 |
| 3 | Series overview page (all 8 categories) | ░ planned | Elena, Greta, Leon | R-013 |
| 4 | Video detail page with metadata display | ░ planned | Elena, Greta | R-014 |
| 5 | YouTube thumbnail A/B testing framework | ░ planned | Simon, Mia | R-015 |

═══════════════════════════════════════════════════════════════════════════════

## Backlog (Prioritized)

| # | Item | Priority | Agents | R-ID |
|---|------|----------|--------|------|
| 6 | SEO: Schema.org VideoObject for all pages | high | Elena, Felix | R-016 |
| 7 | Performance: lazy-load images + video grid | high | Elena, Olivia | R-017 |
| 8 | YouTube: shorts strategy (vertical clips) | medium | Mia, Simon, Leon | R-018 |
| 9 | frai.tv: cookie consent banner (DSGVO) | medium | Paul, Elena | R-019 |
| 10 | frai.tv: search functionality | medium | Elena, Felix | R-020 |
| 11 | CI/CD: Playwright E2E tests in pipeline | medium | Iris, Jakob | R-021 |
| 12 | Content: Christmas category page refresh | low | Leon, Greta | R-022 |
| 13 | YouTube: community posts automation | low | Felix, Simon | R-023 |

═══════════════════════════════════════════════════════════════════════════════

## Recently Completed

| Item | Completed | R-ID |
|------|-----------|------|
| YouTube title revert ([8K] to 8K HQ) | 2026-04-15 | R-001 |
| Wochenschau category fix (27 to 1) | 2026-04-15 | R-002 |
| Full Movie tag for feature-length | 2026-04-15 | R-003 |
| 8+ localizations for all videos | 2026-04-15 | R-004 |
| frai.tv SEO (robots.txt, OG, Schema) | 2026-04-14 | R-005 |
| i18n initialization fix | 2026-04-16 | R-006 |
| remaikeData.js sync (91 to 431 videos) | 2026-04-16 | R-007 |
| CI/CD Node 18 to 22 + deploy trigger | 2026-04-16 | R-008 |
| Wochenschau page with 94 episodes | 2026-05-16 | R-009 |
| ESLint errors resolved for CI deploy | 2026-05-16 | R-010 |

═══════════════════════════════════════════════════════════════════════════════

## Notes

- YouTube channel: 440 videos, 22.4k subscribers
- frai.tv: React/Vite SPA deployed to Checkdomain shared hosting
- Languages supported: DE, EN, FR, JA, KO, PT-BR, HI, ES
- Deploy via: deploy-frai.ps1 (WinSCP FTP/TLS)
- CI/CD: GitHub Actions on master branch push

═══════════════════════════════════════════════════════════════════════════════
