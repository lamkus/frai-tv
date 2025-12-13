export function initHeroEffects() {
    // Terminal dynamic lines
    const term = document.getElementById('terminal-dynamic');
    if (term) {
        const films = [
            { name: 'Felix the Cat (1919)', status: '4K HDR' },
            { name: 'Superman (1941)', status: '4K 60fps' },
            { name: 'Betty Boop (1932)', status: '4K Color' },
            { name: 'Popeye (1933)', status: '4K HDR' },
            { name: 'Steamboat Willie (1928)', status: '4K' }
        ];
        let filmIdx = 0;
        function showFilm() {
            const film = films[filmIdx];
            term.innerHTML = `<span class="terminal-prompt">▶</span> ${film.name} → ${film.status} <span class="status">✓</span>`;
            filmIdx = (filmIdx + 1) % films.length;
            setTimeout(showFilm, 2500);
        }
        showFilm();
    }

    // Canvas particles - TRUE ANTIGRAVITY (Free floating, bounce, mouse impulse)
    const canvas = document.getElementById('hero-canvas');
    if (canvas && canvas.getContext) {
        const ctx = canvas.getContext('2d');
        function resize() { canvas.width = canvas.clientWidth; canvas.height = canvas.clientHeight; }
        resize();
        window.addEventListener('resize', resize);

        const symbols = ['📼', '💾', '🎞️', '⚡', '🧠', '📺', 'GPU', '4K', '8K', '🎬', '📹', '🖥️'];
        const particles = [];

        // Physics constants
        const FRICTION = 0.99; // Air resistance
        const WALL_BOUNCE = 0.8; // Energy kept after hitting wall
        const MOUSE_FORCE = 2.5; // Impulse strength
        const MAX_SPEED = 15;

        // Initialize particles randomly
        for (let i = 0; i < 25; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                text: symbols[Math.floor(Math.random() * symbols.length)],
                size: 18 + Math.random() * 28,
                vx: (Math.random() - 0.5) * 4, // Initial random drift
                vy: (Math.random() - 0.5) * 4,
                rotation: Math.random() * 360,
                rotationSpeed: (Math.random() - 0.5) * 2,
                mass: 1 + Math.random() * 2 // Mass affects momentum
            });
        }

        // Mouse interaction state
        let mouseX = 0, mouseY = 0, lastMouseX = 0, lastMouseY = 0;
        let mouseVx = 0, mouseVy = 0;

        const trackMouse = (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Calculate mouse velocity
            mouseVx = x - lastMouseX;
            mouseVy = y - lastMouseY;

            lastMouseX = mouseX = x;
            lastMouseY = mouseY = y;
        };

        canvas.addEventListener('mousemove', trackMouse);
        document.addEventListener('mousemove', trackMouse);

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (const p of particles) {
                // 1. Apply Physics
                p.x += p.vx;
                p.y += p.vy;
                p.rotation += p.rotationSpeed;

                // Friction
                p.vx *= FRICTION;
                p.vy *= FRICTION;
                p.rotationSpeed *= 0.99;

                // 2. Wall Collisions (Bounce)
                if (p.x < p.size) { p.x = p.size; p.vx *= -WALL_BOUNCE; p.rotationSpeed += p.vy * 0.1; }
                if (p.x > canvas.width - p.size) { p.x = canvas.width - p.size; p.vx *= -WALL_BOUNCE; p.rotationSpeed -= p.vy * 0.1; }
                if (p.y < p.size) { p.y = p.size; p.vy *= -WALL_BOUNCE; p.rotationSpeed += p.vx * 0.1; }
                if (p.y > canvas.height - p.size) { p.y = canvas.height - p.size; p.vy *= -WALL_BOUNCE; p.rotationSpeed -= p.vx * 0.1; }

                // 3. Mouse Interaction (Collision/Impulse)
                const dx = p.x - mouseX;
                const dy = p.y - mouseY;
                const dist = Math.sqrt(dx * dx + dy * dy);
                const hitRadius = p.size + 50; // Mouse influence radius

                if (dist < hitRadius) {
                    // Calculate impact vector
                    const angle = Math.atan2(dy, dx);
                    const force = (hitRadius - dist) / hitRadius; // Stronger closer

                    // Transfer mouse velocity to particle (Impulse)
                    // If mouse is moving fast, impart that velocity
                    // If mouse is still, just push away gently (static field)

                    const pushX = Math.cos(angle) * force * MOUSE_FORCE;
                    const pushY = Math.sin(angle) * force * MOUSE_FORCE;

                    // Add mouse velocity influence
                    const mouseInfluence = 0.2;
                    p.vx += pushX + (mouseVx * mouseInfluence);
                    p.vy += pushY + (mouseVy * mouseInfluence);

                    // Add spin on impact
                    p.rotationSpeed += (Math.random() - 0.5) * force * 10;
                }

                // Limit speed
                const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                if (speed > MAX_SPEED) {
                    p.vx = (p.vx / speed) * MAX_SPEED;
                    p.vy = (p.vy / speed) * MAX_SPEED;
                }

                // 4. Draw
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rotation * Math.PI / 180);

                // Glow effect
                ctx.shadowBlur = 15;
                ctx.shadowColor = 'rgba(0, 240, 255, 0.4)';

                ctx.fillStyle = 'rgba(0, 240, 255, 0.9)';
                ctx.font = `bold ${p.size}px "Space Grotesk"`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(p.text, 0, 0);
                ctx.restore();
            }

            // Reset mouse velocity decay
            mouseVx *= 0.5;
            mouseVy *= 0.5;

            requestAnimationFrame(draw);
        }
        draw();
    }

    // Matrix rain
    const matrixCanvas = document.getElementById('matrix-rain');
    if (matrixCanvas && matrixCanvas.getContext) {
        const mCtx = matrixCanvas.getContext('2d');
        function resizeMatrix() {
            matrixCanvas.width = window.innerWidth;
            matrixCanvas.height = window.innerHeight;
        }
        resizeMatrix();
        window.addEventListener('resize', resizeMatrix);

        const chars = '01アイウエオカキクケコサシスセソ';
        const fontSize = 14;
        const columns = Math.floor(matrixCanvas.width / fontSize);
        const drops = Array(columns).fill(1);

        function drawMatrix() {
            mCtx.fillStyle = 'rgba(3, 3, 8, 0.05)';
            mCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
            mCtx.fillStyle = '#00f0ff';
            mCtx.font = `${fontSize}px 'JetBrains Mono', monospace`;

            for (let i = 0; i < drops.length; i++) {
                const text = chars[Math.floor(Math.random() * chars.length)];
                mCtx.fillStyle = Math.random() > 0.95 ? '#ff00aa' : '#00f0ff';
                mCtx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > matrixCanvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 45);
    }

    // Cursor trail
    const retroIcons = ['📼', '💿', '🎞️', '📀', '🎬', '📹'];
    let lastTrailTime = 0, trailDistance = 0, lastX = 0, lastY = 0;

    document.addEventListener('mousemove', (e) => {
        const now = Date.now();
        trailDistance += Math.sqrt((e.clientX - lastX) ** 2 + (e.clientY - lastY) ** 2);
        lastX = e.clientX; lastY = e.clientY;

        if (now - lastTrailTime > 80 && trailDistance > 40) {
            lastTrailTime = now;
            trailDistance = 0;
            const icon = document.createElement('span');
            icon.className = 'cursor-trail-icon';
            icon.textContent = retroIcons[Math.floor(Math.random() * retroIcons.length)];
            icon.style.left = e.clientX + 'px';
            icon.style.top = e.clientY + 'px';
            document.body.appendChild(icon);
            setTimeout(() => icon.remove(), 800);
        }
    });
}
