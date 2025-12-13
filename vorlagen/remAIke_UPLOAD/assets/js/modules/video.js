import { state } from './store.js';
import { updateTimeline, updatePreviewLabel, populateGallery, updateSyncStatus } from './ui.js';

// ══════════════════════════════════════════════════════════════════════════════
// HLS VIDEO LOADING
// ══════════════════════════════════════════════════════════════════════════════
export function loadVideo(videoEl, src) {
    if (!src || !videoEl) return;

    if (src.endsWith('.m3u8')) {
        if (typeof Hls !== 'undefined' && Hls.isSupported()) {
            const hls = new Hls({
                capLevelToPlayerSize: true,
                maxBufferLength: 30,
                maxMaxBufferLength: 60
            });
            hls.loadSource(src);
            hls.attachMedia(videoEl);
            state.hlsInstances.push(hls);
        } else if (videoEl.canPlayType('application/vnd.apple.mpegurl')) {
            videoEl.src = src;
        }
    } else {
        videoEl.src = src;
    }
    videoEl.load();
}

// �?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?
// PLAYBACK RATE / SLOWMO CONTROL
// �?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?
export function setPlaybackRate(rate = 1) {
    state.slowmoRate = rate || 1;
    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal, state.zoomVideo].forEach(v => {
        if (v) v.playbackRate = state.slowmoRate;
    });
    // Return the latest drift after forcing a resync so QA widgets can read it
    return syncVideos();
}

// ══════════════════════════════════════════════════════════════════════════════
// BULLETPROOF VIDEO SYNCHRONIZATION (SMPTE ST 2059-2)
// ══════════════════════════════════════════════════════════════════════════════
let syncLoopActive = false;
const SYNC_THRESHOLD = 0.042; // 42ms (approx 1 frame at 24fps)
const SYNC_CHECK_INTERVAL = 100;

export function syncVideos() {
    // Master is always sliderEnhanced (or clickVideo if slider not present, but we use sliderEnhanced as ref)
    const master = state.sliderEnhanced || state.clickVideo;
    if (!master) {
        updateSyncStatus(0, 0);
        return 0;
    }

    const masterTime = master.currentTime;
    let maxDrift = 0;
    // Sync all other videos to master
    const slaves = [state.sliderOriginal, state.clickVideo].filter(v => v && v !== master);

    slaves.forEach((slave, idx) => {
        if (!slave || slave.readyState < 2) return;
        const drift = Math.abs(slave.currentTime - masterTime);
        if (drift > maxDrift) maxDrift = drift;
        if (drift > SYNC_THRESHOLD) {
            try {
                slave.currentTime = masterTime;
            } catch (e) {
                console.warn(`Sync failed for video ${idx}:`, e);
            }
        }
    });

    updateSyncStatus(maxDrift, masterTime);
    return maxDrift;
}

export function startSyncLoop() {
    if (syncLoopActive) return;
    syncLoopActive = true;

    function syncTick() {
        if (!syncLoopActive) return;
        syncVideos();
        setTimeout(() => requestAnimationFrame(syncTick), SYNC_CHECK_INTERVAL);
    }
    requestAnimationFrame(syncTick);
    console.log('✅ Video sync loop started');
}

export function stopSyncLoop() {
    syncLoopActive = false;
    console.log('⏹️ Video sync loop stopped');
}

// ══════════════════════════════════════════════════════════════════════════════
// PLAY/PAUSE CONTROLS
// ══════════════════════════════════════════════════════════════════════════════
export function playAll() {
    syncVideos();
    setPlaybackRate(state.slowmoRate);
    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
        if (v && v.paused) v.play().catch(e => console.warn('Play failed:', e));
    });
    state.isPlaying = true;
    const btnPlay = document.getElementById('btn-play');
    if (btnPlay) btnPlay.innerHTML = '<span>⏸</span>';
    startSyncLoop();
}

export function pauseAll() {
    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
        if (v && !v.paused) v.pause();
    });
    state.isPlaying = false;
    const btnPlay = document.getElementById('btn-play');
    if (btnPlay) btnPlay.innerHTML = '<span>▶</span>';
    stopSyncLoop();
}

// ══════════════════════════════════════════════════════════════════════════════
// FRAME STEPPING
// ══════════════════════════════════════════════════════════════════════════════
const FRAME_TIME = () => (1 / (state.masterFps || 24));

export function frameBack() {
    pauseAll();
    const master = state.sliderEnhanced || state.clickVideo;
    const newTime = Math.max(0, (master ? master.currentTime : 0) - FRAME_TIME());
    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
        if (v) v.currentTime = newTime;
    });
    updateTimeline();
}

export function frameForward() {
    pauseAll();
    const master = state.sliderEnhanced || state.clickVideo;
    const newTime = Math.min((master ? master.duration : 0) || 0, (master ? master.currentTime : 0) + FRAME_TIME());
    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
        if (v) v.currentTime = newTime;
    });
    updateTimeline();
}

export function seekRelative(seconds) {
    const master = state.sliderEnhanced || state.clickVideo;
    const newTime = Math.max(0, Math.min((master ? master.duration : 0) || 0, (master ? master.currentTime : 0) + seconds));
    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
        if (v) v.currentTime = newTime;
    });
    updateTimeline();
}

