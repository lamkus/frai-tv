#!/usr/bin/env node
/**
 * AI-Enhanced Chapter Detection
 *
 * 1. Downloads YouTube video (low quality)
 * 2. Detects potential chapter boundaries via ffmpeg (black/silence)
 * 3. Extracts screenshot frames at each boundary
 * 4. Sends frames to OpenAI Vision API for analysis
 * 5. AI identifies: title cards, scene changes, episode intros
 * 6. Feedback loop: adjusts boundaries based on AI confidence
 * 7. Outputs refined chapter timestamps with AI-generated titles
 *
 * Usage:
 *   node ai-chapter-detection.mjs --ytId 3gzbxznJ_PM
 *   node ai-chapter-detection.mjs --ytId FG-vqRH5Cg4 --apiKey sk-xxx
 *
 * Requires: yt-dlp, ffmpeg, OPENAI_API_KEY env var (or --apiKey)
 */

import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import https from 'node:https';

// ─────────────────────────────────────────────────────────────
// CLI Args
// ─────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) {
      args._.push(a);
      continue;
    }
    const key = a.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
    } else {
      args[key] = next;
      i++;
    }
  }
  return args;
}

// ─────────────────────────────────────────────────────────────
// Shell runner
// ─────────────────────────────────────────────────────────────
function run(cmd, cmdArgs, { captureStderr = false, captureStdout = false } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, cmdArgs, {
      stdio: ['ignore', captureStdout ? 'pipe' : 'inherit', captureStderr ? 'pipe' : 'inherit'],
      shell: process.platform === 'win32',
    });
    let stderr = '',
      stdout = '';
    if (captureStderr) child.stderr.on('data', (d) => (stderr += d.toString()));
    if (captureStdout) child.stdout.on('data', (d) => (stdout += d.toString()));
    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) {
        const err = new Error(`${cmd} exited ${code}`);
        err.stderr = stderr;
        err.stdout = stdout;
        reject(err);
      } else resolve({ stderr, stdout });
    });
  });
}

// ─────────────────────────────────────────────────────────────
// ffmpeg parsers
// ─────────────────────────────────────────────────────────────
function parseBlackdetect(stderr) {
  const events = [];
  const re =
    /black_start:(\d+(?:\.\d+)?)\s+black_end:(\d+(?:\.\d+)?)\s+black_duration:(\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(stderr))) {
    events.push({ start: Number(m[1]), end: Number(m[2]), duration: Number(m[3]) });
  }
  return events;
}

function parseSilencedetect(stderr) {
  const events = [];
  const re =
    /silence_start:\s*(\d+(?:\.\d+)?)\s*[\s\S]*?silence_end:\s*(\d+(?:\.\d+)?)\s*\|\s*silence_duration:\s*(\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(stderr))) {
    events.push({ start: Number(m[1]), end: Number(m[2]), duration: Number(m[3]) });
  }
  // fallback: just silence_end
  if (events.length === 0) {
    const re2 = /silence_end:\s*(\d+(?:\.\d+)?)/g;
    while ((m = re2.exec(stderr))) {
      events.push({ start: null, end: Number(m[1]), duration: 0 });
    }
  }
  return events;
}

function parseSceneChanges(stderr) {
  const events = [];
  const re = /pts_time:([\d.]+)\s+t:([\d.]+)\s+scene_score=([\d.]+)/g;
  let m;
  while ((m = re.exec(stderr))) {
    events.push({ time: Number(m[1]), score: Number(m[3]) });
  }
  return events;
}

// ─────────────────────────────────────────────────────────────
// Time formatting
// ─────────────────────────────────────────────────────────────
function toTimestamp(totalSeconds) {
  const s = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  return `${m}:${String(sec).padStart(2, '0')}`;
}

