const CACHE_NAME = 'stacey-card-v2';
const urlsToCache = [
  '/rag7/',
  '/rag7/index.html',
  '/rag7/style.css',
  '/rag7/app.js',
  '/rag7/vcard.js',
  '/rag7/chat-ui.js',
  '/rag7/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;

  // For navigation requests serve cached index.html as offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() =>
        caches.match('/rag7/index.html')
      )
    );
    return;
  }

  // Cache-first for everything else
  event.respondWith(
    caches.match(request).then(cached => cached || fetch(request))
  );
});