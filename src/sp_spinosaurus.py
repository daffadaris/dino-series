import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Spinosaurus aegyptiacus for the dinosaur series (RESEARCH_GUIDE.md). Building SPEC has no side effects; run as a
script to write the SVG and GSAP page.

Built skeleton first, in metres. A 14 m, 7.4 t biped standing with its weight over the hips (Sereno et al. 2022, via
Wikipedia and the NHM; the paper itself was not reachable). Skull 1.6 m (Hendrickx et al. 2016 favoured 1.6 m over
Dal Sasso et al.'s 1.75 m): long, low and narrow, an expanded tip with a notch behind it, nostrils set far back, a
small crest in front of the eyes (not the scimitar crest of S. mirabilis), straight conical teeth. S-curved neck.
Robust arms with three fingers and an enlarged first claw. Short hind legs, about a quarter of body length
(Wikipedia summary; UNVERIFIED), hip socket at about 2.5 m, below T. rex's (NHM); long, flat-clawed toes. A sail of
neural spines at least 1.65 m long, drawn about 1.6 m above the back and peaking over the rear of the trunk; its
soft-tissue outline is RECONSTRUCTED. A deep paddle tail from tall neural spines and long chevrons (Ibrahim et al.
2020), about 5.5 m outside the body. Posture and swimming ability are DEBATED; this is the land-biped stance."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
import scenery
from dinokit import OL, D, CLAW, IVORY, path, stroke, line, piv, dots

C = "spn"
LOOK = K.Look(C, skin="#4F6E70", belly="#D8C9A3", accent="#C59A62")   # deep teal, sand; sail accent is artistic
S = 64                                   # drawing units per metre
F = K.Frame(482, 514, S)                 # x 0 = hip socket, y 0 = ground
FAR = (0.3, 0.12)                        # three-quarter view: far-side limbs sit forward and higher

def part(pts, **kw): return K.rig_part(LOOK, pts, **kw)
def m(ps, off=(0, 0)): return F.pts([(x + off[0], y + off[1]) for x, y in ps])
def rot(ps, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in ps]
def shift(ps, o): return [(x + o[0], y + o[1]) for x, y in ps]

# ------------------------------------------------------------------ skeleton (metres): joint centres
HIP, KNEE, ANKLE = (0, 2.5), (0.4, 1.5), (-0.1, 0.66)
ARM_SHIFT = (-0.26, 0.04)             # the arm set sits under the shorter chest
SHOULDER, ELBOW, WRIST = [(x + ARM_SHIFT[0], y + ARM_SHIFT[1]) for x, y in [(3.15, 2.75), (3.38, 2.05), (3.88, 1.68)]]

# ------------------------------------------------------------------ hind limbs: thigh > shin > foot > toes (short legs, flat claws)
THIGH = [(0.7, 2.95), (0.85, 2.3), (0.65, 1.75), (0.45, 1.42), (0.12, 1.4), (-0.25, 1.75), (-0.5, 2.4), (-0.6, 2.95), (0.05, 3.15)]
SHIN = [(0.6, 1.6), (0.35, 1.0), (0.08, 0.66), (-0.2, 0.58), (-0.28, 0.75), (0.02, 1.2), (0.2, 1.68)]
FOOT = [(-0.3, 0.78), (0.0, 0.74), (0.32, 0.24), (0.82, 0.13), (0.9, 0.03), (0.18, 0.0), (0.0, 0.05), (-0.28, 0.58)]
TOES = [((0.84, 0.08), 0.17, 0.07), ((0.74, 0.15), 0.15, 0.06), ((0.62, 0.2), 0.12, 0.05)]   # digits III, II, IV: (base, length, height)

def hind_leg(side):
    far = side == "far"; o = FAR if far else (0, 0)
    toes = "".join(piv(f"toe-{side}-{i + 1}", f"{C}-toe", *F(b[0] + o[0], b[1] + o[1]),
                       path(K.smooth(m(K.claw(b, ln, h), o))[0], CLAW, 0.85 if far else None))
                   for i, (b, ln, h) in enumerate(TOES))
    foot = piv(f"foot-{side}", f"{C}-foot", *F(ANKLE[0] + o[0], ANKLE[1] + o[1]), part(m(FOOT, o), far=far, tex=False) + toes)
    shin = piv(f"shin-{side}", f"{C}-shin", *F(KNEE[0] + o[0], KNEE[1] + o[1]), foot + part(m(SHIN, o), far=far))
    return piv(f"leg-{side}", f"{C}-leg", *F(HIP[0] + o[0], HIP[1] + o[1]), shin + part(m(THIGH, o), skip=(7, 8), seam=(0, 6), far=far, seam_op=0.3))

# ------------------------------------------------------------------ arms: upper arm > forearm > hand > three fingers (digit I claw enlarged)
UPPER_ARM = [(2.85, 3.05), (3.45, 3.05), (3.6, 2.55), (3.5, 2.05), (3.32, 1.92), (3.15, 2.1), (2.95, 2.6)]
FOREARM = [(3.3, 2.2), (3.5, 2.18), (3.98, 1.8), (3.95, 1.62), (3.78, 1.6), (3.25, 1.98)]
PALM = [(3.78, 1.8), (4.02, 1.76), (4.1, 1.58), (3.98, 1.46), (3.8, 1.52)]
FINGERS = [((4.03, 1.62), -55, 0.16, 0.24, 0.09), ((4.06, 1.52), -70, 0.14, 0.16, 0.07), ((3.95, 1.48), -80, 0.12, 0.13, 0.06)]   # base, angle, finger, claw, claw height
UPPER_ARM, FOREARM, PALM = (shift(a, ARM_SHIFT) for a in (UPPER_ARM, FOREARM, PALM))
FINGERS = [(shift([b], ARM_SHIFT)[0], *rest) for b, *rest in FINGERS]

def finger(base, ang, flen, clen, ch):
    """finger capsule from its base along ang (degrees, negative = down), with a hooked claw at the end"""
    body = rot([(0, 0.035), (flen, 0.03), (flen + 0.02, 0), (flen, -0.03), (0, -0.035), (-0.02, 0)], ang)
    tip = rot([(flen, 0)], ang)[0]
    return shift(body, base), shift(rot(K.claw((0, 0), clen, ch), ang), (base[0] + tip[0], base[1] + tip[1]))

def arm(side):
    far = side == "far"; o = FAR if far else (0, 0)
    fingers = ""
    for i, spec in enumerate(FINGERS):
        fb, cl = finger(*spec)
        fingers += piv(f"finger-{side}-{i + 1}", f"{C}-finger", *F(spec[0][0] + o[0], spec[0][1] + o[1]),
                       part(m(fb, o), far=far, tex=False) + path(K.smooth(m(cl, o))[0], CLAW, 0.85 if far else None))
    hand = piv(f"hand-{side}", f"{C}-hand", *F(WRIST[0] + o[0], WRIST[1] + o[1]), fingers + part(m(PALM, o), far=far, tex=False))
    forearm = piv(f"forearm-{side}", f"{C}-forearm", *F(ELBOW[0] + o[0], ELBOW[1] + o[1]), hand + part(m(FOREARM, o), far=far))
    return piv(f"arm-{side}", f"{C}-arm", *F(SHOULDER[0] + o[0], SHOULDER[1] + o[1]), forearm + part(m(UPPER_ARM, o), skip=(0, 6), seam=(1, 5), far=far, seam_op=0.22))

# ------------------------------------------------------------------ tail: five nested segments; deep paddle from tall spines and chevrons
TAIL_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in
                      [(0.1, 2.8, 0.85), (-1.0, 2.85, 0.8), (-2.3, 2.75, 0.68), (-3.5, 2.55, 0.82), (-4.6, 2.35, 0.95), (-5.8, 2.1, 0.78), (-6.9, 1.9, 0.22)]])

