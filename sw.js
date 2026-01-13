const CACHE_NAME = 'stacey-card-v1';
const urlsToCache = [
  '/rag7/',
  '/rag7/index.html',
  '/rag7/style.css',
  '/rag7/manifest.json'
];

// Install event - cache resources and activate immediately
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting()) // Activate immediately
      .catch(error => console.error('Cache installation failed:', error))
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => cacheName !== CACHE_NAME)
            .map(cacheName => caches.delete(cacheName))
        );
      })
      .then(() => self.clients.claim()) // Take control immediately
      .catch(error => console.error('Cache cleanup failed:', error))
  );
});

// Fetch event - cache-first with network fallback and timeout
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        
        // Clone the request for fetch
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest, { 
          // Add timeout to prevent hanging requests
          signal: AbortSignal.timeout ? AbortSignal.timeout(5000) : undefined 
        })
          .then(response => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone response for cache
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => cache.put(event.request, responseToCache))
              .catch(error => console.error('Failed to update cache:', error));
            
            return response;
          })
          .catch(error => {
            console.error('Fetch failed:', error);
            // Could return a custom offline page here
            throw error;
          });
      })
  );
});