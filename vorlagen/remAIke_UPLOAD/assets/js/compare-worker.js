// compare-worker.js - OffscreenCanvas worker that computes exact pixel diffs
// Statically import pixelmatch so that it is bundled by webpack. Keep a CDN fallback
// as a last resort for browsers that for some reason don't have the inlined module.
import pixelmatch from 'pixelmatch';
// Use a local reassignable variable for runtime use so the CDN fallback can replace
// it if the bundled import isn't usable in the runtime environment.
let pixelmatchLocal = pixelmatch || (pixelmatch && pixelmatch.pixelmatch) || null;

// If pixelmatch is not a function for some reason, attempt a CDN dynamic import as a last resort.
(async () => {
    if (typeof pixelmatchLocal === 'function') return;
    try {
        // Leave the CDN import to runtime; avoid webpack treating it as an external module
        const mod = await import(/* webpackIgnore: true */ 'https://cdn.jsdelivr.net/npm/pixelmatch@5.3.0/dist/pixelmatch.esm.js');
        pixelmatchLocal = mod.default || mod.pixelmatch || pixelmatchLocal;
    } catch (e2) {
        console.warn('pixelmatch not available in worker (local or CDN)', e2);
    }
})();

self.addEventListener('message', async (e) => {
    const data = e.data;
    if (!data || data.cmd !== 'diff') return;
    const width = data.width; const height = data.height;
    const aBuf = new Uint8ClampedArray(data.a);
    const bBuf = new Uint8ClampedArray(data.b);
    const threshold = data.threshold || 0.02; // normalized 0..1
    const diffMode = data.diffMode || 0; // 0 RGB, 1 Luma

    const out = new Uint8ClampedArray(width * height * 4);
    let diffCount = 0;
    let seSum = 0; // squared error sum across RGB

    function luma(r,g,b){ return 0.2126*r + 0.7152*g + 0.0722*b; }

    if (typeof pixelmatchLocal === 'function') {
        // Use pixelmatch for high-quality diff if available
        const outBuf = new Uint8ClampedArray(width * height * 4);
        diffCount = pixelmatchLocal(aBuf, bBuf, outBuf, width, height, {threshold: threshold, includeAA: false});
        // copy outBuf into out
        out.set(outBuf);
        // compute seSum
        let sSum = 0;
        for (let i=0;i<width*height;i++){
            const idx=i*4;
            const dr=aBuf[idx]-bBuf[idx];
            const dg=aBuf[idx+1]-bBuf[idx+1];
            const db=aBuf[idx+2]-bBuf[idx+2];
            sSum+=dr*dr+dg*dg+db*db;
        }
        seSum = sSum;
    } else {
        for (let i=0; i<width*height; i++){
        const idx = i*4;
        const ar = aBuf[idx], ag = aBuf[idx+1], ab = aBuf[idx+2];
        const br = bBuf[idx], bg = bBuf[idx+1], bb = bBuf[idx+2];
        let delta = 0;
        if (diffMode === 1) {
            const la = luma(ar,ag,ab)/255.0;
            const lb = luma(br,bg,bb)/255.0;
            delta = Math.abs(la - lb);
        } else {
            const dr = (ar - br)/255.0;
            const dg = (ag - bg)/255.0;
            const db = (ab - bb)/255.0;
            delta = Math.sqrt(dr*dr + dg*dg + db*db) / 1.73205;
        }
        if (delta > threshold) {
            diffCount++;
            // Heatmap: red intensity by delta
            const intensity = Math.min(1, delta);
            out[idx] = Math.floor(255 * intensity);
            out[idx+1] = 0;
            out[idx+2] = Math.floor(255 * (1-intensity));
            out[idx+3] = 255;
        } else {
            // show grayscale of original to ease recognition
            const g = Math.floor((ar+ag+ab)/3);
            out[idx] = g; out[idx+1] = g; out[idx+2] = g; out[idx+3] = 255;
        }
        // accumulate squared error for PSNR
        const dr = (ar - br);
        const dg = (ag - bg);
        const db = (ab - bb);
            seSum += (dr*dr + dg*dg + db*db);
        }
    }

    const diffPercent = Math.round((diffCount / (width*height)) * 10000) / 100;
    const mse = seSum / (3.0 * width * height);
    const psnr = (mse === 0) ? Infinity : (10.0 * Math.log10((255.0*255.0) / mse));
    // create OffscreenCanvas and draw diff;
    const oc = new OffscreenCanvas(width, height);
    const ctx = oc.getContext('2d');
    const imageData = new ImageData(out, width, height);
    ctx.putImageData(imageData, 0, 0);
    const blob = await oc.convertToBlob({type: 'image/png'});
    // Transfer blob using postMessage (Blob is structured clone, transferable isn't necessary)
    self.postMessage({cmd:'diffResult', diffCount, diffPercent, psnr, mse, blob}, []);
});
