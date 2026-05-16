/**
 * generate-sitemap.mjs — Enhanced sitemap for frai.tv
 * Pages + video references with video:video markup
 * - Wochenschau: family_friendly=no, geo tags, multilingual descriptions
 * - Mega-brand cross-promotion (frai.tv / remAIke.IT / YouTube)
 * Updated: 2026-02-23
 */
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataPath = resolve(__dirname, '../src/data/projectorData.js');
const outPath = resolve(__dirname, '../public/sitemap.xml');

// Dynamic import for full data access
import { pathToFileURL } from 'url';
const dataModuleUrl = pathToFileURL(resolve(__dirname, '../src/data/projectorData.js')).href;
const data = await import(dataModuleUrl);
const { VIDEOS, WOCHENSCHAU_EVENTS } = data;

const unique = [];
const seen = new Set();
for (const v of VIDEOS) {
  if (!v?.id || seen.has(v.id)) continue;
  seen.add(v.id);
  unique.push(v);
}

const today = new Date().toISOString().slice(0, 10);

const esc = (s = '') =>
  String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

function videoDescription(v) {
  if (v.cat === 'wochenschau' && v.wNum && WOCHENSCHAU_EVENTS?.[v.wNum]) {
    const ev = WOCHENSCHAU_EVENTS[v.wNum];
    return (
      `Deutsche Wochenschau Nr. ${v.wNum} (${ev.date}) — ${ev.en}. ` +
      `Location: ${ev.loc}. Original WWII newsreel for educational purposes. AI remastered in 8K. ` +
      `Free on frai.tv — restored by remAIke.IT.`
    );
  }
  if (v.cat === 'soundies') {
    return `${v.t} — rare 1940s Soundie (jukebox music film). Jazz &amp; Swing restored in 8K. Free on frai.tv.`;
  }
  return `${v.t} — AI remastered in 8K quality. Public domain classic. Free on frai.tv — restored by remAIke.IT.`;
}

let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">

  <!-- Navigation Pages -->
  <url>
    <loc>https://frai.tv/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://frai.tv/timeline</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://frai.tv/live</loc>
    <lastmod>${today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://frai.tv/impressum</loc>
    <lastmod>${today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://frai.tv/datenschutz</loc>
    <lastmod>${today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>

  <!-- Videos (${unique.length} total with video:video markup) -->
`;

for (const v of unique) {
  const title = esc(v.t);
  const thumb = `https://i.ytimg.com/vi/${v.id}/maxresdefault.jpg`;
  const contentUrl = `https://www.youtube.com/watch?v=${v.id}`;
  const playerUrl = `https://www.youtube-nocookie.com/embed/${v.id}`;
  const isWochenschau = v.cat === 'wochenschau';
  const familyFriendly = isWochenschau ? 'no' : 'yes';
  const desc = esc(videoDescription(v));
  const priority = isWochenschau ? '0.8' : '0.6';

  // Wochenschau gets geo tag
  const ev = (isWochenschau && v.wNum && WOCHENSCHAU_EVENTS?.[v.wNum]) || null;
  const geoTag = ev
    ? `\n      <video:tag>${esc(ev.loc)}</video:tag>\n      <video:tag>${esc(ev.en)}</video:tag>\n      <video:tag>Wochenschau ${v.wNum}</video:tag>\n      <video:tag>WWII newsreel</video:tag>`
    : '';

  xml += `  <url>
    <loc>https://frai.tv/watch/${v.id}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>${priority}</priority>
    <video:video>
      <video:thumbnail_loc>${thumb}</video:thumbnail_loc>
      <video:title>${title}</video:title>
      <video:description>${desc}</video:description>
      <video:content_loc>${contentUrl}</video:content_loc>
      <video:player_loc>${playerUrl}</video:player_loc>
      <video:family_friendly>${familyFriendly}</video:family_friendly>
      <video:live>no</video:live>${geoTag}
    </video:video>
  </url>
`;
}

xml += `</urlset>\n`;

writeFileSync(outPath, xml, 'utf-8');
console.log(`Sitemap: ${unique.length} videos + 5 pages -> ${outPath}`);
