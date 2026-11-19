import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
"""Group poster: all four dinosaurs at their real lengths (series layout)."""
import json, re, sys, pathlib, subprocess, importlib.util
sys.path.insert(0, HERE)
import dinokit as K

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

rex = load("rex5", HERE + "/build5.py")
poster = load("rexposter", HERE + "/build_poster.py")          # gives the T. rex click CSS
species = {s: load(f"sp_{s}", f"{HERE}/sp_{s}.py").SPEC for s in ("triceratops", "stegosaurus", "titanosaur")}

# ---- measure each drawing's nose-to-tail span (viewBox units) in a real browser
def measure():
    from playwright.sync_api import sync_playwright
    out = {}
    files = {"trex": ("trex-animated.svg", "#tail", "#head")}
    files.update({s: (f"{s}-animated.svg", "#tail", "#head") for s in species})
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = b.new_page()
        for k, (f, a, z) in files.items():
            pg.goto(f"file://{HERE}/{f}"); pg.wait_for_timeout(200)
            out[k] = pg.evaluate(f"""() => {{ const s = document.querySelector('svg'); s.classList.remove('tr-anim','tri-anim','stg-anim','tit-anim');
              const vb = s.viewBox.baseVal, r = s.getBoundingClientRect(), k = vb.width / r.width;
              const t = document.querySelector('{a}').getBoundingClientRect(), h = document.querySelector('{z}').getBoundingClientRect();
              return {{ left: (t.left - r.left) * k, right: (h.right - r.left) * k, vbw: vb.width, vbh: vb.height }}; }}""")
        b.close()
    return out

M = measure()
LENGTH = {"trex": 12, "triceratops": 9, "stegosaurus": 9, "titanosaur": 34}     # metres (Patagotitan 31-37: midpoint)
PX_PER_M = 26.5
def scale_of(k): return LENGTH[k] * PX_PER_M / (M[k]["right"] - M[k]["left"])

def strip_ids(frag, keep):
    return re.sub(r' id="([^"]+)"', lambda m: m.group(0) if any(m.group(1).startswith(p) for p in keep) else "", frag)

def place(k, frag, x_nose_left, ground_y, ground_vb, cls_hole, act_hole, label):
    s = scale_of(k); vbw, vbh = M[k]["vbw"], M[k]["vbh"]
    w, h = vbw * s, vbh * s
    left = x_nose_left - M[k]["left"] * s; top = ground_y - ground_vb * s
    return (f'<button type="button" class="grp-btn" aria-label="{label}" onClick="{{{{{act_hole}}}}}" style="position: absolute; left: {left:.0f}px; top: {top:.0f}px; width: {w:.0f}px; height: {h:.0f}px; padding: 0; margin: 0; border: 0; background: none; cursor: pointer; display: block">'
            f'<svg class="{{{{{cls_hole}}}}}" aria-hidden="true" viewBox="0 0 {vbw} {vbh}" width="{w:.0f}" height="{h:.0f}" style="display: block; overflow: visible">{frag}</svg></button>')

keep = ("trx-", "tri-", "stg-", "tit-")
rex_frag = strip_ids(rex.FRAG.replace(rex.SKIN, rex.DEFAULT_SKIN), keep)
frags = {s: strip_ids(sp["look"].defs() + sp["frag"].replace(K.SKIN, sp["look"].skin), keep) for s, sp in species.items()}
for s, sp in species.items():
    K.motion_css(sp["code"], None, sp["action"], sp["dur"])
click_css = {s: K.motion_css(sp["code"], None, sp["action"], sp["dur"])[0] for s, sp in species.items()}

# ground lines: titanosaur stands further back, the other three in a front row
BACK_G, FRONT_G = 812, 868
figures = [
    place("titanosaur", frags["titanosaur"], 70, BACK_G, species["titanosaur"].get("ground", 650), "titClass", "titAct", "Make the titanosaur call"),
    place("trex", rex_frag, 48, FRONT_G, 514, "trexClass", "trexAct", "Make the T. rex roar"),
    place("triceratops", frags["triceratops"], 420, FRONT_G + 6, species["triceratops"].get("ground", 514), "triClass", "triAct", "Make the Triceratops charge"),
    place("stegosaurus", frags["stegosaurus"], 742, FRONT_G - 4, species["stegosaurus"].get("ground", 514), "stgClass", "stgAct", "Make the Stegosaurus swing its tail"),
]

