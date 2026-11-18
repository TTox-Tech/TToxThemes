/* Variant/material records; theme ownership is declared in TToxThemeFamilies below. */
window.TToxThemes = {
  sterling: {name:'Sterling',material:'glass',colors:{bg:'#10151d',fg:'#e0e5ee',muted:'#a9b2c0',accent:'#8eaecb',edge:'#77818f',err:'#dba5ab'}},
  vino: {name:'Vino',material:'glass',colors:{bg:'#191116',fg:'#eadfe4',muted:'#bcaab2',accent:'#c68299',edge:'#88727c',err:'#e19da8'}},
  graphite: {name:'Graphite',material:'glass',colors:{bg:'#191816',fg:'#e8e3dc',muted:'#b8aea1',accent:'#c69b78',edge:'#847b70',err:'#dfa49b'}},
  'v-r-v3n0m': {
    name:'V-R-V3N0M',material:'symbiote',
    colors:{bg:'#0d1014',fg:'#f0f2f5',muted:'#bec4cd',accent:'#d8dce5',edge:'#626a77',err:'#efb8b6',surface:'#24282f',raised:'#343a44',inset:'#191d24',selected:'#454d59'},
    shine:'#EDF0F7',
    description:'V-R-V3N0M / living charcoal, wet silver edges, liquid desktop surfaces',
    interaction:{sense:175,reach:85,release:215,mound:135,rim:115,glint:120,strands:5,margin:230,maxSurfaces:{balanced:3,full:4}}
  }
};
/* A theme defines structure/material. A colour variant never creates a new theme. */
window.TToxThemeFamilies = {
  minimalistix:{name:'MinimalistiX',variants:['sterling','vino','graphite'],defaultVariant:'sterling',layout:'minimalistix'},
  'v-r-v3n0m':{name:'V-R-V3N0M',variants:['v-r-v3n0m'],defaultVariant:'v-r-v3n0m',layout:'symbiote'}
};
for(const [id,p] of Object.entries(window.MinimalistiXDesign?.palettes||{})){
  window.TToxThemes[id].colors={bg:p.bg,surface:p.surface,raised:p.raised,inset:p.bg,fg:p.fg,muted:p.muted,accent:p.accent,edge:p.line,err:p.err,ok:p.ok,warn:p.warn,folder:p.folder,hi:p.fg_hi,accentText:p.accent_text};
  window.TToxThemes[id].description='MinimalistiX / '+window.TToxThemes[id].name+' colour · glass desktop';
}
window.TToxThemeFamilyOf = variant => Object.keys(window.TToxThemeFamilies).find(id=>window.TToxThemeFamilies[id].variants.includes(variant))||'minimalistix';
