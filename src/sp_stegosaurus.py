import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Stegosaurus for the dinosaur series. Building SPEC has no side effects; run as a script to write outputs."""
import sys
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, D, OL, path, stroke, line, rim, piv, skin_part, stripes, spots, dots, spike, eye

def plate(x, y, w, h, lean=-8):
    """broad, round-topped plate standing on (x, y), as on the S. stenops skeleton 'Sophie'"""
    return (f"M{x-.3*w:.1f} {y} C{x-.62*w:.1f} {y-.3*h:.1f} {x-.6*w+lean*.4:.1f} {y-.72*h:.1f} {x-.28*w+lean*.7:.1f} {y-.9*h:.1f} "
            f"C{x-.1*w+lean:.1f} {y-1.0*h:.1f} {x+.1*w+lean:.1f} {y-1.02*h:.1f} {x+.3*w+lean*.7:.1f} {y-.88*h:.1f} "
            f"C{x+.62*w+lean*.4:.1f} {y-.68*h:.1f} {x+.62*w:.1f} {y-.3*h:.1f} {x+.3*w:.1f} {y} Z")

C = "stg"
LOOK = K.Look(C, skin="#5E7E7A", belly="#DCD2B2", accent="#B25C3A")
PLATE, PLATE_RIM, FLUSH, HORN, NAIL, BEAK = "#B25C3A", "#7E3A24", "#E8402A", "#E6D9BC", "#3A2A2C", "#4A3A30"

# ------------------------------------------------------------------ geometry
BODY_D = ("M318 233 C350 190 410 160 470 160 C560 160 650 210 720 280 C740 300 750 320 748 340 "
          "C744 370 720 392 680 400 C600 414 500 414 430 400 C380 390 344 352 326 300 Z")
BODY_TOP = "M318 233 C350 190 410 160 470 160 C560 160 650 210 720 280"
TAIL_D = "M340 238 C250 220 150 206 40 194 C30 193 28 202 36 206 C150 226 250 256 340 310 Z"
TAIL_TOP = "M340 238 C250 220 150 206 40 194"
# long, nearly straight hind leg: heavy thigh, knee at the front, shin down to a short ankle and three-toed foot
HIND_D = ("M380 250 C430 224 510 236 530 290 C544 330 540 364 526 388 C520 400 516 412 514 426 "
          "C510 448 506 466 504 480 C504 490 508 496 512 500 L512 508 L432 508 C424 500 428 490 436 484 "
          "C442 462 442 438 436 418 C430 402 418 392 404 380 C380 356 368 322 370 296 C370 276 372 262 380 250 Z")
HIND_FOOT = "M420 494 C432 486 480 486 498 494 C506 500 506 512 498 514 L426 514 C416 514 414 500 420 494 Z"
# short, stout foreleg with the elbow slightly flexed back and a column-like hand
FORE_D = ("M660 320 C690 308 722 322 724 352 C726 376 714 394 700 404 C696 428 698 456 700 480 "
          "C702 496 694 508 680 508 L646 508 C634 506 632 496 636 486 C642 466 642 444 636 426 "
          "C628 408 628 380 634 356 C638 338 648 326 660 320 Z")
def open_top(d):
    """outline for a limb: drops the first segment (the arc where it meets the body) and the closing Z"""
    head, rest = d.split(" C", 1)
    first_end = " ".join(rest.split(" ")[4:6])
    return "M" + first_end + " C" + rest.split(" C", 1)[1].rstrip(" Z")
HIND_OUT = open_top(HIND_D)
FORE_FOOT = "M632 494 C644 486 682 486 696 494 C704 500 704 512 696 514 L638 514 C628 514 626 500 632 494 Z"
NECK_D = "M696 286 C740 290 790 320 826 352 L838 410 C800 410 756 396 716 372 C700 344 692 306 696 286 Z"
HEAD_D = "M812 350 C842 340 886 346 916 362 C936 372 942 388 932 396 C906 408 866 410 836 406 C814 402 802 378 812 350 Z"

def spine(t):
    """point on the back line, t in 0..1 from rump (318,233) through hips (470,160) to shoulders (720,280)"""
    if t < 0.4:
        return K.bez((318, 233), (350, 190), (410, 160), (470, 160), t / 0.4)
    return K.bez((470, 160), (560, 160), (650, 210), (720, 280), (t - 0.4) / 0.6)

def tail_top(t):
    return K.bez((340, 238), (250, 220), (150, 206), (40, 194), t)

def nails(xf, y=500):
    """two hoof-like nails at the front of a foot"""
    return "".join(path(f"M{xf-6} {y-6+k*8} C{xf+2} {y-8+k*8} {xf+8} {y-3+k*8} {xf+8} {y+2+k*8} C{xf+2} {y+3+k*8} {xf-4} {y+3+k*8} {xf-6} {y+1+k*8} Z", NAIL)
                   for k in (0, 1))

def plate_markup(ds, far=False):
    out = []
    for d in ds:
        out.append(path(d, PLATE))
        out.append(path(d, LOOK.url("shade")))
        out.append(f'<path d="{d}" fill="none" stroke="{PLATE_RIM}" stroke-width="5" stroke-linejoin="round" opacity="0.85"></path>')
        if far: out.append(path(d, D, 0.3))
        out.append(stroke(d, 2.5))
    return "".join(out)

def plate_veins(specs):
    out = []
    for x, y, w, h, lean in specs:
        tx, ty = x + lean * 0.55, y - h * 0.62
        out.append(f"M{x} {y-3} L{tx:.1f} {ty:.1f} M{x+(tx-x)*0.45:.1f} {y-(y-ty)*0.45:.1f} L{x-w*0.28:.1f} {y-h*0.5:.1f} "
                   f"M{x+(tx-x)*0.45:.1f} {y-(y-ty)*0.45:.1f} L{x+w*0.26:.1f} {y-h*0.48:.1f}")
    return line(" ".join(out), 0.22, 1.5)

# plates along the back: (t on spine, height, width), far row slightly darker and offset
# tallest plates over the hips and base of the tail, smaller toward the shoulders; S. stenops plates are broad
NEAR_PLATES = [(0.08, 100, 78), (0.24, 108, 84), (0.42, 94, 74), (0.6, 74, 58), (0.78, 52, 42), (0.92, 32, 28)]
FAR_PLATES = [(0.16, 108, 84), (0.33, 102, 80), (0.51, 84, 66), (0.69, 62, 50), (0.86, 40, 32)]
def plate_specs(rows, dy):
    out = []
    for t, h, w in rows:
        x, y = spine(t)
        out.append((round(x, 1), round(y + dy, 1), w, h, -8 - 6 * (1 - t)))
    return out
near_specs, far_specs = plate_specs(NEAR_PLATES, 8), plate_specs(FAR_PLATES, 6)
TAIL_NEAR = [(0.07, 84, 66), (0.22, 62, 50), (0.37, 42, 34), (0.5, 26, 22)]
TAIL_FAR = [(0.14, 72, 58), (0.3, 50, 40), (0.44, 32, 26)]
def tail_plate_specs(rows, dy):
    out = []
    for t, h, w in rows:
        x, y = tail_top(t)
        out.append((round(x, 1), round(y + dy, 1), w, h, -10))
    return out
tail_near, tail_far = tail_plate_specs(TAIL_NEAR, 7), tail_plate_specs(TAIL_FAR, 6)
pd = lambda specs: [plate(*s) for s in specs]

def flush_group(specs):
    return f'<g class="{C}-flush" opacity="0" fill="{FLUSH}">' + "".join(f'<path d="{d}"></path>' for d in pd(specs)) + "</g>"

# ------------------------------------------------------------------ parts
LOOK_L = LOOK
far_hind = (skin_part(LOOK, HIND_D, ao=True, far=True, tex=False, outline_d=open_top(HIND_D)) + skin_part(LOOK, HIND_FOOT, ao=True, far=True, tex=False) + nails(500))
far_fore = (skin_part(LOOK, FORE_D, ao=True, far=True, tex=False, outline_d=open_top(FORE_D)) + skin_part(LOOK, FORE_FOOT, ao=True, far=True, tex=False) + nails(698))
LEG_FAR = f'<g id="leg-far" transform="translate(36 -2)">{far_hind}</g>'
FORELEG_FAR = f'<g id="foreleg-far" transform="translate(32 -2)">{far_fore}</g>'

# tail with its plates and four spikes (far pair behind, near pair in front)
def cone(bx, by, tx, ty, w, bend=0.18):
    """evenly tapered, slightly back-curved spike from a base of half-width w at (bx, by) to the tip (tx, ty)"""
    lx, rx = bx - w, bx + w
    dx, dy = tx - bx, ty - by; ln = (dx * dx + dy * dy) ** 0.5; nx, ny = -dy / ln, dx / ln
    c1 = ((lx + tx) / 2 + nx * ln * bend * 0.5, (by + ty) / 2 + ny * ln * bend * 0.5)
    c2 = ((rx + tx) / 2 + nx * ln * bend * 0.35, (by + ty) / 2 + ny * ln * bend * 0.35)
    return f"M{lx} {by+3} Q{c1[0]:.1f} {c1[1]:.1f} {tx} {ty} Q{c2[0]:.1f} {c2[1]:.1f} {rx} {by+3} Z"
# the four spikes stuck out sideways and back, so from the side they point back and only a little up
spikes_far = [cone(132, 206, 86, 150, 8, 0.12), cone(92, 202, 46, 150, 7, 0.12)]
spikes_near = [cone(148, 210, 96, 160, 9, 0.12), cone(108, 205, 56, 160, 8, 0.12)]
def spike_markup(ds, far=False):
    out = []
    for d in ds:
        out.append(path(d, HORN)); out.append(path(d, LOOK.url("shade")))
        if far: out.append(path(d, D, 0.34))
        out.append(stroke(d, 2.4))
    return "".join(out)
tail_inner = (spike_markup(spikes_far, far=True) + plate_markup(pd(tail_far), far=True) + plate_markup(pd(tail_near))
              + flush_group(tail_near + tail_far)
              + skin_part(LOOK, TAIL_D,
                          belly="M36 206 C150 226 250 256 340 310 L340 292 C250 240 150 214 44 202 Z",
                          layers=stripes([(84, 199, 8, 7), (130, 203, 11, 9), (180, 207, 14, 10), (230, 213, 17, 12), (280, 222, 20, 13)])
                          + spots([(60, 198), (200, 208), (330, 240), (330, 290), (200, 236), (60, 204)], 10, 2, 4, 0.12, 21)
                          + line("M330 268 C260 248 170 226 60 204", 0.12, 2.2),
                          outline_d=TAIL_D.rstrip(" Z"), fade=True, rim_d=TAIL_TOP)
              + spike_markup(spikes_near)
              + line("M136 208 L136 214 M96 203 L96 209", 0.3, 2))
TAIL = piv("tail", f"{C}-tail", 330, 262, tail_inner)

# body with the two plate rows behind its back line
plates_inner = (plate_markup(pd(far_specs), far=True) + plate_veins(far_specs)
                + plate_markup(pd(near_specs)) + plate_veins(near_specs)
                + flush_group(near_specs + far_specs))
PLATES = f'<g id="plates">{plates_inner}</g>'
body_inner = (PLATES + skin_part(
    LOOK, BODY_D,
    belly="M748 330 C744 370 720 392 680 400 C600 414 500 414 430 400 C380 390 344 352 326 300 L340 296 C356 340 392 372 440 384 C510 396 600 396 670 384 C710 376 736 356 744 326 Z",
    layers=(path("M318 233 C350 190 410 160 470 160 C560 160 650 210 720 280 L708 290 C640 226 560 182 470 182 C414 182 362 206 330 246 Z", D, 0.24)
            + stripes([(360, 198, 34, 14), (420, 174, 40, 15), (490, 168, 44, 16), (556, 178, 42, 15), (616, 200, 36, 14), (668, 236, 30, 12)])
            + spots([(330, 240), (470, 172), (650, 218), (735, 300), (720, 380), (600, 404), (450, 396), (340, 330)], 24, 3, 7, 0.13, 7)
            + line("M600 236 C612 280 610 330 596 376 M650 246 C660 286 660 330 648 368", 0.08, 2.4)
            + line("M560 392 C578 398 600 400 622 398 M574 404 C590 408 608 408 626 406", 0.18, 2)),
    outline_d=BODY_D.rstrip(" Z"), rim_d=BODY_TOP))
BODY = piv("body", f"{C}-body", 520, 410, body_inner)

LEG_NEAR = ('<g id="leg-near">'
            + skin_part(LOOK, HIND_D, ao=True, outline_d=HIND_OUT,
                        layers=line("M380 300 C410 286 452 288 486 302 M398 340 C420 352 444 356 468 354", 0.12, 2.2)
                        + line("M444 446 C458 452 476 454 494 450 M444 460 C458 466 476 468 494 464 M500 396 C512 404 522 404 528 398", 0.22, 1.8),
                        rim_d="M392 246 C430 226 500 232 526 280")
            + skin_part(LOOK, HIND_FOOT, ao=True) + line("M448 490 L448 512 M472 490 L472 512", 0.26, 1.8) + nails(500)
            + "</g>")
FORELEG_NEAR = ('<g id="foreleg-near">'
                + skin_part(LOOK, FORE_D, ao=True, outline_d=open_top(FORE_D), layers=line("M644 444 C656 450 674 452 694 448 M644 458 C656 464 674 466 694 462 M634 410 C650 418 676 416 700 404", 0.22, 1.8)
                            + line("M664 330 C684 336 704 350 716 368", 0.12, 2.2))
                + skin_part(LOOK, FORE_FOOT, ao=True) + line("M660 490 L660 512 M680 490 L680 512", 0.26, 1.8) + nails(698)
                + "</g>")

head_inner = (
    skin_part(LOOK, NECK_D, belly="M838 410 C800 410 756 396 716 372 L724 358 C760 380 800 394 834 396 Z",
              layers=stripes([(712, 288, 22, 11), (750, 300, 20, 10), (786, 318, 16, 9)], 0.26)
              + line("M744 318 C752 334 756 352 754 370 M776 330 C784 346 788 362 786 380 M806 344 C812 358 816 372 814 388", 0.16, 2)
              + dots([(730, 372), (780, 392), (826, 402), (826, 396), (780, 386), (730, 366)], 18, 1.2, 2.2, 0.22, 9),
              outline_d="M722 293 C760 304 798 326 826 352 M838 410 C808 410 776 400 744 386",
              rim_d="M700 288 C740 292 790 320 822 348")
    + skin_part(LOOK, HEAD_D, belly="M836 406 C866 410 906 408 932 396 L928 388 C904 398 868 400 838 398 Z",
                layers=path("M812 350 C842 340 886 346 916 362 L912 368 C884 356 846 352 818 362 Z", D, 0.2)
                + line("M842 396 C872 398 902 396 932 390", 0.45, 2.2) + line("M824 372 C830 382 836 390 846 396", 0.18, 1.8)
                + dots([(820, 356), (880, 350), (926, 372), (900, 392), (836, 394)], 26, 0.7, 1.3, 0.14, 4),
                rim_d="M814 348 C842 338 886 344 914 358", light=True)
    + path("M918 368 C934 372 944 384 938 394 C930 400 920 400 912 396 Z", BEAK) + stroke("M918 368 C934 372 944 384 938 394 C930 400 920 400 912 396", 2.2)
    + stroke("M918 378 C922 376 926 377 928 380", 2, D, 0.55)
    + eye(860, 366, f"{C}-eyelid", 4.8)
    + path("M846 360 C852 352 868 350 878 356 C878 358 876 360 874 360 C866 356 856 357 850 364 Z", D, 0.42)
)
# small plates continue up the neck; bony ossicles stud the throat
neck_plates = "".join(path(plate(x, y, w, h, -6), PLATE) + path(plate(x, y, w, h, -6), LOOK.url("shade")) + stroke(plate(x, y, w, h, -6), 2.2)
                      for x, y, w, h in [(722, 296, 26, 30), (756, 308, 22, 24), (788, 326, 18, 18)])
gular = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E6D9BC" stroke="#2A1C22" stroke-width="1.2"></circle>' for x, y, r in [(770, 396, 3.4), (790, 402, 3), (810, 405, 2.6), (782, 392, 2.4)])
HEAD = piv("head", f"{C}-head", 712, 322, neck_plates + head_inner + gular)

SHADOW = '<ellipse cx="520" cy="514" rx="300" ry="12" fill="#000000" opacity="0.3"></ellipse>'
ANIMAL = (SHADOW + LEG_FAR + FORELEG_FAR + TAIL + BODY + LEG_NEAR + HEAD + FORELEG_NEAR)
FRAG = piv("act", f"{C}-act", 520, 514, ANIMAL)

# ------------------------------------------------------------------ motion
ACTION = {
    "tail": [(0, "rotate(0)"), (0.22, "rotate(12deg)"), (0.4, "rotate(12deg)"), (0.52, "rotate(-14deg)"), (0.62, "rotate(-10deg)"),
             (0.74, "rotate(3deg)"), (0.86, "rotate(-1deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.25, "rotate(4deg)"), (0.7, "rotate(4deg)"), (1, "rotate(0)")],
    "flush": [(0, "0"), (0.25, "0.6"), (0.7, "0.6"), (1, "0")],
    "act": [(0, "translateX(0)"), (0.52, "translateX(0)"), (0.6, "translateX(-6px)"), (0.75, "translateX(0)"), (1, "translateX(0)")],
}
GSAP = """      .call(() => gsap.getTweensOf(parts.tail).forEach(t => { if (t.parent !== act) t.pause(); }), [], 0)
      .to(parts.tail, { rotation: 12, duration: 0.35, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: 4, duration: 0.3, ease: 'power2.out' }, 0)
      .to(document.querySelectorAll('.stg-flush'), { opacity: 0.6, duration: 0.3 }, 0)
      .to(parts.tail, { rotation: -14, duration: 0.22, ease: 'power3.in' }, 0.62)
      .to(parts.act, { x: -6, duration: 0.12, yoyo: true, repeat: 1, ease: 'power1.out' }, 0.84)
      .to(parts.tail, { rotation: 0, duration: 0.8, ease: 'elastic.out(1, 0.45)' }, 0.95)
      .to(parts.head, { rotation: 0, duration: 0.5, ease: 'power2.inOut' }, 1.0)
      .to(document.querySelectorAll('.stg-flush'), { opacity: 0, duration: 0.6 }, 1.0)
      .call(() => gsap.getTweensOf(parts.tail).forEach(t => { if (t.parent !== act) t.resume(); }))"""

# ------------------------------------------------------------------ poster scene: Morrison plain, hazy noon
def conifer(x, base, h, sc=1.0, color="#6F7A5A"):
    """araucaria-like: tall bare trunk, layered flat crowns near the top"""
    tw = 6 * sc
    crowns = "".join(
        f'<ellipse cx="{x + (k % 2) * 6 - 3}" cy="{base - h + 24 * sc + k * 22 * sc:.0f}" rx="{(34 + k * 9) * sc:.0f}" ry="{8 * sc:.0f}"></ellipse>'
        for k in range(4))
    return (f'<g fill="{color}"><path d="M{x-tw} {base} L{x-tw*0.4:.1f} {base-h} L{x+tw*0.4:.1f} {base-h} L{x+tw} {base} Z"></path>{crowns}'
            f'<ellipse cx="{x}" cy="{base - h + 8 * sc:.0f}" rx="{20 * sc:.0f}" ry="{9 * sc:.0f}"></ellipse></g>')

def cycad(x, y, sc, color, flip=False):
    fl = -1 if flip else 1
    fronds = "".join(
        f'<path d="M0 0 C{fl*a*0.4:.0f} {-l*0.5:.0f} {fl*a*0.85:.0f} {-l*0.85:.0f} {fl*a:.0f} {-l:.0f} C{fl*a*0.8:.0f} {-l*0.74:.0f} {fl*a*0.35:.0f} {-l*0.36:.0f} 0 0 Z"></path>'
        for a, l in [(-120, 70), (-90, 110), (-50, 140), (-10, 150), (30, 140), (70, 112), (110, 76)])
    trunk = f'<path d="M-14 0 L-10 -40 L10 -40 L14 0 Z"></path>'
    return f'<g transform="translate({x} {y}) scale({sc})" fill="{color}">{trunk}<g transform="translate(0 -36)">{fronds}</g></g>'

def band(y, h, color, phase=0):
    w = [y - 6 + phase, y + 6 - phase, y - 3, y + 4]
    return (f'<path d="M0 {y} C270 {w[0]} 540 {w[1]} 810 {w[2]} C930 {w[3]} 1010 {y} 1080 {y - 2} '
            f'L1080 {y + h} C810 {y + h + 4} 540 {y + h - 5} 270 {y + h + 3} C160 {y + h + 6} 70 {y + h} 0 {y + h + 2} Z" fill="{color}"></path>')

SCENE = f'''<svg aria-hidden="true" viewBox="0 0 1080 900" width="1080" height="900" style="position: absolute; top: 0; left: 0; display: block">
<defs>
<linearGradient id="stg-sc-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B9CFD8"></stop><stop offset="0.72" stop-color="#EDE3CC"></stop></linearGradient>
<radialGradient id="stg-sc-sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF8E6" stop-opacity="0.75"></stop><stop offset="0.3" stop-color="#FFF1D2" stop-opacity="0.35"></stop><stop offset="1" stop-color="#FFF1D2" stop-opacity="0"></stop></radialGradient>
<linearGradient id="stg-sc-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2E8D2" stop-opacity="0"></stop><stop offset="0.6" stop-color="#F2E8D2" stop-opacity="0.6"></stop><stop offset="1" stop-color="#F2E8D2" stop-opacity="0"></stop></linearGradient>
<linearGradient id="stg-sc-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#3B2414" stop-opacity="0.34"></stop></linearGradient>
<radialGradient id="stg-sc-shadow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#3B2414" stop-opacity="0.34"></stop><stop offset="1" stop-color="#3B2414" stop-opacity="0"></stop></radialGradient>
</defs>
<rect x="0" y="0" width="1080" height="900" fill="url(#stg-sc-sky)"></rect>
<circle cx="800" cy="250" r="300" fill="url(#stg-sc-sun)"></circle>
<path d="M0 648 L70 648 L96 612 L250 606 L272 648 L470 648 L498 600 L700 594 L726 648 L860 648 L884 618 L1000 614 L1022 648 L1080 648 L1080 900 L0 900 Z" fill="#CBB9A0"></path>
<path d="M96 612 L250 606 L252 616 L98 622 Z M498 600 L700 594 L702 606 L500 612 Z M884 618 L1000 614 L1002 622 L886 626 Z" fill="#BCA88E"></path>
<g opacity="0.78">{conifer(118, 700, 250, 1.0)}{conifer(196, 704, 200, 0.8)}{conifer(930, 702, 270, 1.05)}{conifer(1010, 706, 210, 0.85)}</g>
<rect x="0" y="560" width="1080" height="170" fill="url(#stg-sc-haze)"></rect>
<path d="M0 722 C120 704 220 714 320 708 C440 700 540 718 660 710 C780 702 880 716 1080 706 L1080 900 L0 900 Z" fill="#CDAE72"></path>
{band(748, 16, "#BF9C5E")}
{band(786, 22, "#D9BE86", 2)}
{band(830, 14, "#B58A4E", -2)}
{band(868, 40, "#BF9C5E", 1)}
<rect x="0" y="702" width="1080" height="198" fill="url(#stg-sc-ground)"></rect>
<ellipse cx="560" cy="822" rx="380" ry="24" fill="url(#stg-sc-shadow)"></ellipse>
{cycad(52, 905, 1.0, "#4F5638")}{cycad(150, 912, 0.7, "#5C6442", True)}{cycad(1030, 908, 1.05, "#4F5638", True)}
</svg>'''

# ------------------------------------------------------------------ rig sheet parts (viewBox crops in drawing units)
RIG = [
    ("Body and plates", "#body, #plates", BODY, (292, 80, 470, 340)),
    ("Tail with spikes", "#tail", TAIL, (20, 110, 330, 210)),
    ("Head and neck", "#head", HEAD, (688, 280, 262, 136)),
    ("Near hind leg", "#leg-near", LEG_NEAR, (362, 218, 190, 300)),
    ("Far hind leg", "#leg-far", LEG_FAR, (398, 216, 190, 300)),
    ("Forelegs", "#foreleg-near, #foreleg-far", f'<g transform="translate(-20 0)">{FORELEG_NEAR}</g>' + f'<g transform="translate(30 0)">{FORELEG_FAR}</g>', (606, 312, 202, 206)),
]

SPEC = dict(
    code=C, slug="stegosaurus", board="Stegosaurus", name="Stegosaurus", short="Stegosaurus", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "plates", "tail", "head", "leg-near", "leg-far", "foreleg-near", "foreleg-far"],
    action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the Stegosaurus swing its tail", action_verb="swing its tail", page_bg="#D9D4C4",
    scene=SCENE, title="Stegosaurus", title_px=190, binomial="Stegosaurus stenops", subtitle="the narrow-faced roof lizard",
    paragraph="A plant eater with two staggered rows of tall bony plates down its back and a spiked tail for defence, carrying its small head about a metre off the ground.",
    facts=[("6.5 m", "adult length"), ("152–145", "million years ago"), ("4", "tail spikes")],
    footer="Fossils come from the Morrison Formation of Colorado, Wyoming and Utah, with more found in Portugal.",
    hint="Tap the Stegosaurus to swing its tail", skin_swatches=["#5E7E7A", "#7A8450", "#9E6B7B", "#8A6A3E"],
    dino_top=262, rig_parts=RIG, rig_h=960,
)

if __name__ == "__main__":
    frag = K.write_all(SPEC)
    K.poster_board(SPEC, frag)
    K.rig_board(SPEC, frag)
    K.shoot("stegosaurus-animated.svg", 1000, 560)
    print("ok")
