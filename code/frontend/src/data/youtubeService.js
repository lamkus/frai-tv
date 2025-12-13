/**
 * frai.tv - YouTube API Service
 *
 * Service zum Abrufen von Videos vom YouTube-Kanal
 * Verwendet die YouTube Data API v3
 * Fallback auf Mock-Daten wenn API nicht verfügbar
 */

import { CHANNEL_CONFIG, DECADES, remaikeVideos } from './remaikeData';

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE = 'https://www.googleapis.com/youtube/v3';

// Fallback wenn kein API Key vorhanden
const USE_MOCK_DATA = !import.meta.env.VITE_YOUTUBE_API_KEY;

// Cache für manuell kategorisierte Videos (ytId -> Video)
const manualVideoCache = new Map(remaikeVideos.map((v) => [v.ytId, v]));

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Holt die Channel-ID anhand des Handles (@remAIke_IT)
 */
export async function getChannelId(handle = '@remAIke_IT') {
  if (USE_MOCK_DATA) {
    return CHANNEL_CONFIG.channelId;
  }

  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY;

  try {
    const response = await fetch(
      `${API_BASE}/channels?part=id,snippet&forHandle=${handle}&key=${apiKey}`
    );

    if (!response.ok) {
      throw new Error(`YouTube API Error: ${response.status}`);
    }

    const data = await response.json();

    if (data.items && data.items.length > 0) {
      return data.items[0].id;
    }

    throw new Error('Channel not found');
  } catch (error) {
    console.error('Error fetching channel ID:', error);
    return null;
  }
}

/**
 * Holt alle Videos eines Kanals
 * Mit robustem Fallback auf remaikeVideos wenn API nicht verfügbar
 */
export async function fetchChannelVideos(channelId, maxResults = 50) {
  // Fallback zu lokalen Video-Daten wenn kein API Key
  if (USE_MOCK_DATA) {
    console.log('YouTube API: Using local video data (no API key configured)');
    return remaikeVideos.map(enrichVideoMetadata);
  }

  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY;

  try {
    // Erst die Upload-Playlist ID holen
    const channelResponse = await fetch(
      `${API_BASE}/channels?part=contentDetails,snippet&id=${channelId}&key=${apiKey}`
    );

    if (!channelResponse.ok) {
      const errorText = await channelResponse.text();
      console.error('YouTube Channel API Error:', channelResponse.status, errorText);
      throw new Error(`YouTube API Error: ${channelResponse.status}`);
    }

    const channelData = await channelResponse.json();

    // Wenn kein Channel gefunden, versuche über Handle
    if (!channelData.items || channelData.items.length === 0) {
      console.warn('Channel not found by ID, trying search...');
      return await fetchVideosViaSearch(CHANNEL_CONFIG.channelHandle, maxResults);
    }

    const uploadsPlaylistId = channelData.items?.[0]?.contentDetails?.relatedPlaylists?.uploads;

    if (!uploadsPlaylistId) {
      console.warn('Uploads playlist not found, trying search API...');
      return await fetchVideosViaSearch(channelId, maxResults);
    }

    // Dann die Videos aus der Playlist holen
    const videos = [];
    let pageToken = '';

    while (videos.length < maxResults) {
      const playlistResponse = await fetch(
        `${API_BASE}/playlistItems?part=snippet,contentDetails&playlistId=${uploadsPlaylistId}&maxResults=50&pageToken=${pageToken}&key=${apiKey}`
      );

      if (!playlistResponse.ok) {
        throw new Error(`YouTube API Error: ${playlistResponse.status}`);
      }

      const playlistData = await playlistResponse.json();

      for (const item of playlistData.items || []) {
        videos.push(transformYouTubeVideo(item));
        if (videos.length >= maxResults) break;
      }

      pageToken = playlistData.nextPageToken || '';
      if (!pageToken) break;
    }

    // Statistics für alle Videos in einem Batch laden
    const videosWithStats = await enrichVideosWithStats(videos, apiKey);
    return videosWithStats;
  } catch (error) {
    console.error('Error fetching channel videos:', error);
    // Fallback auf Search API
    return await fetchVideosViaSearch(channelId, maxResults);
  }
}

/**
 * Enriches videos with statistics (viewCount, likeCount, etc.) via batch API call
 */
