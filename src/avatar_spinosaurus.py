"""Spinosaurus channel profile picture: a head-and-neck portrait on a 1024 x 1024 artboard.
Building the SVG has no side effects (build()); running the script writes svg/avatar/spinosaurus-avatar.svg.
Design brief: three layer groups (background, middle, foreground), cel shading, 8 px outer outlines, no text,
essentials inside the central circle (r ~ 410 px), recognisable at 40 px. Every shape is plain geometry, no random choices.
Anatomy (see README, Scientific accuracy): a long, low, narrow crocodile-like skull, nostrils set back from the tip,
a small crest in front of the eyes (S. aegyptiacus), a rounded expanded snout tip, a thin sail of neural spines."""
import os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# palette from the brief
SAGE, OLIVE, BASE, LIGHT, SHADE, OCHRE, INK, WATER = "#B9D6A5", "#829F69", "#397B49", "#83B85B", "#24563C", "#C69A51", "#18382D", "#689F8D"
OCHRE_D, MUD, MUD_L = "#9C7436", "#A88B52", "#C0A870"   # darker ochre for sail base and mud, derived from the accent
OUT, MID, FINE = 9, 6, 5                                # line weights (px on 1024)

def P(d, fill="none", stroke=None, w=OUT, extra=""):
    s = f' stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{s} {extra}/>'

def blade(x, y, ang, ln, wd):
    """a chunky tapered leaf from (x, y) pointing at ang degrees (0 = right, 90 = up)"""
    a = math.radians(ang); dx, dy = math.cos(a), -math.sin(a); nx, ny = -dy, dx
    tip = (x + dx * ln, y + dy * ln)
    c1 = (x + dx * ln * .45 + nx * wd, y + dy * ln * .45 + ny * wd)
    c2 = (x + dx * ln * .45 - nx * wd, y + dy * ln * .45 - ny * wd)
    return f"M{x:.0f} {y:.0f} Q{c1[0]:.0f} {c1[1]:.0f} {tip[0]:.0f} {tip[1]:.0f} Q{c2[0]:.0f} {c2[1]:.0f} {x:.0f} {y:.0f}Z"

def weichselia(x, y, s, fill, line=None, w=MID, lean=0):
    """Weichselia simplified to a stiff stem with 3 pairs of fat blades and a crown blade"""
    out = []
    for i, (hy, ln, ang) in enumerate([(0.30, 70, 40), (0.52, 62, 46), (0.74, 52, 52)]):
        for sgn in (1, -1):
            a = 90 + sgn * (90 - ang) + lean
            out.append(P(blade(x + lean * hy * 1.2 * s, y - 150 * hy * s, a, ln * s, 14 * s), fill, line, w))
    out.append(P(blade(x + lean * 1.2 * s, y - 150 * s * .9, 90 + lean, 62 * s, 12 * s), fill, line, w))
    out.append(P(f"M{x:.0f} {y:.0f} L{x + lean * 1.2 * s:.0f} {y - 150 * s * .9:.0f}", "none", line or fill, max(w, 8 * s)))
    return "".join(out)

# ---------------------------------------------------------------- background: sage sky, tidal water, olive fern silhouettes
def background():
    g = [f'<rect width="1024" height="1024" fill="{SAGE}"/>']
    g.append(P("M0 590 C120 560 200 600 300 585 C420 568 520 596 640 584 C780 570 900 596 1024 580 L1024 1024 L0 1024Z", OLIVE, None, 0, 'opacity="0.55"'))
    # three silhouette ferns on the far shore (low contrast, no outline)
    for x, y, s, l in [(95, 640, .62, -8), (205, 650, .5, 6), (330, 646, .42, -4)]:
        g.append(weichselia(x, y, s, OLIVE, None, 0, l))
    # tidal water: three curved horizontal bands
    for y, a in [(690, 18), (752, 22), (816, 20)]:
        g.append(P(f"M-20 {y} C160 {y - a} 320 {y + a} 520 {y} S880 {y - a} 1044 {y + 4} L1044 {y + 30} C860 {y + 30 + a} 700 {y + 30 - a} 520 {y + 32} S180 {y + 30 + a} -20 {y + 30}Z",
                   WATER, None, 0, 'opacity="0.9"'))
    return "".join(g)

