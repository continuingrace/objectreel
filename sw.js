const CACHE='objectreel-v1.1.1';
const CORE=['./','./index.html','./manifest.webmanifest','./layout-fix-v1.1.1.css'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const isHTML=e.request.mode==='navigate'||new URL(e.request.url).pathname.endsWith('/index.html');
  if(isHTML){
    e.respondWith(fetch(e.request).then(async r=>{
      let html=await r.text();
      if(!html.includes('layout-fix-v1.1.1.css'))html=html.replace('</head>','<link rel="stylesheet" href="./layout-fix-v1.1.1.css"></head>');
      html=html.replaceAll('v1.1.0','v1.1.1').replaceAll("VERSION='1.1.0'","VERSION='1.1.1'");
      const out=new Response(html,{status:r.status,statusText:r.statusText,headers:{'Content-Type':'text/html; charset=utf-8'}});
      caches.open(CACHE).then(c=>c.put(e.request,out.clone())).catch(()=>{});
      return out;
    }).catch(()=>caches.match(e.request).then(async r=>{
      if(!r)return caches.match('./index.html');
      let html=await r.text();
      if(!html.includes('layout-fix-v1.1.1.css'))html=html.replace('</head>','<link rel="stylesheet" href="./layout-fix-v1.1.1.css"></head>');
      html=html.replaceAll('v1.1.0','v1.1.1').replaceAll("VERSION='1.1.0'","VERSION='1.1.1'");
      return new Response(html,{headers:{'Content-Type':'text/html; charset=utf-8'}});
    })));
    return;
  }
  e.respondWith(fetch(e.request).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});return r}).catch(()=>caches.match(e.request)));
});