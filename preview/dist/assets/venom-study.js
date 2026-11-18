/* A single instance of the supplied liquid renderer, with native cursor only. */
window.createVenomStudy = function(root) {
  const stage=root.querySelector('#room-venom-stage'),button=root.querySelector('#room-venom-button');
  const gl=stage.querySelector('[data-layer="liquid"]'),overlay=stage.querySelector('[data-layer="threads"]');
  const status=root.querySelector('#room-liquid-status');
  let instance=null,key='',settings=null,blocked=false,failed=false;
  function destroy(){instance?.destroy();instance=null;key='';gl.hidden=overlay.hidden=true;button.style.transform='';}
  function sync(){
    if(!settings)return;
    const enabled=settings.visible&&settings.enabled&&!blocked;
    stage.inert=blocked;
    if(!enabled){destroy();status.textContent=settings.visible?(blocked?'Paused while control center is open':settings.reason):'';return;}
    const nextKey=JSON.stringify([settings.color,settings.effects]);
    if(instance&&key===nextKey)return;
    destroy();failed=false;gl.hidden=overlay.hidden=false;
    try {
      instance=window.mountNativeVenom(stage,button,gl,overlay,{
        background:'#020203',gooColor:settings.color,strands:7,reach:140,pixelRatio:settings.effects==='full'?1.5:1,
        advanced:{shine:'#EDF0F7',sense:290,release:215,shadow:0},
        onStatus(value){failed=value==='fallback';if(failed&&instance)queueMicrotask(()=>destroy());status.textContent=failed?'WebGL unavailable / static lacquer fallback':'Live liquid / native cursor';}
      });
      if(!instance||failed){destroy();status.textContent='WebGL unavailable / static lacquer fallback';}
      else key=nextKey;
    }catch(error){destroy();status.textContent='Liquid renderer unavailable / static lacquer fallback';console.error('Venom renderer failed',error);}
  }
  button.addEventListener('click',()=>root.dispatchEvent(new CustomEvent('ttox:open-controls',{detail:{trigger:button}})));
  root.addEventListener('ttox:overlay',e=>{blocked=e.detail.open;sync();});
  return {configure(next){settings=next;sync();},destroy};
};
