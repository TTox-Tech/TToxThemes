const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path'),{stripTypeScriptTypes}=require('node:module');
const source=fs.readFileSync(path.resolve(__dirname,'../src/surface-geometry.ts'),'utf8');
const ctx={};vm.createContext(ctx);vm.runInContext(stripTypeScriptTypes(source)+';globalThis.shape={at:roundedSurfaceAt,nearest:roundedSurfaceNearest}',ctx);
function shape(w,h,r){return{x:17,y:31,w,h,r,ls:w-2*r,vs:h-2*r,P:2*(w-2*r)+2*(h-2*r)+2*Math.PI*r};}
for(const p of [shape(220,72,36),shape(380,520,22),shape(300,240,18),shape(54,270,20)]){
 for(let i=0;i<512;i++){
  const s=i/512*p.P,point=ctx.shape.at(p,s),near=ctx.shape.nearest(p,point.x,point.y),roundtrip=ctx.shape.at(p,near.s);
  assert(Math.abs(near.dist)<1e-6);
  assert(Math.hypot(point.x-roundtrip.x,point.y-roundtrip.y)<1e-5,JSON.stringify({p,s,point,near,roundtrip}));
  assert(Math.abs(Math.hypot(point.nx,point.ny)-1)<1e-8);
 }
 assert(ctx.shape.nearest(p,p.x+p.w/2,p.y+p.h/2).dist<0);
 assert(ctx.shape.nearest(p,p.x-20,p.y-20).dist>0);
}
const p=shape(220,72,36);
for(let x=-30;x<300;x+=7)for(let y=-50;y<150;y+=7){const cy=p.y+p.r,cx=Math.max(p.x+p.r,Math.min(p.x+p.w-p.r,x)),old=Math.hypot(x-cx,y-cy)-p.r;assert(Math.abs(ctx.shape.nearest(p,x,y).dist-old)<1e-7);}
console.log('Rounded window, widget, dock and pill contours round-trip; capsule geometry remains equivalent.');
