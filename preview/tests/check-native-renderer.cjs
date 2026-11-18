const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),code=fs.readFileSync(path.join(root,'dist/assets/venom-native.js'),'utf8');
const source=fs.readFileSync(path.join(root,'src/reference/VenomButton.originkit.tsx'),'utf8');
const shader=source.match(/const FRAG = (`[\s\S]*?`)/)[1];
const originalShader=vm.runInNewContext('(()=>{const MS=7,NP=12,MSPK=8,MDROP=6;return '+shader+'})()');
function setup({reduced=false,noGL=false}={}){
 let now=0,seq=0,glRequests=0,draws=0;const frames=new Map(),shaderSources=[],listeners=new Map(),docListeners=new Map();
 const target={style:{},tagName:'BUTTON',contains:e=>e===target,offsetWidth:220,offsetHeight:72,addEventListener:(n,f)=>listeners.set('btn:'+n,f),removeEventListener:n=>listeners.delete('btn:'+n),getBoundingClientRect(){const s=Number(this.style.transform?.match(/scale\(([^)]+)\)/)?.[1]||1);return {left:400-110*s,top:250-36*s,width:220*s,height:72*s}}};
 const stage={style:{},offsetWidth:800,offsetHeight:500,getBoundingClientRect:()=>({left:0,top:0,width:800,height:500}),addEventListener:(n,f)=>listeners.set(n,f),removeEventListener:n=>listeners.delete(n)};
 const gl=new Proxy({createShader:()=>({}),createProgram:()=>({}),createBuffer:()=>({}),getProgramParameter:()=>true,getUniformLocation:()=>({}),getAttribLocation:()=>0,shaderSource:(s,text)=>shaderSources.push(text),drawArrays:()=>draws++},{get(o,k){if(k in o)return o[k];if(String(k).toUpperCase()===k)return 1;return (...args)=>{for(const arg of args)if(typeof arg==='number')assert(Number.isFinite(arg));for(const arg of args)if(arg instanceof Float32Array)assert([...arg].every(Number.isFinite));};}});
 const hx=new Proxy({},{get:()=>()=>{}});
 const liquid={hidden:false,dataset:{},getContext:()=>{glRequests++;return noGL?null:gl},addEventListener:(n,f)=>listeners.set('gl:'+n,f),removeEventListener:n=>listeners.delete('gl:'+n)};
 const threads={hidden:false,getContext:()=>hx};
 const context={window:{devicePixelRatio:1,matchMedia:()=>({matches:reduced}),addEventListener:(n,f)=>listeners.set('win:'+n,f),removeEventListener:n=>listeners.delete('win:'+n)},document:{hidden:false,addEventListener:(n,f)=>docListeners.set(n,f),removeEventListener:n=>docListeners.delete(n)},performance:{now:()=>now},requestAnimationFrame:f=>{frames.set(++seq,f);return seq;},cancelAnimationFrame:id=>frames.delete(id),ResizeObserver:class{observe(){}unobserve(){}disconnect(){}},IntersectionObserver:class{observe(){}unobserve(){}disconnect(){}}};
 vm.createContext(context);vm.runInContext(code,context);
 let status='';const instance=context.window.mountNativeVenom(stage,target,liquid,threads,{onStatus:s=>status=s});
 function step(n){for(let i=0;i<n&&frames.size;i++){const [id,f]=frames.entries().next().value;frames.delete(id);now+=1000/60;f(now);}}
 function move(x,y){listeners.get('pointermove')({target:stage,pointerType:'mouse',clientX:x,clientY:y});}
 return {gl,hx,frames,shaderSources,liquid,threads,instance,listeners,docListeners,context,step,move,status:()=>status,glRequests:()=>glRequests,draws:()=>draws};
}
if(require.main===module){
const t=setup();assert(t.instance);assert.equal(t.status(),'live');const nativeShader=t.shaderSources.find(s=>s.includes('uniform float uRadius'));assert(nativeShader);assert.equal(nativeShader.slice(nativeShader.indexOf('float env(')),originalShader.slice(originalShader.indexOf('float env(')),'Supplied material optics and fragment lighting are retained');
t.step(1);assert.equal(t.liquid.dataset.state,'idle');assert.equal(t.frames.size,0,'Idle renderer sleeps');t.move(5,5);t.step(600);assert.equal(t.frames.size,0,'A stationary pointer outside sensing range also sleeps');
t.move(400,486);t.step(30);assert.equal(t.liquid.dataset.state,'seek');
t.move(400,365);t.step(5);assert.equal(t.liquid.dataset.state,'grow');t.step(40);assert.equal(t.liquid.dataset.state,'hold');
t.listeners.get('pointerleave')();t.step(1);assert.equal(t.liquid.dataset.state,'snap');t.step(600);assert.equal(t.liquid.dataset.state,'idle');assert.equal(t.frames.size,0,'Recoil settles and the loop stops');
t.move(400,365);assert.equal(t.frames.size,1);t.context.document.hidden=true;t.docListeners.get('visibilitychange')();assert.equal(t.frames.size,0,'Hidden page suspends rendering');
t.instance.destroy();assert.equal(t.frames.size,0);assert.equal(t.listeners.size,0,'All input handlers cleaned up');assert.equal(t.docListeners.size,0);
const no=setup({noGL:true});assert.equal(no.instance,null);assert.equal(no.status(),'fallback');assert(no.liquid.hidden&&no.threads.hidden);
const reduced=setup({reduced:true});assert.equal(reduced.instance,null);assert.equal(reduced.glRequests(),0,'Reduced motion skips WebGL initialization');
assert(!code.includes('Path2D'));assert(!/cursor\s*=\s*['"]none/.test(code));assert(!code.includes('GLOVE'));assert(!code.includes('ghostAt'));
console.log(JSON.stringify({shader:'reference optics, generalized rounded surface',states:['idle','seek','grow','hold','snap','idle'],idle_loop:'stops',hidden_page:'suspends',cleanup:'passed',fallback:'passed',reduced_motion:'no GL context',custom_pointer:'removed',draws:t.draws()}));

}
module.exports=setup;
