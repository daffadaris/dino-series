"""2D design styles of a species drawing, each with its own construction (shape language, line, how tone
is made), not a recolour. Same group ids, classes, pivots and motion CSS as svg/<species>-animated.svg.
Choice and recipes: reports/Dinosaur SVG illustration styles.md. SVGs are transparent cutouts; backdrops live
in the preview pages. Usage: python3 src/styles.py [style ...] [species ...]  (defaults: all styles, trex);
several species also write svg/styles/<style>.html, one style across those species.
"""
import colorsys, math, pathlib, random, re, sys
import stylekit as K
import dinokit as D

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "svg" / "styles"
INK, OL = "#1D1E30", "#2A1C22"          # lifted charcoal, never #000000
PUPIL = "#15110D"                        # dinokit.eye pupil fill: marks the eye in every species
LENGTH_M = {"trex": 12, "triceratops": 8.5, "stegosaurus": 6.5, "titanosaur": 31, "ankylosaurus": 7,
            "spinosaurus": 14, "pachycephalosaurus": 3.0}  # README "Scientific accuracy" (checked adult lengths)
NAMES = {"trex": "Tyrannosaurus rex", "triceratops": "Triceratops horridus", "stegosaurus": "Stegosaurus stenops",
         "titanosaur": "Patagotitan mayorum", "ankylosaurus": "Ankylosaurus magniventris",
         "spinosaurus": "Spinosaurus aegyptiacus", "pachycephalosaurus": "Pachycephalosaurus wyomingensis"}


def rng(*key):
    return random.Random("-".join(map(str, key)))


def area(p):
    return abs(K.area(p))


def is_pupil(l):
    return l.tag == "circle" and l.fill.upper() == PUPIL


def path(d, fill="none", stroke=None, w=None, extra=""):
    s = f' stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{s}{extra}/>'


# ------------------------------------------------------------------ extra geometry
def scan(p, y):
    """x-intervals where the horizontal line y lies inside polygon p."""
    xs = sorted(x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                for (x1, y1), (x2, y2) in zip(p, p[1:] + p[:1]) if (y1 > y) != (y2 > y))
    return list(zip(xs[::2], xs[1::2]))


def rot(p, deg, c=(0, 0)):
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in p]


def clip(p, a, b, c):
    """Sutherland-Hodgman: part of p where a*x + b*y <= c."""
    out = []
    for P, Q in zip(p, p[1:] + p[:1]):
        fp, fq = a * P[0] + b * P[1] - c, a * Q[0] + b * Q[1] - c
        if fp <= 0: out.append(P)
        if (fp <= 0) != (fq <= 0):
            t = fp / (fp - fq); out.append((P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t))
    return out


