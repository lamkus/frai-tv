import { state } from './store.js';

const translations = {
    en: {
        'nav.studio': 'Studio',
        'nav.features': 'Features',
        'nav.youtube': 'YouTube',
        'hero.badge': 'Reference grade | Broadcast ready | Archive safe',
        'hero.subtitle': 'Neural Optical Engine with SMPTE-lock, slowmo slider and 8K streaming. Frame-accurate QC for archives, broadcasters and studios.',
        'hero.ctaStudio': 'Open comparison studio',
        'hero.ctaB2B': 'For institutions',
        'hero.meta': 'Available: 4K/8K | Format: broadcast ready | Contact: remAIke_IT',
        'studio.badge': 'Interactive comparison',
        'studio.title': 'Experience the difference',
        'studio.subtitle': 'Click, drag, zoom – inspect every frame of our optical enhancement.',
        'studio.selectLabel': 'Select comparison:',
        'controls.modesLabel': 'Compare modes',
        'controls.playLabel': 'Play both streams'
    },
    de: {
        'nav.studio': 'Studio',
        'nav.features': 'Funktionen',
        'nav.youtube': 'YouTube',
        'hero.badge': 'Referenzqualität | Sendequalität | Archivstandard',
        'hero.subtitle': 'Neural Optical Engine mit SMPTE-Lock, Slowmo-Slider und 8K Streaming. Frame-genaue QC für Archive, Sender und Studios.',
        'hero.ctaStudio': 'Studio öffnen',
        'hero.ctaB2B': 'Für Institutionen',
        'hero.meta': 'Verfügbar: 4K/8K | Format: Broadcast-ready | Kontakt: remAIke_IT',
        'studio.badge': 'Interaktiver Vergleich',
        'studio.title': 'Erleben Sie den Unterschied',
        'studio.subtitle': 'Klicken, ziehen, zoomen – prüfen Sie jedes Detail unserer Optimierung.',
        'studio.selectLabel': 'Vergleich wählen:',
        'controls.modesLabel': 'Vergleichsmodi',
        'controls.playLabel': 'Beide Streams abspielen'
    },
    fr: {
        'nav.studio': 'Studio',
        'nav.features': 'Fonctionnalités',
        'nav.youtube': 'YouTube',
        'hero.badge': 'Qualité de référence | Diffusion | Archives',
        'hero.subtitle': 'Moteur Optique Neural avec SMPTE-lock, ralenti et streaming 8K. Contrôle image par image pour archives, diffuseurs et studios.',
        'hero.ctaStudio': 'Ouvrir le studio de comparaison',
        'hero.ctaB2B': 'Pour les institutions',
        'hero.meta': 'Disponible : 4K/8K | Format : prêt pour la diffusion | Contact : remAIke_IT',
        'studio.badge': 'Comparaison interactive',
        'studio.title': 'Vivez la différence',
        'studio.subtitle': 'Cliquez, faites glisser, zoomez – inspectez chaque détail de notre amélioration.',
        'studio.selectLabel': 'Sélectionner la comparaison :',
        'controls.modesLabel': 'Modes de comparaison',
        'controls.playLabel': 'Lire les deux flux'
    },
    es: {
        'nav.studio': 'Estudio',
        'nav.features': 'Funciones',
        'nav.youtube': 'YouTube',
        'hero.badge': 'Calidad de referencia | Emisión | Archivo',
        'hero.subtitle': 'Motor Óptico Neural con SMPTE-lock, control de cámara lenta y streaming 8K. QC cuadro a cuadro para archivos, cadenas y estudios.',
        'hero.ctaStudio': 'Abrir estudio de comparación',
        'hero.ctaB2B': 'Para instituciones',
        'hero.meta': 'Disponible: 4K/8K | Formato: listo para emisión | Contacto: remAIke_IT',
        'studio.badge': 'Comparación interactiva',
        'studio.title': 'Experimenta la diferencia',
        'studio.subtitle': 'Haz clic, arrastra y haz zoom: explora cada detalle de nuestra mejora.',
        'studio.selectLabel': 'Seleccionar comparación:',
        'controls.modesLabel': 'Modos de comparación',
        'controls.playLabel': 'Reproducir ambos vídeos'
    },
    mx: {
        'nav.studio': 'Estudio',
        'nav.features': 'Funciones',
        'nav.youtube': 'YouTube',
        'hero.badge': 'Calidad de referencia | Televisión | Archivo',
        'hero.subtitle': 'Motor Óptico Neural con SMPTE-lock, slider de cámara lenta y streaming 8K. QC cuadro a cuadro para televisoras, archivos y estudios.',
        'hero.ctaStudio': 'Abrir estudio de comparación',
        'hero.ctaB2B': 'Para instituciones',
        'hero.meta': 'Disponible: 4K/8K | Formato: listo para emisión | Contacto: remAIke_IT',
        'studio.badge': 'Comparación interactiva',
        'studio.title': 'Siente la diferencia',
        'studio.subtitle': 'Haz clic, arrastra y haz zoom: revisa cada cuadro de nuestra mejora.',
        'studio.selectLabel': 'Seleccionar comparación:',
        'controls.modesLabel': 'Modos de comparación',
        'controls.playLabel': 'Reproducir ambos videos'
    }
};

export let currentLanguage = 'en';

export function applyTranslations(lang) {
    const dict = translations[lang] || translations.en;
    document.documentElement.lang = lang === 'mx' ? 'es-MX' : lang;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const value = dict[key];
        if (value) el.textContent = value;
    });
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });
    currentLanguage = lang;
    localStorage.setItem('remAIke_lang', lang);
}
