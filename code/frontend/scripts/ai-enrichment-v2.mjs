import 'dotenv/config';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.warn('⚠️ OPENAI_API_KEY not set. Running in MOCK MODE.');
}

const VIDEOS_PATH = join(process.cwd(), 'public', 'data', 'videos.json');

async function enrichVideos() {
  console.log('🚀 Starting AI Metadata Enrichment v2...');
  if (!OPENAI_API_KEY) console.log('🧪 MOCK MODE: No real API calls will be made.');

  const videos = JSON.parse(readFileSync(VIDEOS_PATH, 'utf8'));
  console.log(`📊 Total videos in database: ${videos.length}`);

  // Filter videos that need enrichment (e.g., missing category or year)
  const pending = videos.filter((v) => !v.category || !v.year || !v.metadata);
  console.log(`⏳ Videos pending enrichment: ${pending.length}`);

  if (pending.length === 0) {
    console.log('✅ All videos are already enriched.');
    return;
  }

  // Process in small batches to avoid rate limits and context window issues
  const BATCH_SIZE = 1;
  const toProcess = pending.slice(0, BATCH_SIZE);

  console.log(`📦 Processing batch of ${toProcess.length} videos...`);

  for (const video of toProcess) {
    try {
      console.log(`🔍 Analyzing: "${video.title}" (${video.ytId})`);
      const enrichment = await analyzeVideo(video);

      if (enrichment) {
        // Update video object
        video.year = enrichment.year || video.year;
        video.decade = enrichment.decade || video.decade;
        video.category = enrichment.category || video.category;
        video.subcategory = enrichment.subcategory || video.subcategory;
        video.tags = [...new Set([...(video.tags || []), ...(enrichment.tags || [])])];

        // Add v2 metadata
        video.metadata = enrichment.metadata;
        video.i18n = enrichment.i18n;
        video.seo = enrichment.seo;

        console.log(
          `   ✅ Success: ${enrichment.category} | ${enrichment.year} | ${enrichment.metadata.color}`
        );
      }
    } catch (error) {
      console.error(`   ❌ Error analyzing ${video.ytId}:`, error.message);
    }
  }

  // Save updated videos.json
  writeFileSync(VIDEOS_PATH, JSON.stringify(videos, null, 2));
  console.log(`\n💾 Updated ${VIDEOS_PATH}`);
  console.log(`🎉 Batch complete. ${toProcess.length} videos processed.`);
}

async function analyzeVideo(video) {
  if (!OPENAI_API_KEY) {
    // Return mock data for testing
    return {
      year: 1940,
      decade: '1940s',
      category: 'cartoons',
      subcategory: 'fleischer-studios',
      tags: ['classic', 'animation', 'public-domain'],
      metadata: {
        director: 'Dave Fleischer',
        cast: ['Jack Mercer', 'Mae Questel'],
        genres: ['Animation', 'Comedy'],
        color: 'B&W',
        rating: 'FSK 0',
        originalLanguage: 'en',
      },
      i18n: {
        de: {
          title: `[MOCK] ${video.title}`,
          description: 'Dies ist eine KI-generierte deutsche Beschreibung.',
        },
        en: {
          title: `[MOCK] ${video.title}`,
          description: 'This is an AI-generated English description.',
        },
        fr: {
          title: `[MOCK] ${video.title}`,
          description: "Ceci est une description française générée par l'IA.",
        },
      },
      seo: {
        metaTitle: `${video.title} | Klassiker auf FRai.TV`,
        metaDescription: `Sehen Sie ${video.title} in bester Qualität auf FRai.TV.`,
        keywords: ['Klassiker', 'Film', 'Archiv'],
      },
    };
  }

  const prompt = `Analyze this YouTube video metadata and provide a deep enrichment.
Title: ${video.title}
Description: ${video.description}

Return a JSON object with the following structure:
{
  "year": number,
  "decade": "19XXs",
  "category": "classic-films|cartoons|documentaries|propaganda|comedy|christmas|commercials",
  "subcategory": "string",
  "tags": ["string"],
  "metadata": {
    "director": "string",
    "cast": ["string"],
    "genres": ["string"],
    "color": "B&W|Color",
    "rating": "FSK 0|FSK 6|FSK 12|FSK 16",
    "originalLanguage": "string"
  },
  "i18n": {
    "de": { "title": "German Title", "description": "German Description" },
    "en": { "title": "English Title", "description": "English Description" },
    "fr": { "title": "French Title", "description": "French Description" }
  },
  "seo": {
    "metaTitle": "SEO Title",
    "metaDescription": "SEO Description",
    "keywords": ["keyword1", "keyword2"]
  }
}

Rules:
1. If information is unknown, use null or empty array.
2. For "color", detect if it's a silent film or vintage B&W.
3. For "i18n", translate the title and description naturally.
4. For "category", use the provided enum values.
5. Return ONLY the JSON object.`;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content:
            'You are a film historian and SEO expert specializing in public domain and classic cinema.',
        },
        { role: 'user', content: prompt },
      ],
      temperature: 0.2,
      response_format: { type: 'json_object' },
    }),
  });

  if (!response.ok) {
    throw new Error(`OpenAI API error: ${response.statusText}`);
  }

  const data = await response.json();
  return JSON.parse(data.choices[0].message.content);
}

enrichVideos().catch(console.error);
