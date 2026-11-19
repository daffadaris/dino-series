import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
"""Shared toolkit for the dinosaur series (T. rex style: outlines, stripes, pale belly,
gradient shading, scale texture, rim light). Each species module builds parts with these
helpers; write_all() emits the standalone SVG, GSAP page, poster board and rig board."""
import json, math, pathlib, random, re
from matplotlib.path import Path as MPath

OL, D, L = "#2A1C22", "#000000", "#FFFFFF"
CLAW, EYE, IVORY = "#3A2A2C", "#E0B04A", "#EFE6D0"
SKIN = "SKIN"          # placeholder, replaced by a colour or {{skin}}
OUT = pathlib.Path(HERE)

# ------------------------------------------------------------------ primitives
def piv(gid, cls, x, y, inner):
    ident = f' id="{gid}"' if gid else ""
    return f'<g transform="translate({x} {y})"><g{ident} class="{cls}"><g transform="translate({-x} {-y})">{inner}</g></g></g>'

def path(d, fill, op=None, extra=""):
    o = f' opacity="{op}"' if op is not None else ""
    return f'<path d="{d}" fill="{fill}"{o}{extra}></path>'

def stroke(d, w=3, color=OL, op=None):
    o = f' opacity="{op}"' if op is not None else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{o}></path>'

def line(d, op, w=2.2):
    return stroke(d, w, D, op)

def rim(d, w=3.6, dy=3.8, op=0.6):
    return f'<path d="{d}" fill="none" stroke="#FFE4C0" stroke-width="{w}" stroke-linecap="round" opacity="{op}" transform="translate(0 {dy})"></path>'

def stripe(x, y, ln, w=14):
    return f'<path d="M{x} {y} L{x+w} {y+1} L{x+w*0.45:.0f} {y+ln} L{x+w*0.1:.0f} {y+ln*0.9:.0f} Z"></path>'

def stripes(spec, op=0.3):
    return f'<g fill="{D}" opacity="{op}">' + "".join(stripe(*s) for s in spec) + "</g>"

def scatter(poly, n, rmin, rmax, seed=3):
    rnd = random.Random(seed + n); p = MPath(poly); xs = [a for a, _ in poly]; ys = [b for _, b in poly]; out = []
    while len(out) < n:
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        if p.contains_point((x, y)): out.append((round(x, 1), round(y, 1), round(rnd.uniform(rmin, rmax), 1)))
    return out

def spots(poly, n, rmin, rmax, op=0.14, seed=3):
    rnd = random.Random(seed)
    return f'<g fill="{D}" opacity="{op}">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{r*1.8:.1f}" ry="{r:.1f}" transform="rotate({rnd.randint(-25, 25)} {x} {y})"></ellipse>'
        for x, y, r in scatter(poly, n, rmin, rmax, seed)) + "</g>"

def dots(poly, n, rmin=0.8, rmax=1.6, op=0.1, seed=5):
    return f'<g fill="{D}" opacity="{op}">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x, y, r in scatter(poly, n, rmin, rmax, seed)) + "</g>"

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0], u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])

def plate(x, y, w, h, lean=-8):
    """kite-shaped stegosaur plate standing on (x, y)"""
    return (f"M{x-w*0.3:.1f} {y} C{x-w*0.7:.1f} {y-h*0.35:.1f} {x+lean-w*0.55:.1f} {y-h*0.8:.1f} {x+lean:.1f} {y-h:.1f} "
            f"C{x+lean+w*0.55:.1f} {y-h*0.8:.1f} {x+w*0.7:.1f} {y-h*0.35:.1f} {x+w*0.3:.1f} {y} Z")

def spike(bx, by, tx, ty, w):
    mx, my = (bx + tx) / 2, (by + ty) / 2
    return f"M{bx-w} {by+2} Q{bx-w*0.3:.1f} {my:.1f} {tx} {ty} Q{bx+w*0.7:.1f} {my:.1f} {bx+w} {by+2} Z"

