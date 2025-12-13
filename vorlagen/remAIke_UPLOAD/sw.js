// Service Worker v3.0.0 - VIDEOS COMPLETELY BYPASSED
const CACHE = 'reaimastered-v3';
const STATIC_ASSETS = [
  '/main.html',
  '/offline.html',
  '/manifest.webmanifest',
  '/assets/css/main_styles.min.css',
  '/assets/js/main.min.js',
  '/assets/icons/icon-192.png',
  '/assets/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
  console.log('[SW] Installing v3');
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
      .catch(err => console.warn('[SW] Install failed:', err))
  );
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v3');
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // BYPASS: Non-GET requests
  if (event.request.method !== 'GET') return;
  
  // BYPASS: Videos, HLS, uploads - NEVER intercept streaming content
  if (url.pathname.match(/\.(mp4|webm|m3u8|ts|m4s|mkv|avi|mov)$/i) ||
      url.pathname.startsWith('/assets/video') ||
      url.pathname.startsWith('/uploads') ||
      url.pathname.startsWith('/hls') ||
      url.pathname.startsWith('/api/')) {
    return; // Let browser handle natively
  }
  
  // BYPASS: External resources
  if (url.origin !== location.origin) return;
  
  // For everything else: network-first with cache fallback
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Only cache complete 200 OK responses
        if (response.ok && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(event.request).then(r => r || caches.match('/offline.html')))
  );
});
