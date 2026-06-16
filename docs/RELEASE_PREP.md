# 🚀 Release Preparation Guide

Complete pre-release checklist for production deployment of remaike.TV.

---

## 📋 Pre-Release Checklist

### 1. Code Quality

- [ ] All unit tests passing: `npm run test`
- [ ] E2E tests passing: `npm run test:e2e`
- [ ] Linting clean: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] No console errors/warnings in browser

### 2. Data Integrity

- [ ] Run AI video sync: `npm run yt:sync-ai`
- [ ] Verify `public/data/videos.json` contains latest videos
- [ ] Check for duplicate entries (dedupe should prevent this)
- [ ] Validate video schema (ytId, title, thumbnail, category)
- [ ] Verify thumbnail URLs are accessible

### 3. API Endpoints

- [ ] Health check responds: `/api.php?path=health`
- [ ] Videos endpoint returns data: `/api.php?path=videos`
- [ ] Analytics event logging works: POST `/api.php?path=analytics/event`
- [ ] Analytics summary works: `/api.php?path=analytics/summary&days=7`
- [ ] Analytics backup endpoint secured with key

### 4. Frontend Features

- [ ] Video playback works on desktop
- [ ] Video playback works on mobile
- [ ] Double-tap seek gestures functional
- [ ] Autoplay fallback ("Click to Play") works
- [ ] Category filtering works
- [ ] Search works (if implemented)
- [ ] Continue Watching updates correctly
- [ ] Navigation (TopNav) works
- [ ] Footer links are correct

### 5. UX/UI Polish

- [ ] Mobile responsive (test on 375px, 768px, 1920px)
- [ ] Loading skeletons appear correctly
- [ ] Hover effects smooth (VideoCard, buttons)
- [ ] Transitions/animations work
- [ ] No layout shift (CLS)
- [ ] Typography readable on all screen sizes
- [ ] Color contrast meets WCAG AA

### 6. Accessibility

- [ ] Axe audit passes: `npm run test:e2e -- accessibility.spec.js`
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] ARIA labels present on interactive elements
- [ ] Screen reader testing (NVDA/JAWS)

### 7. Performance

- [ ] Lighthouse score > 90 (Performance)
- [ ] First Contentful Paint < 1.5s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Cumulative Layout Shift < 0.1
- [ ] Time to Interactive < 3.5s
- [ ] Bundle size < 500KB (check dist/)

### 8. Security

- [ ] CSP headers configured (see `installation/csp_example.conf`)
- [ ] HTTPS enforced
- [ ] Analytics backup endpoint requires admin key
- [ ] No sensitive data in client-side code
- [ ] No exposed API keys in source code
- [ ] XSS protections in place

### 9. SEO

- [ ] `<title>` and `<meta description>` set
- [ ] Open Graph tags present
- [ ] Twitter Card tags present
- [ ] Canonical URLs set
- [ ] Sitemap generated (if applicable)
- [ ] robots.txt configured

### 10. Deployment

- [ ] `.env.production` configured correctly
- [ ] Build succeeds: `npm run build`
- [ ] Verify deployment: `npm run verify:prod`
- [ ] FTP credentials valid (GitHub Secrets)
- [ ] Backup current production before deploy
- [ ] Deploy to staging first (if available)
- [ ] Monitor for errors post-deployment

---

## 🔄 Release Workflow

### Step 1: Pre-Flight Checks

```bash
cd code/frontend

# 1. Pull latest
git pull origin main

# 2. Install dependencies
npm ci

# 3. Run tests
npm run test
npm run test:e2e

# 4. Lint
npm run lint

# 5. Build
npm run build

# 6. Verify build artifacts
ls -lh dist/
```

### Step 2: AI Video Sync

```bash
# Fetch latest videos with AI categorization
npm run yt:sync-ai

# Review changes
git diff public/data/videos.json

# Commit if new videos
git add public/data/videos.json
git commit -m "🤖 Update videos.json with AI sync"
git push
```

### Step 3: Create Release

```bash
# Tag release (semantic versioning)
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release"
git push origin v1.0.0
```

**GitHub Actions will automatically:**
1. Build frontend (`npm run build`)
2. Deploy to Checkdomain via FTP
3. Verify deployment health

### Step 4: Post-Deployment Verification

```bash
# Verify production endpoints
npm run verify:prod

# Expected output:
# ✓ index.html OK
# ✓ /api.php?path=health OK
# ✓ /api.php?path=videos OK
# ✓ 92 videos found
# ✓ ALL TESTS PASSED
```

### Step 5: Smoke Testing

**Desktop (Chrome DevTools):**
1. Open https://frai.tv
2. Check Console (no errors)
3. Play a video
4. Test seek (double-tap)
5. Check Continue Watching updates

**Mobile (Real Device):**
1. Open https://frai.tv on phone
2. Test video playback
3. Test double-tap gestures
4. Check responsive layout

### Step 6: Monitor

- **Analytics**: Check `/api.php?path=analytics/summary&days=1`
- **Logs**: Monitor Checkdomain/Plesk logs for errors
- **User Reports**: Watch for bug reports/issues

---

## 🐛 Rollback Procedure

If deployment fails:

### Quick Rollback (Manual)

```powershell
# Restore from backup
cd code/frontend
.\deploy-checkdomain.ps1 -RestoreBackup

# Or use WinSCP to restore from backup folder
```

### Git Rollback

```bash
# Revert to previous release
git revert HEAD
git push

# Force re-deploy
git tag -a v1.0.1 -m "Hotfix: Rollback broken release"
git push origin v1.0.1
```

---

## 📊 Success Metrics

### Launch Day (Day 0)
- [ ] Zero 5xx errors
- [ ] < 5% 4xx errors
- [ ] Page load < 3s (avg)
- [ ] Video play success rate > 95%

### Week 1
- [ ] Lighthouse scores maintained
- [ ] Analytics collecting data
- [ ] No critical bugs reported
- [ ] Continue Watching working for users

### Month 1
- [ ] AI video sync running daily
- [ ] New videos appearing automatically
- [ ] User engagement metrics positive
- [ ] Performance metrics stable

---

## 🛠️ Maintenance Tasks

### Daily
- [ ] AI video sync runs (automated via GitHub Actions)
- [ ] Monitor analytics for anomalies

### Weekly
- [ ] Review analytics backup size
- [ ] Check for new console errors
- [ ] Update dependencies: `npm outdated`

### Monthly
- [ ] Security audit: `npm audit`
- [ ] Lighthouse audit
- [ ] Accessibility audit
- [ ] Review and refine AI categorization

---

## 📞 Support Contacts

- **Code Issues**: GitHub Issues
- **Hosting (Checkdomain)**: support@checkdomain.de
- **Analytics**: Local NDJSON logs + Matomo (if configured)

---

## 🎯 Post-Release Roadmap

### Phase 2: Backend Migration
- [ ] Deploy Node + Prisma backend to Plesk
- [ ] Migrate analytics from NDJSON to MySQL
- [ ] Add user accounts/authentication

### Phase 3: Advanced Features
- [ ] User playlists
- [ ] Watch history sync across devices
- [ ] Advanced search (Algolia/Meilisearch)
- [ ] Recommendations engine

### Phase 4: Mobile Apps
- [ ] React Native app (iOS/Android)
- [ ] Offline download support
- [ ] Push notifications

---

**Last Updated**: 2024-01-XX  
**Version**: 1.0.0
