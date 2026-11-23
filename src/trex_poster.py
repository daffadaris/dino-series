import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
import pathlib, importlib.util, sys
sys.path.insert(0, HERE)
import scenery
spec = importlib.util.spec_from_file_location("dino", HERE + "/trex_svg.py")
dino = importlib.util.module_from_spec(spec); spec.loader.exec_module(dino)

BUFF, UMBER, LABEL = "#E5C895", "#2B1E16", "#CDB894"

# poster scene: Hell Creek floodplain (src/scenery.py)
SCENE = scenery.set_hell_creek()

DINO = f'''<button type="button" class="tr-btn" aria-label="Make the T. rex roar" onClick="{{{{roar}}}}" style="position: absolute; top: 262px; left: 0; width: 1080px; height: 605px; padding: 0; margin: 0; border: 0; background: none; cursor: pointer; display: block">
<svg class="{{{{animClass}}}}" aria-hidden="true" viewBox="0 0 1000 560" width="1080" height="605" style="display: block">
{dino.FRAG.replace(dino.SKIN, "{{skin}}")}
</svg>
</button>'''

CSS = """
body{margin:0}
a{color:#2B1E16}a:hover{color:#000}
.tr-btn:focus-visible{outline:3px solid #2B1E16;outline-offset:-6px;border-radius:12px}
.tr-tail,.tr-body,.tr-head,.tr-jaw,.tr-arm,.tr-arm-far{transform-origin:0 0}
.tr-eyelid{transform-origin:0 0;transform:scaleY(0)}
.tr-anim .tr-body{animation:tr-breath 3.2s ease-in-out infinite}
.tr-anim .tr-tail{animation:tr-tail 5s ease-in-out infinite}
.tr-anim .tr-eyelid{animation:tr-blink 5s linear infinite}
.tr-roaring .tr-head{animation:tr-head-roar 1.5s cubic-bezier(.3,.7,.2,1)}
.tr-roaring .tr-jaw{animation:tr-jaw-roar 1.5s cubic-bezier(.3,.7,.2,1)}
.tr-roaring .tr-arm,.tr-roaring .tr-arm-far{animation:tr-arm-roar 1.5s ease-in-out}
@keyframes tr-breath{0%,100%{transform:scale(1,1)}50%{transform:scale(1.006,1.016)}}
@keyframes tr-tail{0%,100%{transform:rotate(0)}50%{transform:rotate(-1.5deg)}}
@keyframes tr-blink{0%,93%,100%{transform:scaleY(0)}95.5%{transform:scaleY(1)}}
@keyframes tr-head-roar{0%{transform:rotate(0)}16%{transform:rotate(4deg)}38%,74%{transform:rotate(-8deg)}100%{transform:rotate(0)}}
@keyframes tr-jaw-roar{0%,16%{transform:rotate(0)}38%,74%{transform:rotate(16deg)}100%{transform:rotate(0)}}
@keyframes tr-arm-roar{0%,100%{transform:rotate(0)}40%,74%{transform:rotate(14deg)}}
@media (prefers-reduced-motion: reduce){.tr-anim *,.tr-roaring *{animation:none !important}}
""".strip()

FACTS = [("12 m", "snout to tail tip"), ("68–66", "million years ago"), ("50–60", "serrated teeth")]
facts_html = "\n".join(f'''<div style="display: flex; flex-direction: column; gap: 4px">
<span style="font-family: 'Big Shoulders Display', 'Public Sans', sans-serif; font-weight: 800; font-size: 80px; line-height: 0.95; color: {BUFF}">{n}</span>
<span style="font-size: 20px; color: {LABEL}">{l}</span>
</div>''' for n, l in FACTS)

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>T. rex poster</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&amp;family=Public+Sans:ital,wght@0,400;0,500;1,400&amp;display=swap">
<style>
{CSS}
</style>
</helmet>
<div style="width: 1080px; height: 1350px; position: relative; overflow: hidden; background: {UMBER}; font-family: 'Public Sans', system-ui, sans-serif; color: {UMBER}">

<div style="position: relative; width: 1080px; height: 900px">
{SCENE}
<div style="position: absolute; top: 56px; left: 64px; display: flex; flex-direction: column; gap: 10px">
<h1 style="margin: 0; font-family: 'Big Shoulders Display', 'Public Sans', sans-serif; font-weight: 900; font-size: 300px; line-height: 0.8; letter-spacing: -0.01em; color: {UMBER}">T. rex</h1>
<p style="margin: 0; font-size: 28px; color: {UMBER}"><em>Tyrannosaurus rex</em>, the tyrant lizard king</p>
</div>
{DINO}
<p style="position: absolute; right: 56px; bottom: 20px; margin: 0; padding: 6px 12px; border-radius: 8px; background: rgba(243, 223, 194, 0.9); font-size: 17px; font-weight: 500; color: {UMBER}">Tap the dinosaur to make it roar</p>
</div>

<div style="box-sizing: border-box; height: 450px; padding: 52px 64px 48px; display: flex; flex-direction: column; gap: 36px; color: {BUFF}">
<p style="margin: 0; font-size: 30px; line-height: 1.4; max-width: 860px">One of the largest meat-eating land animals ever, with a bite among the strongest of any land animal.</p>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px">
{facts_html}
</div>
<p style="margin: 0; margin-top: auto; font-size: 18px; line-height: 1.5; color: {LABEL}">Fossils come from the Hell Creek Formation of Montana and the Dakotas, and other Late Cretaceous rocks of western North America.</p>
</div>

</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"animate":{{"editor":"boolean","default":true}},"skin":{{"editor":"color","default":"#9E6B7B","options":["#9E6B7B","#6B6250","#4E6E63","#7A5A48"]}},"$preview":{{"width":1080,"height":1350}}}}'>
class Component extends DCLogic {{
componentWillUnmount() {{
clearTimeout(this._roarTimer);
}}
renderVals() {{
const animate = this.props.animate ?? true;
const roaring = this.state && this.state.roaring;
return {{
skin: this.props.skin ?? '#9E6B7B',
animClass: (animate ? 'tr-anim' : '') + (roaring ? ' tr-roaring' : ''),
roar: () => {{
clearTimeout(this._roarTimer);
this.setState({{ roaring: false }}, () => {{
requestAnimationFrame(() => this.setState({{ roaring: true }}));
}});
this._roarTimer = setTimeout(() => this.setState({{ roaring: false }}), 1600);
}}
}};
}}
}}
</script>
</body>
</html>
'''
pathlib.Path(ROOT + "/boards/Main.dc.html").write_text(HTML)

# local preview with the template holes filled in, for a screenshot check
prev = (HTML.replace('<script src="./support.js"></script>', "")
        .replace("<helmet>", "").replace("</helmet>", "").replace("<x-dc>", "").replace("</x-dc>", "")
        .replace("{{skin}}", "#9E6B7B").replace("{{animClass}}", "").replace('onClick="{{roar}}"', ""))
prev = prev[:prev.index('<script type="text/x-dc"')] + "</body></html>"
pathlib.Path(ROOT + "/shots/preview.html").write_text(prev)
print("ok", HTML.count("{{"), "holes")
