/* Demo adapter: deterministic fixtures, no system calls, network requests or secret persistence. */
window.TToxNetwork = (()=>{
 const clone=value=>JSON.parse(JSON.stringify(value));
 function ipv4(value){return /^\d{1,3}(\.\d{1,3}){3}$/.test(value)&&value.split('.').every(p=>Number(p)<=255&&String(Number(p))===p);}
 function validateSettings(draft){
  const errors={};const cfg={ipv4:draft.ipv4,address:String(draft.address||'').trim(),gateway:String(draft.gateway||'').trim(),dnsAuto:Boolean(draft.dnsAuto),dns:String(draft.dns||'').split(/[\s,]+/).filter(Boolean),ipv6:draft.ipv6,mtu:Number(draft.mtu),autoconnect:Boolean(draft.autoconnect),metered:draft.metered,mac:draft.mac};
  if(!['auto','manual'].includes(cfg.ipv4))errors.ipv4='Choose DHCP or Manual.';
  if(cfg.ipv4==='manual'){
   const [address,prefix,...extra]=cfg.address.split('/');
   if(!ipv4(address)||!/^\d{1,2}$/.test(prefix||'')||Number(prefix)>32||extra.length)errors.address='Use an IPv4 address with prefix, such as 192.0.2.24/24.';
   if(!ipv4(cfg.gateway))errors.gateway='Enter a valid IPv4 gateway.';
  }
  if(!cfg.dnsAuto&&(!cfg.dns.length||cfg.dns.length>3||cfg.dns.some(s=>!ipv4(s))))errors.dns='Enter one to three IPv4 DNS server addresses.';
  if(!['auto','disabled'].includes(cfg.ipv6))errors.ipv6='Choose Automatic or Disabled.';
  const min=cfg.ipv6==='disabled'?576:1280;
  if(!Number.isInteger(cfg.mtu)||!(cfg.mtu===0||(cfg.mtu>=min&&cfg.mtu<=9000)))errors.mtu='Use 0 for automatic, or '+min+'–9000 bytes.';
  if(!['auto','yes','no'].includes(cfg.metered))errors.metered='Choose a metering policy.';
  if(!['stable','random','permanent'].includes(cfg.mac))errors.mac='Choose a MAC privacy mode.';
  return{valid:Object.keys(errors).length===0,errors,value:cfg};
 }
 function validatePassphrase(value){return (typeof value==='string'&&((value.length>=8&&value.length<=63)||/^[a-fA-F0-9]{64}$/.test(value)))?'':'Use 8–63 characters, or a 64-digit hexadecimal WPA key.';}
 function changes(before,after){const out=[];const labels={ipv4:'IPv4 method',address:'IPv4 address',gateway:'Gateway',dnsAuto:'Automatic DNS',dns:'DNS servers',ipv6:'IPv6 method',mtu:'MTU',autoconnect:'Auto-connect',metered:'Metered connection',mac:'MAC privacy'};for(const key of Object.keys(labels)){if(after.ipv4==='auto'&&['address','gateway'].includes(key))continue;if(after.dnsAuto&&key==='dns')continue;if(JSON.stringify(before[key])!==JSON.stringify(after[key]))out.push({label:labels[key],before:before[key],after:after[key]});}return out;}
 const defaults={ipv4:'auto',address:'192.0.2.24/24',gateway:'192.0.2.1',dnsAuto:true,dns:['192.0.2.1'],ipv6:'auto',mtu:0,autoconnect:true,metered:'auto',mac:'stable'};
 const fixture=[
  {id:'studio',ssid:'Studio Wi-Fi',security:'WPA2 Personal',band:'5 GHz',channel:44,frequency:5220,signal:86,rssi:-49,rate:866,bssid:'02:00:00:00:00:41',saved:true},
  {id:'lab',ssid:'Lab_5G',security:'WPA2 Personal',band:'5 GHz',channel:149,frequency:5745,signal:64,rssi:-65,rate:433,bssid:'02:00:00:00:00:52',saved:false},
  {id:'guest',ssid:'Guest network',security:'Open',band:'2.4 GHz',channel:6,frequency:2437,signal:42,rssi:-74,rate:144,bssid:'02:00:00:00:00:63',saved:false},
  {id:'archive',ssid:'Workshop archive',security:'WPA2 Personal',band:'2.4 GHz',channel:11,frequency:2462,signal:12,rssi:-91,rate:54,bssid:'02:00:00:00:00:74',saved:false,unavailable:true}
 ];
 const trace={down:[142,188,171,240,212,184,155,320,278,223,190,201,261,179,142],up:[18,24,21,38,28,22,17,45,31,25,20,29,34,21,18]};
 function createDemo({radio=true,wait=(ms,signal)=>new Promise((resolve,reject)=>{
  let id;const abort=()=>{clearTimeout(id);reject(new DOMException('Cancelled','AbortError'));};if(signal?.aborted){abort();return;}id=setTimeout(()=>{signal?.removeEventListener('abort',abort);resolve();},ms);signal?.addEventListener('abort',abort,{once:true});
 })}={}){
  let enabled=radio,active=radio?'studio':null,sample=0,totalDown=12.4,totalUp=1.8,revision=0;
  const networks=clone(fixture),profiles=new Map(networks.filter(n=>n.saved).map(n=>[n.id,clone(defaults)]));
  function snapshot(){const accessPoint=networks.find(n=>n.id===active),profile=active?profiles.get(active):null;const link=accessPoint?{address:profile.ipv4==='manual'?profile.address:defaults.address,gateway:profile.ipv4==='manual'?profile.gateway:defaults.gateway,dns:profile.dnsAuto?defaults.dns:profile.dns,ipv6:profile.ipv6==='auto'?'2001:db8:42::24/64':''}:null;return clone({link,mode:'demo',radio:enabled,active,networks,profile:active?profiles.get(active):null,revision,interface:'wlan0',driver:'iwlwifi (sample)',mac:'02:00:00:00:01:24',ipv6:'2001:db8:42::24/64',metrics:{down:accessPoint?trace.down[sample%trace.down.length]:0,up:accessPoint?trace.up[sample%trace.up.length]:0,latency:accessPoint?12+(sample%4):null,totalDown,totalUp,historyDown:Array.from({length:Math.min(30,sample+1)},(_,i)=>trace.down[(Math.max(0,sample-29)+i)%trace.down.length]),historyUp:Array.from({length:Math.min(30,sample+1)},(_,i)=>trace.up[(Math.max(0,sample-29)+i)%trace.up.length]),sample},capabilities:{read:true,edit:true,password:'test-only',systemAccess:false}});}
  return{
   snapshot,
   tick(){sample++;if(active){totalDown+=trace.down[sample%trace.down.length]/1024;totalUp+=trace.up[sample%trace.up.length]/1024;}return snapshot();},
   setRadio(value){enabled=Boolean(value);if(!enabled)active=null;revision++;return snapshot();},
   async scan(signal){if(!enabled)throw new Error('Turn Wi-Fi on before scanning.');await wait(600,signal);return snapshot();},
   async connect(id,password='',signal){
    const n=networks.find(n=>n.id===id);if(!enabled)throw new Error('Turn Wi-Fi on first.');if(!n)throw new Error('This network is no longer available.');
    if(n.security!=='Open'&&!n.saved){const error=validatePassphrase(password);if(error)throw new Error(error);}password='';
    await wait(750,signal);if(signal?.aborted)throw new DOMException('Cancelled','AbortError');if(!enabled)throw new Error('Wi-Fi was switched off.');if(n.unavailable)throw new Error('Sample access point did not respond. Choose another demo network.');
    n.saved=true;if(!profiles.has(id))profiles.set(id,clone(defaults));active=id;revision++;return snapshot();
   },
   disconnect(){active=null;revision++;return snapshot();},
   forget(id){const n=networks.find(n=>n.id===id);if(!n)throw new Error('Unknown network.');n.saved=false;profiles.delete(id);if(active===id)active=null;revision++;return snapshot();},
   apply(id,draft){if(id!==active)throw new Error('Connect to this network before changing its profile.');const checked=validateSettings(draft);if(!checked.valid)throw new Error(Object.values(checked.errors)[0]);const previous=clone(profiles.get(id));profiles.set(id,checked.value);revision++;return{previous,snapshot:snapshot()};},
   restore(id,profile){if(profiles.has(id))profiles.set(id,clone(profile));revision++;return snapshot();},
   diagnostics(){return active?[['Link','Connected'],['Local route','Available (demo)'],['DNS','Responding (demo)'],['Internet','Not probed by this preview']]:[['Link','Disconnected'],['Local route','Unavailable'],['DNS','Not checked'],['Internet','Not checked']];}
  };
 }
 return{createDemo,validateSettings,validatePassphrase,changes};
})();