class Look:
    """per-species palette and gradient ids"""
    def __init__(self, code, skin, belly, accent=None):
        self.code, self.skin, self.belly, self.accent = code, skin, belly, accent or skin
    def id(self, name): return f"{self.code}-{name}"
    def url(self, name): return f"url(#{self.id(name)})"
    def defs(self):
        c = self.code
        return f'''<defs>
<linearGradient id="{c}-shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF0D8" stop-opacity="0.3"></stop><stop offset="0.32" stop-color="#FFF0D8" stop-opacity="0"></stop><stop offset="0.66" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#000000" stop-opacity="0.4"></stop></linearGradient>
<linearGradient id="{c}-ao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0.02"></stop><stop offset="1" stop-color="#000000" stop-opacity="0.32"></stop></linearGradient>
<linearGradient id="{c}-fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000000" stop-opacity="0.2"></stop><stop offset="0.55" stop-color="#000000" stop-opacity="0"></stop></linearGradient>
<radialGradient id="{c}-light" cx="0.4" cy="0.28" r="0.62"><stop offset="0" stop-color="#FFF0D8" stop-opacity="0.4"></stop><stop offset="1" stop-color="#FFF0D8" stop-opacity="0"></stop></radialGradient>
<pattern id="{c}-scales" patternUnits="userSpaceOnUse" width="7" height="12"><circle cx="3.5" cy="3" r="2.6" fill="none" stroke="#000000" stroke-width="0.6"></circle><circle cx="0" cy="9" r="2.6" fill="none" stroke="#000000" stroke-width="0.6"></circle><circle cx="7" cy="9" r="2.6" fill="none" stroke="#000000" stroke-width="0.6"></circle></pattern>
</defs>'''

def skin_part(look, d, *, belly=None, layers="", outline=True, outline_d=None, light=False, ao=False, fade=False, rim_d=None, far=False, tex=True):
    """a silhouette with the series' standard layers; returns markup in draw order"""
    out = [path(d, SKIN)]
    if belly: out.append(path(belly, look.belly))
    out.append(layers)
    if tex: out.append(path(d, look.url("scales"), 0.2))
    out.append(path(d, look.url("shade")))
    if light: out.append(path(d, look.url("light")))
    if ao: out.append(path(d, look.url("ao")))
    if fade: out.append(path(d, look.url("fade")))
    if rim_d: out.append(rim(rim_d))
    if far: out.append(path(d, D, 0.32))
    if outline: out.append(stroke(outline_d or d))
    return "".join(out)

def eye(cx, cy, cls, r=5.5):
    lid = f'<ellipse cx="{cx}" cy="{cy}" rx="{r+1.2}" ry="{r+0.8}" fill="{SKIN}"></ellipse>'
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{r+3}" ry="{r+2.2}" fill="{D}" opacity="0.36"></ellipse>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.93:.1f}" fill="{EYE}"></ellipse>'
            f'<circle cx="{cx+0.4}" cy="{cy}" r="{r*0.5:.1f}" fill="#15110D"></circle>'
            f'<circle cx="{cx+1.6}" cy="{cy-1.4}" r="1" fill="{L}"></circle>'
            + piv("", cls, cx, cy, lid))

# ------------------------------------------------------------------ motion
def keyframes(name, frames, loop=None):
    """frames: [(t 0..1, css)]; loop=(start, span) remaps into a longer idle cycle"""
    if loop:
        s, span = loop
        frames = [(0, frames[0][1])] + [(s + t * span, v) for t, v in frames] + [(1, frames[-1][1])]
    body = "".join(f"{t*100:.1f}%{{{v}}}" for t, v in frames)
    return f"@keyframes {name}{{{body}}}"

def motion_css(code, idle_parts, action, dur):
    """idle_parts: classes that breathe/sway; action: {part_class: [(t, css)]}"""
    c = code
    css = [f".{c}-{p}{{transform-origin:0 0}}" for p in ("act", "body", "tail", "head", "jaw", "neck", "flush")]
    css.append(f".{c}-eyelid{{transform-origin:0 0;transform:scaleY(0)}}")
    css.append(f".{c}-flush{{opacity:0}}")
    css += [f".{c}-anim .{c}-body{{animation:{c}-breath 3.4s ease-in-out infinite}}",
            f".{c}-anim .{c}-tail{{animation:{c}-sway 5s ease-in-out infinite}}",
            f".{c}-anim .{c}-eyelid{{animation:{c}-blink 5.5s linear infinite}}",
            f"@keyframes {c}-breath{{0%,100%{{transform:scale(1,1)}}50%{{transform:scale(1.005,1.014)}}}}",
            f"@keyframes {c}-sway{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(-1.4deg)}}}}",
            f"@keyframes {c}-blink{{0%,93%,100%{{transform:scaleY(0)}}95.5%{{transform:scaleY(1)}}}}"]
    click, loop = [], []
    for part, frames in action.items():
        prop = "opacity" if part == "flush" else "transform"
        fr = [(t, f"{prop}:{v}") for t, v in frames]
        click += [keyframes(f"{c}-do-{part}", fr), f".{c}-acting .{c}-{part}{{animation:{c}-do-{part} {dur}s cubic-bezier(.3,.7,.2,1)}}"]
        loop += [keyframes(f"{c}-loop-{part}", fr, loop=(0.55, 0.4)), f".{c}-anim.{c}-loop .{c}-{part}{{animation:{c}-loop-{part} {dur/0.4:.2f}s cubic-bezier(.3,.7,.2,1) infinite}}"]
    tail = [f"@media (prefers-reduced-motion: reduce){{.{c}-anim *,.{c}-acting *{{animation:none !important}}}}"]
    return "\n".join(css + click), "\n".join(css + loop + tail), "\n".join(tail)

