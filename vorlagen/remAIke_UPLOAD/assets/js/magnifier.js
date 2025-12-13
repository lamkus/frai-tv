class MagnifierLens {
    constructor(element) {
        this.element = element;
        this.originalImg = element.querySelector('.magnifier-original');
        this.enhancedImg = element.querySelector('.magnifier-enhanced');
        this.lens = null;
        this.init();
    }

    init() {
        // Create magnifier lens
        this.lens = document.createElement('div');
        this.lens.className = 'magnifier-lens';
        this.lens.style.display = 'none';
        this.element.appendChild(this.lens);

        // Set up enhanced image as background
        this.enhancedImg.style.display = 'none';

        // Event listeners
        this.element.addEventListener('mouseenter', this.showLens.bind(this));
        this.element.addEventListener('mousemove', this.moveLens.bind(this));
        this.element.addEventListener('mouseleave', this.hideLens.bind(this));

        // Touch support
        this.element.addEventListener('touchstart', this.showLens.bind(this), { passive: true });
        this.element.addEventListener('touchmove', this.moveLens.bind(this), { passive: true });
        this.element.addEventListener('touchend', this.hideLens.bind(this));
    }

    showLens(e) {
        this.lens.style.display = 'block';
        this.lens.style.backgroundImage = `url(${this.enhancedImg.src})`;

        // Ensure images are loaded to get correct dimensions
        const enhancedImage = new Image();
        enhancedImage.src = this.enhancedImg.src;
        enhancedImage.onload = () => {
            const zoomFactor = enhancedImage.naturalWidth / this.originalImg.width;
            this.lens.style.backgroundSize = `${this.originalImg.width * zoomFactor}px ${this.originalImg.height * zoomFactor}px`;
            this.moveLens(e);
        };
    }

    moveLens(e) {
        e.preventDefault();

        const rect = this.element.getBoundingClientRect();
        const x = (e.clientX || e.touches[0].clientX) - rect.left;
        const y = (e.clientY || e.touches[0].clientY) - rect.top;

        // Position lens
        const lensSize = 150;
        this.lens.style.left = `${x - lensSize/2}px`;
        this.lens.style.top = `${y - lensSize/2}px`;

        // Calculate background position for zoom effect
        const enhancedImage = new Image();
        enhancedImage.src = this.enhancedImg.src;
        const zoomFactor = enhancedImage.naturalWidth / this.originalImg.width;

        const bgX = x * zoomFactor - lensSize/2;
        const bgY = y * zoomFactor - lensSize/2;
        this.lens.style.backgroundPosition = `-${bgX}px -${bgY}px`;
    }

    hideLens() {
        this.lens.style.display = 'none';
    }
}

// This file only defines the class. Initialization is handled in main.js or gallery.js
// to ensure it runs after dynamic content is loaded.

