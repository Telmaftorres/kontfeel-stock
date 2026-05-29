const CACHE = 'kstock-v1';
const SHELL = ['/', '/index.html', '/scan.html', '/admin.html', '/labels.html', '/style.css', '/api.js', '/config.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
});

self.addEventListener('fetch', e => {
  if (e.request.url.includes('script.google.com')) return;
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
