// compare-renderer.js
// Minimal WebGL renderer with CPU 2D fallback.

export class CompareRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.gl = null;
        this.ctx2d = null;
        this.mode = 'split';
        this.splitX = 0.5; // normalized
        this.threshold = 0.02;
        this.heatmap = true;
        this.center = {x:0.5,y:0.5};
        this.radius = 0.15;
        this.tileSize = 50.0;
        this.useGPUPreferred = true;
        this.blend = 1.0;
            this.uDiffMode = null; // Initialize uDiffMode
        this._init();
    }

    _init() {
        try {
            this.gl = this.canvas.getContext('webgl2') || this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl');
        } catch(e) {
            this.gl = null;
        }

        if (!this.gl) {
            // Fallback to 2D canvas
            this.ctx2d = this.canvas.getContext('2d');
        } else {
            this._setupGL();
        }
    }

    setMode(mode) {
        this.mode = mode;
    }

    setThreshold(v) {
        this.threshold = v;
    }

    setSplit(pos) {
        this.splitX = pos;
    }

    _compileShader(type, src) {
        const gl = this.gl;
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
            console.error('Shader compile error', gl.getShaderInfoLog(s));
            gl.deleteShader(s);
            return null;
        }
        return s;
    }

    _createProgram(vs, fs) {
        const gl = this.gl;
        const v = this._compileShader(gl.VERTEX_SHADER, vs);
        const f = this._compileShader(gl.FRAGMENT_SHADER, fs);
        const p = gl.createProgram();
        gl.attachShader(p, v);
        gl.attachShader(p, f);
        gl.linkProgram(p);
        if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
            console.error('Program link error', gl.getProgramInfoLog(p));
            return null;
        }
        return p;
    }

    _setupGL() {
        const gl = this.gl;

        // Vertex shader
        const vsSource = `
        attribute vec2 aPos;
        attribute vec2 aUV;
        varying vec2 vUV;
        void main() {
            vUV = aUV;
            gl_Position = vec4(aPos, 0.0, 1.0);
        }
        `;

        // Fragment shader (handles split, difference and heatmap)
        const fsSource = `
        precision mediump float;
        uniform sampler2D uA;
        uniform sampler2D uB;
        uniform float uSplitX;
        uniform vec2 uCenter;
        uniform float uRadius;
        uniform float uTileSize;
        uniform float uThreshold;
        uniform float uBlend;
        uniform int uMode; // 0=split, 1=diff, 2=heatmap, 3=circle, 4=checkerboard
        uniform int uDiffMode; // 0 = RGB euclidean, 1 = luma absolute
            uniform int uPalette; // 0=red-green,1=blue-orange,2=grayscale
        varying vec2 vUV;

        vec3 heatmap(float v) {
            // map 0..1 to green->yellow->red
            if (uPalette == 0) {
                // red->green
                return vec3(1.0 - v, v, 0.0) * vec3(1.0, 0.9, 0.4);
            } else if (uPalette == 1) {
                // blue->orange
                return vec3(1.0 - v, 0.5 * v, v * 0.2 + 0.2);
            }
            // grayscale
            return vec3(v, v, v);
        }

        void main() {
            vec4 a = texture2D(uA, vUV);
            vec4 b = texture2D(uB, vUV);
            if (uMode == 0) {
                // split
                if (vUV.x < uSplitX) {
                    gl_FragColor = a;
                } else {
                    gl_FragColor = b;
                }
                return;
            }

            float delta = length(a.rgb - b.rgb) / 1.73205; // normalized by sqrt(3)
            if (uDiffMode == 1) {
                float la = dot(a.rgb, vec3(0.2126, 0.7152, 0.0722));
                float lb = dot(b.rgb, vec3(0.2126, 0.7152, 0.0722));
                delta = abs(la - lb);
            }
            if (uMode == 3) {
                // circle reveal: show b inside circle centered at uCenter
                float d = distance(vUV, uCenter);
                if (d < uRadius) {
                    gl_FragColor = b;
                } else {
                    gl_FragColor = a;
                }
                return;
            }

            if (uMode == 4) {
                // checkerboard pattern: use tile size in pixels, convert to uv
                float tiles = uTileSize;
                vec2 coord = vUV * tiles;
                float f = mod(floor(coord.x) + floor(coord.y), 2.0);
                if (f < 0.5) gl_FragColor = a; else gl_FragColor = b;
                return;
            }
            if (uMode == 1) {
                // difference visual: red overlay blended via uBlend
                vec4 diffColor;
                if (delta < uThreshold) {
                    diffColor = a;
                } else {
                    diffColor = vec4(vec3(1.0, 0.0, 0.0) * delta + vec3(0.0), 1.0);
                }
                gl_FragColor = mix(a, diffColor, uBlend);
                return;
            }

            if (uMode == 2) {
                // heatmap overlay, mix with original scaled by uBlend
                vec3 hm = heatmap(delta);
                gl_FragColor = vec4(mix(a.rgb, hm, delta * uBlend), 1.0);
                return;
            }

            gl_FragColor = a;
        }
        `;

        const prog = this._createProgram(vsSource, fsSource);
        gl.useProgram(prog);
        this.program = prog;

        // Setup buffers
        const positions = new Float32Array([
            -1, -1, 0, 0,
             1, -1, 1, 0,
            -1,  1, 0, 1,
             1,  1, 1, 1
        ]);

        const posBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

        const aPos = gl.getAttribLocation(prog, 'aPos');
        const aUV = gl.getAttribLocation(prog, 'aUV');
        const FSIZE = positions.BYTES_PER_ELEMENT;
        gl.enableVertexAttribArray(aPos);
        gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, FSIZE * 4, 0);
        gl.enableVertexAttribArray(aUV);
        gl.vertexAttribPointer(aUV, 2, gl.FLOAT, false, FSIZE * 4, FSIZE * 2);

        // textures
        this.texA = gl.createTexture();
        this.texB = gl.createTexture();

        // uniform locations
        this.uA = gl.getUniformLocation(prog, 'uA');
        this.uB = gl.getUniformLocation(prog, 'uB');
        this.uSplitX = gl.getUniformLocation(prog, 'uSplitX');
        this.uThreshold = gl.getUniformLocation(prog, 'uThreshold');
        this.uBlend = gl.getUniformLocation(prog, 'uBlend');
        this.uMode = gl.getUniformLocation(prog, 'uMode');
        this.uCenter = gl.getUniformLocation(prog, 'uCenter');
        this.uRadius = gl.getUniformLocation(prog, 'uRadius');
        this.uTileSize = gl.getUniformLocation(prog, 'uTileSize');
        this.uDiffMode = gl.getUniformLocation(prog, 'uDiffMode');
        this.uPalette = gl.getUniformLocation(prog, 'uPalette');

        gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);

        gl.clearColor(0,0,0,1);
    }

    setCenter(normX, normY) {
        this.center = {x: normX, y: normY};
    }

    setRadius(r) {
        this.radius = r; // normalized 0..1
    }

    setTileSize(px) {
        this.tileSize = px;
    }

    setDiffMode(mode) {
        // 0 = RGB, 1 = Luma
        this.diffMode = mode;
    }

    setPalette(p) { this.palette = p; }

    setBlend(v) { this.blend = v; }

    setUseGPU(flag) {
        this.useGPUPreferred = !!flag;
    }

    _uploadTexture(tex, image) {
        const gl = this.gl;
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        try {
            gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        } catch (e) {
            // fallback: if imageBitmap can't be used directly
            // draw to a hidden canvas then read
            const c = document.createElement('canvas');
            c.width = image.width; c.height = image.height;
            const ctx = c.getContext('2d');
            ctx.drawImage(image, 0, 0);
            gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, c);
        }
    }

    async render(imageA, imageB) {
        // imageA/B can be Image, ImageBitmap, or canvas
        if (this.useGPUPreferred && this.gl) {
            const gl = this.gl;
            // resize if needed
            if (this.canvas.width !== imageA.width || this.canvas.height !== imageA.height) {
                this.canvas.width = imageA.width;
                this.canvas.height = imageA.height;
                gl.viewport(0, 0, this.canvas.width, this.canvas.height);
            }

            this._uploadTexture(this.texA, imageA);
            this._uploadTexture(this.texB, imageB);

            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.activeTexture(gl.TEXTURE0);
            gl.bindTexture(gl.TEXTURE_2D, this.texA);
            gl.uniform1i(this.uA, 0);
            gl.activeTexture(gl.TEXTURE1);
            gl.bindTexture(gl.TEXTURE_2D, this.texB);
            gl.uniform1i(this.uB, 1);
            gl.uniform1f(this.uSplitX, this.splitX);
                gl.uniform1f(this.uThreshold, this.threshold);
                gl.uniform1f(this.uBlend, this.blend || 1.0);
            gl.uniform2f(this.uCenter, this.center?.x || 0.5, this.center?.y || 0.5);
            gl.uniform1f(this.uRadius, this.radius || 0.1);
            gl.uniform1f(this.uTileSize, this.tileSize || 50.0);
                gl.uniform1i(this.uDiffMode, this.diffMode || 0); // Set uniform for diffMode
                gl.uniform1i(this.uPalette, this.palette || 0);
            let modeid = 0;
            if (this.mode === 'split') modeid = 0;
            else if (this.mode === 'difference') modeid = 1;
            else if (this.mode === 'heatmap') modeid = 2;
            gl.uniform1i(this.uMode, modeid);

            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            return;
        }

        // Fallback to 2D canvas
        if (!this.ctx2d) return;
        this.canvas.width = imageA.width;
        this.canvas.height = imageA.height;
        const ctx = this.ctx2d;
        ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
        ctx.drawImage(imageA, 0, 0);
        if (this.mode === 'split') {
            const px = Math.floor(this.splitX * this.canvas.width);
            ctx.save();
            ctx.beginPath();
            ctx.rect(px, 0, this.canvas.width - px, this.canvas.height);
            ctx.clip();
            ctx.drawImage(imageB, 0, 0);
            ctx.restore();
            return;
        }
        if (this.mode === 'circle') {
            ctx.save();
            const centerX = Math.floor((this.center?.x || 0.5) * this.canvas.width);
            const centerY = Math.floor((this.center?.y || 0.5) * this.canvas.height);
            const radiusPx = Math.floor((this.radius || 0.1) * Math.min(this.canvas.width, this.canvas.height));
            ctx.beginPath();
            ctx.arc(centerX, centerY, radiusPx, 0, Math.PI*2);
            ctx.clip();
            ctx.drawImage(imageB, 0, 0);
            ctx.restore();
            return;
        }

        if (this.mode === 'difference') {
            // simple difference overlay using globalCompositeOperation with blend alpha
            ctx.save();
            ctx.globalCompositeOperation = 'difference';
            ctx.globalAlpha = this.blend || 1.0;
            ctx.drawImage(imageB, 0, 0);
            ctx.restore();
            return;
        }

        if (this.mode === 'heatmap') {
            // CPU-based heatmap fallback uses difference composite as approximation with alpha mix
            ctx.save();
            ctx.globalCompositeOperation = 'difference';
            ctx.globalAlpha = this.blend || 1.0;
            ctx.drawImage(imageB, 0, 0);
            ctx.globalCompositeOperation = 'source-over';
            ctx.restore();
            return;
        }
        if (this.mode === 'checkerboard') {
            const tilePx = Math.floor(this.tileSize || 50.0);
            for (let y = 0; y < this.canvas.height; y += tilePx) {
                for (let x = 0; x < this.canvas.width; x += tilePx) {
                    const f = ((Math.floor(x/tilePx) + Math.floor(y/tilePx)) % 2);
                    if (f === 0) ctx.drawImage(imageA, x, y, tilePx, tilePx, x, y, tilePx, tilePx);
                    else ctx.drawImage(imageB, x, y, tilePx, tilePx, x, y, tilePx, tilePx);
                }
            }
            return;
        }
    }
}