# ------------------------------------------------------------------ outputs
def write_all(sp):
    """sp: dict built by a species module"""
    c, look = sp["code"], sp["look"]
    vb_w, vb_h = sp["viewbox"]
    frag = look.defs() + sp["frag"]
    css_click, css_loop, css_rm = motion_css(c, None, sp["action"], sp["dur"])

    # standalone animated SVG: idle loop with the signature move every few seconds
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" class="{c}-anim {c}-loop" role="img" aria-label="Animated {sp['name']}">
<title>{sp['name']} (animatable)</title>
<!-- Groups you can animate: {", ".join("#" + i for i in sp["ids"])}, .{c}-eyelid
     Each moving group sits inside a wrapper whose origin is its joint: rotate/scale with transform-origin 0 0
     (GSAP: svgOrigin "0 0"). Remove the {c}-anim class on the root to stop the built-in loop. -->
<style>
{css_loop}
</style>
{frag.replace(SKIN, look.skin)}
</svg>
'''
    (OUT / f"{sp['slug']}-animated.svg").write_text(svg)

    # GSAP page
    gsap_page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{sp['name']}: GSAP animation</title>
<style>
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: {sp['page_bg']}; font-family: system-ui, sans-serif; color: #2B1E16; }}
  main {{ width: min(1000px, 100%); padding: 24px; box-sizing: border-box; }}
  button {{ all: unset; display: block; width: 100%; cursor: pointer; border-radius: 12px; }}
  button:focus-visible {{ outline: 3px solid #2B1E16; outline-offset: 4px; }}
  svg {{ display: block; width: 100%; height: auto; }}
  p {{ margin: 12px 0 0; font-size: 16px; }}
  .{c}-eyelid {{ transform: scaleY(0); }}
</style>
</head>
<body>
<main>
  <button type="button" id="dino" aria-label="{sp['action_label']}">
    <svg viewBox="0 0 {vb_w} {vb_h}" aria-hidden="true">
{frag.replace(SKIN, look.skin)}
    </svg>
  </button>
  <p>Click or tap the {sp['short']}, or press Enter, to {sp['action_verb']}.</p>
</main>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>
  const q = (s) => document.querySelector(s);
  const parts = {{ {", ".join(f"{k.replace('-', '_')}: q('#{k}')" for k in sp["ids"])}, lid: document.querySelectorAll('.{c}-eyelid') }};
  gsap.set(Object.values(parts).filter(p => p && !(p instanceof NodeList)), {{ svgOrigin: '0 0' }});
  gsap.set(parts.lid, {{ svgOrigin: '0 0', scaleY: 0 }});
  const mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', () => {{
    gsap.to(parts.body, {{ scaleY: 1.014, scaleX: 1.005, duration: 1.7, ease: 'sine.inOut', yoyo: true, repeat: -1 }});
    const tailIdle = gsap.to(parts.tail, {{ rotation: -1.4, duration: 2.5, ease: 'sine.inOut', yoyo: true, repeat: -1 }});
    gsap.timeline({{ repeat: -1, repeatDelay: 4.5 }})
      .to(parts.lid, {{ scaleY: 1, duration: 0.08, ease: 'power1.in' }})
      .to(parts.lid, {{ scaleY: 0, duration: 0.12, ease: 'power1.out' }});
    const act = gsap.timeline({{ paused: true }})
{sp['gsap']};
    // the idle tail sway would fight any move that also turns the tail: pause it while the move plays
    act.eventCallback('onStart', () => tailIdle.pause());
    act.eventCallback('onComplete', () => tailIdle.resume());
    const play = () => act.restart();
    q('#dino').addEventListener('click', play);
    return () => q('#dino').removeEventListener('click', play);
  }});
</script>
</body>
</html>
'''
    (OUT / f"{sp['slug']}-gsap.html").write_text(gsap_page)
    sp["css_click"] = css_click
    return frag

