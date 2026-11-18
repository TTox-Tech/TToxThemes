type Surface = {x:number,y:number,w:number,h:number,r:number,ls:number,vs:number,P:number}
function roundedSurfaceAt(p:Surface,s:number) {
 const {x,y,w,h,r,ls,vs,P}=p,q=Math.PI*r/2
 s=((s%P)+P)%P
 if(s<ls)return{x:x+r+s,y,nx:0,ny:-1};s-=ls
 if(s<q){const a=-Math.PI/2+s/r;return{x:x+w-r+Math.cos(a)*r,y:y+r+Math.sin(a)*r,nx:Math.cos(a),ny:Math.sin(a)}}s-=q
 if(s<vs)return{x:x+w,y:y+r+s,nx:1,ny:0};s-=vs
 if(s<q){const a=s/r;return{x:x+w-r+Math.cos(a)*r,y:y+h-r+Math.sin(a)*r,nx:Math.cos(a),ny:Math.sin(a)}}s-=q
 if(s<ls)return{x:x+w-r-s,y:y+h,nx:0,ny:1};s-=ls
 if(s<q){const a=Math.PI/2+s/r;return{x:x+r+Math.cos(a)*r,y:y+h-r+Math.sin(a)*r,nx:Math.cos(a),ny:Math.sin(a)}}s-=q
 if(s<vs)return{x,y:y+h-r-s,nx:-1,ny:0};s-=vs
 const a=Math.PI+s/r;return{x:x+r+Math.cos(a)*r,y:y+r+Math.sin(a)*r,nx:Math.cos(a),ny:Math.sin(a)}
}
function roundedSurfaceNearest(p:Surface,qx:number,qy:number) {
 const {x,y,w,h,r,ls,vs}=p,q=Math.PI*r/2,eps=1e-6
 const dx=Math.abs(qx-x-w/2)-(w/2-r),dy=Math.abs(qy-y-h/2)-(h/2-r)
 const dist=Math.hypot(Math.max(dx,0),Math.max(dy,0))+Math.min(Math.max(dx,dy),0)-r
 const cx=Math.max(x+r,Math.min(x+w-r,qx)),cy=Math.max(y+r,Math.min(y+h-r,qy))
 const vx=qx-cx,vy=qy-cy,len=Math.hypot(vx,vy)
 let px:number,py:number
 if(len>eps){px=cx+vx/len*r;py=cy+vy/len*r}
 else{
  const edges=[qy-y,x+w-qx,y+h-qy,qx-x],edge=edges.indexOf(Math.min(...edges))
  px=edge===1?x+w:edge===3?x:qx;py=edge===0?y:edge===2?y+h:qy
 }
 let s:number
 if(py<=y+eps)s=px-x-r
 else if(px>x+w-r&&py<y+r)s=ls+(Math.atan2(py-y-r,px-x-w+r)+Math.PI/2)*r
 else if(px>=x+w-eps)s=ls+q+py-y-r
 else if(px>x+w-r&&py>y+h-r)s=ls+q+vs+Math.atan2(py-y-h+r,px-x-w+r)*r
 else if(py>=y+h-eps)s=ls+2*q+vs+x+w-r-px
 else if(px<x+r&&py>y+h-r)s=2*ls+2*q+vs+(Math.atan2(py-y-h+r,px-x-r)-Math.PI/2)*r
 else if(px<=x+eps)s=2*ls+3*q+vs+y+h-r-py
 else{s=2*ls+3*q+2*vs+(Math.atan2(py-y-r,px-x-r)+2*Math.PI-Math.PI)*r}
 return{s:((s%p.P)+p.P)%p.P,dist}
}
