#!/usr/bin/env python3
"""Spinosaurus profile picture: 1024x1024, cel-shaded green, built to survive a 40 px circle.

Writes svg/spinosaurus-avatar.svg and svg/spinosaurus-avatar.png (needs Playwright).
Everything is plain geometry, no filters, no randomness: rebuilds are identical.
Palette is the brief's: tide #16382C, body #2E7D46 / #46A85E, accent #8BE052,
ink #0B1712, pale mint #D9F7BE (no #000000, no #FFFFFF).
"""
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BG, BODY, LIGHT, ACCENT, INK, MINT = "#16382C", "#2E7D46", "#46A85E", "#8BE052", "#0B1712", "#D9F7BE"
SHADE = "#256A3C"      # one shadow step under jaw / neck
FAR_BANK = "#0F2A21"   # distant mud bank
WATER = "#1F5440"      # tidal water
MID_BANK = "#274A33"   # mid-ground mud ridge

# ---- subject silhouettes (original coordinates, 1024 canvas) ------------------
HEAD = ("M 842 510 C 822 497 770 490 720 478 C 685 470 665 450 640 428 "
        "C 622 412 600 396 574 404 C 556 410 548 424 540 432 "
        "C 515 428 490 440 470 462 C 420 500 380 560 358 650 L 340 900 L 610 900 "
        "C 585 740 570 680 590 620 C 600 592 612 578 640 566 "
        "C 700 566 780 562 828 548 C 848 542 854 524 842 510 Z")
SAIL = ("M 480 500 Q 450 400 408 312 Q 368 376 338 262 Q 292 360 262 290 "
        "Q 222 400 206 372 Q 180 430 176 520 L 200 720 L 260 900 L 490 900 Z")
SPINES = [((408, 312), (450, 560)), ((338, 262), (395, 610)),
          ((262, 290), (330, 650)), ((206, 372), (255, 690))]


def bez(p, t):
    u = 1 - t
    return tuple(u**3 * p[0][i] + 3 * u * u * t * p[1][i] + 3 * u * t * t * p[2][i] + t**3 * p[3][i] for i in (0, 1))


def bez_d(p, t):
    u = 1 - t
    return tuple(3 * u * u * (p[1][i] - p[0][i]) + 6 * u * t * (p[2][i] - p[1][i]) + 3 * t * t * (p[3][i] - p[2][i]) for i in (0, 1))


def frond(pts, n=4, leaf=84):
    """Chunky Weichselia-style frond: curved stem plus paired round leaflets, outline layer then colour layer."""
    segs = []
    for t0, t1 in [(0, 0.5), (0.5, 1)]:  # stem as polyline of short pieces
        pass
    stem = [bez(pts, i / 20) for i in range(21)]
    stem_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in stem)
    leaves = []
    for k in range(n):
        t = 0.3 + 0.7 * k / (n - 1) if n > 1 else 0.6
        x, y = bez(pts, t)
        dx, dy = bez_d(pts, t)
        a = math.atan2(dy, dx)
        ln = leaf * (1 - 0.45 * t)
        for side, col in ((-1, LIGHT), (1, BODY)):
            b = a + side * math.radians(62)
            leaves.append((x, y, x + ln * math.cos(b), y + ln * math.sin(b), col))
    tx, ty = bez(pts, 1)
    dx, dy = bez_d(pts, 1)
    a = math.atan2(dy, dx)
    leaves.append((tx, ty, tx + 56 * math.cos(a), ty + 56 * math.sin(a), ACCENT))
    out = [f'<path d="{stem_d}" fill="none" stroke="{INK}" stroke-width="64" stroke-linecap="round" stroke-linejoin="round"/>']
    for x1, y1, x2, y2, c in leaves:
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="64" stroke-linecap="round"/>')
    out.append(f'<path d="{stem_d}" fill="none" stroke="{BODY}" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>')
    for x1, y1, x2, y2, c in leaves:
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="34" stroke-linecap="round"/>')
    return "\n".join(out)


def cel_shape(sid, d, hl=(12, 26), sh=(-10, -16), rim=False):
    """Fill, one highlight crescent (upper-left light) and one shadow crescent, via masks."""
    hx, hy = hl
    sx, sy = sh
    s = f'''<mask id="{sid}-hl"><path d="{d}" fill="#fff"/><path d="{d}" fill="#000" transform="translate({hx} {hy})"/></mask>
<mask id="{sid}-sh"><path d="{d}" fill="#fff"/><path d="{d}" fill="#000" transform="translate({sx} {sy})"/></mask>
<clipPath id="{sid}-clip"><path d="{d}"/></clipPath>
<path d="{d}" fill="{BODY}"/>
<path d="{d}" fill="{SHADE}" mask="url(#{sid}-sh)"/>
<path d="{d}" fill="{LIGHT}" mask="url(#{sid}-hl)"/>'''
    if rim:
        s += f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="22" clip-path="url(#{sid}-clip)" mask="url(#{sid}-hl)"/>'
    return s


