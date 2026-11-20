import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Spinosaurus for the dinosaur series. Building SPEC has no side effects; run as a script to write outputs.
Anatomy: a 14 m, 7.4 t biped standing with its weight over the hips (Sereno et al. 2022); short hind legs with
long, flat-bottomed toes; robust three-fingered arms with an enlarged thumb claw; a long, low, crocodile-like skull
with straight conical teeth, a notch near the jaw tip and nostrils set well back; an S-curved neck; a thin sail of
neural spines up to about 1.65 m, peaking over the rear of the back (its exact outline is unknown); and a deep,
paddle-like tail built from tall neural spines and long chevrons (Ibrahim et al. 2020)."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, D, OL, path, stroke, line, rim, piv, skin_part, stripes, spots, dots, eye

C = "spn"
LOOK = K.Look(C, skin="#A0694A", belly="#E2D3B4", accent="#D9A441")
CLAW, TOOTH, SAIL_BAND = "#3A2A2C", "#EFE6D0", "#5A3326"

def bez(p0, p1, p2, p3, t): return K.bez(p0, p1, p2, p3, t)

# ------------------------------------------------------------------ geometry (1000 x 560, ground at 514; about 67 px per metre)
# hind legs: short, about a quarter of body length; long toes with flat-bottomed claws
LEG_D = ("M410 334 C432 300 500 302 514 342 C524 374 514 404 496 420 C500 436 498 452 490 466 "
         "C484 478 482 488 486 496 L494 504 L438 508 C430 500 434 490 442 482 C450 466 452 448 448 432 "
         "C430 420 412 398 406 372 C402 356 404 344 410 334 Z")
FOOT_D = "M434 496 C456 488 502 490 522 498 L540 504 C548 508 546 516 538 516 L440 516 C430 516 426 502 434 496 Z"
TOE_CLAWS = ("M536 502 C546 502 552 508 552 512 C548 514 542 514 536 512 Z "
             "M518 504 C526 504 532 508 532 512 C528 514 522 514 518 512 Z "
             "M500 506 C507 506 512 509 512 513 C508 514 503 514 500 513 Z")

def leg(gid, far=False, dx=0):
    t = f' transform="translate({dx} -4)"' if dx else ""
    out = skin_part(LOOK, LEG_D, ao=True, far=far, tex=not far, outline_d=K_open(LEG_D),
                    layers="" if far else line("M452 452 C466 458 480 458 492 454 M452 466 C466 472 478 472 490 468 M488 412 C500 420 510 418 516 410", 0.22, 1.8),
                    rim_d=None if far else "M420 324 C444 304 496 306 512 336")
    out += skin_part(LOOK, FOOT_D, ao=True, far=far, tex=False)
    out += path(TOE_CLAWS, CLAW) + stroke(TOE_CLAWS, 1.6)
    return f'<g id="{gid}"{t}>{out}</g>'

def K_open(d):
    """limb outline without the arc where it meets the body"""
    head, rest = d.split(" C", 1)
    first_end = " ".join(rest.split(" ")[4:6])
    return "M" + first_end + " C" + rest.split(" C", 1)[1].rstrip(" Z")

LEG_FAR = leg("leg-far", far=True, dx=34)
LEG_NEAR = leg("leg-near")

# arms: robust, three fingers, the first with a large curved claw
ARM_D = ("M662 374 C680 364 698 374 700 392 L714 426 C726 434 736 442 742 450 C746 456 742 462 736 460 "
         "C726 456 714 450 704 444 C694 440 686 430 682 418 L666 398 C658 390 658 380 662 374 Z")
ARM_CLAWS = ("M738 446 C752 448 760 460 756 474 C752 466 746 458 736 454 Z "
             "M738 458 C746 460 750 466 748 472 C744 468 740 464 734 462 Z "
             "M728 458 C735 461 738 467 736 472 C732 468 728 465 724 463 Z")