# ---------------------------------------------------------------- middle: sail, neck, head, mud bank, ferns
BASES = [(600, 470), (684, 524), (766, 588), (842, 660), (906, 740)]
TIPS = [(590, 262), (690, 168), (784, 218), (860, 336), (915, 480)]

def sail():
    pts = [BASES[0]] + [None]
    d = f"M{BASES[0][0]} {BASES[0][1]} L{TIPS[0][0]} {TIPS[0][1]}"
    for i in range(1, 5):   # concave scallop between spine tips
        (x0, y0), (x1, y1) = TIPS[i - 1], TIPS[i]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        d += f" Q{mx - 6 + (y1 - y0) * .0:.0f} {my + 26:.0f} {x1} {y1}"
    d += f" L{BASES[4][0]} {BASES[4][1]}Z"
    rays = "".join(P(f"M{b[0]} {b[1]} L{t[0]} {t[1]}", "none", SHADE, MID) for b, t in zip(BASES, TIPS))
    band = P(f"M{BASES[0][0]} {BASES[0][1]} L{BASES[4][0]} {BASES[4][1]} L{BASES[4][0] - 20} {BASES[4][1] - 120} L{BASES[0][0] + 10} {BASES[0][1] - 110}Z", OCHRE_D, None, 0, 'opacity="0.85"')
    return (f'<g id="sail"><clipPath id="sailclip"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="{OCHRE}"/><g clip-path="url(#sailclip)">{band}{rays}</g>'
            + P(d, "none", INK, OUT) + "</g>")

NECK = ("M552 414 C640 430 712 508 790 600 C850 672 900 740 930 800 L940 1040 L650 1040 C650 900 640 760 600 650 "
        "C585 610 565 580 545 556Z")

# head, facing left. upper = skull and upper jaw above the mouth line; lower = lower jaw
UPPER = ("M152 512 C138 492 148 462 186 456 C230 450 296 456 338 442 C376 430 408 410 432 386 "
         "C452 372 486 368 508 388 C534 394 562 408 582 434 C594 466 590 494 566 506 "
         "C534 508 500 514 440 514 C350 518 250 520 152 512Z")
MOUTH = "M152 512 C250 520 350 518 440 514 C500 514 534 508 566 500"
LOWER = ("M566 500 C580 520 570 546 546 556 C480 574 400 580 330 566 C270 554 200 552 166 542 "
         "C150 536 146 520 152 512 C250 520 350 518 440 514 C500 514 534 508 566 500Z")

def head():
    g = ['<g id="head">']
    g.append(f'<clipPath id="upclip"><path d="{UPPER}"/></clipPath><clipPath id="lowclip"><path d="{LOWER}"/></clipPath>')
    # lower jaw: base then shadow underside
    g.append(P(LOWER, BASE))
    g.append(f'<g clip-path="url(#lowclip)">' + P("M120 540 C260 556 420 556 600 520 L600 620 L120 620Z", SHADE) + "</g>")
    # upper head: base, light top strip, brow shadow, big scale marks
    g.append(P(UPPER, BASE))
    g.append(f'<g clip-path="url(#upclip)">'
             + P("M140 440 C240 436 300 446 350 422 C400 400 430 372 470 358 L520 340 L560 400 C500 396 440 412 380 438 C320 462 220 462 140 470Z", LIGHT)
             + P("M440 392 C480 404 520 420 566 424 L600 470 L596 400Z", SHADE)
             + P("M380 478 C410 470 440 474 468 486 C440 500 400 500 380 478Z", SHADE, None, 0)
             + P("M500 462 C530 456 556 466 566 488 C540 500 512 492 500 462Z", SHADE, None, 0)
             + "</g>")
    g.append(P(UPPER, "none", INK, OUT))
    g.append(P(LOWER, "none", INK, OUT))
    g.append(P(MOUTH, "none", INK, MID))
    # small crest ridge in front of the eyes (internal line)
    g.append(P("M436 392 C450 412 452 424 446 436", "none", INK, FINE))
    # retracted nostril, set back from the snout tip
    g.append(P("M338 446 C350 434 372 436 378 446 C366 454 348 454 338 446Z", INK, None, 0))
    # eye: ochre iris, dark pupil, flat lid for a deadpan, knowing default look
    g.append(f'<g id="eye"><circle cx="486" cy="446" r="26" fill="{OCHRE}" stroke="{INK}" stroke-width="{MID}"/>'
             f'<ellipse cx="480" cy="450" rx="9" ry="14" fill="{INK}"/><circle cx="476" cy="444" r="4.5" fill="#F3EBCF"/>'
             + P("M456 440 C470 424 504 420 518 436 L518 424 C500 408 466 412 456 426Z", BASE, None, 0)
             + P("M456 441 C470 425 504 421 518 437", "none", INK, MID) + "</g>")
    # brow ridge over the eye: angular, heavy
    g.append(P("M448 420 C470 396 512 396 536 422", "none", INK, OUT))
    g.append("</g>")
    return "".join(g)

