# AI Automation - remAIke.TV

> High-End AI-powered Video Management & Internationalisierung

## 🚀 Features Overview

| Feature | Status | Cost | Automation |
|---------|--------|------|------------|
| AI Video Sync | ✅ Active | GPT-4o | GitHub Actions (3 AM UTC) |
| Translation | ✅ Active | GPT-4o-mini | Batch API (-50%) |
| Auto-Kategorisierung | ✅ Active | - | Per Video |
| Tag-Generation | ✅ Active | - | Per Video |

## 🤖 Scripts

### 1. AI Video Sync (YouTube → AI Categorization)

```bash
# Set API keys
$env:YOUTUBE_API_KEY = "AIzaSy..."
$env:OPENAI_API_KEY = "sk-..."

# Run sync (all videos with pagination)
cd code/frontend
node scripts/sync-youtube-ai.mjs
```

**Features:**
- ✅ Holt ALLE Videos vom Channel (Pagination)
- ✅ AI-Kategorisierung (classic-films, cartoons, christmas, etc.)
- ✅ Automatische Tags
- ✅ Dekaden-Erkennung (1920s, 1930s, etc.)
- ✅ Fallback: Claude → OpenAI → Heuristik

### 2. Video Translation (Multi-Language)

```bash
# Realtime (sofort, voller Preis)
node scripts/translate-videos.mjs --lang=en,es,fr

# Batch API (50% günstiger, max 24h)
node scripts/translate-videos.mjs --lang=en,es,fr --batch
```

**Unterstützte Sprachen:**
- 🇩🇪 Deutsch (de) - Basis
- 🇬🇧 English (en)
- 🇪🇸 Español (es)
- 🇫🇷 Français (fr)
- 🇮🇹 Italiano (it)
- 🇵🇹 Português (pt)
- 🇳🇱 Nederlands (nl)
- 🇵🇱 Polski (pl)
- 🇯🇵 日本語 (ja)
- 🇨🇳 中文 (zh)

### 3. Check Batch Status

```bash
# Check batch progress
node scripts/check-batch.mjs batch_abc123

# Output: Status, Progress %, Results download
```

## 📊 Cost Optimization

### OpenAI Batch API
- **50% Rabatt** auf alle Batch-Requests
- Completion innerhalb 24h (meist schneller)
- Ideal für Übersetzungen, Bulk-Categorization

```
Normal API:  ~$0.002 pro Video-Übersetzung
Batch API:   ~$0.001 pro Video-Übersetzung
              ↓
Ersparnis:   50% bei 100+ Videos = $0.10+ gespart
```

### Modell-Auswahl
| Task | Modell | Kosten |
|------|--------|--------|
| Kategorisierung | gpt-4o | Höchste Qualität |
| Übersetzung | gpt-4o-mini | Kosteneffizient |
| Fallback | Claude 3.5 | Alternative |

## 🔄 GitHub Actions Automation

### Daily Sync (3 AM UTC)

`.github/workflows/sync-youtube.yml`:
```yaml
name: Daily YouTube Sync
on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM UTC = 4 AM Berlin
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
        working-directory: code/frontend
      - run: node scripts/sync-youtube-ai.mjs
        working-directory: code/frontend
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add code/frontend/public/data/videos.json
          git diff --staged --quiet || git commit -m "🤖 Auto-sync YouTube videos"
          git push
```

### Required Secrets
1. `YOUTUBE_API_KEY` - YouTube Data API v3
2. `OPENAI_API_KEY` - OpenAI API Key
3. `ANTHROPIC_API_KEY` (optional) - Claude Fallback

## 🎛️ Admin Panel

URL: `https://frai.tv/admin`
Password: `remaike2024`

### AI Tab Features
1. **AI Sync** - Manueller Sync trigger
2. **Translate** - Multi-Language Übersetzung
3. **History** - Alle AI-Operationen
4. **Settings** - Automation-Kontrolle

## 📁 Output Files

```
public/data/
├── videos.json          # Haupt-Videodaten (AI-enriched)
└── i18n/
    ├── videos_en.json   # English translations
    ├── videos_es.json   # Spanish translations
    ├── videos_fr.json   # French translations
    └── ...
```

## 🔒 API Keys

### YouTube Data API v3
- Console: https://console.cloud.google.com
- Quota: 10,000 units/day
- Stored in: `RUNBOOK.md` (local), GitHub Secrets (CI)

### OpenAI API
- Console: https://platform.openai.com
- Models: gpt-4o, gpt-4o-mini
- Batch API für 50% Rabatt

## 📈 Monitoring

### Sync History (localStorage)
```javascript
// Browser Console
JSON.parse(localStorage.getItem('ai_sync_history'))
```

### Log Files
```
.tempilot/log.json  # Session logs
data/batches/       # Batch JSONL files
```

## 🚨 Troubleshooting

### "YOUTUBE_API_KEY not set"
```bash
$env:YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

### "Rate limit exceeded"
- Wait 1 minute, retry
- Use Batch API for bulk operations
- Check quota: https://console.cloud.google.com/apis/dashboard

### "Batch failed"
```bash
# Check batch errors
node scripts/check-batch.mjs batch_xxx
```

## 📋 Checklist für neue Sprache

1. [ ] Sprache zu `availableLanguages` in `AIManagementTab.jsx` hinzufügen
2. [ ] Translation-Script testen: `node translate-videos.mjs --lang=xx`
3. [ ] Frontend i18n-Support prüfen
4. [ ] Deploy und verifizieren

---

**Automatisiert. Skalierbar. High-End.** 🎬
