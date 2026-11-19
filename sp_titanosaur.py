import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
"""Titanosaur (Patagotitan mayorum) for the dinosaur series. Import has no side effects;
run as a script to write the SVG, GSAP page, poster board and rig board."""
import sys
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, D, L, OL, CLAW, path, stroke, line, rim, stripes, spots, dots, skin_part, piv, bez

C = "tit"
LOOK = K.Look(C, skin="#7C8AA0", belly="#D8D2C2")

# ------------------------------------------------------------------ legs (columnar, padded feet)
HIND = "M300 380 C340 350 400 356 416 400 C428 440 420 480 404 500 L406 620 C408 640 400 650 386 650 L338 650 C326 650 322 640 324 628 L326 500 C304 470 292 420 300 380 Z"
HIND_FOOT = "M316 634 C326 624 404 624 418 634 C424 640 422 650 414 650 L322 650 C312 650 310 640 316 634 Z"
HIND_NAILS = "M408 637 C415 637 420 642 419 648 C414 646 410 645 406 645 Z M396 639 C402 639 406 643 405 648 C401 646 398 646 395 646 Z"
FORE = "M600 380 C636 362 690 372 698 412 C704 450 692 490 680 504 L682 620 C684 640 676 650 662 650 L618 650 C606 650 602 640 604 628 L606 500 C590 470 588 410 600 380 Z"
FORE_FOOT = "M596 634 C606 624 678 624 690 634 C696 640 694 650 686 650 L602 650 C594 650 590 640 596 634 Z"

def leg(gid, d, foot, nails=None, far=False, dx=0):
    inner = []
    if far:
        inner.append(f'<g fill="{SKIN}" stroke="{OL}" stroke-width="3" stroke-linejoin="round">{path(d, SKIN)}{path(foot, SKIN)}</g>')
        inner.append(f'<g fill="{D}" opacity="0.34">{path(d, D)}{path(foot, D)}</g>')
        if nails: inner.append(path(nails, CLAW, 0.85))
    else:
        inner.append(skin_part(LOOK, d, ao=True, layers=dots([(310, 390), (410, 400), (404, 600), (330, 600)] if "M300" in d else [(606, 390), (694, 412), (680, 600), (610, 600)], 40, 0.8, 1.5, 0.1)))
        inner.append(line("M330 500 C350 506 380 506 402 500 M330 520 C352 526 380 526 402 520" if "M300" in d else "M608 500 C628 506 656 506 680 500 M608 520 C630 526 656 526 680 520", 0.18, 2))
        inner.append(skin_part(LOOK, foot, tex=False))
        inner.append(line("M346 636 L346 650 M372 636 L372 650" if "M300" in d else "M626 636 L626 650 M652 636 L652 650", 0.28, 2))
        if nails: inner.append(path(nails, CLAW))
    t = f' transform="translate({dx} -2)"' if dx else ""
    return f'<g id="{gid}"{t}>{"".join(inner)}</g>'

LEG_FAR = leg("leg-far", HIND, HIND_FOOT, HIND_NAILS, far=True, dx=44)
FORELEG_FAR = leg("foreleg-far", FORE, FORE_FOOT, far=True, dx=40)
LEG_NEAR = leg("leg-near", HIND, HIND_FOOT, HIND_NAILS)
FORELEG_NEAR = leg("foreleg-near", FORE, FORE_FOOT)

# ------------------------------------------------------------------ tail
TAIL_D = "M300 330 C220 336 120 366 24 418 C14 424 16 434 26 434 C120 408 226 396 306 424 Z"
TAIL = piv("tail", f"{C}-tail", 300, 380, skin_part(
    LOOK, TAIL_D,
    belly="M26 434 C120 408 226 396 306 424 L306 406 C226 380 120 394 32 426 Z",
    layers=path("M300 330 C220 336 120 366 24 418 C20 420 20 422 24 422 C120 374 220 350 300 348 Z", D, 0.26)
           + stripes([(80, 392, 10, 8), (140, 366, 14, 10), (196, 350, 20, 12), (250, 340, 24, 13)])
           + dots([(40, 420), (300, 336), (300, 410), (120, 404)], 60)
           + line("M296 370 C230 372 150 390 60 420", 0.12, 2.2),
    fade=True, rim_d="M300 330 C220 336 120 366 24 418",
    outline_d="M300 330 C220 336 120 366 24 418 C14 424 16 434 26 434 C120 408 226 396 306 424"))

