/**
 * generate-static-pages.mjs — Pre-render static HTML for non-video routes
 * =======================================================================
 * Generates index.html files for each SPA route so Googlebot sees real content
 * instead of an empty <div id="root"></div>.
 *
 * Each page includes:
 *  - Full <head> with title, description, OG tags, canonical, JSON-LD
 *  - A <noscript> / <main> section with actual text content for crawlers
 *  - The Vite SPA bundle references so React hydrates for real users
 *
 * Output: public/{route}/index.html (Vite copies public/ into dist/ on build)
 *
 * Run BEFORE `vite build` — same as generate-watch-pages.mjs
 */
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  VIDEOS,
  GENRES,
  CHANNEL,
  WOCHENSCHAU_EVENTS,
  genre,
  fmtViews,
} from '../src/data/projectorData.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const publicDir = resolve(__dirname, '../public');

const htmlEscape = (value = '') =>
  String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');

// ── Page Definitions ───────────────────────────────────────────
const PAGES = [
  {
    route: '/timeline',
    title: 'Timeline — Filmgeschichte 1894 bis heute | frai.tv',
    description:
      'Interaktive Zeitleiste aller restaurierten Filme auf frai.tv: Von den ersten Stummfilmen 1894 bis zu modernen Klassikern. Chronologisch sortiert nach Jahrzehnt.',
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: 'Timeline — Filmgeschichte 1894 bis heute',
      description:
        'Interaktive Zeitleiste aller restaurierten Public Domain Filme von 1894 bis heute.',
      url: 'https://frai.tv/timeline',
      numberOfItems: VIDEOS.length,
      provider: { '@id': 'https://frai.tv/#organization' },
    },
    content: () => {
      // Group by decade for crawler content
      const decades = {};
      for (const v of VIDEOS) {
        const d = v.y ? `${Math.floor(v.y / 10) * 10}s` : 'Undatiert';
        if (!decades[d]) decades[d] = [];
        decades[d].push(v);
      }
      let html = '<h1>Timeline — Filmgeschichte auf frai.tv</h1>\n';
      html += `<p>${VIDEOS.length} restaurierte Filme von 1894 bis heute, chronologisch sortiert.</p>\n`;
      for (const [decade, vids] of Object.entries(decades).sort()) {
        html += `<h2>${decade}</h2>\n<ul>\n`;
        for (const v of vids.slice(0, 10)) {
          html += `  <li><a href="/watch/${v.id}">${htmlEscape(v.t)}</a> (${v.y || '?'})</li>\n`;
        }
        if (vids.length > 10) html += `  <li>... und ${vids.length - 10} weitere</li>\n`;
        html += '</ul>\n';
      }
      return html;
    },
  },
  {
    route: '/live',
    title: 'CommunityTV — Live Stream Dashboard | frai.tv',
    description:
      'Interaktives Live-Stream-Dashboard mit Voting, Chat, Queue und Reactions. Second-Screen fuer YouTube Live Streams von remAIke_IT.',
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: 'CommunityTV — Live Stream Dashboard',
      description:
        'Interactive live stream dashboard for frai.tv community. Voting, chat, queue management.',
      url: 'https://frai.tv/live',
      provider: { '@id': 'https://frai.tv/#organization' },
    },
    content: () =>
      '<h1>CommunityTV — Live Stream Dashboard</h1>\n' +
      '<p>Interaktives Live-Stream-Dashboard fuer die frai.tv Community. ' +
      'Voting, Chat, Queue und Reactions in Echtzeit.</p>\n' +
      '<p><a href="https://www.youtube.com/@remAIke_IT">Zum YouTube Live Stream</a></p>\n',
  },
  {
    route: '/impressum',
    title: 'Impressum | frai.tv',
    description:
      'Impressum und rechtliche Informationen zu frai.tv — FREE AI Enhanced TV. Angaben gemaess Paragraph 5 TMG.',
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: 'Impressum',
      description: 'Legal notice for frai.tv — FREE AI Enhanced TV',
      url: 'https://frai.tv/impressum',
      provider: { '@id': 'https://frai.tv/#organization' },
    },
    content: () =>
      '<h1>Impressum</h1>\n' +
      '<p>Angaben gemaess Paragraph 5 TMG</p>\n' +
      '<p>frai.tv ist ein Projekt der skillbox.nrw GmbH.</p>\n' +
      '<p><a href="/">Zurueck zur Startseite</a></p>\n',
  },
  {
    route: '/datenschutz',
    title: 'Datenschutz | frai.tv',
    description:
      'Datenschutzerklaerung von frai.tv. Informationen zur Verarbeitung personenbezogener Daten gemaess DSGVO.',
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: 'Datenschutzerklaerung',
      description: 'Privacy policy for frai.tv — GDPR compliant',
      url: 'https://frai.tv/datenschutz',
      provider: { '@id': 'https://frai.tv/#organization' },
    },
    content: () =>
      '<h1>Datenschutzerklaerung</h1>\n' +
      '<p>Informationen zur Verarbeitung personenbezogener Daten gemaess DSGVO.</p>\n' +
      '<p><a href="/">Zurueck zur Startseite</a></p>\n',
  },
];

