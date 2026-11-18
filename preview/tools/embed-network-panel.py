from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'dist/index.html';text=p.read_text();start=text.index('<section id="room-wifi-panel"');end=text.index('    <section class="room-panel room-command"',start)
fragment=(root/'src/network-panel.html').read_text().replace('<section class="room-panel room-wifi"','<section id="room-wifi-panel" class="room-panel room-wifi"',1)
p.write_text(text[:start]+fragment+'\n'+text[end:])
