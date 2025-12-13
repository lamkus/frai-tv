import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

// If Postgres uses an auth method that node-postgres can't handle (e.g. GSS/SSPI),
// pg-protocol can throw an uncaught exception. For the ad-landing use case we prefer
// to keep the API alive and gracefully run without DB.
if (globalThis.__DB_DISABLED__ === undefined) {
  globalThis.__DB_DISABLED__ = false;
}

let prisma = null;

process.on('uncaughtException', (err) => {
  const msg = String(err?.message || '');
  if (msg.startsWith('Unknown authenticationOk message type ')) {
    console.error('Postgres auth method unsupported; disabling DB and continuing:', msg);
    globalThis.__DB_DISABLED__ = true;
    prisma = null;
    return;
  }

  console.error('Uncaught exception:', err);
  process.exit(1);
});

const app = express();
const PORT = process.env.PORT || 4000;

// Middlewares
app.use(cors());
app.use(express.json());

import {
  fetchChannelUploads,
  getCachedVideos,
  fetchChannelPlaylists,
  fetchPlaylistVideos,
  groupVideosBySeries,
  extractSeries,
} from './services/youtubeImporter.js';
import getPrisma from './services/dbClient.js';
import {
  requireAdminSecret,
  getAuthUrl,
  exchangeCodeForTokens,
  saveTokens,
  loadTokens,
  clearTokens,
  getYoutubeClient,
} from './services/youtubeOAuth.js';
import {
  createPlaylistAdmin,
  createOrAddPlaylistItem,
  listMyPlaylistsAdmin,
  syncSeriesPlaylists,
} from './services/youtubeAdminSync.js';
import { fetchLivestreams } from './services/youtubeLive.js';

// Placeholder data
// Load cached videos if available (fallback) — the importer updates this cache
let videos = [];
prisma = getPrisma();

// Load either from DB (if available) or from cached importer cache
(async () => {
  if (prisma) {
    try {
      const dbVideos = await prisma.video.findMany({ where: { hidden: false }, take: 500 });
      if (dbVideos && dbVideos.length > 0) {
        videos = dbVideos.map((v) => ({
          id: v.id,
          ytId: v.ytId,
          title: v.title,
          description: v.description,
          thumbnail: v.thumbnailUrl || v.customThumbnail,
          publishDate: v.publishDate?.toISOString?.() || null,
        }));
      }
    } catch (e) {
      console.warn('Failed loading videos from DB, falling back to cache', e?.message);
    }
  }

  if (!videos || videos.length === 0) {
    const cached = await getCachedVideos();
    if (cached && cached.length > 0) {
      videos = cached.map((v, idx) => ({
        id: idx + 1,
        ytId: v.id,
        title: v.title,
        description: v.description,
        thumbnail: v.thumbnail,
        publishDate: v.publishDate,
      }));
    } else {
      videos = [
        {
          id: 1,
          title: 'Beispielvideo 1',
          description: 'Dies ist ein Beispielvideo',
          embedUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          category: 'Beispiel',
          duration: 212,
          publishDate: '2020-01-01',
          ytId: 'dQw4w9WgXcQ',
        },
      ];
    }
  }
})();

// API Routes
// basic health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// simple telemetry: request counting and basic metrics
let requestCount = 0;
app.use((req, res, next) => {
  requestCount += 1;
  next();
});

app.get('/api/metrics', (req, res) => {
  const mem = process.memoryUsage();
  res.json({
    uptime: process.uptime(),
    nodeVersion: process.version,
    memory: mem,
    requestCount,
  });
});

// ============================================================================
// LIVE / SENDER ENDPOINTS
// ============================================================================

// Returns current live streams and upcoming scheduled streams for a channel
app.get('/api/livestreams', async (req, res) => {
  const channelId = req.query.channelId || process.env.REMAIKE_CHANNEL_ID;
  if (!channelId) {
    return res.status(400).json({ error: 'channelId required (set REMAIKE_CHANNEL_ID env)' });
  }

  const maxResults = Math.min(Math.max(parseInt(req.query.maxResults || '8', 10) || 8, 1), 25);
  const force = String(req.query.force || '') === '1';

  try {
    const data = await fetchLivestreams({ channelId, maxResults, force });
    return res.json(data);
  } catch (e) {
    console.error('livestreams error', e?.message || e);
    return res.status(500).json({ error: 'Failed to fetch livestreams' });
  }
});

