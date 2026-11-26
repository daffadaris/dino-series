import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Stegosaurus stenops for the dinosaur series (RESEARCH_GUIDE.md). Building SPEC has no side effects; run as a script
to write the SVG and GSAP page.

Built skeleton first, in metres, at 6.5 m, the adult S. stenops length (Wikipedia; the NHM's 9 m is for the genus).
Proportions from "Sophie" (NHMUK PV R36730, Maidment, Brassey and Barrett 2015, PLOS ONE), a 5.5-6 m young adult with
a 0.87 m femur, scaled up: hip socket about 1.85 m, shoulder joint about 1.2 m (forelimb about 65% of the hind limb),
so the back slopes up to high hips; the head stays below about 1 m (Wikipedia). 19 dermal plates (Sophie: 18 found,
19 estimated) in two staggered rows, largest over the hips and tail base, smaller toward neck and tail, set in the
skin; four tail spikes in two pairs, angled steeply up, back and out (posterodorsolateral, PLOS). Hind feet three
short hoofed toes; front feet five toes, the inner two with blunt hooves (the hand is not preserved in Sophie:
RECONSTRUCTED from other specimens). No throat ossicles (absent in Sophie). Plate colour is unknown: dark accents
are an artistic choice."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
import scenery
from dinokit import OL, D, CLAW, path, stroke, line, piv, dots

C = "stg"
LOOK = K.Look(C, skin="#6F7F5A", belly="#D9CCA6", accent="#5B4A3B")   # muted green, sand, dark plates: artistic
S = 130                                  # drawing units per metre
F = K.Frame(500, 514, S)                 # x 0 = hip socket, y 0 = ground
FAR = (0.14, 0.06)                       # three-quarter view: far-side limbs sit forward and higher

def part(pts, **kw): return K.rig_part(LOOK, pts, **kw)
def m(ps, off=(0, 0)): return F.pts([(x + off[0], y + off[1]) for x, y in ps])
def rot(ps, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in ps]
def margin(x, pts):
    """y of a profile line at x, from (x, y) points"""
    pts = sorted(pts)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]

# ------------------------------------------------------------------ skeleton (metres): joint centres
HIP, KNEE, ANKLE = (0, 1.85), (0.15, 1.0), (0.08, 0.28)
SHOULDER, ELBOW, WRIST = (1.75, 1.2), (1.82, 0.72), (1.82, 0.22)

# ------------------------------------------------------------------ hind limbs: thigh > shin > foot > three hoofed toes
THIGH = [(0.38, 2.0), (0.45, 1.55), (0.35, 1.15), (0.22, 0.95), (-0.05, 0.93), (-0.25, 1.2), (-0.33, 1.6), (-0.3, 2.0), (0.05, 2.1)]
SHIN = [(0.35, 1.1), (0.3, 0.6), (0.22, 0.28), (-0.05, 0.25), (-0.15, 0.5), (-0.12, 1.05), (0.12, 1.15)]
FOOT = [(-0.12, 0.36), (0.14, 0.36), (0.28, 0.2), (0.36, 0.08), (0.3, 0.0), (-0.14, 0.0), (-0.2, 0.14)]
HIND_TOES = [((0.16, 0.07), 0.18), ((0.2, 0.035), 0.22), ((0.24, 0.0), 0.25)]     # back to front: (base, length)

def toes(side, specs, far, o, kind="toe", hooved=None, h=0.075):
    """short toes pointing forward from their bases, each its own group; hooved: indices with a blunt hoof"""
    out = ""
    for i, ((bx, by), ln) in enumerate(specs):
        toe = [(bx, by + h), (bx + ln * 0.7, by + h * 0.92), (bx + ln, by + h * 0.4), (bx + ln * 0.96, by), (bx, by)]
        hoof = [(bx + ln * 0.62, by + h * 0.95), (bx + ln * 0.92, by + h * 0.8), (bx + ln * 1.08, by + h * 0.3), (bx + ln * 1.04, by), (bx + ln * 0.62, by)]
        cap = path(K.smooth(m(hoof, o))[0], CLAW, 0.85 if far else None) if hooved is None or i in hooved else ""
        out += piv(f"{kind}-{side}-{len(specs) - i}", f"{C}-{kind}", *F(bx + o[0], by + o[1]), part(m(toe, o), skip=(4,), far=far, tex=False) + cap)
    return out