async function enrichVideosWithStats(videos, apiKey) {
  if (!videos.length) return videos;

  try {
    // Batch video IDs (max 50 per request)
    const videoIds = videos.map((v) => v.ytId).filter(Boolean);
    if (!videoIds.length) return videos;

    const response = await fetch(
      `${API_BASE}/videos?part=statistics,contentDetails&id=${videoIds.join(',')}&key=${apiKey}`
    );

    if (!response.ok) {
      console.warn('Stats API failed, returning videos without stats');
      return videos;
    }

    const data = await response.json();
    const statsMap = new Map();

    for (const item of data.items || []) {
      statsMap.set(item.id, {
        viewCount: parseInt(item.statistics?.viewCount || 0),
        likeCount: parseInt(item.statistics?.likeCount || 0),
        commentCount: parseInt(item.statistics?.commentCount || 0),
        duration: parseDuration(item.contentDetails?.duration),
      });
    }

    // Merge stats into videos
    return videos.map((video) => {
      const stats = statsMap.get(video.ytId);
      if (stats) {
        return { ...video, ...stats };
      }
      return video;
    });
  } catch (error) {
    console.error('Error enriching videos with stats:', error);
    return videos;
  }
}

/**
 * Fallback: Videos über Search API suchen (intern)
 */
async function fetchVideosViaSearch(channelIdOrHandle, maxResults = 50) {
  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY;
  if (!apiKey) return [];

  try {
    const searchResponse = await fetch(
      `${API_BASE}/search?part=snippet&channelId=${channelIdOrHandle}&type=video&maxResults=${Math.min(
        maxResults,
        50
      )}&order=date&key=${apiKey}`
    );

    if (!searchResponse.ok) {
      console.error('YouTube Search API failed:', searchResponse.status);
      return [];
    }

    const searchData = await searchResponse.json();

    return (searchData.items || []).map((item) => ({
      id: item.id.videoId,
      ytId: item.id.videoId,
      title: item.snippet.title,
      description: item.snippet.description,
      thumbnail:
        item.snippet.thumbnails?.maxres?.url ||
        item.snippet.thumbnails?.high?.url ||
        item.snippet.thumbnails?.medium?.url ||
        `https://img.youtube.com/vi/${item.id.videoId}/hqdefault.jpg`,
      publishedAt: item.snippet.publishedAt,
      channelTitle: item.snippet.channelTitle,
      channelId: item.snippet.channelId,
    }));
  } catch (error) {
    console.error('Search API fallback failed:', error);
    return [];
  }
}

/**
 * Holt Details zu einem Video
 */
export async function fetchVideoDetails(videoId) {
  if (USE_MOCK_DATA) {
    return null;
  }

  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY;

  try {
    const response = await fetch(
      `${API_BASE}/videos?part=snippet,contentDetails,statistics&id=${videoId}&key=${apiKey}`
    );

    if (!response.ok) {
      throw new Error(`YouTube API Error: ${response.status}`);
    }

    const data = await response.json();

    if (data.items && data.items.length > 0) {
      return transformYouTubeVideoDetails(data.items[0]);
    }

    return null;
  } catch (error) {
    console.error('Error fetching video details:', error);
    return null;
  }
}

/**
 * Holt die neuesten N Videos sortiert nach Veröffentlichungsdatum
 */
export async function getLatestVideos(count = 3) {
  const channelId = CHANNEL_CONFIG.channelId;
  const videos = await fetchChannelVideos(channelId, 50);

  if (!videos || videos.length === 0) {
    // Fallback zu Mock-Daten falls keine API-Videos
    return remaikeVideos.slice(0, count).map(enrichVideoMetadata);
  }

  // Sortiere nach Datum (neueste zuerst)
  const sorted = videos.sort(
    (a, b) => new Date(b.publishDate || b.publishedAt) - new Date(a.publishDate || a.publishedAt)
  );

  return sorted.slice(0, count).map(enrichVideoMetadata);
}

/**
 * Sucht nach Videos auf dem Kanal
 */
export async function searchChannelVideos(channelId, query, maxResults = 25) {
  if (USE_MOCK_DATA) {
    return [];
  }

  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY;

  try {
    const response = await fetch(
      `${API_BASE}/search?part=snippet&channelId=${channelId}&q=${encodeURIComponent(
        query
      )}&type=video&maxResults=${maxResults}&key=${apiKey}`
    );

    if (!response.ok) {
      throw new Error(`YouTube API Error: ${response.status}`);
    }

    const data = await response.json();

    return (data.items || []).map(transformYouTubeSearchResult);
  } catch (error) {
    console.error('Error searching videos:', error);
    return [];
  }
}

// ============================================================================
// DATA TRANSFORMATION
// ============================================================================

/**
 * Transformiert YouTube API Playlist Item in unser Format
 */
