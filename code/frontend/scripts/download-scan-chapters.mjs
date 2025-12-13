#!/usr/bin/env node
/**
 * Download YouTube video (low quality), scan for chapter boundaries, output timestamps.
 * Requires: yt-dlp (or youtube-dl) + ffmpeg in PATH.
 *
 * Usage:
 *   node download-scan-chapters.mjs --ytId 3gzbxznJ_PM --titles ../../docs/METADATA_POPEYE_MARATHON_3gzbxznJ_PM.txt
 *   node download-scan-chapters.mjs --ytId 3gzbxznJ_PM --episodes 20
 */

import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

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

function run(cmd, cmdArgs, { captureStderr = false, captureStdout = false } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, cmdArgs, {
      stdio: ['ignore', captureStdout ? 'pipe' : 'inherit', captureStderr ? 'pipe' : 'inherit'],
      shell: process.platform === 'win32',
    });

    let stderr = '';
    let stdout = '';
    if (captureStderr) child.stderr.on('data', (d) => (stderr += d.toString('utf8')));
    if (captureStdout) child.stdout.on('data', (d) => (stdout += d.toString('utf8')));

    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) {
        const err = new Error(`${cmd} exited with code ${code}`);
        err.stderr = stderr;
        err.stdout = stdout;
        reject(err);
        return;
      }
      resolve({ stderr, stdout });
    });
  });
}

function parseBlackdetect(stderr) {
  const events = [];
  const re =
    /black_start:(\d+(?:\.\d+)?)\s+black_end:(\d+(?:\.\d+)?)\s+black_duration:(\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(stderr))) {
    events.push({ blackStart: Number(m[1]), blackEnd: Number(m[2]), duration: Number(m[3]) });
  }
  return events;
}

function parseSilencedetect(stderr) {
  const ends = [];
  const re = /silence_end:\s*(\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(stderr))) {
    ends.push(Number(m[1]));
  }
  return ends;
}

function toTimestamp(totalSeconds) {
  const s = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
}

function uniqSorted(arr) {
  return Array.from(new Set(arr.map((x) => Math.round(x)))).sort((a, b) => a - b);
}

function chooseBoundaries({ candidates, count, minGapSec, targetGapSec }) {
  const picks = [0];
  let last = 0;
  while (picks.length < count + 1) {
    const target = last + targetGapSec;
    const eligible = candidates.filter((t) => t >= last + minGapSec);
    if (eligible.length === 0) break;
    let best = eligible[0];
    let bestDist = Math.abs(best - target);
    for (const t of eligible) {
      const d = Math.abs(t - target);
      if (d < bestDist) {
        best = t;
        bestDist = d;
      }
      if (t > target && d > bestDist) break;
    }
    picks.push(best);
    last = best;
  }
  return picks;
}

function readTitlesFromMetadataTxt(filePath) {
  const txt = fs.readFileSync(filePath, 'utf8');
  const lines = txt.split(/\r?\n/);
  const out = [];
  let inChapterSection = false;
  for (const line of lines) {
    if (
      line.includes('📺 INHALT') ||
      line.includes('INHALT (Kapitel)') ||
      line.includes('KAPITEL')
    ) {
      inChapterSection = true;
      continue;
    }
    if (!inChapterSection) continue;
    if (!line.trim()) continue;
    if (line.includes('[...')) break;
    const m = line.match(/^\s*\d{1,2}:\d{2}(?::\d{2})?\s+(.+?)\s*$/);
    if (!m) continue;
    let title = m[1].trim();
    // Normalize common formatting (bullets / emojis / leading dashes)
    title = title.replace(/^[-•\u2022]+\s*/g, '').trim();

    // Skip intro lines from templates; we always add our own 00:00 intro
    const lower = title.toLowerCase();
    const isIntro =
      lower === 'intro' ||
      lower === 'intro & start' ||
      lower === 'intro and start' ||
      lower.startsWith('intro');
    if (isIntro) continue;

    out.push(title);
  }
  return out;
}

