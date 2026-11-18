const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const ctx={window:{},DOMException,console};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../dist/assets/network-model.js'),'utf8'),ctx);const N=ctx.window.TToxNetwork;
(async()=>{
 const adapter=N.createDemo({wait:async(ms,signal)=>{if(signal?.aborted)throw new DOMException('Cancelled','AbortError')}});
 const original=adapter.snapshot().profile;
 assert.equal(adapter.snapshot().capabilities.systemAccess,false);
 const bad=N.validateSettings({...original,ipv4:'manual',address:'999.1.1.1/99',gateway:'bad',dnsAuto:false,dns:'oops',mtu:512});assert(!bad.valid);assert(bad.errors.address&&bad.errors.gateway&&bad.errors.dns&&bad.errors.mtu);
 assert(N.validatePassphrase('short'));assert.equal(N.validatePassphrase('test-passphrase-123'),'');
 const secret='secret-must-not-persist-42';await adapter.connect('lab',secret);const after=adapter.snapshot();assert.equal(after.active,'lab');assert(!JSON.stringify(after).includes(secret));
 const changed=adapter.apply('lab',{...after.profile,dnsAuto:false,dns:'1.1.1.1, 9.9.9.9'});assert.equal(changed.snapshot.profile.dns[0],'1.1.1.1');assert(N.changes(changed.previous,changed.snapshot.profile).length>=2);
 adapter.restore('lab',changed.previous);assert.equal(adapter.snapshot().profile.dnsAuto,true);
 await assert.rejects(adapter.connect('archive','test-passphrase-123'),/did not respond/);assert.equal(adapter.snapshot().active,'lab');
 const abort=new AbortController();abort.abort();await assert.rejects(adapter.connect('guest','',abort.signal),{name:'AbortError'});
 adapter.setRadio(false);await assert.rejects(adapter.scan(),/Turn Wi-Fi/);await assert.rejects(adapter.connect('guest'),/Turn Wi-Fi/);assert.equal(adapter.snapshot().active,null);
 adapter.setRadio(true);await adapter.connect('guest');assert.equal(adapter.snapshot().active,'guest');adapter.forget('guest');assert.equal(adapter.snapshot().active,null);
 console.log('Demo connection, format validation, independent failure/cancellation, profile apply/restore and secret-free snapshots passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
