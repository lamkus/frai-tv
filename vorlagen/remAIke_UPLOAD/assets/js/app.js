// Mobile Nav Toggle
function toggleNav() {
    document.getElementById('navLinks').classList.toggle('active');
}

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Video Compare - Drag Slider
const videoCompare = document.getElementById('videoCompare');
const videoBefore = videoCompare.querySelector('.video-before');
const videoAfter = videoCompare.querySelector('.video-after');
const sliderHandle = document.getElementById('sliderHandle');

let isDragging = false;
let sliderPos = 50; // percentage

// Sync videos on load and during playback
videoBefore.addEventListener('loadedmetadata', () => {
    videoAfter.currentTime = videoBefore.currentTime;
});

videoBefore.addEventListener('play', () => {
    videoAfter.currentTime = videoBefore.currentTime;
    videoAfter.play();
});

// Keep videos synced
setInterval(() => {
    if (Math.abs(videoBefore.currentTime - videoAfter.currentTime) > 0.1) {
        videoAfter.currentTime = videoBefore.currentTime;
    }
}, 500);

function updateSlider(x) {
    const rect = videoCompare.getBoundingClientRect();
    sliderPos = Math.max(0, Math.min(100, ((x - rect.left) / rect.width) * 100));

    sliderHandle.style.left = sliderPos + '%';
    sliderHandle.setAttribute('aria-valuenow', Math.round(sliderPos));
    videoAfter.style.clipPath = `inset(0 ${100 - sliderPos}% 0 0)`;
}

function startDrag(e) {
    isDragging = true;
    videoCompare.classList.add('dragging');
    // Slowmo effect: reduce playbackRate during drag
    videoBefore.playbackRate = 0.25;
    videoAfter.playbackRate = 0.25;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    updateSlider(clientX);
}

function doDrag(e) {
    if (!isDragging) return;
    e.preventDefault();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    updateSlider(clientX);
}

function stopDrag() {
    isDragging = false;
    videoCompare.classList.remove('dragging');
    // Restore normal speed after drag
    videoBefore.playbackRate = 1.0;
    videoAfter.playbackRate = 1.0;
}

// Mouse events
sliderHandle.addEventListener('mousedown', startDrag);
videoCompare.addEventListener('mousedown', (e) => {
    if (e.target === sliderHandle || sliderHandle.contains(e.target)) return;
    startDrag(e);
});
document.addEventListener('mousemove', doDrag);
document.addEventListener('mouseup', stopDrag);

// Touch events
sliderHandle.addEventListener('touchstart', startDrag, { passive: false });
videoCompare.addEventListener('touchstart', (e) => {
    if (e.target === sliderHandle || sliderHandle.contains(e.target)) return;
    startDrag(e);
}, { passive: false });
document.addEventListener('touchmove', doDrag, { passive: false });
document.addEventListener('touchcancel', stopDrag);
document.addEventListener('touchcancel', stopDrag);

// Keyboard navigation for slider
sliderHandle.addEventListener('keydown', (e) => {
    const step = 5; // 5% steps
    switch(e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            sliderPos = Math.max(0, sliderPos - step);
            updateSlider(videoCompare.getBoundingClientRect().left + (sliderPos / 100) * videoCompare.offsetWidth);
            break;
        case 'ArrowRight':
            e.preventDefault();
            sliderPos = Math.min(100, sliderPos + step);
            updateSlider(videoCompare.getBoundingClientRect().left + (sliderPos / 100) * videoCompare.offsetWidth);
            break;
        case 'Home':
            e.preventDefault();
            sliderPos = 0;
            updateSlider(videoCompare.getBoundingClientRect().left);
            break;
        case 'End':
            e.preventDefault();
            sliderPos = 100;
            updateSlider(videoCompare.getBoundingClientRect().right);
            break;
    }
});

// Initialize slider position
updateSlider(videoCompare.getBoundingClientRect().left + videoCompare.offsetWidth / 2);

// Load Gallery from HLS videos
const galleryData = [
    { title: 'Felix the Cat - Feline Follies', year: '1919', folder: 'felix-feline-follies', youtube: 'https://www.youtube.com/watch?v=example1' },
    { title: 'Superman - Destruction Inc.', year: '1942', folder: 'superman-destruction', youtube: 'https://www.youtube.com/watch?v=example2' },
    { title: 'Superman - Japoteurs', year: '1942', folder: 'superman-japoteurs', youtube: 'https://www.youtube.com/watch?v=example3' },
    { title: 'Superman - Eleventh Hour', year: '1942', folder: 'superman-eleventh-hour', youtube: 'https://www.youtube.com/watch?v=example4' },
    { title: 'Felix the Cat - Felix Swims', year: '1922', folder: 'felix-swim', youtube: 'https://www.youtube.com/watch?v=example5' },
    { title: 'Dinner for One', year: '1963', folder: 'dinner-for-one-1963', youtube: 'https://www.youtube.com/watch?v=example6' }
];

const galleryGrid = document.getElementById('galleryGrid');

galleryData.forEach(item => {
    const card = document.createElement('div');
    card.className = 'gallery-card';

    // Card click goes to studio
    card.onclick = (e) => {
        if (!e.target.closest('.gallery-youtube-btn')) {
            window.location.href = `remaike-studio.html?video=${item.folder}`;
        }
    };

    card.innerHTML = `
        <div class="gallery-video">
            <video autoplay loop muted playsinline loading="lazy">
                <source src="assets/video/clips/01_enhanced.mp4" type="video/mp4">
            </video>
            <div class="gallery-overlay">
                <span style="color: var(--brand-primary)">Klicken für Vergleich →</span>
            </div>
            <div class="gallery-play">▶</div>
        </div>
        <div class="gallery-info">
            <div class="gallery-header">
                <div class="gallery-title">${item.title}</div>
                <a href="${item.youtube}" target="_blank" class="gallery-youtube-btn" title="Watch on YouTube">
                    <span class="yt-icon">▶</span>
                </a>
            </div>
            <div class="gallery-meta">${item.year} • 8K Restored</div>
        </div>
    `;

    galleryGrid.appendChild(card);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