app.get('/api/videos', (req, res) => {
  const limit = Math.min(Math.max(parseInt(req.query.limit || '200', 10) || 200, 1), 500);
  const cursor = req.query.cursor ? parseInt(String(req.query.cursor), 10) : null;
  const q = typeof req.query.q === 'string' ? req.query.q.trim() : '';

  // If DB available, return results from DB with basic pagination/search support.
  if (prisma) {
    const where = {
      hidden: false,
      ...(q
        ? {
            OR: [
              { title: { contains: q, mode: 'insensitive' } },
              { description: { contains: q, mode: 'insensitive' } },
              { customTitle: { contains: q, mode: 'insensitive' } },
              { customDescription: { contains: q, mode: 'insensitive' } },
            ],
          }
        : {}),
    };

    prisma.video
      .findMany({
        where,
        orderBy: { id: 'asc' },
        ...(cursor ? { cursor: { id: cursor }, skip: 1 } : {}),
        take: limit,
      })
      .then((rows) => {
        const data = rows.map((v) => ({ ...v, thumbnail: v.thumbnailUrl || v.customThumbnail }));
        const nextCursor = rows.length > 0 ? rows[rows.length - 1].id : null;
        res.json({ data, pageInfo: { limit, nextCursor, hasMore: rows.length === limit } });
      })
      .catch(() => res.json({ data: videos }));
    return;
  }

  res.json({ data: videos });
});

app.get('/api/videos/:id', (req, res) => {
  const video = videos.find((v) => v.id === parseInt(req.params.id, 10));
  if (!video) return res.status(404).json({ error: 'Video not found' });
  res.json({ data: video });
});

// Video stats endpoint - returns YouTube statistics for a given ytId
app.get('/api/video-stats/:ytId', async (req, res) => {
  const { ytId } = req.params || {};
  if (!ytId) return res.status(400).json({ error: 'ytId required' });

  try {
    const { getVideoStatistics } = await import('./services/youtubeImporter.js');
    const stats = await getVideoStatistics(ytId);
    if (!stats) return res.status(404).json({ error: 'Stats not available' });
    return res.json({ data: stats });
  } catch (err) {
    console.error('video-stats error', err?.message || err);
    return res.status(500).json({ error: 'Failed to fetch video stats' });
  }
});

// ============================================================================
// PLAYLIST & SERIES ENDPOINTS
// ============================================================================

// Get all playlists from channel
app.get('/api/playlists', async (req, res) => {
  const channelId = req.query.channelId || process.env.REMAIKE_CHANNEL_ID;
  if (!channelId) {
    return res.status(400).json({ error: 'channelId required (set REMAIKE_CHANNEL_ID env)' });
  }

  try {
    const playlists = await fetchChannelPlaylists(channelId);
    return res.json({ data: playlists });
  } catch (err) {
    console.error('playlists error', err?.message);
    return res.status(500).json({ error: 'Failed to fetch playlists' });
  }
});

// Get videos in a specific playlist
app.get('/api/playlists/:playlistId/videos', async (req, res) => {
  const { playlistId } = req.params;
  const maxResults = parseInt(req.query.maxResults || '50', 10);

  try {
    const videos = await fetchPlaylistVideos(playlistId, maxResults);
    return res.json({ data: videos });
  } catch (err) {
    console.error('playlist-videos error', err?.message);
    return res.status(500).json({ error: 'Failed to fetch playlist videos' });
  }
});

// Get all videos grouped by series
app.get('/api/series', async (req, res) => {
  try {
    // Get all videos (from cache or DB)
    let allVideos = videos;
    if (prisma) {
      try {
        const take = Math.min(Math.max(parseInt(req.query.limit || '5000', 10) || 5000, 1), 5000);
        const dbVideos = await prisma.video.findMany({ where: { hidden: false }, take });
        if (dbVideos.length > 0) {
          allVideos = dbVideos.map((v) => ({
            id: v.id,
            ytId: v.ytId,
            title: v.title,
            description: v.description,
            thumbnail: v.thumbnailUrl,
            year: v.year,
            category: v.category,
          }));
        }
      } catch {
        // use in-memory videos
      }
    }

    const grouped = groupVideosBySeries(allVideos);
    return res.json({
      data: {
        series: grouped.series,
        seriesCount: grouped.series.length,
        standaloneCount: grouped.standalone.length,
      },
    });
  } catch (err) {
    console.error('series error', err?.message);
    return res.status(500).json({ error: 'Failed to group videos by series' });
  }
});