# ------------------------------------------------------------------ body (with osteoderms)
BODY_D = "M262 330 C320 268 440 250 540 262 C620 272 680 300 720 340 C750 370 756 420 730 456 C700 494 620 512 520 512 C420 512 330 494 290 460 C254 430 242 370 262 330 Z"
BODY_POLY = [(280, 340), (540, 270), (710, 340), (730, 440), (520, 500), (300, 460)]
osteo = "".join(
    f'<ellipse cx="{x}" cy="{y}" rx="{r*1.6:.1f}" ry="{r:.1f}" fill="{SKIN}" stroke="{OL}" stroke-width="1.4"></ellipse>'
    f'<ellipse cx="{x}" cy="{y}" rx="{r*1.6:.1f}" ry="{r:.1f}" fill="{D}" opacity="0.2"></ellipse>'
    f'<path d="M{x-r} {y-r*0.3:.1f} C{x-r*0.4:.1f} {y-r*0.9:.1f} {x+r*0.4:.1f} {y-r*0.9:.1f} {x+r} {y-r*0.3:.1f}" fill="none" stroke="#FFE4C0" stroke-width="1.2" opacity="0.5"></path>'
    for x, y, r in K.scatter([(300, 312), (420, 282), (560, 282), (680, 320), (660, 338), (540, 304), (420, 304), (300, 334)], 16, 3.2, 5.2, seed=21))
BODY = piv("body", f"{C}-body", 500, 512, skin_part(
    LOOK, BODY_D,
    belly="M730 456 C700 494 620 512 520 512 C420 512 330 494 290 460 L300 444 C340 476 420 492 520 492 C610 492 680 476 716 440 Z",
    layers=path("M262 330 C320 268 440 250 540 262 C620 272 680 300 720 340 L706 352 C668 316 612 292 540 284 C444 274 330 290 274 346 Z", D, 0.26)
           + stripes([(300, 300, 32, 16), (350, 280, 40, 18), (400, 268, 46, 19), (452, 262, 50, 20), (504, 262, 50, 20), (556, 268, 48, 19), (606, 280, 42, 18), (654, 298, 34, 16)])
           + spots(BODY_POLY, 28, 3, 7, 0.14, seed=7)
           + dots(BODY_POLY, 260)
           + line("M600 300 C616 350 616 410 600 470 M640 312 C656 360 656 420 640 470", 0.07, 2.4)
           + line("M330 470 C380 488 450 496 520 498", 0.12, 2)
           + osteo,
    rim_d="M262 330 C320 268 440 250 540 262 C620 272 680 300 720 340",
    outline_d="M262 330 C320 268 440 250 540 262 C620 272 680 300 720 340 C750 370 756 420 730 456 C700 494 620 512 520 512 C420 512 330 494 290 460"))

# ------------------------------------------------------------------ head + jaw (inside the neck)
JAW = piv("jaw", f"{C}-jaw", 858, 154,
    path("M858 152 C880 146 910 136 936 126 C944 134 944 142 938 148 Z", "#4A1C1E")
    + path("M866 154 C890 150 916 146 932 144 L930 148 C912 150 890 154 868 158 Z", "#8E3A3E")
    + skin_part(LOOK, "M856 150 C880 156 916 154 938 146 C944 152 938 162 926 164 C900 168 870 168 856 162 Z",
                belly="M858 160 C880 166 908 166 926 162 C934 160 938 156 940 152 L938 150 C930 158 910 160 880 158 C870 158 862 156 858 156 Z", tex=False)
    + line("M862 156 C884 160 912 158 936 150", 0.3, 1.6))
SKULL_D = "M838 118 C858 102 902 102 928 116 C946 126 950 138 940 146 C918 154 880 158 856 154 C840 150 830 132 838 118 Z"
HEAD = piv("head", f"{C}-head", 850, 140,
    JAW
    + skin_part(LOOK, SKULL_D,
                layers=path("M838 118 C858 102 902 102 928 116 C940 122 946 128 948 136 L940 134 C930 122 904 112 880 112 C862 112 848 118 842 128 Z", D, 0.22)
                       + dots([(842, 120), (900, 106), (944, 132), (900, 150), (850, 148)], 30, 0.6, 1.1, 0.12)
                       + line("M858 150 C884 154 914 150 938 144", 0.4, 1.8)
                       + line("M846 132 C850 142 856 148 864 152", 0.16, 1.6),
                light=True, rim_d="M838 118 C858 102 902 102 928 116 C946 126 950 138 948 140")
    + path("M882 108 C888 96 906 95 914 106 Z", SKIN) + stroke("M882 108 C888 96 906 95 914 106", 2.2) + path("M886 106 C892 100 904 99 910 105 Z", D, 0.18)
    + stroke("M906 108 C910 105 915 106 917 109", 2, D, 0.6)
    + K.eye(874, 122, f"{C}-eyelid", r=4)
    + path("M862 116 C868 110 882 110 888 116 C882 114 870 114 864 120 Z", D, 0.45))

