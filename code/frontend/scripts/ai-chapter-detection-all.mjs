#!/usr/bin/env node
/**
 * AI Chapter Detection - Batch Process All Compilations
 *
 * Runs ai-chapter-detection.mjs on all compilation videos from remaikeData.js
 *
 * Usage:
 *   node ai-chapter-detection-all.mjs
 *   node ai-chapter-detection-all.mjs --apiKey sk-xxx
 *   OPENAI_API_KEY=sk-xxx node ai-chapter-detection-all.mjs
 */

import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import video data
const dataPath = path.join(__dirname, '..', 'src', 'data', 'remaikeData.js');

async function loadCompilations() {
  const module = await import(dataPath);
  const videos = module.videos || [];

  // Filter for compilations (marathon, collection, fest, etc.)
  return videos.filter((v) => {
    if (!v.ytId) return false;
    const title = (v.title || '').toLowerCase();
    const tags = (v.tags || []).join(' ').toLowerCase();
    return (
      title.includes('marathon') ||
      title.includes('collection') ||
      title.includes('fest') ||
      title.includes('compilation') ||
      tags.includes('compilation') ||
      (v.duration && v.duration > 3600) // > 1 hour likely compilation
    );
  });
}

function runScript(ytId, apiKey) {
  return new Promise((resolve, reject) => {
    const args = ['scripts/ai-chapter-detection.mjs', '--ytId', ytId];
    if (apiKey) args.push('--apiKey', apiKey);

    const child = spawn('node', args, {
      cwd: path.join(__dirname, '..'),
      stdio: 'inherit',
      shell: process.platform === 'win32',
    });

    child.on('error', reject);
    child.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Exit code ${code}`));
    });
  });
}

async function main() {
  const apiKey =
    process.argv.find((a) => a.startsWith('--apiKey='))?.split('=')[1] ||
    process.argv[process.argv.indexOf('--apiKey') + 1] ||
    process.env.OPENAI_API_KEY;

  console.log('\n🤖 AI Chapter Detection - Batch Mode');
  console.log('═'.repeat(50));

  if (apiKey) {
    console.log('✓ OpenAI API key detected - AI analysis enabled\n');
  } else {
    console.log('⚠ No API key - running in screenshot-only mode\n');
  }

  const compilations = await loadCompilations();
  console.log(`Found ${compilations.length} compilation videos:\n`);

  for (const v of compilations) {
    console.log(`  • ${v.ytId} - ${v.title}`);
  }
  console.log('');

  let success = 0;
  let failed = 0;

  for (let i = 0; i < compilations.length; i++) {
    const v = compilations[i];
    console.log(`\n${'─'.repeat(50)}`);
    console.log(`Processing ${i + 1}/${compilations.length}: ${v.title}`);
    console.log('─'.repeat(50));

    try {
      await runScript(v.ytId, apiKey);
      success++;
    } catch (e) {
      console.error(`❌ Failed: ${e.message}`);
      failed++;
    }
  }

  console.log('\n' + '═'.repeat(50));
  console.log('📊 BATCH COMPLETE');
  console.log('═'.repeat(50));
  console.log(`✓ Success: ${success}`);
  console.log(`✗ Failed: ${failed}`);
  console.log(`Total: ${compilations.length}`);
}

main().catch((e) => {
  console.error('Fatal:', e);
  process.exit(1);
});