function toFFmpegTime(sec) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(
    Math.floor(s)
  ).padStart(2, '0')}.${String(Math.floor((s % 1) * 1000)).padStart(3, '0')}`;
}

// ─────────────────────────────────────────────────────────────
// Extract frame at timestamp
// ─────────────────────────────────────────────────────────────
async function extractFrame(videoPath, timeSec, outPath) {
  await run(
    'ffmpeg',
    [
      '-hide_banner',
      '-loglevel',
      'error',
      '-ss',
      toFFmpegTime(timeSec),
      '-i',
      videoPath,
      '-frames:v',
      '1',
      '-q:v',
      '2',
      '-y',
      outPath,
    ],
    { captureStderr: true }
  );
  return fs.existsSync(outPath);
}

// ─────────────────────────────────────────────────────────────
// OpenAI Vision API call
// ─────────────────────────────────────────────────────────────
async function analyzeFrameWithAI(imagePath, apiKey, context = {}) {
  const imageData = fs.readFileSync(imagePath);
  const base64 = imageData.toString('base64');
  const mimeType = imagePath.endsWith('.png') ? 'image/png' : 'image/jpeg';

  const prompt = `Analyze this video frame from a classic film/cartoon compilation.

Context:
- Video type: ${context.videoType || 'Classic film/cartoon compilation'}
- Position: ${toTimestamp(context.timeSec || 0)} into video
- Previous chapter: "${context.prevTitle || 'Start'}"

Determine:
1. Is this a CHAPTER BOUNDARY? (title card, episode intro, significant scene change, fade from black)
2. What is the content? (title text, character intro, scene description)
3. Confidence score (0.0-1.0)

Respond in JSON only:
{
  "isChapterBoundary": true/false,
  "confidence": 0.0-1.0,
  "title": "Detected title or scene description",
  "reason": "Why this is/isn't a chapter boundary",
  "contentType": "title_card|episode_intro|scene_change|black_frame|content|unknown"
}`;

  const body = JSON.stringify({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'user',
        content: [
          { type: 'text', text: prompt },
          {
            type: 'image_url',
            image_url: { url: `data:${mimeType};base64,${base64}`, detail: 'low' },
          },
        ],
      },
    ],
    max_tokens: 300,
    temperature: 0.2,
  });

  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: 'api.openai.com',
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`,
          'Content-Length': Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            if (json.error) {
              reject(new Error(json.error.message));
              return;
            }
            const content = json.choices?.[0]?.message?.content || '';
            // Extract JSON from response
            const jsonMatch = content.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              resolve(JSON.parse(jsonMatch[0]));
            } else {
              resolve({
                isChapterBoundary: false,
                confidence: 0.3,
                title: '',
                reason: 'Could not parse AI response',
              });
            }
          } catch (e) {
            reject(e);
          }
        });
      }
    );
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─────────────────────────────────────────────────────────────
// Batch analyze frames for efficiency
// ─────────────────────────────────────────────────────────────
async function batchAnalyzeFrames(frames, apiKey, videoType) {
  const results = [];
  const batchSize = 3; // Parallel requests (be mindful of rate limits)

  for (let i = 0; i < frames.length; i += batchSize) {
    const batch = frames.slice(i, i + batchSize);
    const batchPromises = batch.map((frame, idx) =>
      analyzeFrameWithAI(frame.imagePath, apiKey, {
        videoType,
        timeSec: frame.timeSec,
        prevTitle: results[results.length - 1]?.title || 'Start',
      })
        .then((result) => ({ ...frame, ai: result }))
        .catch((err) => ({
          ...frame,
          ai: {
            isChapterBoundary: false,
            confidence: 0,
            title: '',
            reason: err.message,
            error: true,
          },
        }))
    );

    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);

    // Progress
    console.log(`  AI Analysis: ${Math.min(i + batchSize, frames.length)}/${frames.length} frames`);

    // Rate limit pause
    if (i + batchSize < frames.length) {
      await new Promise((r) => setTimeout(r, 500));
    }
  }

  return results;
}

// ─────────────────────────────────────────────────────────────
// Find yt-dlp
// ─────────────────────────────────────────────────────────────
function findYtDlp() {
  for (const n of ['yt-dlp', 'youtube-dl']) {
    try {
      execSync(`${n} --version`, { stdio: 'ignore' });
      return n;
    } catch {
      /* not found */
    }
  }
  return null;
}

