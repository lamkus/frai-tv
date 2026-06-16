import 'dotenv/config';
import { writeFileSync } from 'fs';
import { join } from 'path';
import { processVideoTitle } from './series-matcher.mjs';

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || process.env.VITE_YOUTUBE_API_KEY;
const ACCESS_TOKEN = process.env.YOUTUBE_ACCESS_TOKEN;
const CHANNEL_ID = process.env.CHANNEL_ID || 'UCVFv6Egpl0LDvigpFbQXNeQ';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

if (!YOUTUBE_API_KEY && !ACCESS_TOKEN) {
  console.error('Neither YOUTUBE_API_KEY nor YOUTUBE_ACCESS_TOKEN set');
  process.exit(1);
}

async function fetchYouTube(url) {
  const headers = {};
  if (ACCESS_TOKEN) {
    headers['Authorization'] = `Bearer ${ACCESS_TOKEN}`;
  } else {
    url += `&key=${YOUTUBE_API_KEY}`;
  }

  const res = await fetch(url, { headers });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`YouTube API error: ${res.status} ${err}`);
  }
  return res.json();
}

async function fetchChannelVideos() {
  const channelUrl = `https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=${CHANNEL_ID}`;
  const channelData = await fetchYouTube(channelUrl);
  const playlistId = channelData.items?.[0]?.contentDetails?.relatedPlaylists?.uploads;
  if (!playlistId) throw new Error('No uploads playlist');

  // Fetch ALL videos with pagination (not just first 50)
  const allVideos = [];
  let pageToken = '';
  let pageCount = 0;
  const MAX_PAGES = 20; // Safety limit: 20 pages * 50 = 1000 videos max

  do {
    const videosUrl = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId=${playlistId}&maxResults=50${
      pageToken ? `&pageToken=${pageToken}` : ''
    }`;
    const videosData = await fetchYouTube(videosUrl);

    if (videosData.items) {
      allVideos.push(...videosData.items);
      console.log(
        `   Fetched page ${++pageCount}: ${videosData.items.length} videos (total: ${
          allVideos.length
        })`
      );
    }

    pageToken = videosData.nextPageToken || '';
  } while (pageToken && pageCount < MAX_PAGES);

  return allVideos;
}

async function analyzeWithAI(video) {
  const title = video.snippet.title;
  const description = video.snippet.description;
  const prompt = `Analyze this YouTube video and categorize it. Return JSON with: category (classic-films|cartoons|documentaries|propaganda|comedy|christmas|commercials), subcategory, tags (array), decade (e.g. "1940s"), year (number).

Title: ${title}
Description: ${description.substring(0, 500)}

Return only valid JSON.`;

  // Try Anthropic Claude first if available
  if (ANTHROPIC_API_KEY) {
    try {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 1024,
          messages: [{ role: 'user', content: prompt }],
        }),
      });
      const data = await res.json();
      const text = data.content?.[0]?.text || '{}';
      return JSON.parse(text.replace(/```json\n?|```/g, ''));
    } catch (e) {
      console.warn('Claude failed:', e.message);
    }
  }

  // Fallback to OpenAI
  if (OPENAI_API_KEY) {
    try {
      const res = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: 'gpt-4o',
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.3,
        }),
      });
      const data = await res.json();
      const text = data.choices?.[0]?.message?.content || '{}';
      return JSON.parse(text.replace(/```json\n?|```/g, ''));
    } catch (e) {
      console.warn('OpenAI failed:', e.message);
    }
  }

  // Fallback: simple heuristic
  return guessCategory(title, description);
}

function guessCategory(title, description) {
  const t = (title + ' ' + description).toLowerCase();
  if (/christmas|weihnacht|santa|xmas/i.test(t))
    return {
      category: 'christmas',
      subcategory: 'movies',
      tags: ['christmas'],
      decade: '1950s',
      year: 1950,
    };
  if (/cartoon|animation|popeye|betty boop|felix/i.test(t))
    return {
      category: 'cartoons',
      subcategory: 'fleischer',
      tags: ['cartoon'],
      decade: '1940s',
      year: 1940,
    };
  if (/chaplin|keaton|comedy|sketch/i.test(t))
    return {
      category: 'comedy',
      subcategory: 'chaplin',
      tags: ['comedy'],
      decade: '1920s',
      year: 1920,
    };
  return {
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['classic'],
    decade: '1920s',
    year: 1920,
  };
}

/**
 * Smart fallback categorization based on title/description keywords
 */
function smartCategorize(title, description) {
  const text = `${title} ${description}`.toLowerCase();

  // Extract year from title
  const yearMatch =
    title.match(/\((\d{4})\)/) ||
    title.match(/[-–—]\s*(19\d{2}|20[0-2]\d)/) ||
    title.match(/\b(19\d{2})\b/);
  const year = yearMatch ? parseInt(yearMatch[1], 10) : null;
  const decade = year ? `${Math.floor(year / 10) * 10}s` : null;

  // Determine category based on keywords
  let category = 'classic-films';
  let subcategory = 'general';
  let tags = ['classic', 'public-domain'];

  // Christmas content
  if (/christmas|santa|rudolph|snowflake|holiday|xmas/i.test(text)) {
    category = 'christmas';
    subcategory = 'christmas-specials';
    tags = ['christmas', 'holiday', 'classic'];
  }
  // Cartoons
  else if (
    /cartoon|animation|animated|fleischer|popeye|casper|betty boop|superman|felix|mel-o-toons|disney/i.test(
      text
    )
  ) {
    category = 'cartoons';
    subcategory = 'classic-cartoons';
    tags = ['cartoon', 'animation', 'classic'];
  }
  // Comedy
  else if (/comedy|chaplin|keaton|buster|dinner for one|lucy|laugh|funny/i.test(text)) {
    category = 'comedy';
    subcategory = 'silent-comedy';
    tags = ['comedy', 'classic'];
  }
  // Horror
  else if (
    /horror|dracula|frankenstein|nosferatu|zombie|caligari|phantom|witch|halloween/i.test(text)
  ) {
    category = 'classic-films';
    subcategory = 'horror';
    tags = ['horror', 'classic', 'halloween'];
  }
  // War/Documentary
  else if (/war|wwii|ww2|propaganda|newsreel|atomic|nazi|pearl harbor|civil defense/i.test(text)) {
    category = 'classic-films';
    subcategory = 'documentary';
    tags = ['documentary', 'historical', 'war'];
  }
  // Sci-Fi
  else if (/sci-fi|science fiction|space|robot|metropolis|prehistoric|planet/i.test(text)) {
    category = 'classic-films';
    subcategory = 'sci-fi';
    tags = ['sci-fi', 'classic'];
  }
  // Commercials
  else if (/coca-cola|commercial|advertisement|ad\b/i.test(text)) {
    category = 'commercials';
    subcategory = 'vintage-ads';
    tags = ['commercial', 'vintage', 'advertising'];
  }
  // Silent films
  else if (/silent|1900s|1910s|1920s|méliès|edison|pathé/i.test(text) || (year && year < 1930)) {
    category = 'classic-films';
    subcategory = 'silent-films';
    tags = ['silent', 'classic', 'early-cinema'];
  }

  return { category, subcategory, tags, year, decade };
}

async function run() {
  console.log('Fetching videos from YouTube...');
  const videos = await fetchChannelVideos();
  console.log(`Found ${videos.length} videos`);

  const enriched = [];
  for (const v of videos) {
    const ytId = v.contentDetails?.videoId || v.snippet?.resourceId?.videoId;
    if (!ytId) continue;

    const title = v.snippet.title;
    const description = v.snippet.description;

    console.log(`Analyzing: ${title}`);

    // Step 1: Series detection & episode matching
    const seriesMatch = processVideoTitle(title, description);

    // Step 2: Categorization - use smart fallback since AI is expensive
    let ai = smartCategorize(title, description);

    if (seriesMatch.seriesId) {
      // Override with series-specific category
      if (seriesMatch.seriesId === 'charlie-chaplin' || seriesMatch.seriesId === 'buster-keaton') {
        ai.category = 'comedy';
        ai.subcategory = 'silent-comedy';
      } else {
        ai.category = 'cartoons';
        ai.subcategory = seriesMatch.seriesId;
      }
      ai.tags = [seriesMatch.seriesId.replace(/-/g, ''), 'classic', 'public-domain'];
      if (seriesMatch.year) {
        ai.year = seriesMatch.year;
        ai.decade = `${Math.floor(seriesMatch.year / 10) * 10}s`;
      }
      console.log(
        `  → Series: ${seriesMatch.seriesName} #${seriesMatch.episodeNumber}/${seriesMatch.episodeTotal}`
      );
    }

    enriched.push({
      id: ytId,
      ytId,
      title: seriesMatch.formattedTitle || title,
      originalTitle: title,
      description: v.snippet.description,
      formattedDescription: seriesMatch.formattedDescription || null,
      thumbnailUrl: v.snippet.thumbnails?.maxresdefault?.url || v.snippet.thumbnails?.high?.url,
      publishDate: v.snippet.publishedAt,
      year: seriesMatch.year || ai.year || new Date(v.snippet.publishedAt).getFullYear(),
      decade: ai.decade,
      category: ai.category,
      subcategory: ai.subcategory,
      tags: ai.tags || [],
      duration: 0,
      // Series metadata
      seriesId: seriesMatch.seriesId,
      seriesName: seriesMatch.seriesName,
      episodeNumber: seriesMatch.episodeNumber,
      episodeTotal: seriesMatch.episodeTotal,
      matchConfidence: seriesMatch.matchConfidence,
    });
  }

  const outPath = join(process.cwd(), 'public', 'data', 'videos.json');
  writeFileSync(outPath, JSON.stringify(enriched, null, 2));
  console.log(`Wrote ${enriched.length} videos to ${outPath}`);

  // Print summary
  const seriesCount = enriched.filter((v) => v.seriesId).length;
  console.log(`\n📊 Summary:`);
  console.log(`   Total videos: ${enriched.length}`);
  console.log(`   Series matched: ${seriesCount}`);
  console.log(`   Standalone: ${enriched.length - seriesCount}`);
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
