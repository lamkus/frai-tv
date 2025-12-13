import axios from 'axios';
import fs from 'fs/promises';
import path from 'path';

const CACHE_FILE = path.resolve(process.cwd(), 'tmp', 'youtube_cache.json');

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetch playlist items (uploads) from a channel with simple retries and exponential backoff.
 * Uses YOUTUBE_API_KEY env var. Falls back to local cache file when unavailable.
 */
export async function fetchChannelUploads(channelId, maxResults = 50) {
  const key = process.env.YOUTUBE_API_KEY;
  if (!key) {
    // Try to return cached data when API key not set
    return readCacheOrEmpty();
  }

  try {
    // 1. Get the "Uploads" playlist ID for the channel
    const channelRes = await axios.get('https://www.googleapis.com/youtube/v3/channels', {
      params: {
        key,
        id: channelId,
        part: 'contentDetails',
      },
      timeout: 10000,
    });

    const uploadsPlaylistId =
      channelRes.data?.items?.[0]?.contentDetails?.relatedPlaylists?.uploads;

    if (!uploadsPlaylistId) {
      console.warn(`No uploads playlist found for channel ${channelId}`);
      return readCacheOrEmpty();
    }

    // 2. Fetch videos from the uploads playlist
    const videos = await fetchPlaylistVideos(uploadsPlaylistId, maxResults);

    // Normalize to match expected format
    const normalizedAll = videos.map((it) => ({
      id: it.id,
      title: it.title,
      description: it.description,
      publishDate: it.publishDate,
      thumbnail: it.thumbnail,
    }));

    // 3. Update cache
    try {
      await writeCache({
        channelId,
        fetchedAt: new Date().toISOString(),
        items: normalizedAll,
      });
    } catch (e) {
      /* ignore cache errors */
    }

    return normalizedAll;
  } catch (err) {
    console.error('fetchChannelUploads failed:', err?.message);
    return readCacheOrEmpty();
  }
}

// ============================================================================
// PLAYLIST IMPORT - Fetches all playlists from a channel
// ============================================================================

const PLAYLISTS_CACHE_FILE = path.resolve(process.cwd(), 'tmp', 'playlists_cache.json');

/**
 * Fetch all playlists from a YouTube channel
 */
export async function fetchChannelPlaylists(channelId) {
  const key = process.env.YOUTUBE_API_KEY;
  if (!key) {
    return readPlaylistsCacheOrEmpty();
  }

  const url = 'https://www.googleapis.com/youtube/v3/playlists';
  try {
    const res = await axios.get(url, {
      params: {
        key,
        channelId,
        part: 'id,snippet,contentDetails',
        maxResults: 50,
      },
      timeout: 10000,
    });

    const items = (res.data && res.data.items) || [];
    const playlists = items.map((pl) => ({
      id: pl.id,
      title: pl.snippet.title,
      description: pl.snippet.description,
      thumbnail: pl.snippet.thumbnails?.high?.url || pl.snippet.thumbnails?.default?.url,
      videoCount: pl.contentDetails?.itemCount || 0,
      publishedAt: pl.snippet.publishedAt,
    }));

    // Cache playlists
    await writePlaylistsCache({ channelId, fetchedAt: new Date().toISOString(), playlists });
    return playlists;
  } catch (err) {
    console.error('fetchChannelPlaylists failed:', err?.message);
    return readPlaylistsCacheOrEmpty();
  }
}

/**
 * Fetch all videos in a specific playlist
 */
