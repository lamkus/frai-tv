/**
 * Load and display video comparisons dynamically
 * Pairs "original" and "enhanced" videos side-by-side
 * Frontend shows NO technical pipeline names (internal only)
 */

class VideoComparison {
    constructor() {
        this.comparisons = [];
        this.loadConfig();
    }

    async loadConfig() {
        try {
            const response = await fetch('/assets/video/comparisons.json');
            const data = await response.json();
            this.comparisons = data.comparisons || [];
            this.renderComparisons();
        } catch (error) {
            console.warn('Could not load comparison config:', error);
            this.renderPlaceholder();
        }
    }

    cleanTitle(title) {
        // Remove internal pipeline suffixes and metadata for display
        return title
            .replace(/_sls$/, '')
            .replace('_starlight_mini', '')
            .replace(/_nyx\d+/, '')
            .replace(/_(\d+)$/, '')
            .replace(/^\d+\.\d+\.\d+\s+/, '')  // Remove date prefix
            .replace(/_/g, ' ')
            .trim();
    }

    renderComparisons() {
        const grid = document.getElementById('showcaseGrid');
        if (!grid) return;

        if (this.comparisons.length === 0) {
            grid.innerHTML = '<p>Vergleiche werden geladen...</p>';
            return;
        }

        grid.innerHTML = this.comparisons.map((comp, idx) => `
            <div class="showcase-card" data-tilt>
                <div class="video-quality-badge">8K Enhanced</div>
                <div class="comparison-container video-comparison-slider" data-video-comparison="${idx}">
                    <div class="video-comparison-wrapper">
                        <div class="comparison-original">
                            <video width="100%" height="100%"
                                   title="Originalmaterial" muted playsinline>
                                <source src="/assets/video/clips/${comp.original}" type="video/mp4">
                                Ihr Browser unterstützt das Video-Tag nicht.
                            </video>
                            <span class="comparison-label">Original</span>
                        </div>
                        <div class="comparison-enhanced">
                            <video width="100%" height="100%"
                                   title="Restauriert zu 8K" muted playsinline>
                                <source src="/assets/video/clips/${comp.enhanced}" type="video/mp4">
                                Ihr Browser unterstützt das Video-Tag nicht.
                            </video>
                            <span class="comparison-label">Restauriert</span>
                        </div>
                    </div>
                    <div class="video-comparison-slider-handle"></div>
                </div>
                <div class="showcase-info">
                    <h3>${this.cleanTitle(comp.title)}</h3>
                    <p class="quality-spec">Archivmaterial • Vollständig restauriert zu 8K</p>
                </div>
            </div>
        `).join('');

        // Reinitialize tilt effect
        if (window.VanillaTilt) {
            VanillaTilt.init(document.querySelectorAll('[data-tilt]'));
        }

        // Initialize video sliders (merge with screenshot slider logic)
        this.initializeVideoSliders();
    }

    initializeVideoSliders() {
        document.querySelectorAll('.video-comparison-slider').forEach(container => {
            const handle = container.querySelector('.video-comparison-slider-handle');
            const wrapper = container.querySelector('.video-comparison-wrapper');
            const enhanced = container.querySelector('.comparison-enhanced');
            let isDragging = false;

            const updatePosition = (e) => {
                if (!isDragging) return;

                const rect = container.getBoundingClientRect();
                let x = e.clientX || (e.touches && e.touches[0].clientX) || 0;
                x = x - rect.left;
                x = Math.max(0, Math.min(x, rect.width));
                const percentage = (x / rect.width) * 100;

                handle.style.left = `${percentage}%`;
                enhanced.style.width = `${percentage}%`;
            };

            handle.addEventListener('mousedown', () => isDragging = true);
            handle.addEventListener('touchstart', () => isDragging = true, { passive: true });

            document.addEventListener('mouseup', () => isDragging = false);
            document.addEventListener('touchend', () => isDragging = false);

            document.addEventListener('mousemove', updatePosition);
            document.addEventListener('touchmove', updatePosition, { passive: true });

            // Click anywhere on the container to set slider position
            container.addEventListener('click', (e) => {
                const rect = container.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const percentage = (x / rect.width) * 100;

                handle.style.left = `${percentage}%`;
                enhanced.style.width = `${percentage}%`;
            });

            // Initialize at 50%
            handle.style.left = '50%';
            enhanced.style.width = '50%';
        });
    }

    renderPlaceholder() {
        const grid = document.getElementById('showcaseGrid');
        if (!grid) return;

        grid.innerHTML = `
            <div class="showcase-card">
                <div class="video-quality-badge">Demo</div>
                <div class="video-placeholder">
                    <p>Vergleichsvideos werden vorbereitet...</p>
                </div>
                <div class="showcase-info">
                    <h3>Restaurierungs-Demo</h3>
                    <p class="quality-spec">Beispiele werden in Kürze verfügbar sein</p>
                </div>
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VideoComparison();
});
