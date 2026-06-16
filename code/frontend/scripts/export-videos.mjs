import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataPath = path.join(__dirname, '..', 'src', 'data', 'remaikeData.js');

// Import the data module dynamically
const dataModule = await import('../src/data/remaikeData.js');
const videos = dataModule.remaikeVideos || [];

// Add thumbnail URLs to each video
const enrichedVideos = videos.map((video) => ({
  ...video,
  thumbnail: video.thumbnail || `https://i.ytimg.com/vi/${video.ytId}/mqdefault.jpg`,
}));

const outDir = path.join(__dirname, '..', 'public', 'data');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
const outFile = path.join(outDir, 'videos.json');
fs.writeFileSync(outFile, JSON.stringify(enrichedVideos, null, 2), 'utf8');
console.log(`Wrote ${enrichedVideos.length} videos to ${outFile}`);
