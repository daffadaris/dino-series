import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Ankylosaurus for the dinosaur series. Building SPEC has no side effects; run as a script to write outputs.
Anatomy follows Arbour & Mallon 2017 (FACETS 2: 764-794): stubby, widely spaced keeled osteoderms with no large
flank spikes, two cervical half-rings, pyramidal squamosal and jugal horns, side-facing nostrils under a roofing
scale, and a low, flat tail club (AMNH 5214: about 60 cm long, 49 cm wide, 19 cm tall) on a stiff handle."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
import scenery
from dinokit import SKIN, D, OL, path, stroke, line, piv, skin_part, stripes, spots, dots, eye
C = "ank"
LOOK = K.Look(C, skin="#8C6F48", belly="#DED0AA", accent="#CDB98E")
BONE, NAIL, BEAK = "#BFA674", "#3A2A2C", "#4A3A30"

# ---------------- geometry (1000 x 560, ground at 514)
BODY_D = ("M300 300 C340 250 430 222 520 222 C620 222 700 248 760 298 C782 318 792 344 788 366 "
          "C782 396 752 416 700 424 C600 434 480 434 400 422 C350 414 316 382 304 342 Z")
BODY_TOP = "M300 300 C340 250 430 222 520 222 C620 222 700 248 760 298"
TAIL_D = "M330 280 C270 270 210 286 126 294 L126 314 C210 314 270 334 332 368 Z"
TAIL_TOP = "M330 280 C270 270 210 286 126 294"
CLUB_D = ("M138 296 C126 288 108 286 92 288 C78 286 62 288 52 294 C44 298 42 310 52 316 "
          "C62 322 78 324 92 322 C108 324 126 322 138 314 C142 310 142 300 138 296 Z")
HIND_D = ("M392 320 C432 300 502 308 518 352 C528 386 518 422 498 436 L502 486 C504 500 496 508 484 508 "
          "L442 508 C430 506 426 496 430 486 L434 440 C410 426 392 396 388 366 C386 346 386 332 392 320 Z")
HIND_FOOT = "M428 494 C440 486 486 486 504 494 C512 500 512 512 504 514 L434 514 C424 514 422 500 428 494 Z"
FORE_D = ("M670 356 C696 346 726 358 728 388 C730 410 718 428 704 436 L706 488 C708 500 700 508 688 508 "
          "L656 508 C644 506 642 496 646 486 L648 440 C642 424 644 400 650 380 C654 366 660 360 670 356 Z")
FORE_FOOT = "M642 494 C654 486 692 486 706 494 C714 500 714 512 706 514 L648 514 C638 514 636 500 642 494 Z"
NECK_D = "M736 290 C780 292 818 312 842 336 L848 402 C812 406 772 398 738 382 C728 352 728 314 736 290 Z"
HEAD_D = ("M818 322 C852 304 906 308 940 330 C960 344 966 368 958 388 C942 406 902 412 866 410 "
          "C836 408 816 390 812 366 C810 348 810 332 818 322 Z")

def spine(t):
    if t < 0.45:
        return K.bez((300, 300), (340, 250), (430, 222), (520, 222), t / 0.45)
    return K.bez((520, 222), (620, 222), (700, 248), (760, 298), (t - 0.45) / 0.55)

def tangent(f, t, e=0.004):
    a, b = f(max(0, t - e)), f(min(1, t + e))
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

def scute(x, y, w, h, ang, far=False):
    """keeled oval osteoderm"""
    t = f'transform="rotate({ang:.1f} {x:.1f} {y:.1f})"'
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w}" ry="{h}" fill="{BONE}" {t}></ellipse>'
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w}" ry="{h}" fill="{LOOK.url("shade")}" {t}></ellipse>'
            f'<ellipse cx="{x:.1f}" cy="{y+h*0.35:.1f}" rx="{w*0.9:.1f}" ry="{h*0.55:.1f}" fill="{D}" opacity="0.18" {t}></ellipse>'
            f'<path d="M{x-w*0.7:.1f} {y:.1f} L{x+w*0.7:.1f} {y:.1f}" stroke="#FFF2D6" stroke-width="1.6" opacity="0.55" stroke-linecap="round" {t}></path>'
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w}" ry="{h}" fill="none" stroke="{OL}" stroke-width="2" {t}></ellipse>'
            + (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w}" ry="{h}" fill="{D}" opacity="0.3" {t}></ellipse>' if far else ""))

def nails(xf, y=500):
    return "".join(path(f"M{xf-6} {y-6+k*8} C{xf+2} {y-8+k*8} {xf+8} {y-3+k*8} {xf+8} {y+2+k*8} C{xf+2} {y+3+k*8} {xf-4} {y+3+k*8} {xf-6} {y+1+k*8} Z", NAIL) for k in (0, 1, 2))