// Get videos for a specific series
app.get('/api/series/:seriesId', async (req, res) => {
  const { seriesId } = req.params;

  try {
    let allVideos = videos;
    if (prisma) {
      try {
        const take = Math.min(Math.max(parseInt(req.query.limit || '5000', 10) || 5000, 1), 5000);
        const dbVideos = await prisma.video.findMany({ where: { hidden: false }, take });
        if (dbVideos.length > 0) {
          allVideos = dbVideos.map((v) => ({
            id: v.id,
            ytId: v.ytId,
            title: v.title,
            description: v.description,
            thumbnail: v.thumbnailUrl,
            year: v.year,
            category: v.category,
          }));
        }
      } catch {
        // use in-memory videos
      }
    }

    const grouped = groupVideosBySeries(allVideos);
    const series = grouped.series.find((s) => s.id === seriesId);

    if (!series) {
      return res.status(404).json({ error: `Series '${seriesId}' not found` });
    }

    return res.json({ data: series });
  } catch (err) {
    console.error('series error', err?.message);
    return res.status(500).json({ error: 'Failed to fetch series' });
  }
});

// Manual trigger to refresh a channel's uploads (safe for dev/admin use)
app.post('/api/refresh-channel', async (req, res) => {
  const { channelId } = req.body || {};
  if (!channelId) return res.status(400).json({ error: 'channelId required' });

  try {
    const maxResults = parseInt(req.body.maxResults || '50', 10) || 50;
    const items = await fetchChannelUploads(channelId, maxResults);
    // normalize to "videos" array shape
    videos = items.map((v, idx) => ({
      id: idx + 1,
      ytId: v.id,
      title: v.title,
      description: v.description,
      thumbnail: v.thumbnail,
      publishDate: v.publishDate,
    }));

    // If Prisma DB present, upsert videos into DB for long-term storage
    if (prisma) {
      try {
        let added = 0;
        let updated = 0;
        for (const item of items) {
          const up = await prisma.video.upsert({
            where: { ytId: item.id },
            create: {
              ytId: item.id,
              title: item.title,
              description: item.description,
              thumbnailUrl: item.thumbnail,
              publishDate: item.publishDate ? new Date(item.publishDate) : null,
            },
            update: {
              title: item.title,
              description: item.description,
              thumbnailUrl: item.thumbnail,
              publishDate: item.publishDate ? new Date(item.publishDate) : undefined,
            },
          });
          if (up) {
            // cannot reliably detect, just increment updated for now
            // (create vs update information is not returned separately by upsert)
            updated += 1;
          }
        }
        if (prisma) {
          await prisma.importLog.create({
            data: {
              channelId,
              status: 'success',
              videosFound: items.length,
              videosAdded: added,
              videosUpdated: updated,
              completedAt: new Date(),
            },
          });
        }
      } catch (e) {
        console.error('DB upsert failed:', e?.message || e);
        try {
          await prisma.importLog.create({
            data: {
              channelId,
              status: 'partial',
              videosFound: items.length,
              errorMessage: `${e?.message || e}`,
            },
          });
        } catch (ee) {
          // noop
        }
      }
    }

    return res.json({ status: 'ok', imported: videos.length });
  } catch (err) {
    console.error('refresh-channel error', err?.message || err);
    return res.status(500).json({ error: 'Failed to refresh channel' });
  }
});

