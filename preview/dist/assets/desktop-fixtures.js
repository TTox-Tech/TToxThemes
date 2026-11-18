/* Reference data only. Native providers will supply the same domain records. */
window.TToxDesktopFixtures = {
  bluetooth: [
    {id:'headphones',name:'Studio headphones',kind:'Audio',battery:76,paired:true,connected:false},
    {id:'keyboard',name:'Lab keyboard',kind:'Keyboard',battery:54,paired:false,connected:false,code:'482 619'},
    {id:'speaker',name:'Workshop speaker',kind:'Audio',battery:31,paired:false,connected:false,unavailable:true}
  ],
  tracks:[{id:'quiet',title:'Quiet Hours',artist:'Studio session',duration:272},{id:'orbit',title:'Low Orbit',artist:'Night archive',duration:198},{id:'rain',title:'After the Rain',artist:'Studio session',duration:246}],
  containers:[{id:'api',name:'api-dev',image:'node:22-alpine',port:3000,state:'running',cpu:2.4,memory:184},{id:'db',name:'postgres',image:'postgres:16',port:5432,state:'running',cpu:.8,memory:96},{id:'worker',name:'queue-worker',image:'python:3.12-slim',port:null,state:'stopped',cpu:0,memory:0}],
  services:[{id:'ssh',name:'SSH server',state:'running'},{id:'cron',name:'Cron scheduler',state:'running'},{id:'docker',name:'Docker engine',state:'running',denied:true}],
  processes:[{id:1542,name:'plasmashell',cpu:2.6,memory:224},{id:2911,name:'api-dev',cpu:2.4,memory:184},{id:2870,name:'postgres',cpu:.8,memory:96},{id:1990,name:'kitty',cpu:.4,memory:42}],
  disks:[{id:'root',name:'System',path:'/',used:56,total:128,read:4.2,write:1.1},{id:'home',name:'Home',path:'/home',used:28,total:128,read:.8,write:.4}],
  cpuTrace:[12,17,13,29,21,16,18,12,16,14,33,23,19,25,15,18,21,14,17,12],
  widgets:[{id:'clock',title:'Clock',description:'Time and date'},{id:'system',title:'System',description:'CPU, memory and storage'},{id:'network',title:'Network',description:'Wi-Fi and throughput'},{id:'terminal',title:'Terminal',description:'Session reference'},{id:'dev',title:'Dev watchlist',description:'Containers and repository'},{id:'notes',title:'Notes',description:'A local working draft'},{id:'media',title:'Now playing',description:'Playback and queue'}],
  profiles:{work:['clock','terminal','dev','system','notes','network','media'],minimal:['clock','terminal','system'],pentest:['clock','terminal','network','system','notes'],music:['clock','media','notes']},
  notifications:[{id:'build',title:'Theme build complete',body:'Palette outputs are ready for review.',app:'Build',route:'Dev',read:false},{id:'session',title:'Work session ready',body:'2 containers are running. Inspect their health and logs.',app:'Dev',route:'Dev',read:false}],
  namespaces:{development:[{name:'api-7c9',ready:'1/1',state:'Running'},{name:'worker-3f2',ready:'0/1',state:'Pending'}],system:[{name:'coredns-2a1',ready:'1/1',state:'Running'}]}
};
