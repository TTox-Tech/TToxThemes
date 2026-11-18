// Independent simulations share one compiled WebGL program and drawing buffer.
function createVenomBackend(canvas:HTMLCanvasElement,copyToTargets=false) {
 let gl:WebGLRenderingContext|null=null,program:WebGLProgram|null=null,quad:WebGLBuffer|null=null,aLoc=0,attempted=false,disposed=false,users=0
 const shaders:WebGLShader[]=[]
 function acquire(){
  if(disposed)return null
  if(!attempted){
   attempted=true;gl=canvas.getContext('webgl',{premultipliedAlpha:true,antialias:false,alpha:true}) as WebGLRenderingContext|null
   if(!gl)return null
   const compile=(type:number,text:string)=>{const s=gl!.createShader(type);if(!s)return null;shaders.push(s);gl!.shaderSource(s,text);gl!.compileShader(s);return s}
   const vs=compile(gl.VERTEX_SHADER,VERT),fs=compile(gl.FRAGMENT_SHADER,FRAG),p=gl.createProgram()
   if(p&&vs&&fs){gl.attachShader(p,vs);gl.attachShader(p,fs);gl.linkProgram(p);if(gl.getProgramParameter(p,gl.LINK_STATUS))program=p;else gl.deleteProgram(p)}
   if(program){quad=gl.createBuffer();aLoc=gl.getAttribLocation(program,'a')}
  }
  if(!gl||!program||!quad)return null
  users++;return{gl,program}
 }
 function prepare(width:number,height:number){
  if(!gl||!program||!quad)throw new Error('Liquid backend is unavailable')
  if(canvas.width!==width)canvas.width=width
  if(canvas.height!==height)canvas.height=height
  gl.viewport(0,0,width,height);gl.useProgram(program);gl.bindBuffer(gl.ARRAY_BUFFER,quad);gl.enableVertexAttribArray(aLoc);gl.vertexAttribPointer(aLoc,2,gl.FLOAT,false,0,0)
 }
 function present(target:HTMLCanvasElement){
  if(!copyToTargets||target===canvas)return
  const ctx=target.getContext('2d');if(!ctx)throw new Error('Liquid presentation canvas unavailable')
  ctx.clearRect(0,0,target.width,target.height);ctx.drawImage(canvas,0,0)
 }
 function destroy(){
  if(disposed)return;disposed=true
  if(gl){if(quad)gl.deleteBuffer(quad);if(program)gl.deleteProgram(program);for(const s of shaders)gl.deleteShader(s);gl.getExtension('WEBGL_lose_context')?.loseContext()}
  gl=null;program=null;quad=null;shaders.length=0
 }
 return{canvas,acquire,prepare,present,release(){users=Math.max(0,users-1)},destroy}
}
(window as any).createVenomBackend=createVenomBackend