# ---------------- osteoderm armour: four rows of stubby keeled osteoderms following the back line, spaced apart
def armour():
    out = []
    rows = [(12, 14, 8, 0.08, 0.92, 7), (42, 13, 7, 0.12, 0.88, 6), (72, 11, 6, 0.16, 0.84, 6), (100, 8, 5, 0.2, 0.8, 5)]
    for dy, w, h, t0, t1, n in rows:
        for i in range(n):
            t = t0 + (t1 - t0) * i / (n - 1)
            x, y = spine(t)
            ang = tangent(spine, t)
            # push inward along the normal
            a = math.radians(ang + 90)
            out.append(scute(x + math.cos(a) * dy, y + math.sin(a) * dy, w, h, ang))
    return "".join(out)

# ---------------- parts
far_hind = skin_part(LOOK, HIND_D, ao=True, far=True, tex=False) + skin_part(LOOK, HIND_FOOT, ao=True, far=True, tex=False) + nails(506)
far_fore = skin_part(LOOK, FORE_D, ao=True, far=True, tex=False) + skin_part(LOOK, FORE_FOOT, ao=True, far=True, tex=False) + nails(708)
LEG_FAR = f'<g id="leg-far" transform="translate(34 -4)">{far_hind}</g>'
FORELEG_FAR = f'<g id="foreleg-far" transform="translate(30 -4)">{far_fore}</g>'

def tail_top(t):
    return K.bez((330, 280), (270, 270), (210, 286), (126, 294), t)
tail_scutes = "".join(scute(*tail_top(t), 9 - 4 * t, 5, tangent(tail_top, t)) for t in (0.1, 0.3, 0.5, 0.7, 0.88))
tail_side = "".join(scute(*[a + b for a, b in zip(tail_top(t), (0, 30 - 18 * t))], 7 - 3 * t, 4, tangent(tail_top, t)) for t in (0.2, 0.42, 0.64))
# two large paired osteoderms make the knob, small ones line the midline and tip
club = (path(CLUB_D, BONE) + path(CLUB_D, LOOK.url("shade")) + path(CLUB_D, LOOK.url("light"))
        + line("M92 288 C96 298 96 312 92 322", 0.35, 2.2)
        + "".join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="2.6" fill="{D}" opacity="0.16"></ellipse>' for x, y in [(56, 300), (54, 310), (64, 296)])
        + line("M62 304 C70 300 80 300 86 304 M100 302 C110 298 122 298 130 302", 0.2, 1.6)
        + stroke(CLUB_D, 3))
tail_inner = (skin_part(LOOK, TAIL_D,
                        belly="M126 314 C210 314 270 334 332 368 L332 352 C270 322 210 308 128 308 Z",
                        layers=stripes([(180, 284, 10, 8), (230, 278, 13, 9), (280, 274, 16, 11)])
                        + spots([(140, 296), (330, 290), (330, 350), (140, 312)], 10, 2, 4, 0.12, 21),
                        outline_d=TAIL_D.rstrip(" Z"), fade=True, rim_d=TAIL_TOP)
              + tail_scutes + tail_side + club
              + f'<g class="{C}-flush" opacity="0"><path d="{TAIL_D} {CLUB_D}" fill="{D}"></path></g>')
TAIL = piv("tail", f"{C}-tail", 320, 316, tail_inner)

body_inner = (skin_part(
    LOOK, BODY_D,
    belly="M788 356 C782 396 752 416 700 424 C600 434 480 434 400 422 C350 414 316 382 304 342 L318 338 C334 376 366 400 410 406 C490 416 600 416 690 406 C738 398 772 380 784 350 Z",
    layers=(stripes([(380, 246, 30, 13), (450, 228, 34, 14), (530, 224, 36, 15), (604, 230, 34, 14), (668, 250, 30, 13)], 0.22)
            + spots([(310, 300), (520, 236), (760, 300), (780, 380), (600, 424), (420, 414), (310, 350)], 22, 3, 6, 0.12, 7)
            + armour()
            + line("M560 404 C578 410 600 412 622 410 M574 416 C590 420 608 420 626 418", 0.18, 2)),
    outline_d=BODY_D.rstrip(" Z"), rim_d=BODY_TOP))
BODY = piv("body", f"{C}-body", 540, 420, body_inner)

