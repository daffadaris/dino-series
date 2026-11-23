"""Geometry core for the style variants: read a species SVG, keep its groups, ids, classes, pivots and motion
CSS, and hand every leaf shape to a style renderer as sampled polygons with its resolved paint."""
import math, re, xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

NS = "{http://www.w3.org/2000/svg}"
PAINT = ("fill", "stroke", "stroke-width", "opacity", "stroke-linejoin", "stroke-linecap", "fill-opacity", "stroke-opacity")


# ------------------------------------------------------------------ path sampling
def _cubic(p0, p1, p2, p3, n):
    return [tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))
            for t in (i / n for i in range(1, n + 1))]


def _n(*pts):
    return max(2, int(sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) / 3))


def parse_path(d):
    """Subpaths of an SVG path as point lists sampled every ~3 px; returns [(points, closed)]."""
    toks = re.findall(r"[MmLlHhVvCcQqZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    out, pts, cur, start, cmd, i = [], [], (0.0, 0.0), (0.0, 0.0), None, 0
    num = lambda k: [float(x) for x in toks[i:i + k]]
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                if len(pts) > 1: out.append((pts, True))
                pts, cur = [start], start  # a drawing command may follow Z without M
                continue
        if cmd is None: raise ValueError("path data must start with a command")
        rel = cmd.islower(); c = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if c == "M":
            if len(pts) > 1: out.append((pts, False))
            x, y = num(2); i += 2; cur = start = (ox + x, oy + y); pts = [cur]
            cmd = "l" if rel else "L"
        elif c == "L":
            x, y = num(2); i += 2; cur = (ox + x, oy + y); pts.append(cur)
        elif c == "H":
            x, = num(1); i += 1; cur = ((ox if rel else 0) + x, cur[1]); pts.append(cur)
        elif c == "V":
            y, = num(1); i += 1; cur = (cur[0], (oy if rel else 0) + y); pts.append(cur)
        elif c == "C":
            v = num(6); i += 6
            p1, p2, p3 = [(ox + v[k], oy + v[k + 1]) for k in (0, 2, 4)]
            pts += _cubic(cur, p1, p2, p3, _n(cur, p1, p2, p3)); cur = p3
        elif c == "Q":
            v = num(4); i += 4
            q, p3 = (ox + v[0], oy + v[1]), (ox + v[2], oy + v[3])
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts += _cubic(cur, p1, p2, p3, _n(cur, p1, p2, p3)); cur = p3
        else:
            raise ValueError(f"unsupported path command {cmd!r}")
    if len(pts) > 1: out.append((pts, False))
    return out


def ellipse_pts(cx, cy, rx, ry):
    n = max(12, int(2 * math.pi * max(rx, ry) / 3))
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def shapes_of(el):
    """[(points, closed)] for a leaf element, in its own user space (its transform attribute not applied)."""
    tag, a = el.tag.replace(NS, ""), el.attrib
    f = lambda k, dflt=0: float(a.get(k, dflt))
    if tag == "path": return parse_path(a["d"])
    if tag == "circle": return [(ellipse_pts(f("cx"), f("cy"), f("r"), f("r")), True)]
    if tag == "ellipse": return [(ellipse_pts(f("cx"), f("cy"), f("rx"), f("ry")), True)]
    if tag in ("polyline", "polygon"):
        v = [float(x) for x in re.findall(r"-?\d*\.?\d+", a["points"])]
        return [(list(zip(v[::2], v[1::2])), tag == "polygon")]
    if tag == "rect":
        x, y, w, h = f("x"), f("y"), f("width"), f("height")
        return [([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True)]
    return []


# ------------------------------------------------------------------ polygon helpers
def area(p):
    return 0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1]))


def centroid(p):
    A = area(p)
    if abs(A) < 1e-6: return (sum(x for x, _ in p) / len(p), sum(y for _, y in p) / len(p))
    cx = sum((a[0] + b[0]) * (a[0] * b[1] - b[0] * a[1]) for a, b in zip(p, p[1:] + p[:1])) / (6 * A)
    cy = sum((a[1] + b[1]) * (a[0] * b[1] - b[0] * a[1]) for a, b in zip(p, p[1:] + p[:1])) / (6 * A)
    return cx, cy


