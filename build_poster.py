import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("dino", HERE + "/build5.py")
dino = importlib.util.module_from_spec(spec); spec.loader.exec_module(dino)

SKY, FAR, SAND, OCHRE, BUFF, RUST, UMBER, LABEL = "#C9D6DA", "#A7B2B9", "#D6AB72", "#C08A55", "#E5C895", "#B5763F", "#2B1E16", "#CDB894"

def band(y, h, color, phase=0):
    w = [y - 6 + phase, y + 6 - phase, y - 3, y + 4]
    return (f'<path d="M0 {y} C270 {w[0]} 540 {w[1]} 810 {w[2]} C930 {w[3]} 1010 {y} 1080 {y - 2} '
            f'L1080 {y + h} C810 {y + h + 4} 540 {y + h - 5} 270 {y + h + 3} C160 {y + h + 6} 70 {y + h} 0 {y + h + 2} Z" fill="{color}"></path>')

def fern(x, y, sc, color, flip=False):
    fl = -1 if flip else 1
    fronds = "".join(
        f'<path d="M0 0 C{fl*a*0.35:.0f} {-l*0.45:.0f} {fl*a*0.8:.0f} {-l*0.8:.0f} {fl*a:.0f} {-l:.0f} C{fl*a*0.75:.0f} {-l*0.72:.0f} {fl*a*0.3:.0f} {-l*0.35:.0f} 0 0 Z"></path>'
        for a, l in [(-70, 120), (-40, 150), (-10, 165), (25, 150), (60, 118), (90, 80), (-95, 75)])
    return f'<g transform="translate({x} {y}) scale({sc})" fill="{color}">{fronds}</g>'

SCENE = f'''<svg aria-hidden="true" viewBox="0 0 1080 900" width="1080" height="900" style="position: absolute; top: 0; left: 0; display: block">
<defs>
<linearGradient id="sc-sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#AFC4CF"></stop>
<stop offset="0.55" stop-color="#D5D3CC"></stop>
<stop offset="0.75" stop-color="#EBCFA8"></stop>
</linearGradient>
<radialGradient id="sc-sun" cx="0.5" cy="0.5" r="0.5">
<stop offset="0" stop-color="#FFF4DC" stop-opacity="0.95"></stop>
<stop offset="0.25" stop-color="#FFE2B0" stop-opacity="0.55"></stop>
<stop offset="1" stop-color="#FFE2B0" stop-opacity="0"></stop>
</radialGradient>
<linearGradient id="sc-haze" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#F3DFC2" stop-opacity="0"></stop>
<stop offset="0.6" stop-color="#F3DFC2" stop-opacity="0.55"></stop>
<stop offset="1" stop-color="#F3DFC2" stop-opacity="0"></stop>
</linearGradient>
<linearGradient id="sc-ground" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#000000" stop-opacity="0"></stop>
<stop offset="1" stop-color="#3B2414" stop-opacity="0.35"></stop>
</linearGradient>
<radialGradient id="sc-shadow" cx="0.5" cy="0.5" r="0.5">
<stop offset="0" stop-color="#3B2414" stop-opacity="0.38"></stop>
<stop offset="1" stop-color="#3B2414" stop-opacity="0"></stop>
</radialGradient>
</defs>
<rect x="0" y="0" width="1080" height="900" fill="url(#sc-sky)"></rect>
<circle cx="880" cy="600" r="330" fill="url(#sc-sun)"></circle>
<path d="M0 640 L60 640 L88 612 L190 608 L210 640 L340 640 L372 600 L520 596 L546 640 L700 640 L724 620 L820 616 L842 640 L1080 640 L1080 900 L0 900 Z" fill="#CDBFB6"></path>
<path d="M0 668 L120 668 L150 626 L300 620 L326 668 L560 668 L600 618 L770 612 L800 668 L1080 668 L1080 900 L0 900 Z" fill="#B7A39A"></path>
<path d="M150 626 L300 620 L302 630 L152 636 Z M600 618 L770 612 L772 624 L602 630 Z M156 646 L318 640 L320 646 L158 652 Z M606 640 L784 634 L786 640 L608 646 Z" fill="#A08C84"></path>
<rect x="0" y="560" width="1080" height="160" fill="url(#sc-haze)"></rect>
<path d="M0 724 C120 704 200 716 300 710 C420 702 520 720 640 712 C760 704 880 718 1080 708 L1080 900 L0 900 Z" fill="{SAND}"></path>
{band(748, 16, OCHRE)}
{band(786, 22, BUFF, 2)}
{band(830, 14, RUST, -2)}
{band(868, 40, OCHRE, 1)}
<rect x="0" y="704" width="1080" height="196" fill="url(#sc-ground)"></rect>
<ellipse cx="400" cy="824" rx="380" ry="26" fill="url(#sc-shadow)"></ellipse>
{fern(40, 900, 1.1, "#4A3A2C")}{fern(130, 905, 0.8, "#5B4636", True)}{fern(1010, 905, 1.2, "#4A3A2C", True)}{fern(930, 910, 0.75, "#5B4636")}
</svg>'''

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
pathlib.Path(HERE + "/project/Main.dc.html").write_text(HTML)

# local preview with the template holes filled in, for a screenshot check
prev = (HTML.replace('<script src="./support.js"></script>', "")
        .replace("<helmet>", "").replace("</helmet>", "").replace("<x-dc>", "").replace("</x-dc>", "")
        .replace("{{skin}}", "#9E6B7B").replace("{{animClass}}", "").replace('onClick="{{roar}}"', ""))
prev = prev[:prev.index('<script type="text/x-dc"')] + "</body></html>"
pathlib.Path(HERE + "/shots/preview.html").write_text(prev)
print("ok", HTML.count("{{"), "holes")
