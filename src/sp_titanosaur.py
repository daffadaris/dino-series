import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Titanosaur (Patagotitan mayorum) for the dinosaur series. Import has no side effects;
run as a script to write the SVG, GSAP page, poster board and rig board."""
import sys
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, D, L, OL, CLAW, path, stroke, line, rim, stripes, spots, dots, skin_part, piv, bez

C = "tit"
LOOK = K.Look(C, skin="#7C8AA0", belly="#D8D2C2")

# ------------------------------------------------------------------ proportions
# Follows published skeletal reconstructions of Patagotitan for general proportions (not traced): at 31 m the back
# stands about 4.7 m high and the head about 11-12 m up; a long neck raised at roughly 45 degrees, a comparatively
# small, deep torso, short pillar-like legs and a long, tapering tail. About 34 drawing units per metre.

# ------------------------------------------------------------------ legs (columnar, padded feet)
HIND = ("M438 520 C466 502 520 504 530 530 C536 550 530 566 522 578 L524 632 C526 644 518 650 508 650 "
        "L468 650 C458 650 454 642 456 632 L458 586 C444 572 432 540 438 520 Z")
HIND_FOOT = "M450 636 C458 628 520 628 532 636 C536 642 534 650 528 650 L456 650 C448 650 446 642 450 636 Z"
HIND_NAILS = "M522 638 C529 638 534 643 533 649 C528 647 524 646 520 646 Z M510 640 C516 640 520 644 519 649 C515 647 512 647 509 647 Z"
FORE = ("M642 518 C670 502 712 508 718 530 C722 550 716 566 708 578 L710 632 C712 644 704 650 694 650 "
        "L658 650 C648 650 644 642 646 632 L648 586 C638 572 634 536 642 518 Z")
FORE_FOOT = "M640 638 C648 630 708 630 718 638 C722 644 720 650 714 650 L646 650 C638 650 636 642 640 638 Z"

def open_top(d):
    """limb outline without the arc where it meets the body"""
    head, rest = d.split(" C", 1)
    return "M" + " ".join(rest.split(" ")[4:6]) + " C" + rest.split(" C", 1)[1].rstrip(" Z")

def leg(gid, d, foot, nails=None, far=False, dx=0, creases=""):
    if far:
        inner = (skin_part(LOOK, d, ao=True, far=True, tex=False, outline_d=open_top(d))
                 + skin_part(LOOK, foot, far=True, tex=False) + (path(nails, CLAW, 0.85) if nails else ""))
    else:
        inner = (skin_part(LOOK, d, ao=True, outline_d=open_top(d), layers=line(creases, 0.18, 2))
                 + skin_part(LOOK, foot, tex=False) + (path(nails, CLAW) if nails else ""))
    t = f' transform="translate({dx} -2)"' if dx else ""
    return f'<g id="{gid}"{t}>{inner}</g>'

LEG_FAR = leg("leg-far", HIND, HIND_FOOT, HIND_NAILS, far=True, dx=40)
FORELEG_FAR = leg("foreleg-far", FORE, FORE_FOOT, far=True, dx=36)
LEG_NEAR = leg("leg-near", HIND, HIND_FOOT, HIND_NAILS, creases="M462 600 C478 606 500 606 518 600 M462 614 C480 620 500 620 518 614")
FORELEG_NEAR = leg("foreleg-near", FORE, FORE_FOOT, creases="M652 600 C668 606 688 606 706 600 M652 614 C670 620 688 620 706 614")

# ------------------------------------------------------------------ tail (long and tapering)
TAIL_TOP = "M424 506 C350 512 256 532 154 562 C104 578 66 592 40 602"
TAIL_D = TAIL_TOP + " C30 604 32 612 42 610 C84 602 140 594 200 588 C300 578 380 576 440 580 Z"
TAIL = piv("tail", f"{C}-tail", 420, 544, skin_part(
    LOOK, TAIL_D,
    belly="M42 610 C84 602 140 594 200 588 C300 578 380 576 440 580 L440 568 C380 564 300 566 200 576 C140 580 80 588 44 594 Z",
    layers=path(TAIL_TOP + " C70 582 110 572 160 562 C260 540 356 522 424 520 Z", D, 0.24)
           + stripes([(120, 568, 7, 6), (180, 554, 9, 7), (240, 540, 11, 8), (300, 526, 13, 9), (360, 514, 15, 10)])
           + dots([(60, 590), (430, 490), (430, 566), (200, 578)], 60)
           + line("M428 548 C350 550 250 560 120 582", 0.12, 2),
    fade=True, rim_d=TAIL_TOP, outline_d=TAIL_D.rstrip(" Z")))

# ------------------------------------------------------------------ body (with osteoderms): smaller and lower than before
BODY_TOP = "M408 500 C462 480 556 468 640 470 C696 472 734 500 744 536"
BODY_D = BODY_TOP + " C752 566 732 588 694 596 C620 608 516 606 456 594 C420 586 400 562 400 536 C400 522 402 508 408 500 Z"
BODY_POLY = [(412, 506), (560, 478), (730, 506), (740, 562), (600, 598), (420, 580)]
osteo = "".join(
    f'<ellipse cx="{x}" cy="{y}" rx="{r*1.6:.1f}" ry="{r:.1f}" fill="{SKIN}" stroke="{OL}" stroke-width="1.2"></ellipse>'
    f'<ellipse cx="{x}" cy="{y}" rx="{r*1.6:.1f}" ry="{r:.1f}" fill="{D}" opacity="0.2"></ellipse>'
    for x, y, r in K.scatter([(430, 502), (560, 478), (690, 480), (716, 504), (560, 500), (430, 518)], 14, 2.4, 3.8, seed=21))
BODY = piv("body", f"{C}-body", 566, 588, skin_part(
    LOOK, BODY_D,
    belly="M744 536 C752 566 732 588 694 596 C620 608 516 606 456 594 C420 586 400 562 400 536 L414 536 C418 556 436 570 464 578 C524 588 616 588 684 576 C718 568 738 554 742 536 Z",
    layers=path(BODY_TOP + " L734 542 C722 514 694 492 640 490 C560 490 468 498 412 520 Z", D, 0.24)
           + stripes([(430, 494, 22, 12), (476, 482, 24, 13), (520, 474, 26, 14), (564, 470, 26, 14), (608, 470, 24, 13), (652, 474, 22, 12), (694, 484, 18, 11)])
           + spots(BODY_POLY, 20, 2.4, 5, 0.14, seed=7) + dots(BODY_POLY, 180)
           + line("M640 486 C654 516 654 560 640 596", 0.07, 2.2)
           + osteo,
    rim_d=BODY_TOP, outline_d=BODY_TOP + " C752 566 732 588 694 596 C620 608 516 606 456 594"))

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

# ------------------------------------------------------------------ neck (contains the head): long, raised at about 45 degrees
NECK_TOP = ((560, 492), (690, 462), (772, 340), (826, 268))
NECK_D = ("M560 492 C690 462 772 340 826 268 C850 236 884 212 920 216 L934 252 "
          "C900 268 858 306 822 356 C790 402 760 470 732 562 C690 552 610 528 560 492 Z")
neck_stripes = []
for t, ln, w in [(0.2, 18, 11), (0.34, 17, 10), (0.48, 16, 10), (0.62, 14, 9), (0.76, 12, 8), (0.9, 10, 7)]:
    x, y = bez(*NECK_TOP, t)
    neck_stripes.append((round(x), round(y + 3), ln, w))
# the head keeps its drawing, scaled to sauropod proportions and seated on the end of the neck
HEAD_PLACED = f'<g transform="translate(924 238) rotate(10) scale(0.72) translate(-850 -140)">{HEAD}</g>'
NECK = piv("neck", f"{C}-neck", 680, 510, skin_part(
    LOOK, NECK_D,
    belly="M934 252 C900 268 858 306 822 356 C790 402 760 470 732 560 L718 552 C744 468 774 398 808 350 C846 298 886 264 924 244 Z",
    layers=path("M560 492 C690 462 772 340 826 268 C850 236 884 212 920 216 L912 230 C892 230 872 244 858 258 C786 340 700 470 580 506 Z", D, 0.22)
           + stripes(neck_stripes)
           + dots([(610, 500), (700, 466), (772, 360), (826, 276), (920, 238), (822, 360), (730, 556), (660, 520)], 110)
           + line("M852 292 C858 296 864 297 868 296 M824 328 C830 332 836 333 840 332 M798 366 C804 370 810 371 814 370 M776 406 C782 410 788 411 792 410", 0.2, 1.6),
    rim_d="M566 488 C692 458 772 338 826 266 C850 236 882 214 914 216",
    outline_d="M560 492 C690 462 772 340 826 268 C850 236 884 212 920 216 L934 252 C900 268 858 306 822 356 C790 402 760 470 732 562")
    + HEAD_PLACED)

# snout-to-tail midline in drawing units; the group poster measures length along it, since the raised neck
# makes the straight-line span much shorter than the animal
MIDLINE = [(992, 252), (924, 238), (850, 262), (790, 340), (740, 410), (680, 500), (600, 522), (420, 540), (250, 562), (40, 604)]

# ------------------------------------------------------------------ assemble
INNER = (f'<ellipse cx="540" cy="652" rx="300" ry="12" fill="{D}" opacity="0.3"></ellipse>'
         + LEG_FAR + FORELEG_FAR + TAIL + NECK + BODY + LEG_NEAR + FORELEG_NEAR)
FRAG = piv("act", f"{C}-act", 540, 650, INNER)

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
    facts=[("31 m", "estimated length"), ("102", "million years ago"), ("2.38 m", "thigh bone")],
    footer="Known only from La Flecha ranch in Chubut Province, Argentina, in rocks about 101.6 million years old.",
    hint="Tap the titanosaur to make it call", skin_swatches=["#7C8AA0", "#7A8450", "#9E6B7B", "#5E7E7A"],
    dino_top=130, midline=MIDLINE,
    rig_parts=[
        ("Neck, head and jaw", "#neck, #head, #jaw", NECK, (550, 196, 450, 370)),
        ("Body", "#body", BODY, (392, 460, 362, 150)),
        ("Tail", "#tail", TAIL, (24, 494, 424, 112)),
        ("Near hind leg", "#leg-near", LEG_NEAR, (426, 466, 116, 188)),
        ("Far hind leg", "#leg-far", LEG_FAR, (466, 464, 116, 188)),
        ("Near front leg", "#foreleg-near", FORELEG_NEAR, (630, 472, 96, 182)),
        ("Far front leg", "#foreleg-far", FORELEG_FAR, (666, 470, 96, 182)),
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
