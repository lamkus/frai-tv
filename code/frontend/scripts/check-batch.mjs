#!/usr/bin/env node
/**
 * Check OpenAI Batch Status
 *
 * Usage:
 *   node scripts/check-batch.mjs <batch_id>
 *   node scripts/check-batch.mjs batch_abc123
 *
 * When complete, downloads results to public/data/i18n/
 */

import 'dotenv/config';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.error('❌ OPENAI_API_KEY not set');
  process.exit(1);
}

const batchId = process.argv[2];

if (!batchId) {
  console.error('Usage: node check-batch.mjs <batch_id>');
  process.exit(1);
}

async function checkBatch() {
  console.log(`🔍 Checking batch: ${batchId}\n`);

  const response = await fetch(`https://api.openai.com/v1/batches/${batchId}`, {
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
  });

  const batch = await response.json();

  console.log('📊 Batch Status:');
  console.log(`   ID: ${batch.id}`);
  console.log(`   Status: ${batch.status}`);
  console.log(`   Created: ${new Date(batch.created_at * 1000).toISOString()}`);

  if (batch.request_counts) {
    console.log(`   Total: ${batch.request_counts.total}`);
    console.log(`   Completed: ${batch.request_counts.completed}`);
    console.log(`   Failed: ${batch.request_counts.failed}`);
  }

  if (batch.status === 'completed' && batch.output_file_id) {
    console.log('\n✅ Batch completed! Downloading results...');
    await downloadResults(batch.output_file_id);
  } else if (batch.status === 'failed') {
    console.log('\n❌ Batch failed');
    if (batch.errors) {
      console.log('Errors:', JSON.stringify(batch.errors, null, 2));
    }
  } else if (batch.status === 'in_progress') {
    const progress = batch.request_counts
      ? Math.round((batch.request_counts.completed / batch.request_counts.total) * 100)
      : 0;
    console.log(`\n⏳ In progress: ${progress}%`);
    console.log('   Run this command again later to check status.');
  } else {
    console.log(`\n⏳ Status: ${batch.status}`);
  }

  return batch;
}

async function downloadResults(outputFileId) {
  const response = await fetch(`https://api.openai.com/v1/files/${outputFileId}/content`, {
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
  });

  const content = await response.text();
  const lines = content.trim().split('\n');

  // Parse results and group by language
  const resultsByLang = {};

  for (const line of lines) {
    try {
      const result = JSON.parse(line);
      const customId = result.custom_id; // video-{id}-{lang}
      const parts = customId.split('-');
      const lang = parts[parts.length - 1];
      const videoId = parts.slice(1, -1).join('-');

      if (!resultsByLang[lang]) {
        resultsByLang[lang] = {};
      }

      const content = result.response?.body?.choices?.[0]?.message?.content;
      if (content) {
        try {
          const parsed = JSON.parse(content.replace(/```json\n?|```/g, ''));
          resultsByLang[lang][videoId] = parsed;
        } catch (e) {
          console.warn(`   ⚠️ Could not parse result for ${videoId}`);
        }
      }
    } catch (e) {
      console.warn('   ⚠️ Could not parse line');
    }
  }

  // Save translations
  const outputDir = join(__dirname, '../public/data/i18n');
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  for (const [lang, translations] of Object.entries(resultsByLang)) {
    const outputFile = join(outputDir, `videos_${lang}.json`);
    writeFileSync(outputFile, JSON.stringify(translations, null, 2));
    console.log(`   Saved: ${outputFile} (${Object.keys(translations).length} videos)`);
  }

  console.log('\n🎉 Results downloaded successfully!');
}

checkBatch().catch(console.error);