LEG_NEAR = ('<g id="leg-near">' + skin_part(LOOK, HIND_D, light=True, ao=True,
            layers=line("M436 446 C448 452 464 454 478 452 M434 462 C446 468 464 470 478 468", 0.22, 1.8),
            rim_d="M404 316 C440 300 504 310 520 350")
            + skin_part(LOOK, HIND_FOOT, ao=True) + nails(506) + "</g>")
FORELEG_NEAR = ('<g id="foreleg-near">' + skin_part(LOOK, FORE_D, ao=True,
                layers=line("M656 448 C668 454 684 456 698 452 M654 462 C666 468 684 470 698 466", 0.22, 1.8))
                + skin_part(LOOK, FORE_FOOT, ao=True) + nails(708) + "</g>")

# neck with two half-rings of keeled osteoderms
ring_band = lambda d: path(d, D, 0.22) + stroke(d, 1.6, OL, 0.6)
neck_rings = (ring_band("M746 292 C758 290 772 293 782 298 C784 316 782 336 778 352 C768 350 758 346 750 340 C746 324 744 306 746 292 Z")
              + "".join(scute(x, y, w, 6, a) for x, y, w, a in [(764, 296, 11, 6), (777, 318, 8, 84), (775, 338, 7, 92)])
              + ring_band("M796 306 C808 310 818 318 826 326 C826 344 822 362 816 374 C806 370 798 364 792 358 C792 340 794 322 796 306 Z")
              + "".join(scute(x, y, w, 6, a) for x, y, w, a in [(810, 312, 11, 30), (820, 336, 8, 86), (817, 356, 7, 96)]))
horn_sq = "M846 318 L798 300 L830 342 Z"     # squamosal horn, top back of skull
horn_qj = "M852 392 C844 402 834 410 822 416 C824 404 828 392 834 382 Z"      # quadratojugal horn, cheek
skull_tiles = "".join(path(f"M{x} {y} l9 -4 l9 3 l-1 8 l-10 3 l-8 -4 Z", D, 0.14) + stroke(f"M{x} {y} l9 -4 l9 3 l-1 8 l-10 3 l-8 -4 Z", 1.2, OL, 0.5)
                      for x, y in [(836, 324), (858, 316), (882, 316), (906, 322), (926, 334), (842, 340), (912, 346)])
head_inner = (
    skin_part(LOOK, NECK_D, belly="M848 402 C812 406 772 398 738 382 L744 368 C776 384 812 392 844 390 Z",
              layers=dots([(740, 380), (790, 396), (840, 400), (840, 392), (790, 388), (740, 372)], 18, 1.2, 2.2, 0.22, 9),
              outline_d="M736 290 C780 292 818 312 842 336 M848 402 C812 406 772 398 744 386",
              rim_d="M738 292 C780 294 816 312 838 334")
    + neck_rings
    + path(horn_sq, BONE) + path(horn_sq, LOOK.url("shade")) + stroke(horn_sq, 2.2)
    + skin_part(LOOK, HEAD_D, belly="M866 410 C902 412 942 406 958 388 L952 384 C936 398 900 402 866 402 Z",
                layers=path("M818 322 C852 304 906 308 940 330 L934 336 C902 316 856 314 824 332 Z", D, 0.18)
                + skull_tiles
                + line("M860 398 C894 402 928 398 956 386", 0.45, 2.2),
                rim_d="M820 320 C854 304 904 308 936 326", light=True)
    + path(horn_qj, BONE) + path(horn_qj, LOOK.url("shade")) + stroke(horn_qj, 2.2)
    + path("M942 348 C960 354 970 372 962 390 C954 396 942 396 932 392 Z", BEAK) + stroke("M942 348 C960 354 970 372 962 390 C954 396 942 396 932 392", 2.2)
    + f'<ellipse cx="930" cy="374" rx="7" ry="4" fill="#1E1416" transform="rotate(28 930 374)"></ellipse>'
    + path("M914 366 C922 356 938 356 946 364 C938 364 926 366 918 372 Z", D, 0.3) + stroke("M914 366 C922 356 938 356 946 364", 1.8)
    + eye(880, 352, f"{C}-eyelid", 4.8)
    + path("M864 346 C870 336 890 334 902 342 C902 344 900 346 898 346 C888 340 874 342 868 350 Z", D, 0.45)
)
HEAD = piv("head", f"{C}-head", 740, 330, head_inner)

SHADOW = '<ellipse cx="540" cy="514" rx="330" ry="12" fill="#000000" opacity="0.3"></ellipse>'
ANIMAL = SHADOW + LEG_FAR + FORELEG_FAR + TAIL + BODY + LEG_NEAR + HEAD + FORELEG_NEAR
FRAG = piv("act", f"{C}-act", 540, 514, ANIMAL)


