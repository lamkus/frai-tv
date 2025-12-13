// compare-codec-webcodecs.js
// Attempt to use requestVideoFrameCallback (rVFC) or WebCodecs where possible to get accurate frame access.

import MP4Box from 'mp4box';

export class VideoFrameExtractor {
    constructor(videoElement) {
        this.video = videoElement;
        this._lastFrameNumber = -1;
    }

    async seekToTime(timeSec) {
        // Seek and ensure ready
        return new Promise((resolve, reject) => {
            let called = false;
            const onSeeked = () => {
                if (called) return;
                called = true;
                this.video.removeEventListener('seeked', onSeeked);
                resolve();
            };
            this.video.addEventListener('seeked', onSeeked);
            try { this.video.currentTime = timeSec; }
            catch (e) { this.video.removeEventListener('seeked', onSeeked); reject(e); }
            // fallback timeout
            setTimeout(()=>{ if (!called) { called = true; this.video.removeEventListener('seeked', onSeeked); resolve(); } }, 1000);
        });
    }

    async getFrameImageBitmap() {
        // Use createImageBitmap on the video element; consistent with pixel-perfect
        // draw: createImageBitmap(video) often gives current frame; use rVFC if available
        if ('requestVideoFrameCallback' in HTMLVideoElement.prototype) {
            return new Promise((resolve, reject) => {
                const cb = (now, metadata) => {
                    // createImageBitmap will capture the frame
                    createImageBitmap(this.video).then(img => resolve(img)).catch(reject);
                };
                try {
                    this.video.requestVideoFrameCallback(cb);
                } catch (e) { createImageBitmap(this.video).then(resolve).catch(reject); }
            });
        }

        // Fallback: draw to canvas and create bitmap
        const c = document.createElement('canvas');
        c.width = this.video.videoWidth; c.height = this.video.videoHeight;
        const ctx = c.getContext('2d');
        ctx.drawImage(this.video, 0, 0, c.width, c.height);
        return createImageBitmap(c);
    }

    async getFrameAtIndex(index, fps=25) {
        const time = index / fps;
        await this.seekToTime(time);
        return await this.getFrameImageBitmap();
    }
}

// New helper: use MediaStreamTrackProcessor to get VideoFrames if available
export class WebCodecsExtractor {
    constructor(videoElement) {
        this.video = videoElement;
        this.processor = null; this.reader = null;
        this._initProcessor();
    }

    _initProcessor() {
        try {
            if (window.MediaStreamTrackProcessor && this.video.captureStream) {
                const stream = this.video.captureStream();
                const track = stream.getVideoTracks()[0];
                if (track) {
                    this.processor = new MediaStreamTrackProcessor({ track });
                    this.reader = this.processor.readable.getReader();
                }
            }
        } catch (e) {
            console.warn('MediaStreamTrackProcessor not available', e);
            this.processor = null; this.reader = null;
        }
    }

    async seekToTime(timeSec) {
        return new Promise((resolve, reject) => {
            const onSeeked = () => { this.video.removeEventListener('seeked', onSeeked); resolve(); };
            this.video.addEventListener('seeked', onSeeked);
            try { this.video.currentTime = timeSec; }
            catch (e) { this.video.removeEventListener('seeked', onSeeked); reject(e); }
            setTimeout(()=>{ this.video.removeEventListener('seeked', onSeeked); resolve(); }, 1000);
        });
    }

    async getVideoFrame() {
        if (!this.reader) {
            // fallback: use requestVideoFrameCallback createImageBitmap
            if ('requestVideoFrameCallback' in HTMLVideoElement.prototype) {
                return new Promise((resolve, reject) => {
                    const cb = (now, meta) => { createImageBitmap(this.video).then(resolve).catch(reject); };
                    try { this.video.requestVideoFrameCallback(cb); } catch(e){ createImageBitmap(this.video).then(resolve).catch(reject);}
                    });
            }
        }
        try {
            const r = await this.reader.read();
            if (r && r.value) return r.value; // VideoFrame object
            return null;
        } catch (e) {
            console.warn('Failed to read VideoFrame from processor', e);
            return null;
        }
    }

    async getFrameImageBitmap() {
        const vf = await this.getVideoFrame();
        if (!vf) return null;
        if (typeof vf.close === 'function' && typeof VideoFrame !== 'undefined' && vf instanceof VideoFrame) {
            try { const img = await createImageBitmap(vf); vf.close(); return img; } catch (e) { try{ vf.close(); }catch{}; throw e; }
        }
        // if got ImageBitmap already
        return vf;
    }

