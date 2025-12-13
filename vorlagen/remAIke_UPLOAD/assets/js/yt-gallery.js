// assets/js/yt-gallery.js
// Dedicated gallery module — isolated from main slider code.
export function initGallery(opts = {}) {
    const ytGallery = document.getElementById('yt-gallery');
    const ytSearch = document.getElementById('yt-search');
    const ytFilter = document.getElementById('yt-filter');
    const loadMoreBtn = document.getElementById('yt-load-more');
    const ytChannelName = document.getElementById('yt-channel-name');

    const PAGE_SIZE = opts.pageSize || 8;
    const skipApi = opts.skipApi === true || window.__YT_GALLERY_SKIP_API__ === true;
    let pageNum = 1;

    // small shared preview overlay
    let preview = document.getElementById('gallery-hover-preview');
    if (!preview) {
        preview = document.createElement('video');
        preview.id = 'gallery-hover-preview';
        preview.style.position = 'absolute';
        preview.style.width = '220px';
        preview.style.height = '124px';
        preview.style.objectFit = 'cover';
        preview.style.display = 'none';
        preview.muted = true;
        preview.playsInline = true;
        preview.loop = true;
        preview.style.borderRadius = '6px';
        preview.style.boxShadow = '0 6px 20px rgba(0,0,0,0.5)';
        document.body.appendChild(preview);
    }

    let youtubeVideos = opts.fallback || [];

    function getFilteredVideos() {
        const q = (ytSearch?.value || '').toLowerCase();
        const f = (ytFilter?.value || 'all');
        return youtubeVideos.filter(v => {
            const matchesQuery = q === '' || (v.title && v.title.toLowerCase().includes(q)) || (v.meta && v.meta.toLowerCase().includes(q));
            const matchesFilter = f === 'all' || (f === 'restored' && v.meta && v.meta.toLowerCase().includes('restor')) || (f === 'archive' && v.meta && v.meta.toLowerCase().includes('archive'));
            return matchesQuery && matchesFilter;
        });
    }

    function renderYouTubeGallery() {
        if (!ytGallery) return;
        ytGallery.innerHTML = '';
        const list = getFilteredVideos();
        const visibleList = list.slice(0, PAGE_SIZE * pageNum);
        visibleList.forEach((v, i) => {
            const thumb = document.createElement('div');
            thumb.className = 'yt-thumb' + (i === 0 ? ' active' : '');
            const thumbUrl = v.thumb || (v.id ? `https://img.youtube.com/vi/${v.id}/mqdefault.jpg` : 'assets/video-thumbnail.svg');
            thumb.innerHTML = `
                <img src="${thumbUrl}" alt="${v.title}">
                <div class="yt-play-badge">▶</div>
                <div class="yt-card-info">
                    <div class="yt-card-title">${v.title}</div>
                    <div class="yt-card-meta">${v.meta || ''}</div>
                </div>
            `;
            if (v.comparisonId) {
                const mappedBadge = document.createElement('div');
                mappedBadge.className = 'yt-mapped-badge';
                mappedBadge.textContent = 'Mapped';
                mappedBadge.style.position = 'absolute';
                mappedBadge.style.top = '8px';
                mappedBadge.style.right = '8px';
                mappedBadge.style.padding = '4px 6px';
                mappedBadge.style.background = 'rgba(0,0,0,0.6)';
                mappedBadge.style.color = 'var(--accent)';
                mappedBadge.style.borderRadius = '4px';
                thumb.appendChild(mappedBadge);
            }
            // Add a CTA if this video maps to a local comparison
            if (v.comparisonId) {
                const btn = document.createElement('button');
                btn.className = 'yt-compare-btn';
                btn.textContent = 'View Comparison';
                btn.style.position = 'absolute';
                btn.style.bottom = '10px';
                btn.style.right = '10px';
                btn.style.padding = '6px 8px';
                btn.style.borderRadius = '4px';
                btn.style.background = 'var(--accent)';
                btn.style.color = '#000';
                btn.style.cursor = 'pointer';
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    // Dispatch gallery-select but with comparisonId
                    const ev = new CustomEvent('gallery-select', { detail: { comparisonId: v.comparisonId, youtubeId: v.id }, bubbles: true });
                    document.dispatchEvent(ev);
                });
                thumb.appendChild(btn);
            }

            // on click -> set active and dispatch event
            thumb.addEventListener('click', () => {
                document.querySelectorAll('.yt-thumb').forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
                // Dispatch a global event that other parts of the app can listen to
                const ev = new CustomEvent('gallery-select', { detail: { id: v.id, title: v.title }, bubbles: true });
                document.dispatchEvent(ev);
            });

            // Hover preview
            thumb.addEventListener('mousemove', (e) => {
                if (!v.preview) return;
                preview.style.left = (e.pageX + 12) + 'px';
                preview.style.top = (e.pageY + 12) + 'px';
            });
            thumb.addEventListener('mouseenter', () => {
                if (!v.preview) return;
                preview.src = v.preview;
                preview.style.display = 'block';
                preview.play().catch(() => {});
            });
            thumb.addEventListener('mouseleave', () => {
                preview.pause();
                preview.style.display = 'none';
                preview.src = '';
            });

            ytGallery.appendChild(thumb);
        });

        // Show / hide load-more
        if (loadMoreBtn) {
            if (list.length > PAGE_SIZE * pageNum) {
                loadMoreBtn.classList.add('show');
            } else {
                loadMoreBtn.classList.remove('show');
            }
        }
    }

    async function loadYouTubeVideos() {
        try {
            if (skipApi) {
                renderYouTubeGallery();
                return;
            }

            const resp = await fetch('/api/youtube/channel');
            if (resp.ok) {
                const data = await resp.json();
                if (data.videos && data.videos.length > 0) {
                    youtubeVideos = data.videos.map(v => ({ id: v.id, title: v.title, meta: v.publishedAt ? new Date(v.publishedAt).toLocaleDateString() : '', preview: v.preview || '' }));
                    if (data.channel?.title && ytChannelName) ytChannelName.textContent = data.channel.title;
                }
            } else {
                // On 404 or other non-OK, stay with fallback
                renderYouTubeGallery();
                return;
            }
        } catch (e) {
            console.warn('[Gallery] YouTube API failed, using fallback');
        }
        pageNum = 1;
        renderYouTubeGallery();
    }

    if (ytSearch) ytSearch.addEventListener('input', () => { pageNum = 1; renderYouTubeGallery(); });
    if (ytFilter) ytFilter.addEventListener('change', () => { pageNum = 1; renderYouTubeGallery(); });
    if (loadMoreBtn) loadMoreBtn.addEventListener('click', () => { pageNum += 1; renderYouTubeGallery(); });

    if (opts.fallback && opts.fallback.length) youtubeVideos = opts.fallback;

    loadYouTubeVideos();

    function setVideos(list) {
        youtubeVideos = list || [];
        pageNum = 1;
        renderYouTubeGallery();
    }

    return { renderYouTubeGallery, reload: loadYouTubeVideos, setVideos };
}

// Auto-init if yt-gallery present (legacy fallback)
if (!window.__YT_GALLERY_AUTO_DISABLED__) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (document.getElementById('yt-gallery')) {
                initGallery({ fallback: window.REMAIKE_FALLBACK || [], skipApi: false });
            }
        });
    } else {
        if (document.getElementById('yt-gallery')) {
            initGallery({ fallback: window.REMAIKE_FALLBACK || [], skipApi: false });
        }
    }
}