def arm(gid, cls, far=False, dx=0):
    inner = (skin_part(LOOK, ARM_D, ao=True, far=far, tex=False,
                       layers="" if far else line("M688 410 C696 414 702 420 706 428", 0.2, 1.6))
             + path(ARM_CLAWS, CLAW) + stroke(ARM_CLAWS, 1.6))
    g = piv(gid, cls, 672, 382, f'<g transform="rotate(-30 672 382)">{inner}</g>')   # arms held up, clear of the ground
    return f'<g transform="translate({dx} -6)">{g}</g>' if dx else g

ARM_FAR = arm("arm-far", f"{C}-arm-far", far=True, dx=22)
ARM_NEAR = arm("arm-near", f"{C}-arm")

# ------------------------------------------------------------------ tail: deep and paddle-like, from tall neural spines above and long chevrons below
TAIL_TOP = [((446, 302), (400, 296), (330, 284), (260, 282)), ((260, 282), (190, 282), (120, 300), (56, 330))]
TAIL_BOTTOM = [((60, 342), (120, 344), (190, 348), (260, 350)), ((260, 350), (330, 354), (400, 372), (446, 398))]
TAIL_D = ("M446 302 C400 296 330 284 260 282 C190 282 120 300 56 330 C50 334 52 342 60 342 "
          "C120 344 190 348 260 350 C330 354 400 372 446 398 Z")
TAIL_CORE = "M446 316 C380 314 300 312 220 316 C160 320 110 326 64 334 L66 338 C120 338 200 336 270 338 C340 342 400 358 446 382 Z"
def curve_y(segs, x):
    """y of a pair of cubic segments at x (sampled)"""
    pts = [K.bez(*s, k / 40) for s in segs for k in range(41)]
    return min(pts, key=lambda p: abs(p[0] - x))[1]
def tail_spines():
    """tall neural spines above the tail core and long chevrons below it, seen through the skin"""
    out = []
    for x in range(96, 440, 22):
        top, bot = curve_y(TAIL_TOP, x), curve_y(TAIL_BOTTOM, x)
        core_top = 316 + (0 if x > 220 else (220 - x) * 0.1)
        if core_top - top > 8: out.append(f"M{x} {top + 4:.0f} L{x + 3} {core_top:.0f}")
        core_bot = 338 + max(0, x - 270) * 0.25
        if bot - core_bot > 8: out.append(f"M{x} {core_bot:.0f} L{x - 3} {bot - 4:.0f}")
    return line(" ".join(out), 0.16, 1.6)
TAIL = piv("tail", f"{C}-tail", 440, 340, skin_part(
    LOOK, TAIL_D,
    belly="M60 342 C120 344 190 348 260 350 C330 354 400 372 446 398 L446 384 C400 360 330 342 260 340 C190 338 120 336 66 336 Z",
    layers=path(TAIL_D, D, 0.12) + path(TAIL_CORE, SKIN) + path(TAIL_CORE, LOOK.url("shade"))
           + tail_spines()
           + stripes([(140, 300, 10, 9), (200, 290, 14, 11), (260, 286, 16, 12), (320, 290, 18, 13), (380, 298, 18, 13)], 0.28)
           + dots([(70, 334), (240, 292), (440, 310), (440, 386), (240, 344), (80, 340)], 90, seed=31),
    fade=True, outline_d=TAIL_D.rstrip(" Z"), rim_d="M446 302 C400 296 330 284 260 282 C190 282 120 300 56 330"))

# ------------------------------------------------------------------ body with the sail
BODY_D = ("M430 304 C500 296 600 300 662 314 C690 322 708 344 706 372 C704 400 684 420 650 428 "
          "C590 438 520 436 470 420 C440 410 424 380 424 350 C424 330 426 314 430 304 Z")
BODY_TOP = "M430 304 C500 296 600 300 662 314 C690 322 708 344 706 372"
# thin sail of neural spines; tallest over the rear of the back, sloping down toward the shoulders
SAIL_D = ("M704 336 C684 304 644 266 596 234 C560 210 526 194 498 190 C474 188 456 200 448 224 "
          "C440 250 434 280 430 306 C520 296 610 300 704 336 Z")
