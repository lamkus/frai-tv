/**
 * remAIke.TV - Video Data & Taxonomy
 *
 * Kategorie-System für restaurierte/remastered klassische Filme
 * YouTube Kanal: @remAIke_IT
 *
 * Content-Typen:
 * - Klassische Filme (Public Domain)
 * - Cartoons & Animationen
 * - Dokumentationen & Newsreels
 * - Werbung & Propaganda
 * - Silent Films
 */

// ============================================================================
// CHANNEL CONFIGURATION
// ============================================================================

export const CHANNEL_CONFIG = {
  channelId: 'UCVFv6Egpl0LDvigpFbQXNeQ',
  channelHandle: '@remAIke_IT',
  channelName: 'remAIke IT',
  channelUrl: 'https://www.youtube.com/@remAIke_IT',
  description:
    'Klassische Filme & Cartoons, restauriert in 4K & 8K. Public Domain Schätze neu aufbereitet.',
  language: 'de',
};

// ============================================================================
// DECADE TAXONOMY
// ============================================================================

export const DECADES = [
  {
    id: '1900s',
    label: '1900er',
    range: [1900, 1909],
    icon: '🎬',
    color: 'sepia',
    description: 'Die Geburt des Kinos',
  },
  {
    id: '1910s',
    label: '1910er',
    range: [1910, 1919],
    icon: '🎭',
    color: 'amber',
    description: 'Stummfilm-Ära beginnt',
  },
  {
    id: '1920s',
    label: '1920er',
    range: [1920, 1929],
    icon: '📽️',
    color: 'orange',
    description: 'Goldene Stummfilm-Ära',
  },
  {
    id: '1930s',
    label: '1930er',
    range: [1930, 1939],
    icon: '🎤',
    color: 'gold',
    description: 'Tonfilm-Revolution',
  },
  {
    id: '1940s',
    label: '1940er',
    range: [1940, 1949],
    icon: '✈️',
    color: 'olive',
    description: 'Kriegszeit & Film Noir',
  },
  {
    id: '1950s',
    label: '1950er',
    range: [1950, 1959],
    icon: '📺',
    color: 'cyan',
    description: 'TV-Ära & Technicolor',
  },
  {
    id: '1960s',
    label: '1960er',
    range: [1960, 1969],
    icon: '🚀',
    color: 'purple',
    description: 'Pop Culture & TV Shows',
  },
  {
    id: '1970s',
    label: '1970er',
    range: [1970, 1979],
    icon: '🕺',
    color: 'indigo',
    description: 'New Hollywood & Disco',
  },
  {
    id: '1980s',
    label: '1980er',
    range: [1980, 1989],
    icon: '📼',
    color: 'pink',
    description: 'VHS & TV Movies',
  },
  {
    id: '1990s',
    label: '1990er',
    range: [1990, 1999],
    icon: '🎄',
    color: 'red',
    description: 'Ikonische Werbung',
  },
];

// ============================================================================
// CATEGORY TAXONOMY - Für Film-Content
// ============================================================================

export const CATEGORIES = [
  {
    id: 'classic-films',
    label: 'Klassische Filme',
    icon: '🎬',
    color: 'gold',
    hex: '#d4af37',
    subcategories: [
      { id: 'silent-films', label: 'Stummfilme' },
      { id: 'film-noir', label: 'Film Noir' },
      { id: 'horror', label: 'Horror Klassiker' },
      { id: 'adventure', label: 'Abenteuer' },
      { id: 'drama', label: 'Drama' },
    ],
  },
  {
    id: 'cartoons',
    label: 'Cartoons & Animation',
    icon: '🎨',
    color: 'red',
    hex: '#e50914',
    subcategories: [
      { id: 'fleischer', label: 'Fleischer Studios' },
      { id: 'disney', label: 'Disney Classics' },
      { id: 'superman', label: 'Superman' },
      { id: 'popeye', label: 'Popeye' },
      { id: 'betty-boop', label: 'Betty Boop' },
      { id: 'casper', label: 'Casper' },
    ],
  },
  {
    id: 'documentaries',
    label: 'Dokumentationen',
    icon: '📽️',
    color: 'blue',
    hex: '#2979ff',
    subcategories: [
      { id: 'newsreels', label: 'Newsreels & Wochenschau' },
      { id: 'historical', label: 'Historisch' },
      { id: 'science', label: 'Wissenschaft' },
      { id: 'travelogues', label: 'Reisefilme' },
    ],
  },
  {
    id: 'propaganda',
    label: 'Propaganda & Zeitdokumente',
    icon: '📜',
    color: 'olive',
    hex: '#8b8b00',
    subcategories: [
      { id: 'wwii', label: 'WWII' },
      { id: 'cold-war', label: 'Kalter Krieg' },
      { id: 'civil-defense', label: 'Civil Defense' },
    ],
  },
  {
    id: 'comedy',
    label: 'Comedy & Sketche',
    icon: '😂',
    color: 'yellow',
    hex: '#ffd600',
    subcategories: [
      { id: 'chaplin', label: 'Charlie Chaplin' },
      { id: 'keaton', label: 'Buster Keaton' },
      { id: 'lucy', label: 'Lucille Ball' },
      { id: 'sketch', label: 'TV Sketche' },
    ],
  },
  {
    id: 'christmas',
    label: 'Weihnachts-Specials',
    icon: '🎄',
    color: 'green',
    hex: '#00c853',
    subcategories: [
      { id: 'movies', label: 'Weihnachtsfilme' },
      { id: 'cartoons', label: 'Weihnachts-Cartoons' },
      { id: 'commercials', label: 'Weihnachtswerbung' },
    ],
  },
  {
    id: 'commercials',
    label: 'Werbung & Commercials',
    icon: '📺',
    color: 'orange',
    hex: '#ff9100',
    subcategories: [
      { id: 'coca-cola', label: 'Coca-Cola' },
      { id: 'vintage-ads', label: 'Vintage Werbung' },
    ],
  },
];

// ============================================================================
// CONTENT TYPES
// ============================================================================

export const CONTENT_TYPES = [
  { id: 'feature-film', label: 'Spielfilm', icon: '🎬', color: 'gold' },
  { id: 'short-film', label: 'Kurzfilm', icon: '🎞️', color: 'silver' },
  { id: 'cartoon', label: 'Cartoon', icon: '🎨', color: 'red' },
  { id: 'documentary', label: 'Dokumentation', icon: '📽️', color: 'blue' },
  { id: 'newsreel', label: 'Newsreel', icon: '📰', color: 'gray' },
  { id: 'commercial', label: 'Werbung', icon: '📺', color: 'orange' },
  { id: 'tv-episode', label: 'TV Episode', icon: '📺', color: 'purple' },
];

// ============================================================================
// MILESTONE TYPES - Kept for compatibility
// ============================================================================

export const MILESTONE_TYPES = [
  { id: 'world-first', label: 'World Firsts', icon: '🏆', color: 'gold' },
  { id: 'iconic-moment', label: 'Iconic Moments', icon: '⭐', color: 'amber' },
  { id: 'documentary', label: 'Dokumentationen', icon: '🎬', color: 'red' },
];