// ── HTML Template ──────────────────────────────────────────────
function buildPage({ route, title, description, jsonLd, content }) {
  const url = `https://frai.tv${route}`;
  const ogImage = 'https://i.ytimg.com/vi/FG-vqRH5Cg4/maxresdefault.jpg';
  const bodyContent = typeof content === 'function' ? content() : content;

  return `<!doctype html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${htmlEscape(title)}</title>
  <meta name="description" content="${htmlEscape(description)}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="${url}" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="${url}" />
  <meta property="og:title" content="${htmlEscape(title)}" />
  <meta property="og:description" content="${htmlEscape(description)}" />
  <meta property="og:image" content="${ogImage}" />
  <meta property="og:site_name" content="frai.tv" />
  <meta property="og:locale" content="de_DE" />

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${htmlEscape(title)}" />
  <meta name="twitter:description" content="${htmlEscape(description)}" />
  <meta name="twitter:image" content="${ogImage}" />

  <!-- Theme -->
  <meta name="theme-color" content="#0a0a0c" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="manifest" href="/manifest.json" />
  <link rel="apple-touch-icon" href="/icons/icon-192.png" />

  <!-- Preconnect -->
  <link rel="preconnect" href="https://i.ytimg.com" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

  <!-- JSON-LD -->
  <script type="application/ld+json">${JSON.stringify(jsonLd)}</script>

  <style>
    body { font-family: Inter, system-ui, sans-serif; margin: 0; background: #0f1117; color: #e5e7eb; }
    .seo-content { max-width: 900px; margin: 0 auto; padding: 40px 24px; }
    .seo-content h1 { font-size: 2rem; margin-bottom: 16px; }
    .seo-content h2 { font-size: 1.4rem; margin-top: 24px; color: #c9a962; }
    .seo-content a { color: #c9a962; }
    .seo-content ul { padding-left: 20px; }
    .seo-content li { margin-bottom: 4px; }
    .seo-content p { line-height: 1.6; opacity: 0.85; }
    /* Hide SEO content when JS loads the SPA */
    .js-loaded .seo-content { display: none; }
  </style>
</head>
<body>
  <div id="root"></div>
  <div class="seo-content">
    ${bodyContent}
    <nav>
      <p>
        <a href="/">Startseite</a> |
        <a href="/timeline">Timeline</a> |
        <a href="/live">CommunityTV</a> |
        <a href="/impressum">Impressum</a> |
        <a href="/datenschutz">Datenschutz</a>
      </p>
      <p style="margin-top:16px;font-size:13px;opacity:0.6;">
        <a href="https://www.youtube.com/@remAIke_IT">YouTube @remAIke_IT</a> |
        <a href="https://www.remaike.IT">remAIke.IT</a>
      </p>
    </nav>
  </div>
  <script>
    // Load SPA bundle if JS is enabled — the SPA takes over rendering
    (function() {
      var s = document.querySelector('.seo-content');
      if (s) s.style.display = 'none';
      // Find and load the main JS bundle
      fetch('/').then(function(r) { return r.text(); }).then(function(html) {
        var m = html.match(/src="(\\/assets\\/index-[^"]+\\.js)"/);
        if (m) {
          var script = document.createElement('script');
          script.type = 'module';
          script.src = m[1];
          document.head.appendChild(script);
          // Also load the CSS
          var cssMatch = html.match(/href="(\\/assets\\/index-[^"]+\\.css)"/);
          if (cssMatch) {
            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = cssMatch[1];
            document.head.appendChild(link);
          }
        }
      }).catch(function() {
        // If fetch fails, show the static content
        if (s) s.style.display = '';
      });
    })();
  </script>
</body>
</html>`;
}

