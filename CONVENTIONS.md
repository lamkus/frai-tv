# CONVENTIONS.md - Coding Guidelines

> Copybox v2026.09 - Read-only reference for all agents.

═══════════════════════════════════════════════════════════════════════════════

## Languages

| Context | Language | Version |
|---------|----------|---------|
| Frontend | JavaScript/JSX | ES2022+ |
| Backend/Scripts | Node.js | v22 LTS |
| Automation | Python | 3.11+ |
| Styling | Tailwind CSS | v3 |
| Markup | HTML5 | - |

═══════════════════════════════════════════════════════════════════════════════

## Framework & Libraries

- **UI Framework**: React 18
- **Build Tool**: Vite 5
- **CSS**: Tailwind CSS 3 (utility-first, no custom CSS unless necessary)
- **Routing**: React Router v6
- **i18n**: react-i18next with HTTP backend (JSON translation files)
- **Testing**: Vitest (unit), Playwright (E2E)
- **Linting**: ESLint with recommended rules

═══════════════════════════════════════════════════════════════════════════════

## Project Structure

```
code/frontend/          Frontend SPA (React/Vite)
  src/
    components/         React components
    pages/              Page-level components
    locales/            Translation JSON files (de, en, fr, ja, ko, pt, hi, es)
    data/               Static data (remaikeData.js, videos.json)
    assets/             Images, icons
  public/               Static assets served as-is
  vite.config.js        Vite configuration
  tailwind.config.js    Tailwind configuration

scripts/                Python/Node automation scripts
data/                   Raw data files, exports
.github/workflows/      CI/CD pipeline definitions
```

═══════════════════════════════════════════════════════════════════════════════

## Data Layer

- **Primary data**: `remaikeData.js` - static export of all video metadata (431+ entries)
- **Secondary data**: `videos.json` - generated from YouTube API
- **No database**: All data is static, generated offline
- **Sync process**: Python scripts pull from YouTube API, transform, write to static files

═══════════════════════════════════════════════════════════════════════════════

## Deployment

| Target | Method | Host |
|--------|--------|------|
| frai.tv | WinSCP FTP/TLS | host254.checkdomain.de |
| CI Build | GitHub Actions | GitHub-hosted runners |
| Deploy trigger | Push to master | Automatic via deploy.yml |

**Deploy scripts**:
- `deploy-frai.ps1` - PowerShell deploy via WinSCP
- `deploy-checkdomain.ps1` - Alternative deploy script

**Important**: Shared hosting - no server-side rendering, static SPA only.

═══════════════════════════════════════════════════════════════════════════════

## Git Workflow

- **Branch**: `master` (production)
- **Merge strategy**: Squash merges for feature branches
- **Commit style**: Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **PR required**: Yes, for all changes to master
- **CI checks**: ESLint + build must pass before merge

═══════════════════════════════════════════════════════════════════════════════

## Code Style

### JavaScript/JSX
- ESLint enforced, zero warnings policy
- No unused imports or variables
- Functional components with hooks (no class components)
- Named exports preferred over default exports
- Destructure props at function signature level

### CSS/Tailwind
- Utility classes in JSX, no separate CSS files
- Responsive: mobile-first (`sm:`, `md:`, `lg:` breakpoints)
- Dark mode: not currently implemented

### Python
- PEP 8 compliance
- Type hints for function signatures
- Docstrings for public functions

═══════════════════════════════════════════════════════════════════════════════

## i18n Rules

- All user-facing strings must use `t('key')` from react-i18next
- Translation files: `src/locales/{lang}/translation.json`
- Supported languages: DE (primary), EN, FR, JA, KO, PT-BR, HI, ES
- Fallback language: DE
- Never hardcode text in components

═══════════════════════════════════════════════════════════════════════════════

## Security

- No secrets in source code (use `.env` files, never committed)
- `token.json` in `.gitignore`
- YouTube OAuth tokens stored locally only
- No user authentication on frai.tv (public read-only site)
- CSP headers configured at hosting level

═══════════════════════════════════════════════════════════════════════════════

## Testing

- **Unit tests**: Vitest for utility functions and component logic
- **E2E tests**: Playwright for critical user flows
- **Coverage target**: 60% for new code
- **CI requirement**: All tests pass before deploy

═══════════════════════════════════════════════════════════════════════════════

## Performance Targets

- Lighthouse Performance: >80
- First Contentful Paint: <2s
- Bundle size: <500KB gzipped
- Images: WebP format, lazy-loaded

═══════════════════════════════════════════════════════════════════════════════