function findYtDlp() {
  const names = ['yt-dlp', 'youtube-dl'];
  for (const n of names) {
    try {
      execSync(`${n} --version`, { stdio: 'ignore' });
      return n;
    } catch {
      // not found
    }
  }
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const ytId = args.ytId;
  if (!ytId) {
    console.error('Missing --ytId <YouTube-video-ID>');
    process.exit(2);
  }

  const ytdlp = findYtDlp();
  if (!ytdlp) {
    console.error(
      'yt-dlp or youtube-dl not found in PATH. Install: https://github.com/yt-dlp/yt-dlp'
    );
    process.exit(2);
  }

  const titlesPath = args.titles ? path.resolve(args.titles) : null;
  const titles =
    titlesPath && fs.existsSync(titlesPath) ? readTitlesFromMetadataTxt(titlesPath) : [];

  const minGapSec = Number(args.minGapSec || 240);
  const targetGapSec = Number(args.targetGapSec || 405);

  const outDir = path.resolve(
    args.outDir || path.join(process.cwd(), '..', '..', 'docs', 'youtube', 'chapters')
  );
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `${ytId}.txt`);

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'yt-scan-'));
  const tempVideo = path.join(tempDir, `${ytId}.mp4`);

  console.log(`Downloading ${ytId} (low quality) for analysis...`);
  console.log(`Tool: ${ytdlp}`);

  try {
    // Download worst quality video+audio (fast)
    await run(ytdlp, [
      '-f',
      'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
      '--merge-output-format',
      'mp4',
      '-o',
      tempVideo,
      '--no-playlist',
      `https://www.youtube.com/watch?v=${ytId}`,
    ]);

    if (!fs.existsSync(tempVideo)) {
      throw new Error('Download failed: temp video not found');
    }

    console.log('Download complete. Scanning for chapter boundaries...');

    // Black detect
    const black = await run(
      'ffmpeg',
      [
        '-hide_banner',
        '-i',
        tempVideo,
        '-vf',
        'blackdetect=d=0.35:pic_th=0.98',
        '-an',
        '-f',
        'null',
        '-',
      ],
      { captureStderr: true }
    );
    const blackEvents = parseBlackdetect(black.stderr);

    // Silence detect
    const silence = await run(
      'ffmpeg',
      [
        '-hide_banner',
        '-i',
        tempVideo,
        '-af',
        'silencedetect=noise=-30dB:d=0.7',
        '-f',
        'null',
        '-',
      ],
      { captureStderr: true }
    );
    const silenceEnds = parseSilencedetect(silence.stderr);

    const candidates = uniqSorted([...blackEvents.map((e) => e.blackEnd), ...silenceEnds]).filter(
      (t) => t >= 0
    );

    const episodeCount = Number(args.episodes || 0) || (titles.length ? titles.length : 0);
    if (!episodeCount) {
      // Auto-estimate from video duration if we downloaded it
      const stats = fs.existsSync(tempVideo) ? fs.statSync(tempVideo) : null;
      // Fallback: estimate ~7 min segments if no episode count provided
      console.warn(
        'No --episodes provided and no titles file found. Estimating from black/silence events...'
      );
      // Use number of black events as rough proxy (often = episode count)
      const autoCount = Math.max(
        3,
        blackEvents.length > 5 ? blackEvents.length : Math.round(candidates.length / 2)
      );
      console.log(
        `Auto-estimated ${autoCount} chapters from ${blackEvents.length} black events, ${silenceEnds.length} silence events.`
      );
      const boundaries = chooseBoundaries({
        candidates,
        count: autoCount,
        minGapSec,
        targetGapSec,
      });

      const lines = [];
      lines.push('CHAPTERS / KAPITEL:');
      lines.push('00:00 - Intro & Start');
      for (let i = 0; i < autoCount; i += 1) {
        const t = boundaries[i + 1] ?? null;
        if (t === null) break;
        const title = titles[i] || `Episode ${i + 1}`;
        lines.push(`${toTimestamp(t)} - ${title}`);
      }

      fs.writeFileSync(outPath, lines.join('\n') + '\n', 'utf8');

      console.log('');
      console.log('Done! Chapter file written:');
      console.log(outPath);
      console.log('');
      console.log('Preview:');
      console.log(lines.slice(0, 15).join('\n'));
      if (lines.length > 15) console.log('...');
      return;
    }

    const boundaries = chooseBoundaries({
      candidates,
      count: episodeCount,
      minGapSec,
      targetGapSec,
    });

    const lines = [];
    lines.push('CHAPTERS / KAPITEL:');
    lines.push('00:00 - Intro & Start');
    for (let i = 0; i < episodeCount; i += 1) {
      const t = boundaries[i + 1] ?? null;
      if (t === null) break;
      const title = titles[i] || `Episode ${i + 1}`;
      lines.push(`${toTimestamp(t)} - ${title}`);
    }

    fs.writeFileSync(outPath, lines.join('\n') + '\n', 'utf8');

    console.log('');
    console.log('Done! Chapter file written:');
    console.log(outPath);
    console.log('');
    console.log('Preview:');
    console.log(lines.slice(0, 15).join('\n'));
    if (lines.length > 15) console.log('...');
  } finally {
    // Cleanup temp
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch {
      // ignore
    }
  }
}

main().catch((e) => {
  console.error('Failed:', e?.message || e);
  process.exit(1);
});
