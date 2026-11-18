"""Keep the supplied solver and shader; remove React, custom pointers and autoplay."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
raw=(root/'src/reference/VenomButton.originkit.tsx').read_text()
prefix=raw[raw.index('/* A cartoon glove pointer'):raw.index('type Props =')]
prefix=prefix[prefix.index('/* With the system pointer'):]
# Generalize only the stadium distance field to rounded rectangles; retain the optics and rope solver.
prefix=prefix.replace('uniform float uDpr;', 'uniform float uRadius;\nuniform float uDpr;')
a=prefix.index('  float rr = uPill.w * 0.5;');b=prefix.index('  float r;',a)
prefix=prefix[:a]+'''  float rr = clamp(uRadius, 1.0, min(uPill.z, uPill.w) * 0.5);
  vec2 c = uPill.xy + uPill.zw * 0.5;
  vec2 q = abs(p - c) - (uPill.zw * 0.5 - vec2(rr));
  vec2 body = vec2(length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - rr, rr);
'''+prefix[b:]
body=raw[raw.index('        // one 2D overlay'):raw.index('    }, [])')]
body=body.replace('            shaders.length = 0', '            shaders.length = 0\n            gl.getExtension("WEBGL_lose_context")?.loseContext()')
body=re.sub(r'        const onCanvas = .*\n','',body)
a=body.index('        const gloveP =');b=body.index('        // the press:')
body=body[:a]+body[b:]
a=body.index('        // ghost path for autoplay');b=body.index('        // ---- goo state ----')
body=body[:a]+body[b:]
a=body.index('        // read from the controls every frame');b=body.index('        const spawn =')
body=body[:a]+'''        const grips = NATIVE_GRIPS, bands = NATIVE_BANDS
        const gripAt = (g: [number, number]) => ({ x: hand.x + g[0], y: hand.y + g[1] })

'''+body[b:]
a=body.index('            drawn = L.cursor');b=body.index('            const hk =',a)
body=body[:a]+body[b:]
a=body.index('            const ghostOn =');b=body.index('            near = nearest',a)
body=body[:a]+'''            const present = ptr.inside
            hand = { x: ptr.x, y: ptr.touch ? ptr.y - num(A.fingerLift, 52, 0, 200) : ptr.y }
            anchor = { x: hand.x, y: hand.y }
'''+body[b:]
body=body.replace('ptr.touch || (touchOnly && ghost)', 'ptr.touch')
a=body.index('            // ---- the goo creeping over the glove ----');b=body.index('            // ---- the overlay:',a)
body=body[:a]+body[b:]
body=body.replace('const ovDraw = list.length > 0 || (drawn && present)','const ovDraw = list.length > 0')
a=body.index('            // ---- the pointer, always on top');b=body.index('            if (holding && list.length)',a)
body=body[:a]+body[b:]
# Stage-relative client coordinates support nested windows and controls.
a=body.index('            const bw = btn.offsetWidth');b=body.index('            pill.r =',a)
body=body[:a]+'''            const sr = stage.getBoundingClientRect(), br = btn.getBoundingClientRect()
            const sx = w / (sr.width || 1), sy = h / (sr.height || 1)
            pill.w = br.width * sx; pill.h = br.height * sy
            pill.x = (br.left - sr.left) * sx; pill.y = (br.top - sr.top) * sy
'''+body[b:]
a=body.index('            let x: number, y: number');b=body.index('            ptr.x = x',a)
body=body[:a]+'''            const rect = stage.getBoundingClientRect()
            const x = (e.clientX - rect.left) * w / (rect.width || 1)
            const y = (e.clientY - rect.top) * h / (rect.height || 1)
'''+body[b:]
body=body.replace('dpr = Math.min(2, window.devicePixelRatio || 1)','dpr = Math.min(num(live.current.pixelRatio, 1, 0.75, 2), window.devicePixelRatio || 1)')
body=body.replace('        const touchOnly = !!window.matchMedia?.("(hover: none) and (pointer: coarse)").matches\n','')
body=body.replace('        let touched = false\n','').replace('touched = true; ','')
# One context can move between any desktop surface while keeping its compiled shader.
body=body.replace('r: 0, ls: 0, P: 1','r: 0, ls: 0, vs: 0, P: 1')
body=body.replace('            pill.r = pill.h / 2','            pill.r = Math.max(1, Math.min(num(live.current.radius, pill.h / 2, 1, 999), pill.w / 2, pill.h / 2))')
body=body.replace('            pill.ls = Math.max(0, pill.w - pill.h)','            pill.ls = Math.max(0, pill.w - 2 * pill.r)\n            pill.vs = Math.max(0, pill.h - 2 * pill.r)')
body=body.replace('pill.P = 2 * pill.ls + 2 * Math.PI * pill.r || 1','pill.P = 2 * pill.ls + 2 * pill.vs + 2 * Math.PI * pill.r || 1')
a=body.index('        const at = (s: number) => {');b=body.index('        const loopDiff',a)
body=body[:a]+'''        const at = (s: number) => roundedSurfaceAt(pill, s)
        const nearest = (x: number, y: number) => roundedSurfaceNearest(pill, x, y)
'''+body[b:]
body=body.replace('uRes: uni("uRes"),', 'uRadius: uni("uRadius"), uRes: uni("uRes"),')
body=body.replace('gl.uniform1f(U.uDpr,', 'gl.uniform1f(U.uRadius, pill.r)\n                gl.uniform1f(U.uDpr,')
body=body.replace('stage.addEventListener("pointer', 'eventSurface.addEventListener("pointer').replace('stage.removeEventListener("pointer','eventSurface.removeEventListener("pointer')
body=body.replace('if (e.target === btn && !reduced) pressed = true', 'if (btn.tagName === "BUTTON" && btn.contains(e.target as Node) && !reduced) pressed = true')
body=body.replace('const transform = press === 1 ?', 'const transform = btn.tagName !== "BUTTON" || press === 1 ?')
# Wake only from input, geometry changes or an unsettled physics state.
body=body.replace('            place(e)\n','            place(e)\n            wake()\n')
body=body.replace('&& !reduced) pressed = true','&& !reduced) { pressed = true; wake() }')
body=body.replace('            pressed = false\n','            pressed = false\n            wake()\n')
body=body.replace('const onLeave = () => { if (!ptr.touch) ptr.inside = false }','const onLeave = () => { if (!ptr.touch) ptr.inside = false; wake() }')
body=body.replace('&& !reduced) pressed = true }','&& !reduced) { pressed = true; wake() } }')
body=body.replace('const onKeyUp = () => { pressed = false }','const onKeyUp = () => { pressed = false; wake() }')
body=body.replace('            measure()\n        }\n\n        // Touch','            measure()\n            wake()\n        }\n\n        // Touch')
body=body.replace('        let raf = 0\n','        let raf = 0\n        let running = true, visible = true, moving = false\n')
body=body.replace('            if (holding || seeking) {\n                moundS', '            if (Math.abs(mound) < 0.01 && Math.abs(moundV) < 0.03 && !holding && !seeking) { mound = 0; moundV = 0 }\n            if (holding || seeking) {\n                moundS')
body=body.replace('            lean +=', '            const oldLean = lean\n            lean +=')
body=body.replace('            lastGlKey = glKey','            lastGlKey = glKey\n            moving = !still || Math.abs(pressV) > 0.01 || Math.abs(press - pressTo) > 0.0001 || Math.abs(moundV) > 0.03 || Math.abs(mound) > 0.01 || Math.abs(lean - oldLean) > 0.00005\n            glc.dataset.state = mode')
a=body.index('        // One rAF loop.');b=body.index('        const ro = new ResizeObserver',a)
body=body[:a]+'''        function wake() {
            if (running && visible && !document.hidden && !raf) raf = requestAnimationFrame(frame)
        }
        function frame(now: number) {
            raf = 0
            if (!running || !visible || document.hidden) return
            draw(now)
            if (moving) wake()
        }
        const onVisibility = () => {
            if (document.hidden) { cancelAnimationFrame(raf); raf = 0; ptr.inside = false }
            else { prev = -1; wake() }
        }
        document.addEventListener('visibilitychange', onVisibility)
        const io = new IntersectionObserver(entries => {
            visible = entries.some(entry => entry.isIntersecting)
            if (!visible) { cancelAnimationFrame(raf); raf = 0; ptr.inside = false }
            else { prev = -1; wake() }
        })
        io.observe(stage)
'''+body[b:]
body=body.replace('        raf = requestAnimationFrame(frame)','        wake()')
body=body.replace('        return () => {\n            cancelAnimationFrame(raf)', '''        const destroy = () => {
            running = false
            cancelAnimationFrame(raf)
            io.disconnect()
            document.removeEventListener('visibilitychange', onVisibility)''')
# Shared graphics resources do not share physics state or target identity.
a=body.index('        // ---- WebGL setup ----');b=body.index('        const uni =',a)
body=body[:a]+'''        if (reduced) { setFallback(true); return null }
        const ownBackend = !settings.backend
        const backend = settings.backend || createVenomBackend(glc)
        const binding = backend.acquire()
        if (!binding) { if (ownBackend) backend.destroy(); setFallback(true); return null }
        const {gl, program} = binding
        const disposeGL = () => { backend.release(); if (ownBackend) backend.destroy() }
        const onContextLost = (e: Event) => { e.preventDefault(); setFallback(true) }
        backend.canvas.addEventListener('webglcontextlost', onContextLost)
'''+body[b:]
a=body.index('        quad = gl.createBuffer()');b=body.index('        const quadData',a)
body=body[:a]+body[b:]
body=body.replace('            gl.viewport(0, 0, glc.width, glc.height)\n','')
body=body.replace('                gl.clearColor(0, 0, 0, 0)','                backend.prepare(glc.width, glc.height)\n                gl.clearColor(0, 0, 0, 0)')
body=body.replace('                gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)','                gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)\n                backend.present(glc)')
body=body.replace('glc.removeEventListener("webglcontextlost", onContextLost)','backend.canvas.removeEventListener("webglcontextlost", onContextLost)')
body=body.replace('            if (moving) wake()','            if (moving) wake()\n            else live.current.onSettled?.()')
# Read-only state, pointer seeding and release let the manager preserve a hold while admitting a neighbour.
# Retargeting changes the body and radius without rebuilding the shared GL program.
body+='''
        live.current.onStatus?.('live')
        return {destroy, wake, getState: () => mode,
            pointer: (event: PointerEvent) => onMove(event),
            release: () => { ptr.inside = false; ptr.down = false; pressed = false; snap(true); wake() }
        }
'''
# Reduced motion never creates a GL context.
body=body.replace('        // The Framer canvas has no pointer, so the ghost glove shows what the button does.\n','')
body=body.replace('        // ---- WebGL setup ----','        if (reduced) { setFallback(true); return null }\n\n        // ---- WebGL setup ----',1)
body=body.replace('            return\n        }\n        const program = prog','            return null\n        }\n        const program = prog',1)
source='''// Adapted from the user-supplied Venom Button — Originkit.
// The original SDF shader and Verlet solver are retained; cursor drawing and autoplay are removed.
'''+prefix+'''
function mountNativeVenom(stage: HTMLElement, initialButton: HTMLElement, glc: HTMLCanvasElement, hc: HTMLCanvasElement, settings: Record<string, any> = {}) {
    let btn = initialButton\n    const eventSurface = settings.eventSurface || stage
    const live = {current:{background:'#020203',strands:7,reach:140,gooColor:'#020203',...settings,adv:{...ADVANCED_DEFAULTS,...settings.advanced}}}
    const setFallback = (flag: boolean) => { glc.hidden = flag; hc.hidden = flag; live.current.onStatus?.(flag ? 'fallback' : 'live') }
'''+body+'''\n}
(window as any).mountNativeVenom = mountNativeVenom;
(window as any).venomSurfaceDistance = (rect: DOMRect, x: number, y: number, radius: number) => {
    const r = Math.max(1, Math.min(radius || rect.height / 2, rect.width / 2, rect.height / 2))
    const dx = Math.abs(x - rect.left - rect.width / 2) - (rect.width / 2 - r)
    const dy = Math.abs(y - rect.top - rect.height / 2) - (rect.height / 2 - r)
    return Math.hypot(Math.max(dx, 0), Math.max(dy, 0)) + Math.min(Math.max(dx, dy), 0) - r
}
'''
assert not any(token in source for token in ['useEffect','GLOVE','Path2D','SHAPES','drawn =','ghostAt','cursor = "glove"'])
(root/'src/venom-native.ts').write_text(source)
print('Native renderer derived from supplied code:',len(source),'bytes')