# ------------------------------------------------------------------ motion
# the club swung side to side; seen from the side the tail foreshortens and darkens as it swings away, then whips back
ACTION = {
    "tail": [(0, "rotate(0) scaleX(1)"), (0.24, "rotate(3deg) scaleX(0.78)"), (0.4, "rotate(3deg) scaleX(0.78)"),
             (0.5, "rotate(-2deg) scaleX(1.03)"), (0.6, "rotate(-1deg) scaleX(0.86)"), (0.74, "rotate(1deg) scaleX(1.01)"),
             (0.88, "rotate(0) scaleX(0.98)"), (1, "rotate(0) scaleX(1)")],
    "head": [(0, "rotate(0)"), (0.24, "rotate(-3deg)"), (0.5, "rotate(2deg)"), (0.7, "rotate(1deg)"), (1, "rotate(0)")],
    "flush": [(0, "0"), (0.24, "0.3"), (0.4, "0.3"), (0.5, "0"), (1, "0")],
    "act": [(0, "translateX(0)"), (0.48, "translateX(0)"), (0.54, "translateX(-6px)"), (0.68, "translateX(0)"), (1, "translateX(0)")],
}
GSAP = """      .to(parts.tail, { rotation: 3, scaleX: 0.78, duration: 0.4, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -3, duration: 0.35, ease: 'power2.out' }, 0)
      .to(document.querySelectorAll('.ank-flush'), { opacity: 0.3, duration: 0.35 }, 0)
      .to(parts.tail, { rotation: -2, scaleX: 1.03, duration: 0.16, ease: 'power3.in' }, 0.64)
      .to(document.querySelectorAll('.ank-flush'), { opacity: 0, duration: 0.16 }, 0.64)
      .to(parts.head, { rotation: 2, duration: 0.2, ease: 'power2.out' }, 0.64)
      .to(parts.act, { x: -6, duration: 0.1, yoyo: true, repeat: 1, ease: 'power1.out' }, 0.8)
      .to(parts.tail, { rotation: 0, scaleX: 1, duration: 0.8, ease: 'elastic.out(1, 0.5)' }, 0.82)
      .to(parts.head, { rotation: 0, duration: 0.5, ease: 'power2.inOut' }, 1.0)"""

# ------------------------------------------------------------------ poster scene: Hell Creek floodplain (src/scenery.py)
SCENE = scenery.set_hell_creek()

# ------------------------------------------------------------------ rig sheet parts (viewBox crops in drawing units)
RIG = [
    ("Body and armour", "#body", BODY, (290, 206, 510, 236)),
    ("Tail and club", "#tail", TAIL, (30, 256, 316, 124)),
    ("Head and neck", "#head", HEAD, (722, 282, 256, 156)),
    ("Hind legs", "#leg-near, #leg-far", LEG_NEAR + f'<g transform="translate(150 0)">{LEG_FAR}</g>', (378, 290, 330, 230)),
    ("Forelegs", "#foreleg-near, #foreleg-far", FORELEG_NEAR + f'<g transform="translate(60 0)">{FORELEG_FAR}</g>', (630, 340, 200, 180)),
]

SPEC = dict(
    code=C, slug="ankylosaurus", board="Ankylosaurus", name="Ankylosaurus", short="Ankylosaurus", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "tail", "head", "leg-near", "leg-far", "foreleg-near", "foreleg-far"],
    action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the Ankylosaurus swing its tail club", action_verb="swing its tail club", page_bg="#DCD3BF",
    scene=SCENE, title="Ankylosaurus", title_px=170, binomial="Ankylosaurus magniventris", subtitle="the fused lizard",
    paragraph="A low, broad plant eater covered in bony armour, with horned corners on its skull and a heavy club of bone at the end of a stiff tail.",
    facts=[("6–8 m", "snout to tail tip"), ("70–66", "million years ago"), ("60 cm", "tail club length")],
    footer="The first skeleton was found in 1906 in the Hell Creek Formation of Montana; others come from Wyoming, Alberta and Saskatchewan.",
    hint="Tap the Ankylosaurus to swing its club", skin_swatches=["#8C6F48", "#7A8450", "#5E7E7A", "#9E6B7B"],
    dino_top=262, rig_parts=RIG, rig_h=960,
)

if __name__ == "__main__":
    frag = K.write_all(SPEC)
    K.poster_board(SPEC, frag)
    K.rig_board(SPEC, frag)
    print(K.shoot("ankylosaurus-animated.svg", 1000, 560))
    print(K.shoot("ankylosaurus-poster", 1080, 1350))
    print(K.shoot("ankylosaurus-rig", 1700, 960))