# ------------------------------------------------------------------ canvas boards (poster + rig), same series layout as the T. rex poster
BUFF, LABEL, UMBER = "#E5C895", "#CDB894", "#2B1E16"

def poster_board(sp, frag):
    """sp keys used: code, name, title, title_px, binomial, subtitle, scene (svg markup 1080x900),
    dino_top, viewbox, paragraph, facts [(num, label)x3], footer, hint, action_label, skin_swatches"""
    c, look = sp["code"], sp["look"]
    vb_w, vb_h = sp["viewbox"]; h = round(1080 * vb_h / vb_w)
    facts = "\n".join(f'''<div style="display: flex; flex-direction: column; gap: 4px">
<span style="font-family: 'Big Shoulders Display', 'Public Sans', sans-serif; font-weight: 800; font-size: 80px; line-height: 0.95; color: {BUFF}">{n}</span>
<span style="font-size: 20px; color: {LABEL}">{l}</span>
</div>''' for n, l in sp["facts"])
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{sp['name']} poster</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&amp;family=Public+Sans:ital,wght@0,400;0,500;1,400&amp;display=swap">
<style>
body{{margin:0}}
a{{color:{UMBER}}}a:hover{{color:#000}}
.{c}-btn:focus-visible{{outline:3px solid {UMBER};outline-offset:-6px;border-radius:12px}}
{sp['css_click']}
</style>
</helmet>
<div style="width: 1080px; height: 1350px; position: relative; overflow: hidden; background: {UMBER}; font-family: 'Public Sans', system-ui, sans-serif; color: {UMBER}">
<div style="position: relative; width: 1080px; height: 900px">
{sp['scene']}
<div style="position: absolute; top: 56px; left: 64px; display: flex; flex-direction: column; gap: 10px">
<h1 style="margin: 0; font-family: 'Big Shoulders Display', 'Public Sans', sans-serif; font-weight: 900; font-size: {sp['title_px']}px; line-height: 0.8; padding-bottom: 0.14em; letter-spacing: -0.01em; color: {UMBER}">{sp['title']}</h1>
<p style="margin: 0; font-size: 28px; color: {UMBER}"><em>{sp['binomial']}</em>, {sp['subtitle']}</p>
</div>
<button type="button" class="{c}-btn" aria-label="{sp['action_label']}" onClick="{{{{act}}}}" style="position: absolute; top: {sp['dino_top']}px; left: 0; width: 1080px; height: {h}px; padding: 0; margin: 0; border: 0; background: none; cursor: pointer; display: block">
<svg class="{{{{animClass}}}}" aria-hidden="true" viewBox="0 0 {vb_w} {vb_h}" width="1080" height="{h}" style="display: block">
{frag.replace(SKIN, "{{skin}}")}
</svg>
</button>
<p style="position: absolute; right: 56px; bottom: 20px; margin: 0; padding: 6px 12px; border-radius: 8px; background: rgba(243, 223, 194, 0.9); font-size: 17px; font-weight: 500; color: {UMBER}">{sp['hint']}</p>
</div>
<div style="box-sizing: border-box; height: 450px; padding: 52px 64px 48px; display: flex; flex-direction: column; gap: 36px; color: {BUFF}">
<p style="margin: 0; font-size: 30px; line-height: 1.4; max-width: 880px">{sp['paragraph']}</p>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px">
{facts}
</div>
<p style="margin: 0; margin-top: auto; font-size: 18px; line-height: 1.5; color: {LABEL}">{sp['footer']}</p>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"animate":{{"editor":"boolean","default":true}},"skin":{{"editor":"color","default":"{look.skin}","options":{json.dumps(sp['skin_swatches'])}}},"$preview":{{"width":1080,"height":1350}}}}'>
class Component extends DCLogic {{
componentWillUnmount() {{ clearTimeout(this._t); }}
renderVals() {{
const animate = this.props.animate ?? true;
const acting = this.state && this.state.acting;
return {{
skin: this.props.skin ?? '{look.skin}',
animClass: (animate ? '{c}-anim' : '') + (acting ? ' {c}-acting' : ''),
act: () => {{
clearTimeout(this._t);
this.setState({{ acting: false }}, () => requestAnimationFrame(() => this.setState({{ acting: true }})));
this._t = setTimeout(() => this.setState({{ acting: false }}), {int(sp['dur'] * 1000) + 100});
}}
}};
}}
}}
</script>
</body>
</html>
'''
    (OUT / "project" / f"{sp['board']}.dc.html").write_text(html)
    preview(html, f"{sp['slug']}-poster", look.skin)
    return html

def rig_board(sp, frag, S=0.8):
    """sp['rig_parts']: [(label, ids, markup, (x, y, w, h))]"""
    c, look = sp["code"], sp["look"]
    vb_w, vb_h = sp["viewbox"]
    sk = lambda m: m.replace(SKIN, "{{skin}}")
    def part_svg(markup, vb, label):
        x, y, w, h = vb
        return f'<svg role="img" aria-label="{label}" viewBox="{x} {y} {w} {h}" width="{w*S:.0f}" height="{h*S:.0f}" style="display: block">{sk(markup)}</svg>'
    items = "".join(f'''<div style="display: flex; flex-direction: column; gap: 14px; align-items: flex-start">{part_svg(m, vb, n)}<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 17px; font-weight: 600; color: #ECE6E8">{n}</span><span style="font-size: 14px; color: #B9B3B6">{ids}</span></div></div>''' for n, ids, m, vb in sp["rig_parts"])
    big_h = 560 * vb_h / vb_w * 1000 / 560
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{sp['name']} rig sheet</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600&amp;display=swap">
<style>
body{{margin:0}}
a{{color:#ECE6E8}}a:hover{{color:#FFFFFF}}
.{c}-eyelid{{transform-origin:0 0;transform:scaleY(0)}}
.{c}-flush{{opacity:0}}
</style>
</helmet>
<div style="width: 1700px; height: {sp.get('rig_h', 960)}px; box-sizing: border-box; padding: 40px 56px; background: #3E3E40; font-family: 'Public Sans', system-ui, sans-serif; color: #ECE6E8; display: flex; flex-direction: column; gap: 28px">
<div style="display: flex; justify-content: space-between; align-items: flex-start">
<div style="display: flex; flex-direction: column; gap: 6px; max-width: 420px">
<h1 style="margin: 0; font-size: 34px; font-weight: 600">{sp['name']} rig</h1>
<p style="margin: 0; font-size: 17px; line-height: 1.5; color: #B9B3B6">Each part is its own group in the SVG, pivoting at its joint. Overlapping ends stay hidden when the parts are assembled.</p>
</div>
<svg role="img" aria-label="Assembled {sp['name']}" viewBox="0 0 {vb_w} {vb_h}" width="1000" height="{big_h:.0f}" style="display: block; margin-top: -24px">
{sk(frag)}
</svg>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: auto">
{items}
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"skin":{{"editor":"color","default":"{look.skin}","options":{json.dumps(sp['skin_swatches'])}}},"$preview":{{"width":1700,"height":{sp.get('rig_h', 960)}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{ skin: this.props.skin ?? '{look.skin}' }}; }}
}}
</script>
</body>
</html>
'''
    (OUT / "project" / f"{sp['board']}Rig.dc.html").write_text(html)
    preview(html, f"{sp['slug']}-rig", look.skin)
    return html

def preview(html, name, skin):
    """plain-HTML copy with template holes filled, for local screenshots"""
    p = (html.replace('<script src="./support.js"></script>', "").replace("<helmet>", "").replace("</helmet>", "")
         .replace("<x-dc>", "").replace("</x-dc>", "").replace("{{skin}}", skin).replace("{{animClass}}", "")
         .replace('onClick="{{act}}"', ""))
    p = p[:p.index('<script type="text/x-dc"')] + "</body></html>"
    (OUT / "shots" / f"{name}.html").write_text(p)

def shoot(name, w, h, out=None):
    """screenshot a preview or file into shots/"""
    import subprocess
    src = OUT / "shots" / f"{name}.html" if not name.endswith(".svg") else OUT / name
    out = out or (OUT / "shots" / f"{pathlib.Path(name).stem}.png")
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    "--virtual-time-budget=3000", "--default-background-color=C9D6DAFF", f"--screenshot={out}", f"file://{src}"],
                   capture_output=True)
    return out
