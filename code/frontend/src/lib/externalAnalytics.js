// External analytics adapters (Matomo + optional GTM)
// Loaded only after explicit GDPR analytics consent.

let externalInitialized = false;

function normalizeBaseUrl(url) {
  return String(url || '')
    .trim()
    .replace(/\/+$/, '');
}

function loadScriptOnce(src) {
  if (!src) return;
  if (document.querySelector(`script[src="${src}"]`)) return;
  const s = document.createElement('script');
  s.async = true;
  s.defer = true;
  s.src = src;
  document.head.appendChild(s);
}

export function initExternalAnalytics() {
  if (externalInitialized) return;

  const matomoUrl = normalizeBaseUrl(import.meta.env.VITE_MATOMO_URL);
  const matomoSiteId = String(import.meta.env.VITE_MATOMO_SITE_ID || '').trim();

  // Matomo
  if (matomoUrl && matomoSiteId) {
    window._paq = window._paq || [];
    window._paq.push(['setTrackerUrl', `${matomoUrl}/matomo.php`]);
    window._paq.push(['setSiteId', matomoSiteId]);
    window._paq.push(['enableLinkTracking']);
    loadScriptOnce(`${matomoUrl}/matomo.js`);
  }

  // Optional GTM (useful for YouTube embed progress triggers)
  const gtmId = String(import.meta.env.VITE_GTM_ID || '').trim();
  if (gtmId) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    loadScriptOnce(`https://www.googletagmanager.com/gtm.js?id=${encodeURIComponent(gtmId)}`);
  }

  externalInitialized = true;
}

export function trackExternalPageView(path, title) {
  if (window._paq) {
    window._paq.push(['setCustomUrl', path]);
    if (title) window._paq.push(['setDocumentTitle', title]);
    window._paq.push(['trackPageView']);
  }
}

export function trackExternalEvent(category, action, name, value) {
  if (window._paq) {
    const v = Number.isFinite(value) ? Math.round(value) : undefined;
    // Matomo signature: trackEvent(category, action, [name], [value])
    if (v !== undefined) {
      window._paq.push(['trackEvent', category, action, name, v]);
    } else if (name) {
      window._paq.push(['trackEvent', category, action, name]);
    } else {
      window._paq.push(['trackEvent', category, action]);
    }
  }
}
