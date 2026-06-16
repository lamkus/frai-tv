# FRai.TV — Release Proof Checklist

This checklist defines the minimum evidence to declare a production release as “ready”.

## 1) Local build & lint (required)
- [ ] Frontend build passes (`npm run build`)
- [ ] Frontend lint passes (`npm run lint`)
- [ ] Backend syntax check passes (`node --check src/index.js`)

## 2) Backend health (required)
- [ ] `/api/health` returns `{ "status": "ok" }`
- [ ] `/api/metrics` returns uptime + requestCount
- [ ] `/api/livestreams` returns data (or clean 400 if `REMAIKE_CHANNEL_ID` missing)

## 3) Frontend health (required)
- [ ] Home loads without console errors
- [ ] `/sender` loads and “off‑air” state renders with empty streams
- [ ] No React runtime errors in console

## 4) Analytics (recommended)
- [ ] GDPR modal: decline → no analytics, accept → analytics active
- [ ] Matomo realtime shows events after consent
- [ ] UTM attribution visible for `/sender?utm_source=youtube...`

## 5) Stability checks (required)
- [ ] Hard refresh bypasses service worker cache
- [ ] On slow 3G throttling: hero still renders within 3 seconds
- [ ] API errors handled gracefully (no white screen)

## 6) Release sign‑off (required)
- [ ] Checklist signed
- [ ] Rollback plan recorded
- [ ] Release tag (vX.Y.Z)

---

## Notes
- If any check fails, do not call the release “final”.
- For live domain validation, use your own network access (this environment cannot reach external domains reliably).
