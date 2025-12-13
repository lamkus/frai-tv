/**
 * YouTube Slider/Carousel
 */

export function initYouTubeSlideshow() {
    // Support legacy markup (youtube-grid) and the main site markup (#yt-carousel)
    let grid = document.getElementById('youtube-grid');
    let cards = document.querySelectorAll('.youtube-card');
    let indicators = document.querySelectorAll('.youtube-indicators .indicator');
    const prev = document.getElementById('youtube-prev');
    const next = document.getElementById('youtube-next');

    // Fallback to the main site's carousel markup
    if ((!grid || grid.children.length === 0) && document.getElementById('yt-carousel')) {
        grid = document.getElementById('yt-carousel');
        cards = grid.querySelectorAll('.yt-item');
        indicators = grid.querySelectorAll('.yt-item'); // reuse as simple indicators
    }

    if (!grid || cards.length === 0) {
        console.warn('YouTube slider: Elements not found');
        return;
    }

    let currentIndex = 0;

    function updateSlider() {
        // Smooth slide animation
        const offset = currentIndex * (100 + 2); // 100% width + 2rem gap
        grid.style.transform = `translateX(-${currentIndex * 100}%)`;

        // Update active card
        cards.forEach((card, idx) => {
            card.classList.toggle('active', idx === currentIndex);
        });

        // Update indicators
        indicators.forEach((ind, idx) => {
            ind.classList.toggle('active', idx === currentIndex);
        });

        console.log(`YouTube slider: ${currentIndex + 1}/${cards.length}`);
    }

    if (next) {
        next.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % cards.length;
            updateSlider();
        });
    }

    if (prev) {
        prev.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + cards.length) % cards.length;
            updateSlider();
        });
    }

    // Click indicators to jump directly
    indicators.forEach((ind, idx) => {
        ind.addEventListener('click', () => {
            currentIndex = idx;
            updateSlider();
        });
    });

    // Auto-advance every 8 seconds
    const autoSlide = setInterval(() => {
        currentIndex = (currentIndex + 1) % cards.length;
        updateSlider();
    }, 8000);

    // Pause auto-slide on hover
    grid.addEventListener('mouseenter', () => clearInterval(autoSlide));

    updateSlider(); // Initial render
}
