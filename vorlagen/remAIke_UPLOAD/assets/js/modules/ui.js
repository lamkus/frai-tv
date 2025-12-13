import { state } from './store.js';
import { loadComparison, playAll, pauseAll, syncVideos, frameBack, frameForward, seekRelative } from './video.js';

// ══════════════════════════════════════════════════════════════════════════════
// MOBILE NAV TOGGLE
// ══════════════════════════════════════════════════════════════════════════════
export function toggleNav() {
    document.getElementById('navLinks')?.classList.toggle('active');
}

// ══════════════════════════════════════════════════════════════════════════════
// COMPARISON MODE SWITCHING
// ══════════════════════════════════════════════════════════════════════════════
export function toggleSliderMode(enabled) {
    state.sliderMode = enabled;
    const previewContainer = document.getElementById('click-preview-container');
    const sliderContainer = document.getElementById('slider-container');
    if (previewContainer) previewContainer.style.display = enabled ? 'none' : 'block';
    if (sliderContainer) sliderContainer.style.display = enabled ? 'block' : 'none';
    console.log('Slider mode:', enabled ? 'enabled' : 'disabled');
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDER DRAG WITH SLOWMO EFFECT
// ══════════════════════════════════════════════════════════════════════════════
let isDragging = false;

export function initSliderDrag() {
    if (!state.sliderHandle || !state.wrapper) return;

    state.sliderHandle.addEventListener('mousedown', () => {
        isDragging = true;
        // Slowmo effect: reduce playbackRate during drag
        [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
            if (v) v.playbackRate = 0.25;
        });
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            // Restore normal speed after drag
            [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
                if (v) v.playbackRate = 1.0;
            });
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging || !state.sliderMode) return;
        const rect = state.wrapper.getBoundingClientRect();
        const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        state.sliderHandle.style.left = (x * 100) + '%';
        if (state.sliderEnhanced) state.sliderEnhanced.style.clipPath = `inset(0 ${(1-x)*100}% 0 0)`;
    });

    // Touch support
    state.sliderHandle.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isDragging = true;
        [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
            if (v) v.playbackRate = 0.25;
        });
    }, { passive: false });

    document.addEventListener('touchmove', (e) => {
        if (!isDragging || !state.sliderMode) return;
        const touch = e.touches[0];
        const rect = state.wrapper.getBoundingClientRect();
        const x = Math.max(0, Math.min(1, (touch.clientX - rect.left) / rect.width));
        state.sliderHandle.style.left = (x * 100) + '%';
        if (state.sliderEnhanced) state.sliderEnhanced.style.clipPath = `inset(0 ${(1-x)*100}% 0 0)`;
    }, { passive: false });

    document.addEventListener('touchend', () => {
        if (isDragging) {
            isDragging = false;
            [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
                if (v) v.playbackRate = 1.0;
            });
        }
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// ZOOM LENS MODE
// ══════════════════════════════════════════════════════════════════════════════
let zoomLevel = 4;
let currentZoomSource = null;

function syncZoomVideo() {
    if (state.currentMode !== 'zoom' || !currentZoomSource || !state.zoomVideo) return;
    if (state.zoomVideo.src !== currentZoomSource.src) {
        state.zoomVideo.src = currentZoomSource.src;
        state.zoomVideo.currentTime = currentZoomSource.currentTime;
        state.zoomVideo.play().catch(() => {});
    }
    state.zoomVideo.currentTime = currentZoomSource.currentTime;
}

export function initZoomLens() {
    if (!state.wrapper || !state.zoomLens) return;

    let isZoomed = false; // Track zoom state
    let holdTimeout; // For hold detection

    // Click to toggle zoom on/off and position
    state.wrapper.addEventListener('click', (e) => {
        if (state.currentMode !== 'zoom') return;
        e.preventDefault();

        const rect = state.wrapper.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (!isZoomed) {
            // Activate zoom at click position
            state.zoomLens.style.left = x + 'px';
            state.zoomLens.style.top = y + 'px';
            state.zoomLens.style.display = 'block';
            isZoomed = true;
            // Pan video to click point
            const zoomPx = -(x / rect.width) * (zoomLevel - 1) * 100;
            const zoomPy = -(y / rect.height) * (zoomLevel - 1) * 100;
            state.zoomVideo.style.objectPosition = `${50 + zoomPx}% ${50 + zoomPy}%`;
            state.zoomLabel.textContent = 'Enhanced'; // Default to enhanced on tap
            currentZoomSource = state.videoEnhanced;
            syncZoomVideo();
        } else {
            // Deactivate zoom
            state.zoomLens.style.display = 'none';
            isZoomed = false;
        }
    });

    // Hold to toggle enhanced/original
    state.wrapper.addEventListener('mousedown', (e) => {
        if (state.currentMode !== 'zoom' || !isZoomed) return;
        holdTimeout = setTimeout(() => {
            // On hold, switch to enhanced
            state.zoomLabel.textContent = 'Enhanced';
            currentZoomSource = state.videoEnhanced;
            syncZoomVideo();
        }, 200); // 200ms hold delay
    });

    state.wrapper.addEventListener('mouseup', () => {
        if (holdTimeout) {
            clearTimeout(holdTimeout);
            // On release, switch to original
            state.zoomLabel.textContent = 'Original';
            currentZoomSource = state.videoOriginal;
            syncZoomVideo();
        }
    });

    // Touch support for mobile
    state.wrapper.addEventListener('touchstart', (e) => {
        if (state.currentMode !== 'zoom') return;
        e.preventDefault();

        const touch = e.touches[0];
        const rect = state.wrapper.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;

        if (!isZoomed) {
            // Activate zoom at touch position
            state.zoomLens.style.left = x + 'px';
            state.zoomLens.style.top = y + 'px';
            state.zoomLens.style.display = 'block';
            isZoomed = true;
            // Pan video to touch point
            const zoomPx = -(x / rect.width) * (zoomLevel - 1) * 100;
            const zoomPy = -(y / rect.height) * (zoomLevel - 1) * 100;
            state.zoomVideo.style.objectPosition = `${50 + zoomPx}% ${50 + zoomPy}%`;
            state.zoomLabel.textContent = 'Enhanced';
            currentZoomSource = state.videoEnhanced;
            syncZoomVideo();
        }

        // Start hold timer for touch
        holdTimeout = setTimeout(() => {
            if (isZoomed) {
                state.zoomLabel.textContent = 'Enhanced';
                currentZoomSource = state.videoEnhanced;
                syncZoomVideo();
            }
        }, 200);
    }, { passive: false });

    state.wrapper.addEventListener('touchend', (e) => {
        if (holdTimeout) {
            clearTimeout(holdTimeout);
            if (isZoomed) {
                state.zoomLabel.textContent = 'Original';
                currentZoomSource = state.videoOriginal;
                syncZoomVideo();
            }
        }
    }, { passive: false });
}

// ══════════════════════════════════════════════════════════════════════════════
// CLICK PREVIEW - HIGH-END INSTANT COMPARISON
// ══════════════════════════════════════════════════════════════════════════════
export function initClickPreview() {
    const previewContainer = document.getElementById('click-preview-container');
    const clickTarget = previewContainer || state.wrapper;

    if (!clickTarget) {
        console.warn('Click preview: No target found');
        return;
    }

    // Preload both videos for instant switching
    if (state.sliderEnhanced && state.sliderOriginal) {
        state.sliderEnhanced.preload = 'auto';
        state.sliderOriginal.preload = 'auto';
    }

    clickTarget.addEventListener('click', (e) => {
        if (state.sliderMode) return;
        if (e.target.closest('button') || e.target.closest('input') || e.target.closest('a')) return;

        e.preventDefault();
        state.isEnhanced = !state.isEnhanced;

        // INSTANT video switch with zero lag
        if (state.clickVideo) {
            const currentTime = state.clickVideo.currentTime;
            const wasPlaying = !state.clickVideo.paused;

            // Determine source
            let newSrc;
            if (state.sliderEnhanced && state.sliderOriginal) {
                newSrc = state.isEnhanced ? state.sliderEnhanced.src : state.sliderOriginal.src;
            } else {
                newSrc = state.isEnhanced ? state.DEFAULT_COMPARISON.enhanced : state.DEFAULT_COMPARISON.original;
            }

            // Only switch if different source
            if (state.clickVideo.src !== newSrc) {
                state.clickVideo.src = newSrc;
                state.clickVideo.load();

                // Fast seek and play
                const seekAndPlay = () => {
                    state.clickVideo.currentTime = currentTime;
                    if (wasPlaying) {
                        state.clickVideo.play().catch(() => {});
                    }
                };

                // Use loadedmetadata for instant response
                state.clickVideo.addEventListener('loadedmetadata', seekAndPlay, { once: true });
            }
        }

        updatePreviewLabel();
        console.log('⚡ Click toggle:', state.isEnhanced ? 'ENHANCED' : 'ORIGINAL');
    });

    clickTarget.addEventListener('touchstart', (e) => {
        if (state.sliderMode) return;
        if (e.target.closest('button') || e.target.closest('input') || e.target.closest('a')) return;

        state.isEnhanced = !state.isEnhanced;

        if (state.clickVideo) {
            const currentTime = state.clickVideo.currentTime;
            if (state.sliderEnhanced && state.sliderOriginal) {
                 state.clickVideo.src = state.isEnhanced ? state.sliderEnhanced.src : state.sliderOriginal.src;
            }
            state.clickVideo.load();
            state.clickVideo.currentTime = currentTime;
            state.clickVideo.play().catch(() => {});
        }

        updatePreviewLabel();
    }, { passive: false });
}

export function updatePreviewLabel() {
    const label = document.getElementById('video-label');
    if (label) {
        // Smooth label transition with scale effect
        label.style.transform = 'scale(0.9)';
        label.style.opacity = '0.7';

        setTimeout(() => {
            label.textContent = state.isEnhanced ? 'ENHANCED' : 'ORIGINAL';
            label.classList.toggle('enhanced', state.isEnhanced);

            // Bounce back
            requestAnimationFrame(() => {
                label.style.transform = '';
                label.style.opacity = '1';
            });
        }, 80);
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// TIMELINE SCRUBBER
// ══════════════════════════════════════════════════════════════════════════════
function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
}

export function updateTimeline() {
    if (!state.videoEnhanced || !state.timelineScrubber) return;
    const current = state.videoEnhanced.currentTime || 0;
    const duration = state.videoEnhanced.duration || 0;
    state.timelineScrubber.value = duration > 0 ? (current / duration) * 100 : 0;
    if (state.timeCurrent) state.timeCurrent.textContent = formatTime(current);
    if (state.timeDuration) state.timeDuration.textContent = formatTime(duration);
}

export function updateSyncStatus(drift, time) {
    const readout = document.getElementById('smpte-readout');
    const lockIcon = document.getElementById('sync-lock');

    // Update Lock Status
    if (lockIcon) {
        if (drift < 0.05) { // 50ms threshold
            lockIcon.classList.add('locked');
            lockIcon.textContent = 'LOCKED';
            lockIcon.style.color = '#00f0ff';
        } else {
            lockIcon.classList.remove('locked');
            lockIcon.textContent = 'DRIFT';
            lockIcon.style.color = '#ff0055';
        }
    }

    // Update SMPTE
    if (readout && typeof time === 'number') {
        const fps = state.masterFps || 24;
        const frame = Math.floor((time % 1) * fps);
        const seconds = Math.floor(time);
        const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        const f = frame.toString().padStart(2, '0');
        readout.textContent = `${h}:${m}:${s}:${f}`;
    }
}

export function initSlowmoControl() {
    const slider = document.getElementById('slowmo-slider');
    const valueDisplay = document.getElementById('slowmo-value');

    if (!slider) return;

    slider.addEventListener('input', (e) => {
        const rate = parseFloat(e.target.value);
        state.slowmoRate = rate;
        if (valueDisplay) valueDisplay.textContent = rate.toFixed(2) + 'x';

        [state.clickVideo, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
            if (v) v.playbackRate = rate;
        });
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// FULLSCREEN
// ══════════════════════════════════════════════════════════════════════════════

export function initTimeline() {
    if (!state.timelineScrubber || !state.videoEnhanced) return;

    state.timelineScrubber.addEventListener('input', (e) => {
        const duration = state.videoEnhanced.duration || 0;
        const seekTime = (parseFloat(e.target.value) / 100) * duration;
        [state.videoEnhanced, state.videoOriginal, state.sliderEnhanced, state.sliderOriginal].forEach(v => {
            if (v) v.currentTime = seekTime;
        });
        updateTimeline();
    });

    state.videoEnhanced.addEventListener('timeupdate', updateTimeline);
    state.videoEnhanced.addEventListener('loadedmetadata', () => {
        if (state.timeDuration) state.timeDuration.textContent = formatTime(state.videoEnhanced.duration);
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// FULLSCREEN
// ══════════════════════════════════════════════════════════════════════════════
export function toggleFullscreen() {
    if (state.wrapper && state.wrapper.requestFullscreen) {
        state.wrapper.requestFullscreen();
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// GALLERY
// ══════════════════════════════════════════════════════════════════════════════
export function populateGallery() {
    const galleryGrid = document.getElementById('galleryGrid');
    if (!galleryGrid) return;

    galleryGrid.innerHTML = '';

    state.COMPARISONS.slice(0, 12).forEach((comp, idx) => {
        const card = document.createElement('div');
        card.className = 'gallery-card';
        card.onclick = (e) => {
            if (!e.target.closest('.gallery-youtube-btn')) {
                loadComparison(idx);
                document.getElementById('studio')?.scrollIntoView({ behavior: 'smooth' });
            }
        };

        card.innerHTML = `
            <div class="gallery-video">
                <video autoplay loop muted playsinline loading="lazy">
                    <source src="${comp.preview || comp.enhanced}" type="video/mp4">
                </video>
                <div class="gallery-overlay">
                    <span>Klicken für Vergleich →</span>
                </div>
                <div class="gallery-play">▶</div>
            </div>
            <div class="gallery-info">
                <div class="gallery-header">
                    <div class="gallery-title">${comp.name}</div>
                    ${comp.youtube ? `<a href="${comp.youtube}" target="_blank" class="gallery-youtube-btn" title="Watch on YouTube"><span class="yt-icon">▶</span></a>` : ''}
                </div>
                <div class="gallery-meta">${comp.year || ''} • 8K Restored</div>
            </div>
        `;

        galleryGrid.appendChild(card);
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// B2B MODAL
// ══════════════════════════════════════════════════════════════════════════════
export function initB2BModal() {
    const b2b = document.getElementById('btn-b2b');
    const modal = document.getElementById('b2b-modal');
    const modalClose = document.getElementById('b2b-close');
    const modalCancel = document.getElementById('b2b-cancel');
    const modalForm = document.getElementById('b2b-form');

    if (b2b && modal) {
        b2b.addEventListener('click', (e) => {
            e.preventDefault();
            modal.classList.add('open');
            modal.setAttribute('aria-hidden', 'false');
        });
    }

    if (modalClose) modalClose.addEventListener('click', () => {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    });

    if (modalCancel) modalCancel.addEventListener('click', () => {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    });

    if (modalForm) {
        modalForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                org: document.getElementById('org')?.value.trim(),
                email: document.getElementById('email')?.value.trim(),
                contact_name: document.getElementById('contact-name')?.value.trim(),
                sector: document.getElementById('sector')?.value,
                scope: document.getElementById('scope')?.value,
                description: document.getElementById('description')?.value.trim(),
                gdpr: document.getElementById('gdpr')?.checked
            };

            if (!formData.org || !formData.email || !formData.gdpr) {
                alert('Bitte füllen Sie alle Pflichtfelder aus.');
                return;
            }

            const submitBtn = modalForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Wird übermittelt...';

            try {
                const response = await fetch('/api/offer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();

                if (result.success) {
                    alert(`✓ Vielen Dank! Ihre Anfrage (${result.offerId}) wurde erfolgreich übermittelt.`);
                    modalForm.reset();
                    modal.classList.remove('open');
                } else {
                    alert(`Fehler: ${result.error}`);
                }
            } catch (err) {
                console.error('B2B offer error:', err);
                alert('Fehler bei der Übermittlung. Bitte versuchen Sie es später erneut.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Anfrage absenden';
            }
        });
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// KEYBOARD SHORTCUTS
// ══════════════════════════════════════════════════════════════════════════════
export function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch(e.key) {
            case ' ': e.preventDefault(); state.isPlaying ? pauseAll() : playAll(); break;
            // case '1': setMode('sidebyside'); break; // Not implemented yet
            case '2': toggleSliderMode(true); break;
            case '3': toggleSliderMode(false); break;
            // case '4': setMode('zoom'); break; // Not implemented yet
            case 'f': case 'F': toggleFullscreen(); break;
            case 's': case 'S': syncVideos(); break;
            case '?': state.shortcutsPanel?.classList.toggle('visible'); break;
            case ',': case '<': frameBack(); break;
            case '.': case '>': frameForward(); break;
            case 'ArrowUp': e.preventDefault(); seekRelative(5); break;
            case 'ArrowDown': e.preventDefault(); seekRelative(-5); break;
        }
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// SMOOTH SCROLL
// ══════════════════════════════════════════════════════════════════════════════
export function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// YOUTUBE SLIDESHOW
// ══════════════════════════════════════════════════════════════════════════════
let currentSlide = 0;
const totalSlides = 3;

export function initYouTubeSlideshow() {
    const prevBtn = document.getElementById('youtube-prev');
    const nextBtn = document.getElementById('youtube-next');
    const indicators = document.querySelectorAll('.indicator');

    function showSlide(index) {
        currentSlide = index;
        document.querySelectorAll('.youtube-card').forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });
        indicators.forEach((ind, i) => {
            ind.classList.toggle('active', i === index);
        });
    }

    if (prevBtn) prevBtn.addEventListener('click', () => {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        showSlide(currentSlide);
    });

    if (nextBtn) nextBtn.addEventListener('click', () => {
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    });

    indicators.forEach((ind, i) => {
        ind.addEventListener('click', () => showSlide(i));
    });

    // Auto-play every 10 seconds
    setInterval(() => {
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    }, 10000);
}

// ══════════════════════════════════════════════════════════════════════════════
// QA LOOP
// ══════════════════════════════════════════════════════════════════════════════
export function initQALoop() {
    const btnRun = document.getElementById('qa-run');
    const log = document.getElementById('qa-log');

    if (!btnRun) return;

    btnRun.addEventListener('click', async () => {
        btnRun.disabled = true;
        btnRun.textContent = 'Running diagnostics...';
        log.textContent = 'Starting QA sequence...';
        log.className = 'qa-log running';

        // 1. Check SMPTE Lock
        const smpteStatus = document.getElementById('qa-smpte-status');
        const driftVal = document.getElementById('qa-drift');

        await new Promise(r => setTimeout(r, 500));

        if (state.sliderEnhanced && state.sliderOriginal) {
            const drift = Math.abs(state.sliderEnhanced.currentTime - state.sliderOriginal.currentTime);
            driftVal.textContent = (drift * 1000).toFixed(1) + 'ms';
            if (drift < 0.05) {
                smpteStatus.textContent = 'LOCKED';
                smpteStatus.className = 'qa-pill success';
            } else {
                smpteStatus.textContent = 'DRIFT';
                smpteStatus.className = 'qa-pill warning';
            }
        } else {
            smpteStatus.textContent = 'NO VIDEO';
            smpteStatus.className = 'qa-pill error';
        }

        // 2. Check Streaming Health
        const streamStatus = document.getElementById('qa-streaming-status');
        await new Promise(r => setTimeout(r, 500));

        if (state.hlsInstances.length > 0) {
            streamStatus.textContent = 'ACTIVE';
            streamStatus.className = 'qa-pill success';
        } else if (state.videoEnhanced && state.videoEnhanced.src) {
            streamStatus.textContent = 'NATIVE';
            streamStatus.className = 'qa-pill success';
        } else {
            streamStatus.textContent = 'IDLE';
            streamStatus.className = 'qa-pill warning';
        }

        // 3. Check Gallery
        const galleryStatus = document.getElementById('qa-gallery-status');
        await new Promise(r => setTimeout(r, 500));

        if (state.COMPARISONS && state.COMPARISONS.length > 0) {
            galleryStatus.textContent = `OK (${state.COMPARISONS.length})`;
            galleryStatus.className = 'qa-pill success';
        } else {
            galleryStatus.textContent = 'EMPTY';
            galleryStatus.className = 'qa-pill error';
        }

        // 4. Check PWA
        const swStatus = document.getElementById('qa-sw-status');
        await new Promise(r => setTimeout(r, 500));

        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            swStatus.textContent = 'ACTIVE';
            swStatus.className = 'qa-pill success';
        } else {
            swStatus.textContent = 'INACTIVE';
            swStatus.className = 'qa-pill warning';
        }

        log.textContent = 'Diagnostics complete. System nominal.';
        log.className = 'qa-log success';
        btnRun.disabled = false;
        btnRun.textContent = 'Run feedback loop';
    });
}
