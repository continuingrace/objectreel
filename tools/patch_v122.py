from pathlib import Path
import re

OLD='1.2.1'
NEW='1.2.2'

for filename in ('index.html','app-base.html'):
    p=Path(filename)
    s=p.read_text(encoding='utf-8')
    assert f'v{OLD}' in s and f"VERSION='{OLD}'" in s, f'version marker missing in {filename}'
    s=s.replace(f'v{OLD}',f'v{NEW}')
    s=s.replace(f"VERSION='{OLD}'",f"VERSION='{NEW}'")

    # Text UI: add letter spacing and line height controls only.
    old='<div class="group"><span class="label">크기</span><input id="textSize" class="range" type="range" min="12" max="96" value="28"></div><div class="group"><span class="label">X 위치</span>'
    new='<div class="group"><span class="label">크기</span><input id="textSize" class="range" type="range" min="12" max="96" value="28"></div><div class="group"><span class="label">자간</span><div class="control-row"><input id="textLetterSpacing" class="range" type="range" min="-3" max="12" step="0.2" value="0"><span id="textLetterSpacingVal" class="value">0px</span></div></div><div class="group"><span class="label">행간</span><div class="control-row"><input id="textLineHeight" class="range" type="range" min="0.8" max="2.2" step="0.05" value="1.18"><span id="textLineHeightVal" class="value">1.18</span></div></div><div class="group"><span class="label">X 위치</span>'
    assert old in s, f'text size marker missing in {filename}'
    s=s.replace(old,new,1)

    # Existing saved text layers receive defaults without altering other saved properties.
    old="if(!Array.isArray(state.texts))state.texts=[];"
    new="if(!Array.isArray(state.texts))state.texts=[];state.texts=state.texts.map(t=>({...t,letterSpacing:t.letterSpacing??0,lineHeight:t.lineHeight??1.18}));"
    assert old in s, f'text restore marker missing in {filename}'
    s=s.replace(old,new,1)

    # Preview text rendering.
    old="el.style.fontFamily=t.font||'Pretendard, sans-serif';c.appendChild(el);"
    new="el.style.fontFamily=t.font||'Pretendard, sans-serif';el.style.letterSpacing=(t.letterSpacing??0)+'px';el.style.lineHeight=t.lineHeight??1.18;c.appendChild(el);"
    assert old in s, f'text render marker missing in {filename}'
    s=s.replace(old,new,1)

    old="['textInput','fontFamily','textColor','textSize','textX','textY','removeText']"
    new="['textInput','fontFamily','textColor','textSize','textLetterSpacing','textLineHeight','textX','textY','removeText']"
    assert old in s, f'text disable marker missing in {filename}'
    s=s.replace(old,new,1)

    old="$('textSize').value=t.size||28;$('textX').value=t.x??50;"
    new="$('textSize').value=t.size||28;$('textLetterSpacing').value=t.letterSpacing??0;$('textLineHeight').value=t.lineHeight??1.18;$('textLetterSpacingVal').textContent=(t.letterSpacing??0).toFixed(1).replace('.0','')+'px';$('textLineHeightVal').textContent=(t.lineHeight??1.18).toFixed(2);$('textX').value=t.x??50;"
    assert old in s, f'text sync marker missing in {filename}'
    s=s.replace(old,new,1)

    old="const t={id:uid(),text:'텍스트',x:50,y:76,size:28,color:'#ffffff',font:'Pretendard, sans-serif'};"
    new="const t={id:uid(),text:'텍스트',x:50,y:76,size:28,color:'#ffffff',font:'Pretendard, sans-serif',letterSpacing:0,lineHeight:1.18};"
    assert old in s, f'addText marker missing in {filename}'
    s=s.replace(old,new,1)

    old="$('textSize').oninput=e=>updateText('size',+e.target.value);$('textX').oninput"
    new="$('textSize').oninput=e=>updateText('size',+e.target.value);$('textLetterSpacing').oninput=e=>updateText('letterSpacing',+e.target.value);$('textLineHeight').oninput=e=>updateText('lineHeight',+e.target.value);$('textX').oninput"
    assert old in s, f'text handlers marker missing in {filename}'
    s=s.replace(old,new,1)

    # Pinking Edge: explicit zigzag around TOP, RIGHT, BOTTOM, LEFT.
    start=s.index('function pinkingClip()')
    end=s.index('function frameStyle',start)
    pinking_clip=r'''function pinkingClip(){const pts=[],step=4,amp=2.8;let i=0;for(let x=0;x<=100;x+=step,i++)pts.push(`${Math.min(x,100)}% ${i%2?amp:0}%`);i=1;for(let y=step;y<=100;y+=step,i++)pts.push(`${100-(i%2?amp:0)}% ${Math.min(y,100)}%`);i=1;for(let x=100-step;x>=0;x-=step,i++)pts.push(`${Math.max(x,0)}% ${100-(i%2?amp:0)}%`);i=1;for(let y=100-step;y>0;y-=step,i++)pts.push(`${i%2?amp:0}% ${Math.max(y,0)}%`);return `polygon(${pts.join(',')})`}
'''
    s=s[:start]+pinking_clip+s[end:]

    start=s.index('function pinkingPath(ctx,bw,bh)')
    end=s.index('function drawFramed',start)
    pinking_path=r'''function pinkingPath(ctx,bw,bh){const n=24,amp=Math.min(bw,bh)*.022,x0=-bw/2,y0=-bh/2,x1=bw/2,y1=bh/2;ctx.beginPath();ctx.moveTo(x0,y0);for(let i=1;i<=n;i++)ctx.lineTo(x0+bw*i/n,y0+(i%2?amp:0));for(let i=1;i<=n;i++)ctx.lineTo(x1-(i%2?amp:0),y0+bh*i/n);for(let i=1;i<=n;i++)ctx.lineTo(x1-bw*i/n,y1-(i%2?amp:0));for(let i=1;i<=n;i++)ctx.lineTo(x0+(i%2?amp:0),y1-bh*i/n);ctx.closePath()}
'''
    s=s[:start]+pinking_path+s[end:]

    # Export text renderer: line-height and letter-spacing match preview intent.
    insert='''function drawLetterSpaced(ctx,text,x,y,spacing){if(!spacing){ctx.fillText(text,x,y);return}const chars=[...text],widths=chars.map(ch=>ctx.measureText(ch).width),total=widths.reduce((a,b)=>a+b,0)+spacing*Math.max(0,chars.length-1);let cx=x-total/2;const align=ctx.textAlign;ctx.textAlign='left';chars.forEach((ch,i)=>{ctx.fillText(ch,cx,y);cx+=widths[i]+spacing});ctx.textAlign=align}\n'''
    marker='async function exportVideo()'
    assert marker in s, f'export marker missing in {filename}'
    s=s.replace(marker,insert+marker,1)

    old="ctx.font=`700 ${(tl.size||28)*2.8}px ${tl.font||'Pretendard, sans-serif'}`;ctx.shadowColor='rgba(0,0,0,.22)';ctx.shadowBlur=14;const lines=(tl.text||'').split('\\n');lines.forEach((line,j)=>ctx.fillText(line,(tl.x??50)/100*W,(tl.y??76)/100*H+j*(tl.size||28)*3.1));"
    new="const exportTextSize=(tl.size||28)*2.8;ctx.font=`700 ${exportTextSize}px ${tl.font||'Pretendard, sans-serif'}`;ctx.shadowColor='rgba(0,0,0,.22)';ctx.shadowBlur=14;const lines=(tl.text||'').split('\\n'),lineStep=exportTextSize*(tl.lineHeight??1.18),letterSpace=(tl.letterSpacing??0)*2.8;lines.forEach((line,j)=>drawLetterSpaced(ctx,line,(tl.x??50)/100*W,(tl.y??76)/100*H+j*lineStep,letterSpace));"
    assert old in s, f'export text marker missing in {filename}'
    s=s.replace(old,new,1)

    # Background video: show immediately from an object URL, then persist its data URL.
    old='let bgEl=null,drag=null,saveTimer=null,db=null,removerModule=null,previewStart=performance.now();'
    new='let bgEl=null,bgPreviewURL=null,drag=null,saveTimer=null,db=null,removerModule=null,previewStart=performance.now();'
    assert old in s, f'bg variable marker missing in {filename}'
    s=s.replace(old,new,1)

    start=s.index('function renderBg()')
    end=s.index('function renderFilm()',start)
    render_bg=r'''function renderBg(srcOverride=null){if(bgEl){try{bgEl.pause?.()}catch{}bgEl.remove()}bgEl=null;const src=srcOverride||state.bg;$('emptyBg').style.display=src?'none':'grid';if(src){bgEl=document.createElement(state.bgKind==='video'?'video':'img');bgEl.src=src;bgEl.className='bg-media';bgEl.style.objectFit=state.bgFit;if(state.bgKind==='video'){bgEl.muted=true;bgEl.defaultMuted=true;bgEl.loop=true;bgEl.playsInline=true;bgEl.autoplay=true;bgEl.preload='auto';bgEl.setAttribute('playsinline','');bgEl.setAttribute('webkit-playsinline','');const startVideo=()=>{bgEl?.play().then(()=>{if($('bgStatus'))$('bgStatus').textContent='영상 준비됨'}).catch(()=>{if($('bgStatus'))$('bgStatus').textContent='미리보기를 한 번 누르면 재생됩니다';if(bgEl)bgEl.onclick=()=>bgEl.play().catch(()=>{})})};bgEl.addEventListener('loadeddata',startVideo,{once:true});bgEl.addEventListener('canplay',startVideo,{once:true});stage.prepend(bgEl);try{bgEl.load();startVideo()}catch{}}else stage.prepend(bgEl)}renderFilm()}
'''
    s=s[:start]+render_bg+s[end:]

    old="$('bgInput').onchange=async e=>{const f=e.target.files?.[0];if(!f)return;state.bg=await dataURL(f);state.bgKind=f.type.startsWith('video/')?'video':'image';renderBg();scheduleSave();e.target.value=''};$('clearBg').onclick=()=>{state.bg=null;state.bgKind=null;renderBg();scheduleSave()};"
    new="$('bgInput').onchange=async e=>{const f=e.target.files?.[0];if(!f)return;const isVideo=f.type.startsWith('video/');state.bg=null;state.bgKind=isVideo?'video':'image';if(bgPreviewURL){URL.revokeObjectURL(bgPreviewURL);bgPreviewURL=null}if(isVideo){bgPreviewURL=URL.createObjectURL(f);$('bgStatus').textContent='영상 불러오는 중…';renderBg(bgPreviewURL);try{state.bg=await dataURL(f);$('bgStatus').textContent='영상 준비됨';scheduleSave()}catch{$('bgStatus').textContent='영상 저장 준비에 실패했습니다'}}else{state.bg=await dataURL(f);renderBg();$('bgStatus').textContent='';scheduleSave()}e.target.value=''};$('clearBg').onclick=()=>{if(bgPreviewURL){URL.revokeObjectURL(bgPreviewURL);bgPreviewURL=null}state.bg=null;state.bgKind=null;$('bgStatus').textContent='';renderBg();scheduleSave()};"
    assert old in s, f'bg input marker missing in {filename}'
    s=s.replace(old,new,1)

    p.write_text(s,encoding='utf-8')
