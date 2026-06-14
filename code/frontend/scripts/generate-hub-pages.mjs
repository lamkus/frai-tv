// Pre-render crawlable HUB pages: /wochenschau/, /series/, /series/<id>/
// + video-sitemap.xml + indexnow url list. Makes series hubs visible to Google/AI.
import { mkdir, writeFile, rm } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { VIDEOS, WOCHENSCHAU_EVENTS, fmtDur, fmtViews } from '../src/data/projectorData.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pub = resolve(__dirname, '../public');

const esc = (v = '') => String(v).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');

// seriesId (route) -> { label, cat (video.cat key), blurb }
const SERIES = [
  { id: 'kwak', label: 'Alfred J. Kwak', cat: 'alfred', blurb: 'Alfred J. Kwak ist eine niederländisch-deutsch-japanische Zeichentrickserie (1989–1991) rund um die Ente Alfred. Die Serie verbindet kindgerechte Abenteuer mit ernsten Themen wie Umwelt, Toleranz und Demokratie. Hier in deutscher Fassung, KI-restauriert in 8K.' },
  { id: 'betty-boop', label: 'Betty Boop', cat: 'betty_boop', blurb: 'Betty Boop, geschaffen von Max Fleischers Fleischer Studios, war eine der prägenden Figuren der US-Animation der frühen 1930er. Viele dieser Pre-Code-Cartoons sind gemeinfrei und gelten als Meilensteine der Trickfilmgeschichte.' },
  { id: 'superman', label: 'Superman (Fleischer)', cat: 'superman', blurb: 'Die Fleischer-/Famous-Studios-Superman-Cartoons (1941–1943) gelten als Meilenstein des Theatrical-Animation und prägten die visuelle Sprache des Superhelden-Genres. Gemeinfrei, KI-restauriert in 8K.' },
  { id: 'felix', label: 'Felix the Cat', cat: 'felix', blurb: 'Felix the Cat war einer der ersten Animations-Stars überhaupt und entstand in der Stummfilmzeit (ab 1919). Die surrealen, gemeinfreien Schwarzweiß-Klassiker beeinflussten Generationen von Zeichnern.' },
  { id: 'popeye', label: 'Popeye', cat: 'popeye', blurb: 'Popeye der Seemann, ursprünglich von Fleischer Studios animiert, zählt zu den bekanntesten Cartoon-Figuren der 1930er/40er. KI-restauriert in 8K.' },
  { id: 'casper', label: 'Casper', cat: 'casper', blurb: 'Casper, der freundliche Geist, stammt aus den Famous-Studios-Cartoons der 1940er/50er — herzliche Kurzfilme für die ganze Familie.' },
  { id: 'maulwurf', label: 'Der kleine Maulwurf', cat: 'maulwurf', blurb: 'Der kleine Maulwurf (Krtek) ist eine tschechische Zeichentrickfigur von Zdeněk Miler, weltweit beliebt und meist ganz ohne Worte erzählt — verständlich in jeder Sprache.' },
  { id: 'soundies', label: 'Soundies', cat: 'soundies', blurb: 'Soundies waren rund dreiminütige Musikfilme, produziert 1940–1947 für münzbetriebene Panoram-Jukeboxen — die Musikvideos vor dem Fernsehen. Jazz, Swing und Big-Band-Auftritte der Ära, KI-restauriert in 8K.' },
  { id: 'looney-tunes', label: 'Golden-Age Cartoons', cat: 'looney', blurb: 'Klassische US-Theatrical-Cartoons aus dem Golden Age der Animation (1930er–1940er), KI-restauriert in 8K.' },
];

const uniqueVideos = (() => {
  const seen = new Set(); const out = [];
  for (const v of VIDEOS) { if (v?.id && !seen.has(v.id)) { seen.add(v.id); out.push(v); } }
  return out;
})();

const byCat = (cat) => uniqueVideos.filter((v) => v.cat === cat);

