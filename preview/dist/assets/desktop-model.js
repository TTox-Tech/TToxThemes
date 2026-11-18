/* Domain state is independent from DOM, animation and storage. All system data is simulated. */
window.TToxDesktopModel = (()=>{
 const F=window.TToxDesktopFixtures,copy=x=>JSON.parse(JSON.stringify(x));
 const clamp=(n,min=0,max=100)=>Math.min(max,Math.max(min,Number(n)||0));
 const one=(value,values,fallback)=>values.includes(value)?value:fallback;
 function create({saved=null,now=()=>Date.now()}={}){
  const defaults=()=>Object.fromEntries(Object.entries(F.profiles).map(([name,ids])=>[name,ids.map(id=>({id,size:id==='terminal'?'L':'M'}))]));
  let s={version:1,audio:{output:'speakers',volume:42,muted:false,input:'internal',micMuted:false,inputGain:65,apps:{player:75,browser:45}},bluetooth:{radio:false,discovered:false,devices:copy(F.bluetooth)},display:{brightness:68,night:false,warmth:35,power:'balanced'},notifications:{dndUntil:0,muted:[],items:copy(F.notifications)},system:{sample:0,elapsed:0,frozen:false,sensors:'ready',history:[{at:0,cpu:12}]},dev:{containers:copy(F.containers),services:copy(F.services),logs:[],context:'none',namespace:'development'},layout:{profile:'work',profiles:defaults()},media:{track:0,position:138,playing:false,repeat:false,available:true},note:{text:'□ Review the theme tokens\n□ Check the low-RAM VM\n□ Keep the flow deliberate',savedAt:0}};
  let revision=0,noticeId=0;const listeners=new Set();
  function outputs(){return[{id:'speakers',name:'Built-in speakers'},...s.bluetooth.devices.filter(d=>d.connected&&d.kind==='Audio').map(d=>({id:d.id,name:d.name}))];}
  function repairAudio(){if(!outputs().some(d=>d.id===s.audio.output))s.audio.output='speakers';}
  function restore(raw){
   if(!raw||raw.version!==1)return;
   if(raw.audio){s.audio.volume=clamp(raw.audio.volume);s.audio.muted=Boolean(raw.audio.muted);s.audio.input=one(raw.audio.input,['internal','usb'],'internal');s.audio.micMuted=Boolean(raw.audio.micMuted);s.audio.inputGain=clamp(raw.audio.inputGain);for(const id of Object.keys(s.audio.apps))if(raw.audio.apps?.[id]!=null)s.audio.apps[id]=clamp(raw.audio.apps[id]);}
   if(raw.display){s.display={brightness:clamp(raw.display.brightness,20),night:Boolean(raw.display.night),warmth:clamp(raw.display.warmth),power:one(raw.display.power,['balanced','saver','performance'],'balanced')};}
   if(raw.notifications){s.notifications.dndUntil=Number(raw.notifications.dndUntil)>now()?Number(raw.notifications.dndUntil):0;s.notifications.muted=Array.isArray(raw.notifications.muted)?raw.notifications.muted.filter(x=>['Build','Dev','System'].includes(x)):[];}
   if(raw.layout){s.layout.profile=one(raw.layout.profile,Object.keys(F.profiles),'work');for(const name of Object.keys(F.profiles)){const ids=new Set();if(Array.isArray(raw.layout.profiles?.[name]))s.layout.profiles[name]=raw.layout.profiles[name].filter(w=>w&&F.widgets.some(x=>x.id===w.id)&&!ids.has(w.id)&&ids.add(w.id)).map(w=>({id:w.id,size:one(w.size,['S','M','L'],'M')}));}}
   if(raw.media){s.media.track=clamp(Math.floor(raw.media.track),0,F.tracks.length-1);s.media.position=clamp(raw.media.position,0,F.tracks[s.media.track].duration);s.media.repeat=Boolean(raw.media.repeat);}
   if(typeof raw.note?.text==='string')s.note={text:raw.note.text.slice(0,1500),savedAt:Number(raw.note.savedAt)||0};
  }
  restore(saved);
  function preferences(){return copy({version:1,audio:s.audio,display:s.display,notifications:{dndUntil:s.notifications.dndUntil,muted:s.notifications.muted},layout:s.layout,media:{track:s.media.track,position:s.media.position,repeat:s.media.repeat},note:s.note});}
  function snapshot(){
   const result=copy(s),t=now();result.hardware=copy(F.hardware||{battery:null,gpu:null});result.mode='demo';result.revision=revision;result.audio.outputs=outputs();result.audio.effectiveVolume=s.audio.muted?0:s.audio.volume;result.audio.playerVolume=result.audio.effectiveVolume*s.audio.apps.player/100;result.notifications.dnd=s.notifications.dndUntil>t;result.notifications.visible=result.notifications.items.filter(n=>!n.dismissed&&(!n.snoozeUntil||n.snoozeUntil<=t));result.notifications.unread=result.notifications.visible.filter(n=>!n.read).length;
   const cpu=F.cpuTrace[s.system.sample%F.cpuTrace.length];result.system.cpu=cpu;result.system.cores=[cpu-4,cpu+3,cpu-2,cpu+3];result.system.memory=+(2.4+(s.system.sample%5)*.03).toFixed(2);result.system.processes=copy(F.processes).map(p=>{const c=s.dev.containers.find(c=>c.name===p.name);return c?{...p,cpu:c.cpu,memory:c.memory}:p;});result.system.disks=copy(F.disks);result.media.current=copy(F.tracks[s.media.track]);return result;
  }
  function emit(persist=true){revision++;const value=snapshot();for(const fn of listeners)fn(value,persist);return value;}
  function notification(title,body,route='Dev',app='Dev'){
   const item={id:'event-'+(++noticeId),title,body,route,app,read:false,quiet:s.notifications.dndUntil>now()||s.notifications.muted.includes(app)};
   s.notifications.items.unshift(item);s.notifications.items=s.notifications.items.slice(0,40);return item;
  }
  function device(id){const d=s.bluetooth.devices.find(d=>d.id===id);if(!d)throw Error('Device is no longer available.');return d;}
  function send(type,p={}){
   switch(type){
    case 'audio.volume':s.audio.volume=clamp(p.value);if(s.audio.volume>0)s.audio.muted=false;break;
    case 'audio.mute':s.audio.muted=!s.audio.muted;break;
    case 'audio.output':if(!outputs().some(d=>d.id===p.id))throw Error('Connect that audio device first.');s.audio.output=p.id;break;
    case 'audio.input':s.audio.input=one(p.id,['internal','usb'],'internal');break;
    case 'audio.mic':s.audio.micMuted=!s.audio.micMuted;break;
    case 'audio.gain':s.audio.inputGain=clamp(p.value);break;
    case 'audio.app':if(!(p.id in s.audio.apps))throw Error('Unknown audio stream.');s.audio.apps[p.id]=clamp(p.value);break;
    case 'bluetooth.radio':s.bluetooth.radio=Boolean(p.value);if(!p.value){s.bluetooth.devices.forEach(d=>d.connected=false);s.bluetooth.discovered=false;}repairAudio();break;
    case 'bluetooth.scan':if(!s.bluetooth.radio)throw Error('Turn Bluetooth on first.');s.bluetooth.discovered=true;break;
    case 'bluetooth.connect':{const d=device(p.id);if(!s.bluetooth.radio)throw Error('Bluetooth is off.');if(d.unavailable)throw Error('Workshop speaker did not respond. Move it into range and retry, or choose Studio headphones.');d.paired=true;d.connected=true;if(d.kind==='Audio')s.audio.output=d.id;break;}
    case 'bluetooth.disconnect':device(p.id).connected=false;repairAudio();break;
    case 'bluetooth.forget':{const d=device(p.id);d.connected=false;d.paired=false;repairAudio();break;}
    case 'display.brightness':s.display.brightness=clamp(p.value,20);break;
    case 'display.night':s.display.night=Boolean(p.value);break;
    case 'display.warmth':s.display.warmth=clamp(p.value);break;
    case 'display.power':s.display.power=one(p.value,['balanced','saver','performance'],'balanced');break;
    case 'display.restore':s.display=copy(p.value);break;
    case 'display.reset':s.display={brightness:68,night:false,warmth:35,power:'balanced'};break;
    case 'notifications.dnd':s.notifications.dndUntil=p.minutes?now()+clamp(p.minutes,1,1440)*60000:0;break;
    case 'notifications.read':{const n=s.notifications.items.find(n=>n.id===p.id);if(n)n.read=true;break;}
    case 'notifications.snooze':{const n=s.notifications.items.find(n=>n.id===p.id);if(n)n.snoozeUntil=now()+60000;break;}
    case 'notifications.dismiss':s.notifications.items.forEach(n=>{if(p.ids.includes(n.id))n.dismissed=true;});break;
    case 'notifications.restore':for(const old of p.items){const i=s.notifications.items.findIndex(n=>n.id===old.id);if(i>=0)s.notifications.items[i]=copy(old);}break;
    case 'notifications.mute':s.notifications.muted=s.notifications.muted.includes(p.app)?s.notifications.muted.filter(a=>a!==p.app):[...s.notifications.muted,p.app];break;
    case 'notifications.sample':notification('Build finished','Review the sample container logs.','Dev','Build');break;
    case 'system.freeze':s.system.frozen=!s.system.frozen;break;
    case 'system.sensors':s.system.sensors=one(p.state,['ready','error'],'ready');break;
    case 'dev.container':{
     const c=s.dev.containers.find(c=>c.id===p.id);if(!c)throw Error('Container is no longer available.');if(!['start','stop','restart'].includes(p.action))throw Error('Unknown action.');
     c.state=p.action==='stop'?'stopped':'running';c.cpu=c.state==='running'?2.4:0;c.memory=c.state==='running'?184:0;
     s.dev.logs.unshift({at:now(),id:c.id,text:c.name+': '+({start:'started; health check passed',stop:'stopped gracefully; ports released',restart:'restarted; health check passed'}[p.action])});s.dev.logs=s.dev.logs.slice(0,30);notification(c.name+' '+c.state,'Container '+p.action+' completed in the demo.');break;
    }
    case 'dev.service':{const d=s.dev.services.find(d=>d.id===p.id);if(!d)throw Error('Service is no longer available.');if(d.denied)throw Error('Authorization denied in this demo scenario. Service unchanged. The installed desktop would use polkit.');d.state=d.state==='running'?'stopped':'running';notification(d.name+' '+d.state,'Service state updated in the demo.');break;}
    case 'dev.context':s.dev.context=one(p.value,['none','local'],'none');break;
    case 'dev.namespace':s.dev.namespace=one(p.value,Object.keys(F.namespaces),'development');break;
    case 'layout.profile':s.layout.profile=one(p.name,Object.keys(F.profiles),'work');break;
    case 'layout.toggle':{const list=s.layout.profiles[s.layout.profile];if(!F.widgets.some(w=>w.id===p.id))throw Error('Unknown widget.');const i=list.findIndex(w=>w.id===p.id);if(i>=0)list.splice(i,1);else list.push({id:p.id,size:'M'});break;}
    case 'layout.size':{const w=s.layout.profiles[s.layout.profile].find(w=>w.id===p.id);if(w)w.size=one(p.size,['S','M','L'],'M');break;}
    case 'layout.move':{const list=s.layout.profiles[s.layout.profile],i=list.findIndex(w=>w.id===p.id);if(i>=0){const target=clamp(i+p.delta,0,list.length-1);const [item]=list.splice(i,1);list.splice(target,0,item);}break;}
    case 'layout.reset':s.layout.profiles[s.layout.profile]=defaults()[s.layout.profile];break;
    case 'layout.restore':s.layout=copy(p.value);break;
    case 'media.play':if(!s.media.available)throw Error('No player is available. Restore the demo player first.');s.media.playing=!s.media.playing;break;
    case 'media.seek':s.media.position=clamp(p.value,0,F.tracks[s.media.track].duration);break;
    case 'media.track':s.media.track=clamp(p.index,0,F.tracks.length-1);s.media.position=0;break;
    case 'media.step':s.media.track=(s.media.track+p.delta+F.tracks.length)%F.tracks.length;s.media.position=0;break;
    case 'media.repeat':s.media.repeat=!s.media.repeat;break;
    case 'media.available':s.media.available=Boolean(p.value);if(!p.value)s.media.playing=false;break;
    case 'note.save':s.note={text:String(p.text).slice(0,1500),savedAt:now()};break;
    default:throw Error('Unknown interaction: '+type);
   }
   return emit();
  }
  return{snapshot,preferences,send,subscribe(fn){listeners.add(fn);return()=>listeners.delete(fn);},tick(seconds=1,{system=false,media=false}={}){
   if(system&&!s.system.frozen){s.system.sample++;s.system.elapsed+=seconds;s.system.history.push({at:s.system.elapsed,cpu:F.cpuTrace[s.system.sample%F.cpuTrace.length]});s.system.history=s.system.history.filter(x=>x.at>=s.system.elapsed-60);}
   if(media&&s.media.playing&&s.media.available){s.media.position+=seconds;while(s.media.position>=F.tracks[s.media.track].duration){s.media.position-=F.tracks[s.media.track].duration;if(s.media.track<F.tracks.length-1)s.media.track++;else if(s.media.repeat)s.media.track=0;else{s.media.position=F.tracks[s.media.track].duration;s.media.playing=false;break;}}}
   return emit(false);
  }};
 }
 return{create};
})();