def tail_rays(k, s0, s1):
    """faint lines for the tall neural spines and chevrons that deepen the distal tail"""
    if k < 2: return ""
    d = ""
    for i in range(int((s1 - s0) / (0.28 * S))):
        x, y, tx, ty, dep = TAIL_SPINE.at(s0 + (i + 0.5) * 0.28 * S); nx, ny = -ty, tx
        if ny > 0: nx, ny = -nx, -ny
        for sgn in (1, -1):
            a = (x + sgn * nx * dep * 0.12, y + sgn * ny * dep * 0.12); b = (x + sgn * nx * dep * 0.4 + tx * 6, y + sgn * ny * dep * 0.4 + ty * 6)
            d += f"M{K._f(a)} L{K._f(b)} "
    return line(d, 0.16, 1.8)

TAIL = K.segmented(LOOK, TAIL_SPINE, [0, 0.2, 0.4, 0.6, 0.8, 1.0], ["tail", "tail-2", "tail-3", "tail-4", "tail-5"], 0.35 * S,
                   [3, 3, 3, 3, 2], tip_cap=0.35, layers=tail_rays)

# ------------------------------------------------------------------ head: long, low skull; lower jaw on its own hinge
HF = K.Frame(0, 0, S)
SKULL = [(-0.06, 0.1), (0.06, 0.34), (0.26, 0.43), (0.45, 0.42), (0.56, 0.47), (0.66, 0.45), (0.85, 0.33), (1.1, 0.24), (1.32, 0.19),
         (1.45, 0.21), (1.56, 0.18), (1.63, 0.08), (1.62, -0.02), (1.52, -0.06), (1.4, -0.04), (1.32, -0.01), (1.25, -0.05), (0.9, -0.07),
         (0.5, -0.08), (0.2, -0.1), (0.02, -0.12), (-0.08, -0.02)]
