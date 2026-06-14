import { mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  VIDEOS,
  ytUrl,
  fmtDur,
  fmtViews,
  CHANNEL,
  WOCHENSCHAU_EVENTS,
} from '../src/data/projectorData.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outRoot = resolve(__dirname, '../public/watch');

const htmlEscape = (value = '') =>
  String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');

const toIsoDuration = (seconds = 0) => {
  const total = Math.max(0, Number(seconds) || 0);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  return `PT${hours ? `${hours}H` : ''}${minutes ? `${minutes}M` : ''}${secs || (!hours && !minutes) ? `${secs}S` : ''}`;
};

// ── Category labels & language helpers ──
const CAT_LABELS = {
  wochenschau: 'WWII Newsreel',
  soundies: 'Vintage Music',
  felix: 'Classic Animation',
  betty_boop: 'Classic Animation',
  superman: 'Superhero',
  alfred: "Children's Series",
  casper: 'Classic Animation',
  maulwurf: "Children's Series",
  looney: 'Classic Animation',
  popeye: 'Classic Animation',
  christmas: 'Holiday Classic',
  gymkhana: 'Motorsport',
  mel_o_toons: 'Classic Animation',
  silent_era: 'Silent Film',
  other: 'Classic Film',
  cinema: 'Classic Cinema',
};

const CAT_LANG = { alfred: 'de', maulwurf: 'de', wochenschau: 'de' };

// TRUE, category-level context — never fabricates per-film plot claims.
const CAT_BLURB = {
  wochenschau:
    'Die Deutsche Wochenschau war die wöchentliche Kino-Nachrichtenschau im Deutschen Reich (1940–1945). Als historisches Dokument der UFA-Zeit ist das Material gemeinfrei und dient ausschließlich der wissenschaftlich-historischen Aufklärung.',
  betty_boop:
    'Betty Boop wurde von Max Fleischers Fleischer Studios geschaffen und prägte die US-Animation der frühen 1930er. Viele dieser Pre-Code-Cartoons sind heute gemeinfrei.',
  soundies:
    'Soundies waren rund dreiminütige Musikfilme, produziert 1940–1947 für münzbetriebene Panoram-Jukeboxen — die Musikvideos vor dem Fernsehen. Jazz, Swing und Big-Band-Auftritte der Ära.',
  felix:
    'Felix the Cat war einer der ersten Animations-Stars und entstand in der Stummfilmzeit (ab 1919). Surreale, gemeinfreie Schwarzweiß-Klassiker.',
  superman:
    'Die Fleischer-/Famous-Studios-Superman-Cartoons (1941–1943) gelten als Meilenstein des Theatrical-Animation und sind gemeinfrei.',
  alfred:
    'Alfred J. Kwak ist eine Zeichentrickserie (1989–1991) rund um die Ente Alfred. Hier in deutscher Fassung, KI-restauriert.',
  casper:
    'Casper, der freundliche Geist, stammt aus den Famous-Studios-Cartoons der 1940er/50er.',
  maulwurf:
    'Der kleine Maulwurf (Krtek) ist eine tschechische Zeichentrickfigur von Zdeněk Miler, weltweit beliebt und meist ohne Worte erzählt.',
  looney:
    'Klassische US-Theatrical-Cartoons aus dem Golden Age der Animation (1930er–1940er), KI-restauriert in 8K.',
  popeye:
    'Popeye der Seemann, ursprünglich von Fleischer Studios animiert — Cartoon-Klassiker der 1930er/40er.',
  christmas: 'Weihnachts-Klassiker und festliche Kurzfilme, KI-restauriert in 8K.',
  gymkhana: 'Präzisions-Stunt-Motorsport-Filme.',
  mel_o_toons: 'Mel-O-Toons — kurze US-Zeichentrickfilme aus den frühen 1960ern.',
  silent_era: 'Werke der Stummfilm-Ära, KI-restauriert in 8K.',
  other: 'Filmklassiker und Archivmaterial, KI-restauriert in 8K von remAIke.IT.',
};
const blurbFor = (cat) => CAT_BLURB[cat] || CAT_BLURB.other;

const stripYear = (title = '') =>
  // Avoid "(1940s) (1940)" doubling: if title already carries a year/parenthetical year, don't append.
  /\(\d{4}s?\)/.test(title);

