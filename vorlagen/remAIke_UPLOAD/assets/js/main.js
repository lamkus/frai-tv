/**
 * remAIke.IT - Main Consolidated JavaScript
 * Modularized Architecture
 */

import { state } from './modules/store.js';
import { applyTranslations } from './modules/i18n.js';
import { initHeroEffects } from './modules/effects.js';
import {
    fetchComparisons,
    loadDefaultComparison,
    loadComparison,
    syncVideos,
    playAll,
    pauseAll,
    startSyncLoop,
    frameBack,
    frameForward
} from './modules/video.js';
import {
    toggleNav,
    toggleSliderMode,
    initSliderDrag,
    initZoomLens,
    initClickPreview,
    initTimeline,
    initB2BModal,
    initKeyboardShortcuts,
    initQALoop,
    initSmoothScroll,
    toggleFullscreen,
    updateTimeline,
    initSlowmoControl
} from './modules/ui.js';
import { initYouTubeSlideshow } from './modules/youtube-slider.js';

// ══════════════════════════════════════════════════════════════════════════════
// PWA SERVICE WORKER
// ══════════════════════════════════════════════════════════════════════════════
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('SW registered:', reg))
            .catch(err => console.log('SW registration failed:', err));
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize DOM references in state
    state.wrapper = document.getElementById('video-wrapper');
    state.clickVideo = document.getElementById('comparison-video');
    state.sliderEnhanced = document.getElementById('slider-enhanced');
    state.sliderOriginal = document.getElementById('slider-original');
    state.sliderHandle = document.getElementById('slider-handle');

    // Aliases for compatibility
    state.videoEnhanced = state.sliderEnhanced;
    state.videoOriginal = state.sliderOriginal;

    state.zoomLens = document.getElementById('zoom-lens');
    state.zoomVideo = document.getElementById('zoom-video');
    state.zoomLabel = document.getElementById('zoom-label');
    state.modeIndicator = document.getElementById('mode-indicator');
    state.clickOverlay = document.getElementById('click-overlay');
    state.shortcutsPanel = document.getElementById('shortcuts-panel');
    state.dropdown = document.getElementById('comparison-dropdown');
    state.rescanBtn = document.getElementById('btn-rescan');
    state.timelineScrubber = document.getElementById('timeline-scrubber');
    state.timeCurrent = document.getElementById('time-current');
    state.timeDuration = document.getElementById('time-duration');
    state.smpteDisplay = document.getElementById('smpte-readout');
    state.syncStatus = document.getElementById('sync-lock');
    state.slowmoSlider = document.getElementById('slowmo-slider');
    state.slowmoValue = document.getElementById('slowmo-value');

    // Nav toggle
    const navToggle = document.getElementById('nav-toggle');
    if (navToggle) navToggle.addEventListener('click', toggleNav);

    // Initialize language
    const stored = localStorage.getItem('remAIke_lang');
    const browserLang = (navigator.language || 'en').toLowerCase();
    let initialLang = stored || (browserLang.startsWith('de') ? 'de' : browserLang.startsWith('fr') ? 'fr' : browserLang.startsWith('es') ? 'es' : 'en');
    // Simple check if lang exists in our dict (we'd need to export translations to check properly, but this is fine)
    if (!['en', 'de', 'fr', 'es', 'mx'].includes(initialLang)) initialLang = 'en';
    applyTranslations(initialLang);

    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => applyTranslations(btn.getAttribute('data-lang')));
    });

    // Initialize all features
    initClickPreview();
    initSliderDrag();
    initTimeline();
    initSlowmoControl();
    initKeyboardShortcuts();
    initSmoothScroll();
    initHeroEffects();
    initB2BModal();
    initYouTubeSlideshow();
    initZoomLens();
    initQALoop();

    // Slider toggle handler
    const sliderToggle = document.getElementById('enable-slider');
    if (sliderToggle) {
        sliderToggle.addEventListener('change', (e) => toggleSliderMode(e.target.checked));
    }

    document.getElementById('btn-play')?.addEventListener('click', () => state.isPlaying ? pauseAll() : playAll());
    document.getElementById('btn-sync')?.addEventListener('click', syncVideos);
    document.getElementById('btn-fullscreen')?.addEventListener('click', toggleFullscreen);
    document.getElementById('btn-frame-back')?.addEventListener('click', frameBack);
    document.getElementById('btn-frame-forward')?.addEventListener('click', frameForward);

    // Dropdown change handler
    if (state.dropdown) {
        state.dropdown.addEventListener('change', (e) => {
            if (e.target.value === 'default') loadDefaultComparison();
            else loadComparison(parseInt(e.target.value));
        });
    }

    // Rescan button
    if (state.rescanBtn) {
        state.rescanBtn.addEventListener('click', async () => {
            state.rescanBtn.classList.add('loading');
            try {
                await fetch(`${state.VIDEO_SERVER}/api/scan`, { method: 'POST' });
                while (state.dropdown.options.length > 1) state.dropdown.remove(1);
                await fetchComparisons();
            } catch (e) {
                console.error('Rescan failed:', e);
            } finally {
                state.rescanBtn.classList.remove('loading');
            }
        });
    }

    // Video sync event listeners
    // Use sliderEnhanced as master for events
    if (state.sliderEnhanced) {
        state.sliderEnhanced.addEventListener('timeupdate', syncVideos);
        state.sliderEnhanced.addEventListener('seeked', syncVideos);
        state.sliderEnhanced.addEventListener('play', () => {
            [state.clickVideo, state.sliderOriginal].forEach(v => {
                if (v && v.paused) v.play().catch(() => {});
            });
            startSyncLoop();
        });
        state.sliderEnhanced.addEventListener('pause', () => {
            [state.clickVideo, state.sliderOriginal].forEach(v => {
                if (v && !v.paused) v.pause();
            });
        });
    }

    // Also attach to clickVideo in case it's the only one active
    if (state.clickVideo) {
         state.clickVideo.addEventListener('play', () => {
             state.isPlaying = true;
             const btnPlay = document.getElementById('btn-play');
             if (btnPlay) btnPlay.innerHTML = '<span>⏸</span>';
         });
         state.clickVideo.addEventListener('pause', () => {
             state.isPlaying = false;
             const btnPlay = document.getElementById('btn-play');
             if (btnPlay) btnPlay.innerHTML = '<span>▶</span>';
         });
         // Sync timeline from clickVideo if sliderEnhanced is not available or not playing
         state.clickVideo.addEventListener('timeupdate', () => {
             if (!state.sliderEnhanced || state.sliderEnhanced.paused) {
                 updateTimeline();
             }
         });
    }

    // Fetch comparisons from API
    await fetchComparisons();

    // Render verification badges if available
    try {
        const resp = await fetch('/assets/data/pairs_verification.json', { cache: 'no-store' });
        if (resp.ok) {
            const ver = await resp.json();
            const map = new Map();
            (ver.results || []).forEach(r => map.set(r.id, r));
            // decorate dropdown options
            if (state.dropdown) {
                for (let i = 0; i < state.dropdown.options.length; i++) {
                    const opt = state.dropdown.options[i];
                    const id = opt.value;
                    if (!id || id === 'default') continue;
                    const info = map.get(id);
                    if (info) {
                        const badge = info.ok && info.enhancedExists && info.originalExists ? '✅ Verified' : (!info.enhancedExists || !info.originalExists ? '⚠ Missing' : '❓ Review');
                        opt.text = opt.text + ' ' + badge;
                    }
                }
            }
        }
    } catch (_) {}

    console.log('✅ remAIke.IT Main initialized (Modular)');
});
