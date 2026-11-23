import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Pachycephalosaurus for the dinosaur series. Building SPEC has no side effects; run as a script to write outputs.
Only the skull of P. wyomingensis is well known, so the body follows related pachycephalosaurs and general
reconstructions: a bipedal, barrel-chested animal about 4.5 m long with a short S-curved neck, small arms, long hind
legs and a long, heavy tail held out level as a counterweight. The skull has a tall, thick, rounded dome (up to about
25 cm of bone), a row of bony nodes across its rear edge, small blunt knobs on the snout, large forward-facing eyes
and a small pointed beak. Whether the dome was used for head-butting is debated; the move is the classic reading."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
import scenery
from dinokit import SKIN, D, OL, path, stroke, line, piv, skin_part, stripes, spots, dots, eye
C = "pch"
LOOK = K.Look(C, skin="#8A6A52", belly="#E6D6B2", accent="#D9C69C")
BONE, NAIL, BEAK = "#D9C69C", "#3A2A2C", "#4A3A30"

# ---------------- geometry (1000 x 560, ground at 514, facing right)
BODY_D = ("M360 306 C398 266 496 254 580 264 C642 272 678 296 686 334 C692 370 666 400 620 412 "
          "C560 426 452 426 402 408 C368 394 350 344 360 306 Z")
BODY_TOP = "M360 306 C398 266 496 254 580 264 C642 272 678 296 686 334"
TAIL_D = ("M374 284 C310 278 226 292 112 326 C108 330 108 334 112 336 C228 342 306 354 380 376 Z")
TAIL_TOP = "M374 284 C310 278 226 292 112 326"
HIND_D = ("M404 322 C446 304 508 318 516 366 C520 400 502 430 486 446 L494 484 L534 498 C546 502 546 514 532 514 "
          "L428 514 C418 512 418 500 430 494 L448 486 L442 452 C420 436 402 402 400 370 C398 350 396 332 404 322 Z")
ARM_D = ("M626 342 C650 338 670 354 668 376 C666 394 658 404 648 410 L652 428 C652 436 644 438 638 434 "
         "L624 406 C616 386 614 354 626 342 Z")
NECK_D = "M644 278 C676 266 714 266 742 278 L750 342 C718 356 682 350 650 338 Z"
HEAD_D = ("M730 300 C736 262 770 242 806 250 C834 256 846 282 848 304 C866 312 876 326 870 340 "
          "C862 352 838 354 818 350 C782 354 746 348 732 332 C726 320 726 308 730 300 Z")
DOME_D = "M736 296 C742 262 772 246 806 252 C830 258 842 280 844 300 C820 292 782 290 750 304 C742 306 738 304 736 296 Z"

def tangent(pts, i):
    a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

def toes(xf, y=506):
    return "".join(path(f"M{xf-6+k*14} {y-4} C{xf+2+k*14} {y-6} {xf+8+k*14} {y-1} {xf+8+k*14} {y+4} "
                        f"C{xf+2+k*14} {y+5} {xf-4+k*14} {y+5} {xf-6+k*14} {y+3} Z", NAIL) for k in (0, 1, 2))

def node(x, y, r, far=False):
    """rounded bony knob"""
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{BONE}"></circle>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{LOOK.url("shade")}"></circle>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{OL}" stroke-width="1.8"></circle>')

# ---------------- legs and arms
far_hind = skin_part(LOOK, HIND_D, ao=True, far=True, tex=False) + toes(496)
LEG_FAR = f'<g id="leg-far" transform="translate(38 -4)">{far_hind}</g>'
far_arm = skin_part(LOOK, ARM_D, ao=True, far=True, tex=False)
ARM_FAR = f'<g id="arm-far" transform="translate(24 -3)">{far_arm}</g>'

tail_inner = skin_part(
    LOOK, TAIL_D,
    belly="M112 336 C228 342 306 354 380 376 L380 360 C306 338 228 332 112 331 Z",
    layers=stripes([(180, 306, 12, 9), (236, 304, 14, 10), (292, 302, 16, 11)])
    + spots([(130, 328), (360, 288), (360, 370), (140, 336)], 10, 2, 4, 0.12, 21),
    outline_d=TAIL_D.rstrip(" Z"), fade=True, rim_d=TAIL_TOP)
TAIL = piv("tail", f"{C}-tail", 372, 320, tail_inner)

