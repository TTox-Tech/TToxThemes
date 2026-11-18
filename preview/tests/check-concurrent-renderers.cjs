const assert=require('node:assert/strict'),setup=require('./check-native-renderer.cjs');
const t=setup();t.instance.destroy();let contexts=0,copiesA=0,copiesB=0;
const shared={width:0,height:0,getContext(type){assert.equal(type,'webgl');contexts++;return t.gl},addEventListener(){},removeEventListener(){}};
const backend=t.context.window.createVenomBackend(shared,true),startShaders=t.shaderSources.length;
function surface(left,width,height,onCopy){
 const stage={style:{},offsetWidth:width,offsetHeight:height,getBoundingClientRect:()=>({left:0,top:0,width,height}),addEventListener(){},removeEventListener(){}};
 const target={tagName:'BUTTON',style:{},offsetWidth:100,offsetHeight:40,contains:e=>e===target,addEventListener(){},removeEventListener(){},getBoundingClientRect(){const s=Number(this.style.transform?.match(/scale\(([^)]+)\)/)?.[1]||1);return{left:left+50-50*s,top:160-20*s,width:100*s,height:40*s}}};
 const local={dataset:{},getContext(type){assert.equal(type,'2d','Presentation layers never request WebGL');return{clearRect(){},drawImage(source){assert.equal(source.width,local.width);assert.equal(source.height,local.height);onCopy()}}},addEventListener(){},removeEventListener(){}};
 const threads={getContext:()=>t.hx};
 const engine=t.context.window.mountNativeVenom(stage,target,local,threads,{backend,radius:20,advanced:{sense:175,release:215},reach:85});
 assert(engine);return engine;
}
const A=surface(80,600,400,()=>copiesA++),B=surface(320,500,300,()=>copiesB++);
assert.equal(contexts,1);assert.equal(t.shaderSources.length-startShaders,2,'One vertex/fragment program for two independent simulations');
function pointer(x){const e={clientX:x,clientY:160,pointerType:'mouse'};A.pointer(e);B.pointer(e)}
pointer(120);t.step(120);assert.equal(A.getState(),'hold');assert.equal(B.getState(),'idle');
pointer(200);t.step(100);assert.equal(A.getState(),'hold');assert.equal(B.getState(),'seek');
pointer(260);t.step(120);assert.equal(A.getState(),'hold');assert.equal(B.getState(),'hold');assert(copiesA>0&&copiesB>0,'Both surfaces present visible frames');
pointer(410);t.step(4);assert.equal(A.getState(),'snap');assert.equal(B.getState(),'hold','B retains its independent hold');
t.step(600);assert.equal(A.getState(),'idle');assert.equal(B.getState(),'hold');
B.release();t.step(600);assert.equal(B.getState(),'idle');assert.equal(t.frames.size,0,'All loops stop after independent retraction');
A.destroy();B.destroy();backend.destroy();
console.log(JSON.stringify({shared_webgl_contexts:contexts,shared_shader_programs:1,concurrent:'A hold + B seek, then both hold',release:'A snaps while B holds',presentation:[copiesA,copiesB],idle_frames:0}));
