"""Generate the review map from explicit interaction records; no native completion claims."""
from pathlib import Path
import json,html
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'src/interaction-depth.json').read_text());e=html.escape
parts=['''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>TToxThemes / Interaction depth</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#14171c;color:#edf0f4;font:14px/1.7 system-ui,sans-serif;padding:28px}main{max-width:1180px;margin:auto}a{color:#c9daeb}h1,h2{font-weight:500;letter-spacing:-.5px}p,small{color:#bcc4ce}.top{display:flex;gap:16px;flex-wrap:wrap}label{display:block;margin:20px 0}input{width:min(100%,450px);padding:10px;background:#262c34;border:1px solid #697280;border-radius:8px;color:inherit;font:inherit}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;vertical-align:top;padding:14px 10px;border-bottom:1px solid #353d48}td:first-child{white-space:nowrap}td:nth-child(2){min-width:170px}td:nth-child(3){min-width:200px}td:nth-child(4){min-width:270px}small{display:block;margin-top:6px}a:focus-visible,input:focus-visible{outline:2px solid #c9daeb;outline-offset:3px}[hidden]{display:none!important}@media(max-width:500px){body{padding:15px}}
</style></head><body><main><div class="top"><a href="/?theme=v-r-v3n0m&view=desktop">← Desktop reference</a><a href="prd-status.html">Native PRD audit</a></div><h1>40 paths with an actual next step.</h1>''']
for k in ['scope','native','visualQA']:parts.append('<p>'+e(data[k])+'</p>')
parts.append('<label>Find an interaction <input id="query" type="search" placeholder="Pairing, undo, FR-H4…"></label><p id="count" role="status">40 interaction paths</p><div class="scroll"><table><thead><tr><th>ID</th><th>Path</th><th>Before</th><th>Now / expected behavior</th><th>Verification</th></tr></thead><tbody>')
for r in data['paths']:
 parts.append('<tr><td>'+e(r['id'])+'<small>'+e(r['prd'])+'</small></td><td><a href="/?theme=v-r-v3n0m&amp;view=desktop&amp;panel='+e(r['panel'])+'">'+e(r['title'])+'</a><small>'+e(r['group'])+'</small></td><td>'+e(r['before'])+'</td><td>'+e(r['after'])+'</td><td>'+e(r['verification'])+'</td></tr>')
parts.append('</tbody></table></div><h2>Still open</h2><ul>')
parts.extend('<li>'+e(x)+'</li>' for x in data['remaining'])
parts.append('</ul><p>Checks: domain state tests and complete shipped HTML in a DOM emulator. The original wallpaper and native cursor remain unchanged.</p></main><script>const query=document.getElementById("query"),rows=[...document.querySelectorAll("tbody tr")];query.oninput=()=>{let n=0;for(const row of rows){row.hidden=!row.textContent.toLowerCase().includes(query.value.toLowerCase());if(!row.hidden)n++;}document.getElementById("count").textContent=n+" interaction paths";};</script></body></html>')
(root/'dist/interaction-depth.html').write_text(''.join(parts))
(root/'dist/interaction-depth.json').write_text(json.dumps(data,indent=2)+'\n')
print('Generated 40-path interaction review map')