// Persist watch progress (used by frontend when users are signed-in)
app.post('/api/watch-progress', async (req, res) => {
  const { userId, ytId, progress, duration } = req.body || {};
  if (!ytId || typeof progress !== 'number' || typeof duration !== 'number') {
    return res.status(400).json({ error: 'ytId, progress and duration required' });
  }

  // Save in DB when available
  if (prisma) {
    try {
      const pct = duration > 0 ? (progress / duration) * 100 : 0;
      // find existing
      const existing = await prisma.watchProgress.findFirst({
        where: { userId: userId || null, ytId },
      });
      if (existing) {
        const updated = await prisma.watchProgress.update({
          where: { id: existing.id },
          data: { progress, duration, percentage: pct },
        });
        return res.json({ data: updated });
      }

      const created = await prisma.watchProgress.create({
        data: { userId: userId || null, ytId, progress, duration, percentage: pct },
      });
      return res.json({ data: created });
    } catch (e) {
      console.error('watch-progress save failed:', e?.message || e);
      return res.status(500).json({ error: 'Failed to save watch progress' });
    }
  }

  // Fallback: write to cache file (tmp/watch_progress.json)
  try {
    const fs = await import('fs/promises');
    const path = await import('path');
    const CACHE = path.resolve(process.cwd(), 'tmp', 'watch_progress.json');
    let existing = [];
    try {
      const txt = await fs.readFile(CACHE, 'utf8');
      existing = JSON.parse(txt) || [];
    } catch (e) {
      existing = [];
    }
    // replace existing entry for ytId/userId
    const filtered = existing.filter(
      (w) => !(w.ytId === ytId && (w.userId || null) === (userId || null))
    );
    filtered.push({
      userId: userId || null,
      ytId,
      progress,
      duration,
      timestamp: new Date().toISOString(),
    });
    await fs.mkdir(path.dirname(CACHE), { recursive: true });
    await fs.writeFile(CACHE, JSON.stringify({ items: filtered }, null, 2), 'utf8');
    return res.json({ data: { ytId, progress, duration } });
  } catch (e) {
    console.error('watch-progress cache save failed:', e?.message || e);
    return res.status(500).json({ error: 'Failed to save watch progress (fallback)' });
  }
});

app.get('/api/watch-progress', async (req, res) => {
  const userId = req.query.userId || null;
  if (prisma) {
    try {
      const rows = await prisma.watchProgress.findMany({ where: { userId: userId || null } });
      return res.json({ data: rows });
    } catch (e) {
      return res.status(500).json({ error: 'Failed to load watch progress' });
    }
  }

  // fallback: read cache
  try {
    const fs = await import('fs/promises');
    const path = await import('path');
    const CACHE = path.resolve(process.cwd(), 'tmp', 'watch_progress.json');
    const txt = await fs.readFile(CACHE, 'utf8');
    const json = JSON.parse(txt);
    const items = (json.items || []).filter((w) => (userId ? w.userId === userId : true));
    return res.json({ data: items });
  } catch (e) {
    return res.json({ data: [] });
  }
});

// Verify Google ID token (simple server-side verification) — optional
app.post('/api/auth/verify', async (req, res) => {
  const { id_token } = req.body || {};
  if (!id_token) return res.status(400).json({ error: 'id_token required' });

  try {
    // Use Google's tokeninfo endpoint to validate id_token
    const verifyUrl = `https://oauth2.googleapis.com/tokeninfo?id_token=${encodeURIComponent(
      id_token
    )}`;
    const { data } = await (await import('axios')).default.get(verifyUrl, { timeout: 5000 });

    // tokeninfo returns user info if valid — we forward safe subset
    const user = {
      sub: data.sub,
      email: data.email,
      name: data.name,
      picture: data.picture,
      locale: data.locale,
    };

    return res.json({ user });
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
});

// ============================================================================
// ADMIN: YOUTUBE OAUTH (WRITE ACCESS)
// ============================================================================

const oauthStates = new Map();
const OAUTH_STATE_TTL_MS = 10 * 60 * 1000;

function cleanupOauthStates() {
  const now = Date.now();
  for (const [key, value] of oauthStates.entries()) {
    if (!value?.createdAt || now - value.createdAt > OAUTH_STATE_TTL_MS) {
      oauthStates.delete(key);
    }
  }
}

function getFrontendRedirectUrl(req) {
  const envRedirect = process.env.ADMIN_OAUTH_SUCCESS_REDIRECT;
  if (envRedirect) return envRedirect;

  const base = process.env.FRONTEND_BASE_URL;
  if (base) return `${base.replace(/\/$/, '')}/admin/login?connected=1`;

  // Best-effort same-origin redirect
  const proto = req.get('x-forwarded-proto') || req.protocol;
  const host = req.get('x-forwarded-host') || req.get('host');
  return `${proto}://${host}/admin/login?connected=1`;
}

app.get('/api/admin/youtube/oauth/url', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  cleanupOauthStates();
  const state = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  oauthStates.set(state, { createdAt: Date.now() });

  try {
    const url = await getAuthUrl({ state });
    return res.json({ url });
  } catch (e) {
    return res.status(500).json({ error: e?.message || 'Failed to generate auth url' });
  }
});

