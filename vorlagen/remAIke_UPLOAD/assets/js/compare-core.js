// compare-core.js - orchestrates loading, events, and renderer
import {CompareRenderer} from './compare-renderer.js';
import {MediaLoader} from './compare-codec.js';

console.log('[compare-core] Module loaded successfully');

const canvas = document.getElementById('canvas');
const renderer = new CompareRenderer(canvas);
const loader = new MediaLoader();

// Showcase mode detection
const urlParams = new URLSearchParams(window.location.search);
const isAdminMode = urlParams.has('admin') || urlParams.get('mode') === 'admin';
const isShowcaseMode = !isAdminMode;

let leftMedia, rightMedia;
let leftUrl = null, rightUrl = null;
let leftImage, rightImage; // ImageBitmaps or HTMLImageElement
let mouseX = 0, mouseY = 0;
let currentMode = 'split';
let lastDiffBlob = null;

// Showcase controller state
let showcaseManifest = null;
let showcaseCurrentPairIndex = 0;
let showcaseModeIndex = 0;
let showcasePairTimer = null;
let showcaseModeTimer = null;
let showcaseCursorAnimFrame = null;
let showcaseCursorAngle = 0;
let showcasePaused = false;

async function loadPair(pair) {
    // pair: {left: url, right: url}
    leftUrl = pair.left; rightUrl = pair.right;
    leftMedia = await loader.loadImage(pair.left);
    rightMedia = await loader.loadImage(pair.right);
    leftImage = leftMedia.image;
    rightImage = rightMedia.image;

    // Set canvas to image dims
    canvas.width = leftImage.width;
    canvas.height = leftImage.height;
    // CSS scale to fit viewport
    const scale = Math.min(window.innerWidth*0.8/leftImage.width, window.innerHeight*0.8/leftImage.height);
    canvas.style.width = (leftImage.width * scale) + 'px';
    canvas.style.height = (leftImage.height * scale) + 'px';
    renderer.setMode(currentMode);
    await renderer.render(leftImage, rightImage);
}

function setMode(mode) {
    currentMode = mode;
    renderer.setMode(mode);
    document.getElementById('modeText').textContent = mode.charAt(0).toUpperCase() + mode.slice(1);
}

// Expose setMode to global scope for existing HTML usage fallback
window.setMode = setMode;

function setStatus(msg, show=true, timeout=4000) {
    const el = document.getElementById('statusText');
    if (!el) return;
    el.textContent = msg;
    el.style.display = show ? 'block' : 'none';
    if (show && timeout>0) setTimeout(()=>{ el.style.display='none'; }, timeout);
}

// hook buttons
const buttons = document.querySelectorAll('.controls button');
buttons.forEach(b=>{
    b.addEventListener('click', (e)=>{
        buttons.forEach(x=>x.classList.remove('active'));
        e.target.classList.add('active');
        const mode = e.target.getAttribute('data-mode') || e.target.textContent.trim().toLowerCase();
        setMode(mode);
        document.getElementById('modeText').textContent = e.target.textContent.trim();
    });
});

const cursorRing = document.querySelector('.cursor-ring');
// mouse mapping + combined handler
canvas.addEventListener('mousemove', (e)=>{
    const rect = canvas.getBoundingClientRect();
    const cssX = e.clientX - rect.left;
    const cssY = e.clientY - rect.top;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    mouseX = Math.floor(cssX * scaleX);
    mouseY = Math.floor(cssY * scaleY);

    // split normalized
    const split = mouseX / canvas.width;
    renderer.setSplit(split);
    // set circle center normalized (vUV space)
    const normX = mouseX / canvas.width;
    const normY = mouseY / canvas.height;
    renderer.setCenter(normX, normY);
    renderer.setRadius(0.12);
    renderer.setTileSize(50.0);
    // update cursor ring CSS
    if (cursorRing) {
        cursorRing.style.left = e.clientX + 'px';
        cursorRing.style.top = e.clientY + 'px';
    }
    updateZoom();
    samplePixel();
    renderer.render(leftImage, rightImage);
});

// update zoom preview canvases
const zoomOriginal = document.getElementById('zoomOriginal');
const zoomEnhanced = document.getElementById('zoomEnhanced');
const zoomOrigCtx = zoomOriginal.getContext('2d');
const zoomEnhCtx = zoomEnhanced.getContext('2d');
const pixelCanvas = document.createElement('canvas');
pixelCanvas.width = 1; pixelCanvas.height = 1;
const pixelCtx = pixelCanvas.getContext('2d');

