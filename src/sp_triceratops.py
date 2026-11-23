import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Triceratops for the dinosaur series. Import builds SPEC only; run as a script to write outputs."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
import scenery
from dinokit import SKIN, D, L, OL, CLAW, piv, path, stroke, line, rim, stripes, spots, dots, skin_part

C = "tri"
LOOK = K.Look(C, skin="#7A8450", belly="#DCCFA6", accent="#C27A48")
HORN, BEAK = "#E6D9BC", "#4A3A30"

# ------------------------------------------------------------------ legs
# hind legs long and columnar under high hips; forelegs shorter, elbows flexed back (rhino-like stance)
HIND = ("M350 262 C380 226 460 222 492 262 C512 290 510 336 496 364 C490 376 486 388 484 402 "
        "C480 428 476 452 474 474 C474 486 478 492 484 496 L484 508 L410 508 C402 500 404 490 414 484 "
        "C420 466 422 444 416 424 C410 406 398 394 384 382 C362 362 348 330 346 300 C344 284 346 272 350 262 Z")
HIND_FOOT = "M398 494 C410 486 466 486 482 494 C490 500 490 512 482 514 L404 514 C394 514 392 500 398 494 Z"
# hooves: three on each hand, four on each foot (three show on the near side)
HIND_NAIL = "M474 492 C486 492 494 498 494 506 C494 512 488 514 480 514 Z M456 496 C464 496 470 501 470 507 C470 512 465 514 459 514 Z M438 498 C445 498 450 502 450 507 C450 512 446 514 440 514 Z"
FRONT = ("M628 288 C664 276 706 292 708 328 C710 352 700 372 684 386 C674 396 666 404 664 416 "
         "C664 440 668 462 672 480 C676 494 672 506 660 508 L616 508 C606 506 604 496 610 486 "
         "C616 470 614 448 606 430 C594 424 586 412 584 396 C580 370 584 346 592 326 C598 306 610 294 628 288 Z")
FRONT_FOOT = "M602 494 C614 486 658 486 672 494 C680 500 680 512 672 514 L608 514 C598 514 596 500 602 494 Z"
FRONT_NAIL = "M664 492 C676 492 684 498 684 506 C684 512 678 514 670 514 Z M646 496 C654 496 660 501 660 507 C660 512 655 514 649 514 Z M628 498 C635 498 640 502 640 507 C640 512 636 514 630 514 Z"

def open_top(d):
    """outline for a limb: drops the first segment (the arc where it meets the body) and the closing Z"""
    head, rest = d.split(" C", 1)
    first_end = " ".join(rest.split(" ")[4:6])
    return "M" + first_end + " C" + rest.split(" C", 1)[1].rstrip(" Z")

def leg(gid, d, foot, nails, far=False, dx=0, wrinkles=""):
    t = f' transform="translate({dx} -2)"' if dx else ""
    body = skin_part(LOOK, d, ao=True, far=far, tex=not far, outline_d=open_top(d),
                     layers=(line(wrinkles, 0.2, 2) if wrinkles else ""))
    ft = skin_part(LOOK, foot, ao=True, far=far, tex=False)
    nl = path(nails, CLAW) + stroke(nails, 2)
    return f'<g id="{gid}"{t}>{body}{ft}{nl}</g>'

FAR_HIND = leg("leg-far", HIND, HIND_FOOT, HIND_NAIL, far=True, dx=44)
FAR_FRONT = leg("foreleg-far", FRONT, FRONT_FOOT, FRONT_NAIL, far=True, dx=40)
NEAR_HIND = leg("leg-near", HIND, HIND_FOOT, HIND_NAIL,
                wrinkles="M420 448 C434 454 452 456 470 452 M420 462 C434 468 452 470 470 466 M360 296 C372 282 390 272 408 270 M478 380 C488 388 496 388 500 382")
NEAR_FRONT = leg("foreleg-near", FRONT, FRONT_FOOT, FRONT_NAIL,
                 wrinkles="M614 446 C626 452 642 454 662 450 M616 460 C628 466 644 468 664 464 M588 400 C604 410 632 412 662 404")

# ------------------------------------------------------------------ tail
# a fairly short, thick tail that slopes down from the hips
TAIL_D = "M356 214 C304 230 226 288 146 352 C130 364 136 378 152 372 C232 344 302 350 352 364 Z"
TAIL_OPEN = "M356 214 C304 230 226 288 146 352 C130 364 136 378 152 372 C232 344 302 350 352 364"
TAIL = piv("tail", f"{C}-tail", 340, 290, skin_part(
    LOOK, TAIL_D,
    belly="M152 372 C232 344 302 350 352 364 L352 346 C300 334 232 330 162 356 Z",
    layers=stripes([(212, 306, 10, 9), (258, 270, 14, 11), (302, 238, 18, 12), (336, 222, 20, 13)], 0.3)
           + line("M340 300 C290 306 220 326 170 352", 0.12, 2.2),
    fade=True, outline_d=TAIL_OPEN, rim_d="M356 214 C304 230 226 288 146 352"))