function transformYouTubeVideo(item) {
  const snippet = item.snippet;
  const videoId = item.contentDetails?.videoId || item.id?.videoId;

  // Versuche Metadaten aus dem Titel zu extrahieren
  const metadata = extractMetadataFromTitle(snippet.title, snippet.description);

  return {
    id: videoId,
    ytId: videoId,
    title: snippet.title,
    description: snippet.description,
    thumbnailUrl: getBestThumbnail(snippet.thumbnails),
    publishDate: snippet.publishedAt,
    channelId: snippet.channelId,
    channelName: snippet.channelTitle,

    // Extrahierte Metadaten
    ...metadata,

    // Platzhalter für manuelle Kategorisierung
    category: metadata.category || null,
    subcategory: null,
    decade: metadata.decade || null,
    year: metadata.year || null,
    milestones: [],
    tags: extractTags(snippet.title, snippet.description),
  };
}

/**
 * Transformiert YouTube API Video Details
 */
function transformYouTubeVideoDetails(item) {
  const snippet = item.snippet;
  const contentDetails = item.contentDetails;
  const statistics = item.statistics;

  return {
    id: item.id,
    ytId: item.id,
    title: snippet.title,
    description: snippet.description,
    thumbnailUrl: getBestThumbnail(snippet.thumbnails),
    publishDate: snippet.publishedAt,
    channelId: snippet.channelId,
    channelName: snippet.channelTitle,

    // Zusätzliche Details
    duration: parseDuration(contentDetails.duration),
    viewCount: parseInt(statistics.viewCount || 0),
    likeCount: parseInt(statistics.likeCount || 0),
    commentCount: parseInt(statistics.commentCount || 0),

    // Tags aus YouTube
    youtubeTags: snippet.tags || [],

    // Extrahierte Metadaten
    ...extractMetadataFromTitle(snippet.title, snippet.description),
    tags: extractTags(snippet.title, snippet.description),
  };
}

/**
 * Transformiert YouTube API Search Result
 */
function transformYouTubeSearchResult(item) {
  return transformYouTubeVideo({
    ...item,
    contentDetails: { videoId: item.id.videoId },
  });
}

// ============================================================================
// METADATA EXTRACTION
// ============================================================================

/**
 * Extrahiert Metadaten (Jahr, Kategorie, etc.) aus dem Videotitel und optional Description
 *
 * Beispiel-Titel-Formate:
 * - "Apple Macintosh 1984 - Die Revolution"
 * - "[1995] Windows 95 Launch"
 * - "Commodore 64 (1982) - Der Heimcomputer"
 */
