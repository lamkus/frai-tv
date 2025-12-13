import axios from 'axios';
import fs from 'fs/promises';
import path from 'path';

const CACHE_FILE = path.resolve(process.cwd(), 'tmp', 'livestreams_cache.json');
const DEFAULT_TTL_MS = 60 * 1000;

async function readCache() {
  try {
    const txt = await fs.readFile(CACHE_FILE, 'utf8');
    return JSON.parse(txt);
  } catch {
    return null;
  }
}

async function writeCache(data) {
  try {
    await fs.mkdir(path.dirname(CACHE_FILE), { recursive: true });
    await fs.writeFile(CACHE_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch {
    // noop
  }
}

async function searchChannel({ key, channelId, eventType, maxResults }) {
  const url = 'https://www.googleapis.com/youtube/v3/search';
  const res = await axios.get(url, {
    params: {
      key,
      channelId,
      part: 'snippet',
      type: 'video',
      eventType,
      maxResults,
      order: 'date',
    },
    timeout: 10000,
  });

  const items = res?.data?.items || [];
  return items
    .map((it) => {
      const ytId = it?.id?.videoId;
      const sn = it?.snippet;
      if (!ytId || !sn) return null;
      return {
        ytId,
        title: sn.title || '',
        description: sn.description || '',
        publishedAt: sn.publishedAt || null,
        thumbnail:
          sn.thumbnails?.maxres?.url ||
          sn.thumbnails?.high?.url ||
          sn.thumbnails?.medium?.url ||
          sn.thumbnails?.default?.url ||
          null,
      };
    })
    .filter(Boolean);
}

async function hydrateVideoDetails({ key, videoIds }) {
  if (!videoIds || videoIds.length === 0) return new Map();

  const url = 'https://www.googleapis.com/youtube/v3/videos';
  const res = await axios.get(url, {
    params: {
      key,
      id: videoIds.join(','),
      part: 'snippet,liveStreamingDetails,statistics',
      maxResults: videoIds.length,
    },
    timeout: 10000,
  });

  const items = res?.data?.items || [];
  const map = new Map();
  for (const it of items) {
    const id = it?.id;
    if (!id) continue;

    const live = it?.liveStreamingDetails || {};
    const stats = it?.statistics || {};
    map.set(id, {
      viewerCount: live?.concurrentViewers ? parseInt(live.concurrentViewers, 10) : null,
      scheduledStartTime: live?.scheduledStartTime || null,
      actualStartTime: live?.actualStartTime || null,
      actualEndTime: live?.actualEndTime || null,
      viewCount: stats?.viewCount ? parseInt(stats.viewCount, 10) : null,
    });
  }

  return map;
}

export async function fetchLivestreams({
  channelId,
  maxResults = 8,
  ttlMs = DEFAULT_TTL_MS,
  force = false,
} = {}) {
  const key = process.env.YOUTUBE_API_KEY;

  // Without API key, we can only serve cached results (or empty).
  if (!key) {
    const cached = await readCache();
    if (cached?.data) return cached.data;
    return { live: [], upcoming: [], fetchedAt: new Date().toISOString() };
  }

  const cached = await readCache();
  const now = Date.now();
  if (
    !force &&
    cached?.fetchedAt &&
    now - new Date(cached.fetchedAt).getTime() < ttlMs &&
    cached?.data
  ) {
    return cached.data;
  }

  if (!channelId) {
    throw new Error('channelId required (set REMAIKE_CHANNEL_ID env or pass channelId)');
  }

  const [liveBase, upcomingBase] = await Promise.all([
    searchChannel({ key, channelId, eventType: 'live', maxResults }),
    searchChannel({ key, channelId, eventType: 'upcoming', maxResults }),
  ]);

  const liveIds = liveBase.map((v) => v.ytId);
  const upcomingIds = upcomingBase.map((v) => v.ytId);

  // Hydrate with viewer counts + scheduled times (best-effort).
  const [liveDetails, upcomingDetails] = await Promise.all([
    hydrateVideoDetails({ key, videoIds: liveIds.slice(0, 50) }),
    hydrateVideoDetails({ key, videoIds: upcomingIds.slice(0, 50) }),
  ]);

  const live = liveBase.map((v) => ({ ...v, ...(liveDetails.get(v.ytId) || {}) }));
  const upcoming = upcomingBase.map((v) => ({ ...v, ...(upcomingDetails.get(v.ytId) || {}) }));

  const data = {
    live,
    upcoming,
    fetchedAt: new Date().toISOString(),
  };

  await writeCache({ fetchedAt: data.fetchedAt, data });
  return data;
}