def hind_leg(side):
    far = side == "far"; o = FAR if far else (0, 0)
    foot = piv(f"foot-{side}", f"{C}-foot", *F(ANKLE[0] + o[0], ANKLE[1] + o[1]),
               part(m(FOOT, o), far=far, tex=False) + toes(side, HIND_TOES, far, o, h=0.085))
    shin = piv(f"shin-{side}", f"{C}-shin", *F(KNEE[0] + o[0], KNEE[1] + o[1]), foot + part(m(SHIN, o), far=far))
    return piv(f"leg-{side}", f"{C}-leg", *F(HIP[0] + o[0], HIP[1] + o[1]), shin + part(m(THIGH, o), skip=(7, 8), seam=(0, 6), far=far, seam_op=0.3))

# ------------------------------------------------------------------ forelimbs: upper arm > forearm > hand (five toes, inner two hoofed)
UPPER_ARM = [(1.5, 1.5), (2.0, 1.5), (2.05, 1.1), (1.95, 0.75), (1.8, 0.68), (1.62, 0.78), (1.52, 1.15)]
FOREARM = [(1.98, 0.78), (1.95, 0.4), (1.92, 0.22), (1.7, 0.2), (1.68, 0.42), (1.66, 0.75), (1.82, 0.85)]
HAND = [(1.68, 0.28), (1.94, 0.28), (2.0, 0.14), (2.02, 0.04), (1.98, 0.0), (1.65, 0.0), (1.66, 0.14)]
FRONT_TOES = [((1.9, 0.07), 0.13), ((1.94, 0.035), 0.15), ((1.97, 0.0), 0.17)]   # back to front; the front two (inner digits) hoofed

def foreleg(side):
    far = side == "far"; o = FAR if far else (0, 0)
    digits = f'<g id="digits-{side}" class="{C}-digits">{toes(side, FRONT_TOES, far, o, kind="finger", hooved=(1, 2), h=0.09)}</g>'
    hand = piv(f"hand-{side}", f"{C}-hand", *F(WRIST[0] + o[0], WRIST[1] + o[1]), part(m(HAND, o), far=far, tex=False) + digits)
    forearm = piv(f"forearm-{side}", f"{C}-forearm", *F(ELBOW[0] + o[0], ELBOW[1] + o[1]), part(m(FOREARM, o), far=far) + hand)
    return piv(f"foreleg-{side}", f"{C}-foreleg", *F(SHOULDER[0] + o[0], SHOULDER[1] + o[1]), forearm + part(m(UPPER_ARM, o), skip=(0,), seam=(1, 6), far=far, seam_op=0.3))

# ------------------------------------------------------------------ plates: 19, staggered in two rows, set in the skin
# (number, x along the back in metres, height, row): largest (13) over the hips; odd numbers near row, even far row
PLATES = [(1, 2.78, 0.16), (2, 2.6, 0.2), (3, 2.4, 0.26), (4, 2.18, 0.34), (5, 1.95, 0.43), (6, 1.7, 0.52), (7, 1.45, 0.6),
          (8, 1.2, 0.68), (9, 0.95, 0.75), (10, 0.7, 0.81), (11, 0.45, 0.86), (12, 0.2, 0.9), (13, -0.05, 0.93),
          (14, -0.32, 0.88), (15, -0.62, 0.78), (16, -0.92, 0.65), (17, -1.22, 0.52), (18, -1.52, 0.4), (19, -1.8, 0.28)]

