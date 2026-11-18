import ctypes as C,os,json,subprocess
from pathlib import Path
os.environ.setdefault('EGL_PLATFORM','surfaceless')
os.environ['MESA_SHADER_CACHE_DISABLE']='true'
egl=C.CDLL('libEGL.so.1');P=C.c_void_p;I=C.c_int;U=C.c_uint
for name,result,args in [('eglGetDisplay',P,[P]),('eglInitialize',U,[P,C.POINTER(I),C.POINTER(I)]),('eglBindAPI',U,[U]),('eglChooseConfig',U,[P,C.POINTER(I),C.POINTER(P),I,C.POINTER(I)]),('eglCreatePbufferSurface',P,[P,P,C.POINTER(I)]),('eglCreateContext',P,[P,P,P,C.POINTER(I)]),('eglMakeCurrent',U,[P,P,P,P]),('eglGetProcAddress',P,[C.c_char_p]),('eglTerminate',U,[P])]:
 f=getattr(egl,name);f.restype=result;f.argtypes=args
D=egl.eglGetDisplay(None);major=I();minor=I();assert egl.eglInitialize(D,C.byref(major),C.byref(minor)),'EGL initialization unavailable'
assert egl.eglBindAPI(0x30A0)
attrs=(I*13)(0x3033,1,0x3040,4,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3038)
config=P();count=I();assert egl.eglChooseConfig(D,attrs,C.byref(config),1,C.byref(count)) and count.value
surface=egl.eglCreatePbufferSurface(D,config,(I*5)(0x3057,4,0x3056,4,0x3038));context=egl.eglCreateContext(D,config,None,(I*3)(0x3098,2,0x3038));assert surface and context
assert egl.eglMakeCurrent(D,surface,surface,context)
def gl(name,result,*args):
 ptr=egl.eglGetProcAddress(name.encode());assert ptr,name
 return C.CFUNCTYPE(result,*args)(ptr)
create=gl('glCreateShader',U,U);source=gl('glShaderSource',None,U,I,C.POINTER(C.c_char_p),C.POINTER(I));compile=gl('glCompileShader',None,U);check=gl('glGetShaderiv',None,U,U,C.POINTER(I));log=gl('glGetShaderInfoLog',None,U,I,C.POINTER(I),C.c_void_p)
data=json.loads(subprocess.check_output(['node','-e',"const fs=require('node:fs'),vm=require('node:vm');const s=fs.readFileSync('src/venom-native.ts','utf8');const f=s.match(/const FRAG = (`[\\s\\S]*?`)/)[1],v=s.match(/const VERT = (`[^`]+`)/)[1],c={MS:7,NP:12,MSPK:8,MDROP:6};process.stdout.write(JSON.stringify({vertex:vm.runInNewContext(v,c),fragment:vm.runInNewContext(f,c)}));"],cwd=Path(__file__).resolve().parents[1]));shaders=[]
for kind,key in [(0x8B31,'vertex'),(0x8B30,'fragment')]:
 shader=create(kind);buf=C.c_char_p(data[key].encode());source(shader,1,C.byref(buf),None);compile(shader);ok=I();check(shader,0x8B81,C.byref(ok))
 if not ok.value:
  length=I();check(shader,0x8B84,C.byref(length));message=C.create_string_buffer(max(length.value,1));log(shader,len(message),None,message);raise AssertionError(message.value.decode())
 shaders.append(shader)
program=gl('glCreateProgram',U)();attach=gl('glAttachShader',None,U,U)
for shader in shaders:attach(program,shader)
gl('glLinkProgram',None,U)(program);ok=I();gl('glGetProgramiv',None,U,U,C.POINTER(I))(program,0x8B82,C.byref(ok));assert ok.value,'Program did not link'
renderer=gl('glGetString',C.c_char_p,U)(0x1F01).decode();egl.eglTerminate(D)
print(json.dumps({'vertex_compile':'passed','fragment_compile':'passed','program_link':'passed','renderer':renderer,'visual_check':False}))