// ============================================================================
// ECHTE VIDEOS VOM @remAIke_IT KANAL
// Manuell kategorisiert basierend auf Titel & Beschreibung
// ============================================================================

export const remaikeVideos = [
  // === CHRISTMAS 2025 SPECIALS ===
  {
    id: 'rudolph-1948',
    ytId: 'YzvGVo8mAQM',
    title: 'Rudolph the Red-Nosed Reindeer (1948) | 8K',
    description: 'Der klassische Max Fleischer Weihnachts-Cartoon in 8K restauriert.',
    year: 1948,
    decade: '1940s',
    category: 'christmas',
    subcategory: 'cartoons',
    tags: ['weihnachten', 'rudolph', 'fleischer', 'cartoon', 'christmas'],
    duration: 480,
  },
  {
    id: 'suzy-snowflake-1953',
    ytId: 'Z4nwcfOqOOw',
    title: 'Suzy Snowflake (1953) | 8K',
    description: 'Charmante Stop-Motion Weihnachts-Kurzfilm aus den 50ern.',
    year: 1953,
    decade: '1950s',
    category: 'christmas',
    subcategory: 'cartoons',
    tags: ['weihnachten', 'stop-motion', 'christmas', 'winter'],
    duration: 300,
  },
  {
    id: 'coca-cola-trucks-1995',
    ytId: 'U-WD47NSgAE',
    title: 'Coca-Cola Christmas Trucks – Holidays Are Coming (1995) | 4K',
    description: 'Der ikonische Coca-Cola Weihnachts-Werbespot.',
    year: 1995,
    decade: '1990s',
    category: 'commercials',
    subcategory: 'coca-cola',
    tags: ['coca-cola', 'weihnachten', 'werbung', 'christmas', 'trucks'],
    duration: 60,
  },
  {
    id: 'coca-cola-trucks-8k',
    ytId: 'WSjkAZkPbKs',
    title: 'EPIC Coca-Cola Christmas Trucks (1995) | 8K',
    description: 'Coca-Cola Weihnachts-Trucks in epischer 8K Qualität.',
    year: 1995,
    decade: '1990s',
    category: 'commercials',
    subcategory: 'coca-cola',
    tags: ['coca-cola', 'weihnachten', 'werbung', 'christmas'],
    duration: 60,
  },
  {
    id: 'batman-santa-1966',
    ytId: 'yIQCHpjp4NE',
    title: 'Merry Christmas from Batman & Robin Meet Santa Claus (1966) | 8K',
    description: 'Klassische 60er Jahre Batman TV-Weihnachtsfolge.',
    year: 1966,
    decade: '1960s',
    category: 'christmas',
    subcategory: 'movies',
    tags: ['batman', 'robin', 'weihnachten', 'tv', '60s', 'santa'],
    duration: 1500,
  },
  {
    id: 'christmas-carol-1984',
    ytId: 'dGD2CeoZX68',
    title: 'A Christmas Carol (1984) George C. Scott | 8K',
    description: 'Die gefeierte Verfilmung von Dickens Weihnachtsgeschichte.',
    year: 1984,
    decade: '1980s',
    category: 'christmas',
    subcategory: 'movies',
    tags: ['dickens', 'weihnachten', 'scrooge', 'george c. scott', 'christmas'],
    duration: 6000,
  },
  {
    id: 'casper-christmas',
    ytId: 'uWacVV7EkxQ',
    title: 'Casper the Friendly Ghost – Christmas Cartoon Special | 8K',
    description: 'Casper Weihnachts-Cartoon-Special in 8K.',
    year: 1950,
    decade: '1950s',
    category: 'christmas',
    subcategory: 'cartoons',
    tags: ['casper', 'weihnachten', 'ghost', 'cartoon', 'christmas'],
    duration: 420,
  },

  // === CLASSIC FILMS ===
  {
    id: 'great-expectations-1946',
    ytId: 'JhJmasQ8N-8',
    title: 'Great Expectations (1946) – David Lean | 8K',
    description: 'David Leans gefeierte Dickens-Verfilmung in 8K restauriert.',
    year: 1946,
    decade: '1940s',
    category: 'classic-films',
    subcategory: 'drama',
    tags: ['david lean', 'dickens', 'british', 'drama', 'classic'],
    duration: 7200,
  },
  {
    id: 'scarlet-street-1945',
    ytId: '_aUNgDJoWoU',
    title: 'Scarlet Street (1945) – Fritz Lang | 8K',
    description: 'Fritz Langs dunkler Film Noir Klassiker.',
    year: 1945,
    decade: '1940s',
    category: 'classic-films',
    subcategory: 'film-noir',
    tags: ['fritz lang', 'film noir', 'crime', 'classic'],
    duration: 6300,
  },
  {
    id: 'metropolis-1927',
    ytId: '8lLtNb11NKU',
    title: 'Metropolis (1927) – Fritz Lang | 4K 8K',
    description: 'Fritz Langs bahnbrechendes Sci-Fi Meisterwerk.',
    year: 1927,
    decade: '1920s',
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['fritz lang', 'sci-fi', 'stummfilm', 'expressionism', 'classic'],
    duration: 9000,
  },
  {
    id: 'phantom-opera-1925',
    ytId: 'b4cqLlJ7t4M',
    title: 'The Phantom of the Opera (1925) – Lon Chaney | 8K',
    description: 'Der ikonische Stummfilm-Horror mit Lon Chaney.',
    year: 1925,
    decade: '1920s',
    category: 'classic-films',
    subcategory: 'horror',
    tags: ['lon chaney', 'horror', 'stummfilm', 'phantom', 'classic'],
    duration: 5400,
  },
  {
    id: 'nosferatu-1922',
    ytId: 'Nzi6aRKDoEs',
    title: 'Nosferatu (1922) | 8K',
    description: 'F.W. Murnaus legendärer Vampirfilm.',
    year: 1922,
    decade: '1920s',
    category: 'classic-films',
    subcategory: 'horror',
    tags: ['murnau', 'horror', 'vampire', 'stummfilm', 'expressionism'],
    duration: 5400,
  },
  {
    id: 'tarzan-revenge-1938',
    ytId: 'cCNm8nNHing',
    title: "Tarzan's Revenge (1938) | 8K",
    description: 'Vintage Dschungel-Abenteuer aus den 30ern.',
    year: 1938,
    decade: '1930s',
    category: 'classic-films',
    subcategory: 'adventure',
    tags: ['tarzan', 'adventure', 'jungle', '30s'],
    duration: 4200,
  },
  {
    id: '20000-leagues-1916',
    ytId: 'LEM6FkBTDNs',
    title: '20,000 Leagues Under the Sea (1916) | 8K',
    description: 'Der bahnbrechende Stummfilm-Abenteuerfilm nach Jules Verne.',
    year: 1916,
    decade: '1910s',
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['jules verne', 'adventure', 'submarine', 'stummfilm'],
    duration: 6300,
  },
  {
    id: 'haxan-1922',
    ytId: 'exukLdxugy8',
    title: 'Häxan (1922) – Witchcraft Through the Ages | 8K',
    description: 'Legendärer schwedisch-dänischer Stummfilm über Hexerei.',
    year: 1922,
    decade: '1920s',
    category: 'classic-films',
    subcategory: 'horror',
    tags: ['horror', 'witchcraft', 'swedish', 'documentary', 'stummfilm'],
    duration: 6600,
  },
  {
    id: 'frankenstein-1910',
    ytId: 'hPQN992PMUY',
    title: 'Frankenstein (1910) | 8K',
    description: 'Die erste Verfilmung von Mary Shelleys Geschichte - Edison Studios.',
    year: 1910,
    decade: '1910s',
    category: 'classic-films',
    subcategory: 'horror',
    tags: ['frankenstein', 'edison', 'horror', 'stummfilm', 'first'],
    duration: 780,
  },
  {
    id: 'voyage-prehistoric-1968',
    ytId: 'pqrCPhUCpxE',
    title: 'Voyage to the Planet of Prehistoric Women (1968) | 8K',
    description: 'Kultiger 60er Jahre Sci-Fi Film.',
    year: 1968,
    decade: '1960s',
    category: 'classic-films',
    subcategory: 'adventure',
    tags: ['sci-fi', '60s', 'cult', 'space'],
    duration: 4800,
  },
  {
    id: 'bill-divorcement-1932',
    ytId: 'YbC2JynVCRA',
    title: 'A Bill of Divorcement (1932) – Barrymore & Katharine Hepburn | 8K',
    description: 'George Cukors Drama mit John Barrymore und Katharine Hepburn.',
    year: 1932,
    decade: '1930s',
    category: 'classic-films',
    subcategory: 'drama',
    tags: ['katharine hepburn', 'barrymore', 'drama', '30s'],
    duration: 4200,
  },

  // === COMEDY ===
  {
    id: 'dinner-for-one-1963',
    ytId: 'z8FqTSpp6Kg',
    title: 'Dinner for One (1963) | 4K 8K',
    description: 'Der legendäre Silvester-Sketch.',
    year: 1963,
    decade: '1960s',
    category: 'comedy',
    subcategory: 'sketch',
    tags: ['silvester', 'comedy', 'british', 'classic', 'new year'],
    duration: 1080,
  },
  {
    id: 'chaplin-film-fest',
    ytId: 'FG-vqRH5Cg4',
    title: 'Charlie Chaplin Film Fest | 8K',
    description: 'Stummfilm-Comedy Marathon mit Charlie Chaplin.',
    year: 1917,
    decade: '1910s',
    category: 'comedy',
    subcategory: 'chaplin',
    tags: ['chaplin', 'comedy', 'stummfilm', 'marathon', 'silent'],
    duration: 5400,
  },
  {
    id: 'chaplin-cure-1917',
    ytId: 'EM076HMwVwI',
    title: 'The Cure (1917) – Charlie Chaplin | 8K',
    description: 'Charlie Chaplins klassischer Stummfilm-Kurzfilm.',
    year: 1917,
    decade: '1910s',
    category: 'comedy',
    subcategory: 'chaplin',
    tags: ['chaplin', 'comedy', 'stummfilm', 'silent'],
    duration: 1500,
  },
  {
    id: 'keaton-convict13-1920',
    ytId: '_3Z1GTYFUAM',
    title: 'Buster Keaton – Convict 13 (1920) | 8K',
    description: 'Buster Keatons präzise Slapstick-Comedy.',
    year: 1920,
    decade: '1920s',
    category: 'comedy',
    subcategory: 'keaton',
    tags: ['keaton', 'comedy', 'stummfilm', 'slapstick'],
    duration: 1200,
  },
  {
    id: 'keaton-wifes-relations-1922',
    ytId: 'mybF4jPjl64',
    title: "Buster Keaton – My Wife's Relations (1922) | 8K",
    description: 'Eine von Keatons cleversten Kurzkomödien.',
    year: 1922,
    decade: '1920s',
    category: 'comedy',
    subcategory: 'keaton',
    tags: ['keaton', 'comedy', 'stummfilm', 'slapstick'],
    duration: 1200,
  },
  {
    id: 'lucy-john-wayne-1966',
    ytId: 'AyjJbgijx68',
    title: 'Lucy Meets John Wayne (1966) | The Lucy Show S5E10 | 8K',
    description: 'Klassische Episode der Lucy Show.',
    year: 1966,
    decade: '1960s',
    category: 'comedy',
    subcategory: 'lucy',
    tags: ['lucy', 'john wayne', 'tv', '60s', 'comedy'],
    duration: 1500,
  },

  // === CARTOONS ===
  {
    id: 'skeleton-dance-1929',
    ytId: 'ezYIk8bReaE',
    title: 'The Skeleton Dance (1929) | 8K',
    description: 'Walt Disneys erste Silly Symphony.',
    year: 1929,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'disney',
    tags: ['disney', 'silly symphony', 'halloween', 'animation'],
    duration: 360,
  },
  {
    id: 'peter-wolf-1960',
    ytId: 'V8qeIRongA0',
    title: 'Mel-O-Toons: Peter and the Wolf (1960) | 8K',
    description: 'Klassischer Cartoon basierend auf Prokofievs Werk.',
    year: 1960,
    decade: '1960s',
    category: 'cartoons',
    subcategory: 'fleischer',
    tags: ['peter and the wolf', 'prokofiev', 'music', 'cartoon'],
    duration: 600,
  },
  {
    id: 'superman-japoteurs-1942',
    ytId: 'bShrsrrzOYQ',
    title: 'Superman: Japoteurs (1942) | 8K',
    description: 'WWII Superman Propaganda-Cartoon.',
    year: 1942,
    decade: '1940s',
    category: 'cartoons',
    subcategory: 'superman',
    tags: ['superman', 'fleischer', 'wwii', 'propaganda'],
    duration: 540,
  },
  {
    id: 'superman-electric-earthquake-1942',
    ytId: 'Aq1OfWdwV-Q',
    title: 'Superman: Electric Earthquake (1942) | 8K',
    description: 'Fleischer Studios Superman Cartoon.',
    year: 1942,
    decade: '1940s',
    category: 'cartoons',
    subcategory: 'superman',
    tags: ['superman', 'fleischer', 'animation'],
    duration: 540,
  },
  {
    id: 'superman-destruction-inc-1943',
    ytId: 'e0Tagj2Z5SU',
    title: "Max Fleischer's Superman: Destruction Inc. (1943) | 8K",
    description: 'Famous Studios Superman WWII Cartoon.',
    year: 1943,
    decade: '1940s',
    category: 'cartoons',
    subcategory: 'superman',
    tags: ['superman', 'famous studios', 'wwii', 'animation'],
    duration: 540,
  },
  {
    id: 'popeye-ancient-fistory-1953',
    ytId: 'unbwEeI4bEE',
    title: 'Popeye the Sailor – Ancient Fistory (1953) | 8K',
    description: 'Popeye im mittelalterlichen Fantasy-Setting.',
    year: 1953,
    decade: '1950s',
    category: 'cartoons',
    subcategory: 'popeye',
    tags: ['popeye', 'famous studios', 'cartoon'],
    duration: 420,
  },
  {
    id: 'popeye-patriotic-1957',
    ytId: 'eeId9wqhtuQ',
    title: 'Patriotic Popeye (1957) | 8K',
    description: 'Popeye feiert den 4. Juli.',
    year: 1957,
    decade: '1950s',
    category: 'cartoons',
    subcategory: 'popeye',
    tags: ['popeye', '4th of july', 'patriotic', 'cartoon'],
    duration: 420,
  },
  {
    id: 'betty-boop-more-pep-1936',
    ytId: 'dkxCgOivonc',
    title: 'Betty Boop – More Pep (1936) | 8K',
    description: 'Betty Boops energiegeladener Kurzfilm.',
    year: 1936,
    decade: '1930s',
    category: 'cartoons',
    subcategory: 'betty-boop',
    tags: ['betty boop', 'fleischer', 'jazz', 'animation'],
    duration: 420,
  },
  {
    id: 'little-nemo-1911',
    ytId: 'T8AnrW3H5i8',
    title: 'Little Nemo (1911) | 8K | World First Animated Film',
    description: 'Winsor McCays historisch erster Animationsfilm.',
    year: 1911,
    decade: '1910s',
    category: 'cartoons',
    subcategory: 'fleischer',
    tags: ['winsor mccay', 'first animation', 'history', 'pioneer'],
    duration: 720,
  },
  {
    id: 'kirby-abridged',
    ytId: 'Qm3K0-XL46Q',
    title: 'Kirby Abridged Collection | 8K',
    description: 'Kirby Anime Parodie-Sammlung.',
    year: 2005,
    decade: '2000s',
    category: 'cartoons',
    subcategory: 'fleischer',
    tags: ['kirby', 'anime', 'parody', 'abridged'],
    duration: 1800,
  },

  // === EARLY CINEMA (1900s) ===
  {
    id: 'cigar-box-1905',
    ytId: 'PySMbbpIAUM',
    title: 'The Cigar Box (1905) | 8K | Segundo de Chomón',
    description: 'Frühe Trick-Kino-Magie von Pathé.',
    year: 1905,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['pathé', 'trick film', 'magic', 'early cinema'],
    duration: 180,
  },
  {
    id: 'golden-beetle-1907',
    ytId: 'IpWrF7DYyWU',
    title: 'The Golden Beetle (1907) | 8K | Ferdinand Zecca',
    description: 'Früher Trick-Kino Juwel von Pathé.',
    year: 1907,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['pathé', 'trick film', 'hand-colored', 'early cinema'],
    duration: 240,
  },
  {
    id: 'frog-1908',
    ytId: 'dfUyhjEnAqw',
    title: 'The Frog (1908) | 8K | Segundo de Chomón',
    description: 'Früher Trick-Film mit Stop-Motion Effekten.',
    year: 1908,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['pathé', 'trick film', 'stop-motion', 'early cinema'],
    duration: 180,
  },
  {
    id: 'bee-rose-1908',
    ytId: 'gMpONbJ3-9U',
    title: 'The Bee and the Rose (1908) | 8K | Segundo de Chomón',
    description: 'Visuell beeindruckender früher Trick-Film.',
    year: 1908,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'silent-films',
    tags: ['pathé', 'trick film', 'hand-crafted', 'early cinema'],
    duration: 180,
  },

  // === DOCUMENTARIES & NEWSREELS ===
  {
    id: 'berlin-symphony-1927',
    ytId: 'DnwDqCsSqRw',
    title: 'Berlin: Symphony of Great City (1927) | 8K',
    description: 'Walter Ruttmanns avantgardistische Stadtsymphonie.',
    year: 1927,
    decade: '1920s',
    category: 'documentaries',
    subcategory: 'historical',
    tags: ['berlin', 'weimar', 'city symphony', 'avantgarde', 'german'],
    duration: 3900,
  },
  {
    id: 'pearl-harbor-1942',
    ytId: 'EasEhYlorqQ',
    title: 'Pearl Harbor (Short Version, 1942) | 8K',
    description: 'WWII Dokumentation über Pearl Harbor.',
    year: 1942,
    decade: '1940s',
    category: 'propaganda',
    subcategory: 'wwii',
    tags: ['wwii', 'pearl harbor', 'documentary', 'history'],
    duration: 1800,
  },
  {
    id: 'biological-warfare-1952',
    ytId: 'Zu_iBCd5NJc',
    title: 'What You Should Know About Biological Warfare (1952) | 8K',
    description: 'Kalter Krieg Civil Defense Film.',
    year: 1952,
    decade: '1950s',
    category: 'propaganda',
    subcategory: 'civil-defense',
    tags: ['cold war', 'civil defense', 'propaganda'],
    duration: 900,
  },
  {
    id: 'duck-cover-1951',
    ytId: 'Ge-mC5q6lXw',
    title: 'Duck and Cover (1951) | 8K',
    description: 'Berühmter Kalter Krieg Civil Defense Film.',
    year: 1951,
    decade: '1950s',
    category: 'propaganda',
    subcategory: 'civil-defense',
    tags: ['cold war', 'atomic', 'civil defense', 'turtle'],
    duration: 540,
  },
  {
    id: 'nazi-camps-1945',
    ytId: 'DO8dSN4aAB4',
    title: 'Nazi Concentration Camps (1945) | 8K',
    description: 'Offizielle US Army Dokumentation für die Nürnberger Prozesse.',
    year: 1945,
    decade: '1940s',
    category: 'documentaries',
    subcategory: 'historical',
    tags: ['wwii', 'holocaust', 'nuremberg', 'history'],
    duration: 3600,
  },
  {
    id: 'my-japan-1945',
    ytId: 'rV78L39ybOU',
    title: 'My Japan (1945) | WWII Propaganda Film | 8K',
    description: 'US Kriegsanleihen-Propaganda aus WWII.',
    year: 1945,
    decade: '1940s',
    category: 'propaganda',
    subcategory: 'wwii',
    tags: ['wwii', 'propaganda', 'war bonds'],
    duration: 600,
  },
  {
    id: 'atomic-bomb-1946',
    ytId: '9AgSJyMnxi8',
    title: 'Atomic Bomb Newsreel (1946) | 8K | German Wochenschau',
    description: 'Deutsche Wochenschau über das Atomzeitalter.',
    year: 1946,
    decade: '1940s',
    category: 'documentaries',
    subcategory: 'newsreels',
    tags: ['atomic', 'wochenschau', 'german', 'nuclear'],
    duration: 420,
  },
  {
    id: 'hindenburg-1937',
    ytId: 'eF81rBeXbzk',
    title: 'The Hindenburg Explodes (1937) | 4K 8K',
    description: 'Restaurierte Newsreel-Aufnahmen der Hindenburg-Katastrophe.',
    year: 1937,
    decade: '1930s',
    category: 'documentaries',
    subcategory: 'newsreels',
    tags: ['hindenburg', 'disaster', 'newsreel', 'zeppelin'],
    duration: 300,
  },
  {
    id: 'revival-organisms-1940',
    ytId: 'D1WD7sS637k',
    title: 'Experiments in the Revival of Organisms (1940) | 8K',
    description: 'Sowjetischer Wissenschaftsfilm.',
    year: 1940,
    decade: '1940s',
    category: 'documentaries',
    subcategory: 'science',
    tags: ['soviet', 'science', 'experiment', 'medical'],
    duration: 1200,
  },
  {
    id: 'wonderful-world-1959',
    ytId: 'UtVxs89CUPc',
    title: 'Wonderful World (1959) | 8K | Coca-Cola Travelogue',
    description: 'Farbenprächtige Weltreise aus den 50ern.',
    year: 1959,
    decade: '1950s',
    category: 'documentaries',
    subcategory: 'travelogues',
    tags: ['coca-cola', 'travel', 'world', '50s', 'color'],
    duration: 900,
  },
  {
    id: 'golden-gate',
    ytId: '2Ua5qHZ5QDw',
    title: 'Golden Gate – Retro San Francisco | 8K',
    description: 'Vintage San Francisco Reisefilm.',
    year: 1950,
    decade: '1950s',
    category: 'documentaries',
    subcategory: 'travelogues',
    tags: ['san francisco', 'golden gate', 'travel', 'vintage'],
    duration: 600,
  },

  // =========================================================================
  // NEUE VIDEOS - Dezember 2025 Update
  // =========================================================================

  // --- Popeye Marathon ---
  {
    id: 'popeye-marathon-8k',
    ytId: '3gzbxznJ_PM',
    title: 'Popeye – Alle Klassiker in einem Video',
    description:
      'Über 4 Stunden Popeye-Cartoon-Marathon! Alle klassischen Episoden der Famous Studios Ära in 8K restauriert. Der ultimative Popeye-Genuss.',
    year: 1945,
    decade: '1940s',
    category: 'cartoons',
    subcategory: 'popeye',
    tags: ['popeye', 'marathon', 'famous studios', 'cartoon', 'sammlung'],
    duration: 16864,
  },

  // --- Christmas Additions ---
  {
    id: 'santas-surprise-1947',
    ytId: 'f8ZGvwk0k-o',
    title: 'Santas Überraschung (1947) – Little Audrey',
    description:
      'Little Audreys bezaubernder Weihnachts-Cartoon aus 1947. Eine herzerwärmende Geschichte über die Magie des Schenkens.',
    year: 1947,
    decade: '1940s',
    category: 'christmas',
    subcategory: 'cartoons',
    tags: ['weihnachten', 'little audrey', 'christmas', 'cartoon', 'famous studios'],
    duration: 505,
  },

  // --- Computer History ---
  {
    id: 'commodore-64-ia',
    ytId: 'j4r3bPPQza0',
    title: 'Commodore 64 – Vintage Computer Dokumentation',
    description:
      'Internet Archive Fundstück: Historische Aufnahmen des legendären Commodore 64. Ein Stück Computergeschichte aus den 80ern.',
    year: 1982,
    decade: '1980s',
    category: 'documentaries',
    subcategory: 'tech',
    tags: ['commodore 64', 'c64', 'computer', '80s', 'retro', 'tech history'],
    duration: 1712,
  },

  // --- Superman ---
  {
    id: 'superman-eleventh-hour-1942',
    ytId: '6A2_RKWP2X4',
    title: 'Superman: Die elfte Stunde (1942)',
    description:
      'Max Fleischers Superman rettet wieder den Tag! Spannender WWII-Propaganda-Cartoon mit atemberaubender Animation.',
    year: 1942,
    decade: '1940s',
    category: 'cartoons',
    subcategory: 'superman',
    tags: ['superman', 'fleischer', 'wwii', 'animation', 'action'],
    duration: 540,
  },

  // --- Prelinger Archive ---
  {
    id: 'children-make-movies',
    ytId: 'EhZdQ74_sCM',
    title: 'Kinder machen Filme (Prelinger Archive)',
    description:
      'Faszinierendes Prelinger Archive Fundstück über Kinder, die ihre eigenen Filme drehen. Ein Zeitdokument der Bildungsfilme.',
    year: 1960,
    decade: '1960s',
    category: 'documentaries',
    subcategory: 'educational',
    tags: ['prelinger', 'kinder', 'bildung', 'filmmaking', 'educational'],
    duration: 547,
  },

  // --- Houdini ---
  {
    id: 'grim-game-1919',
    ytId: 'EMnokZOLpzU',
    title: 'Das grausame Spiel (1919) – Houdini',
    description:
      'Harry Houdini in seinem legendären Stummfilm-Thriller. Der Meister der Entfesselung zeigt spektakuläre Stunts.',
    year: 1919,
    decade: '1910s',
    category: 'classic-films',
    subcategory: 'thriller',
    tags: ['houdini', 'stummfilm', 'thriller', 'stunts', 'magie'],
    duration: 244,
  },

  // --- More Cartoons ---
  {
    id: 'candid-candidate-1937',
    ytId: 'ExbniPRgH70',
    title: 'Der Offenherzige Kandidat (1937)',
    description:
      'Politische Cartoon-Satire aus den 30er Jahren. Eine witzige Zeitkapsel über Wahlkampf und Politik.',
    year: 1937,
    decade: '1930s',
    category: 'cartoons',
    subcategory: 'political',
    tags: ['politik', 'satire', 'cartoon', '30s', 'wahlkampf'],
    duration: 364,
  },

  // --- Classic Films ---
  {
    id: 'charade-1953',
    ytId: 'PSdJJaxI4gM',
    title: 'Charade (1953) – Mystery Klassiker',
    description:
      'Spannender Vintage-Mystery-Film aus den 50ern. Atmosphärische Unterhaltung mit klassischem Hollywood-Charme.',
    year: 1953,
    decade: '1950s',
    category: 'classic-films',
    subcategory: 'mystery',
    tags: ['mystery', 'thriller', '50s', 'klassiker', 'spannung'],
    duration: 4901,
  },
  {
    id: 'cabinet-caligari-1920',
    ytId: '5WVJHELSD7A',
    title: 'Das Cabinet des Dr. Caligari (1920)',
    description:
      'DER deutsche Expressionismus-Klassiker schlechthin. Robert Wienes alptraumhafte Vision beeinflusst das Kino bis heute. Ein Muss für jeden Filmfan.',
    year: 1920,
    decade: '1920s',
    category: 'classic-films',
    subcategory: 'horror',
    tags: ['expressionismus', 'horror', 'stummfilm', 'caligari', 'german', 'klassiker'],
    duration: 4518,
  },
  {
    id: 'white-zombie-1932',
    ytId: 'd8Ak1R_eOlY',
    title: 'White Zombie (1932) – Bela Lugosi',
    description:
      'Der erste Zombie-Langfilm der Geschichte! Bela Lugosi als unheimlicher Voodoo-Meister in diesem atmosphärischen Horrorklassiker.',
    year: 1932,
    decade: '1930s',
    category: 'classic-films',
    subcategory: 'horror',
    tags: ['zombie', 'bela lugosi', 'horror', 'voodoo', 'klassiker', 'halloween'],
    duration: 3920,
  },

  // --- Felix the Cat Collection ---
  {
    id: 'felix-makes-good-1922',
    ytId: 'DMDp52B3Nv4',
    title: 'Felix macht es gut (1922)',
    description:
      'Felix the Cat in einem seiner frühen Abenteuer. Klassische Stummfilm-Animation voller Charme und Witz.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'stummfilm', 'cartoon', 'klassiker', 'pat sullivan'],
    duration: 587,
  },
  {
    id: 'felix-in-love-1922',
    ytId: 'eySdw7WrSps',
    title: 'Felix verliebt sich (1922)',
    description:
      'Der weltberühmte Kater auf romantischen Abwegen. Eine herzerwärmende Stummfilm-Animation aus der goldenen Ära.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'stummfilm', 'romantik', 'cartoon', 'klassiker'],
    duration: 367,
  },
  {
    id: 'felix-at-fair-1922',
    ytId: 'E7X_PG6wJEk',
    title: 'Felix auf dem Jahrmarkt (1922)',
    description:
      'Felix erkundet den Rummel! Fröhliche Stummfilm-Unterhaltung mit dem cleveren Kater.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'jahrmarkt', 'stummfilm', 'cartoon', 'spaß'],
    duration: 264,
  },
  {
    id: 'big-game-hunter',
    ytId: '9_rhugQFh8w',
    title: 'Der Großwildjäger – Cartoon Klassiker',
    description: 'Vintage Cartoon-Abenteuer auf Safari. Humorvolle Animation aus der goldenen Ära.',
    year: 1930,
    decade: '1930s',
    category: 'cartoons',
    subcategory: 'adventure',
    tags: ['safari', 'jagd', 'cartoon', 'abenteuer', 'vintage'],
    duration: 312,
  },
  {
    id: 'felix-circus-1921',
    ytId: 'kLpuqswC0IE',
    title: 'Felix im Zirkus (1921)',
    description:
      'Felix the Cat erlebt Zirkusabenteuer! Einer der frühesten Felix-Cartoons in 8K restauriert.',
    year: 1921,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'zirkus', 'stummfilm', 'cartoon', 'früh'],
    duration: 320,
  },
  {
    id: 'felix-circus-deluxe',
    ytId: 'fFanPpOArKs',
    title: 'Felix im Zirkus – Deluxe 8K Edition',
    description:
      'Premium-Restaurierung von Felix the Cats Zirkusabenteuer. Höchste Bildqualität für Animationsfans.',
    year: 1921,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'zirkus', 'stummfilm', '8k', 'deluxe'],
    duration: 320,
  },
  {
    id: 'felix-revenge-1922',
    ytId: 'ICzD6hNya9c',
    title: 'Felix rächt sich (1922)',
    description:
      'Felix the Cat zeigt es seinen Widersachern! Clevere Stummfilm-Comedy mit dem weltberühmten Kater.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'stummfilm', 'comedy', 'rache', 'cartoon'],
    duration: 525,
  },
  {
    id: 'felix-saves-day-1922',
    ytId: '5CEONd_SGn8',
    title: 'Felix rettet den Tag (1922)',
    description:
      'Der heldenhafte Kater in Aktion! Felix beweist wieder einmal seinen Mut und Einfallsreichtum.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'held', 'stummfilm', 'cartoon', 'aktion'],
    duration: 464,
  },
  {
    id: 'felix-turns-tide-1922',
    ytId: '_jemp3ZpZYY',
    title: 'Felix wendet das Blatt (1922)',
    description:
      'Felix the Cat meistert wieder einmal eine scheinbar aussichtslose Situation mit Witz und Verstand.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'stummfilm', 'cartoon', 'cleverness', 'klassiker'],
    duration: 494,
  },
  {
    id: 'felix-finds-way-1924',
    ytId: '_X9OwQuRshk',
    title: 'Felix findet einen Weg (1924)',
    description:
      'Der einfallsreiche Kater löst jedes Problem! Charmante Stummfilm-Animation aus den goldenen Zwanzigern.',
    year: 1924,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'stummfilm', 'problemlösung', 'cartoon', '20s'],
    duration: 499,
  },
  {
    id: 'felix-minds-kid-1922',
    ytId: 'qZU5lVJMkoM',
    title: 'Felix passt auf das Kind auf (1922)',
    description: 'Felix the Cat als Babysitter! Chaotische und herzerwärmende Stummfilm-Comedy.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'babysitter', 'stummfilm', 'comedy', 'chaos'],
    duration: 497,
  },
  {
    id: 'felix-pedigreedy-1927',
    ytId: '8rr5p_y7k_8',
    title: 'Felix Pedigreedy (1927)',
    description:
      'Felix the Cat in einem späten Stummfilm-Abenteuer. Witzige Satire auf Stammbaum-Besessenheit.',
    year: 1927,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'stummfilm', 'satire', 'cartoon', 'späte 20er'],
    duration: 478,
  },
  {
    id: 'feline-follies-1919',
    ytId: 'AD2oRdK4seI',
    title: "Feline Follies (1919) – Felix' Debüt",
    description:
      'Der allererste Felix the Cat Cartoon! Hier begann die Legende des berühmtesten Katers der Filmgeschichte.',
    year: 1919,
    decade: '1910s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: ['felix the cat', 'debüt', 'erster', 'stummfilm', 'historisch', 'pat sullivan'],
    duration: 255,
  },

  // --- Betty Boop ---
  {
    id: 'betty-boop-kerchoo-1932',
    ytId: '-3UHQiZHPwY',
    title: 'Betty Boop: Ker-Choo! (1932)',
    description:
      'Betty Boop kämpft gegen eine Erkältung! Fleischer Studios Cartoon mit dem typischen Pre-Code Charme.',
    year: 1932,
    decade: '1930s',
    category: 'cartoons',
    subcategory: 'betty-boop',
    tags: ['betty boop', 'fleischer', 'pre-code', 'cartoon', 'jazz age'],
    duration: 381,
  },
  {
    id: 'betty-boop-minnie-moocher-1932',
    ytId: 'tJMJlCQc0UE',
    title: 'Betty Boop: Minnie the Moocher (1932)',
    description:
      'DER legendäre Betty Boop Cartoon mit Cab Calloways Jazz-Meisterwerk. Surrealer Fleischer-Wahnsinn at its finest!',
    year: 1932,
    decade: '1930s',
    category: 'cartoons',
    subcategory: 'betty-boop',
    tags: ['betty boop', 'cab calloway', 'jazz', 'fleischer', 'surreal', 'klassiker'],
    duration: 467,
  },

  // --- Wartime Cartoons ---
  {
    id: 'tokyo-jokio-1943',
    ytId: 'M0-tJK4H3lo',
    title: 'Tokio Jokio (1943) – Merrie Melodies',
    description:
      'Kontroverse WWII-Propaganda der Merrie Melodies. Ein Zeitdokument, das heute zum Verständnis der Kriegszeit dient.',
    year: 1943,
    decade: '1940s',
    category: 'cartoons',
    subcategory: 'wartime',
    tags: ['merrie melodies', 'wwii', 'propaganda', 'warner bros', 'zeitdokument'],
    duration: 410,
  },

  // --- Aesop's Fables ---
  {
    id: 'aesops-skating-hounds-1929',
    ytId: 'Q1H33-Yw_uQ',
    title: 'Äsops Fabeln: Schlittschuh-Hunde (1929)',
    description:
      "Bezaubernder Cartoon aus der Aesop's Fables Serie. Winterliche Unterhaltung aus der frühen Tonfilm-Ära.",
    year: 1929,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'aesop',
    tags: ['aesop', 'fabeln', 'winter', 'schlittschuh', 'frühe tonfilm'],
    duration: 402,
  },

  // --- Krazy Kat ---
  {
    id: 'krazy-kat-keeping-up-1916',
    ytId: 'WWdC0Rq4cQQ',
    title: 'Krazy Kat: Keeping Up (1916)',
    description:
      'Früher Krazy Kat Cartoon basierend auf dem legendären Comic Strip. Ein Stück Animations-Geschichte.',
    year: 1916,
    decade: '1910s',
    category: 'cartoons',
    subcategory: 'krazy-kat',
    tags: ['krazy kat', 'comic', 'stummfilm', 'früh', 'historisch'],
    duration: 420,
  },

  // --- Early Sci-Fi ---
  {
    id: 'airship-destroyed-1909',
    ytId: '3NagSoFaAwI',
    title: 'Luftschiff zerstört (1909) – Erster Sci-Fi Film',
    description:
      'Einer der allerersten Science-Fiction-Filme der Geschichte! Bahnbrechende Spezialeffekte aus der Pionierzeit des Kinos.',
    year: 1909,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'early-cinema',
    tags: ['sci-fi', 'erster', 'luftschiff', 'stummfilm', 'pionier', 'spezialeffekte'],
    duration: 402,
  },

  // --- Little Nemo ---
  {
    id: 'little-nemo-alt-1911',
    ytId: '0pBFESQ-FmA',
    title: 'Little Nemo in Slumberland (1911) – Alternative Version',
    description:
      'Alternative Restaurierung von Winsor McCays bahnbrechendem Animationsfilm. Ein Meilenstein der Filmgeschichte.',
    year: 1911,
    decade: '1910s',
    category: 'cartoons',
    subcategory: 'mccay',
    tags: ['winsor mccay', 'little nemo', 'animation', 'pionier', 'historisch'],
    duration: 619,
  },

  // --- Peter and the Wolf Duplicate ---
  {
    id: 'peter-wolf-alt-1960',
    ytId: '-623U3tgryM',
    title: 'Peter und der Wolf (1960) – Alternative Version',
    description:
      'Mel-O-Toons Version von Prokofievs musikalischem Meisterwerk. Klassische Animation trifft klassische Musik.',
    year: 1960,
    decade: '1960s',
    category: 'cartoons',
    subcategory: 'musical',
    tags: ['peter and the wolf', 'prokofiev', 'musik', 'mel-o-toons', 'klassik'],
    duration: 402,
  },

  // =========================================================================
  // YOUTUBE SHORTS - Kuratierte Kurzvideos (unter 4 Minuten)
  // =========================================================================

  // --- Christmas Shorts ---
  {
    id: 'suzy-snowflake-short-2025',
    ytId: 'EpzJcD6zkvs',
    title: 'Suzy Snowflake (1953)',
    description:
      'Der charmante Stop-Motion Weihnachtsklassiker von 1953. Suzy Snowflake bringt den Winter zu den Kindern – ein Stück TV-Geschichte aus der goldenen Ära der Weihnachtssendungen.',
    year: 1953,
    decade: '1950s',
    category: 'christmas',
    subcategory: 'shorts',
    tags: [
      'weihnachten',
      'stop-motion',
      'christmas',
      'suzy snowflake',
      'winter',
      'kinderklassiker',
    ],
    duration: 124,
    isShort: true,
  },
  {
    id: 'suzy-snowflake-full-1953',
    ytId: 'Z4nwcfOqOOw',
    title: 'Suzy Snowflake – Der erste Weihnachts-Kurzfilm',
    description:
      'Suzy Snowflake (ca. 1953) gilt als einer der ersten Weihnachts-Kurzfilme des amerikanischen Fernsehens. Diese Stop-Motion Animation wurde für lokale TV-Sender produziert.',
    year: 1953,
    decade: '1950s',
    category: 'christmas',
    subcategory: 'shorts',
    tags: ['weihnachten', 'stop-motion', 'christmas', '1953', 'tv klassiker', 'animation'],
    duration: 164,
    isShort: true,
  },
  {
    id: 'coca-cola-trucks-4k',
    ytId: 'U-WD47NSgAE',
    title: 'Coca-Cola Weihnachtstrucks – Holidays Are Coming',
    description:
      'Der ikonische "Holidays Are Coming" Werbespot von Coca-Cola aus 1995. Die leuchtenden Weihnachtstrucks wurden zum Symbol für den Beginn der Weihnachtszeit.',
    year: 1995,
    decade: '1990s',
    category: 'commercials',
    subcategory: 'coca-cola',
    tags: ['coca-cola', 'weihnachten', 'werbung', 'christmas', 'trucks', '1995', 'ikonisch'],
    duration: 61,
    isShort: true,
  },
  {
    id: 'coca-cola-trucks-8k-epic',
    ytId: 'WSjkAZkPbKs',
    title: 'Coca-Cola Christmas Trucks – 8K Remaster',
    description:
      'Die epische 8K-Restaurierung des legendären Coca-Cola Weihnachtsspots. "Holidays Are Coming" definierte Weihnachtswerbung für eine ganze Generation.',
    year: 1995,
    decade: '1990s',
    category: 'commercials',
    subcategory: 'coca-cola',
    tags: ['coca-cola', 'weihnachten', 'werbung', '8k', 'remaster', 'iconic'],
    duration: 61,
    isShort: true,
  },
  {
    id: 'batman-robin-santa-short',
    ytId: 'yIQCHpjp4NE',
    title: 'Batman & Robin treffen Santa Claus',
    description:
      'Aus der kultige 60er Jahre Batman TV-Serie: Batman und Robin begegnen dem Weihnachtsmann. Eine der skurrilsten Weihnachtsszenen der TV-Geschichte.',
    year: 1966,
    decade: '1960s',
    category: 'christmas',
    subcategory: 'tv',
    tags: ['batman', 'robin', 'santa', 'weihnachten', '1966', 'tv serie', 'camp', 'dc comics'],
    duration: 59,
    isShort: true,
  },
  {
    id: 'batman-robin-santa-full',
    ytId: 'gux5NyjkqxE',
    title: 'Batman & Robin Meet Santa Claus (1966)',
    description:
      'Die vollständige Weihnachtsszene aus der Batman TV-Serie von 1966. Adam West und Burt Ward in ihrer ikonischen Interpretation der DC-Helden.',
    year: 1966,
    decade: '1960s',
    category: 'christmas',
    subcategory: 'tv',
    tags: ['batman', 'robin', 'adam west', 'burt ward', 'weihnachten', '60s', 'klassiker'],
    duration: 74,
    isShort: true,
  },

  // --- Historical Shorts ---
  {
    id: 'pearl-harbor-1942-short',
    ytId: 'EasEhYlorqQ',
    title: 'Pearl Harbor – Historische Kurzversion (1942)',
    description:
      'Zeitgenössische Dokumentation des Angriffs auf Pearl Harbor vom 7. Dezember 1941. Produziert von Jam Handy für das US-Kriegsministerium. Historisches Zeitdokument.',
    year: 1942,
    decade: '1940s',
    category: 'documentaries',
    subcategory: 'wwii',
    tags: ['pearl harbor', 'wwii', '1942', 'weltkrieg', 'dokumentation', 'jam handy', 'prelinger'],
    duration: 201,
    isShort: true,
  },

  // --- Early Cinema Pioneers (Pre-1910) ---
  {
    id: 'golden-beetle-1907',
    ytId: 'IpWrF7DYyWU',
    title: 'Der goldene Käfer (1907)',
    description:
      'Ferdinand Zeccas Meisterwerk für Pathé Frères. Ein Juwel des frühen Trickkinos mit handkolorierten Szenen, Bühnenmagie und Stop-Motion-Effekten aus der Pionierzeit des Films.',
    year: 1907,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'early-cinema',
    tags: [
      'ferdinand zecca',
      'pathé',
      '1907',
      'stummfilm',
      'trick film',
      'handkoloriert',
      'pionier',
    ],
    duration: 84,
    isShort: true,
  },
  {
    id: 'the-frog-1908',
    ytId: 'dfUyhjEnAqw',
    title: 'Der Frosch (1908)',
    description:
      'Segundo de Chomóns surrealer Trickfilm kombiniert Stop-Motion, praktische Effekte und Studiomagie. Ein Meisterwerk des vorweltkriegszeitlichen Kinos.',
    year: 1908,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'early-cinema',
    tags: ['segundo de chomón', '1908', 'stummfilm', 'trick film', 'stop-motion', 'surrealismus'],
    duration: 196,
    isShort: true,
  },
  {
    id: 'bee-and-rose-1908',
    ytId: 'gMpONbJ3-9U',
    title: 'Die Biene und die Rose (1908)',
    description:
      'Segundo de Chomóns poetischer Kurzfilm verbindet frühe Tricktechnik mit zarter Handwerkskunst. Ein Meilenstein visueller Erzählung aus der Frühzeit des Kinos.',
    year: 1908,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'early-cinema',
    tags: ['segundo de chomón', '1908', 'stummfilm', 'poesie', 'natur', 'visual art'],
    duration: 202,
    isShort: true,
  },
  {
    id: 'astronomers-dream-1898',
    ytId: 'tk3DHvp9CFs',
    title: 'Der Traum des Astronomen (1898)',
    description:
      "Georges Méliès' visionärer Kurzfilm gilt als einer der ersten Science-Fiction-Filme überhaupt. Der Mondgeist besucht einen schlafenden Astronomen – pure Kino-Magie aus dem 19. Jahrhundert.",
    year: 1898,
    decade: '1900s',
    category: 'classic-films',
    subcategory: 'early-cinema',
    tags: ['georges méliès', '1898', 'science fiction', 'stummfilm', 'pionier', 'mond', 'traum'],
    duration: 186,
    isShort: true,
  },

  // --- Classic Cartoons Shorts ---
  {
    id: 'felix-swim-1922',
    ytId: 'cKMnE6pFz_w',
    title: 'Felix the Cat – In the Swim (1922)',
    description:
      'Einer der frühesten Felix the Cat Kurzfilme. Der weltberühmte Kater erlebt ein humorvolles Unterwasser-Abenteuer – klassische Stummfilm-Animation in 8K restauriert.',
    year: 1922,
    decade: '1920s',
    category: 'cartoons',
    subcategory: 'felix',
    tags: [
      'felix the cat',
      '1922',
      'stummfilm',
      'animation',
      'cartoon',
      'klassiker',
      'pat sullivan',
    ],
    duration: 208,
    isShort: true,
  },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function buildNavigationTree(videos) {
  const tree = {
    byDecade: {},
    byCategory: {},
  };

  DECADES.forEach((decade) => {
    tree.byDecade[decade.id] = { ...decade, videos: [], count: 0 };
  });

  CATEGORIES.forEach((cat) => {
    tree.byCategory[cat.id] = { ...cat, videos: [], count: 0 };
  });

  videos.forEach((video) => {
    if (video.decade && tree.byDecade[video.decade]) {
      tree.byDecade[video.decade].videos.push(video);
      tree.byDecade[video.decade].count++;
    }
    if (video.category && tree.byCategory[video.category]) {
      tree.byCategory[video.category].videos.push(video);
      tree.byCategory[video.category].count++;
    }
  });

  return tree;
}

