const CACHE_NAME = 'stacey-card-v1';
const FETCH_TIMEOUT = 5000; // 5 seconds timeout for network requests
const urlsToCache = [
  '/rag7/',
  '/rag7/index.html',
  '/rag7/style.css',
  '/rag7/manifest.json'
];

// Helper function to validate response for caching
function isValidResponse(response) {
  return response && 
         response.status === 200 && 
         (response.type === 'basic' || response.type === 'cors');
}

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
        
        // Create AbortController for timeout cleanup
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
        
        return fetch(fetchRequest, { signal: controller.signal })
          .then(response => {
            clearTimeout(timeoutId); // Clean up timeout
            
            // Check if valid response (allow both basic and cors types)
            // Return invalid responses without caching to preserve server behavior
            if (!isValidResponse(response)) {
              return response;
            }
            
            // Clone response for cache and update cache asynchronously
            const responseToCache = response.clone();
            event.waitUntil(
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, responseToCache))
                .catch(error => console.error('Failed to update cache:', error))
            );
            
            return response;
          })
          .catch(error => {
            clearTimeout(timeoutId); // Clean up timeout on error
            console.error('Fetch failed:', error);
            // Could return a custom offline page here
            throw error;
          });
      })
  );
});