function updateZoom() {
    if (!leftImage || !rightImage) return;
    // zoom canvas is 150x150 CSS, but 20x20 bitmap
    const zoomSize = 20;
    const half = Math.floor(zoomSize/2);
    const rect = canvas.getBoundingClientRect();
    const cssX = mouseX; const cssY = mouseY; // already canvas pixels
    const startX = Math.max(0, Math.min(canvas.width - zoomSize, Math.floor(cssX - half)));
    const startY = Math.max(0, Math.min(canvas.height - zoomSize, Math.floor(cssY - half)));

    zoomOrigCtx.imageSmoothingEnabled = false;
    zoomEnhCtx.imageSmoothingEnabled = false;
    // draw small area into 20x20 offscreen, then scale in CSS
    zoomOrigCtx.clearRect(0,0,20,20);
    zoomOrigCtx.drawImage(leftImage, startX, startY, zoomSize, zoomSize, 0, 0, 20, 20);
    zoomEnhCtx.clearRect(0,0,20,20);
    zoomEnhCtx.drawImage(rightImage, startX, startY, zoomSize, zoomSize, 0, 0, 20, 20);
}

function samplePixel() {
    if (!leftImage || !rightImage) return;
    const x = Math.max(0, Math.min(canvas.width-1, mouseX));
    const y = Math.max(0, Math.min(canvas.height-1, mouseY));
    // original
    pixelCtx.clearRect(0,0,1,1);
    pixelCtx.drawImage(leftImage, x, y, 1, 1, 0, 0, 1, 1);
    const d1 = pixelCtx.getImageData(0,0,1,1).data;
    // enhanced
    pixelCtx.clearRect(0,0,1,1);
    pixelCtx.drawImage(rightImage, x, y, 1, 1, 0, 0, 1, 1);
    const d2 = pixelCtx.getImageData(0,0,1,1).data;
    document.getElementById('pixelOrig').textContent = `${d1[0]},${d1[1]},${d1[2]}`;
    document.getElementById('pixelEnh').textContent = `${d2[0]},${d2[1]},${d2[2]}`;
    const posElem = document.getElementById('pixelPos');
    if (posElem) posElem.textContent = `${x}, ${y}`;
}

// update zoom when moving
canvas.addEventListener('mousemove', (e)=>{
    const rect = canvas.getBoundingClientRect();
    const cssX = e.clientX - rect.left;
    const cssY = e.clientY - rect.top;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    mouseX = Math.floor(cssX * scaleX);
    mouseY = Math.floor(cssY * scaleY);
    updateZoom();
});

// Expose load for initial test
window.compareCore = { loadPair, setMode };

// Initialize diff worker
let diffWorker = null;
try {
    // Try to load the minified, webpack-bundled worker first
    try { diffWorker = new Worker('assets/js/compare-worker.min.js', { type: 'module' }); }
    catch (e) { diffWorker = new Worker('assets/js/compare-worker.js', { type: 'module' }); }
} catch (e) { console.warn('Web Worker not available', e); }

if (diffWorker) {
    diffWorker.addEventListener('message', (ev) => {
        const d = ev.data;
        if (!d || d.cmd !== 'diffResult') return;
        const diffStats = document.getElementById('diffStats');
        if (diffStats) diffStats.textContent = `Diff: ${d.diffCount} pixels (${d.diffPercent}%), PSNR: ${isFinite(d.psnr)?d.psnr.toFixed(2)+'dB':'∞'}, MSE: ${d.mse?.toFixed(2)}`;
        const preview = document.getElementById('diffPreview');
        if (preview && d.blob) {
            lastDiffBlob = d.blob;
            const url = URL.createObjectURL(lastDiffBlob);
            preview.src = url;
        }
    });
}

// YouTube list and selection
const YT_VIDEOS = [
    {id: 'YE7VzlLtp-4', title: 'Big Buck Bunny'},
    {id: '5xVh-7ywKpE', title: 'Sintel Trailer'},
    {id: 'bK1u9l9yZS0', title: 'Elephants Dream'}
];

