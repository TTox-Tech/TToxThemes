/* Nearby surfaces keep independent state; only graphics resources are shared. */
window.createVenomDesktop = function(root) {
 const selectors='.room-inspector button,.room-wifi button,.room-widget,.room-terminal,.room-bar,.room-dock,.room-panel,.room-notification,.room-quick-grid>button,.room-dock>button,.room-workspaces>button,.room-play,#room-shade-button,#room-launch,#room-preview';
 const status=root.querySelector('#room-surface-status'),records=new Map();
 let settings=null,backend=null,key='',failed=false,point=null,scanFrame=0,disposed=false;
 function limit(){return settings.interaction.maxSurfaces?.[settings.effects]||2;}
 function visible(target){return target.isConnected&&target.getClientRects().length>0;}
 function distance(target){const rect=target.getBoundingClientRect(),radius=parseFloat(getComputedStyle(target).borderTopLeftRadius)||0;return window.venomSurfaceDistance(rect,point.clientX,point.clientY,radius);}
 function remove(record){
  if(records.get(record.target)!==record)return;
  records.delete(record.target);record.instance?.destroy();record.target.classList.remove('room-liquid-active');
  if(record.changedPosition)record.target.style.position='';record.stage.remove();
 }
 function clear(){for(const r of [...records.values()])remove(r);backend?.destroy();backend=null;}
 function fail(){if(failed)return;failed=true;clear();root.dataset.liquid='fallback';status.textContent='WebGL unavailable / static material';}
 function ensure(target,wanted=true){
  const existing=records.get(target);if(existing){existing.wanted=wanted;return existing;}
  if(!settings?.enabled||failed||!visible(target))return null;
  if(records.size>=limit()){
   const expendable=[...records.values()].find(r=>!r.wanted);
   if(!expendable)return null;remove(expendable);
  }
  const css=getComputedStyle(target),stage=document.createElement('span'),gl=document.createElement('canvas'),threads=document.createElement('canvas');
  stage.className='room-liquid-layer';stage.setAttribute('aria-hidden','true');stage.style.setProperty('--liquid-margin',settings.interaction.margin+'px');stage.append(gl,threads);
  const record={target,stage,gl,threads,wanted,instance:null,changedPosition:css.position==='static'};
  records.set(target,record);if(record.changedPosition)target.style.position='relative';target.append(stage);target.classList.add('room-liquid-active');
  if(!backend)backend=window.createVenomBackend(document.createElement('canvas'),true);
  try{
   record.instance=window.mountNativeVenom(stage,target,gl,threads,{
    backend,eventSurface:root,background:settings.color,gooColor:css.getPropertyValue('--r-liquid-base').trim()||settings.color,
    radius:parseFloat(css.borderTopLeftRadius)||(target.tagName==='BUTTON'?999:16),
    pixelRatio:settings.effects==='full'?1.25:1,strands:settings.interaction.strands,
    advanced:{shine:settings.shine,shadow:0,...settings.interaction},
    onStatus(value){if(value==='fallback')queueMicrotask(fail);else{root.dataset.liquid='live';status.textContent='Independent tendrils / shared graphics / native cursor';}},
    onSettled(){if(!record.wanted)remove(record);}
   });
   if(!record.instance){fail();return null;}
   if(point)record.instance.pointer(point);
   return record;
  }catch(error){fail();console.error('Desktop liquid renderer',error);return null;}
 }
 function scan(){
  scanFrame=0;if(!settings?.enabled||failed||disposed)return;
  if(!point){for(const r of records.values()){r.wanted=false;r.instance?.release();}return;}
  const modal=root.querySelector('.room-panel:not([hidden])');
  const all=[...root.querySelectorAll(selectors)].filter(t=>!t.disabled&&visible(t)&&(!modal||modal.contains(t)));
  const measured=all.map(target=>({target,distance:distance(target)}));
  const near=measured.filter(x=>x.distance<=settings.interaction.sense);
  // A container does not compete with its own nearby child controls.
  const eligible=measured.filter(x=>!near.some(y=>x.target!==y.target&&x.target.contains(y.target)));
  const distances=new Map(eligible.map(x=>[x.target,x.distance]));
  const wanted=new Set();
  // Existing holds are reserved first and use release, not sense, hysteresis.
  for(const r of records.values()){
   const state=r.instance?.getState();
   if((state==='hold'||state==='grow')&&distances.has(r.target)&&distances.get(r.target)<=settings.interaction.release)wanted.add(r.target);
  }
  for(const x of eligible.filter(x=>x.distance<=settings.interaction.sense).sort((a,b)=>a.distance-b.distance)){
   if(wanted.size>=limit())break;wanted.add(x.target);
  }
  for(const r of [...records.values()]){
   if(!visible(r.target)||!r.stage.isConnected){remove(r);continue;}
   r.wanted=wanted.has(r.target);if(!r.wanted)r.instance?.release();
  }
  for(const target of wanted){const r=ensure(target);r?.instance?.pointer(point);}
 }
 function schedule(){if(settings?.enabled&&!failed&&!scanFrame&&!disposed)scanFrame=requestAnimationFrame(scan);}
 function pointerMove(e){if(e.pointerType==='touch')return;point={clientX:e.clientX,clientY:e.clientY,pointerType:e.pointerType,isPrimary:e.isPrimary,target:e.target};schedule();}
 function pointerLeave(){point=null;schedule();}
 function focusIn(e){if(point||!settings?.enabled)return;const target=e.target.closest(selectors);if(target)ensure(target);}
 function overlayChange(){queueMicrotask(schedule);}
 root.addEventListener('pointermove',pointerMove,{capture:true,passive:true});root.addEventListener('pointerleave',pointerLeave,{passive:true});root.addEventListener('focusin',focusIn);root.addEventListener('ttox:overlay',overlayChange);
 const observer=new MutationObserver(()=>{
  let removed=false;for(const r of [...records.values()])if(!visible(r.target)||!r.stage.isConnected){remove(r);removed=true;}
  if(removed)schedule();
 });observer.observe(root,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
 return {
  configure(next){const nextKey=JSON.stringify([next.enabled,next.effects,next.color]);settings=next;
   if(nextKey!==key){clear();failed=false;key=nextKey;}
   if(!next.enabled){if(scanFrame)cancelAnimationFrame(scanFrame);scanFrame=0;root.dataset.liquid='off';status.textContent=next.material?(next.effects==='lite'?'Static surfaces / Lite':'Static surfaces / reduced motion'):'';return;}
   if(!records.size)status.textContent='Move between nearby controls / native cursor';schedule();
  },
  destroy(){disposed=true;if(scanFrame)cancelAnimationFrame(scanFrame);scanFrame=0;clear();observer.disconnect();root.removeEventListener('pointermove',pointerMove,true);root.removeEventListener('pointerleave',pointerLeave);root.removeEventListener('focusin',focusIn);root.removeEventListener('ttox:overlay',overlayChange);}
 };
};