def perimeter(p, closed=True):
    q = p + p[:1] if closed else p
    return sum(math.dist(a, b) for a, b in zip(q, q[1:]))


def resample(p, step, closed=True):
    """Points spaced `step` apart along the outline (at least 3 for closed shapes)."""
    q = p + p[:1] if closed else p
    L = perimeter(p, closed)
    n = max(3 if closed else 2, round(L / step))
    step = L / n if closed else L / max(1, n - 1)
    out, acc, k = [q[0]], 0.0, 1
    for a, b in zip(q, q[1:]):
        seg = math.dist(a, b)
        while seg > 0 and acc + seg >= k * step and len(out) < n:
            t = (k * step - acc) / seg
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)); k += 1
        acc += seg
    if not closed and math.dist(out[-1], q[-1]) > 1e-6: out.append(q[-1])
    return out


def chaikin(p, n=2, closed=True):
    for _ in range(n):
        q = p + p[:1] if closed else p
        r = [] if closed else [p[0]]
        for a, b in zip(q, q[1:]):
            r += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        p = r if closed else r + [p[-1]]
    return p


def inside(pt, p):
    x, y, c = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(p, p[1:] + p[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c


def bbox(p):
    xs, ys = [x for x, _ in p], [y for _, y in p]
    return min(xs), min(ys), max(xs), max(ys)


def moments(p):
    """Centre, semi-axes and angle (deg) of the ellipse with the filled region's second moments."""
    A = area(p)
    if abs(A) < 1e-6: return centroid(p), 1.0, 1.0, 0.0
    cx, cy = centroid(p); q = [(x - cx, y - cy) for x, y in p]
    e = [(a, b, a[0] * b[1] - b[0] * a[1]) for a, b in zip(q, q[1:] + q[:1])]
    sxx = sum((a[0] ** 2 + a[0] * b[0] + b[0] ** 2) * c for a, b, c in e) / (12 * A)
    syy = sum((a[1] ** 2 + a[1] * b[1] + b[1] ** 2) * c for a, b, c in e) / (12 * A)
    sxy = sum((a[0] * b[1] + 2 * a[0] * a[1] + 2 * b[0] * b[1] + b[0] * a[1]) * c for a, b, c in e) / (24 * A)
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    l1 = tr / 2 + math.sqrt(max(0, tr * tr / 4 - det)); l2 = tr - l1
    ang = 0.5 * math.degrees(math.atan2(2 * sxy, sxx - syy))
    return (cx, cy), 2 * math.sqrt(l1), 2 * math.sqrt(max(l2, 0.25)), ang  # filled ellipse: var = r^2/4


def d_poly(p, closed=True):
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p)
    return s + (" Z" if closed else "")


def d_smooth(p, closed=True):
    """Catmull-Rom spline through the points, as cubic Beziers."""
    n = len(p)
    if n < 3: return d_poly(p, closed)
    g = (lambda k: p[k % n]) if closed else (lambda k: p[min(max(k, 0), n - 1)])
    s = f"M{p[0][0]:.1f} {p[0][1]:.1f}"
    for k in range(n if closed else n - 1):
        p0, p1, p2, p3 = g(k - 1), g(k), g(k + 1), g(k + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return s + (" Z" if closed else "")


def thick_line(p, w):
    """Closed outline around an open polyline of width w (square joins; good enough for limb strokes)."""
    L, R = [], []
    for k, (x, y) in enumerate(p):
        a, b = p[max(k - 1, 0)], p[min(k + 1, len(p) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m * w / 2, dx / m * w / 2
        L.append((x + nx, y + ny)); R.append((x - nx, y - ny))
    return L + R[::-1]


# ------------------------------------------------------------------ colour helpers
def rgb(c):
    c = c.lstrip("#")
    if len(c) == 3: c = "".join(ch * 2 for ch in c)
    return tuple(int(c[k:k + 2], 16) for k in (0, 2, 4))


def hexc(t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in t)


def mix(a, b, t):
    return hexc([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def lum(c):
    r, g, b = rgb(c)
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255


def nearest(c, palette):
    return min(palette, key=lambda q: sum((x - y) ** 2 for x, y in zip(rgb(c), rgb(q))))


# ------------------------------------------------------------------ walker
class Leaf:
    """A shape with resolved paint. kind: base (opaque fill), tone (translucent overlay), line (stroke only),
    limb (thick coloured stroke), skip (gradient/pattern fill)."""
    def __init__(self, el, paint, part, idx):
        self.el, self.tag = el, el.tag.replace(NS, "")
        self.part, self.idx = part, idx  # nearest group id ("root" outside any) and order within it
        self.fill, self.stroke = paint.get("fill", "#000000"), paint.get("stroke", "none")
        self.sw = float(paint.get("stroke-width", 1)); self.op = paint["_op"]
        self.shapes = shapes_of(el)
        self.transform = el.get("transform")
        solid = self.fill not in ("none",) and not self.fill.startswith("url(")
        if self.fill.startswith("url("): self.kind = "skip"
        elif solid and self.op >= 0.95: self.kind = "base"
        elif solid: self.kind = "tone"
        elif self.stroke not in ("none",) and self.sw >= 6 and self.op >= 0.95:
            self.kind, self.fill = "limb", self.stroke  # the band becomes a filled outline
        elif self.stroke not in ("none",): self.kind = "line"
        else: self.kind = "skip"

    def polys(self):
        """Closed outlines (limb strokes become a closed band)."""
        if self.kind == "limb":
            return [thick_line(resample(p, 3, False), self.sw) for p, _ in self.shapes]
        return [p for p, closed in self.shapes if len(p) >= 3]


def restyle_svg(src, render, *, head_extra="", after=None):
    """Rebuild the SVG: groups kept (paint attrs dropped), leaves replaced by render(leaf) -> svg string.
    after(part_id, leaves, pivot) may return extra svg, drawn last inside that part in drawing coordinates."""
    ET.register_namespace("", NS[1:-1])
    root = ET.fromstring(src)
    assert "</defs>" in src, "species SVG needs a <defs> block"
    head = src[:src.index("</defs>")]
    out = []

    def walk(el, paint, part, bucket):
        tag = el.tag.replace(NS, "")
        if tag in ("defs", "style", "title"): return
        p = dict(paint)
        for k in PAINT:
            if k in el.attrib and k != "opacity": p[k] = el.get(k)
        p["_op"] = paint["_op"] * float(el.get("opacity", 1)) * float(el.get("fill-opacity", 1))
        if tag == "g":
            at = dict((k, v) for k, v in el.attrib.items() if k not in PAINT)
            assert not any(k.startswith("{") for k in at), at  # namespaced attrs would need prefix mapping
            out.append("<g" + "".join(f" {k}={quoteattr(v)}" for k, v in at.items()) + ">")
            gid = el.get("id")
            own = [] if gid else bucket
            for c in el: walk(c, p, gid or part, own)
            if gid and after:
                inner = next((c.get("transform", "") for c in el if c.tag == NS + "g"), "")
                m = re.fullmatch(r"translate\((-?[\d.]+) (-?[\d.]+)\)", inner)
                pivot = (-float(m[1]), -float(m[2])) if m else None
                extra = after(gid, own, pivot)
                if extra: out.append(f'<g transform="{inner}">{extra}</g>' if m else extra)
            out.append("</g>")
            return
        leaf = Leaf(el, p, part, len(bucket))
        bucket.append(leaf)
        s = render(leaf)
        if s:
            out.append(f'<g transform={quoteattr(leaf.transform)}>{s}</g>' if leaf.transform else s)

    for c in root:
        walk(c, {"_op": 1.0}, "root", [])
    return f"{head}{head_extra}</defs>\n{''.join(out)}\n</svg>\n"