const HEAD = (title, desc, url, schemaArr) => `<!doctype html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(desc)}" />
  <link rel="canonical" href="${url}" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="${esc(title)}" />
  <meta property="og:description" content="${esc(desc)}" />
  <meta property="og:url" content="${url}" />
  <meta property="og:site_name" content="frai.tv — FREE AI Enhanced TV" />
${schemaArr.map((s) => `  <script type="application/ld+json">${JSON.stringify(s)}</script>`).join('\n')}
  <style>
    body{font-family:Inter,system-ui,sans-serif;margin:0;background:#0f1117;color:#e5e7eb}
    .wrap{max-width:980px;margin:0 auto;padding:24px}a{color:#facc15;text-decoration:none}a:hover{text-decoration:underline}
    h1{font-size:1.7rem;margin:10px 0}h2{font-size:1.15rem;margin:26px 0 10px}
    p{line-height:1.7;opacity:.92}ul.eps{list-style:none;padding:0;columns:2;column-gap:30px}
    ul.eps li{margin:6px 0;break-inside:avoid}.tag{opacity:.6;font-size:.85rem}
    .grid{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}.card{background:#1a1d27;border-radius:10px;padding:12px 16px}
    nav{margin:8px 0 18px;opacity:.85}nav a{margin-right:14px}
  </style>
</head>
<body>
  <main class="wrap">
    <nav><a href="/">frai.tv</a> · <a href="/wochenschau/">Wochenschau-Archiv</a> · <a href="/series/">Alle Serien</a> · <a href="/timeline/">Timeline</a></nav>`;

const FOOT = `
    <p style="margin-top:30px;opacity:.7;font-size:.9rem">🌐 <a href="https://www.remaike.IT">remAIke.IT</a> · 📺 <a href="https://frai.tv">frai.tv</a> · ▶ <a href="https://www.youtube.com/@remAIke_IT">YouTube @remAIke_IT</a></p>
  </main>
</body>
</html>`;

const epLink = (v) => `      <li><a href="/watch/${v.id}/">${esc(v.t)}</a> <span class="tag">${v.y || ''} · ${fmtDur(v.d)}</span></li>`;

const itemListSchema = (vids, name, url) => ({
  '@context': 'https://schema.org', '@type': 'CollectionPage', name, url,
  mainEntity: {
    '@type': 'ItemList', numberOfItems: vids.length,
    itemListElement: vids.slice(0, 100).map((v, i) => ({
      '@type': 'ListItem', position: i + 1, url: `https://frai.tv/watch/${v.id}/`, name: v.t,
    })),
  },
});

async function writePage(routePath, html) {
  const dir = resolve(pub, routePath);
  await mkdir(dir, { recursive: true });
  await writeFile(resolve(dir, 'index.html'), html, 'utf8');
}

// ── /wochenschau/ ──
function wochenschauPage() {
  const vids = byCat('wochenschau').slice().sort((a, b) => (a.wNum || 0) - (b.wNum || 0));
  const url = 'https://frai.tv/wochenschau/';
  const title = `Deutsche Wochenschau Archiv (1939–1945) — ${vids.length} Folgen in 8K | frai.tv`;
  const desc = `Das chronologische Archiv der Deutschen Wochenschau, KI-restauriert in 8K. ${vids.length} historische WWII-Newsreels mit Ereignis, Ort und Datum — kostenlos auf frai.tv. Historisches Dokument zur wissenschaftlichen Aufklärung.`;
  const eps = vids.map((v) => {
    const ev = v.wNum && WOCHENSCHAU_EVENTS?.[v.wNum];
    const label = ev ? `Nr. ${v.wNum}: ${ev.en} (${ev.date}) — ${ev.loc}` : v.t;
    return `      <li><a href="/watch/${v.id}/">${esc(label)}</a></li>`;
  }).join('\n');
  const html = HEAD(title, desc, url, [itemListSchema(vids, 'Deutsche Wochenschau Archiv', url)]) + `
    <h1>Deutsche Wochenschau — Archiv 1939–1945</h1>
    <p>Die Deutsche Wochenschau war die wöchentliche Kino-Nachrichtenschau im Deutschen Reich. Als historisches Dokument der UFA-Zeit ist das Material gemeinfrei und dient hier ausschließlich der wissenschaftlich-historischen Aufklärung. remAIke.IT hat ${vids.length} Ausgaben mit KI in 8K (4K UHD) restauriert — schärfer als jede bisher verfügbare Fassung.</p>
    <p>Die Folgen sind chronologisch nach Ausgabennummer geordnet. Jede Seite nennt Ereignis, Aufnahmeort und Datum.</p>
    <h2>Alle Folgen (${vids.length})</h2>
    <ul class="eps">
${eps}
    </ul>` + FOOT;
  return writePage('wochenschau', html);
}