function populateYtList() {
    const list = document.getElementById('ytList');
    if (!list) return;
    YT_VIDEOS.forEach(v => {
        const btn = document.createElement('button');
        btn.textContent = v.title;
        btn.addEventListener('click', ()=>{
            const player = document.getElementById('ytPlayer');
            player.src = `https://www.youtube.com/embed/${v.id}?rel=0&autoplay=1`;
            console.log('Loaded YT video', v.title, v.id);
            document.getElementById('ytOpenBtn').href = `https://www.youtube.com/watch?v=${v.id}`;
        });
        list.appendChild(btn);
    });
}
populateYtList();
// default open button points to default sample
document.getElementById('ytOpenBtn').href = `https://www.youtube.com/watch?v=${YT_VIDEOS[0].id}`;
document.getElementById('ytUrlInput').value = YT_VIDEOS[0].id;

function parseYouTubeId(urlOrId) {
    if (!urlOrId) return null;
    // if looks like youtu.be/ID
    const short = urlOrId.match(/youtu\.be\/(.+)(\?|$)/);
    if (short) return short[1].split('?')[0];
    // if contains watch?v=ID
    const w = urlOrId.match(/[?&]v=([a-zA-Z0-9_-]{6,})/);
    if (w) return w[1];
    // embed path
    const embed = urlOrId.match(/embed\/(.+?)(\?|$)/);
    if (embed) return embed[1];
    // plain id (letters, numbers, -_)
    if (/^[a-zA-Z0-9_-]{6,}$/.test(urlOrId.trim())) return urlOrId.trim();
    return null;
}

document.getElementById('ytLoadBtn').addEventListener('click', ()=>{
    const val = document.getElementById('ytUrlInput').value.trim();
    const id = parseYouTubeId(val);
    if (!id) {
        alert('Please paste a valid YouTube URL or ID');
        return;
    }
    const player = document.getElementById('ytPlayer');
    player.src = `https://www.youtube.com/embed/${id}?rel=0&autoplay=1`;
    document.getElementById('ytOpenBtn').href = `https://www.youtube.com/watch?v=${id}`;
    console.log('Loaded YT video from input', id);
});

document.getElementById('ytOpenBtn').addEventListener('click', (e)=>{
    const href = document.getElementById('ytOpenBtn').href;
    if (!href || href === '#') e.preventDefault();
});

// Threshold control
const thresholdSlider = document.getElementById('thresholdSlider');
if (thresholdSlider) {
    thresholdSlider.addEventListener('input', (e)=>{
        const v = parseFloat(e.target.value);
        renderer.setThreshold(v);
    });
}

// GPU toggle
const gpuToggle = document.getElementById('gpuToggle');
if (gpuToggle) {
    gpuToggle.addEventListener('change', (e)=>{
        const useGpu = e.target.checked;
        renderer.setUseGPU(useGpu);
    });
}

// WebCodecs toggle
const webcodecsToggle = document.getElementById('webcodecsToggle');
if (webcodecsToggle) {
    webcodecsToggle.addEventListener('change', (e)=>{
        const useWC = e.target.checked;
        loader.setUseWebCodecs(useWC);
        if (useWC) {
            // Quick availability check
            if (!('VideoDecoder' in window) && !('MediaStreamTrackProcessor' in window) && !('requestVideoFrameCallback' in HTMLVideoElement.prototype)) {
                setStatus('WebCodecs not supported in this browser; fallback will be used', true, 4000);
            } else {
                setStatus('WebCodecs mode enabled (experimental)', true, 2000);
            }
        } else {
            setStatus('WebCodecs mode disabled', true, 1200);
        }
    });
}

// Diff mode select
const diffModeSelect = document.getElementById('diffMode');
if (diffModeSelect) {
    diffModeSelect.addEventListener('change', (e)=>{
        const m = parseInt(e.target.value, 10);
        renderer.setDiffMode(m);
    });
}

const blendSlider = document.getElementById('blendSlider');
if (blendSlider) {
    blendSlider.addEventListener('input', (e)=>{
        const v = parseFloat(e.target.value);
        renderer.setBlend(v);
    });
}

const paletteSelect = document.getElementById('paletteSelect');
if (paletteSelect) {
    paletteSelect.addEventListener('change', (e)=>{
        const p = parseInt(e.target.value, 10);
        renderer.setPalette(p);
    });
}

