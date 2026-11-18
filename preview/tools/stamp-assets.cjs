const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const dist=path.resolve(__dirname,'../dist'),html=path.join(dist,'index.html');
const text=fs.readFileSync(html,'utf8').replace(/(src|href)="(assets\/[^"?]+)(?:\?[^\"]*)?"/g,(_,attribute,file)=>{
 const hash=crypto.createHash('sha256').update(fs.readFileSync(path.join(dist,file))).digest('hex').slice(0,12);
 return `${attribute}="${file}?v=${hash}"`;
});
fs.writeFileSync(html,text);
