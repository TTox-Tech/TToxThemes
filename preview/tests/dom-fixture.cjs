module.exports=function createDOM(url='https://test.local/?theme=v-r-v3n0m&view=desktop'){
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{parseHTML}=require('linkedom');
const dist=path.join(__dirname,'../dist'),html=fs.readFileSync(path.join(dist,'index.html'),'utf8');
const {window}=parseHTML(html),{document}=window;let now=1_000_000,seq=0,focus=null,rafSeq=0,fetches=0;const timers=new Map(),storage=new Map(),rafs=new Map();
Object.defineProperty(document,'activeElement',{get:()=>focus});Object.defineProperty(document,'hidden',{value:false,writable:true});
window.HTMLElement.prototype.focus=function(){focus=this;};window.HTMLElement.prototype.getClientRects=function(){return this.hidden||this.closest('[hidden]')?[]:[{}];};window.HTMLElement.prototype.getBoundingClientRect=function(){return{top:0,left:0,bottom:100,right:200,width:200,height:100};};
Object.defineProperty(window.HTMLSelectElement.prototype,'value',{get(){return this._value??this.querySelector('option[selected]')?.value??this.querySelector('option')?.value??'';},set(v){this._value=String(v);}});
window.HTMLElement.prototype.animate=function(){return{cancel(){},finished:Promise.resolve()};};
window.HTMLCanvasElement.prototype.getContext=()=>null;
class ClockDate extends Date{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}}
const timeout=(fn,ms)=>{const id=++seq;timers.set(id,{fn,at:now+ms});return id;};
const context={window,document,console,MutationObserver:class{observe(){}disconnect(){}},ResizeObserver:class{observe(){}disconnect(){}},Date:ClockDate,URL,URLSearchParams,CustomEvent:window.CustomEvent,Event:window.Event,DOMException,AbortController,Float32Array,performance:{now:()=>now},navigator:{clipboard:{writeText:async()=>{throw Error('denied');}}},location:new URL(url),history:{replaceState(){}},matchMedia:()=>({matches:true,addEventListener(){}}),localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},setTimeout:timeout,clearTimeout:id=>timers.delete(id),setInterval:(fn,ms)=>{const go=()=>{fn();timers.set(id,{fn:go,at:now+ms});};const id=timeout(go,ms);return id;},clearInterval:id=>timers.delete(id),requestAnimationFrame:fn=>{const id=++rafSeq;rafs.set(id,fn);return id;},cancelAnimationFrame:id=>rafs.delete(id),queueMicrotask,fetch(){fetches++;throw Error('Unexpected request');}};
window.matchMedia=context.matchMedia;window.requestAnimationFrame=context.requestAnimationFrame;window.cancelAnimationFrame=context.cancelAnimationFrame;window.localStorage=context.localStorage;window.devicePixelRatio=1;
vm.createContext(context);
// Exercise the actual complete HTML controller and its shipped modules, with a DOM emulator.
for(const m of html.matchAll(/<script(?:\s+src="([^"]+)")?[^>]*>([\s\S]*?)<\/script>/g)){if(m[1]){const file=m[1].split('?')[0];if(file.includes('lucide')){context.lucide=window.lucide={createIcons(){}};continue;}vm.runInContext(fs.readFileSync(path.join(dist,file),'utf8'),context,{filename:file});}else if(m[2].trim())vm.runInContext(m[2],context,{filename:'inline-controller.js'});}
const q=s=>document.querySelector(s),click=s=>{const n=q(s);assert(n,'Missing control '+s);assert(!n.disabled,'Disabled control '+s);return n.onclick?.({currentTarget:n,target:n,preventDefault(){}});},key=k=>'[data-key="'+k+'"]',change=(k,value)=>{const n=q(key(k));assert(n,k);n.value=value;n.onchange?.({target:n});},input=(k,value)=>{const n=q(key(k));assert(n,k);n.value=value;n.oninput?.({target:n});};
async function advance(ms){const end=now+ms;while(true){const next=[...timers].filter(([,t])=>t.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];if(!next)break;const[id,t]=next;now=t.at;timers.delete(id);t.fn();await Promise.resolve();}now=end;await Promise.resolve();}
function open(name){click('#room-shade-button');const b=[...document.querySelectorAll('.depth-shortcuts button')].find(b=>b.textContent===name);if(b)b.onclick();else{click('[data-tile="bluetooth"]');click(key('nav-'+name));}}

return{q,click,key,change,input,advance,open,document,window,context,timers,storage,assert,vm,getFetches:()=>fetches};
};