def neck():
    g = ['<g id="neck">', f'<clipPath id="neckclip"><path d="{NECK}"/></clipPath>', P(NECK, BASE)]
    g.append('<g clip-path="url(#neckclip)">')
    g.append(P("M545 556 C585 580 605 620 620 670 C640 740 650 820 650 1040 L760 1040 C740 860 700 760 640 660 C610 610 580 580 545 556Z", SHADE))
    g.append(P("M570 540 C600 586 620 620 632 662 C646 720 652 800 660 900 C668 800 664 710 646 656 C630 610 604 572 570 540Z", LIGHT))
    for (x, y, rot) in [(700, 560, 40), (770, 650, 48), (840, 740, 55)]:   # big skin bands across the neck
        g.append(P(f"M{x - 30} {y - 8} Q{x} {y - 40} {x + 40} {y + 4} L{x + 34} {y + 30} Q{x} {y} {x - 24} {y + 26}Z", SHADE, None, 0, 'opacity="0.85"'))
    g.append("</g>")
    g.append(P(NECK, "none", INK, OUT))
    g.append("</g>")
    return "".join(g)

def middle():
    mud = P("M-20 800 C80 770 200 770 300 790 C400 806 470 820 520 850 C540 870 500 900 420 900 L-20 900Z", MUD, INK, MID)
    mud += P("M60 800 C120 786 200 788 250 800 C200 812 120 812 60 800Z", MUD_L, None, 0)
    ferns = (weichselia(120, 790, .8, BASE, INK, FINE, -6) + weichselia(250, 800, .62, LIGHT, INK, FINE, 6) + weichselia(350, 812, .5, BASE, INK, FINE, -3))
    return f'<g id="middle">{sail()}{neck()}{head()}<g id="bank">{mud}{ferns}</g></g>'

# ---------------------------------------------------------------- foreground: two big cropped leaves, subtle mud
def foreground():
    mud = P("M120 1000 C260 920 420 940 560 960 C700 940 820 930 920 990 L920 1040 L120 1040Z", MUD, INK, MID)
    mud += P("M300 975 C400 962 500 970 560 978 C480 990 380 990 300 975Z", MUD_L, None, 0)
    leaf1 = P("M70 1040 C90 920 190 800 340 742 C330 840 270 960 170 1040Z", SHADE, INK, OUT) + P("M110 1030 C170 920 250 820 330 752", "none", BASE, MID)
    leaf2 = P("M980 1040 C960 940 880 880 780 860 C790 940 830 1000 880 1040Z", SHADE, INK, OUT) + P("M960 1030 C920 960 860 910 790 870", "none", BASE, MID)
    return f'<g id="foreground">{mud}{leaf1}{leaf2}</g>'

def build(silhouette=False):
    body = (f'<g id="background">{background()}</g>{middle()}{foreground()}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">'
            f'<title>Spinosaurus channel avatar</title>{body}</svg>')

def silhouette_svg():
    """only the animal, one flat ink colour, for the silhouette test"""
    shapes = "".join(P(d, INK, INK, OUT) for d in (NECK, UPPER, LOWER))
    sail_d = sail().split('<path d="')[1].split('"')[0]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">'
            f'<rect width="1024" height="1024" fill="#fff"/>{P(sail_d, INK, INK, OUT)}{shapes}</svg>')

if __name__ == "__main__":
    out = os.path.join(ROOT, "svg", "avatar"); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "spinosaurus-avatar.svg"), "w").write(build())
    open(os.path.join(out, "spinosaurus-silhouette.svg"), "w").write(silhouette_svg())
    print("wrote", out)
