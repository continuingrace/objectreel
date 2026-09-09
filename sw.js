const APP_VERSION='1.1.8';
self.addEventListener('install',event=>event.waitUntil(self.skipWaiting()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  const isApp=url.origin===self.location.origin&&url.pathname.endsWith('/objectreel/app-base.html');
  if(!isApp)return;
  event.respondWith((async()=>{
    try{
      const res=await fetch(req,{cache:'no-store'});
      let html=await res.text();
      html=html.replaceAll('v1.1.0','v1.1.8').replaceAll("VERSION='1.1.0'","VERSION='1.1.8'");
      if(!html.includes('mobile-layout-v1.1.8.css')){
        html=html.replace('</head>','<link rel="stylesheet" href="./mobile-layout-v1.1.8.css?v=1.1.8"></head>');
      }
      const mobileTabs=`<script>(()=>{const placeTabs=()=>{const panel=document.querySelector('.panel'),wrap=document.querySelector('.stage-wrap'),tabs=document.querySelector('.tabs');if(!panel||!wrap||!tabs)return;if(innerWidth<=820){if(tabs.parentElement!==wrap)wrap.appendChild(tabs)}else if(tabs.parentElement!==panel){panel.insertBefore(tabs,panel.firstChild)}};placeTabs();addEventListener('resize',placeTabs)})()<\/script>`;
      if(!html.includes('const placeTabs='))html=html.replace('</body>',mobileTabs+'</body>');
      return new Response(html,{status:res.status,statusText:res.statusText,headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'}});
    }catch(e){return fetch(req);}
  })());
});