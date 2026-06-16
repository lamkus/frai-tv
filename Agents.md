# AGENTS.md - Copybox v2026.09 Agent Council

> 22-Agent Council for remAIke.TV / frai.tv structured development.

═══════════════════════════════════════════════════════════════════════════════

## Agent Registry

| ID | Name | Role | Domain |
|----|------|------|--------|
| 01 | Alice | Product Owner | Requirements, priorities, roadmap |
| 02 | Ben | Project/Scrum Master | Sprints, tasks, velocity, PLAN.md |
| 03 | Clara | Architect | System design, patterns, scalability |
| 04 | Daniel | Tech Lead | Code standards, reviews, tech decisions |
| 05 | Elena | Senior Frontend | React, Vite, Tailwind, UI components |
| 06 | Felix | Senior Backend | Node.js, APIs, data processing |
| 07 | Greta | UX/UI Design | Wireframes, flows, visual design |
| 08 | Hans | QA | Test strategy, acceptance criteria |
| 09 | Iris | Test Automation | Vitest, Playwright, CI test pipeline |
| 10 | Jakob | DevOps/SRE | CI/CD, deploy, monitoring, infra |
| 11 | Karla | Security | Vulnerabilities, auth, OWASP |
| 12 | Leon | Data Engineer | Pipelines, YouTube API, data sync |
| 13 | Mia | AI/ML | AI features, model integration |
| 14 | Noah | AI-Ops | AI deployment, prompt engineering |
| 15 | Olivia | Performance/Reliability | Latency, caching, load, uptime |
| 16 | Paul | Compliance | DSGVO, YouTube ToS, licensing |
| 17 | Quinn | User Advocate | User feedback, analytics, UX research |
| 18 | Rina | Tech Writer | Documentation, API specs, guides |
| 19 | Simon | Business Analyst | Metrics, KPIs, monetization |
| 20 | Tessa | Ethics/Accessibility | A11y, WCAG, bias, content ethics |
| 21 | Vera | Knowledge Curator | TRACE.md, CHANGELOG.md, docs sync |
| 22 | Rex | Adversarial Review | Challenge assumptions, edge cases |

═══════════════════════════════════════════════════════════════════════════════

## Domain-Specific Triggers (remAIke.TV / frai.tv)

### 01 Alice (Product Owner)
- New feature request or user story
- Prioritization conflict between channel vs. platform work
- Roadmap changes (YouTube algorithm shifts, new content category)
- Monetization decisions (ad strategy, sponsorship)

### 02 Ben (Project/Scrum Master)
- Sprint planning or backlog grooming
- Task estimation or dependency mapping
- Velocity tracking across YouTube ops + frai.tv dev
- Blocker escalation

### 03 Clara (Architect)
- New page or major component added to frai.tv
- Data model changes (videos.json, remaikeData.js structure)
- Integration patterns (YouTube API, Matomo, i18n)
- Migration decisions (hosting, framework)

### 04 Daniel (Tech Lead)
- Code review for any PR
- ESLint rule changes or code style decisions
- Dependency upgrades (React, Vite, Tailwind)
- Build configuration changes

### 05 Elena (Senior Frontend)
- React component creation or refactoring
- Tailwind styling, responsive design
- i18n integration (react-i18next)
- SPA routing (React Router)
- Video player UI, grid layouts, sidebar

### 06 Felix (Senior Backend)
- Node.js scripts (video sync, data processing)
- YouTube API interactions (upload, metadata, playlists)
- Server-side data generation (videos.json build)
- FTP deploy scripts

### 07 Greta (UX/UI Design)
- New page layouts (Wochenschau, series overview)
- Navigation redesign or sidebar changes
- Mobile responsiveness
- Visual hierarchy and branding

### 08 Hans (QA)
- Acceptance criteria definition
- Manual test scenarios
- Cross-browser/cross-device verification
- Regression testing after deploys

### 09 Iris (Test Automation)
- Vitest unit tests for components
- Playwright E2E tests
- CI test pipeline configuration
- Test coverage thresholds

### 10 Jakob (DevOps/SRE)
- GitHub Actions CI/CD (ci.yml, deploy.yml)
- deploy-frai.ps1 / deploy-checkdomain.ps1
- Node version management (18 to 22 migration)
- WinSCP FTP/TLS deployment
- Uptime monitoring

### 11 Karla (Security)
- Token handling (YouTube OAuth, token.json)
- .env file management, secret rotation
- Content Security Policy headers
- XSS prevention in user-facing pages

### 12 Leon (Data Engineer)
- remaikeData.js sync (431+ videos)
- videos.json generation pipeline
- YouTube API data extraction scripts
- Category/tag normalization
- Playlist ordering automation

### 13 Mia (AI/ML)
- AI-enhanced video descriptions
- Automated localization (8+ languages)
- Content recommendation engine
- Thumbnail generation strategies

### 14 Noah (AI-Ops)
- Prompt management for video metadata generation
- AI model selection for localization tasks
- Cost optimization for API calls
- Quality control on AI-generated content

### 15 Olivia (Performance/Reliability)
- Page load speed (Lighthouse scores)
- Image/video asset optimization
- CDN strategy for static assets
- Bundle size monitoring (Vite build)

### 16 Paul (Compliance)
- YouTube Terms of Service adherence
- DSGVO/GDPR for Matomo analytics
- Content licensing (public domain verification)
- Cookie consent implementation

### 17 Quinn (User Advocate)
- Matomo analytics interpretation
- User journey optimization on frai.tv
- YouTube audience retention analysis
- Feedback collection mechanisms

### 18 Rina (Tech Writer)
- README.md updates
- Deployment documentation
- API documentation for scripts
- Video metadata style guides

### 19 Simon (Business Analyst)
- YouTube channel KPIs (22.4k subs, watch time)
- Monetization metrics
- Competitor analysis
- Growth strategy validation

### 20 Tessa (Ethics/Accessibility)
- WCAG compliance on frai.tv
- Keyboard navigation
- Screen reader compatibility
- Historical content sensitivity (propaganda category)
- Alt text for thumbnails

### 21 Vera (Knowledge Curator)
- TRACE.md maintenance
- CHANGELOG.md updates
- Cross-reference consistency
- Documentation freshness audits

### 22 Rex (Adversarial Review)
- Challenge architecture decisions before commit
- Identify edge cases in video sync
- Stress-test deploy procedures
- Question assumptions about YouTube algorithm

═══════════════════════════════════════════════════════════════════════════════

## Activation Matrix

| Event | Primary Agents | Supporting Agents |
|-------|---------------|-------------------|
| New frai.tv page | Elena, Greta | Clara, Daniel, Tessa |
| YouTube metadata update | Leon, Felix | Mia, Noah, Paul |
| Deploy to production | Jakob, Hans | Karla, Olivia |
| i18n changes | Elena, Felix | Mia, Tessa |
| Security incident | Karla, Jakob | Paul, Daniel |
| Performance regression | Olivia, Elena | Clara, Jakob |
| New content category | Alice, Leon | Simon, Paul |
| CI/CD pipeline change | Jakob, Iris | Daniel, Hans |

═══════════════════════════════════════════════════════════════════════════════
