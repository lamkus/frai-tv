class AudioComparisonController {
    constructor(videoElement, audioSources, controlButtons, statusBadge) {
        this.video = videoElement;
        this.audioSources = audioSources;
        this.buttons = controlButtons;
        this.statusBadge = statusBadge;
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.sourceNodes = new Map();
        this.gainNode = this.audioContext.createGain();
        this.currentSource = null;
        this.isInitialized = false;

        this.init();
    }

    async init() {
        // Start muted to allow autoplay
        this.video.muted = true;
        try {
            await this.video.play();
        } catch (e) {
            console.error("Autoplay was prevented.", e);
        }

        // Create a single media element source node
        const mediaElementSource = this.audioContext.createMediaElementSource(this.video);
        mediaElementSource.connect(this.gainNode);
        this.gainNode.connect(this.audioContext.destination);

        this.buttons.forEach(button => {
            button.addEventListener('click', () => this.handleButtonClick(button));
        });

        // Resume AudioContext on user interaction
        const resumeAudio = async () => {
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            document.removeEventListener('click', resumeAudio);
        };
        document.addEventListener('click', resumeAudio);
    }

    async handleButtonClick(clickedButton) {
        if (!this.isInitialized) {
            this.video.muted = false;
            this.isInitialized = true;
        }

        const trackName = clickedButton.dataset.track;
        this.setActiveTrack(trackName);

        this.buttons.forEach(btn => btn.classList.remove('active'));
        clickedButton.classList.add('active');
    }

    setActiveTrack(trackName) {
        this.video.src = this.audioSources[trackName];
        this.video.play();
        this.updateStatus(trackName);
    }

    updateStatus(trackName) {
        this.statusBadge.textContent = `Aktiver Track: ${trackName}`;
        this.statusBadge.style.opacity = '1';
        setTimeout(() => { this.statusBadge.style.opacity = '0'; }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('comparison-video');
    const audioButtons = document.querySelectorAll('.audio-btn');
    const statusBadge = document.querySelector('.status-badge');

    const audioSources = {
        'Original': '/assets/audio/original.mp3',
        'Enhanced': '/assets/audio/enhanced.mp3',
        'Stems': '/assets/audio/stems.mp3'
    };

    if (video && audioButtons.length > 0 && statusBadge) {
        new AudioComparisonController(video, audioSources, audioButtons, statusBadge);
    }

    // Mobile menu (re-used from main.js, could be in a shared file)
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if(menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Initialize Tilt Effect for dashboard cards
    if (typeof VanillaTilt !== 'undefined') {
        VanillaTilt.init(document.querySelectorAll(".dashboard-card"), {
            max: 10,
            speed: 300,
            glare: true,
            "max-glare": 0.2,
        });
    }
});