# ------------------------------------------------------------------ body
# deep, barrel-shaped trunk; the back is highest over the hips and slopes down to the shoulders
BODY_D = "M300 262 C318 226 352 206 392 204 C470 200 560 214 630 240 C676 258 708 284 718 320 C728 360 716 396 686 414 C640 436 560 438 490 430 C420 422 362 400 330 364 C306 336 294 298 300 262 Z"
BODY_OPEN = "M392 204 C470 200 560 214 630 240 C676 258 708 284 718 320 C728 360 716 396 686 414 C640 436 560 438 490 430 C420 422 362 400 330 364"
BODY_TOP = "M300 262 C318 226 352 206 392 204 C470 200 560 214 630 240 C676 258 708 284 718 320"
BODY_POLY = [(320, 262), (392, 214), (560, 222), (690, 280), (712, 340), (680, 404), (540, 424), (380, 394), (320, 330)]
BODY = piv("body", f"{C}-body", 520, 420, skin_part(
    LOOK, BODY_D,
    belly="M722 340 C728 370 712 398 686 414 C640 436 560 438 490 430 C420 422 362 400 330 364 L340 352 C372 384 424 402 490 410 C560 418 636 416 676 398 C702 384 716 362 722 340 Z",
    layers=path(BODY_TOP + " L708 330 C700 296 670 272 626 258 C560 234 470 224 394 226 C356 228 326 246 310 272 Z", D, 0.24)
           + stripes([(380, 216, 34, 15), (430, 212, 42, 17), (480, 214, 46, 18), (530, 220, 46, 18), (580, 232, 42, 17), (626, 250, 36, 15), (664, 272, 30, 13)], 0.3)
           + spots(BODY_POLY, 22, 3, 6.5, 0.13, seed=8) + dots(BODY_POLY, 220, seed=9)
           # feature scales: large, widely spaced, cone-tipped (Lane specimen)
           + "".join(f'<path d="M{x-7} {y} l3.5 -6 h7 l3.5 6 l-3.5 6 h-7 Z" fill="#000" opacity="0.14"></path><circle cx="{x}" cy="{y-1}" r="2.2" fill="#FFF0D8" opacity="0.45"></circle>'
                     for x, y in [(410, 250), (480, 236), (550, 244), (620, 266), (676, 300), (440, 300), (520, 292), (600, 310), (670, 346), (480, 352), (560, 360), (640, 376), (380, 330)])
           + line("M610 268 C622 310 622 356 608 404 M560 254 C572 296 574 344 562 396", 0.06, 2.4)
           + line("M540 416 C556 424 574 428 592 428 M552 428 C568 434 584 436 600 434", 0.16, 2),
    outline_d=BODY_OPEN, rim_d=BODY_TOP))

# ------------------------------------------------------------------ head
# skull about a third of body length, carried low; a short, solid frill sweeps up and back over the neck,
# ringed with low, worn epoccipitals as in adults
FRILL_SEGS = [((776, 386), (736, 360), (680, 316), (656, 268)),
              ((656, 268), (640, 232), (646, 198), (676, 188)),
              ((676, 188), (712, 176), (760, 200), (792, 236))]
FRILL_D = "M776 386 C736 360 680 316 656 268 C640 232 646 198 676 188 C712 176 760 200 792 236 C806 252 816 270 822 290 Z"
FRILL_CENTRE = (740, 280)

def frill_bumps():
    pts = []
    for seg, (t0, t1), n in zip(FRILL_SEGS, [(0.3, 1.0), (0.0, 1.0), (0.0, 0.9)], [4, 3, 4]):
        for k in range(n):
            pts.append(K.bez(*seg, t0 + (t1 - t0) * (k + 0.5) / n))
    out = []
    for x, y in pts:
        ang = math.atan2(y - FRILL_CENTRE[1], x - FRILL_CENTRE[0]); ox, oy = math.cos(ang), math.sin(ang)
        tx, ty = -oy, ox
        a = (x + tx * 7 - ox * 3, y + ty * 7 - oy * 3); b = (x - tx * 7 - ox * 3, y - ty * 7 - oy * 3); c = (x + ox * 6, y + oy * 6)
        out.append(f"M{a[0]:.1f} {a[1]:.1f} Q{c[0] + tx * 5:.1f} {c[1] + ty * 5:.1f} {c[0]:.1f} {c[1]:.1f} Q{c[0] - tx * 5:.1f} {c[1] - ty * 5:.1f} {b[0]:.1f} {b[1]:.1f} Z")
    d = " ".join(out)
    return path(d, SKIN) + path(d, D, 0.2) + stroke(d, 2.2)

FRILL_INNER = "M770 366 C734 342 690 306 672 266 C660 238 664 212 686 206 C716 198 754 220 780 250 C792 264 800 280 806 296 Z"
RIBS = " ".join(f"M796 336 L{x:.0f} {y:.0f}" for x, y in [K.bez(*FRILL_SEGS[0], t) for t in (0.5, 0.85)] + [K.bez(*FRILL_SEGS[1], t) for t in (0.3, 0.8)] + [K.bez(*FRILL_SEGS[2], t) for t in (0.3, 0.7)])
FRILL = (frill_bumps() + path(FRILL_D, SKIN) + path(FRILL_D, D, 0.12) + path(FRILL_INNER, LOOK.accent, 0.45)
         + path(FRILL_INNER, LOOK.url("light")) + stroke(RIBS, 2.2, D, 0.14)
         + dots([(670, 250), (690, 200), (780, 236), (800, 300), (770, 370), (700, 310)], 60, 0.8, 1.6, 0.12, seed=12)
         + path(FRILL_D, LOOK.url("shade")) + rim("M656 268 C640 232 646 198 676 188 C712 176 760 200 792 236", 3.2, 4, 0.55) + stroke(FRILL_D))