ten_m = 10 * PX_PER_M
SCENE = f'''<svg aria-hidden="true" viewBox="0 0 1080 900" width="1080" height="900" style="position: absolute; top: 0; left: 0; display: block">
<defs>
<linearGradient id="grp-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B3C6CF"></stop><stop offset="0.6" stop-color="#DCD8CC"></stop><stop offset="0.82" stop-color="#EBD6B2"></stop></linearGradient>
<radialGradient id="grp-sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF4DC" stop-opacity="0.85"></stop><stop offset="1" stop-color="#FFE2B0" stop-opacity="0"></stop></radialGradient>
<linearGradient id="grp-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3DFC2" stop-opacity="0"></stop><stop offset="0.6" stop-color="#F3DFC2" stop-opacity="0.5"></stop><stop offset="1" stop-color="#F3DFC2" stop-opacity="0"></stop></linearGradient>
<linearGradient id="grp-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#3B2414" stop-opacity="0.32"></stop></linearGradient>
</defs>
<rect x="0" y="0" width="1080" height="900" fill="url(#grp-sky)"></rect>
<circle cx="900" cy="640" r="300" fill="url(#grp-sun)"></circle>
<path d="M0 700 C140 668 260 676 380 690 C520 660 660 664 780 684 C880 668 980 668 1080 680 L1080 900 L0 900 Z" fill="#B9B3A4"></path>
<rect x="0" y="620" width="1080" height="140" fill="url(#grp-haze)"></rect>
<path d="M0 772 C200 760 400 768 600 764 C800 760 960 768 1080 762 L1080 900 L0 900 Z" fill="#CFB07A"></path>
<path d="M0 812 C270 806 540 816 810 810 C930 808 1010 812 1080 810 L1080 826 C810 830 540 822 270 828 C160 830 70 826 0 828 Z" fill="#BF9A62"></path>
<path d="M0 846 C270 840 540 850 810 844 C930 842 1010 846 1080 844 L1080 862 C810 866 540 858 270 864 C160 866 70 862 0 864 Z" fill="#DCC08E"></path>
<rect x="0" y="760" width="1080" height="140" fill="url(#grp-ground)"></rect>
<g transform="translate(64 410)">
<rect x="0" y="0" width="{ten_m:.0f}" height="8" fill="#2B1E16"></rect>
<rect x="0" y="0" width="{ten_m/2:.0f}" height="8" fill="#F3E6CF"></rect>
<rect x="0" y="0" width="{ten_m:.0f}" height="8" fill="none" stroke="#2B1E16" stroke-width="2"></rect>
<text x="0" y="-10" font-family="Public Sans, system-ui, sans-serif" font-size="17" font-weight="600" fill="#2B1E16">0</text>
<text x="{ten_m/2:.0f}" y="-10" text-anchor="middle" font-family="Public Sans, system-ui, sans-serif" font-size="17" font-weight="600" fill="#2B1E16">5</text>
<text x="{ten_m:.0f}" y="-10" text-anchor="middle" font-family="Public Sans, system-ui, sans-serif" font-size="17" font-weight="600" fill="#2B1E16">10 m</text>
</g>
</svg>'''

UMBER, BUFF, LABEL = K.UMBER, K.BUFF, K.LABEL
facts = [("31–37 m", "Patagotitan"), ("12 m", "Tyrannosaurus rex"), ("8–9 m", "Triceratops and Stegosaurus")]
facts_html = "\n".join(f'''<div style="display: flex; flex-direction: column; gap: 4px">
<span style="font-family: 'Big Shoulders Display', 'Public Sans', sans-serif; font-weight: 800; font-size: 80px; line-height: 0.95; color: {BUFF}">{n}</span>
<span style="font-size: 20px; color: {LABEL}">{l}</span>
</div>''' for n, l in facts)

