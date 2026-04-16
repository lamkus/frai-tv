/**
 * channelAudit.js - Reads ALL videos from @remAIke_IT channel via YouTube API
 * and exports a complete inventory for optimization.
 *
 * Usage: node --experimental-modules src/services/channelAudit.js
 * Requires: YOUTUBE_API_KEY in .env
 */

import fs from 'node:fs/promises';
import path from 'node:path';

const CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ';
const OUTPUT_DIR = path.resolve(process.cwd(), 'tmp');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'channel_audit.json');

async function getUploadsPlaylistId(youtube) {
  const resp = await youtube.channels.list({
    part: ['contentDetails', 'snippet', 'statistics', 'brandingSettings'],
    id: [CHANNEL_ID],
  });

  const channel = resp?.data?.items?.[0];
  if (!channel) throw new Error('Channel not found');

  return {
    uploadsPlaylistId: channel.contentDetails.relatedPlaylists.uploads,
    channelInfo: {
      title: channel.snippet.title,
      description: channel.snippet.description,
      customUrl: channel.snippet.customUrl,
      country: channel.snippet.country,
      subscriberCount: channel.statistics.subscriberCount,
      videoCount: channel.statistics.videoCount,
      viewCount: channel.statistics.viewCount,
      keywords: channel.brandingSettings?.channel?.keywords || '',
      defaultLanguage: channel.brandingSettings?.channel?.defaultLanguage || '',
    },
  };
}

async function fetchAllPlaylistVideos(youtube, playlistId) {
  const videos = [];
  let pageToken = undefined;
  let page = 0;

  do {
    page++;
    console.log(`  Fetching page ${page}...`);

    const resp = await youtube.playlistItems.list({
      part: ['snippet', 'contentDetails'],
      playlistId,
      maxResults: 50,
      pageToken,
    });

    const items = resp?.data?.items || [];
    for (const item of items) {
      videos.push({
        ytId: item.snippet.resourceId.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        publishedAt: item.snippet.publishedAt,
        position: item.snippet.position,
        thumbnails: item.snippet.thumbnails,
      });
    }

    pageToken = resp?.data?.nextPageToken || undefined;
  } while (pageToken);

  return videos;
}

async function enrichWithVideoDetails(youtube, videos) {
  const enriched = [];
  const batchSize = 50;

  for (let i = 0; i < videos.length; i += batchSize) {
    const batch = videos.slice(i, i + batchSize);
    const ids = batch.map((v) => v.ytId);

    console.log(`  Enriching batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(videos.length / batchSize)}...`);

    const resp = await youtube.videos.list({
      part: ['snippet', 'contentDetails', 'status', 'statistics', 'localizations', 'recordingDetails'],
      id: ids,
    });

    const detailMap = new Map();
    for (const item of resp?.data?.items || []) {
      detailMap.set(item.id, item);
    }

    for (const video of batch) {
      const detail = detailMap.get(video.ytId);
      if (!detail) {
        enriched.push({ ...video, status: 'UNAVAILABLE' });
        continue;
      }

      enriched.push({
        ytId: video.ytId,
        title: detail.snippet.title,
        description: detail.snippet.description,
        publishedAt: detail.snippet.publishedAt,
        channelTitle: detail.snippet.channelTitle,
        tags: detail.snippet.tags || [],
        categoryId: detail.snippet.categoryId,
        defaultLanguage: detail.snippet.defaultLanguage || null,
        defaultAudioLanguage: detail.snippet.defaultAudioLanguage || null,
        liveBroadcastContent: detail.snippet.liveBroadcastContent,
        duration: detail.contentDetails.duration,
        dimension: detail.contentDetails.dimension,
        definition: detail.contentDetails.definition,
        caption: detail.contentDetails.caption,
        licensedContent: detail.contentDetails.licensedContent,
        privacyStatus: detail.status.privacyStatus,
        license: detail.status.license,
        embeddable: detail.status.embeddable,
        madeForKids: detail.status.madeForKids,
        selfDeclaredMadeForKids: detail.status.selfDeclaredMadeForKids,
        viewCount: parseInt(detail.statistics.viewCount || '0', 10),
        likeCount: parseInt(detail.statistics.likeCount || '0', 10),
        commentCount: parseInt(detail.statistics.commentCount || '0', 10),
        localizations: detail.localizations || {},
        recordingDate: detail.recordingDetails?.recordingDate || null,
        thumbnails: detail.snippet.thumbnails,
        status: 'LIVE',
      });
    }
  }

  return enriched;
}

