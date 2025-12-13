import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

import remaikeData from '../src/data/remaikeData.js';

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (!a.startsWith('--')) {
      args._.push(a);
      continue;
    }
    const key = a.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
    } else {
      args[key] = next;
      i += 1;
    }
  }
  return args;
}

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

function findVideoFile(videosDir, ytId) {
  const exts = new Set(['.mp4', '.mkv', '.mov', '.m4v', '.webm']);
  const entries = fs.readdirSync(videosDir, { withFileTypes: true });

  const candidates = entries
    .filter((e) => e.isFile())
    .map((e) => e.name)
    .filter((name) => exts.has(path.extname(name).toLowerCase()))
    .filter((name) => name.includes(ytId));

  if (candidates.length === 0) return null;

  // Prefer exact prefix match
  const exact = candidates.find((n) => n.startsWith(ytId));
  return path.join(videosDir, exact || candidates[0]);
}

function findTitlesFile(docsDir, ytId) {
  // Try: docs/METADATA_*_<ytId>.txt
  const entries = fs.readdirSync(docsDir, { withFileTypes: true });
  const m = entries
    .filter((e) => e.isFile())
    .map((e) => e.name)
    .find((name) => name.startsWith('METADATA_') && name.includes(ytId) && name.endsWith('.txt'));

  return m ? path.join(docsDir, m) : null;
}

function runNode(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [scriptPath, ...args], { stdio: 'inherit' });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) reject(new Error(`Scanner failed with exit code ${code}`));
      else resolve();
    });
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const videosDir = args.videosDir ? path.resolve(args.videosDir) : null;
  if (!videosDir || !fs.existsSync(videosDir)) {
    console.error('Missing/invalid --videosDir <directory-with-local-video-files>');
    process.exit(2);
  }

  const docsDir = path.resolve(args.docsDir || path.join(process.cwd(), '..', '..', 'docs'));
  const outDir = path.resolve(
    args.outDir || path.join(process.cwd(), '..', '..', 'docs', 'youtube', 'chapters')
  );
  fs.mkdirSync(outDir, { recursive: true });

  const allVideos = remaikeData.remaikeVideos || [];
  const onlyCompilations = String(args.all || '') !== 'true' && args.all !== true;
  const targets = onlyCompilations
    ? allVideos.filter((v) => v?.ytId && isCompilation(v))
    : allVideos;

  const scanner = path.resolve(process.cwd(), 'scripts', 'scan-chapters-from-video.mjs');

  let ok = 0;
  let skipped = 0;
  let failed = 0;

  for (const v of targets) {
    if (!v?.ytId) continue;

    const videoFile = findVideoFile(videosDir, v.ytId);
    if (!videoFile) {
      skipped += 1;
      continue;
    }

    const titlesFile = findTitlesFile(docsDir, v.ytId);
    const outFile = path.join(outDir, `${v.ytId}.txt`);

    const cmdArgs = ['--video', videoFile, '--out', outFile, '--prefix', 'CHAPTERS / KAPITEL:'];

    if (titlesFile) {
      cmdArgs.push('--titles', titlesFile);
    }

    // If no titles file, estimate episodes count from duration (best-effort)
    // This is required by the scanner.
    if (!titlesFile) {
      const dur = Number(v.duration || 0);
      const est = Math.max(3, Math.round(dur / 420)); // ~7min segments
      cmdArgs.push('--episodes', String(est));
    }

    console.log('');
    console.log(`== ${v.ytId} :: ${v.title || ''}`);
    console.log(`video: ${videoFile}`);
    if (titlesFile) console.log(`titles: ${titlesFile}`);
    console.log(`out: ${outFile}`);

    try {
      await runNode(scanner, cmdArgs);
      ok += 1;
    } catch (e) {
      failed += 1;
      console.error('FAILED:', e?.message || e);
    }
  }

  console.log('');
  console.log('Batch done.');
  console.log(`OK: ${ok}`);
  console.log(`Skipped (no local file): ${skipped}`);
  console.log(`Failed: ${failed}`);
  console.log('');
  console.log(
    'Next: run `npm run yt:pack` to regenerate docs/youtube/*.md including chapters (if present).'
  );
}

main().catch((e) => {
  console.error('Failed:', e?.message || e);
  process.exit(1);
});
