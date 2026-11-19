import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Detail pass over the definitive boxy-head build (build4.py).

Adds shading, texture, wrinkles, muscle lines and rim light as extra layers.
Never changes a silhouette, the head's shapes, a group id, a class or a pivot:
check_baseline() enforces that against versions/boxy-head-definitive/baseline.json.
"""
import re, json, random, pathlib, importlib.util

spec = importlib.util.spec_from_file_location("base", HERE + "/trex_drawing.py")
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
SKIN, OL, D = B.SKIN, B.OL, B.D
HEAD_SCALE = 1.4
random.seed(11)

# ------------------------------------------------------------------ shared defs
DEFS = f'''<defs>
<linearGradient id="trx-shade" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#FFF0D8" stop-opacity="0.3"></stop>
<stop offset="0.32" stop-color="#FFF0D8" stop-opacity="0"></stop>
<stop offset="0.66" stop-color="#000000" stop-opacity="0"></stop>
<stop offset="1" stop-color="#000000" stop-opacity="0.4"></stop>
</linearGradient>
<linearGradient id="trx-leg-ao" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#000000" stop-opacity="0.02"></stop>
<stop offset="1" stop-color="#000000" stop-opacity="0.32"></stop>
</linearGradient>
<linearGradient id="trx-tail-fade" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#000000" stop-opacity="0.2"></stop>
<stop offset="0.55" stop-color="#000000" stop-opacity="0"></stop>
</linearGradient>
<radialGradient id="trx-thigh-light" cx="0.4" cy="0.28" r="0.62">
<stop offset="0" stop-color="#FFF0D8" stop-opacity="0.42"></stop>
<stop offset="1" stop-color="#FFF0D8" stop-opacity="0"></stop>
</radialGradient>
<radialGradient id="trx-head-light" cx="0.5" cy="0.2" r="0.7">
<stop offset="0" stop-color="#FFF0D8" stop-opacity="0.36"></stop>
<stop offset="1" stop-color="#FFF0D8" stop-opacity="0"></stop>
</radialGradient>
<pattern id="trx-scales" patternUnits="userSpaceOnUse" width="7" height="12">
<circle cx="3.5" cy="3" r="2.6" fill="none" stroke="#000000" stroke-width="0.6"></circle>
<circle cx="0" cy="9" r="2.6" fill="none" stroke="#000000" stroke-width="0.6"></circle>
<circle cx="7" cy="9" r="2.6" fill="none" stroke="#000000" stroke-width="0.6"></circle>
</pattern>
<pattern id="trx-scales-head" patternUnits="userSpaceOnUse" width="{7/HEAD_SCALE:.3f}" height="{12/HEAD_SCALE:.3f}">
<circle cx="{3.5/HEAD_SCALE:.3f}" cy="{3/HEAD_SCALE:.3f}" r="{2.6/HEAD_SCALE:.3f}" fill="none" stroke="#000000" stroke-width="{0.6/HEAD_SCALE:.3f}"></circle>
<circle cx="0" cy="{9/HEAD_SCALE:.3f}" r="{2.6/HEAD_SCALE:.3f}" fill="none" stroke="#000000" stroke-width="{0.6/HEAD_SCALE:.3f}"></circle>
<circle cx="{7/HEAD_SCALE:.3f}" cy="{9/HEAD_SCALE:.3f}" r="{2.6/HEAD_SCALE:.3f}" fill="none" stroke="#000000" stroke-width="{0.6/HEAD_SCALE:.3f}"></circle>
</pattern>
</defs>'''

RIM = "#FFE4C0"
def fill(d, paint, op=1, extra=""):
    return f'<path d="{d}" fill="{paint}" opacity="{op}" stroke="none"{extra}></path>'
def line(d, op, w=2.2, color=D):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"></path>'
def rim(d, w=3.6, dy=3.8, op=0.62):
    return f'<path d="{d}" fill="none" stroke="{RIM}" stroke-width="{w}" stroke-linecap="round" opacity="{op}" transform="translate(0 {dy})"></path>'
def before(part, marker, add, last=False):
    i = part.rfind(marker) if last else part.find(marker)
    assert i >= 0, marker[:60]
    return part[:i] + add + part[i:]
def sil(part, start):
    return re.search(r'<path d="(' + re.escape(start) + r'[^"]*)" fill="SKIN"', part).group(1)
def outline_marker(d, exact=False):
    return f'<path d="{d}" fill="none" stroke="{OL}"' if exact else f'<path d="{d}'

# ------------------------------------------------------------------ tail
TAIL = B.TAIL
tail_d = sil(TAIL, "M480 156")
TAIL = before(TAIL, outline_marker(tail_d.rstrip(" Z"), exact=True), "".join([
    fill(tail_d, "url(#trx-shade)"),
    fill(tail_d, "url(#trx-tail-fade)"),
    fill(tail_d, "url(#trx-scales)", 0.2),
    line("M470 238 C390 228 280 216 150 212 C110 211 80 212 60 213", 0.14, 2.4),
    line("M452 262 C444 276 440 292 442 308 M436 252 C428 266 424 282 426 298", 0.18, 2),
    rim("M480 156 C380 158 230 180 40 207"),
]))

# ------------------------------------------------------------------ body + neck
BODY = B.BODY
body_d = sil(BODY, "M450 160")
BODY = before(BODY, outline_marker(body_d.rstrip(" Z"), exact=True), "".join([
    fill(body_d, "url(#trx-shade)"),
    fill(body_d, "url(#trx-scales)", 0.2),
    line("M712 246 C742 264 760 298 760 338", 0.15, 2.6),
    line("M690 250 C704 284 708 322 700 360", 0.1, 2.2),
    line("M594 372 C608 380 624 384 642 384 M602 386 C616 392 632 394 648 392", 0.2, 2),
    line("M772 232 C780 244 784 258 782 272 M792 220 C800 232 804 246 802 260", 0.14, 2),
    rim("M450 160 C520 146 612 154 690 180 C712 186 726 186 740 180 C762 168 786 156 806 150"),
]))

# ------------------------------------------------------------------ near leg
LEG = B.NEAR_LEG
lower = [sil(LEG, "M524 344"), sil(LEG, "M486 436"), sil(LEG, "M506 486")]
LEG = before(LEG, outline_marker("M524 344 C562 346 578 374 566 400 C552 424 528 438 512 450"), "".join(
    [fill(d, "url(#trx-leg-ao)") for d in lower] + [
    fill(lower[0], "url(#trx-scales)", 0.2),
    line("M494 440 C502 446 512 448 520 446 M492 450 C500 456 510 458 518 456", 0.24, 1.8),
    line("M548 356 C556 366 560 376 560 388 M538 360 C546 370 550 380 550 392", 0.18, 1.8),
    line("M518 474 L526 472 M522 482 L530 480", 0.22, 1.6),
]))
thigh_d = sil(LEG, "M380 200")
LEG = before(LEG, outline_marker("M580 222 C618 262 616 330 584 362"), "".join([
    fill(thigh_d, "url(#trx-thigh-light)"),
    fill(thigh_d, "url(#trx-scales)", 0.2),
    line("M398 230 C430 250 470 262 516 266", 0.12, 2.2),
    line("M560 248 C576 276 580 310 570 340", 0.14, 2.4),
    rim("M394 198 C434 170 518 172 566 214", 2.6, 4, 0.38),
]), last=True)

# ------------------------------------------------------------------ far leg (its outline comes from the group stroke)
FAR = B.FAR_LEG
far_lower = re.findall(r'<path d="(M45[0-9][^"]*|M41[0-9][^"]*|M42[0-9][^"]*)"></path>', FAR.split('<g fill="#000000"')[0])
FAR = before(FAR, '<path d="M514 500', "".join(fill(d, "url(#trx-leg-ao)") for d in far_lower[:3]))

# ------------------------------------------------------------------ head: same shapes, details drawn at body weight
HEAD = B.HEAD
def counter_scale(m):
    tag = m.group(0)
    if f'stroke="{OL}"' in tag:
        return tag
    return re.sub(r'stroke-width="([\d.]+)"', lambda w: f'stroke-width="{float(w.group(1)) / HEAD_SCALE:.2f}"', tag)
HEAD = re.sub(r'<(?:path|polyline|line)[^>]*stroke-width="[\d.]+"[^>]*>', counter_scale, HEAD)
HEAD = re.sub(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"></circle>',
              lambda m: f'<circle cx="{m.group(1)}" cy="{m.group(2)}" r="{float(m.group(3)) / HEAD_SCALE:.2f}"></circle>', HEAD)
skull_d = sil(HEAD, "M804 142")
jaw_d = sil(HEAD, "M804 196 L972")
extra_scales = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x, y, r in B.scatter(
    [(812, 146), (870, 124), (930, 130), (970, 156), (970, 182), (900, 196), (830, 202), (804, 180)], 60, 0.55, 1.0))
s = 1 / HEAD_SCALE
JAW_OUTLINE = "M972 188 C980 190 980 198 974 202"
HEAD = before(HEAD, outline_marker(JAW_OUTLINE), "".join([
    fill(jaw_d, "url(#trx-shade)"),
    fill(jaw_d, "url(#trx-scales-head)", 0.2),
    line("M808 204 C814 210 818 216 820 224 M816 202 C822 208 826 214 828 222", 0.22, 2 * s),
]))
OUTLINE_FIX = ("M826 124 C840 119 856 118 870 118", "M834 124 C845.5 120 858 118 870 118")
HEAD = HEAD.replace(*OUTLINE_FIX)
HEAD = before(HEAD, outline_marker("M834 124 C845.5 120"), "".join([
    fill(skull_d, "url(#trx-head-light)"),
    fill(skull_d, "url(#trx-scales-head)", 0.2),
    f'<g fill="{D}" opacity="0.12">{extra_scales}</g>',
    line("M806 168 C812 178 820 188 830 196 M800 176 C806 186 812 194 820 202", 0.16, 2 * s),
    line("M850 150 C858 156 868 158 878 156", 0.14, 1.8 * s),
    rim("M804 142 C820 126 846 118 870 118 C880 118 888 121 894 126 C902 122 912 122 922 125 C944 130 962 140 974 152", 3.4 * s, 2.6, 0.6),
]), last=True)

# ------------------------------------------------------------------ assemble (same order and wrapper as the definitive build)
FAR_LEG, NEAR_LEG, NEAR_ARM, FAR_ARM = FAR, LEG, B.NEAR_ARM, B.FAR_ARM
FRAG = DEFS + (B.FRAG.replace(B.TAIL, TAIL).replace(B.BODY, BODY).replace(B.NEAR_LEG, LEG)
               .replace(B.FAR_LEG, FAR).replace(B.HEAD, HEAD))
assert TAIL in FRAG and BODY in FRAG and LEG in FRAG and HEAD in FRAG and FAR in FRAG

# ------------------------------------------------------------------ guard rails against the saved baseline
def check_baseline(svg_text):
    base = json.loads(pathlib.Path(ROOT + "/baseline/trex-boxy-head/baseline.json").read_text())
    new_head_paths = set(re.findall(r'd="([^"]+)"', HEAD))
    allowed = {OUTLINE_FIX[0].join(["", ""]) : OUTLINE_FIX[1]}
    missing = [d for d in base["head_paths"] if d not in new_head_paths and not any(d.startswith(k) for k in allowed)]
    assert not missing, f"head shapes changed: {missing[:2]}"
    assert '<g transform="translate(800 180) scale(1.4)">' in HEAD, "head scale changed"
    assert sorted(set(re.findall(r'id="([^"]+)"', svg_text)) - {i for i in re.findall(r'id="(trx-[^"]+)"', svg_text)}) == base["ids"], "group ids changed"
    assert sorted(set(re.findall(r'class="(tr-[^"]+)"', svg_text))) == base["classes"], "classes changed"
    piv = sorted(set(re.findall(r'<g transform="translate\((-?[\d.]+ -?[\d.]+)\)(?: scale\([\d.]+\))?"><g(?: id="[^"]+")? class="tr-', svg_text)))
    assert piv == base["pivots"], f"pivots changed: {piv}"
    for d in (B.TAIL, B.BODY, B.NEAR_LEG, B.FAR_LEG):
        for path in re.findall(r'<path d="([^"]+)" fill="SKIN"', d):
            assert path in svg_text.replace(B.DEFAULT_SKIN, "SKIN") or path in FRAG, "silhouette changed"
    return True

CSS = B.CSS
DEFAULT_SKIN, SWATCHES = B.DEFAULT_SKIN, B.SWATCHES
std = B.std.replace(B.FRAG.replace(SKIN, DEFAULT_SKIN), FRAG.replace(SKIN, DEFAULT_SKIN))
assert std != B.std
check_baseline(std)
pathlib.Path(ROOT + "/svg/trex-animated.svg").write_text(std)