app.get('/api/admin/youtube/oauth/callback', async (req, res) => {
  const { code, state, error } = req.query || {};
  if (error) return res.status(400).send(`OAuth error: ${String(error)}`);
  if (!code || !state) return res.status(400).send('Missing code/state');

  const entry = oauthStates.get(String(state));
  oauthStates.delete(String(state));
  if (!entry) return res.status(400).send('Invalid or expired state');

  try {
    const tokens = await exchangeCodeForTokens(String(code));
    await saveTokens({ prisma, tokens });

    const redirectTo = getFrontendRedirectUrl(req);
    return res.redirect(302, redirectTo);
  } catch (e) {
    console.error('oauth callback error', e?.message || e);
    return res.status(500).send('OAuth exchange failed');
  }
});

app.get('/api/admin/youtube/oauth/status', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  try {
    const tokens = await loadTokens({ prisma });
    if (!tokens) return res.json({ connected: false });
    return res.json({
      connected: true,
      scope: tokens.scope || null,
      expiry_date: tokens.expiry_date || null,
      has_refresh_token: Boolean(tokens.refresh_token),
    });
  } catch (e) {
    return res.status(500).json({ error: 'Failed to read OAuth status' });
  }
});

app.post('/api/admin/youtube/oauth/disconnect', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  try {
    await clearTokens({ prisma });
    return res.json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: 'Failed to disconnect' });
  }
});

// Update YouTube video title/description (uses existing snippet.categoryId)
app.post('/api/admin/youtube/videos/:ytId', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  const { ytId } = req.params || {};
  const { title, description, tags } = req.body || {};
  if (!ytId) return res.status(400).json({ error: 'ytId required' });
  if (typeof title !== 'string' && typeof description !== 'string' && !Array.isArray(tags)) {
    return res.status(400).json({ error: 'Provide at least one of: title, description, tags[]' });
  }

  try {
    const youtube = await getYoutubeClient({ prisma });
    if (!youtube) return res.status(409).json({ error: 'YouTube OAuth not connected' });

    const existing = await youtube.videos.list({
      part: ['snippet'],
      id: [ytId],
      maxResults: 1,
    });

    const item = existing?.data?.items?.[0];
    const snippet = item?.snippet;
    if (!snippet) return res.status(404).json({ error: 'Video not found or no snippet' });

    const updatedSnippet = {
      ...snippet,
      title: typeof title === 'string' ? title : snippet.title,
      description: typeof description === 'string' ? description : snippet.description,
      tags: Array.isArray(tags) ? tags : snippet.tags,
      categoryId: snippet.categoryId,
    };

    const updated = await youtube.videos.update({
      part: ['snippet'],
      requestBody: { id: ytId, snippet: updatedSnippet },
    });

    return res.json({ ok: true, data: updated.data });
  } catch (e) {
    console.error('youtube update error', e?.message || e);
    return res.status(500).json({ error: 'Failed to update YouTube video' });
  }
});

// Create a playlist (admin)
app.post('/api/admin/youtube/playlists', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  const { title, description, privacyStatus } = req.body || {};
  if (!title) return res.status(400).json({ error: 'title required' });

  try {
    const youtube = await getYoutubeClient({ prisma });
    if (!youtube) return res.status(409).json({ error: 'YouTube OAuth not connected' });

    const created = await createPlaylistAdmin({ youtube, title, description, privacyStatus });
    return res.json({ ok: true, data: created });
  } catch (e) {
    console.error('create playlist error', e?.message || e);
    return res.status(500).json({ error: 'Failed to create playlist' });
  }
});

