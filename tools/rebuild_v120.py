from pathlib import Path
import re

VERSION = '1.2.0'
p = Path('app-base.html')
s = p.read_text(encoding='utf-8')

# Always rebuild from the stable 1.1.0 source file, never from generated index.html.
s = s.replace('v1.1.0', f'v{VERSION}')
s = s.replace("VERSION='1.1.0'", f"VERSION='{VERSION}'")
s = s.replace("if('serviceWorker'in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});", '')

# Mobile: preview owns a second tab bar and a buffer; desktop keeps the original panel tabs.
mobile_tabs = '<div class="mobile-tabs tabs"><button class="tab active" data-tab="bg">BG</button><button class="tab" data-tab="obj">Objects</button><button class="tab" data-tab="motion">Motion</button><button class="tab" data-tab="text">Text</button><button class="tab" data-tab="export">Export</button></div><div class="control-buffer">아래에서 항목을 선택하고 조절하세요</div>'
marker = '</div></div></div><aside class="panel"><div class="tabs">'
assert marker in s, 'stage/panel marker missing'
s = s.replace(marker, '</div></div>' + mobile_tabs + '</div><aside class="panel"><div class="tabs">', 1)

# Add the requested hand-cut/pinking edge frame.
frame_option = '<option value="film">Film Frame</option>'
assert frame_option in s, 'frame option marker missing'
s = s.replace(frame_option, frame_option + '<option value="pinking">Pinking Edge</option>', 1)

# Restore per-photo motion selection and expand motions; all option labels use English consistently.
motion_old = '<section class="section" id="sec-motion"><div class="group"><span class="label">선택 오브젝트 모션</span><select id="motionType" class="select"><option value="none">None</option><option value="float">Float</option><option value="sway">Sway</option><option value="zoom">Slow Zoom</option><option value="drift">Drift</option><option value="thunk">뚱땅 좌우 흔들림</option></select>'
motion_new = '<section class="section" id="sec-motion"><div class="group"><span class="label">오브젝트 선택</span><div id="motionObjectsList" class="objects-list"></div><div class="hint">사진마다 다른 모션을 지정할 수 있습니다.</div></div><div class="group"><span class="label">선택 오브젝트 모션</span><select id="motionType" class="select"><option value="none">None</option><option value="float">Float</option><option value="sway">Sway</option><option value="side">Side Rock</option><option value="drift">Drift</option><option value="zoom">Slow Zoom</option><option value="bounce">Bounce</option><option value="pulse">Pulse</option><option value="orbit">Orbit</option><option value="swing">Swing</option><option value="jitter">Jitter</option><option value="thunk">Wobble</option></select>'
assert motion_old in s, 'motion section marker missing'
s = s.replace(motion_old, motion_new, 1)

# Add explicit save UI as a fallback while keeping autosave.
export_marker = '<section class="section" id="sec-export"><div class="group"><span class="label">영상 길이</span>'
assert export_marker in s, 'export marker missing'
s = s.replace(export_marker, '<section class="section" id="sec-export"><div class="group"><span class="label">프로젝트 저장</span><button id="saveProject" class="btn" style="width:100%">지금 저장</button><div id="saveStatus" class="status">자동 저장 사용 중</div></div><div class="group"><span class="label">영상 길이</span>', 1)

# Reduce memory churn: IndexedDB already clones internally, so do not structuredClone the large data URLs first.
old_save = "async function saveState(){try{if(!db)await openDB();db.transaction('project','readwrite').objectStore('project').put(structuredClone(state),'current')}catch(e){console.warn(e)}}function scheduleSave(){clearTimeout(saveTimer);saveTimer=setTimeout(saveState,250)}"
new_save = "async function saveState(){try{if(!db)await openDB();await new Promise((res,rej)=>{const q=db.transaction('project','readwrite').objectStore('project').put(state,'current');q.onsuccess=()=>res();q.onerror=()=>rej(q.error)});const el=$('saveStatus');if(el)el.textContent='저장됨 · '+new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}catch(e){console.warn(e);const el=$('saveStatus');if(el)el.textContent='저장 실패 · 다시 시도해 주세요'}}function scheduleSave(delay=900){clearTimeout(saveTimer);saveTimer=setTimeout(saveState,delay)}"
assert old_save in s, 'saveState marker missing'
s = s.replace(old_save, new_save, 1)