# ------------------------------------------------------------------ neck (contains the head)
NECK_D = "M640 292 C690 238 752 168 818 126 C834 116 852 118 862 130 L876 150 C834 186 794 252 770 340 C760 366 722 380 690 372 C672 350 650 320 640 292 Z"
neck_stripes = []
for t, ln, w in [(0.22, 24, 13), (0.36, 22, 12), (0.5, 20, 11), (0.64, 18, 10), (0.78, 15, 9), (0.9, 12, 8)]:
    x, y = bez((640, 292), (690, 238), (752, 168), (818, 126), t)
    neck_stripes.append((round(x), round(y + 4), ln, w))
NECK = piv("neck", f"{C}-neck", 690, 320, skin_part(
    LOOK, NECK_D,
    belly="M876 150 C834 186 794 252 770 340 C764 356 756 366 746 372 L738 360 C750 350 756 336 760 320 C782 246 822 178 864 142 Z",
    layers=path("M648 284 C690 238 752 168 818 126 C834 116 852 118 862 130 L854 138 C842 130 830 130 822 134 C764 176 708 238 660 294 Z", D, 0.22)
           + stripes(neck_stripes)
           + dots([(660, 290), (820, 132), (860, 148), (770, 330), (700, 360)], 90)
           + line("M806 200 C812 204 818 205 822 204 M784 236 C790 240 796 241 800 240 M768 272 C774 276 780 277 784 276 M758 308 C764 312 770 313 774 312", 0.2, 1.8)
           + line("M700 300 C730 250 780 190 830 150", 0.08, 2.2),
    rim_d="M648 284 C690 238 752 168 818 126",
    outline_d="M648 284 C690 238 752 168 818 126 C834 116 852 118 862 130 L876 150 C834 186 794 252 770 340 C766 354 758 364 748 370")
    + HEAD)

# ------------------------------------------------------------------ assemble
INNER = (f'<ellipse cx="520" cy="652" rx="330" ry="12" fill="{D}" opacity="0.3"></ellipse>'
         + LEG_FAR + FORELEG_FAR + TAIL + NECK + BODY + LEG_NEAR + FORELEG_NEAR)
FRAG = piv("act", f"{C}-act", 500, 650, INNER)