SAIL_EDGE = "M704 336 C684 304 644 266 596 234 C560 210 526 194 498 190 C474 188 456 200 448 224 C440 250 434 280 430 306"
def sail_spines():
    out = []
    for i in range(13):
        t = 0.04 + 0.9 * i / 12
        if t < 0.55:
            x, y = bez((704, 336), (684, 304), (644, 266), (596, 234), t / 0.55)
        else:
            x, y = bez((596, 234), (560, 210), (526, 194), (498, 190), (t - 0.55) / 0.45)
        base_y = 300 + (x - 430) * 0.05 + max(0, x - 640) * 0.3
        out.append(f"M{x - 4:.0f} {y + 6:.0f} L{x - 2:.0f} {base_y:.0f}")
    for x, y in [(486, 196), (466, 210), (452, 236), (444, 262)]:
        out.append(f"M{x} {y + 6} L{x - 4} {302}")
    return line(" ".join(out), 0.2, 2)
SAIL = (path(SAIL_D, SKIN) + path(SAIL_D, LOOK.accent, 0.35)
        + path("M698 330 C680 304 642 270 598 242 C564 220 530 206 504 202 C482 200 466 210 458 230 C452 248 448 266 446 284 "
               "C452 262 458 244 468 232 C478 222 492 218 508 218 C534 220 566 234 598 254 C640 280 676 310 698 330 Z", SAIL_BAND, 0.45)
        + sail_spines() + path(SAIL_D, LOOK.url("shade")) + rim(SAIL_EDGE, 3.2, 4, 0.55) + stroke(SAIL_EDGE))
BODY = piv("body", f"{C}-body", 560, 430, SAIL + skin_part(
    LOOK, BODY_D,
    belly="M706 372 C704 400 684 420 650 428 C590 438 520 436 470 420 C440 410 424 380 424 350 L438 350 C440 378 456 400 480 408 C530 420 590 420 646 410 C676 402 694 388 700 366 Z",
    layers=path(BODY_TOP + " L696 380 C692 352 676 336 656 330 C600 316 510 312 434 320 Z", D, 0.22)
           + stripes([(450, 306, 26, 12), (500, 302, 30, 13), (550, 302, 32, 14), (600, 306, 30, 13), (646, 316, 26, 12)], 0.3)
           + spots([(436, 312), (600, 306), (700, 350), (660, 420), (500, 424), (432, 380)], 18, 3, 6, 0.12, 7)
           + line("M600 316 C610 350 608 390 596 424 M550 312 C560 350 560 392 550 428", 0.06, 2.2),
    outline_d=BODY_D.rstrip(" Z"), rim_d=BODY_TOP))

# ------------------------------------------------------------------ neck, head and jaw (long, low skull like a crocodile's)
def teeth(xs, y_of, down=True, size=6):
    d = []
    for x in xs:
        y = y_of(x); s = size * (1.4 if x > 920 else 1.0)
        d.append(f"M{x - 2.4:.1f} {y:.1f} L{x:.1f} {y + (s if down else -s):.1f} L{x + 2.4:.1f} {y:.1f} Z")
    return path(" ".join(d), TOOTH) + stroke(" ".join(d), 1, OL, 0.6)

UPPER_JAW_Y = lambda x: 252 + (x - 800) * 0.09 - (5 if 918 < x < 934 else 0)   # notch behind the enlarged front teeth
LOWER_JAW_Y = lambda x: 260 + (x - 800) * 0.085

JAW_D = "M798 248 C840 258 900 266 942 270 C950 272 950 280 940 284 C900 286 850 282 816 274 C800 270 792 260 798 248 Z"
JAW = piv("jaw", f"{C}-jaw", 806, 252,
    path("M808 254 C850 262 900 268 938 272 L936 276 C900 274 850 270 810 262 Z", "#5A2A26")
    + teeth(range(826, 946, 10), LOWER_JAW_Y, down=False, size=5)
    + skin_part(LOOK, JAW_D, belly="M816 274 C850 282 900 286 940 284 C946 282 948 278 946 276 C930 280 900 280 850 276 C836 274 824 272 816 270 Z", tex=False)
    + line("M816 268 C860 274 904 278 938 278", 0.3, 1.6))