function buildDescription(video, ev) {
  if (video.cat === 'wochenschau' && ev) {
    return (
      `Deutsche Wochenschau Nr. ${video.wNum} (${ev.date}) — ${ev.en}, ${ev.loc}. ` +
      `Historisches WWII-Newsreel, KI-restauriert in 8K. Kostenlos auf frai.tv — restauriert von remAIke.IT.`
    );
  }
  if (video.cat === 'soundies') {
    return (
      `${video.t} — seltener 1940er Soundie (Jukebox-Musikfilm), Jazz & Swing, restauriert in 8K. ` +
      `Kostenlos auf frai.tv — restauriert von remAIke.IT.`
    );
  }
  return (
    `${video.t}${video.y && !stripYear(video.t) ? ` (${video.y})` : ''} — ${CAT_LABELS[video.cat] || 'Klassiker'}, ` +
    `KI-restauriert in 8K (4K UHD). Kostenlos in voller Länge auf frai.tv — restauriert von remAIke.IT.`
  );
}

// ── Substantive, crawlable body prose (unique per page) ──
function bodyProse(video, ev) {
  const blurb = blurbFor(video.cat);
  const paras = [];
  if (video.cat === 'wochenschau' && ev) {
    paras.push(
      `<strong>${htmlEscape(video.t)}</strong> zeigt die Wochenschau-Ausgabe Nr. ${video.wNum} vom ${ev.date} mit Schwerpunkt „${htmlEscape(ev.en)}" (${htmlEscape(ev.de)}), aufgenommen in ${htmlEscape(ev.loc)}. ${htmlEscape(ev.note)}.`
    );
    paras.push(blurb);
    paras.push(
      `Diese Ausgabe wurde von remAIke.IT mit KI in 8K (4K UHD) restauriert. Die volle Fassung läuft kostenlos auf YouTube; auf frai.tv findest du das gesamte chronologische Wochenschau-Archiv 1939–1945.`
    );
  } else {
    const yr = video.y && !stripYear(video.t) ? ` (${video.y})` : '';
    paras.push(
      `<strong>${htmlEscape(video.t)}</strong>${yr} ist ein ${htmlEscape(CAT_LABELS[video.cat] || 'Klassiker')}-Titel im Archiv von frai.tv. ${blurb}`
    );
    paras.push(
      `Die Fassung wurde von remAIke.IT mit KI auf 8K (4K UHD) hochskaliert und restauriert — schärfer und klarer als die üblichen Online-Versionen. Kostenlos in voller Länge auf YouTube oder im Kontext der Reihe auf frai.tv.`
    );
  }
  return paras.map((p) => `      <p>${p}</p>`).join('\n');
}

// ── FAQ block + FAQPage schema (strong signal for AI answer engines) ──
function faqBlock(video, ev) {
  const qs = [];
  if (video.cat === 'wochenschau' && ev) {
    qs.push([
      `Was ist Die Deutsche Wochenschau Nr. ${video.wNum}?`,
      `Eine deutsche Kino-Nachrichtenschau vom ${ev.date} über „${ev.en}" (${ev.de}), gedreht in ${ev.loc}. Historisches Dokument der Jahre 1940–1945, KI-restauriert in 8K.`,
    ]);
    qs.push([`Wo wurde diese Wochenschau aufgenommen?`, `${ev.loc}.`]);
    qs.push([
      `Ist das Material gemeinfrei?`,
      `Ja — die Deutsche Wochenschau der UFA-Zeit ist Public Domain und wird hier zu historisch-wissenschaftlichen Zwecken gezeigt.`,
    ]);
  } else {
    const blurb = blurbFor(video.cat);
    qs.push([
      `Was ist „${video.t}"?`,
      `Ein ${CAT_LABELS[video.cat] || 'Klassiker'}-Titel${video.y && !stripYear(video.t) ? ` aus ${video.y}` : ''}, KI-restauriert in 8K (4K UHD) von remAIke.IT. ${blurb}`,
    ]);
    qs.push([
      `Wo kann ich „${video.t}" kostenlos ansehen?`,
      `In voller Länge kostenlos auf YouTube (@remAIke_IT) und auf frai.tv.`,
    ]);
  }
  const html = qs
    .map(
      ([q, a]) =>
        `      <details><summary>${htmlEscape(q)}</summary><p>${htmlEscape(a)}</p></details>`
    )
    .join('\n');
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: qs.map(([q, a]) => ({
      '@type': 'Question',
      name: q,
      acceptedAnswer: { '@type': 'Answer', text: a },
    })),
  };
  return { html, schema };
}