NECK_D = "M700 290 C712 302 718 312 720 326 C726 360 720 384 704 404 C730 420 752 424 772 420 L778 362 C764 330 736 304 700 290 Z"
SKULL_D = "M778 298 C800 278 836 272 866 284 C892 296 914 316 930 340 C940 356 948 372 950 386 C944 394 932 394 922 390 C900 394 872 400 842 402 C806 404 780 400 764 388 C752 372 760 318 778 298 Z"
JAW_D = "M796 392 C836 398 884 398 920 390 C932 390 938 398 932 410 C912 430 864 440 824 436 C800 434 786 420 788 406 Z"
BEAK_D = "M908 330 C932 340 952 362 956 386 C956 400 946 406 934 402 L914 394 C924 378 920 350 908 330 Z"   # hooked rostral beak
LBEAK_D = "M910 394 C928 392 940 394 942 400 C936 414 924 422 910 424 Z"
NASAL_D = "M872 300 C876 282 886 266 898 256 C902 272 902 290 896 308 Z"     # short nasal horn above the nostril
NOSTRIL_D = "M884 330 C896 324 910 330 912 342 C906 350 892 350 884 342 Z"
# adult brow horns: about a metre long, angled forward and up
HORN_NEAR = "M808 290 C822 246 852 204 904 176 C886 214 860 256 840 298 Z"
HORN_FAR = "M792 284 C804 240 832 196 880 168 C864 206 842 250 822 292 Z"
JUGAL = "M772 386 C766 402 760 416 756 430 C770 422 780 410 788 396 Z"         # cheek (epijugal) point

def horn(d, far=False):
    return path(d, HORN) + path(d, LOOK.url("ao")) + (path(d, D, 0.3) if far else "") + stroke(d, 2.6)

HEAD_INNER = (
    skin_part(LOOK, NECK_D, belly="M704 404 C730 420 752 424 772 420 L774 404 C752 410 730 404 712 392 Z", outline_d="M704 404 C730 420 752 424 772 420")
    + horn(HORN_FAR, far=True)
    + FRILL
    + skin_part(LOOK, JAW_D, belly="M806 424 C846 436 896 432 928 412 C918 408 892 420 846 422 C826 422 814 420 806 414 Z", tex=False)
    + path(LBEAK_D, BEAK) + stroke(LBEAK_D, 2.4)
    + skin_part(LOOK, SKULL_D,
                layers=path("M778 298 C800 278 836 272 866 284 C892 296 914 316 930 340 L922 346 C906 324 886 306 862 296 C834 286 802 290 784 306 Z", D, 0.22)
                       + path(NOSTRIL_D, D, 0.5)
                       + line("M818 332 C832 346 852 354 874 356", 0.14, 2)
                       + line("M800 398 C840 402 890 398 922 392", 0.4, 2.4)
                       + dots([(780, 300), (860, 284), (930, 344), (900, 392), (790, 392)], 70, 0.8, 1.5, 0.12, seed=13),
                light=True, rim_d="M778 298 C800 278 836 272 866 284 C892 296 914 316 930 340")
    + path(BEAK_D, BEAK) + path(BEAK_D, LOOK.url("shade")) + stroke(BEAK_D, 2.6)
    + horn(NASAL_D)
    + path(JUGAL, SKIN) + path(JUGAL, D, 0.18) + stroke(JUGAL, 2.4)
    + K.eye(818, 316, f"{C}-eyelid", 5)
    + path("M802 308 C810 298 828 296 840 302 C842 304 840 307 838 307 C828 303 814 304 806 312 C804 312 801 310 802 308 Z", D, 0.45)
    + horn(HORN_NEAR)
)
HEAD = piv("head", f"{C}-head", 706, 340, HEAD_INNER)

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

# ------------------------------------------------------------------ poster scene: Hell Creek floodplain (src/scenery.py)
SCENE = scenery.set_hell_creek()

# ------------------------------------------------------------------ rig parts
RIG = [
    ("Head and frill", "#head", HEAD, (630, 160, 340, 290)),
    ("Body", "#body", BODY, (290, 196, 446, 250)),
    ("Tail", "#tail", TAIL, (126, 206, 240, 176)),
    ("Hind legs", "#leg-near, #leg-far", NEAR_HIND + f'<g transform="translate(150 0)">{FAR_HIND}</g>', (336, 218, 364, 302)),
    ("Front legs", "#foreleg-near, #foreleg-far", NEAR_FRONT + f'<g transform="translate(70 0)">{FAR_FRONT}</g>', (576, 280, 250, 240)),
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