function extractMetadataFromTitle(title, description = '') {
  const metadata = {
    year: null,
    decade: null,
    category: null,
    extractedCompanies: [],
  };

  // Jahr-Patterns
  // Accept a wider range of years so Timeline can include older films (e.g. 1930s)
  const yearPatterns = [
    /\b(19\d{2}|20[0-2]\d)\b/, // 1900-2029
    /\[(\d{4})\]/, // [1984]
    /\((\d{4})\)/, // (1984)
  ];

  for (const pattern of yearPatterns) {
    const match = title.match(pattern);
    if (match) {
      const year = parseInt(match[1] || match[0]);
      // Accept historical years back to 1900 because we host classic films
      if (year >= 1900 && year <= 2030) {
        metadata.year = year;
        metadata.decade = getDecadeForYear(year);
        break;
      }
    }
  }

  // Firmen-Detection
  const companyPatterns = {
    apple: /\b(apple|macintosh|mac\b|iphone|ipad|ipod)/i,
    microsoft: /\b(microsoft|windows|xbox|ms-dos)/i,
    ibm: /\b(ibm)\b/i,
    google: /\b(google|android|youtube|chrome)/i,
    atari: /\b(atari)\b/i,
    commodore: /\b(commodore|c64|amiga)/i,
    nintendo: /\b(nintendo|nes|snes|gameboy)/i,
    sony: /\b(sony|playstation|ps[1-5])/i,
    sega: /\b(sega|genesis|dreamcast)/i,
  };

  for (const [company, pattern] of Object.entries(companyPatterns)) {
    if (pattern.test(title)) {
      metadata.extractedCompanies.push(company);
    }
  }

  // Kategorie-Detection für klassische Filme & Cartoons
  const categoryPatterns = {
    // Weihnachten hat höchste Priorität
    christmas:
      /\b(christmas|weihnacht|santa|rudolph|snowflake|holiday|xmas|carol|scrooge|frosty|grinch|nutcracker|winter\s+wonder)\b/i,
    // Cartoons - erweitert
    cartoons:
      /\b(cartoon|animation|animated|anime|superman|popeye|betty\s*boop|casper|fleischer|disney|silly\s*symphony|looney|tunes|tom\s*(and|&)\s*jerry|woody\s*woodpecker|bugs\s*bunny|daffy|porky|tweety|speedy\s*gonzales|roadrunner|wile\s*e|felix\s*(the)?\s*cat|mighty\s*mouse|heckle|jeckle|gertie|winsor|mccay|little\s*nemo|gulliver|hoppity|bugville)\b/i,
    // Comedy - erweitert
    comedy:
      /\b(chaplin|keaton|buster|comedy|komödie|lucy|sketch|dinner\s*for\s*one|slapstick|laurel|hardy|three\s*stooges|marx\s*brothers|abbott|costello|harold\s*lloyd|fatty\s*arbuckle|our\s*gang|little\s*rascals)\b/i,
    // Klassische Filme - erweitert
    'classic-films':
      /\b(film\s*noir|horror|dracula|frankenstein|nosferatu|phantom|metropolis|tarzan|silent|stummfilm|classic|hitchcock|orson\s*welles|citizen\s*kane|casablanca|maltese\s*falcon|double\s*indemnity|sunset\s*blvd|great\s*expectations|oliver\s*twist|david\s*lean|fritz\s*lang|scarlet\s*street|woman\s*in\s*the\s*window|detour|d\.?o\.?a|kiss\s*me\s*deadly|big\s*sleep|key\s*largo|treasure|sierra\s*madre|sherlock|holmes|agatha|christie|western|john\s*wayne|ford)\b/i,
    // Propaganda/Zeitdokumente - erweitert
    propaganda:
      /\b(propaganda|wwii|ww2|world\s*war|war\s*bonds|civil\s*defense|duck\s*and\s*cover|atomic|nuclear|cold\s*war|why\s*we\s*fight|triumph|will|riefenstahl|capra|government|educational|training\s*film|public\s*information|film\s*bulletin)\b/i,
    // Dokumentationen
    documentaries:
      /\b(documentary|dokumentation|newsreel|wochenschau|historical|history|berlin.*symphony|industrial|educational|nat(ional)?\s*geo|discovery|chronicle|report|bericht|interview|footage)\b/i,
    // Werbung - erweitert
    commercials:
      /\b(commercial|werbung|coca[- ]?cola|pepsi|advertisement|ad\b|spot|jingle|brand|product|vintage\s*ad|classic\s*ad|retro\s*ad|tv\s*spot|promo|trailer)\b/i,
  };

  for (const [category, pattern] of Object.entries(categoryPatterns)) {
    if (pattern.test(title)) {
      metadata.category = category;
      break;
    }
  }

  // Fallback: Wenn kein Match, versuche Description zu parsen
  if (!metadata.category && description) {
    for (const [category, pattern] of Object.entries(categoryPatterns)) {
      if (pattern.test(description)) {
        metadata.category = category;
        break;
      }
    }
  }

  return metadata;
}

/**
 * Extrahiert Tags aus Titel und Beschreibung
 */
function extractTags(title, description = '') {
  const text = `${title} ${description}`.toLowerCase();
  const tags = new Set();

  // Bekannte Tech-Keywords & Film-Keywords
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

    // Studios & Brands
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
    'coca-cola',
    'pepsi',
    'ford',
    'chevrolet',
    'dodge',
    'gm',
    'general motors',
    'pan am',
    'twa',
    'nasa',

    // Tech (Legacy)
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
  ];

  keywords.forEach((keyword) => {
    if (text.includes(keyword)) {
      tags.add(keyword);
    }
  });

  // Jahre als Tags
  const yearMatch = text.match(/\b(19[5-9]\d|20[0-2]\d)\b/g);
  if (yearMatch) {
    yearMatch.forEach((year) => tags.add(year));
  }

  return Array.from(tags);
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
 * Wählt das beste verfügbare Thumbnail
 */
function getBestThumbnail(thumbnails) {
  if (!thumbnails) return null;

  const priority = ['maxres', 'standard', 'high', 'medium', 'default'];

  for (const quality of priority) {
    if (thumbnails[quality]?.url) {
      return thumbnails[quality].url;
    }
  }

  return null;
}

/**
 * Parst ISO 8601 Duration (PT1H30M45S) zu Sekunden
 */
function parseDuration(duration) {
  if (!duration) return 0;

  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);

  if (!match) return 0;

  const hours = parseInt(match[1] || 0);
  const minutes = parseInt(match[2] || 0);
  const seconds = parseInt(match[3] || 0);

  return hours * 3600 + minutes * 60 + seconds;
}