async function fetchAllPlaylists(youtube) {
  const playlists = [];
  let pageToken = undefined;

  do {
    const resp = await youtube.playlists.list({
      part: ['snippet', 'status', 'contentDetails', 'localizations'],
      channelId: CHANNEL_ID,
      maxResults: 50,
      pageToken,
    });

    for (const p of resp?.data?.items || []) {
      playlists.push({
        id: p.id,
        title: p.snippet.title,
        description: p.snippet.description,
        privacyStatus: p.status.privacyStatus,
        itemCount: p.contentDetails.itemCount,
        defaultLanguage: p.snippet.defaultLanguage || null,
        localizations: p.localizations || {},
      });
    }

    pageToken = resp?.data?.nextPageToken || undefined;
  } while (pageToken);

  return playlists;
}

export async function runChannelAudit() {
  const { google } = await import('googleapis');

  const apiKey = process.env.YOUTUBE_API_KEY;
  if (!apiKey) throw new Error('YOUTUBE_API_KEY required');

  const youtube = google.youtube({ version: 'v3', auth: apiKey });

  console.log('=== Channel Audit: @remAIke_IT ===\n');

  // 1. Get channel info
  console.log('1. Fetching channel info...');
  const { uploadsPlaylistId, channelInfo } = await getUploadsPlaylistId(youtube);
  console.log(`   Channel: ${channelInfo.title}`);
  console.log(`   Videos: ${channelInfo.videoCount}`);
  console.log(`   Subscribers: ${channelInfo.subscriberCount}`);
  console.log(`   Uploads playlist: ${uploadsPlaylistId}\n`);

  // 2. Fetch all videos from uploads playlist
  console.log('2. Fetching all videos...');
  const basicVideos = await fetchAllPlaylistVideos(youtube, uploadsPlaylistId);
  console.log(`   Found ${basicVideos.length} videos\n`);

  // 3. Enrich with full details
  console.log('3. Enriching with details (tags, stats, localizations)...');
  const videos = await enrichWithVideoDetails(youtube, basicVideos);
  console.log(`   Enriched ${videos.length} videos\n`);

  // 4. Fetch playlists
  console.log('4. Fetching playlists...');
  const playlists = await fetchAllPlaylists(youtube);
  console.log(`   Found ${playlists.length} playlists\n`);

  // 5. Analyze
  const analysis = {
    totalVideos: videos.length,
    liveVideos: videos.filter((v) => v.status === 'LIVE').length,
    unavailable: videos.filter((v) => v.status === 'UNAVAILABLE').length,
    withTags: videos.filter((v) => v.tags?.length > 0).length,
    withoutTags: videos.filter((v) => !v.tags || v.tags.length === 0).length,
    withLocalizations: videos.filter((v) => Object.keys(v.localizations || {}).length > 0).length,
    withoutLocalizations: videos.filter((v) => Object.keys(v.localizations || {}).length === 0).length,
    withDefaultLanguage: videos.filter((v) => v.defaultLanguage).length,
    withoutDefaultLanguage: videos.filter((v) => !v.defaultLanguage).length,
    totalViews: videos.reduce((sum, v) => sum + (v.viewCount || 0), 0),
    totalLikes: videos.reduce((sum, v) => sum + (v.likeCount || 0), 0),
    categoryCounts: {},
    tagFrequency: {},
  };

  for (const v of videos) {
    const cat = v.categoryId || 'unknown';
    analysis.categoryCounts[cat] = (analysis.categoryCounts[cat] || 0) + 1;
    for (const tag of v.tags || []) {
      const t = tag.toLowerCase();
      analysis.tagFrequency[t] = (analysis.tagFrequency[t] || 0) + 1;
    }
  }

  // Sort tags by frequency
  analysis.topTags = Object.entries(analysis.tagFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 50)
    .map(([tag, count]) => ({ tag, count }));

  // 6. Save
  const result = {
    auditDate: new Date().toISOString(),
    channelInfo,
    analysis,
    playlists,
    videos,
  };

  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.writeFile(OUTPUT_FILE, JSON.stringify(result, null, 2), 'utf8');

  console.log('=== Audit Complete ===');
  console.log(`Total videos: ${analysis.totalVideos}`);
  console.log(`Live: ${analysis.liveVideos} | Unavailable: ${analysis.unavailable}`);
  console.log(`With tags: ${analysis.withTags} | Without: ${analysis.withoutTags}`);
  console.log(`With localizations: ${analysis.withLocalizations} | Without: ${analysis.withoutLocalizations}`);
  console.log(`With defaultLanguage: ${analysis.withDefaultLanguage} | Without: ${analysis.withoutDefaultLanguage}`);
  console.log(`Total views: ${analysis.totalViews.toLocaleString()}`);
  console.log(`Playlists: ${playlists.length}`);
  console.log(`\nSaved to: ${OUTPUT_FILE}`);

  return result;
}

// Run directly
if (process.argv[1]?.endsWith('channelAudit.js')) {
  import('dotenv/config').then(() => {
    runChannelAudit().catch((err) => {
      console.error('Audit failed:', err.message);
      process.exit(1);
    });
  });
}
