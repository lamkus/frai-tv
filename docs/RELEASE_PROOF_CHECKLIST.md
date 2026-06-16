# Release Proof Checklist — FRai.TV

Use this checklist to validate a production release end‑to‑end.

## A) Deploy Target
- [ ] Confirm correct deploy path for www.frai.tv (root `/` vs `/FRai.TV/`).
- [ ] Upload latest `dist/` from `code/frontend`.

## B) Cache & Service Worker
- [ ] Hard refresh (Ctrl+Shift+R) on desktop.
- [ ] Clear site data in browser (service worker + cache) and reload.

## C) Backend Health
- [ ] `GET /api/health` returns `{ status: "ok" }` on production domain.
- [ ] `GET /api/livestreams` returns data or a clean 400 when `REMAIKE_CHANNEL_ID` is missing.

## D) Core UX
- [ ] Home loads without console errors.
- [ ] `/sender` renders On‑Air / Off‑Air states.
- [ ] Video playback works (YouTube embed loads after consent).

## E) Analytics & Consent
- [ ] GDPR modal appears for first‑time visit.
- [ ] Decline → no tracking events fired.
- [ ] Accept → analytics events fire (Matomo/GTM if configured).

## F) Ads / Attribution
- [ ] UTM test URL shows campaign attribution (e.g., `?utm_source=youtube&utm_medium=paid&utm_campaign=sender_YYYYMM`).

## G) Regression Sanity
- [ ] Top navigation links work.
- [ ] Mobile layout (320–390px) works on `/sender` and `/watch`.

---

If any item fails, mark it and fix before tagging a release.
