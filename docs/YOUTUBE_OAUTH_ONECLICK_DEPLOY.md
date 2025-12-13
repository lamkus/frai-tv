# YouTube OAuth “One-Click” Admin Connect

Goal: connect the backend once to YouTube with **write access**, then update titles/descriptions from the app.

## What you get

- Admin page: `/admin/login`
- Connect button that starts Google OAuth
- Backend stores tokens in Prisma `Settings` (key: `youtube_oauth_tokens`)
- Admin API endpoints:
  - `GET /api/admin/youtube/oauth/url`
  - `GET /api/admin/youtube/oauth/status`
  - `POST /api/admin/youtube/oauth/disconnect`
  - `GET /api/admin/youtube/oauth/callback`
  - `POST /api/admin/youtube/videos/:ytId`
  - `GET /api/admin/youtube/playlists`
  - `POST /api/admin/youtube/playlists`
  - `POST /api/admin/youtube/playlists/:playlistId/items`
  - `POST /api/admin/youtube/series/sync`

## 1) Create Google OAuth credentials

In Google Cloud Console:

1. Create/select project
2. Enable **YouTube Data API v3**
3. Configure OAuth consent screen
4. Create **OAuth Client ID** (type: Web application)
5. Add **Authorized redirect URI**:

`https://YOUR_DOMAIN/api/admin/youtube/oauth/callback`

Copy:
- Client ID → `YOUTUBE_OAUTH_CLIENT_ID`
- Client secret → `YOUTUBE_OAUTH_CLIENT_SECRET`

## 2) Set backend env vars

In your backend environment (Plesk / Node env):

- `ADMIN_SECRET` = long random string
- `YOUTUBE_OAUTH_CLIENT_ID` = from Google
- `YOUTUBE_OAUTH_CLIENT_SECRET` = from Google
- `YOUTUBE_OAUTH_REDIRECT_URI` = exact redirect URL
- Optional: `FRONTEND_BASE_URL=https://YOUR_DOMAIN`

See example in code/backend/.env.example.

## 3) Ensure reverse proxy routes `/api/*` to backend

Your nginx/plesk config must route `/api/` to the backend port, and serve the SPA normally.

## 4) Connect once

1. Open: `https://YOUR_DOMAIN/admin/login`
2. Paste `ADMIN_SECRET`
3. Click **Connect YouTube OAuth**
4. Approve consent
5. You should get redirected back to `/admin/login?connected=1`
6. Click **Check status** → should show CONNECTED

## 5) Push a title/description update

On `/admin/login`:

- Enter a YouTube video id (e.g. `3gzbxznJ_PM`)
- Paste title + description
- Click **Push to YouTube**

Notes:
- The backend preserves the current `categoryId` by fetching the existing snippet first.
- If Google doesn’t return a refresh token, disconnect and reconnect (Google only returns it on first consent or when forced).

## 6) Auto-create “pro” series playlists (Popeye fix)

This creates two playlists per detected series:
- `SERIES — Episodes`
- `SERIES — Compilations`

And adds videos without duplicating existing playlist items.

Example request:

`POST /api/admin/youtube/series/sync`

Body:
```json
{ "seriesId": "popeye" }
```

Heuristic:
- “Compilation” if title looks like marathon/compilation/collection/etc OR duration ≥ 30 minutes.

## Security note

`ADMIN_SECRET` protects admin endpoints. Treat it like a password.
- Don’t share it publicly
- Rotate it if leaked