LOWER_JAW = [(0.0, -0.09), (0.4, -0.085), (0.9, -0.075), (1.25, -0.055), (1.32, -0.025), (1.4, -0.045), (1.55, -0.065), (1.6, -0.11),
             (1.55, -0.17), (1.4, -0.16), (1.2, -0.14), (0.8, -0.16), (0.4, -0.21), (0.1, -0.21), (-0.05, -0.14)]
JAW_HINGE = (0.06, -0.1)
UPPER_TEETH = [(x, 0.06) for x in (0.62, 0.74, 0.86, 0.98, 1.1, 1.2)] + [(1.37, 0.1), (1.46, 0.12), (1.54, 0.1)]
LOWER_TEETH = [(x, 0.05) for x in (0.68, 0.8, 0.92, 1.04, 1.16)] + [(1.43, 0.1), (1.51, 0.09)]

def margin(x, pts):
    """y of a jaw margin at x, from (x, y) points sorted by x"""
    pts = sorted(pts)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]

def teeth(spec, edge, down):
    """straight conical teeth standing on a jaw margin, tipped slightly forward"""
    out = ""
    for x, ln in spec:
        y = margin(x, edge); w = ln * 0.3; tip = (x + ln * 0.15, y - ln if down else y + ln)
        out += path(K.smooth(HF.pts([(x - w, y), tip, (x + w, y)]))[0], IVORY) + stroke(f"M{K._f(HF(x - w, y))} L{K._f(HF(*tip))} L{K._f(HF(x + w, y))}", 1.2)
    return out

UPPER_EDGE = SKULL[12:21]; LOWER_EDGE = LOWER_JAW[:7]
JAW = piv("jaw", f"{C}-jaw", *HF(*JAW_HINGE), part(HF.pts(LOWER_JAW), tex=False,
          belly=K.smooth(HF.pts([(0.2, -0.17), (0.8, -0.13), (1.4, -0.13), (1.52, -0.15), (1.4, -0.155), (0.8, -0.155), (0.4, -0.2), (0.12, -0.2)]))[0])
          + teeth(LOWER_TEETH, LOWER_EDGE, down=False))
