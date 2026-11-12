// Eve PWA service worker. Scope: this folder only.
// Caches the app shell so Eve opens fast and offline shows the page.
// Never caches the live brain (/api/eve), other origins, or non-GET requests.
const VERSION = "eve-shell-v1";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png", "./apple-touch-icon.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;            // fonts, brain, CDN: straight to network
  if (url.pathname.includes("/api/")) return;                  // never cache live answers
  if (req.mode === "navigate") {
    // network first so updates show up; fall back to the cached shell offline
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(VERSION).then((c) => c.put("./index.html", copy));
        return res;
      }).catch(() => caches.match("./index.html"))
    );
    return;
  }
  // static shell files: cache first
  e.respondWith(caches.match(req).then((hit) => hit || fetch(req)));
});