# the bump on top is the small crest in front of the eye
SKULL_D = ("M796 222 C810 210 826 204 838 202 C846 194 856 196 860 208 C888 218 918 234 944 250 C954 256 956 266 948 270 "
           "C934 266 926 262 918 262 C890 260 856 258 830 256 C812 254 798 248 794 238 C792 232 792 226 796 222 Z")
HEAD = piv("head", f"{C}-head", 806, 240,
    JAW
    + teeth([*range(818, 916, 9), 922, 932, 942], UPPER_JAW_Y, down=True, size=6)
    + skin_part(LOOK, SKULL_D,
                layers=path("M796 222 C810 210 826 204 838 202 C846 194 856 196 860 208 C888 218 918 234 944 250 L936 252 C912 238 884 226 858 220 C836 214 814 218 800 230 Z", D, 0.22)
                       + path("M872 222 C880 218 890 220 896 226 C888 226 880 226 874 226 Z", "#2A1C22", 0.75)       # nostril, set well back
                       + dots([(800, 226), (860, 210), (944, 254), (900, 258), (820, 252)], 50, 0.6, 1.2, 0.14, 33)
                       + line("M812 246 C850 254 900 258 944 264", 0.35, 1.6),
                light=True, rim_d="M798 220 C818 204 842 200 862 206 C890 216 920 232 944 248")
    + eye(828, 222, f"{C}-eyelid", 4.6)
    + path("M816 216 C822 208 836 206 846 212 C846 214 844 216 842 216 C834 212 824 214 820 220 Z", D, 0.45))

NECK_D = ("M640 304 C680 290 716 264 748 238 C770 220 792 212 812 218 L822 262 C800 266 782 278 766 298 "
          "C746 326 724 360 706 384 C690 360 664 330 640 304 Z")
NECK = piv("neck", f"{C}-neck", 676, 334, skin_part(
    LOOK, NECK_D,
    belly="M822 262 C800 266 782 278 766 298 C746 326 724 360 706 384 L696 372 C714 348 734 318 752 294 C770 272 790 258 814 252 Z",
    layers=path("M640 304 C680 290 716 264 748 238 C770 220 792 212 812 218 L806 228 C788 226 770 234 754 248 C724 274 690 300 650 314 Z", D, 0.22)
           + stripes([(690, 286, 20, 11), (722, 262, 18, 10), (754, 238, 15, 9), (782, 222, 12, 8)], 0.28)
           + dots([(650, 306), (760, 236), (812, 224), (760, 300), (712, 372)], 70, seed=35),
    outline_d="M640 304 C680 290 716 264 748 238 C770 220 792 212 812 218 M822 262 C800 266 782 278 766 298 C746 326 724 360 706 384",
    rim_d="M644 300 C682 286 716 260 748 236 C768 220 788 212 808 216")
    + HEAD)

SHADOW = '<ellipse cx="500" cy="514" rx="320" ry="12" fill="#000000" opacity="0.3"></ellipse>'
ANIMAL = SHADOW + LEG_FAR + ARM_FAR + TAIL + BODY + LEG_NEAR + NECK + ARM_NEAR
FRAG = piv("act", f"{C}-act", 500, 514, ANIMAL)