// Initialize controls from renderer defaults
if (thresholdSlider) thresholdSlider.value = renderer.threshold;
if (gpuToggle) gpuToggle.checked = renderer.useGPUPreferred;
if (diffModeSelect) diffModeSelect.value = String(renderer.diffMode || 0);
if (blendSlider) blendSlider.value = renderer.blend || 1.0;
if (paletteSelect) paletteSelect.value = String(renderer.palette || 0);
if (webcodecsToggle) webcodecsToggle.checked = loader.useWebCodecs || false;

// Wire up Run Diff button
async function runDiff() {
    if (!leftImage || !rightImage) { alert('Load a pair first'); return; }
    if (!diffWorker) { alert('Diff worker not available'); return; }
    const width = leftImage.width; const height = leftImage.height;
    let ocA, octxA;
    if (typeof OffscreenCanvas !== 'undefined') {
        ocA = new OffscreenCanvas(width, height);
        octxA = ocA.getContext('2d');
    } else {
        ocA = document.createElement('canvas'); ocA.width = width; ocA.height = height; octxA = ocA.getContext('2d');
    }
    octxA.drawImage(leftImage, 0, 0, width, height);
    const idA = octxA.getImageData(0,0,width,height);
    let ocB, octxB;
    if (typeof OffscreenCanvas !== 'undefined') {
        ocB = new OffscreenCanvas(width, height);
        octxB = ocB.getContext('2d');
    } else {
        ocB = document.createElement('canvas'); ocB.width = width; ocB.height = height; octxB = ocB.getContext('2d');
    }
    octxB.drawImage(rightImage, 0, 0, width, height);
    const idB = octxB.getImageData(0,0,width,height);
    // post message with transferable buffers
    diffWorker.postMessage({ cmd: 'diff', width, height, a: idA.data.buffer, b: idB.data.buffer, threshold: renderer.threshold, diffMode: renderer.diffMode }, [idA.data.buffer, idB.data.buffer]);
}

const runDiffBtn = document.getElementById('runDiffBtn');
if (runDiffBtn) runDiffBtn.addEventListener('click', runDiff);

const downloadDiffBtn = document.getElementById('downloadDiffBtn');
if (downloadDiffBtn) downloadDiffBtn.addEventListener('click', ()=>{
    if (!lastDiffBlob) { alert('No diff available yet'); return; }
    const url = URL.createObjectURL(lastDiffBlob);
    const a = document.createElement('a');
    a.href = url; a.download = 'diff.png';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(()=> URL.revokeObjectURL(url), 1000);
});

