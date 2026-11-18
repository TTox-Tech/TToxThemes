const {q,click,advance,document,window,context,timers,assert}=require('./dom-fixture.cjs')('https://test.local/?theme=minimalistix&colour=sterling&view=desktop');
const change=(id,value)=>{const n=q('#'+id);n.value=value;n.onchange({target:n});};
function key(value,target=q('#ttox-room')){const event=new window.Event('keydown',{bubbles:true,cancelable:true});Object.defineProperty(event,'key',{value});target.dispatchEvent(event);}
function pointer(type,target,x,y){const event=new window.Event(type,{bubbles:true});for(const[k,value]of Object.entries({clientX:x,clientY:y,pointerId:1}))Object.defineProperty(event,k,{value});target.dispatchEvent(event);}
(async()=>{
 assert.equal(q('#ttox-room').dataset.family,'minimalistix');assert(!q('#minimalistix-root').hidden);
 assert.equal(q('#room-theme').querySelectorAll('option').length,2,'Only two theme families');assert.equal(q('#room-palette').querySelectorAll('option').length,3,'Three colour variants belong to MinimalistiX');
 assert.deepEqual([...q('#room-palette').querySelectorAll('option')].map(n=>n.textContent),['Sterling','Vino','Graphite']);
 assert.equal(q('.min-files').style.width,'44%');assert.equal(q('.min-terminal').style.left,'41%');assert.equal(q('#min-workspaces').children.length,4);
 change('room-palette','vino');assert.equal(q('#ttox-room').dataset.family,'minimalistix');assert(q('#min-fastfetch-values').textContent.includes('MinimalistiX / Vino'));assert.equal(q('.min-terminal').style.left,'41%');
 key('h');assert(!q('.room-hud').hidden);assert.equal(q('.min-hud-columns').children.length,3);assert(q('.min-shell').inert);
 click('[data-min-action="container-api"]');assert.equal(q('[data-min-action="container-api"]').dataset.armed,'true');await advance(2100);assert.equal(q('[data-min-action="container-api"]').textContent,'stop');
 click('[data-min-action="container-api"]');click('[data-min-action="container-api"]');await advance(500);assert.equal(q('[data-container=api] .min-tag').textContent,'exited');assert.equal(q('[data-min-container-count]').textContent,'1');
 key('Escape');assert(q('.room-hud').hidden);key('`');assert(!q('.room-drawer').hidden);
 const drawerTab=name=>[...q('#min-drawer-tabs').querySelectorAll('button')].find(n=>n.textContent.includes(name)).onclick();drawerTab('logs');assert(q('#min-drawer-content').textContent.includes('ports released'));drawerTab('scratch');let draft=q('#min-drawer-content textarea');draft.value='retained scratch';draft.oninput();drawerTab('btop');drawerTab('scratch');assert.equal(q('#min-drawer-content textarea').value,'retained scratch');
 key('Escape');key('`');assert.equal(q('#min-drawer-content textarea').value,'retained scratch');key('Escape');
 key(' ');assert(!q('.room-minlauncher').hidden);const input=q('#min-launch-search');input.value='bur';input.oninput();assert(q('#min-launch-results').textContent.includes('Burp Suite Community'));key('Enter',input);assert(!q('.room-hud').hidden);
 click('#min-hud-wifi');assert(!q('.room-wifi').hidden);assert(q('.room-hud').hidden);key('Escape');
 click('[data-workspace="1"]');assert(!q('.min-empty').hidden);click('.min-empty [data-min-open=terminal]');assert(!q('.min-terminal').hidden);assert(q('.min-files').hidden);click('[data-workspace="2"]');assert(!q('.min-files').hidden);assert(q('.min-terminal').hidden);click('.min-dock [data-min-open=terminal]');
 click('[data-min-max=terminal]');assert.equal(q('.min-terminal').style.width,'88%');click('[data-min-max=terminal]');assert.equal(q('.min-terminal').style.width,'50%');
 const header=q('[data-min-drag=files]');pointer('pointerdown',header,0,0);pointer('pointermove',header,20,10);pointer('pointerup',header,20,10);assert.notEqual(q('.min-files').style.left,'7%');
 click('[data-file="infra"]');click('#min-file-open');assert(q('#min-path').textContent.includes('infra'));click('#min-file-up');assert(q('#min-path').textContent.includes('home'));
 change('room-effects','lite');await Promise.resolve();assert(q('.room-desktop').classList.contains('room-lite'));assert(q('#min-poll-label').textContent.includes('5 s'));
 key('n');assert(!q('#min-notification').hidden);await advance(5001);assert(q('#min-notification').hidden);
 document.hidden=true;document.dispatchEvent(new window.Event('visibilitychange'));await advance(10000);assert.equal(timers.size,0,'No MinimalistiX sampling survives page hiding');document.hidden=false;document.dispatchEvent(new window.Event('visibilitychange'));
 change('room-theme','v-r-v3n0m');assert(q('#minimalistix-root').hidden);assert(q('#room-colour-label').hidden);assert.equal(q('#ttox-room').dataset.family,'v-r-v3n0m');await advance(10000);assert.equal(timers.size,0,'Leaving MinimalistiX releases its timers');
 change('room-theme','minimalistix');assert.equal(q('#room-palette').value,'vino','Return to last MinimalistiX colour');assert(!q('#minimalistix-root').hidden);
 console.log('MinimalistiX: theme/colour taxonomy, unchanged composition across colours, HUD actions, drawer persistence, launcher search/keyboard, Wi-Fi routing, workspaces, window geometry and visibility cleanup passed in DOM emulation.');
})().catch(e=>{console.error(e);process.exitCode=1;});
