/**
 * Series Detection & Episode Matching System
 *
 * Features:
 * 1. Detect SERIES from filename/title patterns
 * 2. Extract EPISODE_TITLE and YEAR from various formats
 * 3. Match against canonical episode lists
 * 4. Fuzzy matching with Levenshtein distance
 * 5. Template-based title/description rendering
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ============================================================================
// SERIES DETECTION PATTERNS
// ============================================================================

const SERIES_PATTERNS = [
  // ========== PREFORMATTED (already has episode numbers) ==========
  { pattern: /^Casper\s*\(\d+\/\d+\)/i, series: 'casper', preformatted: true },
  { pattern: /^Superman\s*\(\d+\/\d+\)/i, series: 'superman', preformatted: true },
  { pattern: /^Popeye\s*\(\d+\/\d+\)/i, series: 'popeye', preformatted: true },
  { pattern: /^Betty Boop\s*\(\d+\/\d+\)/i, series: 'betty-boop', preformatted: true },
  { pattern: /^Alfred Jodokus Quack\s*\(\d+\/\d+\)/i, series: 'alfred-j-kwak', preformatted: true },
  { pattern: /^Astro Boy\s*\(\d+\/\d+\)/i, series: 'astro-boy', preformatted: true },
  { pattern: /^Porky Pig\s*\(\d+\/\d+\)/i, series: 'porky-pig', preformatted: true },

  // ========== ALFRED J. KWAK ==========
  { pattern: /^Alfred Jodokus Quack/i, series: 'alfred-j-kwak' },
  { pattern: /^Alfred J\. Kwak/i, series: 'alfred-j-kwak' },
  { pattern: /\bAlfred Jodokus Quack\b/i, series: 'alfred-j-kwak', priority: 10 },

  // ========== ASTRO BOY ==========
  { pattern: /^Astro Boy/i, series: 'astro-boy' },
  { pattern: /\bAstro Boy\b/i, series: 'astro-boy', priority: 10 },

  // ========== PORKY PIG ==========
  { pattern: /^Porky Pig/i, series: 'porky-pig' },
  { pattern: /^Porky's/i, series: 'porky-pig' },
  { pattern: /\bPorky Pig\b/i, series: 'porky-pig', priority: 10 },

  // ========== CASPER ==========
  { pattern: /^Casper\s*[-:—]\s*/i, series: 'casper' },
  { pattern: /^Casper the Friendly Ghost/i, series: 'casper' },
  { pattern: /\bCasper\b/i, series: 'casper', priority: 10 },

  // ========== SUPERMAN (Fleischer) ==========
  { pattern: /^Superman\s*[-:—]\s*/i, series: 'superman' },
  { pattern: /^Superman\s*#?\d+/i, series: 'superman' },
  { pattern: /Superman[-:]\s*/i, series: 'superman' }, // "Superman: Electric Earthquake"
  { pattern: /\bMax Fleischer['']?s?\s*Superman/i, series: 'superman' }, // "Max Fleischer's Superman:"
  { pattern: /\b8k\s+Max Fleischer['']?s?\s*Superman/i, series: 'superman' }, // "8k Max Fleischer's Superman:"
  { pattern: /Fleischer.*Superman/i, series: 'superman' },
  { pattern: /Superman.*Fleischer/i, series: 'superman' },
  { pattern: /Superman.*\(194[1-3]\)/i, series: 'superman' },
  { pattern: /\bSuperman\b/i, series: 'superman', priority: 10 },

  // ========== POPEYE ==========
  { pattern: /^Popeye\s*[-:—]\s*/i, series: 'popeye' },
  { pattern: /^Popeye the Sailor\s*[-:—]\s*/i, series: 'popeye' }, // "Popeye the Sailor – Ancient Fistory"
  { pattern: /^Popeye the Sailor\b/i, series: 'popeye' },
  { pattern: /^Patriotic Popeye/i, series: 'popeye' }, // Special episode
  { pattern: /POPEYE\s*\|/i, series: 'popeye', isMarathon: true }, // "POPEYE | 8K" marathon
  { pattern: /\bPopeye\b.*Marathon/i, series: 'popeye', isMarathon: true },
  { pattern: /\bPopeye\b/i, series: 'popeye', priority: 10 },

  // ========== BETTY BOOP ==========
  { pattern: /^Betty Boop\s*[-:—]\s*/i, series: 'betty-boop' },
  { pattern: /^Betty Boop'?s?\s+/i, series: 'betty-boop' }, // "Betty Boop's Ker-Choo"
  { pattern: /\bBetty Boop\b/i, series: 'betty-boop', priority: 10 },

  // ========== CHARLIE CHAPLIN ==========
  { pattern: /^Charlie Chaplin\s*[-:—]\s*/i, series: 'charlie-chaplin' },
  { pattern: /^Chaplin\s*[-:—]\s*/i, series: 'charlie-chaplin' },
  { pattern: /Charlie Chaplin Film Fest/i, series: 'charlie-chaplin', isMarathon: true },
  { pattern: /Charlie Chaplin.*Marathon/i, series: 'charlie-chaplin', isMarathon: true },
  { pattern: /–\s*Charlie Chaplin\b/i, series: 'charlie-chaplin' }, // "The Cure (1917) – Charlie Chaplin"
  { pattern: /-\s*Charlie Chaplin\b/i, series: 'charlie-chaplin' }, // "The Cure (1917) - Charlie Chaplin"
  { pattern: /\bCharlie Chaplin\b/i, series: 'charlie-chaplin', priority: 10 },
  { pattern: /\(Chaplin\)/i, series: 'charlie-chaplin', priority: 5 },

  // ========== BUSTER KEATON ==========
  { pattern: /^Buster Keaton\s*[-:—]\s*/i, series: 'buster-keaton' },
  { pattern: /–\s*Buster Keaton\b/i, series: 'buster-keaton' },
  { pattern: /-\s*Buster Keaton\b/i, series: 'buster-keaton' },
  { pattern: /\bBuster Keaton\b/i, series: 'buster-keaton', priority: 10 },

  // ========== FELIX THE CAT ==========
  { pattern: /^Felix\s+the\s+Cat\s*[-:—]\s*/i, series: 'felix' },
  { pattern: /^Felix the Cat/i, series: 'felix' },
  { pattern: /^Felix\s*[-:—]\s*/i, series: 'felix' },
  { pattern: /^Felix\s+(at|in|makes|gets|saves|turns|finds|minds|the)/i, series: 'felix' },
  { pattern: /^Feline Follies/i, series: 'felix' }, // First Felix cartoon
  { pattern: /\bFelix the Cat\b/i, series: 'felix', priority: 10 },

  // ========== KIRBY ==========
  { pattern: /^Kirby\s*[-:—]\s*/i, series: 'kirby' },
  { pattern: /Kirby Abridged/i, series: 'kirby', isMarathon: true },
  { pattern: /\bKirby\b/i, series: 'kirby', priority: 10 },

  // ========== THE LUCY SHOW ==========
  { pattern: /The Lucy Show/i, series: 'lucy' },
  { pattern: /\bLucy\b/i, series: 'lucy', priority: 5 },

  // ========== MEL-O-TOONS ==========
  { pattern: /Mel-O-Toons/i, series: 'mel-o-toons' },

  // ========== AESOP'S FABLES ==========
  { pattern: /Aesop['']?s Fables/i, series: 'aesop' },

  // ========== KRAZY KAT ==========
  { pattern: /Krazy Kat/i, series: 'krazy-kat' },

  // ========== WINSOR MCCAY ==========
  { pattern: /Winsor McCay/i, series: 'mccay' },
  { pattern: /Gertie the Dinosaur/i, series: 'mccay' },

  // ========== VINTAGE ADS ==========
  { pattern: /Coca-Cola/i, series: 'coca-cola' },
  { pattern: /Vintage (Ad|Commercial)/i, series: 'vintage-ads' },
];

// ============================================================================
// TITLE CLEANING PATTERNS
// ============================================================================

const CLEAN_PATTERNS = [
  // Replace underscores with spaces FIRST (so other patterns can match)
  { pattern: /_/g, replace: ' ' },
  // Remove year patterns like _1933_ or 1933 in the middle
  { pattern: /\s19[0-6]\d\s/g, replace: ' ' },
  { pattern: /\s19[0-6]\d$/g, replace: '' },
  // Remove resolution markers
  { pattern: /\b(4K|8K|HD|HQ|FHD|UHD|1080p?|720p?|480p?|360p?)\b/gi, replace: '' },
  // Remove quality markers (sls = Source Lacking Sound, common marker)
  {
    pattern: /\b(Remaster(ed)?|Restored|Colorized|Watermarked?|sls|Public\s*Domain)\b/gi,
    replace: '',
  },
  // Remove channel-specific branding
  { pattern: /\breAImaster(ed|ing)?\b/gi, replace: '' }, // @reAImastered channel
  { pattern: /\bremAIke(_IT)?\b/gi, replace: '' }, // @remAIke_IT channel
  { pattern: /\bEdition\b/gi, replace: '' },
  { pattern: /\bChannel\s*Classic\b/gi, replace: '' },
  { pattern: /\bClassic\s*Cartoon\b/gi, replace: '' },
  { pattern: /\bVintage\s*Cartoon\b/gi, replace: '' },
  // Remove YouTube channel tags and handles
  { pattern: /@\w+/g, replace: '' },
  { pattern: /\|.*$/g, replace: '' }, // Remove everything after pipe
  { pattern: /–\s*Best.*/gi, replace: '' }, // "– Best Online Version"
  { pattern: /-\s*Best.*/gi, replace: '' }, // "- Best Online Version"
  // Remove common suffixes
  { pattern: /\bBest Online Version\b/gi, replace: '' },
  { pattern: /\bThis is the version you deserve\b/gi, replace: '' },
  // Remove file extensions
  { pattern: /\.(mp4|mkv|avi|mov|wmv|flv|webm)$/i, replace: '' },
  // Remove bracketed metadata at end
  { pattern: /\s*\[.*?\]\s*$/g, replace: '' },
];

// ============================================================================
// YEAR EXTRACTION
// ============================================================================

/**
 * Extract year from title/filename
 * Priority: (YYYY) pattern > standalone 4-digit year in valid range
 */
function extractYear(text) {
  // Priority 1: Parenthesized year (1900-2030)
  const parenMatch = text.match(/\((\d{4})\)/);
  if (parenMatch) {
    const year = parseInt(parenMatch[1], 10);
    if (year >= 1900 && year <= 2030) {
      return { year, pattern: 'parenthesized' };
    }
  }

  // Priority 2: Year after dash like "- 1942" or "– 1942"
  const dashYearMatch = text.match(/[-–—]\s*(19\d{2}|20[0-2]\d)/);
  if (dashYearMatch) {
    const year = parseInt(dashYearMatch[1], 10);
    if (year >= 1900 && year <= 2030) {
      return { year, pattern: 'dash-year' };
    }
  }

  // Priority 3: Standalone year in text (extended range 1900-2000)
  // Match years with underscore prefix/suffix too (e.g., _1933_)
  const yearMatches = text.match(/\b(19\d{2}|20[0-2]\d)\b/g);
  if (yearMatches) {
    // Extract just the year digits
    const years = yearMatches
      .map((y) => parseInt(y, 10))
      .filter((y) => y >= 1900 && y <= 2000)
      .sort((a, b) => a - b);
    if (years.length > 0) {
      return { year: years[0], pattern: 'standalone' };
    }
  }

  return { year: null, pattern: null };
}

// ============================================================================
// TITLE CLEANING
// ============================================================================

/**
 * Clean title by removing noise tokens
 */
function cleanTitle(title) {
  let cleaned = title;

  // Apply all cleaning patterns
  for (const { pattern, replace } of CLEAN_PATTERNS) {
    cleaned = cleaned.replace(pattern, replace);
  }

  // Remove year patterns
  cleaned = cleaned.replace(/\(\d{4}\)/g, '');
  cleaned = cleaned.replace(/\b19[0-6]\d\b/g, '');

  // Normalize whitespace (but keep spaces!)
  cleaned = cleaned.replace(/\s+/g, ' ').trim();

  return cleaned;
}

/**
 * Normalize string for comparison
 */
function normalize(str) {
  return str
    .toLowerCase()
    .replace(/['']/g, "'")
    .replace(/[""]/g, '"')
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// ============================================================================
// SERIES DETECTION
// ============================================================================

/**
 * Detect series from title/filename
 * Returns { seriesId, preformatted, episodeNumber, episodeTotal } if preformatted
 */
function detectSeries(title) {
  // Sort patterns by priority (lower = higher priority)
  const sorted = [...SERIES_PATTERNS].sort((a, b) => (a.priority || 0) - (b.priority || 0));

  for (const { pattern, series, preformatted } of sorted) {
    if (pattern.test(title)) {
      // Check if it's a preformatted title like "Casper (24/55) Episode Title"
      if (preformatted) {
        const episodeMatch = title.match(/\((\d+)\/(\d+)\)/);
        if (episodeMatch) {
          return {
            seriesId: series,
            preformatted: true,
            episodeNumber: parseInt(episodeMatch[1], 10),
            episodeTotal: parseInt(episodeMatch[2], 10),
          };
        }
      }
      return { seriesId: series, preformatted: false };
    }
  }

  return { seriesId: null, preformatted: false };
}

/**
 * Extract episode title from full title (remove series prefix)
 */
function extractEpisodeTitle(fullTitle, seriesId, preformatted = false) {
  let episodeTitle = fullTitle;

  // Handle preformatted titles: "Casper (24/55) Boo Moon (1954)"
  if (preformatted) {
    // Remove "Series (N/M)" prefix and any following separator
    episodeTitle = episodeTitle.replace(/^\w+(?:\s+\w+)?\s*\(\d+\/\d+\)\s*[-—:]?\s*/i, '');
    return cleanTitle(episodeTitle);
  }

  // Remove common series prefixes (including without separator, em-dash —)
  // Also handles "Title (Year) – Artist Name" suffix patterns
  // Unicode dashes: \u2013 (–) en-dash, \u2014 (—) em-dash
  const DASH = '[-:\u2013\u2014]'; // Regular dash, colon, en-dash, em-dash
  const prefixPatterns = {
    casper: [
      new RegExp(`^Casper\\s*${DASH}\\s*`, 'i'), // "Casper – Title"
      new RegExp(`^Casper the Friendly Ghost\\s*${DASH}\\s*`, 'i'),
    ],
    superman: [
      new RegExp(`^Superman\\s*${DASH}\\s*`, 'i'), // "Superman – Title" or "Superman: Title"
      new RegExp(`^Superman\\s*#?\\d+\\s*${DASH}?\\s*`, 'i'),
      /^Superman\s+The\s+/i,
      // Max Fleischer's Superman patterns - handle various apostrophe forms
      new RegExp(`^Max Fleischer[''\u2019]?s?\\s*Superman\\s*${DASH}?\\s*`, 'i'),
      new RegExp(`^8k\\s*Max Fleischer[''\u2019]?s?\\s*Superman\\s*${DASH}?\\s*`, 'i'),
      // Catch-all: any prefix ending with Superman: or Superman –
      /^.*?\bSuperman\s*[:–—-]\s*/i,
    ],
    popeye: [
      new RegExp(`^Popeye\\s*${DASH}\\s+`, 'i'), // "Popeye – Title" (needs separator)
      new RegExp(`^Popeye the Sailor\\s*${DASH}\\s+`, 'i'), // "Popeye the Sailor – Title"
    ],
    'betty-boop': [
      new RegExp(`^Betty Boop\\s*${DASH}\\s+`, 'i'), // "Betty Boop – Title"
      new RegExp(`^Betty Boop['']?s?\\s+`, 'i'), // "Betty Boop's Title" or "Betty Boop Title"
    ],
    'charlie-chaplin': [
      new RegExp(`^Charlie Chaplin\\s*${DASH}\\s*`, 'i'),
      new RegExp(`^Chaplin\\s*${DASH}\\s*`, 'i'),
      /^Charlie Chaplin Film Fest.*/i,
      new RegExp(`\\s*${DASH}\\s*Charlie Chaplin\\b.*`, 'i'), // Remove "– Charlie Chaplin" suffix
    ],
    'buster-keaton': [
      new RegExp(`^Buster Keaton\\s*${DASH}\\s*`, 'i'),
      new RegExp(`\\s*${DASH}\\s*Buster Keaton\\b.*`, 'i'), // Remove "– Buster Keaton" suffix
    ],
    felix: [
      new RegExp(`^Felix the Cat\\s*${DASH}\\s*`, 'i'), // "Felix the Cat – Title"
      new RegExp(`^Felix\\s*${DASH}\\s*`, 'i'), // "Felix – Title"
      // DON'T strip "Felix at/in/makes..." - let the full title through for matching
      // Remove trailing "Felix the Cat" suffix for titles like "Feline Follies | Felix the Cat"
      /\s*\|?\s*Felix the Cat\s*$/i,
    ],
  };

  const patterns = prefixPatterns[seriesId] || [];
  for (const pattern of patterns) {
    episodeTitle = episodeTitle.replace(pattern, '');
  }

  return cleanTitle(episodeTitle);
}

// ============================================================================
// FUZZY MATCHING (Levenshtein Distance)
// ============================================================================

/**
 * Calculate Levenshtein distance between two strings
 */
function levenshtein(a, b) {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  const matrix = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1, // insertion
          matrix[i - 1][j] + 1 // deletion
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Calculate similarity ratio (0-1)
 */
function similarity(a, b) {
  const normA = normalize(a);
  const normB = normalize(b);
  const distance = levenshtein(normA, normB);
  const maxLen = Math.max(normA.length, normB.length);
  if (maxLen === 0) return 1;
  return 1 - distance / maxLen;
}

/**
 * Token set ratio for fuzzy matching
 * Compares shared tokens between strings
 */
function tokenSetRatio(a, b) {
  const tokensA = new Set(normalize(a).split(' ').filter(Boolean));
  const tokensB = new Set(normalize(b).split(' ').filter(Boolean));

  const intersection = new Set([...tokensA].filter((x) => tokensB.has(x)));
  const union = new Set([...tokensA, ...tokensB]);

  if (union.size === 0) return 0;
  return intersection.size / union.size;
}

// ============================================================================
// EPISODE MATCHING
// ============================================================================

let canonicalData = null;

/**
 * Load canonical episode data
 */
function loadCanonical() {
  if (canonicalData) return canonicalData;

  const canonicalPath = join(__dirname, '../public/data/series/canonical.json');
  if (!existsSync(canonicalPath)) {
    console.warn('⚠️ Canonical series data not found:', canonicalPath);
    return {};
  }

  canonicalData = JSON.parse(readFileSync(canonicalPath, 'utf-8'));
  return canonicalData;
}

/**
 * Match episode against canonical list
 *
 * @param {string} episodeTitle - Cleaned episode title
 * @param {string} seriesId - Series identifier
 * @param {number|null} year - Year hint (optional)
 * @returns {object|null} Match result with episode number, total, confidence
 */
function matchEpisode(episodeTitle, seriesId, year = null) {
  const canonical = loadCanonical();
  const series = canonical[seriesId];

  if (!series || !series.episodes) {
    return null;
  }

  const normalizedInput = normalize(episodeTitle);
  const episodes = series.episodes;

  // Strategy 1: Exact normalized title match
  for (const ep of episodes) {
    if (normalize(ep.title) === normalizedInput) {
      return {
        match: 'exact',
        confidence: 1.0,
        episode: ep,
        n: ep.n,
        total: series.total,
        series: series.name,
      };
    }
  }

  // Strategy 2: Alias match
  for (const ep of episodes) {
    for (const alias of ep.aliases || []) {
      if (normalize(alias) === normalizedInput) {
        return {
          match: 'alias',
          confidence: 0.95,
          episode: ep,
          n: ep.n,
          total: series.total,
          series: series.name,
        };
      }
    }
  }

  // Strategy 3: Fuzzy match
  let bestMatch = null;
  let bestScore = 0;
  const FUZZY_THRESHOLD = 0.7;

  for (const ep of episodes) {
    // Check title
    const titleSim = similarity(episodeTitle, ep.title);
    const tokenSim = tokenSetRatio(episodeTitle, ep.title);
    const combinedScore = titleSim * 0.6 + tokenSim * 0.4;

    // Year bonus
    let yearBonus = 0;
    if (year && ep.year === year) {
      yearBonus = 0.1;
    }

    const finalScore = combinedScore + yearBonus;

    if (finalScore > bestScore && finalScore >= FUZZY_THRESHOLD) {
      bestScore = finalScore;
      bestMatch = ep;
    }

    // Also check aliases
    for (const alias of ep.aliases || []) {
      const aliasSim = similarity(episodeTitle, alias);
      const aliasTokenSim = tokenSetRatio(episodeTitle, alias);
      const aliasScore = aliasSim * 0.6 + aliasTokenSim * 0.4 + yearBonus;

      if (aliasScore > bestScore && aliasScore >= FUZZY_THRESHOLD) {
        bestScore = aliasScore;
        bestMatch = ep;
      }
    }
  }

  if (bestMatch) {
    return {
      match: 'fuzzy',
      confidence: bestScore,
      episode: bestMatch,
      n: bestMatch.n,
      total: series.total,
      series: series.name,
    };
  }

  return null;
}

// ============================================================================
// TITLE & DESCRIPTION TEMPLATES
// ============================================================================

const TEMPLATES = {
  casper: {
    title: '{episodeTitle} ({year}) | Casper #{n}/{total}',
    description: `🎬 Casper the Friendly Ghost - Episode #{n}: "{episodeTitle}" ({year})

This classic cartoon from Famous Studios / Paramount features everyone's favorite friendly ghost in another heartwarming adventure!

📺 Part of the original Casper the Friendly Ghost series (1945-1959)
🎞️ Episode {n} of {total}
⭐ Public Domain Classic

#Casper #ClassicCartoons #PublicDomain #VintageAnimation #1950s`,
  },

  superman: {
    title: '{episodeTitle} ({year}) | Superman #{n}/{total} (Fleischer)',
    description: `🦸 Superman - Episode #{n}: "{episodeTitle}" ({year})

This groundbreaking animated short from Fleischer/Famous Studios set the standard for superhero animation!

📺 Superman Theatrical Cartoons (1941-1943)
🎞️ Episode {n} of {total}
🎨 Animation pioneers: Fleischer Studios
⭐ Public Domain Classic

#Superman #FleischerStudios #ClassicAnimation #PublicDomain #1940s`,
  },

  popeye: {
    title: '{episodeTitle} ({year}) | Popeye #{n}',
    description: `🥬 Popeye the Sailor - "{episodeTitle}" ({year})

I'm strong to the finich, 'cause I eats me spinach! Classic Popeye cartoon from Fleischer/Famous Studios.

📺 Popeye the Sailor (1933-1957)
🎞️ Episode {n}
🎨 Fleischer Studios / Famous Studios
⭐ Public Domain Classic

#Popeye #ClassicCartoons #Fleischer #PublicDomain #VintageAnimation`,
  },

  'betty-boop': {
    title: '{episodeTitle} ({year}) | Betty Boop #{n}',
    description: `💋 Betty Boop - "{episodeTitle}" ({year})

Boop-Oop-A-Doop! Classic Betty Boop cartoon from the golden age of animation.

📺 Betty Boop Series (1930-1939)
🎞️ Episode {n}
🎨 Fleischer Studios
⭐ Public Domain Classic

#BettyBoop #ClassicCartoons #Fleischer #PublicDomain #1930s`,
  },

  'charlie-chaplin': {
    title: '{episodeTitle} ({year}) | Charlie Chaplin',
    description: `🎩 Charlie Chaplin - "{episodeTitle}" ({year})

Silent comedy gold from the legendary Charlie Chaplin, featuring his iconic "Little Tramp" character.

📺 Charlie Chaplin Shorts ({year})
🎬 Silent Film Era Classic
⭐ Public Domain Classic

#CharlieChaplin #SilentFilm #ClassicComedy #PublicDomain #LittleTramp`,
  },

  felix: {
    title: '{episodeTitle} ({year}) | Felix the Cat #{n}',
    description: `🐱 Felix the Cat - "{episodeTitle}" ({year})

One of animation's first superstars! Felix the Cat brought joy to millions in the silent era and beyond.

📺 Felix the Cat (1919-1936)
🎞️ Episode {n}
🎨 Pat Sullivan Studios
⭐ Public Domain Classic

#FelixTheCat #ClassicCartoons #SilentAnimation #PublicDomain #1920s`,
  },

  'buster-keaton': {
    title: '{episodeTitle} ({year}) | Buster Keaton',
    description: `🎭 Buster Keaton - "{episodeTitle}" ({year})

"The Great Stone Face" delivers physical comedy genius in this silent film classic.

📺 Buster Keaton Shorts (1920-1923)
🎬 Silent Comedy Master
⭐ Public Domain Classic

#BusterKeaton #SilentFilm #ClassicComedy #PublicDomain #PhysicalComedy`,
  },

  default: {
    title: '{title} ({year})',
    description: `🎬 {title} ({year})

Classic public domain film restored for modern viewing.

⭐ Public Domain Classic

#ClassicFilm #PublicDomain #VintageHollywood`,
  },
};

/**
 * Render title using template
 */
function renderTitle(template, data) {
  let result = template;
  for (const [key, value] of Object.entries(data)) {
    result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value ?? '');
  }
  return result;
}

/**
 * Render description using template
 */
function renderDescription(template, data) {
  return renderTitle(template, data);
}

// ============================================================================
// MAIN PROCESSING FUNCTION
// ============================================================================

/**
 * Process video title and extract series/episode metadata
 *
 * @param {string} title - Original video title
 * @param {string} description - Original description (for hints)
 * @returns {object} Enriched metadata
 */
export function processVideoTitle(title, description = '') {
  // Step 1: Detect series (now returns object with potential preformatted episode info)
  const detection = detectSeries(title);
  const seriesId = detection.seriesId;

  // Step 2: Extract year
  const { year } = extractYear(title);

  // Step 3: Clean and extract episode title
  const episodeTitle = seriesId
    ? extractEpisodeTitle(title, seriesId, detection.preformatted)
    : cleanTitle(title);

  // Step 4: Match episode
  let matchResult = null;

  // If preformatted, we already have episode info - just need to look up the series data
  if (detection.preformatted && detection.episodeNumber) {
    const canonical = loadCanonical();
    const canonicalSeries = canonical?.[seriesId];
    if (canonicalSeries) {
      const episode = canonicalSeries.episodes?.find((e) => e.n === detection.episodeNumber);
      matchResult = {
        match: 'preformatted',
        confidence: 1,
        n: detection.episodeNumber,
        total: detection.episodeTotal || canonicalSeries.total,
        series: canonicalSeries.name,
        episode: episode || { title: episodeTitle, n: detection.episodeNumber, year },
      };
    }
  } else if (seriesId) {
    // Regular matching against canonical list
    matchResult = matchEpisode(episodeTitle, seriesId, year);
  }

  // Step 5: Build result
  const result = {
    originalTitle: title,
    cleanedTitle: episodeTitle,
    seriesId,
    year: matchResult?.episode?.year || year,
    episodeNumber: matchResult?.n || null,
    episodeTotal: matchResult?.total || null,
    seriesName: matchResult?.series || null,
    matchConfidence: matchResult?.confidence || 0,
    matchType: matchResult?.match || null,
  };

  // Step 6: Generate formatted title & description
  const templateData = {
    title: episodeTitle,
    episodeTitle: matchResult?.episode?.title || episodeTitle,
    year: result.year || 'Unknown',
    n: result.episodeNumber,
    total: result.episodeTotal,
  };

  const templates = seriesId ? TEMPLATES[seriesId] : TEMPLATES.default;
  if (templates) {
    result.formattedTitle = renderTitle(templates.title, templateData);
    result.formattedDescription = renderDescription(templates.description, templateData);
  }

  return result;
}

// ============================================================================
// EXPORTS
// ============================================================================

export {
  detectSeries,
  extractYear,
  cleanTitle,
  extractEpisodeTitle,
  matchEpisode,
  similarity,
  tokenSetRatio,
  loadCanonical,
  TEMPLATES,
};

// CLI test if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const testTitles = [
    'Casper - The Friendly Ghost (1945)',
    "Casper - There's Good Boos To-Night (1948) HQ",
    'Superman - The Mechanical Monsters (1941) 4K Remastered',
    'Popeye - I Eats My Spinach_1933_sls_Watermarked',
    'Betty Boop - Minnie the Moocher (1932)',
    'Charlie Chaplin - The Tramp (1915)',
    'Unknown Movie Title (1940)',
  ];

  console.log('🎬 Series Detection & Episode Matching Test\n');

  for (const title of testTitles) {
    console.log('─'.repeat(60));
    console.log(`Input: ${title}`);
    const result = processVideoTitle(title);
    console.log(`Series: ${result.seriesId || 'none'}`);
    console.log(`Episode: ${result.episodeNumber || 'n/a'}/${result.episodeTotal || 'n/a'}`);
    console.log(`Year: ${result.year || 'unknown'}`);
    console.log(`Match: ${result.matchType} (${(result.matchConfidence * 100).toFixed(0)}%)`);
    console.log(`Formatted: ${result.formattedTitle || result.cleanedTitle}`);
    console.log('');
  }
}
