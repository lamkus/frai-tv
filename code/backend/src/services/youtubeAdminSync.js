function parseIso8601DurationToSeconds(input) {
  if (!input || typeof input !== 'string') return null;

  // Example: PT1H2M3S, PT15M, PT45S
  const match = input.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!match) return null;

  const hours = match[1] ? parseInt(match[1], 10) : 0;
  const minutes = match[2] ? parseInt(match[2], 10) : 0;
  const seconds = match[3] ? parseInt(match[3], 10) : 0;

  return hours * 3600 + minutes * 60 + seconds;
}

async function listAllPlaylistVideoIds(youtube, playlistId) {
  const ids = new Set();
  let pageToken = undefined;

  // playlistItems.list returns max 50 per page
  do {
    const resp = await youtube.playlistItems.list({
      part: ['snippet'],
      playlistId,
      maxResults: 50,
      pageToken,
    });

    const items = resp?.data?.items || [];
    for (const it of items) {
      const videoId = it?.snippet?.resourceId?.videoId;
      if (videoId) ids.add(videoId);
    }

    pageToken = resp?.data?.nextPageToken || undefined;
  } while (pageToken);

  return ids;
}

async function findPlaylistByExactTitle(youtube, title) {
  let pageToken = undefined;

  // We can only list "mine" playlists for the authenticated channel.
  do {
    const resp = await youtube.playlists.list({
      part: ['snippet', 'status'],
      mine: true,
      maxResults: 50,
      pageToken,
    });

    const items = resp?.data?.items || [];
    const found = items.find((p) => p?.snippet?.title === title);
    if (found?.id) return found;

    pageToken = resp?.data?.nextPageToken || undefined;
  } while (pageToken);

  return null;
}

async function createPlaylist(youtube, { title, description, privacyStatus = 'public' }) {
  const resp = await youtube.playlists.insert({
    part: ['snippet', 'status'],
    requestBody: {
      snippet: {
        title,
        description: description || '',
      },
      status: {
        privacyStatus,
      },
    },
  });

  return resp?.data;
}

async function findOrCreatePlaylist(youtube, { title, description, privacyStatus }) {
  const existing = await findPlaylistByExactTitle(youtube, title);
  if (existing) return existing;
  return createPlaylist(youtube, { title, description, privacyStatus });
}

async function addVideoToPlaylistIfMissing(youtube, playlistId, videoId, existingVideoIdsSet) {
  const exists = existingVideoIdsSet?.has?.(videoId);
  if (exists) return { added: false };

  await youtube.playlistItems.insert({
    part: ['snippet'],
    requestBody: {
      snippet: {
        playlistId,
        resourceId: {
          kind: 'youtube#video',
          videoId,
        },
      },
    },
  });

  if (existingVideoIdsSet) existingVideoIdsSet.add(videoId);
  return { added: true };
}

async function fetchVideoMetaMap(youtube, videoIds) {
  // Returns Map(videoId -> { title, durationSeconds })
  const map = new Map();

  const batchSize = 50;
  for (let i = 0; i < videoIds.length; i += batchSize) {
    const batch = videoIds.slice(i, i + batchSize);
    const resp = await youtube.videos.list({
      part: ['snippet', 'contentDetails'],
      id: batch,
      maxResults: batch.length,
    });

    const items = resp?.data?.items || [];
    for (const it of items) {
      const id = it?.id;
      if (!id) continue;
      const title = it?.snippet?.title || '';
      const durationIso = it?.contentDetails?.duration || null;
      const durationSeconds = parseIso8601DurationToSeconds(durationIso);
      map.set(id, { title, durationSeconds });
    }
  }

  return map;
}

function isCompilationVideo({ title, durationSeconds }) {
  const t = (title || '').toLowerCase();
  const keyword = /(marathon|compilation|collection|full|complete|stunden|hours|mega|8k|4k)/i.test(
    t
  );
  const long = typeof durationSeconds === 'number' && durationSeconds >= 30 * 60;
  return Boolean(keyword || long);
}

export async function syncSeriesPlaylists({ youtube, seriesName, videos }) {
  // videos: [{ ytId, title? }]
  const seriesTitleBase = seriesName;
  const episodesTitle = `${seriesTitleBase} — Episodes`;
  const compilationsTitle = `${seriesTitleBase} — Compilations`;

  const ytIds = videos.map((v) => v.ytId).filter(Boolean);
  const metaMap = await fetchVideoMetaMap(youtube, ytIds);

  const episodes = [];
  const compilations = [];

  for (const id of ytIds) {
    const meta = metaMap.get(id) || { title: '', durationSeconds: null };
    if (isCompilationVideo(meta)) compilations.push(id);
    else episodes.push(id);
  }

  const episodesPlaylist = await findOrCreatePlaylist(youtube, {
    title: episodesTitle,
    description: `All ${seriesTitleBase} episodes (auto-synced).`,
    privacyStatus: 'public',
  });

  const compilationsPlaylist = await findOrCreatePlaylist(youtube, {
    title: compilationsTitle,
    description: `All ${seriesTitleBase} compilations / marathons (auto-synced).`,
    privacyStatus: 'public',
  });

  const episodesExisting = await listAllPlaylistVideoIds(youtube, episodesPlaylist.id);
  const compilationsExisting = await listAllPlaylistVideoIds(youtube, compilationsPlaylist.id);

  let addedEpisodes = 0;
  let addedCompilations = 0;

  for (const id of episodes) {
    const r = await addVideoToPlaylistIfMissing(youtube, episodesPlaylist.id, id, episodesExisting);
    if (r.added) addedEpisodes += 1;
  }

  for (const id of compilations) {
    const r = await addVideoToPlaylistIfMissing(
      youtube,
      compilationsPlaylist.id,
      id,
      compilationsExisting
    );
    if (r.added) addedCompilations += 1;
  }

  return {
    seriesName,
    episodesPlaylistId: episodesPlaylist.id,
    compilationsPlaylistId: compilationsPlaylist.id,
    episodesCount: episodes.length,
    compilationsCount: compilations.length,
    addedEpisodes,
    addedCompilations,
  };
}

export async function createOrAddPlaylistItem({ youtube, playlistId, videoId }) {
  await youtube.playlistItems.insert({
    part: ['snippet'],
    requestBody: {
      snippet: {
        playlistId,
        resourceId: { kind: 'youtube#video', videoId },
      },
    },
  });
}

export async function createPlaylistAdmin({ youtube, title, description, privacyStatus }) {
  return createPlaylist(youtube, { title, description, privacyStatus });
}

export async function listMyPlaylistsAdmin({ youtube }) {
  const all = [];
  let pageToken = undefined;

  do {
    const resp = await youtube.playlists.list({
      part: ['snippet', 'status', 'contentDetails'],
      mine: true,
      maxResults: 50,
      pageToken,
    });

    const items = resp?.data?.items || [];
    for (const p of items) {
      all.push({
        id: p.id,
        title: p?.snippet?.title || '',
        description: p?.snippet?.description || '',
        privacyStatus: p?.status?.privacyStatus || null,
        itemCount: p?.contentDetails?.itemCount ?? null,
      });
    }

    pageToken = resp?.data?.nextPageToken || undefined;
  } while (pageToken);

  return all;
}
