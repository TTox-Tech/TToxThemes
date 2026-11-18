const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const dist=path.resolve(__dirname,'../dist'),context={window:{}};vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(dist,'assets/themes.js'),'utf8'),context);
const themes=context.window.TToxThemes;
assert.deepEqual(Object.keys(themes),['sterling','vino','graphite','v-r-v3n0m']);
assert.equal(themes['v-r-v3n0m'].name,'V-R-V3N0M');
for(const t of Object.values(themes))for(const key of ['bg','fg','muted','accent','edge'])assert.match(t.colors[key],/^#[0-9a-fA-F]{6}$/);
const main=fs.readFileSync(path.join(dist,'index.html'),'utf8');
assert(main.includes("const requestedView=new URLSearchParams(location.search).get('view')"));
assert(main.includes('assets/venom-native.js'));assert(main.includes('assets/venom-desktop.js'));assert(main.includes("state.view='desktop'"));assert(!main.includes('surface-response.js'));
for(const m of main.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(m[1]);
for(const file of ['index.html','assets/symbiote.css','assets/venom-native.js','assets/venom-study.js'])assert(!/cursor\s*[:=]\s*['"]?\s*(none|url\s*\()/i.test(fs.readFileSync(path.join(dist,file),'utf8')),'No cursor replacement');
function lum(hex){const c=hex.slice(1).match(/../g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2];}
const colors=themes['v-r-v3n0m'].colors;for(const text of [colors.fg,colors.muted])for(const fill of [colors.bg,colors.inset,colors.surface,colors.raised,colors.selected]){const a=lum(text),b=lum(fill);assert((Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5,'Charcoal material text contrast');}
console.log('Theme registry, integration scripts, view routing and native-cursor checks passed.');