def plate(n, base, up, h):
    """broad plate standing on base (drawing units) along direction up (degrees from vertical, + leans back), height h (m)"""
    w = h * (0.78 if h > 0.4 else 0.9)
    shape = [(-w / 2, 0), (-w * 0.6, h * 0.38), (-w * 0.42, h * 0.8), (-w * 0.08, h), (w * 0.3, h * 0.78), (w * 0.5, h * 0.36), (w / 2, 0), (0, -0.12)]
    pts = [(base[0] + x * S, base[1] - y * S) for x, y in rot(shape, up)]
    fill, out = K.smooth(pts, skip=(6, 7))
    grooves = " ".join(f"M{K._f((base[0] + p[0] * S, base[1] - p[1] * S))} L{K._f((base[0] + q[0] * S, base[1] - q[1] * S))}"
                       for p, q in (rot([(t * w * 0.2, h * 0.08), (t * w * 0.38, h * 0.62)], up) for t in (-0.75, -0.25, 0.3, 0.65)))
    far = n % 2 == 0
    return piv(f"plate-{n}", f"{C}-plate", round(base[0], 1), round(base[1], 1),
               path(fill, LOOK.accent) + line(grooves, 0.22, 1.8) + path(fill, LOOK.url("shade"))
               + (path(fill, D, 0.28) if far else path(fill, "#FFE4C0", 0.12)) + stroke(out))

def on_spine(spine, x_m):
    """base point and lean for a plate standing on a neck or tail centreline at x (metres)"""
    tx_ = F(x_m, 0)[0]; s = min(range(0, int(spine.length) + 1, 2), key=lambda q: abs(spine.at(q)[0] - tx_))
    x, y, tx, ty, d = spine.at(s); nx, ny = -ty, tx
    if ny > 0: nx, ny = -nx, -ny
    return (x + nx * d * 0.4, y + ny * d * 0.4), math.degrees(math.atan2(-nx, -ny))

def plates_where(xs_ok, spine=None):
    out = ""
    for n, x, h in sorted(PLATES, key=lambda p: p[0] % 2 == 1):          # far row first, near row in front
        if not xs_ok(x): continue
        if spine: base, up = on_spine(spine, x)
        else:
            y0, y1 = margin(x - 0.05, BACK), margin(x + 0.05, BACK)
            base, up = F(x, (y0 + y1) / 2 - 0.08), math.degrees(math.atan2(y1 - y0, 0.1))
        out += plate(n, base, up + 6, h)
    return out

# ------------------------------------------------------------------ torso
BACK = [(-0.75, 1.98), (-0.6, 2.08), (-0.2, 2.25), (0.3, 2.28), (0.8, 2.18), (1.3, 1.98), (1.8, 1.72), (2.15, 1.62), (2.4, 1.6)]   # runs on into the neck top
BARREL = BACK[1:] + [(2.6, 1.3), (2.4, 1.01), (2.0, 0.8), (1.4, 0.68), (0.7, 0.72), (0.1, 0.9), (-0.35, 1.2), (-0.65, 1.5), (-0.8, 1.75)]
BELLY = [(2.4, 1.01), (2.0, 0.8), (1.4, 0.68), (0.7, 0.72), (0.1, 0.9), (0.1, 1.15), (0.7, 0.98), (1.4, 0.95), (2.0, 1.05), (2.4, 1.2), (2.62, 1.2), (2.6, 1.08)]
CHEST = [(1.3, 1.98), (1.8, 1.72), (2.15, 1.62), (2.4, 1.6), (2.6, 1.3), (2.4, 1.01), (2.0, 0.8), (1.5, 0.7), (1.2, 1.1), (1.15, 1.6)]
PELVIS = [(-0.6, 2.08), (-0.2, 2.25), (0.3, 2.28), (0.7, 2.2), (0.8, 1.6), (0.5, 0.78), (0.1, 0.9), (-0.35, 1.2), (-0.65, 1.5), (-0.8, 1.75)]
body_poly = m([(-0.5, 2.0), (0.8, 2.05), (2.2, 1.5), (2.2, 1.0), (1.0, 0.8), (-0.3, 1.3)])
BODY = piv("body", f"{C}-body", *F(0.9, 0.9), (
    f'<g id="plates" class="{C}-plates">' + plates_where(lambda x: -0.2 < x < 2.25) + "</g>"
    + f'<g id="abdomen" class="{C}-abdomen">' + part(m(BARREL), skip=(7, 8), belly=K.smooth(m(BELLY))[0],
                                                     layers=dots(body_poly, 60, 1.4, 2.4, 0.08, seed=17)) + "</g>"
    + f'<g id="pelvis" class="{C}-pelvis">' + part(m(PELVIS), seam=(3, 4), seam_op=0.1) + "</g>"
    + f'<g id="chest" class="{C}-chest">' + part(m(CHEST), skip=(3, 4), seam=(7, 8, 9), seam_op=0.1,
                                                  belly=K.smooth(m([(2.4, 1.01), (2.0, 0.8), (1.5, 0.7), (1.45, 0.95), (2.0, 1.05), (2.4, 1.2), (2.62, 1.2), (2.6, 1.08)]))[0]) + "</g>"))