body_inner = skin_part(
    LOOK, BODY_D,
    belly="M686 346 C692 372 666 402 620 412 C560 426 452 426 402 408 C368 394 350 344 360 312 L376 320 C378 360 398 392 430 402 C500 416 580 416 626 400 C660 388 678 366 682 342 Z",
    layers=(stripes([(412, 290, 30, 13), (470, 282, 34, 14), (534, 282, 36, 15), (596, 288, 34, 14), (650, 302, 26, 12)], 0.22)
            + spots([(380, 310), (520, 272), (660, 300), (676, 350), (560, 412), (420, 396), (372, 352)], 20, 3, 6, 0.12, 7)
            + line("M520 388 C540 394 566 396 590 392 M530 402 C548 406 570 406 590 404", 0.16, 2)),
    outline_d=BODY_D.rstrip(" Z"), rim_d=BODY_TOP)
BODY = piv("body", f"{C}-body", 520, 420, body_inner)

LEG_NEAR = ('<g id="leg-near">' + skin_part(LOOK, HIND_D, light=True, ao=True,
            layers=line("M444 458 C456 464 472 466 486 464 M442 472 C454 478 472 480 486 478", 0.2, 1.8),
            rim_d="M412 320 C448 304 506 318 516 360") + toes(496) + "</g>")
ARM_NEAR = ('<g id="arm-near">' + skin_part(LOOK, ARM_D, ao=True,
            layers=line("M634 404 C640 410 648 412 652 410", 0.2, 1.6), rim_d="M630 342 C652 338 668 352 668 372")
            + path("M636 428 l-2 8 M642 430 l1 8 M648 428 l3 7", "none") + "</g>")

# ---------------- head: short S-neck, thick domed skull
dome_rows = "".join(
    stroke(f"M{x} {y} C{x+10} {y-8} {x+30} {y-8} {x+44} {y}", 1.4, OL, 0.25)
    for x, y in [(754, 288), (762, 276), (772, 266)])
rear_nodes = "".join(node(x, y, r) for x, y, r in [(730, 304, 5.2), (728, 316, 5.6), (734, 328, 5.2), (746, 338, 4.6)])
snout_knobs = "".join(node(x, y, r) for x, y, r in [(842, 296, 4.2), (855, 306, 4.6), (864, 318, 4.2), (848, 286, 3.6)])
beak = "M850 318 C868 322 878 332 872 344 C866 350 854 350 842 346 C846 338 848 328 850 318 Z"
head_inner = (
    skin_part(LOOK, NECK_D, belly="M750 342 C718 356 682 350 650 338 L656 326 C686 338 718 342 746 330 Z",
              layers=dots([(654, 330), (700, 346), (746, 336), (740, 300), (700, 280), (660, 296)], 16, 1.2, 2.2, 0.2, 9),
              outline_d="M644 278 C676 266 714 266 742 278 M750 342 C718 356 682 350 654 338",
              rim_d="M648 278 C680 268 714 268 738 280")
    + skin_part(LOOK, HEAD_D, belly="M818 350 C838 354 862 352 870 340 L864 336 C858 346 838 348 818 344 Z",
                layers=(path(DOME_D, BONE, 0.9) + path(DOME_D, LOOK.url("shade")) + path(DOME_D, LOOK.url("light"))
                        + dome_rows
                        + stroke(DOME_D.split(" Z")[0].rsplit("C", 1)[0], 0, OL)),
                rim_d="M738 290 C746 262 774 248 806 254 C826 260 838 276 842 294", light=True)
    + path("M744 304 C770 294 810 294 842 304", "none") + stroke("M742 304 C772 292 814 292 844 302", 2.0, OL, 0.65)
    + rear_nodes + snout_knobs
    + path(beak, BEAK) + stroke(beak, 2.2)
    + f'<ellipse cx="858" cy="320" rx="3.2" ry="2.2" fill="#1E1416"></ellipse>'
    + path("M786 308 C794 298 812 298 820 308 C812 308 800 310 792 316 Z", D, 0.32) + stroke("M786 308 C794 298 812 298 820 308", 1.8)
    + eye(802, 316, f"{C}-eyelid", 6.2)
    + f'<g class="{C}-flush" opacity="0"><path d="{DOME_D}" fill="#D9503A"></path></g>'
)
HEAD = piv("head", f"{C}-head", 650, 312, head_inner)

SHADOW = '<ellipse cx="500" cy="514" rx="300" ry="12" fill="#000000" opacity="0.3"></ellipse>'
LIFT = lambda m: f'<g transform="translate(0 -26)">{m}</g>'   # raises the trunk so the hind legs read long
ANIMAL = SHADOW + LEG_FAR + LIFT(ARM_FAR + TAIL + BODY) + LEG_NEAR + LIFT(HEAD + ARM_NEAR)
FRAG = piv("act", f"{C}-act", 500, 514, ANIMAL)