UPPER = f'<g id="upper-jaw" class="{C}-upper-jaw">' + teeth(UPPER_TEETH, UPPER_EDGE, down=True) + "</g>"
ex, ey = HF(0.4, 0.27); nx_, ny_ = HF(0.95, 0.25)
SKULL_G = (f'<g id="skull" class="{C}-skull">' + part(HF.pts(SKULL), light=True, tex=False)
           + f'<ellipse cx="{nx_}" cy="{ny_}" rx="5" ry="1.6" fill="{OL}" opacity="0.7" transform="rotate(-8 {nx_} {ny_})"></ellipse>'
           + line(K.smooth(HF.pts([(0.48, 0.44), (0.56, 0.47), (0.66, 0.45), (0.6, 0.4)]))[1], 0.25, 1.6)        # small crest before the eye
           + K.eye(ex, ey, f"{C}-eyelid", r=3.4) + "</g>")
HEAD_ANGLE = 8

# ------------------------------------------------------------------ neck: S-curved, two segments, head at the end
NECK_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in [(2.85, 3.0, 1.1), (3.5, 3.45, 0.92), (4.05, 3.95, 0.75), (4.5, 4.28, 0.64), (4.85, 4.38, 0.56)]])
hx, hy, htx, hty, _ = NECK_SPINE.at(NECK_SPINE.length)
HEAD = (f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({HEAD_ANGLE})">'
        + piv("head", f"{C}-head", 0, 0, SKULL_G + JAW + UPPER) + "</g>")
NECK = K.segmented(LOOK, NECK_SPINE, [0, 0.5, 1.0], ["neck", "neck-2"], 0.3 * S, [2, 2], tip_cap=0.1, end=HEAD)

# ------------------------------------------------------------------ torso and sail
BACK = [(-1.45, 2.95), (-1.3, 3.08), (-0.6, 3.25), (0.4, 3.3), (1.4, 3.32), (2.3, 3.37), (2.75, 3.56), (3.2, 3.8), (3.5, 3.95)]   # runs on into the neck top
BARREL = BACK[1:] + [(3.75, 3.55), (3.7, 3.0), (3.5, 2.45), (3.0, 2.05), (2.2, 1.82), (1.3, 1.82), (0.6, 2.0), (0.0, 2.25), (-0.6, 2.45), (-1.2, 2.65), (-1.5, 2.85)]
BELLY = [(3.5, 2.45), (3.0, 2.05), (2.2, 1.82), (1.3, 1.82), (0.6, 2.0), (0.0, 2.25), (0.0, 2.55), (0.6, 2.3), (1.3, 2.15), (2.2, 2.15), (3.0, 2.35), (3.45, 2.75)]
CHEST = [(1.9, 3.33), (2.3, 3.37), (2.75, 3.56), (3.2, 3.8), (3.5, 3.95), (3.75, 3.55), (3.7, 3.0), (3.5, 2.45), (3.0, 2.05), (2.2, 1.82), (1.75, 2.3), (1.7, 2.9)]
PELVIS = [(-1.3, 3.08), (-0.6, 3.25), (0.4, 3.3), (0.95, 3.31), (1.05, 2.6), (0.7, 1.98), (0.0, 2.25), (-0.6, 2.45), (-1.2, 2.65), (-1.5, 2.85)]
# sail height above the back (metres), peaking over the rear of the trunk; outline RECONSTRUCTED, gently uneven at the spine tips
SAIL_H = [(-1.45, 0.1), (-1.1, 0.7), (-0.7, 1.2), (-0.2, 1.55), (0.4, 1.68), (1.0, 1.6), (1.6, 1.4), (2.2, 1.08), (2.7, 0.7), (3.1, 0.3), (3.35, 0.05)]