const exportDiffJsonBtn = document.getElementById('exportDiffJsonBtn');
if (exportDiffJsonBtn) exportDiffJsonBtn.addEventListener('click', ()=>{
    if (!lastDiffBlob) { alert('No diff available yet'); return; }
    const result = {
        left: leftUrl || 'left',
        right: rightUrl || 'right',
        diffCount: document.getElementById('diffStats')?.textContent || null,
        threshold: renderer.threshold,
        diffMode: renderer.diffMode,
        blend: renderer.blend,
        mode: renderer.mode
    };
    const b = new Blob([JSON.stringify(result, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(b);
    const a = document.createElement('a'); a.href = url; a.download = 'diff-stats.json'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000);
});

// Download & Validate button: copy the cli command to clipboard
const downloadValidateBtn = document.getElementById('downloadValidateBtn');
if (downloadValidateBtn) {
    downloadValidateBtn.addEventListener('click', ()=>{
        const val = document.getElementById('ytUrlInput').value.trim();
        const id = parseYouTubeId(val);
        const cmd = `node scripts/download_and_validate_youtube.js "${id}" "assets/video/intropart2.mp4" 0,10,50`;
        navigator.clipboard.writeText(cmd).then(()=>alert('Command copied to clipboard: ' + cmd));
    });
}

// Run Parity via server API - POST /api/parity
const runParityServerBtn = document.getElementById('runParityServerBtn');
if (runParityServerBtn) {
    runParityServerBtn.addEventListener('click', async () => {
        if (!leftUrl || !rightUrl) { alert('Load a pair first'); return; }
        // If both local inputs have files, upload them as multipart/form-data
        const haveLocalFiles = (typeof leftLocal !== 'undefined' && leftLocal && leftLocal.files && leftLocal.files.length) && (typeof rightLocal !== 'undefined' && rightLocal && rightLocal.files && rightLocal.files.length);
        if (haveLocalFiles) {
            const leftFile = leftLocal.files[0];
            const rightFile = rightLocal.files[0];
            const bothImage = leftFile.name.match(/\.(png|jpe?g)$/i) && rightFile.name.match(/\.(png|jpe?g)$/i);
            const method = bothImage ? 'pixelmatch' : 'validate';
            // build formdata
            const fd = new FormData();
            fd.append('left', leftFile, leftFile.name);
            fd.append('right', rightFile, rightFile.name);
            fd.append('method', method);
            fd.append('wait', 'true');
            // frames param optional: if UI provides it, include it
            const framesEl = document.getElementById('parityFrames');
            if (framesEl && framesEl.value) fd.append('frames', framesEl.value);

            setStatus('Uploading files to parity server...');
            runParityServerBtn.disabled = true;
            try {
                const resp = await fetch('/api/parity/upload', { method: 'POST', body: fd });
                const json = await resp.json();
                console.log('Parity upload result', json);
                if (!json.ok) {
                    setStatus('Parity upload failed: ' + (json.error || 'unknown'));
                } else {
                    setStatus('Parity upload finished. See console for detailed results');
                }
            } catch (e) {
                console.error('Parity upload error', e);
                setStatus('Parity upload failed: ' + (e.message || e));
            } finally {
                runParityServerBtn.disabled = false;
            }
            return;
        }

        // otherwise fall back to URL-based parity endpoint
        const method = (leftUrl.endsWith('.png') || leftUrl.endsWith('.jpg') || leftUrl.endsWith('.jpeg')) && (rightUrl.endsWith('.png') || rightUrl.endsWith('.jpg') || rightUrl.endsWith('.jpeg')) ? 'pixelmatch' : 'validate';
        setStatus('Submitting parity job to server...');
        runParityServerBtn.disabled = true;
        try {
            const resp = await fetch('/api/parity', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ left: leftUrl, right: rightUrl, method, wait: true })
            });
            const json = await resp.json();
            console.log('Parity result', json);
            if (!json.ok) {
                setStatus('Parity job failed: ' + (json.error || 'unknown'));
            } else {
                setStatus('Parity finished. Check logs in console or PSNR/SSIM files');
            }
            if (json.out) console.log(json.out);
            if (json.err) console.warn(json.err);
        } catch (e) {
            setStatus('Parity request failed: ' + e.message);
            console.error(e);
        } finally {
            runParityServerBtn.disabled = false;
        }
    });
}

// Local file pair load
const leftLocal = document.getElementById('leftLocal');
const rightLocal = document.getElementById('rightLocal');
const loadLocalPairBtn = document.getElementById('loadLocalPairBtn');
if (loadLocalPairBtn) {
    loadLocalPairBtn.addEventListener('click', async ()=>{
        if (!leftLocal.files.length || !rightLocal.files.length) {
            alert('Please pick both a left and a right file');
            return;
        }
        const leftFile = leftLocal.files[0];
        const rightFile = rightLocal.files[0];
        leftUrl = URL.createObjectURL(leftFile);
        rightUrl = URL.createObjectURL(rightFile);
        try {
            // choose image or video loader
            const leftIsVideo = leftFile.type.startsWith('video/');
            const rightIsVideo = rightFile.type.startsWith('video/');
            if (!leftIsVideo && !rightIsVideo) {
                await loadPair({ left: leftUrl, right: rightUrl });
                return;
            }
            // For videos, extract first frame using getFrameFromVideo
            let leftImg, rightImg;
            if (leftIsVideo) {
                const leftMedia = await loader.loadVideo(leftUrl);
                const frame = await loader.getFrameFromVideo(leftMedia, 0);
                leftImg = frame.image;
            } else {
                const leftMedia = await loader.loadImage(leftUrl);
                leftImg = leftMedia.image;
            }
            if (rightIsVideo) {
                const rightMedia = await loader.loadVideo(rightUrl);
                const frame = await loader.getFrameFromVideo(rightMedia, 0);
                rightImg = frame.image;
            } else {
                const rightMedia = await loader.loadImage(rightUrl);
                rightImg = rightMedia.image;
            }
            leftImage = leftImg; rightImage = rightImg;
            canvas.width = leftImage.width; canvas.height = leftImage.height;
            const scale = Math.min(window.innerWidth*0.8/leftImage.width, window.innerHeight*0.8/leftImage.height);
            canvas.style.width = (leftImage.width * scale) + 'px';
            canvas.style.height = (leftImage.height * scale) + 'px';
            renderer.render(leftImage, rightImage);
        } catch (e) {
            console.error('Failed to load local pair', e);
            alert('Failed to load local pair: ' + e.message);
        }
    });
}

