/* Public app resources only. Personal photos and localStorage never enter
 * this cache. The Web packaging helper replaces BUILD_ID per artifact. */
const BUILD_ID = '__PIXELHUB_BUILD_ID__';
const PREFIX = 'pixelhub-v3:' + self.registration.scope + ':';
const CACHE = PREFIX + BUILD_ID;

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const response = await fetch(new URL('offline-manifest.json', self.registration.scope), {cache: 'no-store'});
    if (!response.ok) throw new Error('Offline manifest unavailable');
    const manifest = await response.json();
    if (manifest.version !== BUILD_ID || !Array.isArray(manifest.files)) throw new Error('Offline identity mismatch');
    const cache = await caches.open(CACHE);
    try {
      await cache.addAll(manifest.files.map(path => new Request(new URL(path, self.registration.scope), {cache: 'reload'})));
    } catch (error) {
      await caches.delete(CACHE);
      throw error;
    }
    // A new version waits until previous tabs close, keeping their resources
    // consistent. Never force a reload while the user is painting.
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = (await caches.keys()).filter(key => key.startsWith(PREFIX));
    const retained = new Set([CACHE, ...keys.filter(key => key !== CACHE).slice(-1)]);
    await Promise.all(keys.filter(key => !retained.has(key)).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  const scope = new URL(self.registration.scope);
  if (request.method !== 'GET' || url.origin !== scope.origin || !url.pathname.startsWith(scope.pathname)) return;
  if (url.pathname.endsWith('/offline-worker.js') || url.pathname.endsWith('/offline-manifest.json') || url.pathname.endsWith('/commit.txt')) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    // A parent scope may control an as-yet-unregistered child product.
    // Only this exact application's entry navigation can use its index.
    const ownNavigation = url.pathname === scope.pathname || url.pathname === scope.pathname + 'index.html';
    if (request.mode === 'navigate' && !ownNavigation) return fetch(request);
    const cached = request.mode === 'navigate'
      ? await cache.match(new URL('index.html', self.registration.scope))
      : await cache.match(request, {ignoreSearch: true});
    return cached || fetch(request);
  })());
});