def back_y(x): return margin(x, BACK)
def sail():
    rnd = K.random.Random("spn-sail")
    xs = [-1.45 + i * 0.28 for i in range(int(4.8 / 0.28) + 1)] + [3.35]
    top = [(x, back_y(x) + margin(x, SAIL_H) + (rnd.uniform(-0.05, 0.07) if 0 < i < len(xs) - 1 else 0)) for i, x in enumerate(xs)]
    base = [(x, back_y(x) - 0.25) for x in (3.35, 1.8, 0.3, -1.45)]
    pts = m(top + base); n = len(top)
    fill, out = K.smooth(pts, skip=range(n - 1, n + 4))
    spines = " ".join(f"M{K._f(F(x, back_y(x) - 0.1))} L{K._f(F(x - 0.04, y - 0.06))}" for x, y in top[1:-1])
    return (f'<g id="sail" class="{C}-sail">' + path(fill, LOOK.accent) + line(spines, 0.24, 2)
            + path(fill, LOOK.url("shade")) + stroke(out) + "</g>")

body_poly = m([(-1.2, 3.0), (1.5, 3.2), (3.4, 3.3), (3.2, 2.2), (1.5, 1.95), (-0.8, 2.5)])
BODY = piv("body", f"{C}-body", *F(1.4, 1.6), (
    sail()
    + f'<g id="abdomen" class="{C}-abdomen">' + part(m(BARREL), skip=(7, 8), seam=(9,), seam_op=0.18, belly=K.smooth(m(BELLY))[0],
                                                     layers=dots(body_poly, 70, 1.4, 2.4, 0.08, seed=13)) + "</g>"
    + f'<g id="pelvis" class="{C}-pelvis">' + part(m(PELVIS), seam=(3, 4), seam_op=0.1) + "</g>"
    + f'<g id="chest" class="{C}-chest">' + part(m(CHEST), skip=(4, 5), seam=(6, 9, 10, 11), seam_op=0.1,
                                                  belly=K.smooth(m([(3.5, 2.45), (3.0, 2.05), (2.2, 1.82), (2.1, 2.18), (3.0, 2.35), (3.45, 2.75)]))[0]) + "</g>"))

# ------------------------------------------------------------------ hidden skeletal guide (joint centres and spines, for editing)
def _guide():
    bones = f"M{K._f(F(*HIP))} L{K._f(F(*KNEE))} L{K._f(F(*ANKLE))} M{K._f(F(*SHOULDER))} L{K._f(F(*ELBOW))} L{K._f(F(*WRIST))}"
    spines = "".join('<path d="M' + " L".join(K._f(sp.at(sp.length * k / 20)[:2]) for k in range(21)) + '" fill="none" stroke="#3A7BD5" stroke-width="2"></path>'
                     for sp in (TAIL_SPINE, NECK_SPINE))
    joints = "".join(f'<circle cx="{F(*p)[0]}" cy="{F(*p)[1]}" r="4" fill="#E5484D"></circle>' for p in (HIP, KNEE, ANKLE, SHOULDER, ELBOW, WRIST))
    return (f'<g id="skeleton-guide" class="{C}-guide" display="none" pointer-events="none">'
            f'<path d="{bones}" fill="none" stroke="#3A7BD5" stroke-width="3"></path>{spines}{joints}</g>')

FRAG = piv("act", f"{C}-act", *F(0.6, 0), hind_leg("far") + arm("far") + TAIL + NECK + BODY + hind_leg("near") + arm("near") + _guide())

_ht = (hx + math.cos(math.radians(HEAD_ANGLE)) * 1.62 * S, hy + math.sin(math.radians(HEAD_ANGLE)) * 1.62 * S)
MIDLINE = ([TAIL_SPINE.at(TAIL_SPINE.length * (1 - k / 10))[:2] for k in range(11)] + [F(1.5, 2.5)]
           + [NECK_SPINE.at(NECK_SPINE.length * k / 6)[:2] for k in range(7)] + [_ht])

