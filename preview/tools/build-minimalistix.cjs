const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),design=JSON.parse(fs.readFileSync(path.join(root,'src/minimalistix-design.json'),'utf8'));
fs.writeFileSync(path.join(root,'dist/assets/minimalistix-design.js'),'/* Generated from src/minimalistix-design.json. */\nwindow.MinimalistiXDesign = '+JSON.stringify(design)+';\n');
const htmlPath=path.join(root,'dist/index.html'),html=fs.readFileSync(htmlPath,'utf8'),fragment=fs.readFileSync(path.join(root,'src/minimalistix.html'),'utf8');
fs.writeFileSync(htmlPath,html.replace(/<!-- MINIMALISTIX START -->[\s\S]*?<!-- MINIMALISTIX END -->/,'<!-- MINIMALISTIX START -->\n'+fragment+'\n<!-- MINIMALISTIX END -->'));