// ── Internal "more from this series" links (funnel + crawl depth) ──
function relatedBlock(video, all) {
  const same = all.filter((x) => x.cat === video.cat && x.id !== video.id).slice(0, 8);
  if (!same.length) return '';
  const items = same
    .map((x) => `        <li><a href="/watch/${x.id}/">${htmlEscape(x.t)}</a></li>`)
    .join('\n');
  const label = CAT_LABELS[video.cat] || 'Reihe';
  return `    <section class="related">
      <h2>Mehr aus dieser Reihe (${htmlEscape(label)})</h2>
      <ul>
${items}
      </ul>
    </section>`;
}

const pageHtml = (video) => {
  const isWochenschau = video.cat === 'wochenschau';
  const ev = (isWochenschau && video.wNum && WOCHENSCHAU_EVENTS?.[video.wNum]) || null;
  const lang = CAT_LANG[video.cat] || 'en';
  const catLabel = CAT_LABELS[video.cat] || 'Classic';

  const title =
    isWochenschau && ev
      ? `Wochenschau ${video.wNum}: ${ev.en} (${ev.date}) | ${ev.loc} | frai.tv`
      : `${video.t} | ${catLabel} | frai.tv`;
  const desc = buildDescription(video, ev);
  const url = `https://frai.tv/watch/${video.id}`;
  const thumb = `https://i.ytimg.com/vi/${video.id}/maxresdefault.jpg`;

  // ── VideoObject JSON-LD ──
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'VideoObject',
    name: video.t,
    description: desc,
    thumbnailUrl: [thumb, thumb.replace('maxresdefault', 'hqdefault')],
    uploadDate: ev?.date
      ? `${ev.date}T00:00:00Z`
      : video.y
        ? `${video.y}-01-01T00:00:00Z`
        : undefined,
    duration: video.d ? toIsoDuration(video.d) : undefined,
    contentUrl: `https://www.youtube.com/watch?v=${video.id}`,
    embedUrl: `https://www.youtube-nocookie.com/embed/${video.id}`,
    url,
    mainEntityOfPage: url,
    interactionStatistic: {
      '@type': 'InteractionCounter',
      interactionType: { '@type': 'WatchAction' },
      userInteractionCount: video.v || 0,
    },
    publisher: {
      '@type': 'Organization',
      name: 'frai.tv',
      alternateName: ['FREE AI Enhanced TV', 'remAIke.IT'],
      url: 'https://frai.tv',
      sameAs: ['https://www.youtube.com/@remAIke_IT', 'https://www.remaike.IT'],
    },
    inLanguage: lang,
  };

  if (isWochenschau && ev) {
    schema.contentLocation = {
      '@type': 'Place',
      name: ev.loc,
      geo: { '@type': 'GeoCoordinates', latitude: ev.lat, longitude: ev.lng },
    };
    schema.about = {
      '@type': 'Event',
      name: ev.en,
      startDate: ev.date,
      location: { '@type': 'Place', name: ev.loc },
      description: ev.note,
    };
    schema.educationalLevel = 'advanced';
    schema.learningResourceType = 'Documentary';
    schema.genre = 'Documentary';
  }

  if (video.cat === 'soundies') {
    schema.genre = 'Jazz / Swing';
    schema.associatedMedia = { '@type': 'MusicRecording', name: video.t, genre: 'Jazz' };
  }

  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'frai.tv', item: 'https://frai.tv/' },
      { '@type': 'ListItem', position: 2, name: catLabel, item: `https://frai.tv/#genre-${video.cat}` },
      { '@type': 'ListItem', position: 3, name: video.t },
    ],
  };

  const fq = faqBlock(video, ev);
  const related = relatedBlock(video, VIDEOS);

  const wochenschauMeta =
    isWochenschau && ev
      ? `
  <meta name="keywords" content="Wochenschau, ${ev.en}, ${ev.de}, WWII newsreel, Deutsche Wochenschau ${video.wNum}, ${ev.loc}, World War 2, Segunda Guerra Mundial, 第二次世界大戦, 8K restored, ${ev.date}" />
  <meta property="og:locale" content="de_DE" />
  <meta property="og:locale:alternate" content="en_US" />
  <meta name="geo.position" content="${ev.lat};${ev.lng}" />
  <meta name="geo.placename" content="${ev.loc}" />`
      : '';

  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${htmlEscape(title)}</title>
  <meta name="description" content="${htmlEscape(desc)}" />
  <link rel="canonical" href="${url}" />${wochenschauMeta}
  <meta property="og:type" content="video.other" />
  <meta property="og:title" content="${htmlEscape(title)}" />
  <meta property="og:description" content="${htmlEscape(desc)}" />
  <meta property="og:url" content="${url}" />
  <meta property="og:image" content="${thumb}" />
  <meta property="og:site_name" content="frai.tv — FREE AI Enhanced TV" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${htmlEscape(title)}" />
  <meta name="twitter:description" content="${htmlEscape(desc)}" />
  <meta name="twitter:image" content="${thumb}" />
  <link rel="alternate" hreflang="de" href="${url}" />
  <link rel="alternate" hreflang="en" href="${url}" />
  <link rel="alternate" hreflang="x-default" href="${url}" />
  <script type="application/ld+json">${JSON.stringify(schema)}</script>
  <script type="application/ld+json">${JSON.stringify(breadcrumb)}</script>
  <script type="application/ld+json">${JSON.stringify(fq.schema)}</script>
  <style>
    body { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background: #0f1117; color: #e5e7eb; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 24px; }
    a { color: #facc15; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .frame { position: relative; width: 100%; padding-top: 56.25%; border-radius: 14px; overflow: hidden; background: #000; margin: 14px 0; }
    iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
    h1 { margin: 12px 0 8px; font-size: 1.55rem; line-height: 1.3; }
    h2 { font-size: 1.15rem; margin: 28px 0 10px; }
    .meta { opacity: .85; margin-bottom: 6px; }
    .loc { opacity: .7; font-size: .95rem; margin-bottom: 8px; }
    .actions { margin: 14px 0; display: flex; gap: 16px; flex-wrap: wrap; }
    .content p { line-height: 1.7; opacity: .92; margin: 10px 0; }
    .related ul { columns: 2; column-gap: 28px; padding-left: 18px; }
    .related li { margin: 5px 0; break-inside: avoid; }
    details { margin: 6px 0; padding: 8px 12px; background: #1a1d27; border-radius: 8px; }
    summary { cursor: pointer; font-weight: 600; }
    details p { margin: 8px 0 2px; opacity: .9; }
    .brand { margin-top: 28px; padding: 16px; background: #1a1d27; border-radius: 10px; font-size: .9rem; line-height: 1.6; }
    .brand a { margin: 0 6px; }
  </style>
</head>
<body>
  <main class="wrap">
    <a href="/">← Zurück zu frai.tv</a>
    <h1>${htmlEscape(video.t)}</h1>
    <p class="meta">🎬 ${htmlEscape(catLabel)} · ${video.y || ''} · ${fmtDur(video.d)} · ${fmtViews(video.v)} Views</p>${
      isWochenschau && ev
        ? `
    <p class="loc">📍 ${htmlEscape(ev.loc)} · 📅 ${ev.date} · 📜 ${htmlEscape(ev.en)}</p>`
        : ''
    }
    <div class="frame">
      <iframe src="https://www.youtube-nocookie.com/embed/${video.id}?autoplay=0&rel=0" title="${htmlEscape(video.t)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
    </div>
    <div class="actions">
      <a href="${ytUrl(video.id)}">▶ In 8K auf YouTube ansehen →</a>
      <a href="/">🎬 Alle Videos auf frai.tv</a>
    </div>
    <section class="content">
${bodyProse(video, ev)}
    </section>
    <section class="faq">
      <h2>Häufige Fragen</h2>
${fq.html}
    </section>
${related}
    <div class="brand">
      🌐 <a href="https://www.remaike.IT">remAIke.IT</a> — AI Video Restoration ·
      📺 <a href="https://frai.tv">frai.tv</a> — FREE AI Enhanced TV ·
      ▶ <a href="https://www.youtube.com/@remAIke_IT">YouTube @remAIke_IT</a>
    </div>
  </main>
</body>
</html>`;
};

const run = async () => {
  await rm(outRoot, { recursive: true, force: true });
  await mkdir(outRoot, { recursive: true });

  const unique = [];
  const seen = new Set();
  for (const video of VIDEOS) {
    if (!video?.id || seen.has(video.id)) continue;
    seen.add(video.id);
    unique.push(video);
  }

  for (const video of unique) {
    const dir = resolve(outRoot, video.id);
    await mkdir(dir, { recursive: true });
    await writeFile(resolve(dir, 'index.html'), pageHtml(video), 'utf8');
  }

  console.log(`Watch pages v2: ${unique.length} -> ${outRoot}`);
};

run().catch((err) => {
  console.error('Watch page generation failed:', err);
  process.exit(1);
});
