import fs from 'fs/promises';
import path from 'path';

const DATA_FILE = path.resolve(process.cwd(), 'public/data/videos.json');

async function main() {
  let raw = await fs.readFile(DATA_FILE, 'utf8');
  // Strip potential BOM and anything before the array start (robustness for manually edited files)
  raw = raw.replace(/^\uFEFF/, '');
  const firstBracket = raw.indexOf('[');
  const lastBracket = raw.lastIndexOf(']');
  if (firstBracket === -1 || lastBracket === -1) throw new Error('Invalid videos.json format');
  const jsonText = raw.slice(firstBracket, lastBracket + 1);
  const videos = JSON.parse(jsonText);
  let changed = 0;
  for (const v of videos) {
    const resolved =
      v.thumbnailUrl ||
      v.thumbnail ||
      (v.ytId ? `https://img.youtube.com/vi/${v.ytId}/maxresdefault.jpg` : '');
    if (!v.thumbnail) {
      v.thumbnail = resolved;
      changed++;
    }
  }
  if (changed > 0) {
    // Backup existing file and write atomically to avoid transient truncation
    try {
      await fs.copyFile(DATA_FILE, DATA_FILE + '.bak');
    } catch (e) {
      // ignore if no existing file
    }
    await fs.writeFile(DATA_FILE + '.tmp', JSON.stringify(videos, null, 2), 'utf8');
    await fs.rename(DATA_FILE + '.tmp', DATA_FILE);
    console.log(`Updated ${changed} videos with thumbnail field.`);
  } else {
    console.log('No changes needed.');
  }
}

main().catch((err) => {
  console.error('Failed to update thumbnails:', err);
  process.exit(1);
});