# ------------------------------------------------------------------ tail: base, middle, tip; four spikes on the tip
TAIL_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in
                      [(0.2, 1.75, 0.95), (-0.6, 1.78, 0.75), (-1.4, 1.62, 0.5), (-2.2, 1.4, 0.32), (-2.9, 1.22, 0.2), (-3.25, 1.12, 0.08)]])

def spike(n, x_m, ln, lift, far):
    """tapering, slightly curved tail spike rising from the tail top at x, pointing back and up by lift degrees"""
    base, up = on_spine(TAIL_SPINE, x_m)
    ang = math.radians(180 - lift + (6 if far else 0))                    # backwards, raised
    dx, dy = math.cos(ang), -math.sin(ang)                                 # page direction (y down)
    nx, ny = -dy, dx; w = 0.045 * S; L = ln * S
    tip = (base[0] + dx * L, base[1] + dy * L)
    mid = (base[0] + dx * L * 0.55 - nx * w * 0.35, base[1] + dy * L * 0.55 - ny * w * 0.35)
    pts = [(base[0] + nx * w, base[1] + ny * w), mid, tip, (mid[0] - nx * w * 0.9, mid[1] - ny * w * 0.9), (base[0] - nx * w, base[1] - ny * w)]
    pts[1] = (mid[0] + nx * w * 0.55, mid[1] + ny * w * 0.55)
    fill, out = K.smooth(pts)
    return piv(f"spike-{n}", f"{C}-spike", round(base[0], 1), round(base[1], 1),
               path(fill, "#E6DCC2") + path(fill, LOOK.url("shade")) + (path(fill, D, 0.3) if far else "") + stroke(out))

SPIKES_FAR = spike(2, -2.5, 0.6, 54, True) + spike(4, -2.8, 0.55, 46, True)
SPIKES_NEAR = spike(1, -2.6, 0.62, 34, False) + spike(3, -2.9, 0.56, 26, False)
TAIL_IDS = ["tail", "tail-2", "tail-3"]
TAIL_CUTS = [0, 0.38, 0.7, 1.0]

def tail_under(k, s0, s1):
    L = TAIL_SPINE.length; a, b = TAIL_SPINE.at(s1)[0], TAIL_SPINE.at(s0)[0]
    lo, hi = (a - F.x0) / S, (b - F.x0) / S
    return plates_where(lambda x: lo < x <= hi and x <= -0.2, TAIL_SPINE) + (SPIKES_FAR if k == 2 else "")

TAIL = K.segmented(LOOK, TAIL_SPINE, TAIL_CUTS, TAIL_IDS, 0.3 * S, [3, 3, 2], tip_cap=0.5, end=SPIKES_NEAR, under=tail_under)

# ------------------------------------------------------------------ head: very small, long and low; toothless beak at the front
HF = K.Frame(0, 0, S)
SKULL = [(-0.03, 0.05), (0.03, 0.13), (0.12, 0.16), (0.22, 0.15), (0.32, 0.11), (0.42, 0.06), (0.47, 0.0), (0.45, -0.04),
         (0.35, -0.05), (0.2, -0.05), (0.08, -0.06), (-0.02, -0.04)]