# Replace the old CSS-animation object renderer with one shared mathematical motion engine.
start = s.index('function frameStyle(o,el)')
end = s.index('function renderTexts()', start)
new_object_engine = r'''function pinkingClip(){const p=[],step=6,amp=2.4;for(let x=0;x<=100;x+=step)p.push(`${x}% ${((x/step)%2?amp:0)}%`);for(let y=0;y<=100;y+=step)p.push(`${100-(((y/step)%2)?amp:0)}% ${y}%`);for(let x=100;x>=0;x-=step)p.push(`${x}% ${100-(((x/step)%2)?amp:0)}%`);for(let y=100;y>=0;y-=step)p.push(`${(((y/step)%2)?amp:0)}% ${y}%`);return `polygon(${p.join(',')})`}
function frameStyle(o,el){el.style.border='0';el.style.padding='0';el.style.background='transparent';el.style.borderRadius='0';el.style.boxShadow='none';el.style.filter='none';el.style.clipPath='none';const f=o.frame||'none';if(f==='rounded')el.style.borderRadius='18px';if(f==='thin')el.style.border='2px solid rgba(255,255,255,.9)';if(f==='polaroid'){el.style.padding='4% 4% 13%';el.style.background='#fff';el.style.boxShadow='0 6px 18px rgba(0,0,0,.16)'}if(f==='shadow')el.style.filter='drop-shadow(0 9px 14px rgba(0,0,0,.28))';if(f==='film'){el.style.border='9px solid #171717';el.style.padding='2px';el.style.background='#171717'}if(f==='pinking')el.style.clipPath=pinkingClip()}
function motionAt(o,t){const d=Math.max(.6,o.speed||4),p=t*Math.PI*2/d,s=Math.sin(p),c=Math.cos(p),s2=Math.sin(p*2);let dx=0,dy=0,dr=0,sc=1;switch(o.motion){case'float':dy=-.012*s;break;case'sway':dr=.055*s;break;case'side':dx=.03*s;dr=.018*s;break;case'drift':dx=.018*s;dy=-.008*c;break;case'zoom':sc=1+.035*(s+1)/2;break;case'bounce':dy=-.018*Math.abs(s);break;case'pulse':sc=1+.045*(s+1)/2;break;case'orbit':dx=.018*c;dy=.010*s;break;case'swing':dr=.095*s;dy=.004*(1-c);break;case'jitter':dx=.006*Math.sin(p*3)+.003*Math.sin(p*7);dy=.004*Math.cos(p*5);dr=.018*Math.sin(p*4);break;case'thunk':dx=.022*s2;dr=.065*s2;break}return{dx,dy,dr,sc}}
function applyTransform(o,el){el.style.left=(o.x??50)+'%';el.style.top=(o.y??50)+'%';el.style.width=(45*(o.scale||1))+'%';el.style.animation='none';el.style.margin='0';el.style.transform=`translate(-50%,-50%) rotate(${o.rotate||0}deg)`;frameStyle(o,el)}
function makePickerThumb(o,list){const w=document.createElement('div');w.className='thumb-wrap'+(o.id===state.selected?' selected':'');const th=document.createElement('img');th.src=o.src;th.className='thumb';th.onclick=()=>{state.selected=o.id;renderObjects()};w.appendChild(th);if(o.cutout||o.processing){const b=document.createElement('span');b.className='badge';b.textContent=o.processing?'…':'✓';w.appendChild(b)}list.appendChild(w)}
function renderObjects(){stage.querySelectorAll('.object').forEach(e=>e.remove());const lists=[$('objectsList'),$('motionObjectsList')].filter(Boolean);lists.forEach(l=>l.innerHTML='');state.objects.forEach((o,i)=>{const img=document.createElement('img');img.src=o.src;img.className='object'+(o.id===state.selected?' selected':'');img.dataset.id=o.id;img.style.zIndex=10+i;applyTransform(o,img);img.onpointerdown=startDrag;stage.appendChild(img);lists.forEach(list=>makePickerThumb(o,list))});syncObject();previewStart=performance.now()}
'''
s = s[:start] + new_object_engine + s[end:]

# Dragging should not write large image state on every pointer move.
old_drag = 'applyTransform(o,e.currentTarget);syncObject();scheduleSave()}function endDrag'
assert old_drag in s, 'drag marker missing'
s = s.replace(old_drag, 'applyTransform(o,e.currentTarget);syncObject()}function endDrag', 1)

# Both desktop and mobile tab bars control the same sections; on mobile, reveal the controls under the sticky preview.
old_tabs = "document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>selectTab(b.dataset.tab));"
new_tabs = "function revealControls(){if(innerWidth>820)return;requestAnimationFrame(()=>{const panel=document.querySelector('.panel');if(!panel)return;const y=panel.getBoundingClientRect().top+scrollY-12;scrollTo({top:Math.max(0,y),behavior:'smooth'})})}document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{selectTab(b.dataset.tab);revealControls()});"
assert old_tabs in s, 'tab handler marker missing'
s = s.replace(old_tabs, new_tabs, 1)

