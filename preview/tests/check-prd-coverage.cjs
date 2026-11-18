const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),a=JSON.parse(fs.readFileSync(path.join(root,'src/prd-coverage.json'),'utf8')),source=fs.readFileSync(path.join(root,'src/reference/TToxThemes-PRD.txt'),'utf8');
const expected=new Set(source.split(/\r?\n/).map(x=>x.trim()).filter(x=>/^(FR-[A-Z]+\d+|NFR-\d+)$/.test(x))),actual=new Set(a.rows.map(x=>x.id));
assert.equal(expected.size,107);assert.deepEqual([...actual].sort(),[...expected].sort());assert.equal(actual.size,a.rows.length);assert.equal(a.native_end_to_end_verified,0);assert.equal(Object.values(a.counts).reduce((x,y)=>x+y,0),107);assert.equal(a.acceptance.length,24);assert.equal(new Set(a.acceptance.map(x=>x.id)).size,24);
for(const r of a.rows){assert(r.requirement&&r.gap&&r.preview);assert(['missing','scaffold','unverified','blocked'].includes(r.native_status));}
assert(fs.readFileSync(path.join(root,'dist/prd-status.html'),'utf8').includes('Reference preview ≠ native kit delivery'));
console.log('All 107 original FR/NFR IDs and all 24 acceptance checks accounted for; no native completion claims.');
