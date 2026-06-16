/**
 * generate-sitemap.mjs — Build-time sitemap generator for frai.tv
 * Generates sitemap.xml with all pages + 318 video entries for Google
 * Run: node scripts/generate-sitemap.mjs (auto-runs in vite build via plugin)
 */
import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DOMAIN = 'https://frai.tv';
const TODAY = new Date().toISOString().slice(0, 10);

// ─── Static pages ───────────────────────────────────────────
const pages = [
  { path: '/', priority: '1.0', freq: 'daily' },
  { path: '/projector', priority: '0.9', freq: 'weekly' },
  { path: '/landing', priority: '0.8', freq: 'monthly' },
  { path: '/browse', priority: '0.8', freq: 'weekly' },
  { path: '/catalog', priority: '0.8', freq: 'weekly' },
  { path: '/timeline', priority: '0.7', freq: 'weekly' },
  { path: '/series', priority: '0.7', freq: 'weekly' },
  { path: '/search', priority: '0.6', freq: 'weekly' },
  { path: '/roulette', priority: '0.6', freq: 'monthly' },
  { path: '/wheel', priority: '0.5', freq: 'monthly' },
  { path: '/shorts', priority: '0.5', freq: 'weekly' },
  { path: '/stats', priority: '0.4', freq: 'monthly' },
  { path: '/impressum', priority: '0.3', freq: 'yearly' },
  { path: '/datenschutz', priority: '0.3', freq: 'yearly' },
];

// ─── Video data (inline from projectorData — top 100 for sitemap) ──
// We dynamically import the data module
async function loadVideos() {
  try {
    const mod = await import('../src/data/projectorData.js');
    return mod.VIDEOS || [];
  } catch {
    console.warn('⚠️ Could not load projectorData.js, generating pages-only sitemap');
    return [];
  }
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function durationISO(seconds) {
  if (!seconds || seconds <= 0) return 'PT0S';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  let iso = 'PT';
  if (h) iso += `${h}H`;
  if (m) iso += `${m}M`;
  if (s) iso += `${s}S`;
  return iso;
}

async function generate() {
  const videos = await loadVideos();

  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
`;

  // Static pages
  for (const p of pages) {
    xml += `  <url>
    <loc>${DOMAIN}${p.path}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>${p.freq}</changefreq>
    <priority>${p.priority}</priority>
  </url>
`;
  }

  // Video pages — each video gets a URL entry with video:video extension
  // This tells Google about our video content and links it to our domain.
  // ALL videos (deduped by id), matching the pre-rendered /watch/<id> pages 1:1.
  const seenIds = new Set();
  const topVideos = videos.filter((v) => v && v.id && !seenIds.has(v.id) && seenIds.add(v.id));
  for (const v of topVideos) {
    const thumbUrl = `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`;
    const ytUrl = `https://www.youtube.com/watch?v=${v.id}`;
    const title = escapeXml(v.t);
    const desc = escapeXml(
      (v.desc || `${v.t} — Public Domain Klassiker in 8K restauriert. Kostenlos auf frai.tv`).slice(
        0,
        2048
      )
    );

    xml += `  <url>
    <loc>${DOMAIN}/watch/${v.id}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
    <video:video>
      <video:thumbnail_loc>${thumbUrl}</video:thumbnail_loc>
      <video:title>${title}</video:title>
      <video:description>${desc}</video:description>
      <video:content_loc>${ytUrl}</video:content_loc>
      <video:player_loc allow_embed="yes">${ytUrl}</video:player_loc>
      <video:duration>${v.d || 0}</video:duration>
      <video:family_friendly>yes</video:family_friendly>
      <video:requires_subscription>no</video:requires_subscription>
      <video:live>no</video:live>
    </video:video>
  </url>
`;
  }

  // Series pages — slugs MUST match the pre-rendered hub pages in /series/<slug>/
  const seriesIds = [
    'betty-boop',
    'superman',
    'felix',
    'kwak',
    'popeye',
    'casper',
    'looney-tunes',
    'maulwurf',
    'soundies',
  ];
  for (const s of seriesIds) {
    xml += `  <url>
    <loc>${DOMAIN}/series/${s}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
`;
  }

  // Category pages
  const categories = ['animation', 'superhero', 'music', 'history', 'kids', 'cinema'];
  for (const c of categories) {
    xml += `  <url>
    <loc>${DOMAIN}/browse/${c}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
`;
  }

  xml += '</urlset>\n';

  const outPath = resolve(__dirname, '../public/sitemap.xml');
  writeFileSync(outPath, xml, 'utf-8');
  console.log(
    `✅ Sitemap generated: ${outPath} (${pages.length} pages + ${topVideos.length} videos + ${seriesIds.length} series + ${categories.length} categories)`
  );
}

generate().catch(console.error);