# ------------------------------------------------------------------ motion: head-butt
# rear back, lunge forward with the dome, tail rising as a counterweight, dome flushing, then recover
ACTION = {
    "head": [(0, "rotate(0)"), (0.28, "rotate(-7deg)"), (0.42, "rotate(-7deg)"), (0.52, "rotate(15deg)"),
             (0.6, "rotate(13deg)"), (0.8, "rotate(4deg)"), (1, "rotate(0)")],
    "tail": [(0, "rotate(0)"), (0.28, "rotate(1deg)"), (0.52, "rotate(5deg)"), (0.7, "rotate(4deg)"), (1, "rotate(0)")],
    "flush": [(0, "0"), (0.3, "0.2"), (0.5, "0.65"), (0.66, "0.5"), (1, "0")],
    "act": [(0, "translateX(0)"), (0.28, "translateX(-14px)"), (0.42, "translateX(-14px)"), (0.52, "translateX(26px)"),
            (0.6, "translateX(20px)"), (0.82, "translateX(4px)"), (1, "translateX(0)")],
}
GSAP = """      .to(parts.act, { x: -14, duration: 0.45, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -7, duration: 0.45, ease: 'power2.out' }, 0)
      .to(document.querySelectorAll('.pch-flush'), { opacity: 0.2, duration: 0.45 }, 0)
      .to(parts.act, { x: 26, duration: 0.16, ease: 'power3.in' }, 0.7)
      .to(parts.head, { rotation: 15, duration: 0.16, ease: 'power3.in' }, 0.7)
      .to(parts.tail, { rotation: 5, duration: 0.2, ease: 'power2.out' }, 0.7)
      .to(document.querySelectorAll('.pch-flush'), { opacity: 0.65, duration: 0.16 }, 0.7)
      .to(parts.act, { x: 0, duration: 0.8, ease: 'elastic.out(1, 0.55)' }, 0.95)
      .to(parts.head, { rotation: 0, duration: 0.7, ease: 'power2.inOut' }, 0.98)
      .to(parts.tail, { rotation: 0, duration: 0.7, ease: 'power2.inOut' }, 0.98)
      .to(document.querySelectorAll('.pch-flush'), { opacity: 0, duration: 0.7 }, 1.0)"""

# ------------------------------------------------------------------ poster scene: Hell Creek floodplain (src/scenery.py)
SCENE = scenery.set_hell_creek()

# ------------------------------------------------------------------ rig sheet parts (viewBox crops in drawing units)
RIG = [
    ("Body", "#body", BODY, (346, 246, 354, 190)),
    ("Tail", "#tail", TAIL, (100, 270, 292, 120)),
    ("Head and neck", "#head", HEAD, (636, 236, 252, 134)),
    ("Hind legs", "#leg-near, #leg-far", LEG_NEAR + f'<g transform="translate(150 0)">{LEG_FAR}</g>', (384, 296, 340, 230)),
    ("Arms", "#arm-near, #arm-far", ARM_NEAR + f'<g transform="translate(60 0)">{ARM_FAR}</g>', (600, 326, 150, 120)),
]

SPEC = dict(
    code=C, slug="pachycephalosaurus", board="Pachycephalosaurus", name="Pachycephalosaurus", short="Pachycephalosaurus", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "tail", "head", "leg-near", "leg-far", "arm-near", "arm-far"],
    action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the Pachycephalosaurus head-butt", action_verb="head-butt", page_bg="#DCD3BF",
    scene=SCENE, title="Pachycephalosaurus", title_px=118, binomial="Pachycephalosaurus wyomingensis", subtitle="the thick-headed lizard",
    paragraph="A bipedal plant-and-more eater with a skull roof of solid bone, a crown of bony knobs and a long, level tail for balance.",
    facts=[("4.5 m", "snout to tail tip"), ("68–66", "million years ago"), ("25 cm", "dome thickness, at most")],
    footer="Known mostly from skulls, found in the Hell Creek Formation of Montana and South Dakota and the Lance Formation of Wyoming.",
    hint="Tap the Pachycephalosaurus to head-butt", skin_swatches=["#8A6A52", "#7A8450", "#6E7C8A", "#A06A5E"],
    dino_top=262, rig_parts=RIG, rig_h=960,
)

if __name__ == "__main__":
    frag = K.write_all(SPEC)
    K.poster_board(SPEC, frag)
    K.rig_board(SPEC, frag)
    print(K.shoot("pachycephalosaurus-animated.svg", 1000, 560))
    print(K.shoot("pachycephalosaurus-poster", 1080, 1350))
    print(K.shoot("pachycephalosaurus-rig", 1700, 960))