// ─────────────────────────────────────────────────────────────
// Merge nearby timestamps
// ─────────────────────────────────────────────────────────────
function mergeNearbyTimestamps(timestamps, minGapSec = 30) {
  if (timestamps.length === 0) return [];
  timestamps.sort((a, b) => a.time - b.time);

  const merged = [timestamps[0]];
  for (let i = 1; i < timestamps.length; i++) {
    const prev = merged[merged.length - 1];
    const curr = timestamps[i];
    if (curr.time - prev.time < minGapSec) {
      // Keep the one with higher confidence
      if (curr.confidence > prev.confidence) {
        merged[merged.length - 1] = curr;
      }
    } else {
      merged.push(curr);
    }
  }
  return merged;
}

// ─────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  const ytId = args.ytId;
  if (!ytId) {
    console.error('Missing --ytId <YouTube-video-ID>');
    process.exit(2);
  }

  const apiKey = args.apiKey || process.env.OPENAI_API_KEY;
  const skipAI = args.skipAI || !apiKey;

  if (skipAI) {
    console.log('⚠️  No OPENAI_API_KEY found. Running in screenshot-only mode (no AI analysis).');
    console.log('   Set OPENAI_API_KEY env var or use --apiKey to enable AI analysis.\n');
  }

  const ytdlp = findYtDlp();
  if (!ytdlp) {
    console.error('yt-dlp not found. Install: winget install yt-dlp');
    process.exit(2);
  }

  const outDir = path.resolve(
    args.outDir || path.join(process.cwd(), '..', '..', 'docs', 'youtube', 'chapters')
  );
  fs.mkdirSync(outDir, { recursive: true });

  const screenshotDir = path.join(outDir, ytId);
  fs.mkdirSync(screenshotDir, { recursive: true });

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'yt-ai-scan-'));
  const tempVideo = path.join(tempDir, `${ytId}.mp4`);

  console.log(`\n🎬 AI Chapter Detection for ${ytId}`);
  console.log('━'.repeat(50));

  try {
    // ─── Step 1: Download ───
    console.log('\n📥 Step 1: Downloading video (low quality)...');
    await run(ytdlp, [
      '-f',
      'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
      '--merge-output-format',
      'mp4',
      '-o',
      tempVideo,
      '--no-playlist',
      `https://www.youtube.com/watch?v=${ytId}`,
    ]);

    if (!fs.existsSync(tempVideo)) throw new Error('Download failed');
    console.log('   ✓ Download complete');

    // ─── Step 2: Detect boundaries ───
    console.log('\n🔍 Step 2: Detecting chapter boundaries...');

    // Black frames
    console.log('   → Scanning black frames...');
    const blackResult = await run(
      'ffmpeg',
      [
        '-hide_banner',
        '-i',
        tempVideo,
        '-vf',
        'blackdetect=d=0.3:pic_th=0.98',
        '-an',
        '-f',
        'null',
        '-',
      ],
      { captureStderr: true }
    );
    const blackEvents = parseBlackdetect(blackResult.stderr);
    console.log(`     Found ${blackEvents.length} black frame sequences`);

    // Silence
    console.log('   → Scanning silence...');
    const silenceResult = await run(
      'ffmpeg',
      [
        '-hide_banner',
        '-i',
        tempVideo,
        '-af',
        'silencedetect=noise=-35dB:d=0.5',
        '-f',
        'null',
        '-',
      ],
      { captureStderr: true }
    );
    const silenceEvents = parseSilencedetect(silenceResult.stderr);
    console.log(`     Found ${silenceEvents.length} silence periods`);

    // Scene changes (high threshold = significant changes only)
    console.log('   → Scanning scene changes...');
    const sceneResult = await run(
      'ffmpeg',
      [
        '-hide_banner',
        '-i',
        tempVideo,
        '-vf',
        "select='gt(scene,0.4)',showinfo",
        '-f',
        'null',
        '-',
      ],
      { captureStderr: true }
    );
    const sceneEvents = parseSceneChanges(sceneResult.stderr);
    console.log(`     Found ${sceneEvents.length} major scene changes`);

    // Additional: Lower threshold scene changes for silent films
    console.log('   → Scanning minor scene changes (for silent films)...');
    const sceneResult2 = await run(
      'ffmpeg',
      [
        '-hide_banner',
        '-i',
        tempVideo,
        '-vf',
        "select='gt(scene,0.25)',showinfo",
        '-f',
        'null',
        '-',
      ],
      { captureStderr: true }
    );
    const sceneEventsLow = parseSceneChanges(sceneResult2.stderr);
    console.log(`     Found ${sceneEventsLow.length} minor scene changes`);

    // ─── Step 3: Combine candidates ───
    console.log('\n📊 Step 3: Combining boundary candidates...');

    const candidates = new Map(); // time -> { sources, score }

    // Black frames are strong indicators
    for (const e of blackEvents) {
      const t = Math.round(e.end);
      if (!candidates.has(t)) candidates.set(t, { time: t, sources: [], score: 0 });
      const c = candidates.get(t);
      c.sources.push('black');
      c.score += 3; // High weight
    }

    // Silence + black = very strong
    for (const e of silenceEvents) {
      const t = Math.round(e.end);
      if (!candidates.has(t)) candidates.set(t, { time: t, sources: [], score: 0 });
      const c = candidates.get(t);
      c.sources.push('silence');
      c.score += 2;

      // Boost if near a black frame
      for (const [bt, bc] of candidates) {
        if (Math.abs(bt - t) < 3 && bc.sources.includes('black')) {
          bc.score += 2;
        }
      }
    }

    // Scene changes
    for (const e of sceneEvents) {
      const t = Math.round(e.time);
      if (!candidates.has(t)) candidates.set(t, { time: t, sources: [], score: 0 });
      const c = candidates.get(t);
      c.sources.push('scene');
      c.score += e.score > 0.6 ? 2 : 1;
    }

    // Minor scene changes (lower weight, but useful for silent films)
    for (const e of sceneEventsLow) {
      const t = Math.round(e.time);
      // Only add if not already a major scene change
      if (candidates.has(t) && candidates.get(t).sources.includes('scene')) continue;
      if (!candidates.has(t)) candidates.set(t, { time: t, sources: [], score: 0 });
      const c = candidates.get(t);
      c.sources.push('scene_minor');
      c.score += e.score > 0.35 ? 1 : 0.5;
    }

    // Sort by score and time
    let sortedCandidates = Array.from(candidates.values())
      .filter((c) => c.time > 10) // Skip first 10 sec
      .sort((a, b) => b.score - a.score || a.time - b.time);

    console.log(`   Found ${sortedCandidates.length} potential chapter points`);

    // Take top candidates (max 50 for AI analysis, or 30 for non-AI)
    const maxCandidates = skipAI ? 30 : 50;
    sortedCandidates = sortedCandidates.slice(0, maxCandidates);

    // ─── Step 4: Extract frames ───
    console.log(`\n📸 Step 4: Extracting ${sortedCandidates.length} screenshot frames...`);

    const frames = [];
    for (let i = 0; i < sortedCandidates.length; i++) {
      const c = sortedCandidates[i];
      const framePath = path.join(
        screenshotDir,
        `frame_${String(i).padStart(3, '0')}_${Math.round(c.time)}s.jpg`
      );

      try {
        await extractFrame(tempVideo, c.time, framePath);
        frames.push({
          index: i,
          timeSec: c.time,
          timestamp: toTimestamp(c.time),
          imagePath: framePath,
          sources: c.sources,
          score: c.score,
        });
      } catch (e) {
        console.warn(`   ⚠ Failed to extract frame at ${toTimestamp(c.time)}`);
      }

      if ((i + 1) % 10 === 0) {
        console.log(`   Extracted ${i + 1}/${sortedCandidates.length} frames`);
      }
    }
    console.log(`   ✓ Extracted ${frames.length} frames to ${screenshotDir}`);

    // ─── Step 5: AI Analysis ───
    let analyzedFrames = frames;

    if (!skipAI) {
      console.log('\n🤖 Step 5: AI Vision Analysis...');
      analyzedFrames = await batchAnalyzeFrames(frames, apiKey, 'Classic film/cartoon compilation');

      // Filter by AI confidence
      const highConfidence = analyzedFrames.filter(
        (f) => f.ai.isChapterBoundary && f.ai.confidence >= 0.6
      );
      console.log(`   ✓ AI identified ${highConfidence.length} high-confidence chapter boundaries`);
    } else {
      console.log('\n⏭️  Step 5: Skipping AI analysis (no API key)');
      // Use heuristic scoring without AI
      analyzedFrames = frames.map((f) => ({
        ...f,
        ai: {
          isChapterBoundary: f.score >= 3,
          confidence: Math.min(1, f.score / 5),
          title: `Chapter at ${f.timestamp}`,
          reason: `Score ${f.score} from: ${f.sources.join(', ')}`,
          contentType: f.sources.includes('black') ? 'black_frame' : 'scene_change',
        },
      }));
    }

    // ─── Step 6: Build chapter list ───
    console.log('\n📝 Step 6: Building chapter list...');

    const chapters = analyzedFrames
      .filter((f) => f.ai.isChapterBoundary && f.ai.confidence >= 0.5)
      .map((f) => ({
        time: f.timeSec,
        title: f.ai.title || `Chapter at ${f.timestamp}`,
        confidence: f.ai.confidence,
        reason: f.ai.reason,
        type: f.ai.contentType,
      }));

    // Merge nearby and sort
    const mergedChapters = mergeNearbyTimestamps(chapters, 60);

    // Always start with 00:00
    if (mergedChapters.length === 0 || mergedChapters[0].time > 5) {
      mergedChapters.unshift({ time: 0, title: 'Intro & Start', confidence: 1, type: 'intro' });
    }

    // ─── Step 7: Output ───
    console.log('\n💾 Step 7: Writing output files...');

    // Chapter file
    const outPath = path.join(outDir, `${ytId}.txt`);
    const lines = ['CHAPTERS / KAPITEL:'];
    for (const ch of mergedChapters) {
      lines.push(`${toTimestamp(ch.time)} - ${ch.title}`);
    }
    fs.writeFileSync(outPath, lines.join('\n') + '\n', 'utf8');
    console.log(`   ✓ Chapters: ${outPath}`);

    // Detailed JSON report
    const reportPath = path.join(outDir, `${ytId}_analysis.json`);
    const report = {
      ytId,
      analyzedAt: new Date().toISOString(),
      aiEnabled: !skipAI,
      detection: {
        blackFrames: blackEvents.length,
        silencePeriods: silenceEvents.length,
        sceneChanges: sceneEvents.length,
        totalCandidates: candidates.size,
        extractedFrames: frames.length,
      },
      chapters: mergedChapters,
      allAnalyzedFrames: analyzedFrames.map((f) => ({
        time: f.timeSec,
        timestamp: f.timestamp,
        sources: f.sources,
        score: f.score,
        ai: f.ai,
        imagePath: path.basename(f.imagePath),
      })),
    };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf8');
    console.log(`   ✓ Analysis report: ${reportPath}`);

    // ─── Summary ───
    console.log('\n' + '═'.repeat(50));
    console.log('✅ CHAPTER DETECTION COMPLETE');
    console.log('═'.repeat(50));
    console.log(`\n📺 Video: https://youtube.com/watch?v=${ytId}`);
    console.log(`📁 Screenshots: ${screenshotDir}`);
    console.log(`📝 Chapters (${mergedChapters.length}):\n`);

    for (const ch of mergedChapters.slice(0, 15)) {
      const conf = skipAI ? '' : ` [${Math.round(ch.confidence * 100)}%]`;
      console.log(`   ${toTimestamp(ch.time)} - ${ch.title}${conf}`);
    }
    if (mergedChapters.length > 15) {
      console.log(`   ... and ${mergedChapters.length - 15} more`);
    }

    console.log('\n💡 Tips:');
    console.log('   - Review screenshots in the chapters folder');
    console.log('   - Edit the .txt file to refine chapter titles');
    if (skipAI) {
      console.log('   - Set OPENAI_API_KEY for AI-powered title detection');
    }
  } finally {
    // Cleanup temp video
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch {
      /* ignore */
    }
  }
}

main().catch((e) => {
  console.error('\n❌ Failed:', e?.message || e);
  process.exit(1);
});
