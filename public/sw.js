// Service worker for Scientific Dashboard PWA.
// Uses a lazy-cache strategy so hashed Vite build assets are cached on first load.
const CACHE = 'sci-dashboard-v1';

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;

  // Serve cached index.html as offline fallback for navigation requests.
  if (request.mode === 'navigate') {
    e.respondWith(
      fetch(request).catch(() => caches.match('/rag7/index.html'))
    );
    return;
  }

  // Cache-first for static assets; lazily populate the cache on first fetch.
  e.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        if (!response.ok) return response;
        const clone = response.clone();
        caches.open(CACHE).then(cache => cache.put(request, clone));
        return response;
      });
    })
  );
});