export async function fetchPlaylistVideos(playlistId, maxResults = 50) {
  const key = process.env.YOUTUBE_API_KEY;
  if (!key) return [];

  const url = 'https://www.googleapis.com/youtube/v3/playlistItems';
  let accumulated = [];
  let pageToken = '';

  while (accumulated.length < maxResults) {
    try {
      const res = await axios.get(url, {
        params: {
          key,
          playlistId,
          part: 'snippet,contentDetails',
          maxResults: Math.min(50, maxResults - accumulated.length),
          pageToken: pageToken || undefined,
        },
        timeout: 10000,
      });

      const items = (res.data && res.data.items) || [];
      const videos = items.map((it) => ({
        id: it.contentDetails.videoId,
        title: it.snippet.title,
        description: it.snippet.description,
        publishDate: it.snippet.publishedAt,
        thumbnail: it.snippet.thumbnails?.high?.url || it.snippet.thumbnails?.default?.url,
        playlistId,
        position: it.snippet.position,
      }));

      accumulated = accumulated.concat(videos);
      pageToken = res.data.nextPageToken || '';
      if (!pageToken) break;
    } catch (err) {
      console.error('fetchPlaylistVideos failed:', err?.message);
      break;
    }
  }

  return accumulated;
}

async function readPlaylistsCacheOrEmpty() {
  try {
    const txt = await fs.readFile(PLAYLISTS_CACHE_FILE, 'utf8');
    const json = JSON.parse(txt);
    return json.playlists || [];
  } catch {
    return [];
  }
}

