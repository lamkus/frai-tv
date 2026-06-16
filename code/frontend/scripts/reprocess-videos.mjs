import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { processVideoTitle } from './series-matcher.mjs';

const videosPath = join(process.cwd(), 'public', 'data', 'videos.json');
const videos = JSON.parse(readFileSync(videosPath, 'utf8'));

console.log(`Reprocessing ${videos.length} videos...`);

const enriched = videos.map((v) => {
  const title = v.originalTitle || v.title;
  const description = v.description;

  const seriesMatch = processVideoTitle(title, description);

  return {
    ...v,
    title: seriesMatch.formattedTitle || title,
    formattedDescription: seriesMatch.formattedDescription || v.formattedDescription,
    seriesId: seriesMatch.seriesId || v.seriesId,
    seriesName: seriesMatch.seriesName || v.seriesName,
    episodeNumber: seriesMatch.episodeNumber || v.episodeNumber,
    episodeTotal: seriesMatch.episodeTotal || v.episodeTotal,
    matchConfidence: seriesMatch.matchConfidence || v.matchConfidence,
  };
});

writeFileSync(videosPath, JSON.stringify(enriched, null, 2));
console.log(`Successfully reprocessed and saved to ${videosPath}`);

const seriesCount = enriched.filter((v) => v.seriesId).length;
console.log(`\n📊 Summary:`);
console.log(`   Total videos: ${enriched.length}`);
console.log(`   Series matched: ${seriesCount}`);
console.log(`   Standalone: ${enriched.length - seriesCount}`);
