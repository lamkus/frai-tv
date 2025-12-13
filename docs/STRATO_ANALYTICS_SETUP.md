# STRATO Analytics Setup (FRai.TV) — Traffic + Video Engagement

This guide covers the practical “next steps” to measure:
- **Where visitors come from** (referrer / campaign / geo)
- **How long they stay** (session/page duration)
- **How they interact with embedded YouTube videos** (start/progress/complete)

## 1) What STRATO gives you “out of the box” (baseline)
Use this as a backup/verification layer.

- STRATO Hosting Statistik (referrers, browsers, basic counts) + logfile download:
  - https://www.strato.de/faq/hosting/so-nutzen-sie-die-statistikauswertungen-in-ihrem-hosting-paket/
- If you have Plesk access:
  - Enable Webalizer/AWStats for log-based charts:
    - https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/websites-and-domains/hosting-settings/general-settings.72050/
  - Use Plesk Log Browser to view/download access/error logs:
    - https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/customer-account-administration/log-files.65210/

Limitations:
- Log stats are **not** true “watch time” for YouTube embeds.
- STRATO “sessions” aren’t GA/Matomo-style session duration.

## 2) Recommended primary analytics: Matomo On-Premise (self-hosted)
Why:
- First-party analytics (data stays with you)
- Stronger GDPR posture than typical third-party analytics
- Full attribution (UTM), geo, sessions, funnels, events

High-level STRATO steps:
1. Create a subdomain like `stats.frai.tv` (or `analytics.frai.tv`).
2. Upload Matomo to that folder (or via Plesk).
3. Create a MySQL database/user in STRATO/Plesk.
4. Run the Matomo web installer and create a site for `frai.tv`.
5. Set up Matomo archiving (cron) if possible on your plan.

Matomo docs entrypoint:
- https://matomo.org/docs/

## 3) Website → Matomo tracking (already prepared in this repo)
The frontend supports optional external analytics **only after GDPR consent**.

Configure these Vite build-time variables:
- `VITE_MATOMO_URL=https://stats.frai.tv`
- `VITE_MATOMO_SITE_ID=1`

Where:
- Add them to `code/frontend/.env.production` (or to your build pipeline environment).

Then rebuild + deploy frontend.

## 4) YouTube engagement tracking (start/progress/complete)
Reality check:
- “Perfect watch time” is best measured in **YouTube Studio**.
- On your website, you can track **player events** (start/progress/complete) for optimization.

Best practical method:
- Google Tag Manager’s built-in **YouTube video trigger**
  - https://support.google.com/tagmanager/answer/7679325

Flow:
1. Create a GTM container and add it to the site (optional in this repo).
2. Enable a YouTube Video trigger (Start + Progress at 25/50/75% + Complete).
3. Send those events either:
   - to Matomo (events), or
   - to GA4 (if you accept the compliance overhead).

Repo variable for GTM loader:
- `VITE_GTM_ID=GTM-XXXXXXX`

Important GDPR note:
- YouTube’s iFrame API can set cookies; gate tracking behind consent.

## 5) Verification & Testing

1. Local dev verification (fast):
  - Start backend (`npm run dev`) and frontend (`npm run dev`).
  - Open the dev site and accept cookies.
  - Open the Admin `Analytics` tab and confirm it shows analytics data.
  - To simulate player events, open DevTools Console and run:
    ```js
     // Simulate video start event (only when VITE_DEBUG_MODE=true)
     window.__REMAIKE_ANALYTICS__ && window.__REMAIKE_ANALYTICS__.trackVideoStart('test-video', 'Test Video', 0);
     // Simulate progress
     window.__REMAIKE_ANALYTICS__ && window.__REMAIKE_ANALYTICS__.trackVideoEvent('test-video', 'progress', { position: 30, duration: 120 });
     // Simulate video end
     window.__REMAIKE_ANALYTICS__ && window.__REMAIKE_ANALYTICS__.trackVideoEnd('test-video');
    ```
  - In the Admin `Analytics` tab, click `Export` to confirm exported JSON contains these events.

2. Matomo verification (if installed):
  - Open Matomo at `https://stats.YOUR_DOMAIN.de` and look in Realtime or Events.
  - Ensure events from the frontend are registered (Video start/progress/end).
  - Confirm UTM campaign attribution when visiting `/sender?utm_source=youtube&utm_medium=paid&utm_campaign=sender_202512`.

## 6) Matomo automation script (VPS)

We added a helper script at `installation/scripts/matomo_installation.sh` that automates a Matomo installation on Debian/Ubuntu (Strato VPS). It will install PHP, MariaDB, Nginx, download Matomo, set up a DB and configure cron archiving. For Plesk-managed servers, prefer the Plesk GUI.

Commands:

```bash
# Run installation script
ssh root@YOUR_SERVER_IP
cd /tmp
curl -O https://raw.githubusercontent.com/<YOUR_REPO>/master/installation/scripts/matomo_installation.sh
chmod +x matomo_installation.sh
sudo ./matomo_installation.sh --domain stats.YOUR_DOMAIN.de
```

After installation, finish Matomo installation via the web UI and add `VITE_MATOMO_URL`/`VITE_MATOMO_SITE_ID` to your frontend build environment.


3. Production sanity checks after deploy:
  - Check that `/api/livestreams` responds with configured `REMAIKE_CHANNEL_ID` (or returns 400 if not set).
  - Ensure the `sender` landing loads inside 1s TTFB under normal load.


## 5) Campaign attribution for YouTube Ads (critical)
Always use UTMs on ad landing URLs:
- `utm_source=youtube`
- `utm_medium=paid`
- `utm_campaign=sender_YYYYMM`
- Optional: `utm_content=creativeA`

Example:
- `https://frai.tv/sender?utm_source=youtube&utm_medium=paid&utm_campaign=sender_202512&utm_content=videoA`

## 6) Proof checklist
- Open `/sender` in an incognito window:
  - Consent modal shows; decline → no tracking; accept → tracking active
- Check Matomo:
  - Realtime visitors visible
  - Referrer/campaign visible (UTMs)
  - Events visible (Video start/progress/complete)