export function filterVideos(videos, filters = {}) {
  return videos.filter((video) => {
    if (filters.decade && video.decade !== filters.decade) return false;
    if (filters.category && video.category !== filters.category) return false;
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const searchable = [video.title, video.description, ...(video.tags || [])]
        .join(' ')
        .toLowerCase();
      if (!searchable.includes(searchLower)) return false;
    }
    return true;
  });
}

export function sortVideos(videos, sortBy = 'year', order = 'desc') {
  const sorted = [...videos];
  sorted.sort((a, b) => {
    let valA, valB;
    switch (sortBy) {
      case 'year':
        valA = a.year || 0;
        valB = b.year || 0;
        break;
      case 'title':
        return order === 'asc' ? a.title.localeCompare(b.title) : b.title.localeCompare(a.title);
      default:
        valA = a.year || 0;
        valB = b.year || 0;
    }
    return order === 'asc' ? valA - valB : valB - valA;
  });
  return sorted;
}

export function groupVideos(videos, groupBy = 'decade') {
  const groups = {};
  videos.forEach((video) => {
    const key = video[groupBy] || 'unknown';
    if (!groups[key]) groups[key] = [];
    groups[key].push(video);
  });
  return groups;
}

export function createTimeline(videos) {
  return sortVideos(videos, 'year', 'asc');
}

export default {
  CHANNEL_CONFIG,
  DECADES,
  CATEGORIES,
  CONTENT_TYPES,
  MILESTONE_TYPES,
  remaikeVideos,
  buildNavigationTree,
  filterVideos,
  sortVideos,
  groupVideos,
  createTimeline,
};
