const CACHE_NAME = 'arrow-escape-v1.0.0';
const STATIC_ASSETS = [
    './',
    './index.html',
    './css/styles.css',
    './js/main.js',
    './js/core/game_loop.js',
    './js/engine/pyodide_loader.js',
    './js/ui/screens.js',
    './js/ui/level_select_screen.js',
    './js/ui/auth_screens.js',
    './js/api/client.js',
    './assets/runtime/modules.json',
    './assets/runtime/runtime_manifest.json',
    './assets/runtime/asset_manifest.json',
    'https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Pre-caching static assets');
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('[SW] Pre-cache partial warning:', err);
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
                        console.log('[SW] Clearing old cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    // Skip API routes from static caching
    if (event.request.url.includes('/api/v1/')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
                // Return cached response and update cache in background (Stale-While-Revalidate)
                fetch(event.request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, networkResponse);
                        });
                    }
                }).catch(() => {});
                return cachedResponse;
            }
            return fetch(event.request);
        })
    );
});
