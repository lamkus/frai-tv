    const VIDEO_SERVER = ''; // Relative path for same-origin serving

    // ──────────────────────────────────────────────────────────────
    // I18N SETUP
    // ──────────────────────────────────────────────────────────────
    const translations = {
        en: {
            'nav.studio': 'Studio',
            'nav.features': 'Features',
            'nav.youtube': 'YouTube',

            'hero.badge': 'Reference grade • Broadcast ready • Archive safe',
            'hero.title': 'FILM HERITAGE. REIMAGINED.',
            'hero.subtitle': 'AI-assisted restoration for archives, broadcasters and studios — frame-by-frame, manual QC and master-quality deliverables.',
            'hero.ctaStudio': '🎬 Open comparison studio',
            'hero.ctaB2B': 'For institutions',
            'hero.meta': 'Available: 4K/8K • Format: broadcast ready • Contact: remAIke_IT',

            'studio.badge': '✨ Interactive comparison',
            'studio.title': 'Experience the difference',
            'studio.subtitle': 'Click, drag, zoom – explore every detail of our AI enhancement.',
            'studio.selectLabel': 'Select comparison:',

            'features.badge': '🛠️ Technology stack',
            'features.title': 'Enhancement pipeline',
            'features.subtitle': 'State-of-the-art AI models for video restoration.',

            'controls.modesLabel': 'Compare modes',
            'controls.modeSideBySide': 'Side by side',
            'controls.modeSlider': 'Slider',
            'controls.modeClick': 'Click',
            'controls.modeZoom': 'Zoom',
            'controls.playLabel': 'Play both streams',
            'controls.sync': 'Sync',
            'controls.fullscreen': 'Fullscreen'
        },
        de: {
            'nav.studio': 'Studio',
            'nav.features': 'Funktionen',
            'nav.youtube': 'YouTube',

            'hero.badge': 'Referenzqualität • Sendequalität • Archivstandard',
            'hero.title': 'FILMERBE. NEU ERLEBT.',
            'hero.subtitle': 'KI-gestützte Restaurierung für Archive, Sender und Produktionshäuser — Frame-by-frame, manuelle QC und Master-Qualität.',
            'hero.ctaStudio': '🎬 Studio öffnen',
            'hero.ctaB2B': 'Für Institutionen',
            'hero.meta': 'Verfügbar: 4K/8K • Format: Broadcast-ready • Kontakt: remAIke_IT',

            'studio.badge': '✨ Interaktiver Vergleich',
            'studio.title': 'Erleben Sie den Unterschied',
            'studio.subtitle': 'Klicken, ziehen, zoomen – prüfen Sie jedes Detail unserer KI-Optimierung.',
            'studio.selectLabel': 'Vergleich wählen:',

            'features.badge': '🛠️ Technologie-Stack',
            'features.title': 'Enhancement-Pipeline',
            'features.subtitle': 'State-of-the-Art KI-Modelle für Videorestaurierung.',

            'controls.modesLabel': 'Vergleichsmodi',
            'controls.modeSideBySide': 'Nebeneinander',
            'controls.modeSlider': 'Slider',
            'controls.modeClick': 'Klick',
            'controls.modeZoom': 'Zoom',
            'controls.playLabel': 'Beide Streams abspielen',
            'controls.sync': 'Sync',
            'controls.fullscreen': 'Vollbild'
        },
        fr: {
            'nav.studio': 'Studio',
            'nav.features': 'Fonctionnalités',
            'nav.youtube': 'YouTube',

            'hero.badge': 'Qualité de référence • Diffusion • Archives',
            'hero.title': 'PATRIMOINE CINÉMA. RÉINVENTÉ.',
            'hero.subtitle': 'Restauration assistée par IA pour archives, diffuseurs et studios — image par image, contrôle manuel et masters prêts pour la diffusion.',
            'hero.ctaStudio': '🎬 Ouvrir le studio de comparaison',
            'hero.ctaB2B': 'Pour les institutions',
            'hero.meta': 'Disponible : 4K/8K • Format : prêt pour la diffusion • Contact : remAIke_IT',

            'studio.badge': '✨ Comparaison interactive',
            'studio.title': 'Vivez la différence',
            'studio.subtitle': 'Cliquez, faites glisser, zoomez – inspectez chaque détail de notre amélioration IA.',
            'studio.selectLabel': 'Sélectionner la comparaison :',

            'features.badge': '🛠️ Pile technologique',
            'features.title': 'Pipeline d’amélioration',
            'features.subtitle': "Modèles d’IA de pointe pour la restauration vidéo.",

            'controls.modesLabel': 'Modes de comparaison',
            'controls.modeSideBySide': 'Côte à côte',
            'controls.modeSlider': 'Slider',
            'controls.modeClick': 'Clic',
            'controls.modeZoom': 'Zoom',
            'controls.playLabel': 'Lire les deux flux',
            'controls.sync': 'Sync',
            'controls.fullscreen': 'Plein écran'
        },
        es: {
            'nav.studio': 'Estudio',
            'nav.features': 'Funciones',
            'nav.youtube': 'YouTube',

            'hero.badge': 'Calidad de referencia • Emisión • Archivo',
            'hero.title': 'PATRIMONIO FÍLMICO. REIMAGINADO.',
            'hero.subtitle': 'Restauración asistida por IA para archivos, cadenas y estudios — fotograma a fotograma, control manual y masters listos para emisión.',
            'hero.ctaStudio': '🎬 Abrir estudio de comparación',
            'hero.ctaB2B': 'Para instituciones',
            'hero.meta': 'Disponible: 4K/8K • Formato: listo para emisión • Contacto: remAIke_IT',

            'studio.badge': '✨ Comparación interactiva',
            'studio.title': 'Experimenta la diferencia',
            'studio.subtitle': 'Haz clic, arrastra y haz zoom: explora cada detalle de nuestra mejora con IA.',
            'studio.selectLabel': 'Seleccionar comparación:',

            'features.badge': '🛠️ Stack tecnológico',
            'features.title': 'Pipeline de mejora',
            'features.subtitle': 'Modelos de IA de última generación para restauración de vídeo.',

            'controls.modesLabel': 'Modos de comparación',
            'controls.modeSideBySide': 'Lado a lado',
            'controls.modeSlider': 'Slider',
            'controls.modeClick': 'Clic',
            'controls.modeZoom': 'Zoom',
            'controls.playLabel': 'Reproducir ambos vídeos',
            'controls.sync': 'Sync',
            'controls.fullscreen': 'Pantalla completa'
        },
        mx: {
            'nav.studio': 'Estudio',
            'nav.features': 'Funciones',
            'nav.youtube': 'YouTube',

            'hero.badge': 'Calidad de referencia • Televisión • Archivo',
            'hero.title': 'LEGADO DEL CINE. REIMAGINADO.',
            'hero.subtitle': 'Restauración asistida por IA para archivos, televisoras y estudios — cuadro por cuadro, revisión manual y masters listos para pantalla grande.',
            'hero.ctaStudio': '🎬 Abrir estudio de comparación',
            'hero.ctaB2B': 'Para instituciones',
            'hero.meta': 'Disponible: 4K/8K • Formato: listo para emisión • Contacto: remAIke_IT',

            'studio.badge': '✨ Comparación interactiva',
            'studio.title': 'Siente la diferencia',
            'studio.subtitle': 'Haz clic, arrastra y haz zoom: revisa cada cuadro de nuestra mejora con IA.',
            'studio.selectLabel': 'Seleccionar comparación:',

            'features.badge': '🛠️ Stack tecnológico',
            'features.title': 'Pipeline de mejora',
            'features.subtitle': 'Modelos de IA de última generación para restauración de video.',

            'controls.modesLabel': 'Modos de comparación',
            'controls.modeSideBySide': 'Lado a lado',
            'controls.modeSlider': 'Slider',
            'controls.modeClick': 'Clic',
            'controls.modeZoom': 'Zoom',
            'controls.playLabel': 'Reproducir ambos videos',
            'controls.sync': 'Sync',
            'controls.fullscreen': 'Pantalla completa'
        }
    };

    let currentLanguage = 'en';

    function applyTranslations(lang) {
        const dict = translations[lang] || translations.en;
        document.documentElement.lang = lang === 'mx' ? 'es-MX' : lang;
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const value = dict[key];
            if (!value) return;
            // Allow icons/emojis before text, so only replace text node if needed
            if (el.tagName === 'A' || el.tagName === 'BUTTON' || el.tagName === 'SPAN' || el.tagName === 'DIV' || el.tagName === 'H1' || el.tagName === 'H2' || el.tagName === 'P') {
                el.textContent = value;
            }
        });

        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
        });
        currentLanguage = lang;
        localStorage.setItem('remAIke_lang', lang);
    }

    // Hero effects: typewriter, terminal, canvas background
    function initHeroEffects() {
        // Typewriter headline
        const tw = document.querySelector('.typewriter');
        if (tw) {
            const text = tw.textContent.trim();
            tw.textContent = '';
            let idx = 0;
            const speed = 50;
            const type = () => {
                if (idx <= text.length) {
                    tw.textContent = text.substring(0, idx);
                    idx++;
                    setTimeout(type, speed);
                }
            };
            type();
        }

        // Terminal dynamic lines - Film restoration messages
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

        // Canvas particles background (subtle)
        const canvas = document.getElementById('hero-canvas');
        if (canvas && canvas.getContext) {
            const ctx = canvas.getContext('2d');
            function resize() { canvas.width = canvas.clientWidth; canvas.height = canvas.clientHeight; }
            resize();
            window.addEventListener('resize', resize);

            const particles = [];
            for (let i = 0; i < 24; i++) {
                particles.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, r: 6 + Math.random()*20, vx: (Math.random()-0.5)*0.2, vy: (Math.random()-0.5)*0.2, a: 0.08 + Math.random()*0.2 });
            }
            function draw() {
                ctx.clearRect(0,0,canvas.width, canvas.height);
                const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
                g.addColorStop(0, 'rgba(0,240,255,0.03)');
                g.addColorStop(1, 'rgba(124,58,237,0.03)');
                ctx.fillStyle = g; ctx.fillRect(0,0,canvas.width, canvas.height);
                for (const p of particles) {
                    p.x += p.vx; p.y += p.vy;
                    if (p.x < -50) p.x = canvas.width + 50; if (p.y < -50) p.y = canvas.height + 50; if (p.x > canvas.width + 50) p.x = -50; if (p.y > canvas.height +50) p.y = -50;
                    ctx.beginPath(); ctx.fillStyle = `rgba(255,255,255,${p.a})`; ctx.arc(p.x, p.y, p.r, 0, Math.PI*2); ctx.fill();
                }
                requestAnimationFrame(draw);
            }
            draw();
        }

        // ──────────────────────────────────────────────────────────────
        // MATRIX RAIN EFFECT (subtle binary rain)
        // ──────────────────────────────────────────────────────────────
        const matrixCanvas = document.getElementById('matrix-rain');
        if (matrixCanvas && matrixCanvas.getContext) {
            const mCtx = matrixCanvas.getContext('2d');
            function resizeMatrix() {
                matrixCanvas.width = window.innerWidth;
                matrixCanvas.height = window.innerHeight;
            }
            resizeMatrix();
            window.addEventListener('resize', resizeMatrix);

            const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
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
                    const x = i * fontSize;
                    const y = drops[i] * fontSize;

                    // Vary color slightly
                    mCtx.fillStyle = Math.random() > 0.95 ? '#ff00aa' : (Math.random() > 0.9 ? '#7c3aed' : '#00f0ff');
                    mCtx.fillText(text, x, y);

                    if (y > matrixCanvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }
            setInterval(drawMatrix, 45);
        }

        // ──────────────────────────────────────────────────────────────
        // RETRO CURSOR TRAIL (VHS, CD, Film icons)
        // ──────────────────────────────────────────────────────────────
        const retroIcons = ['📼', '💿', '🎞️', '📀', '🎬', '📹'];
        let lastTrailTime = 0;
        const trailThrottle = 80; // ms between icons
        let trailDistance = 0;
        let lastX = 0, lastY = 0;

        document.addEventListener('mousemove', (e) => {
            const now = Date.now();
            const dx = e.clientX - lastX;
            const dy = e.clientY - lastY;
            trailDistance += Math.sqrt(dx * dx + dy * dy);
            lastX = e.clientX;
            lastY = e.clientY;

            if (now - lastTrailTime > trailThrottle && trailDistance > 40) {
                lastTrailTime = now;
                trailDistance = 0;

                const icon = document.createElement('span');
                icon.className = 'cursor-trail-icon';
                icon.textContent = retroIcons[Math.floor(Math.random() * retroIcons.length)];
                icon.style.left = e.clientX + 'px';
                icon.style.top = e.clientY + 'px';
                document.body.appendChild(icon);

                // Remove after animation
                setTimeout(() => icon.remove(), 800);
            }
        });

        // B2B button opens the modal
        const b2b = document.getElementById('btn-b2b');
        const modal = document.getElementById('b2b-modal');
        const modalClose = document.getElementById('b2b-close');
        const modalCancel = document.getElementById('b2b-cancel');
        const modalForm = document.getElementById('b2b-form');

        if (b2b && modal) {
            b2b.addEventListener('click', (e) => {
                e.preventDefault();
                modal.classList.add('open');
                modal.setAttribute('aria-hidden', 'false');
            });
        }
        if (modalClose) modalClose.addEventListener('click', () => {
            modal.classList.remove('open');
            modal.setAttribute('aria-hidden', 'true');
        });
        if (modalCancel) modalCancel.addEventListener('click', () => {
            modal.classList.remove('open');
            modal.setAttribute('aria-hidden', 'true');
        });

        if (modalForm) {
            modalForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                // Collect form data
                const org = document.getElementById('org').value.trim();
                const email = document.getElementById('email').value.trim();
                const contactName = document.getElementById('contact-name').value.trim();
                const sector = document.getElementById('sector').value;
                const scope = document.getElementById('scope').value;
                const description = document.getElementById('description').value.trim();
                const gdprConsent = document.getElementById('gdpr').checked;

                // Validation
                if (!org) {
                    alert('Bitte geben Sie Ihre Organisation ein.');
                    document.getElementById('org').focus();
                    return;
                }

                if (!email) {
                    alert('Bitte geben Sie eine E-Mail-Adresse ein.');
                    document.getElementById('email').focus();
                    return;
                }

                // Email format validation
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    alert('Bitte geben Sie eine gültige E-Mail-Adresse ein.');
                    document.getElementById('email').focus();
                    return;
                }

                if (!sector || sector === '') {
                    alert('Bitte wählen Sie eine Branche aus.');
                    return;
                }

                if (!scope || scope === '') {
                    alert('Bitte wählen Sie den Projektumfang aus.');
                    return;
                }

                if (!gdprConsent) {
                    alert('Bitte akzeptieren Sie unsere Datenschutzrichtlinie.');
                    document.getElementById('gdpr').focus();
                    return;
                }

                // Disable submit button while processing
                const submitBtn = modalForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Wird übermittelt...';

                try {
                    const response = await fetch('/api/offer', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            org,
                            email,
                            contact_name: contactName,
                            sector,
                            scope,
                            description,
                            gdpr: true
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(`✓ Vielen Dank! Ihre Anfrage (${result.offerId}) wurde erfolgreich übermittelt.\n\nWir senden Ihnen in Kürze ein detailliertes Angebot per E-Mail zu.`);
                        modalForm.reset();
                        modal.classList.remove('open');
                        modal.setAttribute('aria-hidden', 'true');
                    } else {
                        alert(`Fehler bei der Übermittlung: ${result.error}`);
                    }
                } catch (err) {
                    console.error('B2B offer error:', err);
                    alert('Fehler: Anfrage konnte nicht übermittelt werden. Bitte versuchen Sie es später erneut oder kontaktieren Sie uns unter hello@remAIke.IT');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            });
        }
    }

    // Video Comparisons
    let COMPARISONS = [];

    // Default comparison (Korn - Freak On a Leash) - Licensed Preview
    // Shows only excerpts: 1:00-1:18 and 2:15-2:35 with crossfade
    const DEFAULT_COMPARISON = {
        id: 'korn-freak-preview',
        name: 'Korn – Freak On a Leash (4K Upscale) • Licensed Preview',
        original: 'uploads/korn/preview/original_preview.mp4',
        enhanced: 'uploads/korn/preview/enhanced_preview.mp4',
        isPreview: true,
        segments: '1:00-1:18 → 2:15-2:35',
        notice: '© Licensed preview material. Full video available for B2B licensing.'
    };

    // State
    let currentIdx = -1; // -1 = default comparison
    let currentMode = 'slider'; // Slider is default for high-end presentation
    let isPlaying = false;
    let showingEnhanced = true;

    // Elements
    const wrapper = document.getElementById('video-wrapper');
    const videoEnhanced = document.getElementById('video-enhanced');
    const videoOriginal = document.getElementById('video-original');
    const sliderEnhanced = document.getElementById('slider-enhanced');
    const sliderOriginal = document.getElementById('slider-original');
    const sliderHandle = document.getElementById('slider-handle');
    const zoomLens = document.getElementById('zoom-lens');
    const zoomVideo = document.getElementById('zoom-video');
    const zoomLabel = document.getElementById('zoom-label');
    const modeIndicator = document.getElementById('mode-indicator');
    const clickOverlay = document.getElementById('click-overlay');
    const shortcutsPanel = document.getElementById('shortcuts-panel');

    // Fetch Comparisons and populate dropdown
    const dropdown = document.getElementById('comparison-dropdown');
    const rescanBtn = document.getElementById('btn-rescan');

    // HLS Management
    let hlsInstances = [];

    function loadVideo(videoEl, src) {
        if (!src) return;

        // Check if HLS
        if (src.endsWith('.m3u8')) {
            if (Hls.isSupported()) {
                const hls = new Hls({
                    capLevelToPlayerSize: true,
                    maxBufferLength: 30,
                    maxMaxBufferLength: 60
                });
                hls.loadSource(src);
                hls.attachMedia(videoEl);
                hlsInstances.push(hls);
            } else if (videoEl.canPlayType('application/vnd.apple.mpegurl')) {
                videoEl.src = src;
            }
        } else {
            videoEl.src = src;
        }
        videoEl.load();
    }

    async function fetchComparisons() {
        try {
            const res = await fetch(`${VIDEO_SERVER}/api/comparisons`);
            const data = await res.json();
            COMPARISONS = data.comparisons.map(c => {
                // In static build (VIDEO_SERVER === ''), comparisons.json will contain full paths
                // (e.g. videos/<filename>) and may include a preview field.
                let enhancedPath = c.enhanced;
                let originalPath = c.original;
                if (VIDEO_SERVER && VIDEO_SERVER.trim() !== '') {
                    // Use HLS for server videos
                    enhancedPath = `${VIDEO_SERVER}/hls/${c.id}/enhanced.m3u8`;
                    originalPath = c.original ? `${VIDEO_SERVER}/hls/${c.id}/original.m3u8` : null;
                } else {
                    // prefer preview if present
                    enhancedPath = c.preview || c.enhanced || null;
                    originalPath = c.preview || c.original || null;
                }
                return { ...c, enhanced: enhancedPath, original: originalPath };
            });

            // Populate dropdown with server comparisons
            populateDropdown();

            // Load default comparison (Korn)
            loadDefaultComparison();
        } catch (e) {
            console.error('Failed to fetch comparisons:', e);
            // Still load default comparison even if server fails
            loadDefaultComparison();
        }
    }

    // Featured video keywords - only show these in dropdown (max 5 + default)
    const FEATURED_KEYWORDS = ['felix', 'superman', 'betty', 'popeye', 'steamboat'];
    function isFeatureVideo(name) {
        const lower = name.toLowerCase();
        return FEATURED_KEYWORDS.some(kw => lower.includes(kw));
    }

    function populateDropdown() {
        // Keep the default option, add ALL comparisons
        COMPARISONS.forEach((comp) => {
            const idx = COMPARISONS.indexOf(comp);
            const opt = document.createElement('option');
            opt.value = idx;
            opt.textContent = `🎬 ${comp.name}`;
            dropdown.appendChild(opt);
        });
        console.log(`📺 Showing ${COMPARISONS.length + 1} videos (1 default + ${COMPARISONS.length} from server)`);
    }

    function loadDefaultComparison() {
        currentIdx = -1;
        dropdown.value = 'default';

        // Clear HLS instances
        hlsInstances.forEach(h => h.destroy());
        hlsInstances = [];

        const isStatic = !VIDEO_SERVER || VIDEO_SERVER.trim() === '';
        const originalSrc = isStatic ? DEFAULT_COMPARISON.original : `${VIDEO_SERVER}/${DEFAULT_COMPARISON.original}`;
        const enhancedSrc = isStatic ? DEFAULT_COMPARISON.enhanced : `${VIDEO_SERVER}/${DEFAULT_COMPARISON.enhanced}`;

        console.log('Loading default comparison:', { originalSrc, enhancedSrc });

        [videoEnhanced, sliderEnhanced].forEach(v => loadVideo(v, enhancedSrc));
        [videoOriginal, sliderOriginal].forEach(v => loadVideo(v, originalSrc));

        // Autoplay loop after load
        console.log('✅ All videos ready - starting autoplay loop');
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            v.loop = true;
            v.muted = true;
            v.play().catch(e => console.warn('Autoplay blocked:', e));
        });
        isPlaying = true;
        startSyncLoop();

        // Show license notice for preview content
        showLicenseNotice(true);
        console.log('✅ Loaded: Korn – Freak On a Leash (Licensed Preview)');
    }

    // License notice for copyrighted preview material
    function showLicenseNotice(show) {
        let notice = document.getElementById('license-notice');
        if (show) {
            if (!notice) {
                notice = document.createElement('div');
                notice.id = 'license-notice';
                notice.innerHTML = `
                    <div class="license-badge">
                        <span class="license-icon">©</span>
                        <span class="license-text">Licensed Preview • Segments: 1:00-1:18 → 2:15-2:35</span>
                    </div>
                `;
                wrapper.appendChild(notice);
            }
            notice.style.display = 'block';
        } else if (notice) {
            notice.style.display = 'none';
        }
    }

    function showError(msg) {
        wrapper.innerHTML = `
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;padding:60px;text-align:center;">
                <div style="font-size:5rem;margin-bottom:30px;">⚠️</div>
                <h3 style="color:var(--brand-primary);font-size:1.5rem;margin-bottom:15px;">Connection Error</h3>
                <p style="color:var(--text-muted);margin-bottom:30px;max-width:400px;">${msg}</p>
                <button onclick="location.reload()" style="padding:10px 20px;background:var(--brand-primary);border:none;border-radius:5px;cursor:pointer;">Retry</button>
            </div>
        `;
    }

    // Dropdown change handler
    dropdown.addEventListener('change', (e) => {
        if (e.target.value === 'default') {
            loadDefaultComparison();
        } else {
            loadComparison(parseInt(e.target.value));
        }
    });

    // Rescan button
    rescanBtn.addEventListener('click', async () => {
        rescanBtn.classList.add('loading');
        try {
            await fetch(`${VIDEO_SERVER}/api/scan`, { method: 'POST' });
            // Clear existing server options (keep default)
            while (dropdown.options.length > 1) {
                dropdown.remove(1);
            }
            await fetchComparisons();
        } catch (e) {
            console.error('Rescan failed:', e);
        } finally {
            rescanBtn.classList.remove('loading');
        }
    });

    // Load Comparison from server list
    function loadComparison(idx) {
        currentIdx = idx;
        const comp = COMPARISONS[idx];
        if (!comp) {
            console.error('Comparison not found:', idx);
            return;
        }

        dropdown.value = idx;

        // Clear HLS instances
        hlsInstances.forEach(h => h.destroy());
        hlsInstances = [];

        console.log('Loading comparison:', comp.name, { enhanced: comp.enhanced, original: comp.original });

        // Load enhanced video (required)
        if (comp.enhanced) {
            [videoEnhanced, sliderEnhanced].forEach(v => loadVideo(v, enhancedSrc));
        } else {
            console.error('No enhanced video for:', comp.name);
        }

        // Load original video (optional - use enhanced as fallback)
        const originalSrc = comp.original || comp.enhanced;
        if (originalSrc) {
            [videoOriginal, sliderOriginal].forEach(v => loadVideo(v, originalSrc));
        }

        // Show license notice for preview content
        showLicenseNotice(!!comp.isPreview);

        console.log(`✅ Loaded: ${comp.name}`);
        if (isPlaying) playAll();
    }

    // Mode Switching
    function setMode(mode) {
        currentMode = mode;
        wrapper.className = 'video-wrapper ' + mode + '-mode';

        // Update classic control buttons
        document.querySelectorAll('.control-btn[data-mode]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        const modeNames = { sidebyside: 'Side by Side', slider: 'Slider', click: 'Click Compare', zoom: 'Zoom Lens' };
        modeIndicator.textContent = modeNames[mode];
    }

    // Play/Pause
    function playAll() {
        // Sync before playing to ensure all start from same position
        syncVideos();

        // Play all videos
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v && v.paused) {
                v.play().catch(e => console.warn('Play failed:', e));
            }
        });

        isPlaying = true;
        document.getElementById('btn-play').innerHTML = '<span>⏸</span>';
        startSyncLoop();
    }

    function pauseAll() {
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v && !v.paused) v.pause();
        });
        isPlaying = false;
        document.getElementById('btn-play').innerHTML = '<span>▶</span>';
        stopSyncLoop();
    }

    // ========================================
    // BULLETPROOF VIDEO SYNCHRONIZATION
    // Ensures videos NEVER desync, critical for comparisons
    // Implements SMPTE ST 2059-2 based drift correction logic
    // ========================================

    let syncLoopActive = false;
    const SYNC_THRESHOLD = 0.042; // 42ms (approx 1 frame at 24fps) - SMPTE standard tolerance
    const SYNC_CHECK_INTERVAL = 100; // Check every 100ms (10 FPS)

    function syncVideos() {
        if (!videoEnhanced || !videoOriginal) return;

        const masterTime = videoEnhanced.currentTime;
        const slaves = [videoOriginal, sliderEnhanced, sliderOriginal];

        slaves.forEach((slave, idx) => {
            if (!slave || slave.readyState < 2) return; // Skip if not loaded

            const drift = Math.abs(slave.currentTime - masterTime);

            // If drift exceeds threshold, force sync
            if (drift > SYNC_THRESHOLD) {
                console.log(`🔄 Syncing video ${idx}: drift=${drift.toFixed(3)}s`);
                try {
                    slave.currentTime = masterTime;
                } catch (e) {
                    console.warn(`⚠️ Sync failed for video ${idx}:`, e);
                }
            }
        });
    }

    // Start continuous sync loop using RAF for smooth performance
    function startSyncLoop() {
        if (syncLoopActive) return;
        syncLoopActive = true;

        function syncTick() {
            if (!syncLoopActive) return;
            syncVideos();
            setTimeout(() => requestAnimationFrame(syncTick), SYNC_CHECK_INTERVAL);
        }

        requestAnimationFrame(syncTick);
        console.log('✅ Video sync loop started');
    }

    function stopSyncLoop() {
        syncLoopActive = false;
        console.log('⏹️ Video sync loop stopped');
    }

    // Add event-based sync for immediate corrections
    videoEnhanced.addEventListener('timeupdate', syncVideos);
    videoEnhanced.addEventListener('seeked', syncVideos);
    videoEnhanced.addEventListener('play', () => {
        // Sync all slaves when master plays
        [videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v && v.paused) v.play().catch(() => {});
        });
        startSyncLoop();
    });
    videoEnhanced.addEventListener('pause', () => {
        [videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v && !v.paused) v.pause();
        });
    });

    // Recovery mechanism: if any video stalls, resync
    [videoOriginal, sliderEnhanced, sliderOriginal].forEach((slave, idx) => {
        slave.addEventListener('waiting', () => {
            console.warn(`⏳ Video ${idx} stalled, forcing resync`);
            syncVideos();
        });
        slave.addEventListener('playing', () => {
            syncVideos(); // Resync when playback resumes
        });
    });

    // Add error handlers to all video elements
    [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach((video, idx) => {
        const names = ['videoEnhanced', 'videoOriginal', 'sliderEnhanced', 'sliderOriginal'];
        video.addEventListener('error', (e) => {
            console.error(`❌ Video error on ${names[idx]}:`, {
                src: video.src,
                error: video.error,
                code: video.error?.code,
                message: video.error?.message
            });
        });
        video.addEventListener('loadedmetadata', () => {
            console.log(`✅ Video loaded ${names[idx]}:`, {
                src: video.src,
                duration: video.duration,
                width: video.videoWidth,
                height: video.videoHeight
            });
        });
    });

    // Slider Drag
    let isDragging = false;
    sliderHandle.addEventListener('mousedown', () => {
        isDragging = true;
        // Slowmo effect: reduce playbackRate during drag
        videoEnhanced.playbackRate = 0.25;
        videoOriginal.playbackRate = 0.25;
        sliderEnhanced.playbackRate = 0.25;
        sliderOriginal.playbackRate = 0.25;
    });
    document.addEventListener('mouseup', () => {
        isDragging = false;
        // Restore normal speed after drag
        videoEnhanced.playbackRate = 1.0;
        videoOriginal.playbackRate = 1.0;
        sliderEnhanced.playbackRate = 1.0;
        sliderOriginal.playbackRate = 1.0;
    });
    document.addEventListener('mousemove', (e) => {
        if (!isDragging || currentMode !== 'slider') return;
        const rect = wrapper.getBoundingClientRect();
        const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        sliderHandle.style.left = (x * 100) + '%';
        sliderEnhanced.style.clipPath = `inset(0 ${(1-x)*100}% 0 0)`;
    });

    // Magnetic effect removed for performance

    // Zoom Lens - PERFORMANCE OPTIMIERT (Video-Sync statt Canvas!)
    let zoomLevel = 4; // Default 4x
    let currentZoomSource = null; // Welches Video wird gezoomed

    // Sync zoom-video mit Master
    function syncZoomVideo() {
        if (currentMode !== 'zoom' || !currentZoomSource) return;
        if (zoomVideo.src !== currentZoomSource.src) {
            zoomVideo.src = currentZoomSource.src;
            zoomVideo.currentTime = currentZoomSource.currentTime;
            zoomVideo.play().catch(() => {});
        }
        zoomVideo.currentTime = currentZoomSource.currentTime;
    }

    wrapper.addEventListener('mousemove', (e) => {
        // NUR im zoom-mode aktiv
        if (currentMode !== 'zoom') return;

        const rect = wrapper.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Position lens
        zoomLens.style.left = x + 'px';
        zoomLens.style.top = y + 'px';

        // Enhanced auf linker Seite, Original auf rechter
        const isLeftHalf = x < rect.width / 2;
        zoomLabel.textContent = isLeftHalf ? 'Enhanced' : 'Original';
        const newSource = isLeftHalf ? videoEnhanced : videoOriginal;

        // Wechsel Source nur wenn nötig
        if (currentZoomSource !== newSource) {
            currentZoomSource = newSource;
            syncZoomVideo();
        }

        // Berechne Video-Offset für Zoom (verschiebe Video so dass Cursor-Position im Zentrum)
        const zoomPx = -(x / rect.width) * (zoomLevel - 1) * 100;
        const zoomPy = -(y / rect.height) * (zoomLevel - 1) * 100;
        zoomVideo.style.objectPosition = `${50 + zoomPx}% ${50 + zoomPy}%`;
    });

    // Click to Zoom (Magnify) - NUR im zoom-mode
    // PAUSE ON CLICK für Frame-genaue Vergleiche
    let zoomPaused = false;
    wrapper.addEventListener('click', (e) => {
        if (currentMode !== 'zoom') {
            // In anderen Modi: Click toggles Play/Pause (außer Slider-Handle)
            if (e.target.closest('.slider-handle') || e.target.closest('#slider-handle')) return;
            if (currentMode === 'click') return; // Click-Mode hat eigene Logik
            isPlaying ? pauseAll() : playAll();
            return;
        }

        // Zoom-Modus: PAUSE für Standbild-Vergleich
        if (!zoomPaused) {
            pauseAll();
            zoomPaused = true;
            // Show pause indicator
            const indicator = document.createElement('div');
            indicator.id = 'zoom-pause-indicator';
            indicator.innerHTML = '⏸ PAUSED - Click to resume';
            indicator.style.cssText = 'position:absolute;bottom:80px;left:50%;transform:translateX(-50%);padding:10px 20px;background:rgba(0,0,0,0.85);border:1px solid var(--brand-primary);border-radius:8px;color:var(--brand-primary);font-size:0.9rem;z-index:100;';
            wrapper.appendChild(indicator);
        } else {
            playAll();
            zoomPaused = false;
            document.getElementById('zoom-pause-indicator')?.remove();
        }

        // Right-click cycles zoom levels
    });

    // Right-click to cycle zoom levels (ohne Pause)
    wrapper.addEventListener('contextmenu', (e) => {
        if (currentMode !== 'zoom') return;
        e.preventDefault();

        // Cycle zoom levels: 4x -> 8x -> 2x -> 4x
        if (zoomLevel === 4) zoomLevel = 8;
        else if (zoomLevel === 8) zoomLevel = 2;
        else zoomLevel = 4;

        zoomVideo.style.width = (zoomLevel * 100) + '%';
        zoomVideo.style.height = (zoomLevel * 100) + '%';

        // Show feedback
        const feedback = document.createElement('div');
        feedback.textContent = `${zoomLevel}x`;
        feedback.style.position = 'absolute';
        feedback.style.left = e.clientX + 'px';
        feedback.style.top = e.clientY + 'px';
        feedback.style.color = '#fff';
        feedback.style.fontWeight = 'bold';
        feedback.style.pointerEvents = 'none';
        feedback.style.zIndex = '200';
        feedback.style.textShadow = '0 2px 4px rgba(0,0,0,0.8)';
        feedback.style.animation = 'trailFade 0.5s ease-out forwards';
        document.body.appendChild(feedback);
        setTimeout(() => feedback.remove(), 500);
    });

    // Click Compare - hold to see original
    clickOverlay.addEventListener('mousedown', () => {
        showingEnhanced = false;
        updateClickCompare();
    });
    clickOverlay.addEventListener('mouseup', () => {
        showingEnhanced = true;
        updateClickCompare();
    });
    clickOverlay.addEventListener('mouseleave', () => {
        showingEnhanced = true;
        updateClickCompare();
    });
    // Touch support for mobile
    clickOverlay.addEventListener('touchstart', (e) => {
        e.preventDefault();
        showingEnhanced = false;
        updateClickCompare();
    });
    clickOverlay.addEventListener('touchend', () => {
        showingEnhanced = true;
        updateClickCompare();
    });

    function updateClickCompare() {
        const panelE = document.getElementById('panel-enhanced');
        const panelO = document.getElementById('panel-original');
        if (currentMode === 'click') {
            panelE.style.opacity = showingEnhanced ? '1' : '0';
            panelO.style.opacity = showingEnhanced ? '0' : '1';
        } else {
            panelE.style.opacity = '1';
            panelO.style.opacity = '1';
        }
    }

    // Click-Zoom: Click anywhere on video to zoom 400% with smooth animation
    let isZoomed = false;
    const videoGrid = document.getElementById('video-grid');

    // DISABLED: Conflicted with Zoom Lens click-to-magnify
    /*
    videoGrid.addEventListener('click', (e) => {
        if (currentMode !== 'sidebyside') return;

        const rect = videoGrid.getBoundingClientRect();
        const clickX = ((e.clientX - rect.left) / rect.width) * 100;
        const clickY = ((e.clientY - rect.top) / rect.height) * 100;

        if (!isZoomed) {
            // Zoom in to 400% at click point
            videoGrid.style.transition = 'transform 0.4s ease-out';
            videoGrid.style.transformOrigin = `${clickX}% ${clickY}%`;
            videoGrid.style.transform = 'scale(4)';
            isZoomed = true;
        } else {
            // Zoom out
            videoGrid.style.transition = 'transform 0.3s ease-in';
            videoGrid.style.transform = 'scale(1)';
            isZoomed = false;
        }
    });
    */

    // Reset zoom when switching modes (wrap setMode only once DOM is ready)
    const originalSetMode = setMode;
    setMode = function(mode) {
        if (isZoomed) {
            videoGrid.style.transition = 'transform 0.2s ease-in';
            videoGrid.style.transform = 'scale(1)';
            isZoomed = false;
        }
        originalSetMode(mode);
    };

    // Event Listeners - classic control bar
    document.querySelectorAll('.control-btn[data-mode]').forEach(btn => {
        btn.addEventListener('click', () => setMode(btn.dataset.mode));
    });

    document.getElementById('btn-play').addEventListener('click', () => isPlaying ? pauseAll() : playAll());
    document.getElementById('btn-sync').addEventListener('click', syncVideos);
    document.getElementById('btn-fullscreen').addEventListener('click', () => {
        if (wrapper.requestFullscreen) wrapper.requestFullscreen();
    });

    // Frame Stepping Functions
    const FRAME_TIME = 1/24; // 24fps standard

    function frameBack() {
        pauseAll();
        const newTime = Math.max(0, videoEnhanced.currentTime - FRAME_TIME);
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v) v.currentTime = newTime;
        });
        updateTimeline();
    }

    function frameForward() {
        pauseAll();
        const newTime = Math.min(videoEnhanced.duration || 0, videoEnhanced.currentTime + FRAME_TIME);
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v) v.currentTime = newTime;
        });
        updateTimeline();
    }

    // Timeline Scrubber Functions
    const timelineScrubber = document.getElementById('timeline-scrubber');
    const timeCurrent = document.getElementById('time-current');
    const timeDuration = document.getElementById('time-duration');

    function formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    }

    function updateTimeline() {
        if (!videoEnhanced) return;
        const current = videoEnhanced.currentTime || 0;
        const duration = videoEnhanced.duration || 0;
        timelineScrubber.value = duration > 0 ? (current / duration) * 100 : 0;
        timeCurrent.textContent = formatTime(current);
        timeDuration.textContent = formatTime(duration);
    }

    // Timeline seek
    timelineScrubber.addEventListener('input', (e) => {
        const duration = videoEnhanced.duration || 0;
        const seekTime = (parseFloat(e.target.value) / 100) * duration;
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v) v.currentTime = seekTime;
        });
        updateTimeline();
    });

    // Update timeline on video timeupdate
    videoEnhanced.addEventListener('timeupdate', updateTimeline);
    videoEnhanced.addEventListener('loadedmetadata', () => {
        timeDuration.textContent = formatTime(videoEnhanced.duration);
    });

    // Wire up frame stepping buttons
    document.getElementById('btn-frame-back').addEventListener('click', frameBack);
    document.getElementById('btn-frame-forward').addEventListener('click', frameForward);

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return;

        switch(e.key) {
            case ' ': e.preventDefault(); isPlaying ? pauseAll() : playAll(); break;
            case '1': setMode('sidebyside'); break;
            case '2': setMode('slider'); break;
            case '3': setMode('click'); break;
            case '4': setMode('zoom'); break;
            case 'f': case 'F': wrapper.requestFullscreen?.(); break;
            case 's': case 'S': syncVideos(); break;
            case '?': shortcutsPanel.classList.toggle('visible'); break;
            case 'ArrowRight': e.shiftKey ? loadComparison(Math.min(currentIdx + 1, COMPARISONS.length - 1)) : null; break;
            case 'ArrowLeft': e.shiftKey ? loadComparison(Math.max(currentIdx - 1, 0)) : null; break;
            case ',': case '<': frameBack(); break;
            case '.': case '>': frameForward(); break;
            case 'ArrowUp': e.preventDefault(); seekRelative(5); break;
            case 'ArrowDown': e.preventDefault(); seekRelative(-5); break;
        }
    });

    function seekRelative(seconds) {
        const newTime = Math.max(0, Math.min(videoEnhanced.duration || 0, videoEnhanced.currentTime + seconds));
        [videoEnhanced, videoOriginal, sliderEnhanced, sliderOriginal].forEach(v => {
            if (v) v.currentTime = newTime;
        });
        updateTimeline();
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', async () => {
        // Restore original feel: Side by Side as default
        setMode('sidebyside');

        // Wire up classic control buttons
        document.querySelectorAll('.control-btn[data-mode]').forEach(btn => {
            btn.addEventListener('click', () => setMode(btn.dataset.mode));
        });
        document.getElementById('btn-play').addEventListener('click', () => {
            isPlaying ? pauseAll() : playAll();
        });
        document.getElementById('btn-sync').addEventListener('click', syncVideos);
        document.getElementById('btn-fullscreen').addEventListener('click', toggleFullscreen);

        // Language selector
        const stored = localStorage.getItem('remAIke_lang');
        const browserLang = (navigator.language || 'en').toLowerCase();
        let initialLang = stored || (browserLang.startsWith('de') ? 'de' : browserLang.startsWith('fr') ? 'fr' : browserLang.startsWith('es') ? 'es' : 'en');
        if (!translations[initialLang]) initialLang = 'en';
        applyTranslations(initialLang);
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => applyTranslations(btn.getAttribute('data-lang')));
        });

        initHeroEffects();
        await fetchComparisons();
    });