    async getFrameAtIndex(index, fps=25) {
        const time = index / fps;
        await this.seekToTime(time);
        // Prefer a direct demux + VideoDecoder path when possible (MP4Box + VideoDecoder)
        try {
            // If video.src is a blob or file-like url (object URL), try to fetch the data for demuxing
            const src = this.video.currentSrc || this.video.src;
            if (src && (src.startsWith('blob:') || src.startsWith('object:')) && typeof fetch === 'function' && typeof MP4Box !== 'undefined' && typeof VideoDecoder !== 'undefined') {
                // fetch data and attempt mp4 demux -> VideoDecoder (best-effort)
                const resp = await fetch(src);
                // check content-length header (if set) and skip decode if too large
                const SIZE_LIMIT = 50 * 1024 * 1024; // 50MB
                const cl = resp.headers && resp.headers.get ? resp.headers.get('content-length') : null;
                if (cl && Number(cl) > SIZE_LIMIT) {
                    console.warn(`Skipping MP4 demux for ${src} because content-length ${cl} exceeds ${SIZE_LIMIT} bytes`);
                } else {
                    const res = await this._decodeMp4FromResponse(resp, index, fps);
                    if (res) {
                        // If we received a VideoFrame return an ImageBitmap for compatibility
                        if (typeof VideoFrame !== 'undefined' && res instanceof VideoFrame) {
                            try { const ib = await createImageBitmap(res); try{ res.close(); }catch{}; return ib; } catch(e) { try{ res.close(); }catch{}; return res; }
                        }
                        return res;
                    }
                }
            }
        } catch (e) {
            console.warn('WebCodecs MP4 demuxer attempt failed, falling back to processor', e);
        }
        return await this.getFrameImageBitmap();
    }

    async _decodeMp4FromResponse(response, index, fps=25) {
        if (typeof MP4Box === 'undefined' || typeof VideoDecoder === 'undefined') return null;
        try {
            const mp4boxFile = MP4Box.createFile();
            let resolveReady; let readyPromise = new Promise(res=>resolveReady=res);
            mp4boxFile.onError = (e) => { console.warn('mp4box error', e); };
            mp4boxFile.onReady = (info) => { resolveReady(info); };
            const reader = response.body && response.body.getReader ? response.body.getReader() : null;
            let offset = 0;
            const READ_LIMIT = 10 * 1024 * 1024; // 10MB streaming cap for header/sample parse
            let totalRead = 0;
            if (reader) {
                let done = false;
                while (!done) {
                    const {value, done: d} = await reader.read();
                    if (d || !value) { done = true; break; }
                    const ab = value.buffer ? value.buffer : value;
                    ab.fileStart = offset;
                    try { mp4boxFile.appendBuffer(ab); mp4boxFile.flush(); } catch (e) { /* ignore append errors */ }
                    offset += ab.byteLength;
                    totalRead += ab.byteLength;
                    if (totalRead > READ_LIMIT) break; // avoid OOM
                }
            } else {
                try {
                    const ab = await response.arrayBuffer();
                    ab.fileStart = 0;
                    mp4boxFile.appendBuffer(ab);
                    try { mp4boxFile.flush(); } catch (e) {}
                } catch (e) { console.warn('Failed to read arrayBuffer from response', e); return null; }
            }
            const info = await readyPromise;
            if (!info || !info.tracks || !info.tracks.length) return null;
            const videoTrack = info.tracks.find(t => t.video && t.codec);
            if (!videoTrack) return null;
            const trackId = videoTrack.id;
            mp4boxFile.setExtractionOptions(trackId, null, { nbSamples: 1 });
            return await new Promise((resolve, reject) => {
                const decoder = new VideoDecoder({
                    output: (frame) => {
                        try { mp4boxFile.stop(); resolve(frame); } catch (e) { try{ frame.close(); }catch{}; reject(e); }
                    },
                    error: (e) => { console.warn('decoder error', e); }
                });
                try { decoder.configure({ codec: videoTrack.codec }); } catch (e) { console.warn('decoder configure failed', e); }
                mp4boxFile.onSamples = (id, user, samples) => {
                    if (!samples || !samples.length) return;
                    const s = samples[0];
                    const isKey = !!s.is_sync;
                    const chunk = new EncodedVideoChunk({ type: isKey ? 'key' : 'delta', timestamp: s.cts, data: new Uint8Array(s.data) });
                    try { decoder.decode(chunk); } catch (e) { console.warn('decode chunk failed', e); }
                };
                try { mp4boxFile.start(); } catch (e) { console.warn('mp4box start failed', e); }
                // continue streaming reader if available to feed more data while decoding
                if (reader) {
                    (async () => {
                        try {
                            while (true) {
                                const {value, done} = await reader.read();
                                if (done) break;
                                const ab = value.buffer ? value.buffer : value;
                                ab.fileStart = offset;
                                try { mp4boxFile.appendBuffer(ab); mp4boxFile.flush(); } catch (e) {}
                                offset += ab.byteLength;
                                totalRead += ab.byteLength;
                                if (totalRead > READ_LIMIT) break;
                            }
                        } catch (e) { /* ignore */ }
                    })();
                }
                setTimeout(()=>{ try{ mp4boxFile.stop(); }catch{}; reject(new Error('mp4 decode timeout')); }, 4000);
            });
        } catch (e) { console.warn('decodeMp4FromResponse failed', e); return null; }
    }
}