# Preview and export must share exactly the same motion function.
start = s.index('function preview(now)')
end = s.index('function loadImage', start)
new_preview = r'''function preview(now){const dur=state.duration||10,t=((now-previewStart)/1000)%dur,r=stage.getBoundingClientRect();state.objects.forEach((o,i)=>{const el=stage.querySelector(`.object[data-id="${o.id}"]`);if(!el)return;el.style.opacity=Math.max(0,Math.min(1,op(i,t,dur)));const m=motionAt(o,t),deg=(o.rotate||0)+m.dr*180/Math.PI;el.style.transform=`translate(-50%,-50%) translate(${m.dx*r.width}px,${m.dy*r.height}px) rotate(${deg}deg) scale(${m.sc})`});requestAnimationFrame(preview)}
'''
s = s[:start] + new_preview + s[end:]

# Canvas frame renderer with Pinking Edge.
start = s.index('function drawFramed(ctx,im,bw,bh,frame)')
end = s.index('async function exportVideo', start)
new_frame_renderer = r'''function pinkingPath(ctx,bw,bh){const step=Math.max(10,Math.min(bw,bh)*.045),amp=step*.45,x0=-bw/2,y0=-bh/2,x1=bw/2,y1=bh/2;ctx.beginPath();ctx.moveTo(x0,y0);let flip=0;for(let x=x0;x<=x1;x+=step){ctx.lineTo(Math.min(x,x1),y0+(flip?amp:0));flip^=1}flip=0;for(let y=y0;y<=y1;y+=step){ctx.lineTo(x1-(flip?amp:0),Math.min(y,y1));flip^=1}flip=0;for(let x=x1;x>=x0;x-=step){ctx.lineTo(Math.max(x,x0),y1-(flip?amp:0));flip^=1}flip=0;for(let y=y1;y>=y0;y-=step){ctx.lineTo(x0+(flip?amp:0),Math.max(y,y0));flip^=1}ctx.closePath()}
function drawFramed(ctx,im,bw,bh,frame){const f=frame||'none';if(f==='shadow'){ctx.save();ctx.shadowColor='rgba(0,0,0,.35)';ctx.shadowBlur=34;ctx.shadowOffsetY=20;ctx.drawImage(im,-bw/2,-bh/2,bw,bh);ctx.restore();return}if(f==='polaroid'){const px=bw*.055,py=bw*.055,bottom=bw*.16;ctx.fillStyle='#fff';ctx.fillRect(-bw/2-px,-bh/2-py,bw+px*2,bh+py+bottom);ctx.drawImage(im,-bw/2,-bh/2,bw,bh);return}if(f==='thin'){ctx.drawImage(im,-bw/2,-bh/2,bw,bh);ctx.strokeStyle='rgba(255,255,255,.94)';ctx.lineWidth=Math.max(3,bw*.008);ctx.strokeRect(-bw/2,-bh/2,bw,bh);return}if(f==='film'){const b=Math.max(14,bw*.04);ctx.fillStyle='#171717';ctx.fillRect(-bw/2-b,-bh/2-b,bw+b*2,bh+b*2);ctx.drawImage(im,-bw/2,-bh/2,bw,bh);ctx.fillStyle='#eee';for(let x=-bw/2;x<bw/2;x+=bw/8){ctx.fillRect(x,-bh/2-b*.72,bw/18,b*.28);ctx.fillRect(x,bh/2+b*.44,bw/18,b*.28)}return}if(f==='rounded'){ctx.save();roundRect(ctx,-bw/2,-bh/2,bw,bh,Math.min(bw,bh)*.07);ctx.clip();ctx.drawImage(im,-bw/2,-bh/2,bw,bh);ctx.restore();return}if(f==='pinking'){ctx.save();pinkingPath(ctx,bw,bh);ctx.clip();ctx.drawImage(im,-bw/2,-bh/2,bw,bh);ctx.restore();return}ctx.drawImage(im,-bw/2,-bh/2,bw,bh)}
'''
s = s[:start] + new_frame_renderer + s[end:]

