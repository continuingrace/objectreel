from pathlib import Path

OLD='1.2.4'
NEW='1.2.5'

helper="""function drawExportPoster(ctx,W,H,bgv,bgi,imgs,gp){ctx.clearRect(0,0,W,H);ctx.fillStyle='#ddd';ctx.fillRect(0,0,W,H);if(bgv)drawFit(ctx,bgv,W,H,state.bgFit);else if(bgi)drawFit(ctx,bgi,W,H,state.bgFit);if(state.filmEnabled&&state.bgFilterOpacity>0){const [r,g,b]=rgb(state.bgFilterColor);ctx.fillStyle=`rgba(${r},${g},${b},${state.bgFilterOpacity/100})`;ctx.fillRect(0,0,W,H)}if(state.grainAmount>0){ctx.save();ctx.globalAlpha=state.grainAmount/100*.28;ctx.fillStyle=gp;ctx.fillRect(0,0,W,H);ctx.restore()}state.objects.forEach((o,i)=>{if(state.sequenceMode==='sequence'&&i!==0)return;const im=imgs[o.id],bw=W*.45*(o.scale||1),bh=bw*(im.naturalHeight/im.naturalWidth),x=(o.x??50)/100*W,y=(o.y??50)/100*H,r=(o.rotate||0)*Math.PI/180;ctx.save();ctx.translate(x,y);ctx.rotate(r);drawFramed(ctx,im,bw,bh,o.frame);ctx.restore()});state.texts.forEach(tl=>{if(!tl.text)return;ctx.save();ctx.fillStyle=tl.color||'#fff';ctx.textAlign='center';ctx.textBaseline='middle';const exportScale=W/TEXT_REFERENCE_WIDTH,exportTextSize=(tl.size||28)*exportScale;ctx.font=`700 ${exportTextSize}px ${tl.font||'Pretendard, sans-serif'}`;ctx.shadowColor='rgba(0,0,0,.22)';ctx.shadowBlur=14;const letterSpace=(tl.letterSpacing??0)*exportScale,lines=wrapCanvasText(ctx,tl.text||'',W*.84,letterSpace),lineStep=exportTextSize*(tl.lineHeight??1.18),centerY=(tl.y??76)/100*H,startY=centerY-((lines.length-1)*lineStep)/2;lines.forEach((line,j)=>drawLetterSpaced(ctx,line,(tl.x??50)/100*W,startY+j*lineStep,letterSpace));ctx.restore()})}\n"""

for filename in ('index.html','app-base.html'):
    p=Path(filename)
    s=p.read_text(encoding='utf-8')
    if f'v{OLD}' not in s or f"VERSION='{OLD}'" not in s:
        raise SystemExit(f'version marker missing in {filename}')
    if 'function drawExportPoster(' in s:
        raise SystemExit(f'poster helper already exists in {filename}')

    s=s.replace(f'v{OLD}',f'v{NEW}')
    s=s.replace(f"VERSION='{OLD}'",f"VERSION='{NEW}'")

    marker='async function exportVideo()'
    if marker not in s:
        raise SystemExit(f'exportVideo marker missing in {filename}')
    s=s.replace(marker,helper+marker,1)

    old="rec.start(100);const started=performance.now(),gp=ctx.createPattern(grainTile,'repeat');"
    new="const gp=ctx.createPattern(grainTile,'repeat');drawExportPoster(ctx,W,H,bgv,bgi,imgs,gp);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));rec.start(100);const started=performance.now();"
    if old not in s:
        raise SystemExit(f'recorder marker missing in {filename}')
    s=s.replace(old,new,1)

    old="function frame(now){const t=(now-started)/1000;"
    new="function frame(now){const elapsed=(now-started)/1000,t=Math.max(0,elapsed-.35);"
    if old not in s:
        raise SystemExit(f'frame time marker missing in {filename}')
    s=s.replace(old,new,1)

    old="const a=op(i,Math.min(t,dur-.001),dur);if(a<=0)return;"
    new="const a=elapsed<.35?(state.sequenceMode==='sequence'?(i===0?1:0):1):op(i,Math.min(t,dur-.001),dur);if(a<=0)return;"
    if old not in s:
        raise SystemExit(f'alpha marker missing in {filename}')
    s=s.replace(old,new,1)

    p.write_text(s,encoding='utf-8')
