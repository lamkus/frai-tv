# Go-Live Checklist — remAIke.TV

This checklist helps you mark your deployment as "Production Ready" and covers the minimum items for a safe launch.

## 1. Infrastructure
- [ ] Backend deployed and running under PM2
  - `pm2 status` shows `remaike-backend` running
  - `curl http://127.0.0.1:4000/api/health` returns status OK
- [ ] Nginx or Plesk routing configured
  - `/api/*` reverse proxy to backend
  - SPA fallback to `index.html`
- [ ] SSL certificate installed (Let's Encrypt or other)
- [ ] CDN set up for `static` assets if available

## 2. Database/Cache
- [ ] PostgreSQL reachable with correct `DATABASE_URL`
- [ ] Prisma migrations applied (`npx prisma migrate deploy`)
- [ ] Redis (if used) healthy and connected

## 3. Analytics & Monitoring
- [ ] Matomo running and ingesting events (`stats.YOUR_DOMAIN.de`)
- [ ] Matomo archiving cron runs hourly (or via archiving trigger)
- [ ] Alerts configured (e.g. uptime monitoring, error logs)
- [ ] Optional: Datadog/Strato metrics/Prometheus/Grafana for infra

## 4. Privacy & Compliance
- [ ] GDPR cookie modal present and blocking tracking before accept
- [ ] Admin OAuth configured and token storage secure
- [ ] Privacy policy updated and linked on site
- [ ] Review YouTube ToS and API quotas

## 5. Frontend
- [ ] Production build completed and deployed
- [ ] Env vars configured for production (`VITE_API_URL`, `VITE_MATOMO_URL`) in `code/frontend/.env.production`
- [ ] Test `sender` page for On-Air / Off-Air states

## 6. Ads / Campaigns
- [ ] All ad links contain UTM parameters
- [ ] Test ad click → landing (UTM attribution in Matomo)

## 7. QA & Beta
- [ ] Beta testing completed (100 users)
- [ ] Core bugs logged & fixed
- [ ] Performance test (load test) ran and meets expected capacity metrics

## 8. Release
- [ ] Tag release `v1.0.0` and create changelog
- [ ] Run final smoke test (page load, video playback, consent, tracking events)
- [ ] Backup DB and create rollback plan

---

When all boxes are checked, mark the site as Live and monitor traffic for the first 72 hours.
