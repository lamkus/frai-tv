import fs from 'node:fs';
import path from 'node:path';

import remaikeData from '../src/data/remaikeData.js';

const OUT_DIR = path.resolve(process.cwd(), '..', '..', 'docs', 'youtube');
const CHAPTERS_DIR = path.resolve(OUT_DIR, 'chapters');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function slugify(input) {
  return String(input || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);
}

function hhmmss(totalSeconds) {
  const s = Math.max(0, Math.floor(Number(totalSeconds) || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  return `${m}:${String(sec).padStart(2, '0')}`;
}

function isCompilation(video) {
  const title = (video.title || '').toLowerCase();
  const tags = (video.tags || []).map((t) => String(t).toLowerCase());

  const duration = Number(video.duration || 0);
  const longForm = duration >= 60 * 30; // 30 min+

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

function buildTemplate(video) {
  const ytId = video.ytId;
  const title = video.title || '';
  const year = video.year || '';
  const duration = Number(video.duration || 0);

  const chaptersPath = path.join(CHAPTERS_DIR, `${ytId}.txt`);
  const chaptersTxt = fs.existsSync(chaptersPath)
    ? fs.readFileSync(chaptersPath, 'utf8').trim()
    : '';

  const primaryTag = Array.isArray(video.tags) && video.tags.length ? video.tags[0] : '';
  const tags = Array.isArray(video.tags) ? video.tags : [];

  const safeTitle = title.replace(/\s+/g, ' ').trim();
  const optimizedTitle = `${safeTitle} | 8K Restoration${year ? ` (${year})` : ''}`.trim();

  const descriptionLines = [safeTitle, '', video.description || '', ''];

  if (chaptersTxt) {
    // Use scanned chapters if available
    descriptionLines.push(...chaptersTxt.split(/\r?\n/));
  } else {
    // Fallback template
    descriptionLines.push(
      'CHAPTERS / KAPITEL:',
      '00:00 - Intro',
      '00:00 - Episode 1: [Title]',
      '00:00 - Episode 2: [Title]',
      '00:00 - Episode 3: [Title]',
      '00:00 - Outro'
    );
  }

  descriptionLines.push(
    '',
    `⏱️ Duration: ${hhmmss(duration)}`,
    `▶️ Watch: https://youtu.be/${ytId}`,
    '',
    '🔔 Subscribe: https://www.youtube.com/@remAIke_IT?sub_confirmation=1',
    '',
    '#restoration #classic #8k'
  );

  if (primaryTag) descriptionLines.push(`#${String(primaryTag).replace(/\s+/g, '')}`);

  // Add tags as hashtags (limited / safe)
  const hashTags = tags
    .slice(0, 12)
    .map((t) => String(t).trim())
    .filter(Boolean)
    .map((t) => `#${t.replace(/[^a-zA-Z0-9]+/g, '')}`)
    .filter((t) => t.length > 1);

  const footer = [
    '',
    '---',
    'Notes:',
    '- Replace the 00:00 placeholders with real cut points from the YouTube timeline.',
    '- YouTube requires the first timestamp to be 00:00 to enable chapters.',
  ];

  return {
    optimizedTitle,
    description: descriptionLines.join('\n') + '\n' + hashTags.join(' ') + '\n' + footer.join('\n'),
  };
}

function main() {
  ensureDir(OUT_DIR);

  const videos = remaikeData.remaikeVideos || [];
  const targets = videos.filter((v) => v?.ytId && isCompilation(v));

  const index = [];

  for (const video of targets) {
    const { optimizedTitle, description } = buildTemplate(video);
    const fileBase = `${video.ytId}_${slugify(video.id || video.title || 'video')}.md`;
    const outPath = path.join(OUT_DIR, fileBase);

    const content = [
      `# YouTube Metadata`,
      `- ytId: ${video.ytId}`,
      `- id: ${video.id || ''}`,
      `- duration: ${hhmmss(video.duration || 0)}`,
      '',
      `## Title (Optimized)`,
      optimizedTitle,
      '',
      `## Description (Paste into YouTube)`,
      '```',
      description.trimEnd(),
      '```',
      '',
    ].join('\n');

    fs.writeFileSync(outPath, content, 'utf8');

    index.push({
      ytId: video.ytId,
      title: video.title,
      file: path.relative(path.resolve(process.cwd(), '..', '..'), outPath),
    });
  }

  const indexPath = path.join(OUT_DIR, 'INDEX.md');
  const indexMd = [
    '# YouTube Optimization Pack',
    '',
    'Generated files (one per compilation video):',
    '',
    ...index
      .sort((a, b) => String(a.title).localeCompare(String(b.title)))
      .map((x) => `- ${x.ytId} — ${x.title} → ${x.file.replace(/\\/g, '/')}`),
    '',
  ].join('\n');

  fs.writeFileSync(indexPath, indexMd, 'utf8');

  console.log(`Generated ${index.length} metadata file(s) in: ${OUT_DIR}`);
}

main();