ACTION = {
    "neck": [(0, "rotate(0)"), (0.3, "rotate(-12deg)"), (0.75, "rotate(-12deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.3, "rotate(10deg)"), (0.75, "rotate(10deg)"), (1, "rotate(0)")],
    "jaw": [(0, "rotate(0)"), (0.32, "rotate(0)"), (0.45, "rotate(16deg)"), (0.52, "rotate(12deg)"), (0.6, "rotate(16deg)"), (0.7, "rotate(15deg)"), (0.82, "rotate(0)"), (1, "rotate(0)")],
    "tail": [(0, "rotate(0)"), (0.3, "rotate(3deg)"), (0.75, "rotate(3deg)"), (1, "rotate(0)")],
}
GSAP = """      .to(parts.neck, { rotation: -12, duration: 0.65, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: 10, duration: 0.65, ease: 'power2.out' }, 0)
      .to(parts.tail, { rotation: 3, duration: 0.65, ease: 'sine.out' }, 0)
      .to(parts.jaw, { rotation: 16, duration: 0.25, ease: 'power2.out' }, 0.7)
      .to(parts.jaw, { rotation: 12, duration: 0.12, yoyo: true, repeat: 3, ease: 'none' }, 0.95)
      .to(parts.jaw, { rotation: 0, duration: 0.25, ease: 'power2.in' }, 1.55)
      .to([parts.neck, parts.head, parts.tail], { rotation: 0, duration: 0.6, ease: 'power2.inOut' }, 1.6)"""

# ------------------------------------------------------------------ poster scene: Patagonian conifer forest, misty morning
def conifer(x, base, h, w, tiers=7):
    """tall narrow conifer: a jagged spindle crown on a thin trunk"""
    pts_l, pts_r = [], []
    top = base - h
    for i in range(tiers + 1):
        t = i / tiers
        y = top + t * h * 0.82
        half = w * 0.5 * (0.15 + 0.85 * (t ** 0.8)) * (1.0 if i % 2 else 0.72)
        pts_l.append((x - half, y)); pts_r.append((x + half, y + h * 0.04))
    crown = f"M{x} {top} " + " ".join(f"L{a:.0f} {b:.0f}" for a, b in pts_r) + " " + " ".join(f"L{a:.0f} {b:.0f}" for a, b in reversed(pts_l)) + " Z"
    trunk = f"M{x-w*0.05:.0f} {base - h*0.2:.0f} L{x+w*0.05:.0f} {base - h*0.2:.0f} L{x+w*0.06:.0f} {base} L{x-w*0.06:.0f} {base} Z"
    return crown + " " + trunk

def fern(x, y, sc, color, flip=False):
    fl = -1 if flip else 1
    fronds = "".join(
        f'<path d="M0 0 C{fl*a*0.35:.0f} {-l*0.45:.0f} {fl*a*0.8:.0f} {-l*0.8:.0f} {fl*a:.0f} {-l:.0f} C{fl*a*0.75:.0f} {-l*0.72:.0f} {fl*a*0.3:.0f} {-l*0.35:.0f} 0 0 Z"></path>'
        for a, l in [(-70, 120), (-40, 150), (-10, 165), (25, 150), (60, 118), (90, 80), (-95, 75)])
    return f'<g transform="translate({x} {y}) scale({sc})" fill="{color}">{fronds}</g>'

def band(y, h, color, phase=0):
    return (f'<path d="M0 {y} C270 {y-6+phase} 540 {y+6-phase} 810 {y-3} C930 {y+4} 1010 {y} 1080 {y-2} '
            f'L1080 {y+h} C810 {y+h+4} 540 {y+h-5} 270 {y+h+3} C160 {y+h+6} 70 {y+h} 0 {y+h+2} Z" fill="{color}"></path>')

far_trees = "".join(path(conifer(x, 724, h, w), "#AEB8BC") for x, h, w in
                    [(20, 300, 60), (90, 360, 70), (170, 280, 56), (250, 340, 66), (330, 300, 58), (420, 380, 72), (510, 290, 56),
                     (600, 350, 66), (690, 300, 60), (770, 370, 70), (860, 320, 62), (950, 360, 68), (1040, 300, 60)])
mid_trees = "".join(path(conifer(x, 734, h, w, 9), "#96A4A6") for x, h, w in
                    [(40, 470, 92), (190, 420, 84), (330, 500, 96), (740, 460, 90), (900, 520, 100), (1050, 440, 86)])
SCENE = f'''<svg aria-hidden="true" viewBox="0 0 1080 900" width="1080" height="900" style="position: absolute; top: 0; left: 0; display: block">
<defs>
<linearGradient id="tit-sc-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9B9C6"></stop><stop offset="0.8" stop-color="#E1E4DE"></stop></linearGradient>
<radialGradient id="tit-sc-sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FBF5E6" stop-opacity="0.9"></stop><stop offset="0.3" stop-color="#F3EBD6" stop-opacity="0.45"></stop><stop offset="1" stop-color="#F3EBD6" stop-opacity="0"></stop></radialGradient>
<linearGradient id="tit-sc-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EEF0EA" stop-opacity="0"></stop><stop offset="0.65" stop-color="#EEF0EA" stop-opacity="0.7"></stop><stop offset="1" stop-color="#EEF0EA" stop-opacity="0.1"></stop></linearGradient>
<linearGradient id="tit-sc-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#1F2A18" stop-opacity="0.38"></stop></linearGradient>
<radialGradient id="tit-sc-shadow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#1F2A18" stop-opacity="0.4"></stop><stop offset="1" stop-color="#1F2A18" stop-opacity="0"></stop></radialGradient>
</defs>
<rect x="0" y="0" width="1080" height="900" fill="url(#tit-sc-sky)"></rect>
<circle cx="880" cy="430" r="340" fill="url(#tit-sc-sun)"></circle>
{far_trees}
<rect x="0" y="420" width="1080" height="320" fill="url(#tit-sc-haze)"></rect>
{mid_trees}
<rect x="0" y="560" width="1080" height="190" fill="url(#tit-sc-haze)" opacity="0.8"></rect>
<path d="M0 722 C200 712 400 726 600 718 C800 710 950 722 1080 716 L1080 900 L0 900 Z" fill="#8E9A6C"></path>
{band(766, 18, "#7F8C5E")}
{band(804, 22, "#A1AB7A", 2)}
{band(850, 50, "#7F8C5E", -1)}
<rect x="0" y="716" width="1080" height="184" fill="url(#tit-sc-ground)"></rect>
<ellipse cx="560" cy="836" rx="380" ry="24" fill="url(#tit-sc-shadow)"></ellipse>
{fern(40, 905, 1.05, "#3E4E36")}{fern(140, 910, 0.75, "#4A5C3F", True)}{fern(1020, 910, 0.95, "#3E4E36", True)}
</svg>'''

SPEC = dict(
    code=C, slug="titanosaur", board="Titanosaur", name="Titanosaur", short="titanosaur", look=LOOK,
    viewbox=(1000, 700), frag=FRAG,
    ids=["act", "body", "tail", "neck", "head", "jaw", "leg-near", "leg-far", "foreleg-near", "foreleg-far"],
    action=ACTION, dur=2.2, gsap=GSAP,
    action_label="Make the titanosaur call", action_verb="make it call", page_bg="#D3DBDF",
    scene=SCENE, title="Titanosaur", title_px=180, binomial="Patagotitan mayorum", subtitle="the titan from Patagonia",
    paragraph="One of the largest animals ever to walk on land: a long-necked plant eater weighing around 50 to 57 tonnes by recent estimates.",
    facts=[("31–37 m", "estimated length"), ("102", "million years ago"), ("2.38 m", "thigh bone")],
    footer="Known only from La Flecha ranch in Chubut Province, Argentina, in rocks about 101.6 million years old.",
    hint="Tap the titanosaur to make it call", skin_swatches=["#7C8AA0", "#7A8450", "#9E6B7B", "#5E7E7A"],
    dino_top=130,
    rig_parts=[
        ("Neck, head and jaw", "#neck, #head, #jaw", NECK, (628, 92, 332, 292)),
        ("Body", "#body", BODY, (238, 248, 524, 272)),
        ("Tail", "#tail", TAIL, (8, 322, 302, 118)),
        ("Near hind leg", "#leg-near", LEG_NEAR, (286, 346, 140, 308)),
        ("Far hind leg", "#leg-far", LEG_FAR, (330, 344, 140, 308)),
        ("Near front leg", "#foreleg-near", FORELEG_NEAR, (584, 358, 116, 296)),
        ("Far front leg", "#foreleg-far", FORELEG_FAR, (624, 356, 116, 296)),
    ],
    rig_h=1080,
)

FONT_CSS = """<style>
@font-face{font-family:'Big Shoulders Display';font-weight:800;src:url(/tmp/fonts/node_modules/@fontsource/big-shoulders-display/files/big-shoulders-display-latin-800-normal.woff2)}
@font-face{font-family:'Big Shoulders Display';font-weight:900;src:url(/tmp/fonts/node_modules/@fontsource/big-shoulders-display/files/big-shoulders-display-latin-900-normal.woff2)}
@font-face{font-family:'Public Sans';font-weight:400;src:url(/tmp/fonts/node_modules/@fontsource/public-sans/files/public-sans-latin-400-normal.woff2)}
@font-face{font-family:'Public Sans';font-weight:500;src:url(/tmp/fonts/node_modules/@fontsource/public-sans/files/public-sans-latin-500-normal.woff2)}
@font-face{font-family:'Public Sans';font-style:italic;font-weight:400;src:url(/tmp/fonts/node_modules/@fontsource/public-sans/files/public-sans-latin-400-italic.woff2)}
@font-face{font-family:'Public Sans';font-weight:600;src:url(/tmp/fonts/node_modules/@fontsource/public-sans/files/public-sans-latin-500-normal.woff2)}
</style>"""

def pw_shoot(name, w, h, crop=None):
    from playwright.sync_api import sync_playwright
    src = K.OUT / "shots" / f"{name}.html"
    html = src.read_text().replace("<style>", FONT_CSS + "<style>", 1)
    tmp = K.OUT / "shots" / f"{name}-fonts.html"; tmp.write_text(html)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": w, "height": h}); pg.goto(f"file://{tmp}"); pg.wait_for_timeout(900)
        pg.screenshot(path=str(K.OUT / "shots" / f"{name}.png")); b.close()

if __name__ == "__main__":
    frag = K.write_all(SPEC)
    K.poster_board(SPEC, frag)
    K.rig_board(SPEC, frag)
    K.shoot("titanosaur-animated.svg", 1000, 700)
    pw_shoot("titanosaur-poster", 1080, 1350)
    pw_shoot("titanosaur-rig", 1700, 1080)
    print("ok")
