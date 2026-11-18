const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const dist=path.resolve(__dirname,'../dist'),html=fs.readFileSync(path.resolve(__dirname,'../src/network-panel.html'),'utf8');
let now=0,seq=0,storageWrites=0,fetches=0;const timers=new Map(),nodes=new Map(),docEvents=new Map(),snapshots=[];
const doc={hidden:false,activeElement:null,addEventListener:(n,f)=>docEvents.set(n,f),createElement:t=>new Element(t)};
class Element{
 constructor(tag,id,attrs=''){this.tagName=tag.toUpperCase();this.id=id;this.children=[];this.attrs={};this.value=attrs.match(/value="([^"]*)"/)?.[1]||'';this.type=attrs.match(/type="([^"]*)"/)?.[1]||'';this.checked=/\bchecked\b/.test(attrs);this.hidden=/\bhidden\b/.test(attrs);this.disabled=false;this._text='';}
 set textContent(v){this._text=String(v);this.children=[]}get textContent(){return this._text+this.children.map(x=>x.textContent).join('')}
 append(...nodes){this.children.push(...nodes)}replaceChildren(...nodes){this.children=[...nodes];this._text=''}setAttribute(k,v){this.attrs[k]=String(v)}removeAttribute(k){delete this.attrs[k]}focus(){doc.activeElement=this}
 querySelectorAll(selector){const items=this.formChildren||[];return selector==='[aria-invalid]'?items.filter(e=>'aria-invalid'in e.attrs):items;}
}
for(const m of html.matchAll(/<(\w+)([^>]*\bid="([^"]+)"[^>]*)>/g))nodes.set(m[3],new Element(m[1],m[3],m[2]));
const form=nodes.get('net-settings-form'),body=html.match(/<form id="net-settings-form">([\s\S]*?)<\/form>/)[1];form.formChildren=[...body.matchAll(/\bid="([^"]+)"/g)].map(m=>nodes.get(m[1]));
const root={querySelector:s=>s==='.room-wifi'?new Element('section','panel'):nodes.get(s.slice(1))};
function timeout(f,ms,repeat=false){const id=++seq;timers.set(id,{f,at:now+ms,ms,repeat});return id}
async function advance(ms){const end=now+ms;while(true){const entry=[...timers].filter(([,v])=>v.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];if(!entry)break;const[id,t]=entry;now=t.at;if(t.repeat)t.at+=t.ms;else timers.delete(id);t.f();}now=end;await Promise.resolve();await Promise.resolve();await Promise.resolve();}
const context={window:{},document:doc,DOMException,AbortController,Date:{now:()=>now},console,setTimeout:(f,ms)=>timeout(f,ms),clearTimeout:id=>timers.delete(id),setInterval:(f,ms)=>timeout(f,ms,true),clearInterval:id=>timers.delete(id),fetch(){fetches++;throw Error('Unexpected request')},localStorage:{setItem(){storageWrites++;throw Error('Unexpected storage')}}};
vm.createContext(context);for(const file of ['network-model.js','network-panel.js'])vm.runInContext(fs.readFileSync(path.join(dist,'assets',file),'utf8'),context);
const api=context.window.createTToxNetworkPanel(root,{show(){},back(){},onSnapshot:s=>snapshots.push(s)}),q=id=>nodes.get(id),event={preventDefault(){}};
(async()=>{
 api.open();assert.equal(timers.size,1,'Only open-panel polling starts');assert.equal(q('net-ssid').textContent,'Studio Wi-Fi');
 q('net-networks').children[1].onclick();q('net-connect').onclick();assert.equal(q('net-password-form').hidden,false);
 const secret='private-test-secret-42';q('net-password').value=secret;q('net-password-form').onsubmit(event);assert.equal(q('net-password').value,'','Secret input clears immediately');api.onClose();await advance(1000);assert.equal(timers.size,0);assert.equal(q('net-password').type,'password');
 api.open();q('net-networks').children[1].onclick();q('net-connect').onclick();q('net-password').value=secret;q('net-password-form').onsubmit(event);await advance(800);assert.equal(snapshots.at(-1).active,'lab');assert(!JSON.stringify(snapshots).includes(secret));
 q('net-settings-tab').onclick();q('net-dns-auto').checked=false;q('net-dns-auto').onchange();q('net-dns').value='invalid';q('net-settings-form').onsubmit(event);assert.equal(q('net-error').hidden,false);assert.equal(q('net-dns').attrs['aria-invalid'],'true');
 q('net-dns').value='1.1.1.1';q('net-settings-form').onsubmit(event);assert.equal(q('net-review').hidden,false);assert.equal(q('net-settings-form').hidden,true);q('net-apply').onclick();assert.equal(q('net-checkpoint').hidden,false);assert.equal(snapshots.at(-1).profile.dnsAuto,false);
 await advance(15000);assert.equal(snapshots.at(-1).profile.dnsAuto,true,'Unconfirmed settings revert automatically');assert(q('net-message').textContent.includes('timed out'));
 q('net-dns-auto').checked=false;q('net-dns-auto').onchange();q('net-dns').value='1.1.1.1';q('net-settings-form').onsubmit(event);q('net-apply').onclick();q('net-keep').onclick();api.onClose();assert.equal(snapshots.at(-1).profile.dns[0],'1.1.1.1');assert.equal(timers.size,0);
 api.open();q('net-dns').value='9.9.9.9';q('net-settings-form').onsubmit(event);q('net-apply').onclick();api.onClose();assert.equal(snapshots.at(-1).profile.dns[0],'1.1.1.1','Closing reverts an unconfirmed change');assert.equal(timers.size,0);
 api.open();q('net-password').value=secret;q('net-show-password').onclick();doc.hidden=true;docEvents.get('visibilitychange')();assert.equal(q('net-password').value,'');assert.equal(q('net-password').type,'password');assert.equal(timers.size,0);api.onClose();
 assert.equal(storageWrites,0);assert.equal(fetches,0);
 console.log('Wi-Fi UI: connect/cancel, password wiping, IP/DNS validation, review, timed rollback, keep/close rollback, no closed polling or secret storage/requests.');
})().catch(e=>{console.error(e);process.exitCode=1});
