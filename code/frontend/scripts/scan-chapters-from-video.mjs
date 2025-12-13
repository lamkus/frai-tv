import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

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

function run(cmd, cmdArgs, { captureStderr = false } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, cmdArgs, { stdio: ['ignore', 'ignore', 'pipe'] });

    let stderr = '';
    child.stderr.on('data', (d) => {
      const s = d.toString('utf8');
      if (captureStderr) stderr += s;
    });

    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) {
        const err = new Error(`${cmd} exited with code ${code}`);
        err.stderr = stderr;
        reject(err);
        return;
      }
      resolve({ stderr });
    });
  });
}

function parseBlackdetect(stderr) {
  // lines look like: [blackdetect @ ...] black_start:12.345 black_end:13.210 black_duration:0.865
  const events = [];
  const re =
    /black_start:(\d+(?:\.\d+)?)\s+black_end:(\d+(?:\.\d+)?)\s+black_duration:(\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(stderr))) {
    events.push({
      blackStart: Number(m[1]),
      blackEnd: Number(m[2]),
      duration: Number(m[3]),
    });
  }
  return events;
}

function parseSilencedetect(stderr) {
  // lines look like: silence_start: 123.45
  //                silence_end: 130.12 | silence_duration: 6.67
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
  // Greedy pick boundaries aiming for ~targetGapSec per episode.
  const picks = [0];
  let last = 0;

  while (picks.length < count + 1) {
    const target = last + targetGapSec;

    // Eligible candidates after min gap
    const eligible = candidates.filter((t) => t >= last + minGapSec);
    if (eligible.length === 0) break;

    // Choose candidate closest to target
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
    if (m) {
      out.push(m[1].trim());
    }
  }

  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const videoPath = args.video;
  if (!videoPath) {
    console.error('Missing --video <path-to-video-file>');
    process.exit(2);
  }

  const absVideo = path.resolve(videoPath);
  if (!fs.existsSync(absVideo)) {
    console.error(`Video file not found: ${absVideo}`);
    process.exit(2);
  }

  const titlesPath = args.titles ? path.resolve(args.titles) : null;
  const titles =
    titlesPath && fs.existsSync(titlesPath) ? readTitlesFromMetadataTxt(titlesPath) : [];

  const minGapSec = Number(args.minGapSec || 240); // 4 minutes
  const targetGapSec = Number(args.targetGapSec || 405); // ~6:45

  const outPath = path.resolve(args.out || path.join(process.cwd(), 'chapters.generated.txt'));

  console.log('Scanning video with ffmpeg…');
  console.log(`- video: ${absVideo}`);
  console.log(
    `- titles: ${
      titles.length ? `${titles.length} from ${titlesPath}` : 'none (will output generic Episode N)'
    }`
  );

  // 1) Detect black segments (often between cartoons)
  const black = await run(
    'ffmpeg',
    [
      '-hide_banner',
      '-i',
      absVideo,
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

  // 2) Detect silences (sometimes around transitions)
  const silence = await run(
    'ffmpeg',
    ['-hide_banner', '-i', absVideo, '-af', 'silencedetect=noise=-30dB:d=0.7', '-f', 'null', '-'],
    { captureStderr: true }
  );
  const silenceEnds = parseSilencedetect(silence.stderr);

  // Candidate boundaries: black_end (end of black) + silence_end
  const candidates = uniqSorted([...blackEvents.map((e) => e.blackEnd), ...silenceEnds]).filter(
    (t) => t >= 0
  );

  const episodeCount = Number(args.episodes || (titles.length ? titles.length : 0));
  if (!episodeCount) {
    console.error(
      'Missing --episodes <N> (or provide --titles file that contains N episode lines)'
    );
    console.error(
      'Tip: for Popeye, pass --titles ../../docs/METADATA_POPEYE_MARATHON_3gzbxznJ_PM.txt'
    );
    process.exit(2);
  }

  const boundaries = chooseBoundaries({ candidates, count: episodeCount, minGapSec, targetGapSec });

  const prefix = typeof args.prefix === 'string' ? args.prefix : 'CHAPTERS / KAPITEL:';

  const lines = [];
  lines.push(prefix);
  lines.push('00:00 - Intro & Start');

  for (let i = 0; i < episodeCount; i += 1) {
    const t = boundaries[i + 1] ?? null;
    if (t === null) break;
    const title = titles[i] || `Episode ${i + 1}`;
    lines.push(`${toTimestamp(t)} - ${title}`);
  }

  fs.writeFileSync(outPath, lines.join('\n') + '\n', 'utf8');

  console.log('Done. Generated chapters file:');
  console.log(outPath);
  console.log('');
  console.log('Notes:');
  console.log(
    '- This is fully automatic, but may still be off by a few seconds at some cuts (depends on source).'
  );
  console.log(
    '- If a boundary is wrong, lower/raise --minGapSec or tweak --targetGapSec and rerun.'
  );
}

main().catch((e) => {
  console.error('Failed:', e?.message || e);
  process.exit(1);
});
