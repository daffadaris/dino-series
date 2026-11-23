import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Scenery kit for the dinosaur series: plants, rocks and sky pieces in the series style (dark outer outline,
gradient shading, warm rim light), grouped by the habitat they belong to. Every asset is a function returning SVG
markup placed with its base centre at (x, y); `s` scales it and `flip` mirrors it. Call defs() once per SVG.

Plants are chosen from the fossil floras of each formation:
- Morrison (Stegosaurus): conifers, tree ferns, ferns, cycads, ginkgos and horsetails; no flowering plants or grass.
- Hell Creek (T. rex, Triceratops, Ankylosaurus): about 90% flowering plants, mostly broadleaf trees related to
  magnolias, with palms back from the water, ferns near it and rare dawn redwoods.
- Bahariya (Spinosaurus): a mangrove coast dominated by the fern Weichselia.
- Cerro Barcino (Patagotitan): a drier floodplain with small flowering plants such as Patagoflora."""
import math, pathlib, random

OL = "#2A1C22"

def defs():
    return '''<defs>
<linearGradient id="scn-shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF0D8" stop-opacity="0.28"></stop><stop offset="0.35" stop-color="#FFF0D8" stop-opacity="0"></stop><stop offset="0.6" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#000000" stop-opacity="0.38"></stop></linearGradient>
<linearGradient id="scn-side" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000000" stop-opacity="0.32"></stop><stop offset="0.45" stop-color="#000000" stop-opacity="0"></stop><stop offset="0.8" stop-color="#FFF0D8" stop-opacity="0.18"></stop><stop offset="1" stop-color="#FFF0D8" stop-opacity="0.05"></stop></linearGradient>
</defs>'''

def _place(x, y, s, flip, inner):
    fx = -s if flip else s
    return f'<g transform="translate({x} {y}) scale({fx} {s})">{inner}</g>'

def _part(d, fill, w=2.4, side=False, rim=None):
    """filled shape with shading and outline; rim is an optional top edge to catch the warm light"""
    out = f'<path d="{d}" fill="{fill}"></path><path d="{d}" fill="url(#scn-{"side" if side else "shade"})"></path>'
    if rim: out += f'<path d="{rim}" fill="none" stroke="#FFE4C0" stroke-width="2.4" stroke-linecap="round" opacity="0.55" transform="translate(0 2.5)"></path>'
    return out + f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{w}" stroke-linejoin="round"></path>'

def _lines(d, op=0.25, w=1.4):
    return f'<path d="{d}" fill="none" stroke="#000000" stroke-width="{w}" stroke-linecap="round" opacity="{op}"></path>'

def _blob(cx, cy, r, rnd, bumps=9, jitter=0.18):
    """lumpy rounded outline, for crowns and bushes"""
    pts = []
    for i in range(bumps):
        a = 2 * math.pi * i / bumps
        rr = r * (1 + rnd.uniform(-jitter, jitter))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.82))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} "
    for i in range(bumps):
        p, q = pts[i], pts[(i + 1) % bumps]
        a = 2 * math.pi * (i + 0.5) / bumps
        c = (cx + math.cos(a) * r * 1.28, cy + math.sin(a) * r * 1.05)
        d += f"Q{c[0]:.1f} {c[1]:.1f} {q[0]:.1f} {q[1]:.1f} "
    return d + "Z"

def _trunk(h, w0, w1, lean=0.0, color="#6B5440"):
    top = -h
    d = (f"M{-w0} 0 C{-w0 * 0.9:.1f} {top * 0.4:.1f} {-w1 + lean * 0.6:.1f} {top * 0.8:.1f} {-w1 + lean:.1f} {top} "
         f"L{w1 + lean:.1f} {top} C{w1 + lean * 0.6:.1f} {top * 0.8:.1f} {w0 * 0.9:.1f} {top * 0.4:.1f} {w0} 0 Z")
    return _part(d, color, side=True)

# ------------------------------------------------------------------ Morrison (Late Jurassic)
def araucarian(x, y, s=1.0, flip=False, color="#56663F", seed=1):
    """tall araucarian conifer: straight bare trunk, tiers of drooping branch tufts near the top"""
    rnd = random.Random(seed); h = 300
    out = _trunk(h * 0.92, 9, 4, color="#6E5642")
    for k in range(6):
        ty = -h * (0.56 + k * 0.08); span = 70 - k * 9
        for side in (-1, 1):
            x0, x1 = side * 3, side * span
            d = (f"M{x0} {ty:.0f} C{x0 + side * span * 0.4:.0f} {ty - 14:.0f} {x1 - side * 10:.0f} {ty - 10:.0f} {x1} {ty + 8:.0f} "
                 f"C{x1 - side * 8:.0f} {ty + 18:.0f} {x0 + side * span * 0.4:.0f} {ty + 10:.0f} {x0} {ty + 6:.0f} Z")
            out += _part(d, color, w=2, rim=f"M{x0} {ty:.0f} C{x0 + side * span * 0.4:.0f} {ty - 14:.0f} {x1 - side * 10:.0f} {ty - 10:.0f} {x1} {ty + 8:.0f}")
    out += _part(_blob(0, -h * 0.98, 20, rnd, 7), color, w=2)
    return _place(x, y, s, flip, out)

def cycad(x, y, s=1.0, flip=False, color="#5E6B3A", seed=2):
    """cycad: stout armoured trunk with a crown of stiff, feather-like fronds"""
    trunk = "M-18 0 C-20 -30 -18 -60 -14 -80 L14 -80 C18 -60 20 -30 18 0 Z"
    out = _part(trunk, "#7A6248", side=True) + _lines(" ".join(f"M-16 {-y0} L0 {-y0 - 8} L16 {-y0}" for y0 in range(8, 80, 12)), 0.3)
    for a, l in [(-150, 90), (-125, 110), (-100, 120), (-75, 118), (-50, 106), (-25, 86), (-160, 70), (-15, 66)]:
        r = math.radians(a); tx, ty = math.cos(r) * l, -80 + math.sin(r) * l * 0.9
        mx, my = math.cos(r) * l * 0.5, -80 + math.sin(r) * l * 0.62 - 14
        nx, ny = -math.sin(r) * 9, math.cos(r) * 9
        d = f"M0 -80 Q{mx + nx:.0f} {my + ny:.0f} {tx:.0f} {ty:.0f} Q{mx - nx:.0f} {my - ny:.0f} 0 -80 Z"
        out += _part(d, color, w=1.8) + _lines(f"M0 -80 Q{mx:.0f} {my:.0f} {tx:.0f} {ty:.0f}", 0.3, 1.2)
    return _place(x, y, s, flip, out)

def ginkgo(x, y, s=1.0, flip=False, color="#6F8A3E", seed=3):
    """ginkgo: upright trunk, open branches and a loose crown of fan-leaf clusters"""
    rnd = random.Random(seed)
    out = _trunk(150, 10, 5, color="#6E5642")
    out += _part("M-2 -120 C-20 -150 -40 -170 -60 -180 L-56 -186 C-34 -176 -12 -158 4 -136 Z M2 -130 C20 -160 40 -176 60 -186 L62 -180 C44 -170 26 -152 8 -122 Z", "#6E5642", w=2)
    for cx, cy, r in [(-62, -196, 34), (60, -198, 36), (0, -228, 44), (-30, -170, 28), (34, -168, 28)]:
        out += _part(_blob(cx, cy, r, rnd, 8, 0.22), color, w=2.2, rim=f"M{cx - r * 0.8:.0f} {cy - r * 0.5:.0f} Q{cx} {cy - r * 1.05:.0f} {cx + r * 0.8:.0f} {cy - r * 0.5:.0f}")
    fans = " ".join(f"M{cx} {cy} l-7 -10 q7 -5 14 0 Z" for cx, cy in [(-70, -200), (48, -214), (8, -246), (-20, -226), (70, -190), (-40, -176)])
    out += f'<path d="{fans}" fill="#8FA650" stroke="{OL}" stroke-width="1" opacity="0.9"></path>'
    return _place(x, y, s, flip, out)

def tree_fern(x, y, s=1.0, flip=False, color="#4F6B3C", seed=4):
    """tree fern: slender scaly trunk topped by long arching fronds"""
    out = _trunk(170, 8, 6, lean=6, color="#5E4A3A") + _lines(" ".join(f"M-6 {-y0} l12 -4" for y0 in range(14, 170, 14)), 0.3)
    for a, l in [(-170, 110), (-145, 120), (-120, 100), (-60, 100), (-35, 120), (-10, 110), (-95, 80)]:
        r = math.radians(a); tx, ty = 6 + math.cos(r) * l, -170 + math.sin(r) * l * 0.5 + l * 0.45
        mx, my = 6 + math.cos(r) * l * 0.5, -170 + math.sin(r) * l * 0.55 - 10
        d = f"M6 -170 Q{mx:.0f} {my - 8:.0f} {tx:.0f} {ty:.0f} Q{mx:.0f} {my + 8:.0f} 6 -166 Z"
        out += _part(d, color, w=1.8)
        out += _lines(" ".join(f"M{6 + (tx - 6) * k:.0f} {-170 + (ty + 170) * k - 12 * math.sin(math.pi * k):.0f} l{-4 if tx < 6 else 4} 7" for k in (0.25, 0.4, 0.55, 0.7, 0.85)), 0.35, 1.2)
    return _place(x, y, s, flip, out)

def horsetails(x, y, s=1.0, flip=False, color="#6E7E44", seed=5):
    """a clump of horsetails: jointed upright stems with whorls of fine leaves"""
    rnd = random.Random(seed); out = ""
    for i in range(7):
        bx = (i - 3) * 9 + rnd.uniform(-3, 3); h = rnd.uniform(60, 96); lean = rnd.uniform(-8, 8)
        d = f"M{bx - 3:.0f} 0 L{bx + lean - 2:.0f} {-h:.0f} L{bx + lean + 2:.0f} {-h:.0f} L{bx + 3:.0f} 0 Z"
        out += _part(d, color, w=1.4)
        out += _lines(" ".join(f"M{bx + lean * k - 7:.0f} {-h * k + 4:.0f} L{bx + lean * k:.0f} {-h * k:.0f} L{bx + lean * k + 7:.0f} {-h * k + 4:.0f}" for k in (0.3, 0.5, 0.7, 0.85)), 0.45, 1.1)
    return _place(x, y, s, flip, out)

# ------------------------------------------------------------------ Hell Creek (latest Cretaceous)
def broadleaf(x, y, s=1.0, flip=False, color="#5C7A3E", seed=6):
    """flowering broadleaf tree (magnolia relatives dominated Hell Creek forests)"""
    rnd = random.Random(seed)
    out = _trunk(130, 12, 7, color="#6A5240")
    out += _part("M-4 -110 C-24 -130 -44 -140 -64 -144 L-62 -152 C-40 -148 -18 -136 2 -122 Z M4 -116 C22 -136 44 -148 62 -152 L64 -146 C46 -140 26 -128 10 -108 Z", "#6A5240", w=2)
    for cx, cy, r in [(-60, -160, 46), (58, -164, 48), (0, -196, 58), (-28, -150, 40), (30, -150, 40)]:
        out += _part(_blob(cx, cy, r, rnd, 10, 0.16), color, w=2.4, rim=f"M{cx - r * 0.8:.0f} {cy - r * 0.45:.0f} Q{cx} {cy - r * 1.0:.0f} {cx + r * 0.8:.0f} {cy - r * 0.45:.0f}")
    leaves = " ".join(f"M{cx} {cy} q6 -8 14 -2 q-6 8 -14 2 Z" for cx, cy in [(-90, -160), (84, -170), (-20, -238), (30, -232), (-70, -196), (66, -200)])
    out += f'<path d="{leaves}" fill="#7C9A50" stroke="{OL}" stroke-width="1"></path>'
    return _place(x, y, s, flip, out)

def fan_palm(x, y, s=1.0, flip=False, color="#4E6E3A", seed=7):
    """fan palm: curving trunk with old leaf bases and a crown of fan-shaped leaves"""
    trunk = "M-9 0 C-10 -60 -2 -130 14 -176 L24 -174 C10 -128 4 -60 9 0 Z"
    out = _part(trunk, "#7A6246", side=True) + _lines(" ".join(f"M{-8 + k * 2.6:.0f} {-k * 17:.0f} l14 -5" for k in range(1, 10)), 0.32)
    for a in (-170, -140, -110, -80, -50, -20, -95):
        r = math.radians(a); cx, cy = 19 + math.cos(r) * 46, -176 + math.sin(r) * 34
        ribs = []
        for k in range(7):
            b = r + math.radians(-42 + k * 14)
            ribs.append((cx + math.cos(b) * 40, cy + math.sin(b) * 34))
        d = f"M19 -176 L{cx:.0f} {cy:.0f} " + " ".join(f"L{px:.0f} {py:.0f}" for px, py in ribs) + f" L{cx:.0f} {cy:.0f} Z"
        out += _part(d, color, w=1.6) + _lines(" ".join(f"M{cx:.0f} {cy:.0f} L{px:.0f} {py:.0f}" for px, py in ribs), 0.3, 1)
    return _place(x, y, s, flip, out)

def dawn_redwood(x, y, s=1.0, flip=False, color="#5D7A44", seed=8):
    """dawn redwood (Metasequoia): narrow conical conifer, rare in Hell Creek"""
    out = _trunk(260, 9, 2, color="#7A4E3A")
    for k in range(8):
        ty = -40 - k * 28; half = 62 - k * 7
        d = f"M0 {ty - 34} C{half * 0.4:.0f} {ty - 20} {half} {ty - 4} {half} {ty + 4} C{half * 0.5:.0f} {ty + 10} {-half * 0.5:.0f} {ty + 10} {-half} {ty + 4} C{-half} {ty - 4} {-half * 0.4:.0f} {ty - 20} 0 {ty - 34} Z"
        out += _part(d, color, w=1.8, rim=f"M{-half * 0.6:.0f} {ty - 10} C{-half * 0.3:.0f} {ty - 24} {half * 0.3:.0f} {ty - 24} {half * 0.6:.0f} {ty - 10}")
    return _place(x, y, s, flip, out)

def fern_clump(x, y, s=1.0, flip=False, color="#4C6A36", seed=9):
    """low ground ferns, common near water"""
    out = ""
    for a, l in [(-165, 70), (-140, 84), (-112, 92), (-80, 92), (-52, 84), (-25, 70), (-96, 64)]:
        r = math.radians(a); tx, ty = math.cos(r) * l, math.sin(r) * l * 0.8 + l * 0.25
        mx, my = math.cos(r) * l * 0.45, math.sin(r) * l * 0.6 - 8
        d = f"M0 0 Q{mx - 6:.0f} {my - 6:.0f} {tx:.0f} {ty:.0f} Q{mx + 6:.0f} {my + 6:.0f} 0 0 Z"
        out += _part(d, color, w=1.6)
        out += _lines(" ".join(f"M{tx * k:.0f} {ty * k - 10 * math.sin(math.pi * k):.0f} l{-3 if tx < 0 else 3} 6" for k in (0.3, 0.45, 0.6, 0.75)), 0.35, 1.1)
    return _place(x, y, s, flip, out)

# ------------------------------------------------------------------ Bahariya (Cenomanian mangrove coast)
def weichselia(x, y, s=1.0, flip=False, color="#55703C", seed=10):
    """Weichselia, the fern that dominated the Bahariya mangroves: tall stems with stiff, upright-arching fronds"""
    rnd = random.Random(seed); out = ""
    for i, (bx, h) in enumerate([(-16, 120), (0, 150), (14, 110)]):
        out += _part(f"M{bx - 3} 0 L{bx - 2} {-h} L{bx + 2} {-h} L{bx + 3} 0 Z", "#6A5A3E", w=1.4)
        for a, l in [(-140, 64), (-112, 74), (-80, 76), (-52, 70), (-30, 56)]:
            r = math.radians(a + rnd.uniform(-6, 6)); tx, ty = bx + math.cos(r) * l, -h + math.sin(r) * l * 0.8 + l * 0.15
            mx, my = bx + math.cos(r) * l * 0.5, -h + math.sin(r) * l * 0.55
            d = f"M{bx} {-h} Q{mx - 5:.0f} {my - 4:.0f} {tx:.0f} {ty:.0f} Q{mx + 5:.0f} {my + 4:.0f} {bx} {-h} Z"
            out += _part(d, color, w=1.4)
            out += _lines(" ".join(f"M{bx + (tx - bx) * k:.0f} {-h + (ty + h) * k:.0f} l{-5 if tx < bx else 5} -4 M{bx + (tx - bx) * k:.0f} {-h + (ty + h) * k:.0f} l{-3 if tx < bx else 3} 5" for k in (0.3, 0.5, 0.7)), 0.35, 1)
    return _place(x, y, s, flip, out)

def mudflat(x, y, s=1.0, flip=False, color="#8C7A5A", seed=11):
    """tidal mud bank with a waterline and ripples"""
    d = "M-160 0 C-120 -16 -40 -22 40 -18 C100 -16 140 -8 160 0 Z"
    out = _part(d, color, w=2, rim="M-150 -4 C-100 -18 -20 -22 60 -18")
    out += _lines("M-110 -6 C-80 -10 -50 -10 -20 -8 M10 -8 C40 -10 70 -10 100 -6", 0.25, 1.4)
    return _place(x, y, s, flip, out)

# ------------------------------------------------------------------ Cerro Barcino (Albian, drier floodplain)
def flowering_shrub(x, y, s=1.0, flip=False, color="#6E7A44", seed=12):
    """low shrub with tiny pale flowers, after early flowering plants like Patagoflora"""
    rnd = random.Random(seed)
    out = _part(_blob(0, -30, 44, rnd, 9, 0.2), color, w=2.2, rim="M-34 -50 Q0 -78 34 -50")
    flowers = "".join(f'<circle cx="{rnd.uniform(-36, 36):.0f}" cy="{rnd.uniform(-60, -10):.0f}" r="2.4" fill="#F4E6C2" stroke="{OL}" stroke-width="0.8"></circle>' for _ in range(14))
    return _place(x, y, s, flip, out + flowers)

def dry_conifer(x, y, s=1.0, flip=False, color="#66704A", seed=13):
    """sparse, wind-shaped conifer for drier ground"""
    rnd = random.Random(seed)
    out = _trunk(170, 8, 3, lean=-10, color="#6E5642")
    for cx, cy, r in [(-30, -150, 26), (10, -178, 30), (36, -140, 22), (-12, -120, 20)]:
        out += _part(_blob(cx, cy, r, rnd, 7, 0.25), color, w=2, rim=f"M{cx - r * 0.7:.0f} {cy - r * 0.4:.0f} Q{cx} {cy - r:.0f} {cx + r * 0.7:.0f} {cy - r * 0.4:.0f}")
    return _place(x, y, s, flip, out)

# ------------------------------------------------------------------ shared pieces
def boulder(x, y, s=1.0, flip=False, color="#8A8170", seed=14):
    """faceted boulder with a lit top face"""
    d = "M-60 0 C-66 -26 -50 -52 -18 -60 C14 -66 46 -54 58 -30 C64 -16 62 -6 58 0 Z"
    out = _part(d, color, rim="M-50 -40 C-30 -58 10 -64 40 -50")
    out += _lines("M-20 -58 C-14 -40 -18 -22 -28 -4 M18 -62 C26 -44 30 -24 24 -2", 0.22, 1.6)
    return _place(x, y, s, flip, out)

def pebbles(x, y, s=1.0, flip=False, color="#9A8E78", seed=15):
    rnd = random.Random(seed)
    out = "".join(_part(f"M{px - w} 0 C{px - w} {-h} {px + w} {-h} {px + w} 0 Z", color, w=1.4) for px, w, h in
                  [(rnd.uniform(-60, 60), rnd.uniform(6, 14), rnd.uniform(6, 12)) for _ in range(9)])
    return _place(x, y, s, flip, out)

def cloud(x, y, s=1.0, flip=False, color="#F6EEE0", seed=16):
    """soft cloud, no outline, for distant sky"""
    rnd = random.Random(seed)
    blobs = "".join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"></ellipse>' for cx, cy, rx, ry in
                    [(-50, -10, 50, 22), (10, -24, 60, 32), (66, -10, 46, 20), (0, 0, 110, 16)])
    return _place(x, y, s, flip, f'<g fill="{color}" opacity="0.85">{blobs}</g><g fill="#FFFFFF" opacity="0.5"><ellipse cx="0" cy="-34" rx="40" ry="12"></ellipse></g>')

HABITATS = {
    "Morrison (Stegosaurus)": [("Araucarian conifer", araucarian, 0.7), ("Cycad", cycad, 1.0), ("Ginkgo", ginkgo, 0.8), ("Tree fern", tree_fern, 0.9), ("Horsetails", horsetails, 1.1)],
    "Hell Creek (T. rex, Triceratops, Ankylosaurus)": [("Broadleaf tree", broadleaf, 0.8), ("Fan palm", fan_palm, 0.9), ("Dawn redwood", dawn_redwood, 0.7), ("Ferns", fern_clump, 1.2)],
    "Bahariya (Spinosaurus)": [("Weichselia fern", weichselia, 1.1), ("Tidal mud bank", mudflat, 0.8)],
    "Cerro Barcino (Patagotitan)": [("Flowering shrub", flowering_shrub, 1.2), ("Dry-ground conifer", dry_conifer, 0.9)],
    "Any habitat": [("Boulder", boulder, 1.0), ("Pebbles", pebbles, 1.0), ("Cloud", cloud, 0.8)],
}

# ------------------------------------------------------------------ complete sets: sky, far layer, haze, middle layer, ground, foreground
def _band(y, h, color, phase=0, w=1080):
    return (f'<path d="M0 {y} C{w*0.25:.0f} {y - 6 + phase} {w*0.5:.0f} {y + 6 - phase} {w*0.75:.0f} {y - 3} C{w*0.86:.0f} {y + 4} {w*0.94:.0f} {y} {w} {y - 2} '
            f'L{w} {y + h} C{w*0.75:.0f} {y + h + 4} {w*0.5:.0f} {y + h - 5} {w*0.25:.0f} {y + h + 3} C{w*0.15:.0f} {y + h + 6} {w*0.06:.0f} {y + h} 0 {y + h + 2} Z" fill="{color}"></path>')

def _hills(y, amp, color, seed, w=1080):
    rnd = random.Random(seed); pts = [(0, y)]
    for k in range(1, 7):
        pts.append((w * k / 6, y - rnd.uniform(0.2, 1) * amp))
    d = f"M0 {y} " + " ".join(f"Q{(a[0] + b[0]) / 2:.0f} {min(a[1], b[1]) - amp * 0.4:.0f} {b[0]:.0f} {b[1]:.0f}" for a, b in zip(pts, pts[1:]))
    return f'<path d="{d} L{w} 900 L0 900 Z" fill="{color}"></path>'

def _sky(sid, top, mid, low, sun, sun_xy):
    return (f'<linearGradient id="{sid}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"></stop><stop offset="0.55" stop-color="{mid}"></stop><stop offset="0.8" stop-color="{low}"></stop></linearGradient>'
            f'<radialGradient id="{sid}-sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{sun}" stop-opacity="0.9"></stop><stop offset="0.3" stop-color="{sun}" stop-opacity="0.4"></stop><stop offset="1" stop-color="{sun}" stop-opacity="0"></stop></radialGradient>'
            f'<linearGradient id="{sid}-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{low}" stop-opacity="0"></stop><stop offset="0.6" stop-color="{low}" stop-opacity="0.65"></stop><stop offset="1" stop-color="{low}" stop-opacity="0"></stop></linearGradient>'
            f'<linearGradient id="{sid}-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"></stop><stop offset="1" stop-color="#2A1E10" stop-opacity="0.36"></stop></linearGradient>'
            f'<radialGradient id="{sid}-shadow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#2A1E10" stop-opacity="0.38"></stop><stop offset="1" stop-color="#2A1E10" stop-opacity="0"></stop></radialGradient>')

def _far(markup, tint, op=0.55):
    """distant layer: drawn smaller, then washed with the sky colour for depth"""
    return f'<g opacity="{op}" style="filter: saturate(0.6)">{markup}</g>'

def treeline(fn, y, smin, smax, n, seed=0, gap=None):
    """a dense, distant row of one plant, varied in size, for depth"""
    rnd = random.Random(seed); out = []
    for i in range(n):
        x = -20 + 1120 * (i + rnd.uniform(0.1, 0.9)) / n
        if gap and gap[0] < x < gap[1]: continue
        out.append(fn(round(x), y + rnd.uniform(-4, 4), rnd.uniform(smin, smax), flip=rnd.random() < 0.5, seed=seed * 31 + i))
    return f'<g opacity="0.7">{"".join(out)}</g>'

def _frame(sid, defs_extra, body, w=1080, h=900):
    return (f'<svg aria-hidden="true" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="position: absolute; top: 0; left: 0; display: block">'
            f'{defs()}<defs>{defs_extra}</defs>{body}</svg>')

def set_morrison():
    """Late Jurassic Morrison floodplain, hazy noon: conifer stands, tree ferns and cycads; no grass"""
    sid = "scn-mor"
    far = treeline(araucarian, 680, 0.34, 0.5, 16, seed=1) + "".join(araucarian(x, 694, sc, seed=i) for i, (x, sc) in enumerate([(70, 0.62), (150, 0.5), (900, 0.66), (990, 0.55), (820, 0.45)]))
    mid = tree_fern(230, 712, 0.55) + tree_fern(276, 714, 0.45, True, seed=2) + cycad(196, 716, 0.5) + ginkgo(770, 712, 0.5) + tree_fern(860, 714, 0.5, True) + horsetails(650, 716, 0.7) + horsetails(330, 718, 0.6, seed=8)
    body = (f'<rect width="1080" height="900" fill="url(#{sid}-sky)"></rect><circle cx="780" cy="260" r="300" fill="url(#{sid}-sun)"></circle>'
            + cloud(240, 190, 1.1) + cloud(880, 140, 0.8, seed=3)
            + _hills(660, 60, "#C7B7A0", 1) + _far(far, "#E8DCC4")
            + f'<rect y="560" width="1080" height="180" fill="url(#{sid}-haze)"></rect>' + mid
            + '<path d="M0 716 C200 704 420 718 640 710 C820 702 960 714 1080 708 L1080 900 L0 900 Z" fill="#CDAE72"></path>'
            + _band(752, 16, "#BF9C5E") + _band(792, 22, "#D9BE86", 2) + _band(840, 60, "#B58A4E", -2)
            + f'<rect y="706" width="1080" height="194" fill="url(#{sid}-ground)"></rect><ellipse cx="560" cy="822" rx="380" ry="24" fill="url(#{sid}-shadow)"></ellipse>'
            + cycad(60, 905, 1.0) + cycad(1030, 910, 1.1, True, seed=5) + fern_clump(170, 900, 1.3) + boulder(940, 880, 0.7) + pebbles(400, 870, 0.8))
    return _frame(sid, _sky(sid, "#B9CFD8", "#EDE3CC", "#F2E8D2", "#FFF4DC", (780, 260)), body)

def set_hell_creek():
    """latest Cretaceous Hell Creek river plain, warm late afternoon: broadleaf forest, palms, ferns by the water"""
    sid = "scn-hc"
    far = treeline(broadleaf, 684, 0.26, 0.4, 18, seed=2) + "".join(broadleaf(x, 690, sc, seed=i) for i, (x, sc) in enumerate([(60, 0.55), (180, 0.45), (870, 0.6), (980, 0.5)])) + dawn_redwood(300, 692, 0.45)
    mid = fan_palm(760, 716, 0.55) + fan_palm(820, 714, 0.45, True, seed=2) + broadleaf(140, 718, 0.4, seed=9) + broadleaf(940, 716, 0.42, seed=4) + fan_palm(240, 716, 0.42, seed=3) + fern_clump(700, 718, 0.6)
    body = (f'<rect width="1080" height="900" fill="url(#{sid}-sky)"></rect><circle cx="220" cy="600" r="330" fill="url(#{sid}-sun)"></circle>'
            + cloud(700, 170, 1.2) + cloud(300, 120, 0.7, seed=4)
            + _hills(670, 40, "#B9BC9A", 2) + _far(far, "#E6D8BC")
            + f'<rect y="560" width="1080" height="180" fill="url(#{sid}-haze)"></rect>' + mid
            + '<path d="M0 712 C200 700 420 716 640 706 C820 698 960 708 1080 702 L1080 900 L0 900 Z" fill="#9AA864"></path>'
            + '<path d="M0 734 C220 724 440 742 660 732 C840 724 980 734 1080 728 L1080 758 C960 764 820 754 660 762 C440 772 220 752 0 762 Z" fill="#9FBCC2"></path>'
            + '<path d="M120 744 L260 742 M520 750 L700 746 M860 740 L980 738" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.5"></path>'
            + _band(780, 20, "#8C9A58") + _band(812, 24, "#A7B26E", 2) + _band(850, 50, "#7F8D4E", -2)
            + f'<rect y="704" width="1080" height="196" fill="url(#{sid}-ground)"></rect><ellipse cx="560" cy="826" rx="360" ry="24" fill="url(#{sid}-shadow)"></ellipse>'
            + fern_clump(60, 905, 1.5) + fern_clump(170, 910, 1.1, True, seed=3) + fern_clump(1020, 905, 1.4, True) + boulder(900, 880, 0.55, seed=2))
    return _frame(sid, _sky(sid, "#A8C6CF", "#D4DCCB", "#EED9B0", "#FFE2B0", (220, 600)), body)

def set_bahariya():
    """Cenomanian Bahariya coast: tidal channels and mud banks fringed by Weichselia fern thickets"""
    sid = "scn-bah"
    far = treeline(weichselia, 684, 0.38, 0.6, 22, seed=3)
    body = (f'<rect width="1080" height="900" fill="url(#{sid}-sky)"></rect><circle cx="200" cy="560" r="330" fill="url(#{sid}-sun)"></circle>'
            + cloud(760, 150, 1.0) + cloud(420, 210, 0.7, seed=6)
            + _far(far, "#EED7B4", 0.6)
            + f'<rect y="580" width="1080" height="160" fill="url(#{sid}-haze)"></rect>'
            + '<path d="M0 694 C220 686 460 700 700 692 C860 686 980 692 1080 688 L1080 900 L0 900 Z" fill="#9FB3AE"></path>'
            + '<path d="M60 718 L220 716 M420 728 L640 724 M820 714 L980 712 M140 768 L320 764 M600 776 L760 772" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.45"></path>'
            + mudflat(160, 742, 1.1) + mudflat(900, 736, 0.9, True) + weichselia(110, 734, 0.5, seed=5) + weichselia(190, 738, 0.42, True, seed=6) + weichselia(930, 728, 0.45, seed=7)
            + '<path d="M0 792 C200 776 420 786 640 780 C820 776 960 784 1080 778 L1080 900 L0 900 Z" fill="#C3A877"></path>'
            + _band(836, 18, "#B09461") + _band(866, 40, "#A3885A", 1)
            + f'<rect y="780" width="1080" height="120" fill="url(#{sid}-ground)"></rect><ellipse cx="560" cy="836" rx="380" ry="22" fill="url(#{sid}-shadow)"></ellipse>'
            + weichselia(50, 905, 1.3) + weichselia(1030, 908, 1.2, True, seed=4) + pebbles(820, 880, 0.9))
    return _frame(sid, _sky(sid, "#BFCFD3", "#E9DCC0", "#F2CF98", "#FFD596", (200, 560)), body)

def set_cerro_barcino():
    """latest Albian Cerro Barcino floodplain, dry and open: scattered conifers and low flowering shrubs"""
    sid = "scn-cb"
    far = treeline(dry_conifer, 692, 0.25, 0.42, 12, seed=4, gap=(380, 640)) + "".join(dry_conifer(x, 696, sc, flip=i % 2 == 1, seed=i) for i, (x, sc) in enumerate([(80, 0.55), (190, 0.45), (850, 0.6), (970, 0.5)]))
    body = (f'<rect width="1080" height="900" fill="url(#{sid}-sky)"></rect><circle cx="860" cy="420" r="320" fill="url(#{sid}-sun)"></circle>'
            + cloud(300, 160, 1.2) + cloud(760, 110, 0.8, seed=8)
            + _hills(650, 90, "#C9B39A", 5) + _hills(690, 50, "#B8A88A", 6) + _far(far, "#E9DCC6")
            + f'<rect y="580" width="1080" height="160" fill="url(#{sid}-haze)"></rect>'
            + '<path d="M0 722 C200 712 400 726 600 718 C800 710 950 722 1080 716 L1080 900 L0 900 Z" fill="#B9A274"></path>'
            + flowering_shrub(240, 726, 0.45, seed=7) + flowering_shrub(820, 724, 0.5, True, seed=9) + flowering_shrub(700, 728, 0.35, seed=11)
            + _band(766, 18, "#A48D60") + _band(804, 22, "#C7B184", 2) + _band(850, 50, "#9C8458", -1)
            + f'<rect y="716" width="1080" height="184" fill="url(#{sid}-ground)"></rect><ellipse cx="560" cy="836" rx="380" ry="24" fill="url(#{sid}-shadow)"></ellipse>'
            + flowering_shrub(70, 900, 1.6) + flowering_shrub(1010, 905, 1.4, True, seed=4) + dry_conifer(1050, 910, 1.1, True, seed=2) + boulder(180, 890, 0.6, seed=3) + pebbles(900, 880, 0.8))
    return _frame(sid, _sky(sid, "#A9BFCB", "#E4DDCC", "#EFD9B4", "#FFF0D2", (860, 420)), body)

SETS = {"Morrison": set_morrison, "Hell Creek": set_hell_creek, "Bahariya": set_bahariya, "Cerro Barcino": set_cerro_barcino}


# ------------------------------------------------------------------ outputs: one SVG per asset and per set, plus a sheet board
def _slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")

def _standalone(inner, w, h, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"></rect>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs()}{rect}{inner}</svg>\n'

def sheet_svg():
    """every asset, one row per habitat, labelled"""
    rows, y0 = [], 40
    for hab, items in HABITATS.items():
        cells = "".join(f'<g>{fn(110 + i * 210, 300, sc)}<text x="{110 + i * 210}" y="332" text-anchor="middle" font-family="Public Sans, system-ui, sans-serif" font-size="15" fill="#2B1E16">{name}</text></g>'
                        for i, (name, fn, sc) in enumerate(items))
        rows.append(f'<g transform="translate(0 {y0})"><text x="24" y="20" font-family="Public Sans, system-ui, sans-serif" font-weight="600" font-size="18" fill="#2B1E16">{hab}</text>{cells}</g>')
        y0 += 350
    return rows, y0

if __name__ == "__main__":
    out = pathlib.Path(ROOT) / "svg" / "scenery"; out.mkdir(parents=True, exist_ok=True)
    for hab, items in HABITATS.items():
        for name, fn, sc in items:
            (out / f"{_slug(hab.split(' (')[0])}-{_slug(name)}.svg").write_text(_standalone(fn(150, 380, sc), 300, 400))
    for name, fn in SETS.items():
        svg = fn().replace('aria-hidden="true" ', 'xmlns="http://www.w3.org/2000/svg" ', 1).replace(' style="position: absolute; top: 0; left: 0; display: block"', "")
        (out / f"set-{_slug(name)}.svg").write_text(svg + "\n")
    rows, h = sheet_svg()
    sets = "".join(f'<div style="display: flex; flex-direction: column; gap: 8px"><div style="position: relative; width: 540px; height: 450px; overflow: hidden; border-radius: 10px"><div style="transform: scale(0.5); transform-origin: 0 0; width: 1080px; height: 900px; position: relative">{fn()}</div></div><span style="font-size: 17px; font-weight: 600">{name}</span></div>'
                   for name, fn in SETS.items())
    board = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Scenery kit</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600&amp;display=swap">
<style>body{{margin:0}}</style>
</helmet>
<div style="width: 1180px; box-sizing: border-box; padding: 40px 50px; background: #EFE7D6; font-family: 'Public Sans', system-ui, sans-serif; color: #2B1E16; display: flex; flex-direction: column; gap: 28px">
<div style="display: flex; flex-direction: column; gap: 6px; max-width: 760px">
<h1 style="margin: 0; font-size: 34px; font-weight: 600">Scenery kit</h1>
<p style="margin: 0; font-size: 17px; line-height: 1.5; color: #6E5D4E">Plants and ground pieces for each animal's world, chosen from the fossil flora of its rock formation, and the four poster backgrounds built from them. Built by src/scenery.py.</p>
</div>
<svg role="img" aria-label="Scenery pieces by habitat" viewBox="0 0 1080 {h}" width="1080" height="{h}" style="display: block">{defs()}{"".join(rows)}</svg>
<div style="display: grid; grid-template-columns: repeat(2, 540px); gap: 24px">{sets}</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1180,"height":{h + 1260}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''
    (pathlib.Path(ROOT) / "boards" / "Scenery.dc.html").write_text(board)
    print("ok", len(list(out.glob("*.svg"))), "files; board height", h + 1260)