def edge_dist(pt, p):
    best = 1e9
    for a, b in zip(p, p[1:] + p[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy or 1
        t = max(0, min(1, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / L))
        best = min(best, math.dist(pt, (a[0] + t * dx, a[1] + t * dy)))
    return best


def delaunay(pts):
    """Bowyer-Watson; returns index triples into pts."""
    x0, y0, x1, y1 = K.bbox(pts); m = max(x1 - x0, y1 - y0) * 20
    P = pts + [(x0 - m, y0 - m), (x0 + 2 * m, y0 - m), (x0 - m, y0 + 2 * m)]
    n = len(pts); tris = [(n, n + 1, n + 2)]

    def circ(t):
        (ax, ay), (bx, by), (cx, cy) = (P[i] for i in t)
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) or 1e-9
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return ux, uy, (ax - ux) ** 2 + (ay - uy) ** 2

    cache = {tris[0]: circ(tris[0])}
    for i, (x, y) in enumerate(pts):
        bad = [t for t in tris if (x - cache[t][0]) ** 2 + (y - cache[t][1]) ** 2 < cache[t][2]]
        edges = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = tuple(sorted(e)); edges[k] = edges.get(k, 0) + 1
        tris = [t for t in tris if t not in bad]
        for (a, b), cnt in edges.items():
            if cnt == 1:
                t = (a, b, i); tris.append(t); cache[t] = circ(t)
    return [t for t in tris if max(t) < n]


def jitter(p, r, amt):
    return [(x + r.uniform(-amt, amt), y + r.uniform(-amt, amt)) for x, y in p]


def hexrgb(c):
    return [v / 255 for v in K.rgb(c)]


# ------------------------------------------------------------------ 1. blueprint
def blueprint(sp):
    W, DIM, PIV = "#EAF3FF", "#9CC4EC", "#7FD8FF"

    def render(l):
        if l.kind in ("base", "limb"):
            return "".join(path(K.d_smooth(K.resample(p, 9)), stroke=W, w=2) for p in l.polys() if area(p) > 4)
        if l.kind == "tone" and l.op >= 0.25:
            return "".join(path(K.d_poly(K.resample(p, 6)), stroke=DIM, w=0.9) for p in l.polys() if area(p) < 4000)
        if l.kind == "line" and l.op >= 0.15:
            return "".join(path(K.d_poly(K.resample(p, 4, c), c), stroke=DIM, w=1) for p, c in l.shapes if len(p) > 1)

    def after(gid, leaves, pivot):
        polys = [p for l in leaves if l.kind in ("base", "limb") for p in l.polys()]
        if not polys: return ""
        (cx, cy), a, b, ang = K.moments(max(polys, key=area))
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        v = (-u[1], u[0])
        axis = lambda d, r: f"M{cx - d[0] * r:.1f} {cy - d[1] * r:.1f} L{cx + d[0] * r:.1f} {cy + d[1] * r:.1f}"
        s = (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{a:.1f}" ry="{b:.1f}" transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})" '
             f'fill="none" stroke="{DIM}" stroke-width="1" stroke-dasharray="7 5"/>'
             + path(axis(u, a + 12) + " " + axis(v, b + 12), stroke=DIM, w=0.8, extra=' stroke-dasharray="16 4 3 4"'))
        if pivot:
            x, y = pivot
            s += (f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="{PIV}" stroke-width="1.4"/>'
                  + path(f"M{x - 10} {y} H{x + 10} M{x} {y - 10} V{y + 10}", stroke=PIV, w=1.4))
        return s

    return render, after, ""


# ------------------------------------------------------------------ 2. neon sign
def neon(sp):
    TUBE = {"head": "#3DF5FF", "jaw": "#3DF5FF", "neck": "#3DF5FF", "leg-near": "#FFE14D", "leg-far": "#FFE14D",
            "arm-near": "#FFE14D", "arm-far": "#FFE14D", "foreleg-near": "#FFE14D", "foreleg-far": "#FFE14D"}

    def tube(d, c, w=4.5):
        # glass, core and hot centre as three opaque strokes: crisp alpha, no blur filter
        return (path(d, stroke=K.mix(c, "#140A2E", 0.62), w=w + 6) + path(d, stroke=c, w=w)
                + path(d, stroke=K.mix(c, "#FFFFFF", 0.7), w=w * 0.33))

    def render(l):
        c = TUBE.get(l.part, "#FF4FD8")
        if is_pupil(l):
            (x, y), _, _, _ = K.moments(l.polys()[0]); return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{c}"/>'
        if l.kind in ("base", "limb"):
            return "".join(tube(K.d_poly(K.chaikin(K.resample(p, 12), 2)), c) for p in l.polys() if area(p) > 60)
        if l.kind == "tone" and l.op >= 0.25 and l.idx % 2 == 0:
            s = ""
            for p in l.polys():
                (cx, cy), a, b, ang = K.moments(p)
                if area(p) < 2500 and a > 2.2 * b:
                    dx, dy = math.cos(math.radians(ang)) * a * 0.8, math.sin(math.radians(ang)) * a * 0.8
                    s += tube(f"M{cx - dx:.1f} {cy - dy:.1f} L{cx + dx:.1f} {cy + dy:.1f}", c, 3)
            return s
        if l.kind == "line" and l.op >= 0.5:
            return "".join(tube(K.d_poly(K.resample(p, 6, c2), c2), c, 3) for p, c2 in l.shapes if len(p) > 1)

    return render, None, ""


# ------------------------------------------------------------------ 3. pixel art
def pixel(sp, CELL=6):
    last = {}

    def cells(p):
        x0, y0, x1, y1 = K.bbox(p)
        got = {(i, j) for j in range(int(y0 // CELL), int(y1 // CELL) + 1) for i in range(int(x0 // CELL), int(x1 // CELL) + 1)
               if K.inside(((i + 0.5) * CELL, (j + 0.5) * CELL), p)}
        if not got:
            cx, cy = K.centroid(p); got = {(int(cx // CELL), int(cy // CELL))}
        return got

    def emit(colored):
        rows = {}
        for (i, j), c in colored.items(): rows.setdefault((j, c), []).append(i)
        by_c = {}
        for (j, c), xs in rows.items():
            xs.sort(); start = prev = xs[0]
            for x in xs[1:] + [None]:
                if x is not None and x == prev + 1: prev = x; continue
                by_c.setdefault(c, []).append(f"M{start * CELL} {j * CELL}h{(prev - start + 1) * CELL}v{CELL}h-{(prev - start + 1) * CELL}z")
                if x is not None: start = prev = x
        return "".join(f'<path d="{"".join(d)}" fill="{c}" shape-rendering="crispEdges"/>' for c, d in by_c.items())

    def render(l):
        if is_pupil(l):
            return emit({c: INK for c in cells(l.polys()[0])})
        if l.kind in ("base", "limb"):
            col = l.fill; last[l.part] = col
            light, dark, edge, rim = (K.mix(col, "#FFE9A8", 0.3), K.mix(col, "#3B1F4A", 0.35),
                                      K.mix(col, OL, 0.7), K.mix(col, OL, 0.4))
            out = {}
            for p in l.polys():
                C = cells(p); j0 = min(j for _, j in C); j1 = max(j for _, j in C)
                for i, j in C:
                    t = (j - j0) / max(1, j1 - j0)
                    c = light if t < 0.28 else dark if t > 0.7 else col
                    if len(C) > 4:
                        if (i, j - 1) not in C: c = rim                       # lighter outline on top
                        elif any(n not in C for n in ((i, j + 1), (i - 1, j), (i + 1, j))): c = edge
                    out[(i, j)] = c
            return emit(out)
        if l.kind == "tone" and l.op >= 0.2:
            c = K.mix(last.get(l.part, "#888888"), OL, min(0.8, l.op * 1.3))
            return emit({k: c for p in l.polys() for k in cells(p)})

    return render, None, ""


# ------------------------------------------------------------------ 4. Ben-Day pop art
def benday(sp):
    PAL = {"magenta": ("#E5007E", 0.92), "red": ("#E8312F", 0.0), "yellow": ("#FFE500", 0.15), "cyan": ("#00A6E0", 0.54)}
    defs = "".join(f'<pattern id="bd-{n}" patternUnits="userSpaceOnUse" width="9" height="9" patternTransform="rotate(20)">'
                   f'<rect width="9" height="9" fill="{K.mix(c, "#FFFFFF", 0.8)}"/><circle cx="4.5" cy="4.5" r="2.5" fill="{c}"/></pattern>'
                   for n, (c, _) in PAL.items())
    last = {}

    def pick(col):
        if K.lum(col) > 0.85: return None
        h, s, v = colorsys.rgb_to_hsv(*hexrgb(col))
        if K.lum(col) > 0.7: return "yellow"
        return min(PAL, key=lambda n: min(abs(h - PAL[n][1]), 1 - abs(h - PAL[n][1])))

    def render(l):
        if is_pupil(l):
            return path(K.d_poly(l.polys()[0]), INK)
        if l.kind in ("base", "limb"):
            n = pick(l.fill); last[l.part] = n
            s = ""
            for p in l.polys():
                fill = "#FFFFFF" if n is None else f"url(#bd-{n})" if area(p) > 400 else PAL[n][0]
                s += path(K.d_poly(p), fill, INK, 4 if area(p) > 400 else 2)
            return s
        if l.kind == "tone" and l.op >= 0.25:
            n = last.get(l.part)
            return "".join(path(K.d_poly(p), INK if area(p) < 3000 or n is None else PAL[n][0]) for p in l.polys())
        if l.kind == "line" and l.op >= 0.3:
            return "".join(path(K.d_poly(p, c), stroke=INK, w=2.5) for p, c in l.shapes if len(p) > 1)

    return render, None, defs


# ------------------------------------------------------------------ 5. low-poly
def lowpoly(sp):
    LIGHT = [x / v for x, v in zip((-0.45, -0.65, 0.6), [math.sqrt(0.45 ** 2 + 0.65 ** 2 + 0.6 ** 2)] * 3)]
    last = {}

    def facets(p, col, r):
        per = K.perimeter(p)
        bnd = K.resample(p, per / max(10, min(30, per / 28)))
        s_ = max(20, math.sqrt(area(p) / 45))
        x0, y0, x1, y1 = K.bbox(p)
        inner = []
        for gy in range(int(y0 / s_), int(y1 / s_) + 1):
            for gx in range(int(x0 / s_), int(x1 / s_) + 1):
                q = ((gx + 0.5 + r.uniform(-0.35, 0.35)) * s_, (gy + 0.5 + r.uniform(-0.35, 0.35)) * s_)
                if K.inside(q, p) and edge_dist(q, bnd) > s_ * 0.4: inner.append(q)
        pts = bnd + inner
        z = [0.0] * len(bnd) + [min(edge_dist(q, bnd), 60) * 0.9 for q in inner]
        out = ""
        for t in delaunay(pts):
            a, b, c = (pts[i] for i in t)
            if not K.inside(((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3), p): continue
            A = (b[0] - a[0], b[1] - a[1], z[t[1]] - z[t[0]]); B = (c[0] - a[0], c[1] - a[1], z[t[2]] - z[t[0]])
            n = (A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0])
            m = math.sqrt(sum(v * v for v in n)) or 1
            n = [v / m for v in n] if n[2] >= 0 else [-v / m for v in n]
            lam = round(max(0, sum(x * y for x, y in zip(n, LIGHT))) * 6) / 6
            f = K.mix(col, "#2B1B3A", (0.55 - lam) * 1.1) if lam < 0.55 else K.mix(col, "#FFF1C9", (lam - 0.55) * 0.9)
            out += path(K.d_poly([a, b, c]), f, f, 0.6)
        return out

    def render(l):
        if is_pupil(l): return path(K.d_poly(K.resample(l.polys()[0], 3)), INK)
        if l.kind in ("base", "limb"):
            last[l.part] = l.fill; r = rng(sp, "lowpoly", l.part, l.idx)
            return "".join(facets(p, l.fill, r) if area(p) > 250 else
                           path(K.d_poly(K.resample(p, max(3, K.perimeter(p) / 5))), l.fill, l.fill, 0.6) for p in l.polys())
        if l.kind == "tone" and l.op >= 0.25:
            c = K.mix(last.get(l.part, "#777777"), "#2B1B3A", min(0.7, l.op * 1.4))
            return "".join(path(K.d_poly(K.resample(p, max(4, K.perimeter(p) / 6))), c, c, 0.6) for p in l.polys() if area(p) < 4000)

    return render, None, ""


# ------------------------------------------------------------------ 6. woodcut
def woodcut(sp):
    PAPER, WINK = "#F1E6CF", "#231B1E"

    def gouges(q, r, top, color, wmax):
        """Tapered lens-shaped cuts along scanlines, thick near the light side (top) and fading downwards."""
        x0, y0, x1, y1 = K.bbox(q); h = (y1 - y0) or 1; s = ""
        y = y0 + 4
        while y < y1:
            t = (y - y0) / h
            if (top and t < 0.62) or (not top and t > 0.7):
                w = (wmax * (1 - t / 0.62) if top else wmax * (t - 0.7) / 0.3) + 0.8
                for a, b in scan(q, y):
                    x = a + 4
                    while x < b - 6:
                        L = min(r.uniform(14, 40), b - 4 - x)
                        if L > 6:
                            m = x + L / 2
                            s += path(f"M{x:.1f} {y:.1f}Q{m:.1f} {y - w:.1f} {x + L:.1f} {y + r.uniform(-1, 1):.1f}"
                                      f"Q{m:.1f} {y + w * 0.4:.1f} {x:.1f} {y:.1f}Z", color)
                        x += L + r.uniform(3, 8)
            y += r.uniform(6, 8.5)
        return s

    def render(l):
        r = rng(sp, "woodcut", l.part, l.idx)
        if is_pupil(l): return path(K.d_poly(l.polys()[0]), WINK)
        if l.kind in ("base", "limb"):
            L, s = K.lum(l.fill), ""
            for p in l.polys():
                q = jitter(K.resample(p, 5), r, 0.9); d = K.d_poly(q)
                if area(p) < 120: s += path(d, PAPER if L > 0.6 else WINK, WINK, 1.6)
                elif L < 0.33: s += path(d, WINK)
                elif L > 0.68: s += path(d, PAPER, WINK, 3.2) + gouges(q, r, False, WINK, 2.2)
                else: s += path(d, WINK) + gouges(q, r, True, PAPER, 3.4)
            return s
        if l.kind == "tone" and l.op >= 0.25:
            return "".join(path(K.d_poly(jitter(K.resample(p, 5), r, 0.8)), WINK) for p in l.polys())
        if l.kind == "line" and l.op >= 0.3:
            return "".join(path(K.d_poly(p, c), stroke=WINK, w=2.2) for p, c in l.shapes if len(p) > 1)

    return render, None, ""


# ------------------------------------------------------------------ 7. stained glass
def glass(sp):
    LEAD = OL

    def jewel(col, r):
        h, s, v = colorsys.rgb_to_hsv(*hexrgb(col))
        h = (h + r.uniform(-0.06, 0.06)) % 1
        s = min(1, max(s, 0.55) + r.uniform(0, 0.3)); v = min(1, max(v, 0.6) + r.uniform(0, 0.25))
        return K.hexc([c * 255 for c in colorsys.hsv_to_rgb(h, s, v)])

    def panes(p, r):
        n = max(3, min(9, int(area(p) / 3500)))
        x0, y0, x1, y1 = K.bbox(p); seeds = []
        for _ in range(400):
            q = (r.uniform(x0, x1), r.uniform(y0, y1))
            if K.inside(q, p) and all(math.dist(q, s) > 18 for s in seeds): seeds.append(q)
            if len(seeds) == n: break
        out = []
        for s in seeds:
            cell = p
            for o in seeds:
                if o is s: continue
                a, b = o[0] - s[0], o[1] - s[1]
                cell = clip(cell, a, b, (o[0] ** 2 + o[1] ** 2 - s[0] ** 2 - s[1] ** 2) / 2)
                if len(cell) < 3: break
            if len(cell) >= 3 and area(cell) > 30: out.append(cell)
        return out or [p]

    def render(l):
        r = rng(sp, "glass", l.part, l.idx)
        if is_pupil(l): return path(K.d_poly(l.polys()[0]), LEAD)
        if l.kind in ("base", "limb"):
            s = ""
            for p in l.polys():
                if area(p) < 150: s += path(K.d_poly(p), jewel(l.fill, r), LEAD, 1.8); continue
                for c in panes(p, r): s += path(K.d_poly(c), jewel(l.fill, r), LEAD, 3)
                s += path(K.d_poly(p), stroke=LEAD, w=5.5)
            return s
        if l.kind == "tone" and l.op >= 0.25:
            return "".join(path(K.d_poly(p), stroke=LEAD, w=2.6) for p in l.polys() if area(p) < 3000)
        if l.kind == "line" and l.op >= 0.3:
            return "".join(path(K.d_poly(p, c), stroke=LEAD, w=2.2) for p, c in l.shapes if len(p) > 1)

    return render, None, ""


# ------------------------------------------------------------------ 8. stippled paleo plate
def stipple(sp):
    PLATE, DOT, R = "#F4ECD8", "#2E2620", 2.4

    def dots(p, r, dens, edge):
        """Dart throwing with a minimum spacing (blue-noise stipple), denser towards the lower edge."""
        x0, y0, x1, y1 = K.bbox(p); h = (y1 - y0) or 1
        grid, out = {}, []

        def ok(q):
            gx, gy = int(q[0] // R), int(q[1] // R)
            return all(math.dist(q, o) >= R for i in (-1, 0, 1) for j in (-1, 0, 1) for o in grid.get((gx + i, gy + j), ()))

        def add(q):
            grid.setdefault((int(q[0] // R), int(q[1] // R)), []).append(q); out.append(q)

        if edge:
            for q in K.resample(p, 3.2):
                if r.random() < 0.85 and ok(q): add(q)
        for _ in range(int(area(p) * 0.08)):
            q = (r.uniform(x0, x1), r.uniform(y0, y1))
            if r.random() < dens * (0.45 + 1.1 * (q[1] - y0) / h) and K.inside(q, p) and ok(q): add(q)
        return "".join(f"M{x:.1f} {y:.1f}h0" for x, y in out)

    def dotpath(d):
        return f'<path d="{d}" fill="none" stroke="{DOT}" stroke-width="{R * 0.9:.1f}" stroke-linecap="round"/>' if d else ""

    def render(l):
        r = rng(sp, "stipple", l.part, l.idx)
        if is_pupil(l): return path(K.d_poly(l.polys()[0]), DOT)
        if l.kind in ("base", "limb"):
            t = 0.12 + 0.7 * (1 - K.lum(l.fill))
            return "".join(path(K.d_poly(p), PLATE) + dotpath(dots(p, r, t, True)) for p in l.polys())
        if l.kind == "tone" and l.op >= 0.2:
            return "".join(dotpath(dots(p, r, min(1, l.op * 1.6), False)) for p in l.polys())
        if l.kind == "line" and l.op >= 0.3:
            return dotpath("".join(f"M{x:.1f} {y:.1f}h0" for p, c in l.shapes if len(p) > 1 for x, y in K.resample(p, 3, c)))

    return render, None, ""


# ------------------------------------------------------------------ 9. children's crayon
def crayon(sp):
    def colour(c):
        L = K.lum(c)
        return "#FFFFFF" if L > 0.85 else "#FFC93C" if L > 0.66 else "#8E44D6" if L > 0.3 else "#3E2C9C"

    def rough(p, r, col, w=2.4, closed=True):
        n = max(8, min(36, int(K.perimeter(p, closed) / 22)))
        q = K.resample(p, K.perimeter(p, closed) / n, closed)
        s = ""
        for amt in (1.6, 0.8):                      # rough.js: two passes, the second with half the jitter
            j = jitter(q, r, amt)
            if closed: j = j + [j[0], (j[1][0] + r.uniform(-3, 3), j[1][1] + r.uniform(-3, 3))]  # overshoot
            s += path(K.d_smooth(j, False), stroke=col, w=w)
        return s

    def scribble(p, r, col):
        c = K.centroid(p); q = rot(p, -30, c)
        x0, y0, x1, y1 = K.bbox(q); y, pts, flip = y0 + 2.5, [], False
        while y < y1:
            for a, b in scan(q, y):
                if r.random() < 0.12: continue      # paper gaps
                seg = [(a - 1.5, y + r.uniform(-1, 1)), (b + 1.5, y + r.uniform(-1, 1))]
                pts += seg[::-1] if flip else seg; flip = not flip
            y += r.uniform(4.5, 6.5)
        return path(K.d_poly(rot(pts, 30, c), False), stroke=col, w=3.6) if len(pts) > 1 else ""

    def render(l):
        r = rng(sp, "crayon", l.part, l.idx)
        if is_pupil(l): return path(K.d_poly(l.polys()[0]), OL)
        if l.kind in ("base", "limb"):
            col = colour(l.fill); line = K.mix(col if col != "#FFFFFF" else "#888888", OL, 0.55)
            return "".join((path(K.d_poly(p), col) if area(p) < 100 else scribble(p, r, col)) + rough(p, r, line)
                           for p in l.polys())
        if l.kind == "tone" and l.op >= 0.25:
            return "".join(scribble(p, r, "#2F9E55") for p in l.polys() if area(p) < 3000)
        if l.kind == "line" and l.op >= 0.4:
            return "".join(rough(p, r, OL, 2.2, c) for p, c in l.shapes if len(p) > 1)

    def after(gid, leaves, pivot):
        eye = next((l for l in leaves if is_pupil(l)), None)
        if gid != "head" or not eye: return ""
        (x, y), _, _, _ = K.moments(eye.polys()[0]); r = rng(sp, "crayon", "face")
        e2 = K.ellipse_pts(x - 13, y + 1, 6.5, 7)
        return (path(K.d_poly(e2), "#FFFFFF") + rough(e2, r, OL, 1.8) + f'<circle cx="{x - 12}" cy="{y + 2}" r="2.6" fill="{OL}"/>'
                + path(f"M{x - 4} {y + 16} Q{x + 16} {y + 28} {x + 36} {y + 14}", stroke=OL, w=2.4))

    return render, after, ""


# ------------------------------------------------------------------ 10. Bauhaus geometric
def bauhaus(sp):
    RED, BLUE, YEL = "#D7322B", "#1F4FA3", "#F2C230"
    COL = {"body": RED, "head": RED, "jaw": YEL, "tail": BLUE, "neck": BLUE, "plates": YEL,
           "leg-near": BLUE, "foreleg-near": BLUE, "leg-far": INK, "foreleg-far": INK, "arm-near": INK, "arm-far": INK}
    blend = ' style="mix-blend-mode:multiply"'
    seen = set()

    def triangle(p, col):
        """Tapered wedge along the long axis, wide end at the thicker side."""
        (cx, cy), a, b, ang = K.moments(p)
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        proj = [((x - cx) * u[0] + (y - cy) * u[1], (x - cx) * -u[1] + (y - cy) * u[0]) for x, y in p]
        spread = lambda sg: max([abs(w) for t, w in proj if t * sg > 0.6 * a] or [0])
        sg = 1 if spread(1) < spread(-1) else -1
        tip, base, w = (cx + sg * a * u[0], cy + sg * a * u[1]), (cx - sg * a * u[0], cy - sg * a * u[1]), b * 1.6
        return path(K.d_poly([tip, (base[0] - u[1] * w, base[1] + u[0] * w), (base[0] + u[1] * w, base[1] - u[0] * w)]), col, extra=blend)

    def fit(p, col):
        """Circle for round shapes, otherwise a bar with its angle snapped to 45 degrees."""
        (cx, cy), a, b, ang = K.moments(p)
        if a < 1.6 * b: return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{math.sqrt(a * b):.1f}" fill="{col}"{blend}/>'
        ang = round(ang / 45) * 45
        return (f'<rect x="{cx - a:.1f}" y="{cy - b * 0.9:.1f}" width="{2 * a:.1f}" height="{1.8 * b:.1f}" '
                f'transform="rotate({ang} {cx:.1f} {cy:.1f})" fill="{col}"{blend}/>')

    def main(p, part, col):
        x0, y0, x1, y1 = K.bbox(p)
        if part in ("tail", "neck"): return triangle(p, col)
        if part == "body":                    # dome, flat side on the belly line
            rx, ry = (x1 - x0) / 2, (y1 - y0)
            return path(f"M{x0:.1f} {y1:.1f}A{rx:.1f} {ry:.1f} 0 0 1 {x1:.1f} {y1:.1f}Z", col, extra=blend)
        if part in ("head", "jaw"):           # boxes keep the boxy skull
            return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{blend}/>'
        return fit(p, col)

    def render(l):
        if is_pupil(l):
            (x, y), _, _, _ = K.moments(l.polys()[0]); return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{INK}"/>'
        if l.kind not in ("base", "limb"): return ""
        L, s = K.lum(l.fill), ""
        for p in l.polys():
            if area(p) < 150:
                if L < 0.5: s += fit(p, INK)            # claws; teeth are dropped
                continue
            if l.part not in seen and l.part != "root":
                seen.add(l.part); s += main(p, l.part, COL.get(l.part, RED)); continue
            if L > 0.66 and area(p) > 1500: continue     # belly panels: the primitives already carry the mass
            s += fit(p, YEL if L > 0.66 else COL.get(l.part, RED))
        return s

    return render, None, ""


# ------------------------------------------------------------------ 11. big-head explainer (matches src/char_paleontologist.py)
def explainer(sp):
    src = (ROOT / "svg" / f"{sp}-animated.svg").read_text(encoding="utf-8")
    c = re.search(r'class="([\w]+)-eyelid"', src)[1]
    eyes = [(float(x) - 0.4, float(y), 2 * float(r)) for x, y, r in re.findall(rf'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="{PUPIL}"', src)]
    found, skin = {}, {}

    def eye_of(polys):
        """the eye whose ring, iris, pupil, glint or lid these shapes are"""
        for ex, ey, r in eyes:
            if polys and all(math.hypot(*(a - b for a, b in zip(K.centroid(p), (ex, ey)))) < r + 3
                             and max(K.bbox(p)[2] - K.bbox(p)[0], K.bbox(p)[3] - K.bbox(p)[1]) < 2 * r + 10 for p in polys):
                return ex, ey, r

    def soft(p, closed=True):
        return K.d_poly(K.chaikin(K.resample(p, 5, closed), 2, closed), closed) if K.perimeter(p, closed) > 40 else K.d_poly(p, closed)

    def render(l):
        polys = l.polys()
        e = eye_of(polys)
        if e: found[l.part] = e; return ""
        if l.kind == "skip":   # keep the soft shade and light gradients, drop scale texture, AO and fades
            if any(k in l.fill for k in ("-shade)", "-light)")):
                return "".join(path(soft(p), l.fill, extra=f' opacity="{l.op * 0.8:.2f}"') for p in polys)
        if l.kind in ("base", "limb"):
            col = K.mix(l.fill, "#FFF6E8", 0.12)
            big = max((area(p) for p in polys), default=0)
            if big > skin.get(l.part, (0, ""))[0]: skin[l.part] = (big, col)   # lid colour: the part's largest fill
            return "".join(path(soft(p), col) for p in polys)
        if l.kind == "tone" and l.op >= 0.25:
            return "".join(path(soft(p), OL, extra=f' opacity="{l.op * 0.7:.2f}"') for p in polys)
        if l.kind == "line" and l.op >= 0.6 and K.lum(l.stroke) < 0.3:
            w = min(3.6, max(1.6, l.sw * 1.15))
            return "".join(path(soft(p, c), stroke=OL, w=w) for p, c in l.shapes if len(p) > 1)

    def after(gid, leaves, pivot):
        if gid not in found: return ""
        x, y, r = found[gid]; r = round(max(5.0, r * 1.1), 1); x, y = round(x, 1), round(y, 1)
        return (f'<g class="{c}-blush" opacity="0.45"><ellipse cx="{x + r * 0.4:.1f}" cy="{y + r * 2.2:.1f}" rx="{r * 1.3:.1f}" ry="{r * 0.8:.1f}" fill="{D.BLUSH}"/></g>'
                + D.face_eye(c, x, y, r, skin[gid][1]) + D.drop(round(x - r * 3, 1), round(y - r * 2.4, 1), r / 5, f"{c}-sweat"))

    return render, after, D.face_css(c)


def bighead(svg, k=1.3, fit=0.88):
    """enlarge the head through its pivot wrapper (it carries the jaw; multiplies any scale already there), then shrink
    the whole drawing about the ground line (y 514) so the bigger head stays inside the frame"""
    def f(m):
        return f'<g transform="translate({m[1]} {m[2]}) scale({float(m[3] or 1) * k:g})"><g id="head"'
    out, n = re.subn(r'<g transform="translate\((-?[\d.]+) (-?[\d.]+)\)(?: scale\(([\d.]+)\))?"><g id="head"', f, svg, count=1)
    assert n == 1, "head pivot wrapper not found"
    head, rest = out.split("</defs>\n", 1); body, tail = rest.rsplit("\n</svg>", 1)
    return f'{head}</defs>\n<g transform="translate(40 514) scale({fit}) translate(0 -514)">{body}</g>\n</svg>{tail}'


explainer.post = bighead


# ------------------------------------------------------------------ registry, backdrops, gallery
# key: (label, signature trait, builder, tile CSS background, backdrop svg)
STYLES = {
    "blueprint": ("Blueprint", "light construction lines on drafting blue", blueprint,
                  "#0E3A6E", "grid"),
    "neon": ("Neon sign", "glowing tubes, no fills", neon, "#120C24", "bricks"),
    "pixel": ("Pixel art", "stair-step silhouette on a cell grid", pixel, "#8FD3FF", "pixelground"),
    "benday": ("Ben-Day pop art", "dot lattice under a heavy ink line", benday, "#FFE45C", "burst"),
    "lowpoly": ("Low-poly", "lit triangles, no lines", lowpoly, "#3E5868", ""),
    "woodcut": ("Woodcut", "half solid ink, white chisel cuts", woodcut, "#EFE2C6", ""),
    "glass": ("Stained glass", "jewel panes in a lead network", glass, "#E6EEF2", "rays"),
    "stipple": ("Stippled paleo plate", "dot density, no outline, scientific plate", stipple, "#F4ECD8", "plate"),
    "crayon": ("Children's crayon", "wobbly wax lines, scribble fill", crayon, "#FFFFFF", "garden"),
    "bauhaus": ("Bauhaus", "circles, bars and triangles in primaries", bauhaus, "#F3EEE3", ""),
    "explainer": ("Big-head explainer", "big round head, closed happy eyes, soft flat fills", explainer, "#E9E1CF", ""),
}


def figure_span(src):
    """Left and right x of the drawing in viewBox units (root wrapper transform applied)."""
    m = re.search(r'<g transform="translate\(([\d.]+) ([\d.]+)\) scale\(([\d.]+)\) translate\((-?[\d.]+) (-?[\d.]+)\)">', src)
    a, s, c = (float(m[1]), float(m[3]), -float(m[4])) if m else (0, 1, 0)
    xs = []
    K.restyle_svg(src, lambda l: xs.extend(x for p in l.polys() for x, _ in p) if l.kind == "base" and l.part != "root" else None)
    assert xs, "no filled parts to measure"
    return a + s * (min(xs) - c), a + s * (max(xs) - c)


def backdrop(kind, sp, W, H, span):
    if kind == "grid":
        x0, x1 = span; y = H - 22
        return (f'<defs><pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#2F62A0"/></pattern></defs>'
                f'<rect width="{W}" height="{H}" fill="url(#g)"/><path d="M{x0} {y}H{x1}M{x0} {y - 8}v16M{x1} {y - 8}v16" stroke="#9CC4EC" stroke-width="1.2"/>'
                f'<text x="{(x0 + x1) / 2}" y="{y - 6}" fill="#9CC4EC" font-size="14" text-anchor="middle" font-family="Public Sans">{LENGTH_M[sp]} m</text>')
    if kind == "bricks":
        return "".join(f'<rect x="{x + (y // 34 % 2) * 40}" y="{y}" width="76" height="30" fill="#1B1233"/>'
                       for y in range(0, H, 34) for x in range(-40, W, 80))
    if kind == "pixelground":
        return "".join(f'<rect x="{x}" y="{H - 60 - (x // 60 % 2) * 6}" width="60" height="80" fill="#6AB04C"/>' for x in range(0, W, 60))
    if kind == "burst":
        cx, cy = W * 0.62, H * 0.45
        return "".join(path(f"M{cx} {cy}L{cx + 900 * math.cos(math.radians(a)):.0f} {cy + 900 * math.sin(math.radians(a)):.0f}"
                            f"L{cx + 900 * math.cos(math.radians(a + 7)):.0f} {cy + 900 * math.sin(math.radians(a + 7)):.0f}Z", "#FFD42A")
                       for a in range(0, 360, 14))
    if kind == "rays":
        return "".join(path(f"M{W / 2} -40L{W / 2 + (k - 4) * 160} {H}L{W / 2 + (k - 3.6) * 160} {H}Z", "#F7FAFB") for k in range(9))
    if kind == "plate":
        x0, x1 = span; m = round((x1 - x0) / LENGTH_M[sp]); y = H - 30
        return (f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none" stroke="#2E2620" stroke-width="2"/>'
                f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="none" stroke="#2E2620" stroke-width="0.8"/>'
                f'<text x="34" y="50" fill="#2E2620" font-size="18" font-family="Georgia, serif" font-style="italic">Fig. 1. {NAMES[sp]}</text>'
                f'<path d="M{W - 60 - m} {y}h{m}" stroke="#2E2620" stroke-width="5"/>'
                f'<text x="{W - 60 - m / 2}" y="{y - 10}" fill="#2E2620" font-size="14" font-family="Georgia, serif" text-anchor="middle">1 m</text>')
    if kind == "garden":
        grass = "".join(f"L{x + 9} {H - 40 - (x * 7 % 13)}L{x + 18} {H - 30}" for x in range(-20, W, 18))
        return (f'<circle cx="{W - 70}" cy="70" r="38" fill="#FFD23F"/>'
                + "".join(path(f"M{W - 70 + 48 * math.cos(math.radians(a)):.0f} {70 + 48 * math.sin(math.radians(a)):.0f}"
                               f"L{W - 70 + 66 * math.cos(math.radians(a)):.0f} {70 + 66 * math.sin(math.radians(a)):.0f}", stroke="#FFB400", w=4)
                          for a in range(0, 360, 30))
                + path(f"M-20 {H}V{H - 30}{grass}V{H}Z", "#53C15A"))
    return ""


PAGE_CSS = """body{margin:0;padding:40px 56px;background:#3E3E40;color:#ECE6E8;font-family:'Public Sans',system-ui,sans-serif}
h1{margin:0 0 6px;font:900 56px/1 'Big Shoulders Display',sans-serif}p{margin:0 0 18px;color:#B9B3B6;max-width:70ch}
nav{display:flex;gap:8px;margin-bottom:24px}button{font:600 14px 'Public Sans',sans-serif;padding:6px 14px;border-radius:4px;border:1px solid #8A8487;background:none;color:inherit;cursor:pointer}
button[aria-pressed=true]{background:#ECE6E8;color:#3E3E40}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(var(--w,440px),1fr));gap:24px}
figure{margin:0}.tile{position:relative;border-radius:6px;overflow:hidden}
.tile svg,.tile img{position:absolute;inset:0;width:100%;height:100%}
figcaption{margin-top:8px;font-size:14px;color:#B9B3B6}figcaption b{color:#ECE6E8;display:block;font-size:16px}
body.thumbs{--w:110px}body.thumbs figcaption{font-size:11px}body.thumbs figcaption b{font-size:12px}body.grey main{filter:grayscale(1)}
@media (max-width:600px){body{padding:24px 16px}main{grid-template-columns:1fr}}
"""


def gallery(sp, W, H, span):
    tiles = "\n".join(
        f'<figure><div class="tile" style="background:{bg};aspect-ratio:{W}/{H}"><svg viewBox="0 0 {W} {H}" aria-hidden="true">{backdrop(kind, sp, W, H, span)}</svg>'
        f'<img src="{sp}-{n}.svg" alt="{label} {NAMES[sp]}"></div><figcaption><b>{i}. {label}</b> {trait}</figcaption></figure>'
        for i, (n, (label, trait, _, bg, kind)) in enumerate(STYLES.items(), 1))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NAMES[sp]}: {len(STYLES)} styles</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@900&amp;family=Public+Sans:wght@400;600&amp;display=swap">
<style>{PAGE_CSS}</style></head><body>
<h1>One {NAMES[sp].split()[0]}, {len(STYLES)} styles</h1>
<p>Each version changes how the drawing is built: line, edge, texture and shape. Groups, pivots and idle motion are the same as svg/{sp}-animated.svg. The thumbnail and greyscale views check that every style can still be told apart.</p>
<nav><button data-c="thumbs" aria-pressed="false">Thumbnails</button><button data-c="grey" aria-pressed="false">Greyscale</button></nav>
<main>
{tiles}
</main>
<script>
const set=(c,on)=>{{document.body.classList.toggle(c,on);document.querySelector(`[data-c=${{c}}]`).setAttribute('aria-pressed',on)}};
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>set(b.dataset.c,!document.body.classList.contains(b.dataset.c)));
location.hash.slice(1).split(',').forEach(c=>c&&set(c,true));  // e.g. #thumbs,grey
</script></body></html>
"""


def species_gallery(name, rows):
    """One style across species; rows are (species, width, height)."""
    label, trait, _, bg, _ = STYLES[name]
    tiles = "\n".join(f'<figure><div class="tile" style="background:{bg};aspect-ratio:{W}/{H}"><img src="{sp}-{name}.svg" alt="{label} {NAMES[sp]}"></div>'
                      f'<figcaption><b><i>{NAMES[sp]}</i></b> about {LENGTH_M[sp]} m long</figcaption></figure>' for sp, W, H in rows)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{label}: {len(rows)} species</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@900&amp;family=Public+Sans:wght@400;600&amp;display=swap">
<style>{PAGE_CSS}</style></head><body>
<h1>{label}: {len(rows)} dinosaurs</h1>
<p>{trait[0].upper() + trait[1:]}. Each one is built from its species drawing in svg/, with the same groups, pivots and idle motion.</p>
<main>
{tiles}
</main></body></html>
"""


def main(args):
    names = [a for a in args if a in STYLES] or list(STYLES)
    species = [a for a in args if a not in STYLES] or ["trex"]
    bad = [a for a in species if a not in NAMES]
    if bad: sys.exit(f"unknown style or species: {', '.join(bad)} (styles: {', '.join(STYLES)}; species: {', '.join(NAMES)})")
    OUT.mkdir(exist_ok=True)
    rows = []
    for sp in species:
        src = (ROOT / "svg" / f"{sp}-animated.svg").read_text(encoding="utf-8")
        W, H = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', src).groups())
        ids = set(re.findall(r'<g id="([\w-]+)"', src)); rows.append((sp, W, H))
        for name in names:
            label, _, build, _, _ = STYLES[name]
            render, after, defs = build(sp)
            out = K.restyle_svg(src, render, head_extra=defs, after=after)
            if hasattr(build, "post"): out = build.post(out)
            out = re.sub(r'aria-label="([^"]*)"', rf'aria-label="\1, {label} style"', out, count=1)
            assert set(re.findall(r'<g id="([\w-]+)"', out)) == ids, name   # rig kept
            assert "#000000" not in out.split("</defs>", 1)[1], name          # no pure black in the drawing
            (OUT / f"{sp}-{name}.svg").write_text(out, encoding="utf-8")
            print(f"  {sp}-{name}.svg {len(out) // 1024} KB")
        if len(names) == len(STYLES):
            (OUT / f"{sp}-styles.html").write_text(gallery(sp, W, H, figure_span(src)), encoding="utf-8")
            print(f"svg/styles/{sp}-styles.html")
    if len(species) > 1:
        for name in names:
            (OUT / f"{name}.html").write_text(species_gallery(name, rows), encoding="utf-8")
            print(f"svg/styles/{name}.html")


if __name__ == "__main__":
    main(sys.argv[1:])