// ── Generate Homepage ──────────────────────────────────────────
// The homepage is special: we enhance the existing index.html with crawler content
// instead of creating a subfolder. We'll generate a separate homepage-seo.html
// that the .htaccess can serve to bots, or we inject noscript content.
function buildHomepage() {
  // Generate a list of genres and top videos for crawler visibility
  const genreLinks = GENRES.filter((g) => g.id !== 'all')
    .map((g) => `<li>${g.emoji} ${g.label} (${g.count || '?'} Filme)</li>`)
    .join('\n      ');

  const topVideos = VIDEOS.slice(0, 30)
    .map((v) => `<li><a href="/watch/${v.id}">${htmlEscape(v.t)}</a> — ${fmtViews(v.v)} Views</li>`)
    .join('\n      ');

  return `
    <h1>frai.tv — FREE AI Enhanced TV</h1>
    <p>Ueber ${CHANNEL.total} restaurierte Public Domain Filme in 8K Qualitaet. Kostenlos, legal, werbefrei.</p>
    <h2>Genres</h2>
    <ul>
      ${genreLinks}
    </ul>
    <h2>Beliebte Filme</h2>
    <ul>
      ${topVideos}
    </ul>
    <h2>Ueber frai.tv</h2>
    <p>frai.tv (FREE AI Enhanced TV) ist eine kostenlose Streaming-Plattform fuer restaurierte Public Domain Filme.
    Alle Inhalte werden mit KI-Technologie in 8K Qualitaet restauriert. Das Archiv umfasst Klassiker von 1894 bis heute:
    Betty Boop, Superman, Felix the Cat, Popeye, Casper, Alfred J. Kwak, historische Wochenschau-Dokumentationen,
    Jazz Soundies der 1940er Jahre und vieles mehr.</p>
    <nav>
      <p>
        <a href="/timeline">Timeline</a> |
        <a href="/live">CommunityTV</a> |
        <a href="/impressum">Impressum</a> |
        <a href="/datenschutz">Datenschutz</a> |
        <a href="https://www.youtube.com/@remAIke_IT">YouTube @remAIke_IT</a>
      </p>
    </nav>`;
}

// ── Main ───────────────────────────────────────────────────────
async function run() {
  let count = 0;

  // Generate subpages
  for (const page of PAGES) {
    const dir = resolve(publicDir, page.route.slice(1)); // Remove leading /
    await mkdir(dir, { recursive: true });
    const html = buildPage(page);
    await writeFile(resolve(dir, 'index.html'), html, 'utf8');
    count++;
    console.log(`  Static: ${page.route}`);
  }

  // Inject noscript content into main index.html for homepage SEO
  const indexPath = resolve(__dirname, '../index.html');
  let indexHtml = await readFile(indexPath, 'utf8');

  const homepageContent = buildHomepage();
  const noscriptBlock = `\n  <noscript>\n  <div class="seo-content">${homepageContent}\n  </div>\n  </noscript>`;

  // Remove any existing noscript block (idempotent)
  indexHtml = indexHtml.replace(/\n\s*<noscript>\n\s*<div class="seo-content">[\s\S]*?<\/noscript>/m, '');

  // Insert noscript block after <div id="root"></div>
  indexHtml = indexHtml.replace(
    '<div id="root"></div>',
    `<div id="root"></div>${noscriptBlock}`
  );

  await writeFile(indexPath, indexHtml, 'utf8');
  count++;
  console.log('  Static: / (homepage noscript injected)');

  console.log(`\nStatic pages: ${count} generated`);
}

run().catch((err) => {
  console.error('Static page generation failed:', err);
  process.exit(1);
});