// ========== SHOWCASE MODE ==========
// Auto-cycling viewer experience - no clicks required

async function loadShowcaseManifest() {
    try {
        const resp = await fetch('assets/comparisons/manifest.json');
        showcaseManifest = await resp.json();
        return showcaseManifest;
    } catch (e) {
        console.warn('Failed to load showcase manifest', e);
        return null;
    }
}

function updateShowcaseHUD(pair, mode) {
    const hudTitle = document.getElementById('showcaseTitle');
    const hudSmpte = document.getElementById('showcaseSmpte');
    const hudMode = document.getElementById('showcaseMode');
    const hudDesc = document.getElementById('showcaseDesc');
    const hudYear = document.getElementById('showcaseYear');

    if (hudTitle) hudTitle.textContent = pair.title || '';
    if (hudSmpte) hudSmpte.textContent = pair.smpte || '00:00:00:00';
    if (hudMode) hudMode.textContent = mode.toUpperCase();
    if (hudDesc) hudDesc.textContent = pair.description || '';
    if (hudYear) hudYear.textContent = pair.year ? `(${pair.year})` : '';
}

async function showcaseLoadPair(index) {
    if (!showcaseManifest || !showcaseManifest.pairs || !showcaseManifest.pairs.length) return;
    const pair = showcaseManifest.pairs[index % showcaseManifest.pairs.length];

    // Fade out canvas
    canvas.style.opacity = '0';
    canvas.style.transition = 'opacity 0.5s ease';

    await new Promise(r => setTimeout(r, 500));

    await loadPair({ left: pair.before, right: pair.after });

    // Fade in canvas
    canvas.style.opacity = '1';

    // Update HUD
    const modes = showcaseManifest.showcase?.modes || ['circle', 'split', 'difference', 'checkerboard'];
    updateShowcaseHUD(pair, modes[showcaseModeIndex % modes.length]);
}

function showcaseCycleMode() {
    if (!showcaseManifest) return;
    const modes = showcaseManifest.showcase?.modes || ['circle', 'split', 'difference', 'checkerboard'];
    showcaseModeIndex = (showcaseModeIndex + 1) % modes.length;
    const mode = modes[showcaseModeIndex];
    setMode(mode);

    // Update mode buttons visually
    const buttons = document.querySelectorAll('.controls button[data-mode]');
    buttons.forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-mode') === mode);
    });

    // Update HUD
    if (showcaseManifest.pairs && showcaseManifest.pairs.length > 0) {
        const pair = showcaseManifest.pairs[showcaseCurrentPairIndex % showcaseManifest.pairs.length];
        updateShowcaseHUD(pair, mode);
    }
}

async function showcaseCyclePair() {
    if (!showcaseManifest || !showcaseManifest.pairs) return;
    showcaseCurrentPairIndex = (showcaseCurrentPairIndex + 1) % showcaseManifest.pairs.length;
    showcaseModeIndex = 0; // Reset mode on new pair
    await showcaseLoadPair(showcaseCurrentPairIndex);
}

function showcaseAnimateCursor() {
    if (showcasePaused || !leftImage || !rightImage) {
        showcaseCursorAnimFrame = requestAnimationFrame(showcaseAnimateCursor);
        return;
    }

    // Animate cursor in a smooth pattern (figure-8 or circle)
    showcaseCursorAngle += 0.008;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radiusX = canvas.width * 0.35;
    const radiusY = canvas.height * 0.25;

    // Figure-8 pattern
    mouseX = centerX + radiusX * Math.sin(showcaseCursorAngle);
    mouseY = centerY + radiusY * Math.sin(showcaseCursorAngle * 2);

    // Update renderer
    const split = mouseX / canvas.width;
    renderer.setSplit(split);
    const normX = mouseX / canvas.width;
    const normY = mouseY / canvas.height;
    renderer.setCenter(normX, normY);
    renderer.setRadius(0.12);
    renderer.setTileSize(50.0);

    // Update cursor ring position
    const cursorRing = document.querySelector('.cursor-ring');
    if (cursorRing && canvas) {
        const rect = canvas.getBoundingClientRect();
        const cssX = rect.left + (mouseX / canvas.width) * rect.width;
        const cssY = rect.top + (mouseY / canvas.height) * rect.height;
        cursorRing.style.left = cssX + 'px';
        cursorRing.style.top = cssY + 'px';
    }

    updateZoom();
    samplePixel();
    renderer.render(leftImage, rightImage);

    showcaseCursorAnimFrame = requestAnimationFrame(showcaseAnimateCursor);
}

