const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const events=new Map(),frames=new Map(),instances=new Map();let mutation,opened=false,mounts=0,backends=0,backendDestroys=0,seq=0;
class Element{
 constructor(name,left=0){this.name=name;this.left=left;this.style={position:'',setProperty(){}};this.dataset={};this.children=[];this.parent=null;const classes=new Set();this.classList={add:k=>classes.add(k),remove:k=>classes.delete(k),contains:k=>classes.has(k)};this.tagName='BUTTON';}
 get isConnected(){return this===root||Boolean(this.parent?.isConnected)}
 append(...items){for(const item of items){item.remove();this.children.push(item);item.parent=this;}}
 remove(){if(this.parent){this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null;}}
 setAttribute(){}getClientRects(){return [{}]}closest(){return this}
 contains(e){while(e){if(e===this)return true;e=e.parent;}return false}
 getBoundingClientRect(){return{left:this.left,top:100,width:100,height:40}}
}
const root=new Element('root'),status=new Element('status'),A=new Element('A',0),B=new Element('B',240),C=new Element('C',360),label=new Element('label');root.append(A,B,C,status);A.append(label);
root.addEventListener=(n,f)=>events.set(n,f);root.removeEventListener=n=>events.delete(n);root.querySelector=s=>s==='#room-surface-status'?status:null;root.querySelectorAll=()=>[A,B,C];
const ctx={window:{createVenomBackend(){backends++;return{destroy(){backendDestroys++}}},venomSurfaceDistance:(r,x,y)=>Math.hypot(Math.max(r.left-x,0,x-r.left-r.width),Math.max(r.top-y,0,y-r.top-r.height)),mountNativeVenom(stage,target,gl,threads,options){mounts++;options.onStatus('live');const instance={state:'seek',released:0,destroyed:0,pointer(){},getState(){return this.state},release(){this.state='snap';this.released++},destroy(){this.destroyed++},settle(){this.state='idle';options.onSettled()}};instances.set(target,instance);return instance;}},document:{createElement:t=>new Element(t)},getComputedStyle:t=>({position:t.style.position||'static',borderTopLeftRadius:'20px',getPropertyValue:()=> '#24282f'}),MutationObserver:class{constructor(f){mutation=f}observe(){}disconnect(){}},queueMicrotask:f=>f(),requestAnimationFrame:f=>{frames.set(++seq,f);return seq},cancelAnimationFrame:id=>frames.delete(id),console};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../dist/assets/venom-desktop.js'),'utf8'),ctx);
const controller=ctx.window.createVenomDesktop(root),settings={enabled:true,material:true,effects:'balanced',color:'#24282f',shine:'#edf0f7',interaction:{margin:230,strands:5,sense:175,reach:85,release:215,maxSurfaces:{balanced:2,full:4}}};
function flush(){for(const[id,f]of frames){frames.delete(id);f()}}
function move(x){events.get('pointermove')({pointerType:'mouse',clientX:x,clientY:120,target:root});flush()}
controller.configure(settings);flush();assert.equal(mounts,0,'No context before interaction');
move(30);const a=instances.get(A);assert(a);assert(!instances.has(B));a.state='hold';assert(A.children.includes(label));
move(120);const b=instances.get(B);assert(b);assert.equal(instances.get(A),a);assert.equal(a.state,'hold');assert.equal(a.released,0,'B entering range does not release A');assert.equal(backends,1,'Physics records share graphics');assert.equal(mounts,2);
b.state='hold';move(290);assert.equal(a.released,0,'Hold survives outside sense but inside release radius');assert.equal(b.released,0);assert(!instances.has(C),'New proximity never steals an occupied hold budget');
move(320);assert(a.released>0,'Only A crosses its release radius');assert.equal(b.released,0);assert.equal(instances.get(B),b,'B physics is not remounted');
controller.configure({...settings,enabled:false,effects:'lite'});assert.equal(root.dataset.liquid,'off');assert.equal(backendDestroys,1);assert.equal(b.destroyed,1);
controller.configure(settings);flush();const before=mounts;events.get('pointermove')({pointerType:'touch',clientX:20,clientY:120,target:A});flush();assert.equal(mounts,before,'Touch does not start hover scans');
controller.destroy();assert.equal(events.size,0);assert.equal(frames.size,0);
console.log('A hold + B seek coexist; holds reserve capacity through release hysteresis; one backend; independent release; Lite and disposal clean up.');
