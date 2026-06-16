#!/usr/bin/env node
/**
 * AI Video Translation Script
 *
 * Translates video titles and descriptions using OpenAI API
 * Supports Batch API for 50% cost savings!
 *
 * Usage:
 *   node scripts/translate-videos.mjs --lang=en,es,fr [--batch]
 *   node scripts/translate-videos.mjs --lang=de,en --batch  (50% cheaper!)
 *
 * Environment Variables:
 *   OPENAI_API_KEY - Required for translation
 */

import 'dotenv/config';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.error('❌ OPENAI_API_KEY not set');
  process.exit(1);
}

// Parse CLI arguments
const args = process.argv.slice(2);
const langArg = args.find((a) => a.startsWith('--lang='));
const batchMode = args.includes('--batch');
const languages = langArg ? langArg.replace('--lang=', '').split(',') : ['en'];

console.log('🌐 AI Video Translation');
console.log(`   Languages: ${languages.join(', ')}`);
console.log(`   Mode: ${batchMode ? 'Batch API (-50% cost)' : 'Realtime API'}`);
console.log('');

// Language names for prompts
const languageNames = {
  de: 'German',
  en: 'English',
  es: 'Spanish',
  fr: 'French',
  it: 'Italian',
  pt: 'Portuguese',
  nl: 'Dutch',
  pl: 'Polish',
  ja: 'Japanese',
  zh: 'Chinese',
};

async function loadVideos() {
  const videosPath = join(__dirname, '../public/data/videos.json');
  if (!existsSync(videosPath)) {
    throw new Error('videos.json not found. Run sync-youtube-ai.mjs first!');
  }
  return JSON.parse(readFileSync(videosPath, 'utf-8'));
}

async function translateWithOpenAI(video, targetLang) {
  const langName = languageNames[targetLang] || targetLang;

  const prompt = `Translate this classic film/video metadata to ${langName}. 
Keep the vintage/classic movie tone. Return JSON with: title_${targetLang}, description_${targetLang}

Original Title: ${video.title}
Original Description: ${video.description?.substring(0, 500) || 'No description'}

Return only valid JSON like: {"title_${targetLang}": "...", "description_${targetLang}": "..."}`;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini', // Cost-effective for translation
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3,
    }),
  });

  const data = await response.json();
  const text = data.choices?.[0]?.message?.content || '{}';

  try {
    return JSON.parse(text.replace(/```json\n?|```/g, ''));
  } catch (e) {
    console.warn(`  ⚠️ Parse error for ${video.id}, using fallback`);
    return {
      [`title_${targetLang}`]: video.title,
      [`description_${targetLang}`]: video.description,
    };
  }
}

async function createBatchFile(videos, targetLang) {
  const langName = languageNames[targetLang] || targetLang;
  const lines = [];

  for (const video of videos) {
    const prompt = `Translate this classic film/video metadata to ${langName}. 
Keep the vintage/classic movie tone. Return JSON with: title_${targetLang}, description_${targetLang}

Original Title: ${video.title}
Original Description: ${video.description?.substring(0, 500) || 'No description'}

Return only valid JSON like: {"title_${targetLang}": "...", "description_${targetLang}": "..."}`;

    const request = {
      custom_id: `video-${video.id}-${targetLang}`,
      method: 'POST',
      url: '/v1/chat/completions',
      body: {
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
      },
    };

    lines.push(JSON.stringify(request));
  }

  // Save batch file
  const batchDir = join(__dirname, '../data/batches');
  if (!existsSync(batchDir)) {
    mkdirSync(batchDir, { recursive: true });
  }

  const batchFile = join(batchDir, `translate-${targetLang}-${Date.now()}.jsonl`);
  writeFileSync(batchFile, lines.join('\n'));

  return batchFile;
}

async function submitBatch(batchFile) {
  // Upload file
  const fileContent = readFileSync(batchFile);
  const formData = new FormData();
  formData.append('file', new Blob([fileContent]), 'batch.jsonl');
  formData.append('purpose', 'batch');

  console.log('📤 Uploading batch file...');

  const uploadRes = await fetch('https://api.openai.com/v1/files', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: formData,
  });

  const uploadData = await uploadRes.json();
  const fileId = uploadData.id;

  if (!fileId) {
    throw new Error('Failed to upload batch file: ' + JSON.stringify(uploadData));
  }

  console.log(`   File uploaded: ${fileId}`);

  // Create batch
  console.log('🚀 Creating batch job...');

  const batchRes = await fetch('https://api.openai.com/v1/batches', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      input_file_id: fileId,
      endpoint: '/v1/chat/completions',
      completion_window: '24h',
    }),
  });

  const batchData = await batchRes.json();

  console.log(`   Batch created: ${batchData.id}`);
  console.log(`   Status: ${batchData.status}`);
  console.log('');
  console.log('💡 Batch will complete within 24 hours.');
  console.log(`   Check status: node scripts/check-batch.mjs ${batchData.id}`);

  return batchData;
}

async function translateRealtime(videos, targetLang) {
  console.log(`\n📝 Translating ${videos.length} videos to ${targetLang}...`);

  const translations = {};
  let count = 0;

  for (const video of videos) {
    count++;
    process.stdout.write(`\r   Progress: ${count}/${videos.length}`);

    const result = await translateWithOpenAI(video, targetLang);
    translations[video.id] = result;

    // Rate limiting (60 req/min for gpt-4o-mini)
    await new Promise((r) => setTimeout(r, 200));
  }

  console.log('\n');
  return translations;
}

async function saveTranslations(translations, lang) {
  const outputDir = join(__dirname, '../public/data/i18n');
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  const outputFile = join(outputDir, `videos_${lang}.json`);
  writeFileSync(outputFile, JSON.stringify(translations, null, 2));
  console.log(`✅ Saved translations to ${outputFile}`);
}

async function run() {
  const videos = await loadVideos();
  console.log(`📺 Loaded ${videos.length} videos\n`);

  for (const lang of languages) {
    if (batchMode) {
      console.log(`\n🔄 Creating batch for ${lang}...`);
      const batchFile = await createBatchFile(videos, lang);
      console.log(`   Batch file: ${batchFile}`);

      try {
        await submitBatch(batchFile);
      } catch (e) {
        console.error(`   ❌ Batch submission failed: ${e.message}`);
        console.log('   Falling back to realtime...');
        const translations = await translateRealtime(videos, lang);
        await saveTranslations(translations, lang);
      }
    } else {
      const translations = await translateRealtime(videos, lang);
      await saveTranslations(translations, lang);
    }
  }

  console.log('\n🎉 Translation complete!');
}

run().catch(console.error);