// ══════════════════════════════════════════════════════════════════════════════
// API: FETCH COMPARISONS
// ══════════════════════════════════════════════════════════════════════════════
export async function fetchComparisons() {
    try {
        const res = await fetch(`${state.VIDEO_SERVER}/api/comparisons`);
        const data = await res.json();
        state.COMPARISONS = data.comparisons.map(c => {
            let enhancedPath = c.enhanced;
            let originalPath = c.original;
            if (state.VIDEO_SERVER && state.VIDEO_SERVER.trim() !== '') {
                enhancedPath = `${state.VIDEO_SERVER}/hls/${c.id}/enhanced.m3u8`;
                originalPath = c.original ? `${state.VIDEO_SERVER}/hls/${c.id}/original.m3u8` : null;
            } else {
                enhancedPath = c.preview || c.enhanced || null;
                originalPath = c.preview || c.original || null;
            }
            return { ...c, enhanced: enhancedPath, original: originalPath };
        });
        populateDropdown();
        populateGallery();
        loadDefaultComparison();
    } catch (e) {
        console.error('Failed to fetch comparisons:', e);
        loadDefaultComparison();
        loadStaticGallery();
    }
}

export function populateDropdown() {
    if (!state.dropdown) return;
    state.COMPARISONS.forEach((comp, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = `🎬 ${comp.name}`;
        state.dropdown.appendChild(opt);
    });
    console.log(`📺 Loaded ${state.COMPARISONS.length} videos from API`);
}

export function loadDefaultComparison() {
    state.currentIdx = -1;
    if (state.dropdown) state.dropdown.value = 'default';

    state.hlsInstances.forEach(h => h.destroy());
    state.hlsInstances = [];

    const isStatic = !state.VIDEO_SERVER || state.VIDEO_SERVER.trim() === '';
    const originalSrc = isStatic ? state.DEFAULT_COMPARISON.original : `${state.VIDEO_SERVER}/${state.DEFAULT_COMPARISON.original}`;
    const enhancedSrc = isStatic ? state.DEFAULT_COMPARISON.enhanced : `${state.VIDEO_SERVER}/${state.DEFAULT_COMPARISON.enhanced}`;

    console.log('Loading default comparison:', { originalSrc, enhancedSrc });

    // Load into slider videos (always needed for slider mode)
    if (state.sliderEnhanced) loadVideo(state.sliderEnhanced, enhancedSrc);
    if (state.sliderOriginal) loadVideo(state.sliderOriginal, originalSrc);

    // Load into click video (default mode)
    // Start with ORIGINAL
    if (state.clickVideo) {
        loadVideo(state.clickVideo, originalSrc);
        state.isEnhanced = false;
        updatePreviewLabel();
    }

    [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
        if (v) {
            v.loop = true;
            v.muted = true;
            v.play().catch(e => console.warn('Autoplay blocked:', e));
        }
    });
    setPlaybackRate(state.slowmoRate);
    state.isPlaying = true;
    startSyncLoop();
    console.log('✅ Loaded: Korn – Freak On a Leash (Licensed Preview)');
}

export function loadComparison(idx) {
    state.currentIdx = idx;
    const comp = state.COMPARISONS[idx];
    if (!comp) {
        console.error('Comparison not found:', idx);
        return;
    }

    if (state.dropdown) state.dropdown.value = idx;

    state.hlsInstances.forEach(h => h.destroy());
    state.hlsInstances = [];

    console.log('Loading comparison:', comp.name, { enhanced: comp.enhanced, original: comp.original });

    const originalSrc = comp.original || comp.enhanced; // Fallback if no original
    const enhancedSrc = comp.enhanced;

    if (state.sliderEnhanced) loadVideo(state.sliderEnhanced, enhancedSrc);
    if (state.sliderOriginal) loadVideo(state.sliderOriginal, originalSrc);

    if (state.clickVideo) {
        // Reset to original when loading new video
        loadVideo(state.clickVideo, originalSrc);
        state.isEnhanced = false;
        updatePreviewLabel();
    }

    setPlaybackRate(state.slowmoRate);
    console.log(`✅ Loaded: ${comp.name}`);
    if (state.isPlaying) playAll();
}

function loadStaticGallery() {
    const galleryGrid = document.getElementById('galleryGrid');
    if (!galleryGrid) return;

    // Public Domain Gallery (CONTEXT.md)
    const staticData = [
        { title: 'Felix the Cat - Feline Follies', year: '1919', youtube: 'https://www.youtube.com/@remAIke_IT' },
        { title: 'Felix the Cat - Felix in Love', year: '1922', youtube: 'https://www.youtube.com/@remAIke_IT' },
        { title: 'Betty Boop - Snow White', year: '1933', youtube: 'https://www.youtube.com/@remAIke_IT' },
        { title: 'Superman - Destruction Inc.', year: '1942', youtube: 'https://www.youtube.com/@remAIke_IT' },
        { title: 'Superman - Terror on the Midway', year: '1942', youtube: 'https://www.youtube.com/@remAIke_IT' },
        { title: 'Popeye - Popeye the Sailor Meets Sindbad', year: '1936', youtube: 'https://www.youtube.com/@remAIke_IT' },
        { title: 'Steamboat Willie', year: '1928', youtube: 'https://www.youtube.com/@remAIke_IT' }
    ];

    galleryGrid.innerHTML = '';

    staticData.forEach(item => {
        const card = document.createElement('div');
        card.className = 'gallery-card';
        card.innerHTML = `
            <div class="gallery-video">
                <div class="gallery-placeholder">🎬</div>
                <div class="gallery-overlay">
                    <span>Klicken für Vergleich →</span>
                </div>
            </div>
            <div class="gallery-info">
                <div class="gallery-header">
                    <div class="gallery-title">${item.title}</div>
                    <a href="${item.youtube}" target="_blank" class="gallery-youtube-btn" title="Watch on YouTube"><span class="yt-icon">▶</span></a>
                </div>
                <div class="gallery-meta">${item.year} • 8K Restored</div>
            </div>
        `;
        galleryGrid.appendChild(card);
    });
}