# ------------------------------------------------------------------ motion: a quick strike at a fish, jaws snapping shut
ACTION = {
    "neck": [(0, "rotate(0)"), (0.2, "rotate(-6deg)"), (0.42, "rotate(16deg)"), (0.62, "rotate(16deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.2, "rotate(-4deg)"), (0.42, "rotate(10deg)"), (0.62, "rotate(8deg)"), (1, "rotate(0)")],
    "jaw": [(0, "rotate(0)"), (0.2, "rotate(16deg)"), (0.4, "rotate(18deg)"), (0.46, "rotate(0)"), (1, "rotate(0)")],
    "tail": [(0, "rotate(0)"), (0.42, "rotate(-4deg)"), (0.62, "rotate(-4deg)"), (1, "rotate(0)")],
    "act": [(0, "translateX(0)"), (0.2, "translateX(-6px)"), (0.42, "translateX(12px)"), (0.62, "translateX(12px)"), (1, "translateX(0)")],
}
GSAP = """      .to(parts.neck, { rotation: -6, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -4, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.jaw, { rotation: 17, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.act, { x: -6, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.neck, { rotation: 16, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.head, { rotation: 10, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.act, { x: 12, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.tail, { rotation: -4, duration: 0.32, ease: 'power2.out' }, 0.32)
      .to(parts.jaw, { rotation: 0, duration: 0.08, ease: 'power4.in' }, 0.66)
      .to([parts.neck, parts.head, parts.tail], { rotation: 0, duration: 0.6, ease: 'power2.inOut' }, 1.0)
      .to(parts.act, { x: 0, duration: 0.6, ease: 'power2.inOut' }, 1.0)"""

# ------------------------------------------------------------------ poster scene: Kem Kem river margin, tidal flats and mangroves
def mangrove(x, base, h, sc, color):
    roots = "".join(f'<path d="M{x + dx * sc:.0f} {base} C{x + dx * sc * 0.6:.0f} {base - 24 * sc:.0f} {x + dx * 0.2 * sc:.0f} {base - 40 * sc:.0f} {x} {base - 46 * sc:.0f}" fill="none" stroke="{color}" stroke-width="{4 * sc:.1f}"></path>'
                    for dx in (-40, -24, -8, 10, 26, 42))
    crown = "".join(f'<ellipse cx="{x + dx * sc:.0f}" cy="{base - h + dy * sc:.0f}" rx="{r * sc:.0f}" ry="{r * 0.6 * sc:.0f}" fill="{color}"></ellipse>'
                    for dx, dy, r in [(-40, 26, 44), (34, 22, 46), (0, 0, 54), (-8, 34, 40)])
    return f'{roots}<path d="M{x - 5 * sc:.0f} {base - 44 * sc:.0f} L{x - 3 * sc:.0f} {base - h + 20 * sc:.0f} L{x + 3 * sc:.0f} {base - h + 20 * sc:.0f} L{x + 5 * sc:.0f} {base - 44 * sc:.0f} Z" fill="{color}"></path>{crown}'

SCENE = f'''<svg aria-hidden="true" viewBox="0 0 1080 900" width="1080" height="900" style="position: absolute; top: 0; left: 0; display: block">
<defs>
<linearGradient id="spn-sc-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFCFD3"></stop><stop offset="0.55" stop-color="#E9DCC0"></stop><stop offset="0.78" stop-color="#F2CF98"></stop></linearGradient>
<radialGradient id="spn-sc-sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF2D2" stop-opacity="0.95"></stop><stop offset="0.3" stop-color="#FFD596" stop-opacity="0.45"></stop><stop offset="1" stop-color="#FFD596" stop-opacity="0"></stop></radialGradient>
<linearGradient id="spn-sc-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4E0BE" stop-opacity="0"></stop><stop offset="0.6" stop-color="#F4E0BE" stop-opacity="0.55"></stop><stop offset="1" stop-color="#F4E0BE" stop-opacity="0"></stop></linearGradient>
<linearGradient id="spn-sc-water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C8D6D2"></stop><stop offset="1" stop-color="#8FAAA6"></stop></linearGradient>
<linearGradient id="spn-sc-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#2E2414" stop-opacity="0.36"></stop></linearGradient>
<radialGradient id="spn-sc-shadow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#2E2414" stop-opacity="0.4"></stop><stop offset="1" stop-color="#2E2414" stop-opacity="0"></stop></radialGradient>
</defs>
<rect x="0" y="0" width="1080" height="900" fill="url(#spn-sc-sky)"></rect>
<circle cx="200" cy="600" r="320" fill="url(#spn-sc-sun)"></circle>
<g opacity="0.65">{mangrove(80, 676, 150, 0.9, "#7D8A6A")}{mangrove(190, 680, 120, 0.7, "#7D8A6A")}{mangrove(900, 678, 170, 1.0, "#7D8A6A")}{mangrove(1010, 682, 130, 0.8, "#7D8A6A")}</g>
<rect x="0" y="640" width="1080" height="60" fill="#B7B79A" opacity="0.6"></rect>
<rect x="0" y="590" width="1080" height="150" fill="url(#spn-sc-haze)"></rect>
<path d="M0 696 C220 688 460 700 700 692 C860 686 980 692 1080 688 L1080 900 L0 900 Z" fill="url(#spn-sc-water)"></path>
<path d="M60 720 L220 718 M420 730 L640 726 M820 716 L980 714 M140 770 L320 766 M600 780 L760 776" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.45"></path>
<path d="M0 792 C200 776 420 786 640 780 C820 776 960 784 1080 778 L1080 900 L0 900 Z" fill="#C9AE78"></path>
<path d="M0 836 C270 830 540 840 810 834 C930 832 1010 836 1080 834 L1080 852 C810 856 540 848 270 854 C160 856 70 852 0 854 Z" fill="#B59766"></path>
<rect x="0" y="780" width="1080" height="120" fill="url(#spn-sc-ground)"></rect>
<ellipse cx="560" cy="836" rx="380" ry="22" fill="url(#spn-sc-shadow)"></ellipse>
<path d="M760 742 C772 734 790 734 800 742 C790 750 772 750 760 742 Z M800 742 L812 734 L812 750 Z" fill="#5E6F6C" opacity="0.5"></path>
</svg>'''

# ------------------------------------------------------------------ rig sheet parts (viewBox crops in drawing units)
RIG = [
    ("Body and sail", "#body", BODY, (418, 180, 300, 266)),
    ("Tail", "#tail", TAIL, (44, 246, 412, 166)),
    ("Neck and head", "#neck, #head, #jaw", NECK, (630, 196, 330, 196)),
    ("Hind legs", "#leg-near, #leg-far", LEG_NEAR + f'<g transform="translate(150 0)">{LEG_FAR}</g>', (396, 296, 330, 224)),
    ("Arms", "#arm-near, #arm-far", ARM_NEAR + f'<g transform="translate(110 0)">{ARM_FAR}</g>', (650, 346, 260, 96)),
]

SPEC = dict(
    code=C, slug="spinosaurus", board="Spinosaurus", name="Spinosaurus", short="Spinosaurus", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "tail", "neck", "head", "jaw", "leg-near", "leg-far", "arm-near", "arm-far"],
    action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the Spinosaurus strike at a fish", action_verb="make it strike", page_bg="#DCD6C4",
    scene=SCENE, title="Spinosaurus", title_px=176, binomial="Spinosaurus aegyptiacus", subtitle="the Egyptian spine lizard",
    paragraph="A long-snouted fish hunter with a tall sail on its back, a deep, paddle-like tail and short hind legs. It stalked the rivers and tidal flats of North Africa.",
    facts=[("14 m", "snout to tail tip"), ("100–94", "million years ago"), ("1.65 m", "longest sail spine")],
    footer="Fossils come from the Kem Kem beds of Morocco and the Bahariya Formation of Egypt, where the first skeleton was found; it was destroyed in 1944.",
    hint="Tap the Spinosaurus to make it strike", skin_swatches=["#A0694A", "#7A8450", "#5E7E7A", "#8A6A3E"],
    dino_top=262, rig_parts=RIG, rig_h=960,
)

if __name__ == "__main__":
    frag = K.write_all(SPEC)
    K.poster_board(SPEC, frag)
    K.rig_board(SPEC, frag)
    print(K.shoot("spinosaurus-animated.svg", 1000, 560))
    print(K.shoot("spinosaurus-poster", 1080, 1350))
    print(K.shoot("spinosaurus-rig", 1700, 960))
