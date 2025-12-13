Compare tool: Run Diff worker

This file explains how to use the client-side exact pixel diff and server-side validation tools.

Client-side exact diff (browser):
- Open `compare.html` in a modern Chromium-based browser that supports OffscreenCanvas and Workers.
- Load a pair of images or videos using the left and right file inputs.
  - For local video files, the tool extracts the first frame for comparison.
- Click 'Run Exact Diff' to compute a pixel-accurate diff using an Offscreen worker.
  - The worker computes delta per pixel on the RGBA image and returns a heatmap PNG and stats (pixel count/diff percent).
- Click 'Download Diff PNG' to download the diff image.

Server-side parity validation (CLI):
- Ensure ffmpeg and ffprobe are installed and available on PATH.
- Use the node scripts to validate frames across files (outputs MD5 + PSNR/SSIM logs):

Example validation commands (PowerShell):
```
node scripts/validate-parity.js "assets/video/left.mp4" "assets/video/right.mp4" 0,10,50
node scripts/download_and_validate_youtube.js "https://youtu.be/VIDEO_ID" "assets/video/reference.mp4" 0,10,50

Server-side pixeldiff (PNG):
node scripts/node_pixelmatch.js path/to/left.png path/to/right.png outdiff.png
```

Notes & Limitations:
- The worker-based diff is CPU-based and may be slow for large images; expect lag if comparing 4K sized images in the browser.
- For deterministic decoding of encoded videos, consider implementing WebCodecs + container demuxing (mp4box.js + WebCodecs) for exact frame extraction.
 - There's an experimental WebCodecs-friendly path (via `MediaStreamTrackProcessor` & `VideoFrame`) exposed by the UI toggle; if you need more deterministic decoding you can enable it and consider adding mp4box-based demux + WebCodecs `VideoDecoder` for exact frame access.
 - The worker now calculates PSNR and MSE in addition to raw pixel counts for precise analysis.
- `compare-core.js` implements a WebGL renderer with 2D canvas fallback and a worker diff.

For developers:
- Worker: `assets/js/compare-worker.js` calculates the per-pixel difference. It uses OffscreenCanvas to produce a Blob PNG for the preview.
- Main: `assets/js/compare-core.js` handles UI wiring and worker interactions.
- Renderer: `assets/js/compare-renderer.js` exposes GLSL shader modes and blending.
- If you need WebCodecs decoding, implement a WebCodecs demuxer / VideoDecoder path in `compare-codec-webcodecs.js`.
