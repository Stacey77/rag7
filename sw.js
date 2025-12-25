const CACHE_NAME = 'stacey-card-v1';
const urlsToCache = [
  '/rag7/',
  '/rag7/index.html',
  '/rag7/style.css',
  '/rag7/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});