BEAK = [(0.36, 0.07), (0.43, 0.05), (0.475, 0.0), (0.455, -0.04), (0.38, -0.05), (0.36, 0.0)]
LOWER_JAW = [(0.0, -0.03), (0.2, -0.045), (0.38, -0.045), (0.45, -0.035), (0.44, -0.075), (0.35, -0.09), (0.2, -0.095), (0.05, -0.085), (-0.02, -0.06)]
LOWER_BEAK = [(0.37, -0.045), (0.45, -0.035), (0.44, -0.075), (0.38, -0.08)]
JAW = piv("jaw", f"{C}-jaw", *HF(0.06, -0.05), part(HF.pts(LOWER_JAW), tex=False) + path(K.smooth(HF.pts(LOWER_BEAK))[0], CLAW, 0.85))
UPPER = f'<g id="upper-jaw" class="{C}-upper-jaw">' + path(K.smooth(HF.pts(BEAK))[0], CLAW, 0.85) + "</g>"
ex, ey = HF(0.13, 0.075)
SKULL_G = (f'<g id="skull" class="{C}-skull">' + part(HF.pts(SKULL), light=True, tex=False)
           + f'<ellipse cx="{HF(0.4, 0.04)[0]}" cy="{HF(0.4, 0.04)[1]}" rx="3" ry="2" fill="{OL}" opacity="0.6"></ellipse>'
           + K.eye(ex, ey, f"{C}-eyelid", r=3.6) + "</g>")
HEAD_ANGLE = 18