trex_css = re.search(r"<style>\n(.*?)\n</style>", poster.HTML, re.S).group(1)
trex_css = "\n".join(l for l in trex_css.splitlines() if l.startswith((".tr-", "@keyframes tr-", "@media")))
css = "\n".join([trex_css] + list(click_css.values()))

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Four dinosaurs to scale</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&amp;family=Public+Sans:ital,wght@0,400;0,500;0,600;1,400&amp;display=swap">
<style>
body{{margin:0}}
a{{color:{UMBER}}}a:hover{{color:#000}}
.grp-btn:focus-visible{{outline:3px solid {UMBER};outline-offset:2px;border-radius:12px}}
{css}
</style>
</helmet>
<div style="width: 1080px; height: 1350px; position: relative; overflow: hidden; background: {UMBER}; font-family: 'Public Sans', system-ui, sans-serif; color: {UMBER}">
<div style="position: relative; width: 1080px; height: 900px">
{SCENE}
<div style="position: absolute; top: 56px; left: 64px; display: flex; flex-direction: column; gap: 10px">
<h1 style="margin: 0; font-family: 'Big Shoulders Display', 'Public Sans', sans-serif; font-weight: 900; font-size: 230px; line-height: 0.8; letter-spacing: -0.01em; color: {UMBER}">To scale</h1>
<p style="margin: 0; font-size: 28px; color: {UMBER}">Four dinosaurs at their real lengths</p>
</div>
{"".join(figures)}
<p style="position: absolute; left: 64px; top: 318px; margin: 0; padding: 6px 12px; border-radius: 8px; background: rgba(243, 223, 194, 0.9); font-size: 17px; font-weight: 500; color: {UMBER}">Tap any dinosaur to see its move</p>
</div>
<div style="box-sizing: border-box; height: 450px; padding: 52px 64px 48px; display: flex; flex-direction: column; gap: 36px; color: {BUFF}">
<p style="margin: 0; font-size: 30px; line-height: 1.4; max-width: 900px">Shown side by side for size only. Stegosaurus lived about 155–150 million years ago, Patagotitan about 102 million, and T. rex and Triceratops 68–66 million.</p>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px">
{facts_html}
</div>
<p style="margin: 0; margin-top: auto; font-size: 18px; line-height: 1.5; color: {LABEL}">Lengths are estimates for large adults. Patagotitan is drawn at 34 m, the middle of its revised 31–37 m range.</p>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"animate":{{"editor":"boolean","default":true}},"$preview":{{"width":1080,"height":1350}}}}'>
class Component extends DCLogic {{
componentWillUnmount() {{ Object.values(this._t || {{}}).forEach(clearTimeout); }}
renderVals() {{
const animate = this.props.animate ?? true;
const st = this.state || {{}};
this._t = this._t || {{}};
const go = (key, ms) => () => {{
  clearTimeout(this._t[key]);
  this.setState({{ [key]: false }}, () => requestAnimationFrame(() => this.setState({{ [key]: true }})));
  this._t[key] = setTimeout(() => this.setState({{ [key]: false }}), ms);
}};
return {{
trexClass: (animate ? 'tr-anim' : '') + (st.trex ? ' tr-roaring' : ''),
triClass: (animate ? 'tri-anim' : '') + (st.tri ? ' tri-acting' : ''),
stgClass: (animate ? 'stg-anim' : '') + (st.stg ? ' stg-acting' : ''),
titClass: (animate ? 'tit-anim' : '') + (st.tit ? ' tit-acting' : ''),
trexAct: go('trex', 1700),
triAct: go('tri', {int(species["triceratops"]["dur"] * 1000) + 100}),
stgAct: go('stg', {int(species["stegosaurus"]["dur"] * 1000) + 100}),
titAct: go('tit', {int(species["titanosaur"]["dur"] * 1000) + 100})
}};
}}
}}
</script>
</body>
</html>
'''
pathlib.Path(HERE + "/project/Group.dc.html").write_text(HTML)
prev = HTML.replace('<script src="./support.js"></script>', "").replace("<helmet>", "").replace("</helmet>", "").replace("<x-dc>", "").replace("</x-dc>", "")
for h in ("trexClass", "triClass", "stgClass", "titClass"): prev = prev.replace("{{" + h + "}}", "")
prev = re.sub(r'onClick="\{\{[a-zA-Z]+\}\}"', "", prev)
prev = prev[:prev.index('<script type="text/x-dc"')] + "</body></html>"
pathlib.Path(HERE + "/shots/group-poster.html").write_text(prev)
print(json.dumps({k: {"span": round(v["right"] - v["left"]), "scale": round(scale_of(k), 3)} for k, v in M.items()}))
