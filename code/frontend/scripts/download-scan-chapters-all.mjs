#!/usr/bin/env node
/**
 * Batch download + scan chapters for ALL compilation videos on the channel.
 * Downloads each video in low quality, scans, writes chapter file, deletes temp.
 *
 * Requires: yt-dlp (or youtube-dl) + ffmpeg in PATH.
 *
 * Usage:
 *   node download-scan-chapters-all.mjs
 */

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

import remaikeData from '../src/data/remaikeData.js';

function isCompilation(video) {
  const title = (video.title || '').toLowerCase();
  const tags = (video.tags || []).map((t) => String(t).toLowerCase());
  const duration = Number(video.duration || 0);
  const longForm = duration >= 60 * 30; // 30min+

  const keyword =
    title.includes('marathon') ||
    title.includes('collection') ||
    title.includes('fest') ||
    title.includes('alle') ||
    tags.includes('marathon') ||
    tags.includes('sammlung') ||
    tags.includes('collection');

  return longForm && keyword;
}

function findTitlesFile(docsDir, ytId) {
  try {
    const entries = fs.readdirSync(docsDir, { withFileTypes: true });
    const m = entries
      .filter((e) => e.isFile())
      .map((e) => e.name)
      .find((name) => name.startsWith('METADATA_') && name.includes(ytId) && name.endsWith('.txt'));
    return m ? path.join(docsDir, m) : null;
  } catch {
    return null;
  }
}

function runNode(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [scriptPath, ...args], { stdio: 'inherit' });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) reject(new Error(`Script failed with exit code ${code}`));
      else resolve();
    });
  });
}

async function main() {
  const allVideos = remaikeData.remaikeVideos || [];
  const compilations = allVideos.filter((v) => v?.ytId && isCompilation(v));

  const docsDir = path.resolve(process.cwd(), '..', '..', 'docs');
  const scanner = path.resolve(process.cwd(), 'scripts', 'download-scan-chapters.mjs');

  console.log(`Found ${compilations.length} compilation video(s) to process.\n`);

  let ok = 0;
  let failed = 0;

  for (const v of compilations) {
    console.log('');
    console.log('='.repeat(60));
    console.log(`Processing: ${v.ytId} — ${v.title || ''}`);
    console.log('='.repeat(60));

    const titlesFile = findTitlesFile(docsDir, v.ytId);
    const cmdArgs = ['--ytId', v.ytId];

    if (titlesFile) {
      cmdArgs.push('--titles', titlesFile);
    } else {
      // Estimate episodes from duration (~7 min each)
      const dur = Number(v.duration || 0);
      const est = Math.max(3, Math.round(dur / 420));
      cmdArgs.push('--episodes', String(est));
    }

    try {
      await runNode(scanner, cmdArgs);
      ok += 1;
    } catch (e) {
      failed += 1;
      console.error('FAILED:', e?.message || e);
    }
  }

  console.log('');
  console.log('='.repeat(60));
  console.log('BATCH COMPLETE');
  console.log(`OK: ${ok}`);
  console.log(`Failed: ${failed}`);
  console.log('');
  console.log(
    'Next: run `npm run yt:pack` to regenerate docs/youtube/*.md with chapters included.'
  );
}

main().catch((e) => {
  console.error('Failed:', e?.message || e);
  process.exit(1);
});
