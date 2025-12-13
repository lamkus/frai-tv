export const state = {
    // DOM Elements
    wrapper: null,
    clickVideo: null,
    sliderEnhanced: null,
    sliderOriginal: null,
    sliderHandle: null,
    videoEnhanced: null,
    videoOriginal: null,
    zoomLens: null,
    zoomVideo: null,
    zoomLabel: null,
    modeIndicator: null,
    clickOverlay: null,
    shortcutsPanel: null,
    dropdown: null,
    rescanBtn: null,
    timelineScrubber: null,
    timeCurrent: null,
    timeDuration: null,
    smpteDisplay: null,
    syncStatus: null,
    slowmoSlider: null,
    slowmoValue: null,

    // State Variables
    COMPARISONS: [],
    currentIdx: -1,
    hlsInstances: [],
    isEnhanced: false,
    sliderMode: false,
    isPlaying: false,
    currentMode: 'click',
    masterFps: 24,
    slowmoRate: 1,

    // Constants
    VIDEO_SERVER: '',
    DEFAULT_COMPARISON: {
        id: 'korn-freak-preview',
        name: 'Korn – Freak On a Leash (4K Upscale) — Licensed Preview',
        original: 'uploads/korn/preview/original_preview.mp4',
        enhanced: 'uploads/korn/preview/enhanced_preview.mp4',
        isPreview: true
    }
};
