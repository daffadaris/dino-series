import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
"""Triceratops for the dinosaur series. Import builds SPEC only; run as a script to write outputs."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, D, L, OL, CLAW, piv, path, stroke, line, rim, stripes, spots, dots, skin_part

C = "tri"
LOOK = K.Look(C, skin="#7A8450", belly="#DCCFA6", accent="#C27A48")
HORN, BEAK = "#E6D9BC", "#4A3A30"

# ------------------------------------------------------------------ legs
HIND = "M360 270 C400 246 470 252 492 300 C510 340 500 390 472 410 L476 470 C478 492 470 506 456 508 L404 508 C392 506 388 494 392 482 L396 420 C370 400 350 360 350 320 C350 298 352 282 360 270 Z"
HIND_FOOT = "M388 494 C400 486 456 486 474 494 C482 500 482 512 474 514 L394 514 C384 514 382 500 388 494 Z"
HIND_NAIL = "M466 492 C478 492 486 498 486 506 C486 512 480 514 472 514 Z M448 496 C456 496 462 501 462 507 C462 512 457 514 451 514 Z"
FRONT = "M620 300 C650 286 690 296 700 330 C708 360 690 390 666 402 L668 470 C670 492 662 506 648 508 L612 508 C600 506 598 494 602 484 L606 420 C598 400 600 360 606 336 C610 318 614 306 620 300 Z"
FRONT_FOOT = "M598 494 C610 486 652 486 666 494 C674 500 674 512 666 514 L604 514 C594 514 592 500 598 494 Z"
FRONT_NAIL = "M658 492 C670 492 678 498 678 506 C678 512 672 514 664 514 Z M640 496 C648 496 654 501 654 507 C654 512 649 514 643 514 Z"

def leg(gid, d, foot, nails, far=False, dx=0, wrinkles=""):
    t = f' transform="translate({dx} -2)"' if dx else ""
    body = skin_part(LOOK, d, light=not far, ao=True, far=far, tex=not far,
                     layers=(line(wrinkles, 0.2, 2) if wrinkles else ""))
    ft = skin_part(LOOK, foot, ao=True, far=far, tex=False)
    nl = path(nails, CLAW) + stroke(nails, 2)
    return f'<g id="{gid}"{t}>{body}{ft}{nl}</g>'

FAR_HIND = leg("leg-far", HIND, HIND_FOOT, HIND_NAIL, far=True, dx=46)
FAR_FRONT = leg("foreleg-far", FRONT, FRONT_FOOT, FRONT_NAIL, far=True, dx=40)
NEAR_HIND = leg("leg-near", HIND, HIND_FOOT, HIND_NAIL,
                wrinkles="M398 432 C410 438 426 440 440 438 M398 446 C410 452 424 454 438 452 M362 312 C372 300 386 292 400 290")
NEAR_FRONT = leg("foreleg-near", FRONT, FRONT_FOOT, FRONT_NAIL,
                 wrinkles="M608 430 C618 436 634 438 648 436 M610 444 C620 450 634 452 646 450")

# ------------------------------------------------------------------ tail
TAIL_D = "M350 252 C290 260 190 280 40 300 C32 302 32 310 40 311 C190 318 290 334 356 352 Z"
TAIL_OPEN = "M350 252 C290 260 190 280 40 300 C32 302 32 310 40 311 C190 318 290 334 356 352"
TAIL = piv("tail", f"{C}-tail", 345, 290, skin_part(
    LOOK, TAIL_D,
    belly="M40 311 C190 318 290 334 356 352 L356 336 C290 320 190 306 46 306 Z",
    layers=stripes([(88, 298, 7, 8), (148, 291, 11, 10), (208, 283, 15, 12), (266, 274, 19, 13), (318, 266, 23, 14)], 0.3)
           + line("M350 300 C280 300 180 304 80 306", 0.12, 2.2),
    fade=True, outline_d=TAIL_OPEN, rim_d="M350 252 C290 260 190 280 40 300"))

# ------------------------------------------------------------------ body
BODY_D = "M330 250 C360 228 400 214 440 212 C520 210 600 222 660 244 C690 254 712 266 726 286 C744 316 742 360 716 390 C682 424 620 434 540 432 C470 430 410 418 372 396 C344 378 326 340 320 300 C318 280 322 262 330 250 Z"
BODY_OPEN = "M330 250 C360 228 400 214 440 212 C520 210 600 222 660 244 C690 254 712 266 726 286 C744 316 742 360 716 390 C682 424 620 434 540 432 C470 430 410 418 372 396"
BODY_POLY = [(350, 250), (440, 222), (600, 230), (700, 272), (724, 340), (690, 400), (540, 416), (400, 400), (342, 340)]
BODY = piv("body", f"{C}-body", 520, 410, skin_part(
    LOOK, BODY_D,
    belly="M732 300 C744 344 734 372 716 390 C682 424 620 434 540 432 C470 430 410 418 372 396 L380 380 C420 402 480 412 540 414 C610 416 670 406 704 376 C722 358 730 330 732 300 Z",
    layers=path("M330 250 C360 228 400 214 440 212 C520 210 600 222 660 244 C690 254 712 266 726 286 L716 296 C700 276 680 266 656 260 C600 240 520 230 440 232 C400 234 360 246 336 266 Z", D, 0.26)
           + stripes([(376, 234, 36, 15), (426, 222, 46, 17), (476, 219, 50, 18), (526, 220, 50, 18), (576, 226, 48, 18), (626, 240, 42, 16), (672, 258, 32, 14)], 0.3)
           + spots(BODY_POLY, 22, 3, 6.5, 0.13, seed=8) + dots(BODY_POLY, 220, seed=9)
           + line("M600 260 C612 304 612 350 598 398 M650 262 C662 300 662 346 650 390", 0.06, 2.4)
           + line("M560 412 C576 420 594 424 612 424 M572 424 C588 430 604 432 620 430", 0.16, 2),
    outline_d=BODY_OPEN, rim_d="M330 250 C360 228 400 214 440 212 C520 210 600 222 660 244 C690 254 712 266 726 286"))

# ------------------------------------------------------------------ head
# frill outline segments (cubic), used to place the epoccipital bumps along its rim
FRILL_SEGS = [((672, 304), (628, 268), (612, 190), (646, 136)),
              ((646, 136), (680, 86), (760, 92), (794, 144)),
              ((794, 144), (806, 166), (808, 198), (798, 228))]
FRILL_D = "M672 304 C628 268 612 190 646 136 C680 86 760 92 794 144 C806 166 808 198 798 228 C780 270 736 300 706 312 Z"
FRILL_CENTRE = (722, 210)

def frill_bumps():
    pts = []
    for i, seg in enumerate(FRILL_SEGS):
        rng = [(0.6, 1.0), (0.0, 1.0), (0.0, 0.8)][i]
        n = [3, 9, 4][i]
        for k in range(n):
            t = rng[0] + (rng[1] - rng[0]) * (k + 0.5) / n
            pts.append(K.bez(*seg, t))
    out = []
    for x, y in pts:
        ang = math.atan2(y - FRILL_CENTRE[1], x - FRILL_CENTRE[0]); ox, oy = math.cos(ang), math.sin(ang)
        tx, ty = -oy, ox
        a = (x + tx * 6 - ox * 3, y + ty * 6 - oy * 3); b = (x - tx * 6 - ox * 3, y - ty * 6 - oy * 3); c = (x + ox * 10, y + oy * 10)
        out.append(f"M{a[0]:.1f} {a[1]:.1f} Q{c[0] + tx * 3:.1f} {c[1] + ty * 3:.1f} {c[0]:.1f} {c[1]:.1f} Q{c[0] - tx * 3:.1f} {c[1] - ty * 3:.1f} {b[0]:.1f} {b[1]:.1f} Z")
    d = " ".join(out)
    return path(d, SKIN) + path(d, D, 0.22) + stroke(d, 2.4)

FRILL_INNER = "M684 290 C652 262 640 198 664 154 C690 114 750 116 776 158 C786 178 786 206 778 226 C764 260 730 284 708 294 Z"
RIBS = " ".join(f"M714 292 L{x:.0f} {y:.0f}" for x, y in [K.bez(*FRILL_SEGS[1], t) for t in (0.12, 0.3, 0.5, 0.7, 0.88)] + [K.bez(*FRILL_SEGS[0], 0.7), K.bez(*FRILL_SEGS[2], 0.4)])
FRILL = (frill_bumps() + path(FRILL_D, SKIN) + path(FRILL_D, D, 0.18) + path(FRILL_INNER, LOOK.accent)
         + path(FRILL_INNER, LOOK.url("light")) + stroke(RIBS, 2.4, D, 0.16)
         + dots([(660, 160), (700, 120), (770, 140), (780, 220), (720, 290), (670, 260)], 60, 0.8, 1.6, 0.12, seed=12)
         + path(FRILL_D, LOOK.url("shade")) + rim("M646 136 C680 86 760 92 794 144", 3.2, 4, 0.55) + stroke(FRILL_D))

SKULL_D = "M700 252 C740 236 800 238 842 252 C882 266 912 288 932 308 L952 332 C958 340 954 350 944 352 L902 354 C870 362 830 366 790 364 C750 362 716 346 702 326 C692 310 690 272 700 252 Z"
JAW_D = "M786 346 C834 352 892 352 938 344 C950 344 956 352 948 364 C922 386 868 396 818 392 C794 390 780 372 782 356 Z"
BEAK_D = "M926 302 C946 312 962 328 964 344 C964 356 954 362 942 360 L918 352 C930 338 932 318 926 302 Z"
LBEAK_D = "M916 352 C934 348 948 348 952 356 C948 368 938 378 922 380 Z"
NASAL_D = "M870 270 C872 252 882 236 892 226 C896 242 896 260 892 278 Z"
HORN_NEAR = "M786 250 C800 210 840 164 902 132 C878 168 842 212 818 258 Z"
HORN_FAR = "M770 246 C782 206 818 162 874 128 C852 164 822 208 800 254 Z"
JUGAL = "M744 346 C736 360 730 372 726 384 C742 378 754 366 762 352 Z"

def horn(d, far=False):
    return path(d, HORN) + path(d, LOOK.url("ao")) + (path(d, D, 0.3) if far else "") + stroke(d, 2.6)

HEAD_INNER = (
    horn(HORN_FAR, far=True)
    + FRILL
    + skin_part(LOOK, JAW_D, belly="M796 380 C840 392 900 390 940 372 C930 366 900 376 842 378 C820 378 806 374 796 368 Z", tex=False)
    + path(LBEAK_D, BEAK) + stroke(LBEAK_D, 2.4)
    + skin_part(LOOK, SKULL_D,
                layers=path("M700 252 C740 236 800 238 842 252 C882 266 912 288 932 308 L924 314 C904 296 876 278 840 266 C800 254 742 254 706 268 Z", D, 0.24)
                       + path("M716 300 C736 324 764 340 800 346 C780 330 768 310 764 286 C744 286 726 292 716 300 Z", D, 0.12)
                       + line("M800 300 C812 314 830 322 852 324 M842 290 C856 300 874 306 894 306", 0.14, 2)
                       + line("M884 302 C890 298 898 300 900 306", 0.55, 2.4)
                       + line("M798 362 C840 364 890 360 920 354", 0.4, 2.4)
                       + dots([(712, 262), (800, 246), (900, 290), (940, 330), (880, 354), (760, 352), (708, 318)], 80, 0.8, 1.5, 0.12, seed=13),
                light=True, rim_d="M700 252 C740 236 800 238 842 252 C882 266 912 288 932 308")
    + path(BEAK_D, BEAK) + path(BEAK_D, LOOK.url("shade")) + stroke(BEAK_D, 2.6)
    + horn(NASAL_D)
    + path(JUGAL, SKIN) + path(JUGAL, D, 0.18) + stroke(JUGAL, 2.4)
    + K.eye(772, 284, f"{C}-eyelid", 5.5)
    + path("M756 276 C764 266 782 264 794 270 C796 272 794 275 792 275 C782 271 768 272 760 280 C758 280 755 278 756 276 Z", D, 0.45)
    + horn(HORN_NEAR)
)
HEAD = piv("head", f"{C}-head", 700, 300, HEAD_INNER)

SHADOW = '<ellipse cx="560" cy="516" rx="300" ry="11" fill="#000000" opacity="0.28"></ellipse>'
INNER = SHADOW + FAR_HIND + FAR_FRONT + TAIL + BODY + NEAR_HIND + NEAR_FRONT + HEAD
FRAG = piv("act", f"{C}-act", 520, 514, INNER)

# ------------------------------------------------------------------ motion
ACTION = {
    "act": [(0, "translateX(0)"), (0.18, "translateX(-10px)"), (0.42, "translateX(26px)"), (0.7, "translateX(26px)"), (1, "translateX(0)")],
    "head": [(0, "rotate(0)"), (0.18, "rotate(-6deg)"), (0.42, "rotate(12deg)"), (0.7, "rotate(12deg)"), (0.82, "rotate(9deg)"), (1, "rotate(0)")],
}
GSAP = """      .to(parts.act, { x: -10, duration: 0.28, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -6, duration: 0.28, ease: 'power2.out' }, 0)
      .to(parts.act, { x: 26, duration: 0.4, ease: 'power3.in' }, 0.28)
      .to(parts.head, { rotation: 12, duration: 0.4, ease: 'back.out(2)' }, 0.28)
      .to(parts.head, { rotation: 9, duration: 0.2, ease: 'sine.inOut' }, 1.1)
      .to(parts.act, { x: 0, duration: 0.5, ease: 'power2.inOut' }, 1.12)
      .to(parts.head, { rotation: 0, duration: 0.4, ease: 'power2.inOut' }, 1.3)"""

# ------------------------------------------------------------------ poster scene
def fern(x, y, sc, color, flip=False):
    fl = -1 if flip else 1
    fronds = "".join(
        f'<path d="M0 0 C{fl*a*0.35:.0f} {-l*0.45:.0f} {fl*a*0.8:.0f} {-l*0.8:.0f} {fl*a:.0f} {-l:.0f} C{fl*a*0.75:.0f} {-l*0.72:.0f} {fl*a*0.3:.0f} {-l*0.35:.0f} 0 0 Z"></path>'
        for a, l in [(-70, 120), (-40, 150), (-10, 165), (25, 150), (60, 118), (90, 80), (-95, 75)])
    return f'<g transform="translate({x} {y}) scale({sc})" fill="{color}">{fronds}</g>'

def band(y, h, color, phase=0):
    return (f'<path d="M0 {y} C270 {y-6+phase} 540 {y+6-phase} 810 {y-3} C930 {y+4} 1010 {y} 1080 {y-2} '
            f'L1080 {y+h} C810 {y+h+4} 540 {y+h-5} 270 {y+h+3} C160 {y+h+6} 70 {y+h} 0 {y+h+2} Z" fill="{color}"></path>')

SCENE = f'''<svg aria-hidden="true" viewBox="0 0 1080 900" width="1080" height="900" style="position: absolute; top: 0; left: 0; display: block">
<defs>
<linearGradient id="tri-sc-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A8C6CF"></stop><stop offset="0.5" stop-color="#D4DCCB"></stop><stop offset="0.76" stop-color="#EED9B0"></stop></linearGradient>
<radialGradient id="tri-sc-sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF2D6" stop-opacity="0.95"></stop><stop offset="0.28" stop-color="#FFDFA8" stop-opacity="0.5"></stop><stop offset="1" stop-color="#FFDFA8" stop-opacity="0"></stop></radialGradient>
<linearGradient id="tri-sc-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1E3C4" stop-opacity="0"></stop><stop offset="0.6" stop-color="#F1E3C4" stop-opacity="0.5"></stop><stop offset="1" stop-color="#F1E3C4" stop-opacity="0"></stop></linearGradient>
<linearGradient id="tri-sc-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#1F2A12" stop-opacity="0.38"></stop></linearGradient>
<linearGradient id="tri-sc-river" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B9D2D6"></stop><stop offset="1" stop-color="#8FB3BC"></stop></linearGradient>
<radialGradient id="tri-sc-shadow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#1F2A12" stop-opacity="0.4"></stop><stop offset="1" stop-color="#1F2A12" stop-opacity="0"></stop></radialGradient>
</defs>
<rect x="0" y="0" width="1080" height="900" fill="url(#tri-sc-sky)"></rect>
<circle cx="170" cy="610" r="340" fill="url(#tri-sc-sun)"></circle>
<path d="M0 648 C110 610 230 616 330 640 C430 600 560 604 660 634 C760 606 900 600 1080 628 L1080 900 L0 900 Z" fill="#A9B596"></path>
<path d="M0 684 C140 650 260 656 380 676 C500 646 640 650 760 674 C860 652 980 650 1080 664 L1080 900 L0 900 Z" fill="#93A27A"></path>
<rect x="0" y="580" width="1080" height="150" fill="url(#tri-sc-haze)"></rect>
<path d="M0 712 C200 700 420 716 640 706 C820 698 960 708 1080 702 L1080 900 L0 900 Z" fill="#9AA864"></path>
<path d="M0 734 C220 724 440 742 660 732 C840 724 980 734 1080 728 L1080 756 C960 762 820 752 660 760 C440 770 220 750 0 760 Z" fill="url(#tri-sc-river)"></path>
<path d="M120 742 L260 740 M520 748 L700 744 M860 738 L980 736" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.5"></path>
{band(772, 20, "#8C9A58")}
{band(806, 24, "#A7B26E", 2)}
{band(846, 18, "#8C9A58", -2)}
{band(872, 40, "#7F8D4E", 1)}
<rect x="0" y="704" width="1080" height="196" fill="url(#tri-sc-ground)"></rect>
<ellipse cx="560" cy="826" rx="360" ry="24" fill="url(#tri-sc-shadow)"></ellipse>
{fern(40, 900, 1.1, "#33452B")}{fern(140, 905, 0.8, "#43573A", True)}{fern(1020, 905, 1.05, "#33452B", True)}{fern(940, 910, 0.7, "#43573A")}
</svg>'''

# ------------------------------------------------------------------ rig parts
RIG = [
    ("Head and frill", "#head", HEAD, (604, 82, 372, 316)),
    ("Body", "#body", BODY, (312, 204, 434, 216)),
    ("Tail", "#tail", TAIL, (24, 244, 340, 116)),
    ("Hind legs", "#leg-near, #leg-far", NEAR_HIND + f'<g transform="translate(150 0)">{FAR_HIND}</g>', (340, 238, 360, 282)),
    ("Front legs", "#foreleg-near, #foreleg-far", NEAR_FRONT + f'<g transform="translate(70 0)">{FAR_FRONT}</g>', (590, 280, 230, 240)),
]

SPEC = dict(
    code=C, slug="triceratops", board="Triceratops", name="Triceratops", short="Triceratops", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "tail", "head", "leg-near", "leg-far", "foreleg-near", "foreleg-far"],
    action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the Triceratops charge", action_verb="make it charge", page_bg="#CFD9C4",
    scene=SCENE, title="Triceratops", title_px=190, binomial="Triceratops horridus", subtitle="the three-horned face",
    paragraph="A tank-built plant eater whose head could reach a third of its body length, with a bony frill and three horns. It shared its world with T. rex.",
    facts=[("8–9 m", "snout to tail tip"), ("68–66", "million years ago"), ("1 m", "brow horn length")],
    footer="Fossils are common in the Hell Creek Formation of Montana, Wyoming and the Dakotas, the same rocks that hold T. rex.",
    hint="Tap the Triceratops to make it charge",
    skin_swatches=["#7A8450", "#9E6B7B", "#5E7E7A", "#8A6A3E"], dino_top=262,
    rig_parts=RIG, rig_h=960,
)

if __name__ == "__main__":
    frag = K.write_all(SPEC)
    K.poster_board(SPEC, frag)
    K.rig_board(SPEC, frag)
    print(K.shoot("triceratops-animated.svg", 1000, 560))
    print(K.shoot("triceratops-poster", 1080, 1350))
    print(K.shoot("triceratops-rig", 1700, 960))