// List my playlists (admin)
app.get('/api/admin/youtube/playlists', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  try {
    const youtube = await getYoutubeClient({ prisma });
    if (!youtube) return res.status(409).json({ error: 'YouTube OAuth not connected' });

    const data = await listMyPlaylistsAdmin({ youtube });
    return res.json({ ok: true, data });
  } catch (e) {
    console.error('list playlists error', e?.message || e);
    return res.status(500).json({ error: 'Failed to list playlists' });
  }
});

// Add a video to a playlist (admin)
app.post('/api/admin/youtube/playlists/:playlistId/items', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  const { playlistId } = req.params || {};
  const { videoId } = req.body || {};
  if (!playlistId) return res.status(400).json({ error: 'playlistId required' });
  if (!videoId) return res.status(400).json({ error: 'videoId required' });

  try {
    const youtube = await getYoutubeClient({ prisma });
    if (!youtube) return res.status(409).json({ error: 'YouTube OAuth not connected' });

    await createOrAddPlaylistItem({ youtube, playlistId, videoId });
    return res.json({ ok: true });
  } catch (e) {
    console.error('add playlist item error', e?.message || e);
    return res.status(500).json({ error: 'Failed to add playlist item' });
  }
});

// Sync series playlists (Episodes vs Compilations) for all series or one series
app.post('/api/admin/youtube/series/sync', async (req, res) => {
  const auth = requireAdminSecret(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  const { seriesId } = req.body || {};

  try {
    const youtube = await getYoutubeClient({ prisma });
    if (!youtube) return res.status(409).json({ error: 'YouTube OAuth not connected' });

    // Pull videos (DB preferred)
    let allVideos = videos;
    if (prisma) {
      try {
        const dbVideos = await prisma.video.findMany({ where: { hidden: false }, take: 5000 });
        if (dbVideos.length > 0) {
          allVideos = dbVideos.map((v) => ({
            ytId: v.ytId,
            title: v.title,
            description: v.description,
          }));
        }
      } catch {
        // use in-memory
      }
    }

    const grouped = groupVideosBySeries(allVideos);
    const targetSeries = seriesId
      ? grouped.series.filter((s) => s.id === seriesId)
      : grouped.series;

    const results = [];
    for (const s of targetSeries) {
      const r = await syncSeriesPlaylists({
        youtube,
        seriesName: s.title || s.name || s.id,
        videos: s.videos || [],
      });
      results.push(r);
    }

    return res.json({ ok: true, data: results });
  } catch (e) {
    console.error('series sync error', e?.message || e);
    return res.status(500).json({ error: 'Failed to sync series playlists' });
  }
});

// TODO: Hier wird künftig die Anbindung an die Datenbank und die YouTube
// Data API implementiert. Der Import-Service sollte regelmäßige
// Aktualisierungen via cron durchführen (siehe Pflichtenheft).

app.listen(PORT, () => {
  console.log(`Backend server listening on port ${PORT}`);
});

// Schedule nightly import for configured REMAIKE_CHANNEL_ID if Prisma & API key available
if (process.env.REMAIKE_CHANNEL_ID && process.env.YOUTUBE_API_KEY && prisma) {
  const cron = (await import('node-cron')).default;
  // run at 02:30 every night
  cron.schedule('30 2 * * *', async () => {
    try {
      console.log('Scheduled import: starting channel sync for', process.env.REMAIKE_CHANNEL_ID);
      const items = await fetchChannelUploads(process.env.REMAIKE_CHANNEL_ID, 5000);
      console.log('Scheduled import: fetched', items.length, 'items');
      // Upsert items similar to /refresh-channel
      for (const item of items) {
        await prisma.video.upsert({
          where: { ytId: item.id },
          create: {
            ytId: item.id,
            title: item.title,
            description: item.description,
            thumbnailUrl: item.thumbnail,
            publishDate: item.publishDate ? new Date(item.publishDate) : null,
          },
          update: {
            title: item.title,
            description: item.description,
            thumbnailUrl: item.thumbnail,
            publishDate: item.publishDate ? new Date(item.publishDate) : undefined,
          },
        });
      }
      await prisma.importLog.create({
        data: {
          channelId: process.env.REMAIKE_CHANNEL_ID,
          status: 'success',
          videosFound: items.length,
          videosAdded: items.length,
        },
      });
    } catch (e) {
      console.error('Scheduled import failed:', e?.message || e);
    }
  });
}
