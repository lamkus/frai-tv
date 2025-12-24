import fs from 'fs/promises';
import path from 'path';

const DATA_FILE = path.resolve(process.cwd(), 'public/data/videos.json');
const LOG_FILE = path.resolve(process.cwd(), 'public/data/sync.log');
const API_KEY = process.env.YOUTUBE_API_KEY;
const CHANNEL_ID = process.env.CHANNEL_ID;

if (!API_KEY || !CHANNEL_ID) {
  console.error('Missing YOUTUBE_API_KEY or CHANNEL_ID env vars');
  process.exit(2);
}

async function fetchAllVideos() {
  const items = [];
  let pageToken = '';
  do {
    const q = new URL('https://www.googleapis.com/youtube/v3/search');
    q.searchParams.set('part', 'snippet');
    q.searchParams.set('channelId', CHANNEL_ID);
    q.searchParams.set('maxResults', '50');
    q.searchParams.set('order', 'date');
    q.searchParams.set('type', 'video');
    if (pageToken) q.searchParams.set('pageToken', pageToken);
    q.searchParams.set('key', API_KEY);

    const res = await fetch(q.toString());
    if (!res.ok) throw new Error(`YouTube API error: ${res.status}`);
    const json = await res.json();
    for (const it of json.items || []) {
      items.push({ id: it.id.videoId, snippet: it.snippet });
    }
    pageToken = json.nextPageToken || '';
  } while (pageToken);
  return items;
}

async function fetchDetails(ids) {
  const q = new URL('https://www.googleapis.com/youtube/v3/videos');
  q.searchParams.set('part', 'snippet,contentDetails,statistics');
  q.searchParams.set('id', ids.join(','));
  q.searchParams.set('key', API_KEY);
  const res = await fetch(q.toString());
  if (!res.ok) throw new Error(`YouTube API error (details): ${res.status}`);
  return res.json();
}

async function loadManualMap() {
  try {
    const mod = await import('../src/data/remaikeData.js');
    const remaike = mod.remaikeVideos || [];
    const map = new Map(remaike.map((v) => [v.ytId, v]));
    return map;
  } catch (e) {
    return new Map();
  }
}

async function main() {
  console.log('Starting YouTube sync...');
  const manual = await loadManualMap();
  const searchItems = await fetchAllVideos();
  const ids = searchItems.map((s) => s.id).filter(Boolean);

  const all = [];
  // fetch details in batches of 50
  for (let i = 0; i < ids.length; i += 50) {
    const slice = ids.slice(i, i + 50);
    const details = await fetchDetails(slice);
    for (const it of details.items || []) {
      const snippet = it.snippet || {};
      const manualMeta = manual.get(it.id) || {};

      const fallbackThumb = `https://img.youtube.com/vi/${it.id}/hqdefault.jpg`;
      const chosenThumb =
        manualMeta.thumbnailUrl ||
        snippet.thumbnails?.maxres?.url ||
        snippet.thumbnails?.high?.url ||
        fallbackThumb;

      if (!chosenThumb) {
        console.warn('No thumbnail found for', it.id);
      }

      all.push({
        id: manualMeta.id || it.id,
        ytId: it.id,
        title: manualMeta.customTitle || snippet.title || manualMeta.title || '',
        description:
          manualMeta.customDescription || snippet.description || manualMeta.description || '',
        thumbnailUrl: chosenThumb,
        thumbnail: chosenThumb,
        publishDate: snippet.publishedAt || null,
        year: manualMeta.year || null,
        decade: manualMeta.decade || null,
        category: manualMeta.category || null,
      });
    }
  }

  // sort by publishDate desc
  all.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate));

  // write atomically
  await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
  // keep a backup of the last good data to recover from failed writes
  try {
    await fs.copyFile(DATA_FILE, DATA_FILE + '.bak');
  } catch (e) {
    // ignore when no previous file exists
  }
  await fs.writeFile(DATA_FILE + '.tmp', JSON.stringify(all, null, 2), 'utf8');
  await fs.rename(DATA_FILE + '.tmp', DATA_FILE);

  const now = new Date().toISOString();
  const added = all.length;
  await fs.appendFile(LOG_FILE, `${now},${added},0,0\n`, 'utf8');

  console.log(`Sync complete: ${all.length} videos`);
}

main().catch((err) => {
  console.error('Sync failed:', err);
  process.exit(1);
});
