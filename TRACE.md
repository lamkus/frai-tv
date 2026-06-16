# TRACE.md - Requirements Trace Matrix

> Copybox v2026.09 - All requirements tracked with R-IDs.

═══════════════════════════════════════════════════════════════════════════════

## R-001: YouTube title revert ([8K] to 8K HQ (4K UHD))
Status: DONE
Sprint: completed
Agents: Leon, Felix
Linked: R-004
Notes: Removed bracket format, standardized to "8K HQ (4K UHD)" suffix.

## R-002: Wochenschau category fix (27 to 1)
Status: DONE
Sprint: completed
Agents: Leon, Felix
Linked: R-009
Notes: Corrected category ID from 27 (Education) to 1 (Film & Animation).

## R-003: Full Movie tag for feature-length videos
Status: DONE
Sprint: completed
Agents: Leon, Felix
Linked: R-001
Notes: Added "Full Movie" tag to all videos over 40 minutes runtime.

## R-004: 8+ localizations for all videos
Status: DONE
Sprint: completed
Agents: Mia, Noah, Leon
Linked: R-001
Notes: DE, EN, FR, JA, KO, PT-BR, HI, ES titles and descriptions for 440 videos.

## R-005: frai.tv SEO (robots.txt, OG tags, Schema.org)
Status: DONE
Sprint: completed
Agents: Elena, Felix, Daniel
Linked: R-016
Notes: robots.txt, Open Graph meta tags, basic Schema.org markup deployed.

## R-006: i18n initialization fix
Status: DONE
Sprint: completed
Agents: Elena, Felix
Linked: R-011
Notes: Fixed react-i18next HTTP backend initialization order issue.

## R-007: remaikeData.js sync (91 to 431 videos)
Status: DONE
Sprint: completed
Agents: Leon, Felix
Linked: R-009
Notes: Full video catalog synced from YouTube API into static data file.

## R-008: CI/CD Node 18 to 22 + deploy trigger
Status: DONE
Sprint: completed
Agents: Jakob, Daniel
Linked: R-021
Notes: Updated GitHub Actions to Node 22, deploy triggers on master push.

## R-009: Wochenschau page with 94 episodes
Status: DONE
Sprint: completed
Agents: Elena, Greta, Leon
Linked: R-002, R-007
Notes: Dedicated archive page for Deutsche Wochenschau series (94 episodes).

## R-010: ESLint errors resolved for CI deploy
Status: DONE
Sprint: completed
Agents: Daniel, Elena
Linked: R-008
Notes: Fixed all ESLint errors and warnings blocking CI pipeline.

═══════════════════════════════════════════════════════════════════════════════

## R-011: Sidebar i18n completion (all languages)
Status: IN_PROGRESS
Sprint: current
Agents: Elena, Felix
Linked: R-006
Notes: Some sidebar navigation items still showing untranslated keys.

## R-012: Matomo analytics integration
Status: BACKLOG
Sprint: current
Agents: Jakob, Quinn
Linked: R-019
Notes: Matomo instance available, needs tracking code integration on frai.tv.

## R-013: Series overview page (all 8 categories)
Status: BACKLOG
Sprint: current
Agents: Elena, Greta, Leon
Linked: R-009
Notes: Landing page showing all content categories with filterable grid.

## R-014: Video detail page with metadata display
Status: BACKLOG
Sprint: current
Agents: Elena, Greta
Linked: R-013
Notes: Individual video pages with embedded player, description, related videos.

## R-015: YouTube thumbnail A/B testing framework
Status: BACKLOG
Sprint: current
Agents: Simon, Mia
Linked: R-019
Notes: Framework to test thumbnail variants and measure CTR impact.

## R-016: SEO Schema.org VideoObject for all pages
Status: BACKLOG
Sprint: backlog
Agents: Elena, Felix
Linked: R-005
Notes: Structured data for each video to improve search appearance.

## R-017: Performance lazy-load images + video grid
Status: BACKLOG
Sprint: backlog
Agents: Elena, Olivia
Linked: R-015
Notes: Intersection Observer for thumbnails, virtual scrolling for large grids.

## R-018: YouTube shorts strategy (vertical clips)
Status: BACKLOG
Sprint: backlog
Agents: Mia, Simon, Leon
Linked: R-015
Notes: Extract vertical highlight clips from existing content for Shorts.

## R-019: Cookie consent banner (DSGVO)
Status: BACKLOG
Sprint: backlog
Agents: Paul, Elena
Linked: R-012
Notes: Required before Matomo tracking goes live with PII collection.

## R-020: frai.tv search functionality
Status: BACKLOG
Sprint: backlog
Agents: Elena, Felix
Linked: R-013
Notes: Client-side full-text search across video titles and descriptions.

## R-021: Playwright E2E tests in CI pipeline
Status: BACKLOG
Sprint: backlog
Agents: Iris, Jakob
Linked: R-008
Notes: Automated E2E test suite running on each PR.

## R-022: Christmas category page refresh
Status: BACKLOG
Sprint: backlog
Agents: Leon, Greta
Linked: R-013
Notes: Seasonal page update for Christmas content collection.

## R-023: YouTube community posts automation
Status: BACKLOG
Sprint: backlog
Agents: Felix, Simon
Linked: R-018
Notes: Automated community tab posts for new uploads and milestones.

═══════════════════════════════════════════════════════════════════════════════