def build():
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">')
    o.append('<title>Spinosaurus avatar</title>')
    # background: sky, distant bank, water
    o.append(f'<rect width="1024" height="1024" fill="{BG}"/>')
    o.append(f'<path d="M0 690 L0 650 Q90 612 170 640 Q260 662 330 636 L700 636 Q790 606 860 628 Q950 650 1024 624 L1024 700 Z" fill="{FAR_BANK}"/>')
    # tiny distant fern silhouette
    o.append(f'<path d="M930 650 Q925 610 952 592 Q946 622 962 650 Z M930 650 Q912 622 900 614 Q925 622 940 650 Z" fill="{FAR_BANK}"/>')
    o.append(f'<rect y="700" width="1024" height="324" fill="{WATER}"/>')
    # mid-ground mud ridges either side of the neck, thin rim light
    left = "M0 760 Q70 700 170 704 Q260 708 330 770 L330 800 L0 800 Z"
    right = "M600 790 Q650 740 740 722 Q850 700 1024 744 L1024 800 L600 800 Z"
    for d in (left, right):
        o.append(f'<path d="{d}" fill="{MID_BANK}"/>')
        o.append(f'<path d="{d}" fill="none" stroke="{LIGHT}" stroke-width="9" stroke-linejoin="round"/>')
    o.append('<g transform="translate(470 560) scale(0.93) translate(-470 -560)">')  # keep snout tip, eye and sail inside the 70% safe circle
    # subject: mint sticker halo under everything, then sail, then head+neck
    for d in (SAIL, HEAD):
        o.append(f'<path d="{d}" fill="none" stroke="{MINT}" stroke-width="56" stroke-linejoin="round"/>')
    o.append(f'<path d="{SAIL}" fill="none" stroke="{INK}" stroke-width="34" stroke-linejoin="round"/>')
    o.append(cel_shape("sail", SAIL, hl=(14, 30), sh=(-4, -4), rim=True))
    o.append('<g clip-path="url(#sail-clip)">')
    for (tx, ty), (bx, by) in SPINES:
        o.append(f'<line x1="{tx}" y1="{ty}" x2="{bx}" y2="{by}" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>')
    o.append('</g>')
    o.append(f'<path d="{HEAD}" fill="none" stroke="{INK}" stroke-width="34" stroke-linejoin="round"/>')
    o.append(cel_shape("head", HEAD, hl=(10, 22), sh=(-12, -16)))
    # nostril, mouth with a dry smirk, eye with heavy lid
    o.append(f'<ellipse cx="676" cy="494" rx="14" ry="9" fill="{INK}" transform="rotate(14 676 494)"/>')
    o.append(f'<path d="M 838 536 C 790 550 700 554 640 548 Q 622 546 610 530" fill="none" stroke="{INK}" stroke-width="11" stroke-linecap="round"/>')
    ex, ey = 608, 470
    o.append(f'<clipPath id="eye"><circle cx="{ex}" cy="{ey}" r="35"/></clipPath>')
    o.append(f'<circle cx="{ex}" cy="{ey}" r="35" fill="{MINT}"/>')
    o.append(f'<circle cx="{ex + 17}" cy="{ey + 11}" r="19" fill="{INK}"/>')
    o.append(f'<circle cx="{ex + 24}" cy="{ey + 4}" r="10" fill="{ACCENT}"/>')
    o.append(f'<polygon points="{ex - 50},{ey - 14} {ex + 50},{ey + 10} {ex + 50},{ey - 50} {ex - 50},{ey - 50}" fill="{BODY}" clip-path="url(#eye)"/>')
    o.append(f'<circle cx="{ex}" cy="{ey}" r="35" fill="none" stroke="{INK}" stroke-width="9"/>')
    o.append(f'<line x1="{ex - 48}" y1="{ey - 16}" x2="{ex + 46}" y2="{ey + 10}" stroke="{INK}" stroke-width="14" stroke-linecap="round"/>')
    o.append('</g>')
    # tide in front of the neck base, so the animal rises out of the water
    o.append(f'<path d="M0 806 Q130 792 260 806 T512 806 T768 806 T1024 806 L1024 1024 L0 1024 Z" fill="{WATER}"/>')
    o.append(f'<path d="M 270 806 Q 340 790 420 806 T 590 806 T 700 806" fill="none" stroke="{MINT}" stroke-width="14" stroke-linecap="round"/>')
    # water bars
    for x, y, w in ((60, 870, 150), (640, 880, 170), (400, 940, 220), (760, 830, 100)):
        o.append(f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{BODY}" stroke-width="14" stroke-linecap="round"/>')
    # foreground fronds
    o.append(frond([(300, 1030), (200, 940), (150, 850), (150, 740)]))
    o.append(frond([(770, 1030), (850, 950), (890, 870), (885, 760)], n=4, leaf=80))
    o.append('</svg>')
    return "\n".join(o)


def render(svg_path, png_path, size=1024):
    """Rasterise with Node Playwright (pre-installed in the cloud container)."""
    import subprocess
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          f"const p=await b.newPage({{viewport:{{width:{size},height:{size}}}}});"
          f"await p.goto('{svg_path.as_uri()}');await p.screenshot({{path:'{png_path}'}});await b.close()}})()")
    subprocess.run(["node", "-e", js], check=True)


if __name__ == "__main__":
    out = ROOT / "svg"
    svg = out / "spinosaurus-avatar.svg"
    svg.write_text(build())
    print("wrote", svg)
    if "--no-png" not in sys.argv:
        render(svg, out / "spinosaurus-avatar.png")
        print("wrote", out / "spinosaurus-avatar.png")
