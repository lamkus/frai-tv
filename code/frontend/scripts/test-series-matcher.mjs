#!/usr/bin/env node
/**
 * Test Series Matcher
 */

import { processVideoTitle, loadCanonical } from './series-matcher.mjs';

const testTitles = [
  // Preformatted titles (already have episode numbers)
  'Casper (24/55) Boo Moon (1954) | 8K HQ (4K UHD) | Best Online Version | @remAIke_IT',
  'Superman (9/17) — Terror on the Midway (1942) | 8K (4K UHD) @remAIke_IT | Best Online Version',
  'Superman (14/17) The Mummy Strikes (1943) | 8K HQ (4K UHD) | Best Online Version | @remAIke_IT',
  'Casper (32/55) Spooking with a Brogue (1955) | 8K HQ (4K UHD) | Best Online Version | @remAIke_IT',

  // Old format titles
  'Casper - The Friendly Ghost (1945)',
  'Superman - The Mechanical Monsters (1941) 4K Remastered',
  'Betty Boop – Minnie the Moocher (1932)',

  // Superman variants
  'Superman: Japoteurs (1942) | 8K @remAIke_IT WWII Propaganda Cartoon',
  "Max Fleischer's Superman: Destruction Inc. (1943) | 8K remAIke",

  // Popeye
  'Popeye the Sailor – Ancient Fistory (1953) | 8K @ReAImastered',
  'Patriotic Popeye (1957) 8K @remAIke_IT',

  // Betty Boop
  'Betty Boop – More Pep (1936) | 8K @reAImastered',

  // Charlie Chaplin
  'The Cure (1917) – Charlie Chaplin | 8K remAIke Silent Comedy',

  // Felix the Cat
  'Felix the Cat – Felix Saves the Day (1922) | 8K Remastered',
  'Felix Makes Good (1922) – @reAImastered 8K Edition',

  // Non-series
  'The Skeleton Dance (1929) | 8K @remAIke_IT Disney Silly Symphony',
];

console.log('🎬 Series Detection & Episode Matching Test\n');

// Load canonical data first
const canonical = loadCanonical();
console.log(`📚 Loaded canonical data for: ${Object.keys(canonical).join(', ')}\n`);

for (const title of testTitles) {
  console.log('─'.repeat(60));
  console.log(`Input: ${title}`);
  const result = processVideoTitle(title);
  console.log(`Series: ${result.seriesId || 'none'} (${result.seriesName || 'n/a'})`);
  console.log(`Episode: ${result.episodeNumber || 'n/a'}/${result.episodeTotal || 'n/a'}`);
  console.log(`Year: ${result.year || 'unknown'}`);
  console.log(
    `Match: ${result.matchType || 'none'} (${(result.matchConfidence * 100).toFixed(0)}%)`
  );
  console.log(`Formatted: ${result.formattedTitle || result.cleanedTitle}`);
  console.log('');
}

console.log('✅ Test complete!');