// ── /series/<id>/ ──
function seriesPage(s) {
  const vids = byCat(s.cat);
  if (!vids.length) return null;
  const url = `https://frai.tv/series/${s.id}/`;
  const title = `${s.label} — ${vids.length} Folgen in 8K (4K UHD) | frai.tv`;
  const desc = `${s.label}: ${vids.length} Folgen, KI-restauriert in 8K. ${s.blurb.slice(0, 110)}… Kostenlos auf frai.tv.`;
  const html = HEAD(title, desc, url, [itemListSchema(vids, s.label, url)]) + `
    <h1>${esc(s.label)}</h1>
    <p>${esc(s.blurb)}</p>
    <h2>Alle Folgen (${vids.length})</h2>
    <ul class="eps">
${vids.map(epLink).join('\n')}
    </ul>` + FOOT;
  return writePage(`series/${s.id}`, html);
}

// ── /series/ overview ──
function seriesIndex() {
  const url = 'https://frai.tv/series/';
  const rows = [
    { id: 'wochenschau', label: 'Deutsche Wochenschau', cat: 'wochenschau', href: '/wochenschau/' },
    ...SERIES.map((s) => ({ ...s, href: `/series/${s.id}/` })),
  ].map((s) => ({ ...s, n: byCat(s.cat).length })).filter((s) => s.n > 0);
  const title = `Serien & Sammlungen — Klassiker in 8K | frai.tv`;
  const desc = `Alle Serien auf frai.tv: Wochenschau, Alfred J. Kwak, Betty Boop, Superman, Felix, Popeye, Casper, Soundies und mehr — KI-restauriert in 8K, kostenlos.`;
  const cards = rows.map((s) => `      <div class="card"><a href="${s.href}"><strong>${esc(s.label)}</strong></a><br><span class="tag">${s.n} Folgen</span></div>`).join('\n');
  const schema = { '@context': 'https://schema.org', '@type': 'CollectionPage', name: 'Serien & Sammlungen', url, mainEntity: { '@type': 'ItemList', itemListElement: rows.map((s, i) => ({ '@type': 'ListItem', position: i + 1, url: `https://frai.tv${s.href}`, name: s.label })) } };
  const html = HEAD(title, desc, url, [schema]) + `
    <h1>Serien & Sammlungen</h1>
    <p>Alle restaurierten Serien und Sammlungen von remAIke.IT auf frai.tv — von der Deutschen Wochenschau über Alfred J. Kwak bis zu den Fleischer-Klassikern. Jede Serie KI-restauriert in 8K (4K UHD), kostenlos in voller Länge.</p>
    <div class="grid">
${cards}
    </div>` + FOOT;
  return writePage('series', html);
}

// ── video-sitemap.xml ──
async function videoSitemap() {
  const urls = uniqueVideos.map((v) => {
    const thumb = `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`;
    return `  <url>
    <loc>https://frai.tv/watch/${v.id}/</loc>
    <video:video>
      <video:thumbnail_loc>${thumb}</video:thumbnail_loc>
      <video:title>${esc(v.t)}</video:title>
      <video:description>${esc((v.t + ' — KI-restauriert in 8K (4K UHD) auf frai.tv').slice(0, 200))}</video:description>
      <video:player_loc>https://www.youtube-nocookie.com/embed/${v.id}</video:player_loc>
      <video:platform relationship="allow">web mobile tv</video:platform>
      <video:live>no</video:live>
    </video:video>
  </url>`;
  }).join('\n');
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
${urls}
</urlset>`;
  await writeFile(resolve(pub, 'video-sitemap.xml'), xml, 'utf8');
  return uniqueVideos.length;
}

const run = async () => {
  await rm(resolve(pub, 'series'), { recursive: true, force: true });
  await wochenschauPage();
  await seriesIndex();
  let s = 0;
  for (const ser of SERIES) { if (await seriesPage(ser)) s++; }
  const vc = await videoSitemap();

  // indexnow url list (for later submission)
  const allUrls = [
    'https://frai.tv/', 'https://frai.tv/wochenschau/', 'https://frai.tv/series/', 'https://frai.tv/timeline/',
    ...SERIES.map((x) => `https://frai.tv/series/${x.id}/`),
    ...uniqueVideos.map((v) => `https://frai.tv/watch/${v.id}/`),
  ];
  await writeFile(resolve(__dirname, '../indexnow-urls.json'), JSON.stringify(allUrls, null, 0), 'utf8');

  console.log(`Hub pages: /wochenschau + /series + ${s} series hubs`);
  console.log(`video-sitemap.xml: ${vc} videos`);
  console.log(`indexnow-urls.json: ${allUrls.length} URLs`);
};
run().catch((e) => { console.error(e); process.exit(1); });