async function writePlaylistsCache(data) {
  try {
    await fs.mkdir(path.dirname(PLAYLISTS_CACHE_FILE), { recursive: true });
    await fs.writeFile(PLAYLISTS_CACHE_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch {
    // noop
  }
}

// ============================================================================
// SERIES DETECTION - Automatically group videos into series
// ============================================================================

/**
 * Known series patterns for auto-detection
 */
const SERIES_PATTERNS = [
  { id: 'superman', name: 'Superman', pattern: /\bsuperman\b/i, category: 'cartoons' },
  { id: 'popeye', name: 'Popeye', pattern: /\bpopeye\b/i, category: 'cartoons' },
  { id: 'betty-boop', name: 'Betty Boop', pattern: /\bbetty\s*boop\b/i, category: 'cartoons' },
  { id: 'casper', name: 'Casper', pattern: /\bcasper\b/i, category: 'cartoons' },
  {
    id: 'felix',
    name: 'Felix the Cat',
    pattern: /\bfelix\s*(the)?\s*cat\b/i,
    category: 'cartoons',
  },
  {
    id: 'tom-jerry',
    name: 'Tom & Jerry',
    pattern: /\btom\s*(and|&|und)\s*jerry\b/i,
    category: 'cartoons',
  },
  {
    id: 'looney-tunes',
    name: 'Looney Tunes',
    pattern: /\b(looney\s*tunes|bugs\s*bunny|daffy|porky|tweety)\b/i,
    category: 'cartoons',
  },
  {
    id: 'woody-woodpecker',
    name: 'Woody Woodpecker',
    pattern: /\bwoody\s*woodpecker\b/i,
    category: 'cartoons',
  },
  {
    id: 'mighty-mouse',
    name: 'Mighty Mouse',
    pattern: /\bmighty\s*mouse\b/i,
    category: 'cartoons',
  },
  {
    id: 'chaplin',
    name: 'Charlie Chaplin',
    pattern: /\b(charlie\s*)?chaplin\b/i,
    category: 'comedy',
  },
  { id: 'keaton', name: 'Buster Keaton', pattern: /\bbuster\s*keaton\b/i, category: 'comedy' },
  {
    id: 'laurel-hardy',
    name: 'Laurel & Hardy',
    pattern: /\blaurel\s*(and|&|und)\s*hardy\b/i,
    category: 'comedy',
  },
  {
    id: 'three-stooges',
    name: 'Three Stooges',
    pattern: /\bthree\s*stooges\b/i,
    category: 'comedy',
  },
  {
    id: 'sherlock',
    name: 'Sherlock Holmes',
    pattern: /\bsherlock\s*holmes\b/i,
    category: 'classic-films',
  },
  { id: 'tarzan', name: 'Tarzan', pattern: /\btarzan\b/i, category: 'classic-films' },
  { id: 'dracula', name: 'Dracula', pattern: /\bdracula\b/i, category: 'classic-films' },
  {
    id: 'frankenstein',
    name: 'Frankenstein',
    pattern: /\bfrankenstein\b/i,
    category: 'classic-films',
  },
];

/**
 * Extract series information from video title
 */
export function extractSeries(title) {
  for (const series of SERIES_PATTERNS) {
    if (series.pattern.test(title)) {
      return {
        seriesId: series.id,
        seriesName: series.name,
        seriesCategory: series.category,
      };
    }
  }
  return null;
}

/**
 * Group videos by series
 */
export function groupVideosBySeries(videos) {
  const seriesMap = new Map();
  const standalone = [];

  for (const video of videos) {
    const series = extractSeries(video.title);
    if (series) {
      if (!seriesMap.has(series.seriesId)) {
        seriesMap.set(series.seriesId, {
          id: series.seriesId,
          name: series.seriesName,
          category: series.seriesCategory,
          videos: [],
        });
      }
      seriesMap.get(series.seriesId).videos.push({
        ...video,
        seriesId: series.seriesId,
      });
    } else {
      standalone.push(video);
    }
  }

  return {
    series: Array.from(seriesMap.values()),
    standalone,
  };
}

async function readCacheOrEmpty() {
  try {
    const txt = await fs.readFile(CACHE_FILE, 'utf8');
    const json = JSON.parse(txt);
    return json.items || [];
  } catch (e) {
    return [];
  }
}

async function writeCache(data) {
  try {
    await fs.mkdir(path.dirname(CACHE_FILE), { recursive: true });
    await fs.writeFile(CACHE_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch (e) {
    // noop
  }
}

export async function getCachedVideos() {
  return readCacheOrEmpty();
}

/**
 * Fetch statistics for a single video via YouTube Data API
 * Returns { viewCount, likeCount, commentCount, duration } or null
 */
export async function getVideoStatistics(videoId) {
  const key = process.env.YOUTUBE_API_KEY;
  if (!key) return null;

  const url = 'https://www.googleapis.com/youtube/v3/videos';
  try {
    const res = await axios.get(url, {
      params: {
        key,
        id: videoId,
        part: 'statistics,contentDetails',
      },
      timeout: 8000,
    });

    const item = (res.data && res.data.items && res.data.items[0]) || null;
    if (!item) return null;

    const stats = item.statistics || {};
    const duration = item.contentDetails ? item.contentDetails.duration : null; // ISO 8601 duration
    return {
      viewCount: parseInt(stats.viewCount || 0),
      likeCount: parseInt(stats.likeCount || 0),
      commentCount: parseInt(stats.commentCount || 0),
      durationIso: duration,
    };
  } catch (err) {
    console.error('getVideoStatistics failed', err?.message || err);
    return null;
  }
}

// ============================================================================
// REMAIKE CHANNEL CONFIGURATION
// ============================================================================

export const REMAIKE_CHANNEL = {
  handle: '@remAIke_IT',
  // Channel ID muss noch eingetragen werden nach erstem API-Call
  channelId: process.env.REMAIKE_CHANNEL_ID || null,
};

// ============================================================================
// DECADE & CATEGORY DEFINITIONS (Server-Side)
// ============================================================================

export const DECADES = [
  { id: '1950s', range: [1950, 1959] },
  { id: '1960s', range: [1960, 1969] },
  { id: '1970s', range: [1970, 1979] },
  { id: '1980s', range: [1980, 1989] },
  { id: '1990s', range: [1990, 1999] },
  { id: '2000s', range: [2000, 2009] },
  { id: '2010s', range: [2010, 2019] },
  { id: '2020s', range: [2020, 2029] },
];

export const CATEGORIES = [
  'computer-history',
  'gaming',
  'internet',
  'software',
  'hardware',
  'companies',
  'media',
];

// ============================================================================
// METADATA EXTRACTION
// ============================================================================

/**
 * Extrahiert Jahr aus Video-Titel
 */
function extractYearFromTitle(title) {
  const patterns = [/\b(19[5-9]\d|20[0-2]\d)\b/, /\[(\d{4})\]/, /\((\d{4})\)/];

  for (const pattern of patterns) {
    const match = title.match(pattern);
    if (match) {
      const year = parseInt(match[1] || match[0]);
      // Allow historical years back to 1900
      if (year >= 1900 && year <= 2030) {
        return year;
      }
    }
  }
  return null;
}

/**
 * Findet das Jahrzehnt für ein Jahr
 */
function getDecadeForYear(year) {
  for (const decade of DECADES) {
    if (year >= decade.range[0] && year <= decade.range[1]) {
      return decade.id;
    }
  }
  return null;
}

/**
 * Extrahiert Kategorie aus Titel/Beschreibung
 */
function extractCategory(title, description = '') {
  const text = `${title} ${description}`.toLowerCase();

  const patterns = {
    // Weihnachten hat höchste Priorität
    christmas:
      /\b(christmas|weihnacht|santa|rudolph|snowflake|holiday|xmas|carol|scrooge|frosty|grinch|nutcracker|winter\s+wonder)\b/i,
    // Cartoons
    cartoons:
      /\b(cartoon|animation|animated|anime|superman|popeye|betty\s*boop|casper|fleischer|disney|silly\s*symphony|looney|tunes|tom\s*(and|&)\s*jerry|woody\s*woodpecker|bugs\s*bunny|daffy|porky|tweety|speedy\s*gonzales|roadrunner|wile\s*e|felix\s*(the)?\s*cat|mighty\s*mouse|heckle|jeckle|gertie|winsor|mccay|little\s*nemo|gulliver|hoppity|bugville)\b/i,
    // Comedy
    comedy:
      /\b(chaplin|keaton|buster|comedy|komödie|lucy|sketch|dinner\s*for\s*one|slapstick|laurel|hardy|three\s*stooges|marx\s*brothers|abbott|costello|harold\s*lloyd|fatty\s*arbuckle|our\s*gang|little\s*rascals)\b/i,
    // Klassische Filme
    'classic-films':
      /\b(film\s*noir|horror|dracula|frankenstein|nosferatu|phantom|metropolis|tarzan|silent|stummfilm|classic|hitchcock|orson\s*welles|citizen\s*kane|casablanca|maltese\s*falcon|double\s*indemnity|sunset\s*blvd|great\s*expectations|oliver\s*twist|david\s*lean|fritz\s*lang|scarlet\s*street|woman\s*in\s*the\s*window|detour|d\.?o\.?a|kiss\s*me\s*deadly|big\s*sleep|key\s*largo|treasure|sierra\s*madre|sherlock|holmes|agatha|christie|western|john\s*wayne|ford)\b/i,
    // Propaganda
    propaganda:
      /\b(propaganda|wwii|ww2|world\s*war|war\s*bonds|civil\s*defense|duck\s*and\s*cover|atomic|nuclear|cold\s*war|why\s*we\s*fight|triumph|will|riefenstahl|capra|government|educational|training\s*film|public\s*information|film\s*bulletin)\b/i,
    // Dokumentationen
    documentaries:
      /\b(documentary|dokumentation|newsreel|wochenschau|historical|history|berlin.*symphony|industrial|educational|nat(ional)?\s*geo|discovery|chronicle|report|bericht|interview|footage)\b/i,
    // Werbung
    commercials:
      /\b(commercial|werbung|coca[- ]?cola|pepsi|advertisement|ad\b|spot|jingle|brand|product|vintage\s*ad|classic\s*ad|retro\s*ad|tv\s*spot|promo|trailer)\b/i,
  };

  for (const [category, pattern] of Object.entries(patterns)) {
    if (pattern.test(text)) {
      return category;
    }
  }

  return null;
}

/**
 * Extrahiert Firmen/Studio-Tags
 */
function extractCompanies(title, description = '') {
  const text = `${title} ${description}`.toLowerCase();
  const companies = [];

  const patterns = {
    // Studios
    disney: /\b(disney|walt\s*disney)\b/i,
    fleischer: /\b(fleischer|max\s*fleischer)\b/i,
    warner: /\b(warner|wb|looney\s*tunes)\b/i,
    mgm: /\b(mgm|metro\s*goldwyn\s*mayer)\b/i,
    paramount: /\b(paramount)\b/i,
    universal: /\b(universal)\b/i,
    fox: /\b(20th\s*century|fox)\b/i,
    columbia: /\b(columbia)\b/i,
    ufa: /\b(ufa)\b/i,

    // Brands
    coca_cola: /\b(coca[- ]?cola|coke)\b/i,
    pepsi: /\b(pepsi)\b/i,
    ford: /\b(ford)\b/i,
    chevrolet: /\b(chevrolet|chevy)\b/i,

    // Legacy Tech (keep for compatibility)
    apple: /\b(apple|macintosh|mac\b|iphone|ipad|ipod)/i,
    microsoft: /\b(microsoft|windows|xbox|ms-dos)/i,
    ibm: /\b(ibm)\b/i,
    commodore: /\b(commodore|c64|amiga)/i,
    atari: /\b(atari)\b/i,
    nintendo: /\b(nintendo|nes|snes|gameboy)/i,
  };

  for (const [company, pattern] of Object.entries(patterns)) {
    if (pattern.test(text)) {
      companies.push(company);
    }
  }

  return companies;
}

/**
 * Extrahiert Tags aus Text
 */
function extractTags(title, description = '') {
  const text = `${title} ${description}`.toLowerCase();
  const tags = [];

  const keywords = [
    // Film & TV
    'film',
    'movie',
    'cinema',
    'kino',
    'cartoon',
    'animation',
    'comedy',
    'drama',
    'horror',
    'thriller',
    'western',
    'sci-fi',
    'fantasy',
    'documentary',
    'doku',
    'newsreel',
    'wochenschau',
    'commercial',
    'werbung',
    'tv',
    'television',
    'series',
    'serie',
    'episode',
    'show',
    'silent',
    'stummfilm',
    'black and white',
    'schwarz-weiß',
    'color',
    'technicolor',
    'hd',
    '4k',
    '8k',
    'remastered',
    'restored',
    'restauriert',
    'upscaled',
    'enhanced',
    'ai',
    'ki',

    // Studios
    'disney',
    'fleischer',
    'warner',
    'mgm',
    'paramount',
    'universal',
    'fox',
    'columbia',
    'united artists',
    'rko',
    'pathe',
    'gaumont',
    'ufa',

    // Legacy Tech
    'apple',
    'microsoft',
    'ibm',
    'commodore',
    'atari',
    'nintendo',
    'sega',
    'sony',
    'computer',
    'robot',
    'space',
    'future',
    'technology',
    'pong',
    'nintendo',
    'nes',
    'snes',
    'gameboy',
    'sony',
    'playstation',
    'sega',
    'genesis',
    'internet',
    'www',
    'web',
    'browser',
    'gaming',
    'videospiel',
    'arcade',
    'ki',
    'ai',
    'vr',
    'retro',
    'vintage',
  ];

  keywords.forEach((keyword) => {
    if (text.includes(keyword)) {
      tags.push(keyword);
    }
  });

  return [...new Set(tags)];
}

/**
 * Enriched Video mit extrahierten Metadaten
 */
export function enrichVideoMetadata(video) {
  const year = extractYearFromTitle(video.title);
  const decade = year ? getDecadeForYear(year) : null;
  const category = extractCategory(video.title, video.description);
  const companies = extractCompanies(video.title, video.description);
  const tags = extractTags(video.title, video.description);
  const series = extractSeries(video.title);

  return {
    ...video,
    year,
    decade,
    category: series?.seriesCategory || category,
    companies,
    tags,
    // Series info
    seriesId: series?.seriesId || null,
    seriesName: series?.seriesName || null,
    // Milestones müssen manuell gepflegt werden
    milestones: [],
    // Sprach-Infos
    language: 'de', // Default für remAIke
    hasGermanDub: true,
  };
}

/**
 * Holt Videos vom remAIke Kanal und reichert sie mit Metadaten an
 */
export async function fetchRemaikeVideos(maxResults = 100) {
  const channelId = REMAIKE_CHANNEL.channelId;

  if (!channelId) {
    console.warn('REMAIKE_CHANNEL_ID not configured, using cache');
    return getCachedVideos();
  }

  const videos = await fetchChannelUploads(channelId, maxResults);

  // Enrich each video with metadata
  return videos.map(enrichVideoMetadata);
}
