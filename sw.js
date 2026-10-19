const CACHE_PREFIX='project3studios-v2:'+self.registration.scope+':';
const CACHE=CACHE_PREFIX+'2.0.5-symmetry-indicator';
const CORE=['./engine/client.js','./engine/worker.js','./engine/sculpt.wasm','./','./index.html','./anatomy-assets.js?v=6','./manifest.webmanifest','./icon-180.png','./icon-192.png','./icon-512.png'];
self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE.map(url=>new Request(url,{cache:'reload'})))).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
 event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE&&key.startsWith(CACHE_PREFIX)).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
 const request=event.request;if(request.method!=='GET')return;
 const url=new URL(request.url);
 if(!['https:','http:'].includes(url.protocol))return;
 if(url.origin!==self.location.origin&&!url.hostname.endsWith('.jsdelivr.net')&&url.hostname!=='cdn.jsdelivr.net')return;
 // Check the server for pages on every visit. Cached HTML is an offline fallback.
 if(url.origin===self.location.origin&&(request.mode==='navigate'||/\/(index\.html)?$/.test(url.pathname))){
  event.respondWith((async()=>{
   try{const response=await fetch(new Request(request,{cache:'no-cache'}));if(!response.ok)throw Error('Page unavailable');const cache=await caches.open(CACHE);await cache.put(request,response.clone());return response}
   catch(error){const cache=await caches.open(CACHE);const hit=await cache.match(request)||await cache.match(new URL('./index.html',self.registration.scope).href);if(hit)return hit;throw error}
  })());return;
 }
 event.respondWith((async()=>{const ownCache=await caches.open(CACHE);const hit=await ownCache.match(request);if(hit)return hit;const response=await fetch(request);if(response.ok||response.type==='opaque'){const cache=await caches.open(CACHE);await cache.put(request,response.clone())}return response})());
});