# Replace the old export-only motion math with the shared engine.
old_export_motion = "let x=(o.x??50)/100*W,y=(o.y??50)/100*H,r=(o.rotate||0)*Math.PI/180,sc=1,wv=wave(t,o.speed||4);if(o.motion==='float')y-=18*wv;if(o.motion==='sway')r+=.05*wv;if(o.motion==='zoom')sc+=.03*(wv+1);if(o.motion==='drift'){x+=16*wv;y-=9*Math.cos(t*Math.PI*2/(o.speed||4))}if(o.motion==='thunk'){x+=20*Math.sin(t*Math.PI*4/(o.speed||2));r+=.07*Math.sin(t*Math.PI*4/(o.speed||2))}"
new_export_motion = "let x=(o.x??50)/100*W,y=(o.y??50)/100*H,r=(o.rotate||0)*Math.PI/180,sc=1;const mm=motionAt(o,t);x+=mm.dx*W;y+=mm.dy*H;r+=mm.dr;sc*=mm.sc"
assert old_export_motion in s, 'export motion marker missing'
s = s.replace(old_export_motion, new_export_motion, 1)

# Save explicitly on user request and when iOS sends the page to background.
init_marker = "$('duration').value=state.duration;renderBg();renderObjects();renderTexts();compactPreview();requestAnimationFrame(preview);"
init_new = "$('duration').value=state.duration;renderBg();renderObjects();renderTexts();compactPreview();requestAnimationFrame(preview);if($('saveProject'))$('saveProject').onclick=saveState;document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')saveState()});addEventListener('pagehide',()=>saveState());"
assert init_marker in s, 'init marker missing'
s = s.replace(init_marker, init_new, 1)

# Compact sooner, but only the preview changes size; panel/tabs remain a stable stack.
s = s.replace('scrollY>80', 'scrollY>48')

css = r'''
.mobile-tabs,.control-buffer{display:none}
@media(max-width:820px){
  .workspace{display:block!important;padding:0 12px 150px!important}
  .stage-wrap{position:sticky!important;top:58px!important;z-index:50!important;width:100%!important;min-height:0!important;height:auto!important;padding:9px 0 0!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:flex-start!important;overflow:visible!important;background:var(--bg)!important}
  .stage-shell{position:relative!important;top:auto!important;width:min(100%,320px)!important;margin:0 auto!important;flex:none!important;transform:none!important;transform-origin:top center!important;transition:width .32s cubic-bezier(.22,.8,.3,1),border-radius .32s ease,box-shadow .32s ease!important;box-shadow:0 10px 28px rgba(0,0,0,.12)!important}
  body.preview-compact .stage-shell{width:min(65%,208px)!important;transform:none!important;border-radius:17px!important;box-shadow:0 7px 20px rgba(0,0,0,.10)!important}
  .mobile-tabs{display:grid!important;width:100%!important;margin:10px 0 0!important;padding:8px 4px 10px!important;background:var(--bg)!important;border-bottom:1px solid var(--line)!important;box-shadow:0 7px 16px rgba(0,0,0,.045)!important}
  .control-buffer{display:flex!important;width:100%!important;height:64px!important;align-items:center!important;justify-content:center!important;color:#8b8b86!important;font-size:12px!important;letter-spacing:-.01em!important;background:var(--bg)!important;border-bottom:1px solid rgba(222,222,216,.7)!important}
  .panel{position:relative!important;z-index:10!important;margin:12px 0 28px!important;padding:16px 16px 28px!important;overflow:visible!important}
  .panel>.tabs{display:none!important}
  .section{position:relative!important;z-index:1!important}
  .objects-list{scrollbar-width:none}.objects-list::-webkit-scrollbar{display:none}
  .bottom-mobile{z-index:90!important}
}
'''
Path('mobile-layout-v1.2.0.css').write_text(css, encoding='utf-8')
s = s.replace('</style></head>', '</style><link rel="stylesheet" href="./mobile-layout-v1.2.0.css?v=1.2.0"></head>', 1)

# Static safety checks: no loader/iframe/document.write/service-worker interception in production.
assert 'document.write' not in s
assert '<iframe' not in s
assert 'serviceWorker.register' not in s
assert 'motionObjectsList' in s
assert 'Pinking Edge' in s
assert '>Wobble<' in s
assert '>Side Rock<' in s
assert "const VERSION='1.2.0'" in s
assert '<div class="version">v1.2.0</div>' in s

p.write_text(s, encoding='utf-8')
Path('index.html').write_text(s, encoding='utf-8')
Path('sw.js').write_text("self.addEventListener('install',e=>e.waitUntil(self.skipWaiting()));\nself.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));\n", encoding='utf-8')
print('ObjectReel v1.2.0 rebuilt successfully')
