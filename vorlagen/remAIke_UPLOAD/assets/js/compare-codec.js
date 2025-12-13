// compare-codec.js
// Minimal MediaLoader supporting images and video with optional WebCodecs usage.
import { VideoFrameExtractor, WebCodecsExtractor } from './compare-codec-webcodecs.js';

export class MediaLoader {
    constructor() { this.useWebCodecs = false; }
    setUseWebCodecs(flag) { this.useWebCodecs = !!flag; }

    async loadImage(url) {
        // Return ImageBitmap (for WebGL textures)
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.src = url;
        await new Promise((res, rej) => {
            img.onload = res; img.onerror = rej;
        });
        if ('createImageBitmap' in window) {
            const imgb = await createImageBitmap(img);
            return {type: 'image', image: imgb, width: img.width, height: img.height};
        } else {
            return {type: 'image', image: img, width: img.width, height: img.height};
        }
    }

    async loadVideo(url) {
        // Fallback: returns a simple video element that we can seek & draw.
        const video = document.createElement('video');
        video.crossOrigin = 'anonymous';
        video.src = url;
        video.preload = 'auto';
        video.muted = true;
        video.playsInline = true;
        await video.play().catch(()=>{}); // try to start
        await new Promise((res,rej)=>{
            if (video.readyState >= 2) res(); else video.onloadeddata = res;
        });
        return {type: 'video', video, width: video.videoWidth, height: video.videoHeight};
    }

    async getFrameFromVideo(media, index) {
        // index in frame number. Seek & draw to canvas to get ImageBitmap
        const video = media.video;
        const canvas = document.createElement('canvas');
        canvas.width = media.width; canvas.height = media.height;
        const ctx = canvas.getContext('2d');
        // If we have requestVideoFrameCallback support or WebCodecs, use the extractor
        if (this.useWebCodecs && typeof WebCodecsExtractor !== 'undefined') {
            try {
                const extractor = new WebCodecsExtractor(video);
                const ib = await extractor.getFrameAtIndex(index, media.fps || 25);
                return {image: ib, width: media.width, height: media.height};
            } catch (e) {
                console.warn('WebCodecs extractor failed, falling back', e);
            }
        }
        if ('requestVideoFrameCallback' in HTMLVideoElement.prototype) {
            const extractor = new VideoFrameExtractor(video);
            const ib = await extractor.getFrameAtIndex(index, media.fps || 25);
            return {image: ib, width: media.width, height: media.height};
        }

        // Convert index -> time using frameRate = assume 25? fallback to 30
        const fps = media.fps || 25;
        const time = (index / fps);
        return new Promise((res, rej) => {
            function seeked() {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                canvas.toBlob(async b=>{
                    const img = await createImageBitmap(b);
                    res({image: img, width: canvas.width, height: canvas.height});
                });
            }
            try {
                video.currentTime = time;
                video.onseeked = seeked;
            } catch(e) {
                // If seeking fails, draw current frame
                ctx.drawImage(video, 0, 0);
                canvas.toBlob(async b=>{ const img = await createImageBitmap(b); res({image: img, width: canvas.width, height: canvas.height}); });
            }
        });
    }
}
