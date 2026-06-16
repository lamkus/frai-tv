# CLAUDE.md - remAIke.TV / frai.tv

Read **MASTER_PROMPT.md** for the full Copybox v2026.11 process framework (Sauerland.AI Cognitive Layer, DAP-Protokoll, Popper-Falsifikation).

═══════════════════════════════════════════════════════════════════════════════

## Project Facts

- **Channel**: @remAIke_IT (YouTube, 440 videos, 22.4k subscribers)
- **Content**: 8K restored classic films, newsreels, documentaries, cartoons
- **Platform**: frai.tv - React 18 + Vite 5 + Tailwind CSS SPA
- **Hosting**: Checkdomain shared hosting (host254.checkdomain.de)
- **Deploy**: WinSCP FTP/TLS via deploy-frai.ps1, CI/CD via GitHub Actions
- **Languages**: DE (primary), EN, FR, JA, KO, PT-BR, HI, ES
- **Data**: Static (remaikeData.js, videos.json) - no backend database
- **Git**: master branch, squash merges, conventional commits

## Key Files

- `AGENTS.md` - 22-agent council with domain triggers
- `PLAN.md` - Active sprint and backlog
- `TRACE.md` - Requirements trace matrix (R-IDs)
- `CONVENTIONS.md` - Coding standards
- `CHANGELOG.md` - Change history

## Session Protocol

1. Read PLAN.md to identify current work
2. Reference R-IDs from TRACE.md for all changes
3. Follow CONVENTIONS.md for code style
4. Update TRACE.md and CHANGELOG.md on completion
5. Append session summary to CLOSING.log

═══════════════════════════════════════════════════════════════════════════════