# ------------------------------------------------------------------ neck: short, sloping down to the low head; small plates ride on it
NECK_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in [(2.0, 1.25, 0.8), (2.45, 1.31, 0.56), (2.8, 1.22, 0.36), (3.0, 1.1, 0.26)]])   # slight arch, thinning so the head reads
hx, hy, *_ = NECK_SPINE.at(NECK_SPINE.length)
HEAD = (f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({HEAD_ANGLE})">' + piv("head", f"{C}-head", 0, 0, SKULL_G + JAW + UPPER) + "</g>")
NECK = K.segmented(LOOK, NECK_SPINE, [0, 1.0], ["neck"], 0, [2], tip_cap=0.1, end=HEAD,
                   under=lambda k, s0, s1: plates_where(lambda x: x >= 2.25, NECK_SPINE))

# ------------------------------------------------------------------ hidden skeletal guide
def _guide():
    bones = f"M{K._f(F(*HIP))} L{K._f(F(*KNEE))} L{K._f(F(*ANKLE))} M{K._f(F(*SHOULDER))} L{K._f(F(*ELBOW))} L{K._f(F(*WRIST))}"
    spines = "".join('<path d="M' + " L".join(K._f(sp.at(sp.length * k / 20)[:2]) for k in range(21)) + '" fill="none" stroke="#3A7BD5" stroke-width="2"></path>'
                     for sp in (TAIL_SPINE, NECK_SPINE))
    joints = "".join(f'<circle cx="{F(*p)[0]}" cy="{F(*p)[1]}" r="4" fill="#E5484D"></circle>' for p in (HIP, KNEE, ANKLE, SHOULDER, ELBOW, WRIST))
    return (f'<g id="skeleton-guide" class="{C}-guide" display="none" pointer-events="none">'
            f'<path d="{bones}" fill="none" stroke="#3A7BD5" stroke-width="3"></path>{spines}{joints}</g>')

FRAG = piv("act", f"{C}-act", *F(0.9, 0), hind_leg("far") + foreleg("far") + TAIL + NECK + BODY + hind_leg("near") + foreleg("near") + _guide())

# ------------------------------------------------------------------ move: spiked tail swing (wind up, swipe, recover); no plate colour change
ACTION = {
    "tail": [(0, "rotate(0)"), (0.25, "rotate(6deg)"), (0.5, "rotate(-9deg)"), (0.7, "rotate(-7deg)"), (1, "rotate(0)")],
    "tail-2": [(0, "rotate(0)"), (0.25, "rotate(5deg)"), (0.52, "rotate(-11deg)"), (0.7, "rotate(-8deg)"), (1, "rotate(0)")],
    "tail-3": [(0, "rotate(0)"), (0.25, "rotate(4deg)"), (0.55, "rotate(-13deg)"), (0.72, "rotate(-9deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.3, "rotate(-5deg)"), (0.7, "rotate(-5deg)"), (1, "rotate(0)")],
    "act": [(0, "translateX(0)"), (0.25, "translateX(4px)"), (0.5, "translateX(-6px)"), (0.7, "translateX(-4px)"), (1, "translateX(0)")],
}
GSAP = """      .to(parts.tail, { rotation: 6, duration: 0.45, ease: 'power2.out' }, 0)
      .to(parts.tail_2, { rotation: 5, duration: 0.45, ease: 'power2.out' }, 0)
      .to(parts.tail_3, { rotation: 4, duration: 0.45, ease: 'power2.out' }, 0)
      .to(parts.act, { x: 4, duration: 0.45, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -5, duration: 0.5, ease: 'power2.out' }, 0.1)
      .to(parts.tail, { rotation: -9, duration: 0.35, ease: 'power3.in' }, 0.45)
      .to(parts.tail_2, { rotation: -11, duration: 0.38, ease: 'power3.in' }, 0.47)
      .to(parts.tail_3, { rotation: -13, duration: 0.4, ease: 'power3.in' }, 0.5)
      .to(parts.act, { x: -6, duration: 0.35, ease: 'power3.in' }, 0.45)
      .to([parts.tail, parts.tail_2, parts.tail_3, parts.head], { rotation: 0, duration: 0.6, ease: 'power2.inOut' }, 1.25)
      .to(parts.act, { x: 0, duration: 0.6, ease: 'power2.inOut' }, 1.25)"""

IDS = ["act", "body", "plates", "chest", "abdomen", "pelvis", "tail", "tail-2", "tail-3", "neck", "head", "skull", "upper-jaw", "jaw",
       "leg-near", "leg-far", "foreleg-near", "foreleg-far"]
MIDLINE = ([TAIL_SPINE.at(TAIL_SPINE.length * (1 - k / 10))[:2] for k in range(11)] + [F(1.0, 1.5)]
           + [NECK_SPINE.at(NECK_SPINE.length * k / 4)[:2] for k in range(5)]
           + [(hx + math.cos(math.radians(HEAD_ANGLE)) * 0.47 * S, hy + math.sin(math.radians(HEAD_ANGLE)) * 0.47 * S)])

SPEC = dict(
    code=C, slug="stegosaurus", board="Stegosaurus", name="Stegosaurus", short="Stegosaurus", look=LOOK,
    viewbox=(1000, 560), frag=FRAG, ids=IDS, action=ACTION, dur=2.0, gsap=GSAP,
    action_label="Make the Stegosaurus swing its tail", action_verb="swing its tail", page_bg="#D9D4C4",
    scene=scenery.set_morrison(), title="Stegosaurus", title_px=190, binomial="Stegosaurus stenops", subtitle="the narrow-faced roof lizard",
    paragraph="A plant eater with two staggered rows of tall bony plates down its back and a spiked tail for defence, carrying its small head about a metre off the ground.",
    facts=[("6.5 m", "adult length"), ("152–145", "million years ago"), ("4", "tail spikes")],
    footer="Fossils come from the Morrison Formation of Colorado, Wyoming and Utah, with more found in Portugal.",
    hint="Tap the Stegosaurus to swing its tail", skin_swatches=["#6F7F5A", "#5E7E7A", "#7A8450", "#8A6A3E"],
    dino_top=60, midline=MIDLINE, ground=F.g,
)

if __name__ == "__main__":
    K.write_all(SPEC)          # this rework round: svg/ and gsap/ only; poster and rig board follow later
    print("ok")