# ------------------------------------------------------------------ move: a quick strike at a fish, jaws snapping shut
ACTION = {
    "neck": [(0, "rotate(0)"), (0.2, "rotate(-6deg)"), (0.42, "rotate(12deg)"), (0.62, "rotate(12deg)"), (1, "rotate(0)")],
    "neck-2": [(0, "rotate(0)"), (0.2, "rotate(-3deg)"), (0.42, "rotate(6deg)"), (0.62, "rotate(6deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.2, "rotate(-4deg)"), (0.42, "rotate(6deg)"), (0.62, "rotate(5deg)"), (1, "rotate(0)")],
    "jaw": [(0, "rotate(0)"), (0.2, "rotate(16deg)"), (0.4, "rotate(18deg)"), (0.46, "rotate(0)"), (1, "rotate(0)")],
    "tail": [(0, "rotate(0)"), (0.42, "rotate(-4deg)"), (0.62, "rotate(-4deg)"), (1, "rotate(0)")],
    "act": [(0, "translateX(0)"), (0.2, "translateX(-6px)"), (0.42, "translateX(12px)"), (0.62, "translateX(12px)"), (1, "translateX(0)")],
}
GSAP = """      .to(parts.neck, { rotation: -6, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.neck_2, { rotation: -3, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -4, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.jaw, { rotation: 17, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.act, { x: -6, duration: 0.3, ease: 'power2.out' }, 0)
      .to(parts.neck, { rotation: 12, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.neck_2, { rotation: 6, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.head, { rotation: 6, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.act, { x: 12, duration: 0.32, ease: 'power3.in' }, 0.32)
      .to(parts.tail, { rotation: -4, duration: 0.32, ease: 'power2.out' }, 0.32)
      .to(parts.jaw, { rotation: 0, duration: 0.08, ease: 'power4.in' }, 0.66)
      .to([parts.neck, parts.neck_2, parts.head, parts.tail], { rotation: 0, duration: 0.6, ease: 'power2.inOut' }, 1.0)
      .to(parts.act, { x: 0, duration: 0.6, ease: 'power2.inOut' }, 1.0)"""

IDS = ["act", "body", "chest", "abdomen", "pelvis", "sail", "tail", "tail-2", "tail-3", "tail-4", "tail-5",
       "neck", "neck-2", "head", "skull", "upper-jaw", "jaw", "leg-near", "leg-far", "arm-near", "arm-far"]

SPEC = dict(
    code=C, slug="spinosaurus", board="Spinosaurus", name="Spinosaurus", short="Spinosaurus", look=LOOK,
    viewbox=(1000, 560), frag=FRAG, ids=IDS, action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the Spinosaurus strike at a fish", action_verb="make it strike", page_bg="#DCD6C4",
    scene=scenery.set_bahariya(), title="Spinosaurus", title_px=176, binomial="Spinosaurus aegyptiacus", subtitle="the Egyptian spine lizard",
    paragraph="A long-snouted fish hunter with a tall sail on its back, a deep, paddle-like tail and short hind legs. How well it swam is still debated.",
    facts=[("14 m", "snout to tail tip"), ("100–94", "million years ago"), ("1.65 m", "longest sail spine")],
    footer="Fossils come from the Kem Kem beds of Morocco and the Bahariya Formation of Egypt, where the first skeleton was found; it was destroyed in 1944.",
    hint="Tap the Spinosaurus to make it strike", skin_swatches=["#4F6E70", "#A0694A", "#5E7E7A", "#8A6A3E"],
    dino_top=190, midline=MIDLINE, ground=F.g,
)

if __name__ == "__main__":
    K.write_all(SPEC)          # this rework round: svg/ and gsap/ only; poster and rig board follow later
    print("ok")