function showcaseStart() {
    if (!showcaseManifest || !showcaseManifest.showcase?.enabled) return;

    const modeCycleMs = showcaseManifest.showcase.modeCycleMs || 5000;
    const pairCycleMs = showcaseManifest.showcase.pairCycleMs || 15000;

    // Start mode cycling
    showcaseModeTimer = setInterval(showcaseCycleMode, modeCycleMs);

    // Start pair cycling
    showcasePairTimer = setInterval(showcaseCyclePair, pairCycleMs);

    // Start cursor animation
    if (showcaseManifest.showcase.cursorAnimation !== false) {
        showcaseCursorAnimFrame = requestAnimationFrame(showcaseAnimateCursor);
    }

    console.log('Showcase mode started:', { modeCycleMs, pairCycleMs });
}

function showcaseStop() {
    if (showcaseModeTimer) clearInterval(showcaseModeTimer);
    if (showcasePairTimer) clearInterval(showcasePairTimer);
    if (showcaseCursorAnimFrame) cancelAnimationFrame(showcaseCursorAnimFrame);
    showcaseModeTimer = null;
    showcasePairTimer = null;
    showcaseCursorAnimFrame = null;
}

function showcaseTogglePause() {
    showcasePaused = !showcasePaused;
    const pauseIndicator = document.getElementById('showcasePause');
    if (pauseIndicator) {
        pauseIndicator.style.display = showcasePaused ? 'block' : 'none';
    }
}

// Initialize showcase mode on page load
async function initShowcase() {
    if (!isShowcaseMode) {
        console.log('Admin mode detected, showcase disabled');
        return;
    }

    // Hide admin controls
    document.body.classList.add('showcase-mode');

    const manifest = await loadShowcaseManifest();
    if (!manifest || !manifest.showcase?.enabled) {
        console.log('Showcase not enabled in manifest');
        return;
    }

    // Load first pair
    if (manifest.pairs && manifest.pairs.length > 0) {
        await showcaseLoadPair(0);
    }

    // Start auto-cycling after short delay
    setTimeout(() => {
        showcaseStart();
    }, 2000);

    // Pause on click anywhere
    document.addEventListener('click', (e) => {
        // Ignore if clicking on controls (admin mode)
        if (e.target.closest('.controls') || e.target.closest('.left-column') || e.target.closest('.right-column')) return;
        showcaseTogglePause();
    });

    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Spacebar') {
            e.preventDefault();
            showcaseTogglePause();
        } else if (e.key === 'ArrowRight') {
            showcaseCyclePair();
        } else if (e.key === 'ArrowLeft') {
            showcaseCurrentPairIndex = Math.max(0, showcaseCurrentPairIndex - 2);
            showcaseCyclePair();
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            showcaseCycleMode();
        }
    });
}

// Export showcase controls
window.compareShowcase = {
    start: showcaseStart,
    stop: showcaseStop,
    pause: showcaseTogglePause,
    nextPair: showcaseCyclePair,
    nextMode: showcaseCycleMode,
    isAdmin: isAdminMode
};

// Initialize
console.log('[compare-core] Init block, isShowcaseMode=', isShowcaseMode, 'isAdminMode=', isAdminMode);
if (isShowcaseMode) {
    console.log('[compare-core] Calling initShowcase()');
    initShowcase().catch(e => console.error('[compare-core] initShowcase error:', e));
} else {
    // Admin mode - load default pair
    loadPair({
        left: 'assets/comparisons/betty-boop-hunting_before.jpg',
        right: 'assets/comparisons/betty-boop-hunting_after.jpg'
    });
}
