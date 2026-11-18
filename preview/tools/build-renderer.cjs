const fs=require('node:fs'),path=require('node:path');
const {stripTypeScriptTypes}=require('node:module');
const root=path.resolve(__dirname,'..');
const ts=fs.readFileSync(path.join(root,'src/surface-geometry.ts'),'utf8')+'\n'+fs.readFileSync(path.join(root,'src/venom-native.ts'),'utf8')+'\n'+fs.readFileSync(path.join(root,'src/venom-backend.ts'),'utf8');
const js=stripTypeScriptTypes(ts,{mode:'strip'}).replace(/[ \t]+$/gm,'');
fs.writeFileSync(path.join(root,'dist/assets/venom-native.js'),'(()=>{\n'+js+'\n})();\n');
new (require('node:vm').Script)(js);
console.log('Native renderer builds without React or a runtime compiler.');