/**
 * Reichert ein Video mit zusätzlichen Metadaten an
 * 1. Prüft ob das Video in remaikeVideos manuell kategorisiert ist
 * 2. Falls nicht, extrahiert Metadaten aus dem Titel
 */
export function enrichVideoMetadata(video) {
  if (!video) return video;

  // Versuche manuell kategorisiertes Video zu finden
  const manualMatch = findManualVideoMatch(video.ytId);

  if (manualMatch) {
    // Verwende manuelle Kategorisierung, aber behalte API-Daten (stats, etc.)
    return {
      ...video,
      ...manualMatch,
      // API-Daten haben Vorrang bei dynamischen Werten
      viewCount: video.viewCount || manualMatch.viewCount,
      likeCount: video.likeCount || manualMatch.likeCount,
      duration: video.duration || manualMatch.duration,
      thumbnailUrl:
        video.thumbnailUrl ||
        manualMatch.thumbnailUrl ||
        (video.ytId ? `https://img.youtube.com/vi/${video.ytId}/maxresdefault.jpg` : null),
    };
  }

  // Kein manuelles Match - extrahiere aus Titel
  const extracted = extractMetadataFromTitle(video.title || '', video.description || '');
  const category = video.category || extracted.category || 'classic-films';

  return {
    ...video,
    year: video.year || extracted.year,
    decade: video.decade || extracted.decade,
    category: category,
    tags: video.tags || extracted.tags || [],
    extractedCompanies: video.extractedCompanies || extracted.extractedCompanies || [],
    thumbnailUrl:
      video.thumbnailUrl ||
      video.thumbnail ||
      (video.ytId ? `https://img.youtube.com/vi/${video.ytId}/maxresdefault.jpg` : null),
  };
}

/**
 * Findet ein manuell kategorisiertes Video anhand der YouTube ID
 */
function findManualVideoMatch(ytId) {
  if (!ytId) return null;
  return manualVideoCache.get(ytId) || null;
}

// ============================================================================
// YOUTUBE SHORTS
// ============================================================================

/**
 * Holt YouTube Shorts vom Kanal
 * Verwendet videoDuration=short Filter der YouTube API
 */
export async function fetchYouTubeShorts(channelId, maxResults = 20) {
  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY;

  if (!apiKey) {
    console.warn('No YouTube API key - cannot fetch Shorts');
    return [];
  }

  try {
    // YouTube API videoDuration=short findet Videos unter 4 Minuten
    const searchResponse = await fetch(
      `${API_BASE}/search?part=snippet&channelId=${channelId}&type=video&videoDuration=short&maxResults=${maxResults}&order=date&key=${apiKey}`
    );

    if (!searchResponse.ok) {
      throw new Error(`YouTube API Error: ${searchResponse.status}`);
    }

    const searchData = await searchResponse.json();
    const videoIds = (searchData.items || []).map((item) => item.id.videoId).filter(Boolean);

    if (videoIds.length === 0) {
      console.log('No short videos found');
      return [];
    }

    // Details inkl. Duration und Stats holen
    const detailsResponse = await fetch(
      `${API_BASE}/videos?part=snippet,contentDetails,statistics&id=${videoIds.join(
        ','
      )}&key=${apiKey}`
    );

    if (!detailsResponse.ok) {
      throw new Error(`YouTube API Error: ${detailsResponse.status}`);
    }

    const detailsData = await detailsResponse.json();

    const shorts = (detailsData.items || []).map((item) => ({
      id: item.id,
      ytId: item.id,
      title: item.snippet.title,
      description: item.snippet.description,
      thumbnailUrl: getBestThumbnail(item.snippet.thumbnails),
      publishDate: item.snippet.publishedAt,
      channelName: item.snippet.channelTitle,
      duration: parseDuration(item.contentDetails?.duration),
      viewCount: parseInt(item.statistics?.viewCount || 0),
      likeCount: parseInt(item.statistics?.likeCount || 0),
      commentCount: parseInt(item.statistics?.commentCount || 0),
      isShort: true,
    }));

    console.log(`Found ${shorts.length} YouTube Shorts`);
    return shorts;
  } catch (error) {
    console.error('Error fetching YouTube Shorts:', error);
    return [];
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export const youtubeService = {
  getChannelId,
  fetchChannelVideos,
  fetchVideoDetails,
  getLatestVideos,
  searchChannelVideos,
  fetchYouTubeShorts,
  extractMetadataFromTitle,
  extractTags,
  enrichVideoMetadata,
};

export default youtubeService;
