const CACHE_NAME = 'arrow-escape-pwa-v1.0.0';
const STATIC_ASSETS = [
    './',
    './index.html',
    './offline.html',
    './css/styles.css',
    './js/main.js',
    './js/core/game_loop.js',
    './js/engine/pyodide_loader.js',
    './js/ui/screens.js',
    './js/ui/level_select_screen.js',
    './js/ui/auth_screens.js',
    './js/api/client.js',
    './manifest.json',
    './favicon.ico',
    './assets/runtime/modules.json',
    './assets/runtime/runtime_manifest.json',
    './assets/runtime/asset_manifest.json',
    './assets/runtime/apple-touch-icon.png',
    './assets/runtime/maskable-icon.png',
    './assets/runtime/icon-192.png',
    './assets/runtime/icon-512.png',
    'https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js',
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-caching static assets & offline fallback');
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('[ServiceWorker] Pre-cache partial warning:', err);
            });
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[ServiceWorker] Purging stale cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    if (event.request.url.includes('/api/v1/')) {
        return; // Skip API calls from static SW cache
    }
    
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
                fetch(event.request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, networkResponse);
                        });
                    }
                }).catch(() => {});
                return cachedResponse;
            }
            
            return fetch(event.request).catch(() => {
                if (event.request.mode === 'navigate') {
                    return caches.match('./offline.html');
                }
            });
        })
    );
});
